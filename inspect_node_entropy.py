"""Inspeccion de Node.js y Web Crypto sin solicitar bytes aleatorios."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import shutil
import subprocess
import sys


PROBE_PATH = (
    pathlib.Path(__file__).resolve().parent
    / "entropy_helpers"
    / "node_entropy_probe.cjs"
)

TEXT_FIELDS = frozenset(
    {
        "node_version",
        "node_executable",
        "platform",
        "architecture",
    }
)

BOOLEAN_FIELDS = frozenset(
    {
        "crypto_module_available",
        "webcrypto_get_random_values",
    }
)

OPTIONAL_BOOLEAN_FIELDS = frozenset(
    {
        "shared_openssl",
        "configured_openssl",
    }
)

METADATA_KEYS = (
    TEXT_FIELDS
    | BOOLEAN_FIELDS
    | OPTIONAL_BOOLEAN_FIELDS
    | {
        "inspection_version",
        "openssl_version",
        "fips_mode",
        "exec_argv",
    }
)


def reject_duplicate_keys(pairs):
    result = {}

    for key, value in pairs:
        if key in result:
            raise ValueError(
                "Metadatos con claves duplicadas."
            )

        result[key] = value

    return result


def validate_metadata(value):
    if (
        type(value) is not dict
        or set(value) != METADATA_KEYS
    ):
        raise ValueError(
            "Estructura de metadatos no admitida."
        )

    if (
        type(value["inspection_version"]) is not int
        or value["inspection_version"] != 1
    ):
        raise ValueError(
            "Version de inspeccion no admitida."
        )

    for key in TEXT_FIELDS:
        if (
            type(value[key]) is not str
            or not value[key].strip()
        ):
            raise ValueError(
                "Campo de texto invalido."
            )

    if not pathlib.Path(
        value["node_executable"]
    ).is_absolute():
        raise ValueError(
            "Ruta de Node.js no absoluta."
        )

    for key in BOOLEAN_FIELDS:
        if type(value[key]) is not bool:
            raise ValueError(
                "Campo booleano invalido."
            )

    for key in OPTIONAL_BOOLEAN_FIELDS:
        if (
            value[key] is not None
            and type(value[key]) is not bool
        ):
            raise ValueError(
                "Indicador de compilacion invalido."
            )

    openssl = value["openssl_version"]

    if openssl is not None and (
        type(openssl) is not str
        or not openssl.strip()
    ):
        raise ValueError(
            "Version OpenSSL invalida."
        )

    fips = value["fips_mode"]

    if fips is not None and (
        type(fips) is not int
        or fips not in (0, 1)
    ):
        raise ValueError(
            "Indicador FIPS invalido."
        )

    flags = value["exec_argv"]

    if (
        type(flags) is not list
        or any(
            type(flag) is not str
            for flag in flags
        )
    ):
        raise ValueError(
            "Argumentos del runtime invalidos."
        )

    if (
        value["webcrypto_get_random_values"]
        and not value["crypto_module_available"]
    ):
        raise ValueError(
            "Capacidades declaradas inconsistentes."
        )

    return dict(value)


def parse_metadata(text):
    return validate_metadata(
        json.loads(
            text,
            object_pairs_hook=reject_duplicate_keys,
        )
    )


def _select_node_executable(node_executable=None):
    if node_executable is None:
        executable = shutil.which("node")

        if executable is None:
            raise RuntimeError(
                "No se encontro node en PATH; "
                "no instalar automaticamente."
            )

    else:
        executable = node_executable

    if (
        type(executable) is not str
        or not executable
        or "\0" in executable
    ):
        raise ValueError(
            "La ruta de Node.js debe ser "
            "texto no vacio y sin NUL."
        )

    path = pathlib.Path(executable)

    if not path.is_absolute():
        raise ValueError(
            "La ruta de Node.js debe ser absoluta."
        )

    resolved = path.resolve(strict=True)

    if (
        not resolved.is_file()
        or not os.access(resolved, os.X_OK)
    ):
        raise ValueError(
            "La ruta debe identificar "
            "un archivo ejecutable."
        )

    return str(resolved)


def inspect_node(*, node_executable=None):
    executable = _select_node_executable(
        node_executable
    )

    if not PROBE_PATH.is_file():
        raise RuntimeError(
            "No se encontro node_entropy_probe.cjs."
        )

    described = subprocess.run(
        [
            executable,
            str(PROBE_PATH),
            "--describe",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={
            "PATH": os.defpath,
            "LANG": "C",
            "LC_ALL": "C",
        },
        cwd="/",
        timeout=10.0,
        check=False,
    )

    if (
        described.returncode != 0
        or described.stderr
        or len(described.stdout) > 16384
    ):
        raise RuntimeError(
            "Respuesta de inspeccion no admitida."
        )

    metadata = parse_metadata(
        described.stdout.decode("utf-8")
    )

    return {
        **metadata,

        "selected_node_executable": executable,

        "executable_matches": (
            pathlib.Path(
                metadata["node_executable"]
            ).resolve()
            == pathlib.Path(executable)
        ),
    }


def build_parser():
    parser = argparse.ArgumentParser(
        description=(
            "Inspeccion de Node.js y Web Crypto "
            "sin generar entropy."
        ),
        allow_abbrev=False,
    )

    parser.add_argument(
        "--node",
        default=None,
        metavar="RUTA_ABSOLUTA",
        help=(
            "Ejecutable Node.js explicito; "
            "sin esta opcion se busca node en PATH."
        ),
    )

    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)

    try:
        report = inspect_node(
            node_executable=args.node
        )

    except (
        OSError,
        RuntimeError,
        ValueError,
        subprocess.TimeoutExpired,
        UnicodeError,
    ) as exc:
        print(
            "Inspeccion no completada: "
            + str(exc),
            file=sys.stderr,
        )

        return 1

    print(
        json.dumps(
            report,
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
