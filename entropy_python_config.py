"""Configuracion de prueba: solo Python; Java y JavaScript deshabilitados."""

from __future__ import annotations

import pathlib
import sys

from entropy_policy import PROVIDER_ORDER


HELPER_PATH = (
    pathlib.Path(__file__).resolve().parent
    / "entropy_helpers"
    / "python_entropy_provider.py"
)


def build_python_only_commands(
    *,
    python_executable=None,
):
    executable = (
        sys.executable
        if python_executable is None
        else python_executable
    )

    if (
        type(executable) is not str
        or not executable
        or "\0" in executable
    ):
        raise ValueError(
            "Ejecutable Python invalido."
        )

    if not pathlib.Path(executable).is_absolute():
        raise ValueError(
            "Python debe tener una ruta absoluta."
        )

    if not HELPER_PATH.is_file():
        raise ValueError(
            "No se encontro el auxiliar Python."
        )

    command = (
        executable,
        "-I",
        "-S",
        str(HELPER_PATH),
    )

    commands = {
        p: None
        for p in PROVIDER_ORDER
    }

    commands["python_os"] = command
    commands["python_secrets"] = command

    return commands
