"""Transporte binario acotado para auxiliares de confianza, solo POSIX."""

from __future__ import annotations

import math
import os
import pathlib
import selectors
import signal
import subprocess
import time
from typing import Mapping, Sequence

from entropy_policy import (
    CONTRIBUTION_BYTES,
    KNOWN_PROVIDERS,
)

from entropy_coordinator import (
    ProviderGenerationError,
    ProviderProtocolError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)


def _cleanup(proc):
    try:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass

        proc.wait(timeout=1.0)

    except (OSError, subprocess.TimeoutExpired):
        raise ProviderProtocolError(
            "No se pudo confirmar la limpieza del auxiliar."
        ) from None

    finally:
        for stream in (proc.stdout, proc.stderr):
            if stream is not None:
                stream.close()


class ProcessProviderRunner:
    def __init__(
        self,
        commands: Mapping[str, Sequence[str] | None],
    ):
        if os.name != "posix":
            raise RuntimeError(
                "Este ejecutor requiere POSIX; "
                "Windows no esta implementado."
            )

        if set(commands) != KNOWN_PROVIDERS:
            raise ValueError(
                "Configura exactamente los cuatro proveedores."
            )

        self._commands = {}

        for provider_id, command in commands.items():
            if command is None:
                self._commands[provider_id] = None
                continue

            if (
                not isinstance(command, (tuple, list))
                or not command
            ):
                raise ValueError(
                    "Cada comando debe ser una lista "
                    "o tupla no vacia."
                )

            if any(
                type(arg) is not str or "\0" in arg
                for arg in command
            ):
                raise ValueError(
                    "Los argumentos deben ser texto sin NUL."
                )

            if not pathlib.Path(command[0]).is_absolute():
                raise ValueError(
                    "El ejecutable debe tener ruta absoluta."
                )

            self._commands[provider_id] = tuple(command)

    def acquire(
        self,
        provider_id,
        nbytes,
        *,
        timeout_seconds,
    ):
        if (
            type(provider_id) is not str
            or provider_id not in KNOWN_PROVIDERS
        ):
            raise ValueError("Proveedor no reconocido.")

        if (
            type(nbytes) is not int
            or nbytes != CONTRIBUTION_BYTES
        ):
            raise ValueError(
                "Esta version solo admite "
                "aportaciones de 32 bytes."
            )

        if (
            type(timeout_seconds) not in (int, float)
            or not (0 < timeout_seconds < math.inf)
        ):
            raise ValueError("Timeout invalido.")

        command = self._commands[provider_id]

        if command is None:
            raise ProviderUnavailableError(
                "Proveedor deshabilitado."
            )

        argv = (
            *command,
            "--provider",
            provider_id,
            "--bytes",
            str(nbytes),
        )

        deadline = time.monotonic() + timeout_seconds

        try:
            proc = subprocess.Popen(
                argv,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                close_fds=True,
                start_new_session=True,
                bufsize=0,
                cwd="/",
                env={
                    "PATH": os.defpath,
                    "LANG": "C",
                    "LC_ALL": "C",
                },
            )

        except FileNotFoundError:
            raise ProviderUnavailableError(
                "No se pudo iniciar el ejecutable."
            ) from None

        except OSError:
            raise ProviderProtocolError(
                "Error al iniciar el auxiliar."
            ) from None

        output = bytearray()

        try:
            with selectors.DefaultSelector() as selector:
                for stream, label in (
                    (proc.stdout, "out"),
                    (proc.stderr, "err"),
                ):
                    os.set_blocking(
                        stream.fileno(),
                        False,
                    )

                    selector.register(
                        stream,
                        selectors.EVENT_READ,
                        label,
                    )

                while (
                    selector.get_map()
                    or proc.poll() is None
                ):
                    remaining = (
                        deadline - time.monotonic()
                    )

                    if remaining <= 0:
                        raise ProviderTimeoutError(
                            "Tiempo de adquisicion agotado."
                        )

                    if not selector.get_map():
                        time.sleep(
                            min(remaining, 0.02)
                        )
                        continue

                    events = selector.select(
                        min(remaining, 0.05)
                    )

                    for key, _ in events:
                        limit = (
                            1
                            if key.data == "err"
                            else nbytes + 1 - len(output)
                        )

                        try:
                            chunk = os.read(
                                key.fd,
                                limit,
                            )
                        except BlockingIOError:
                            continue

                        if not chunk:
                            selector.unregister(
                                key.fileobj
                            )

                        elif key.data == "err":
                            raise ProviderProtocolError(
                                "El auxiliar emitio stderr."
                            )

                        else:
                            output.extend(chunk)

                            if len(output) > nbytes:
                                raise ProviderProtocolError(
                                    "Respuesta demasiado larga."
                                )

            code = proc.wait(
                timeout=max(
                    0.0,
                    deadline - time.monotonic(),
                )
            )

            if code == 0 and len(output) == nbytes:
                return bytes(output)

            if code == 10 and not output:
                raise ProviderGenerationError(
                    "El auxiliar declaro "
                    "un fallo de generacion."
                )

            if code == 11 and not output:
                raise ProviderUnavailableError(
                    "El auxiliar declaro indisponibilidad."
                )

            raise ProviderProtocolError(
                "Respuesta o codigo de salida no admitido."
            )

        except subprocess.TimeoutExpired:
            raise ProviderTimeoutError(
                "Tiempo de adquisicion agotado."
            ) from None

        finally:
            _cleanup(proc)
