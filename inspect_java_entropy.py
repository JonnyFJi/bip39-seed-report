"""Inspeccion de Java sin generar aportaciones de entropy."""

from __future__ import annotations

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile


SOURCE_PATH = (
    pathlib.Path(__file__).resolve().parent
    / "entropy_helpers"
    / "JavaEntropyProbe.java"
)

METADATA_KEYS = frozenset(
    {
        "inspection_version",
        "java_version",
        "runtime_version",
        "java_vendor",
        "java_home",
        "vm_name",
        "strong_algorithms",
        "algorithm",
        "provider",
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

    for key in (
        METADATA_KEYS - {"inspection_version"}
    ):
        if (
            type(value[key]) is not str
            or not value[key].strip()
        ):
            raise ValueError(
                "Campo de metadatos invalido."
            )

    return dict(value)


def parse_metadata(text):
    return validate_metadata(
        json.loads(
            text,
            object_pairs_hook=reject_duplicate_keys,
        )
    )


def inspect_java():
    java = shutil.which("java")
    javac = shutil.which("javac")

    if java is None or javac is None:
        raise RuntimeError(
            "Falta java o javac en PATH; "
            "no instalar automaticamente."
        )

    if not SOURCE_PATH.is_file():
        raise RuntimeError(
            "No se encontro JavaEntropyProbe.java."
        )

    java = str(
        pathlib.Path(java).resolve()
    )

    javac = str(
        pathlib.Path(javac).resolve()
    )

    environment = {
        "PATH": os.defpath,
        "LANG": "C",
        "LC_ALL": "C",
    }

    with tempfile.TemporaryDirectory(
        prefix="entropy-java-probe-"
    ) as directory:
        compiled = subprocess.run(
            [
                javac,
                "-encoding",
                "UTF-8",
                "-proc:none",
                "-g:none",
                "-d",
                directory,
                str(SOURCE_PATH),
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment,
            cwd="/",
            timeout=30.0,
            check=False,
        )

        if (
            compiled.returncode != 0
            or compiled.stdout
            or compiled.stderr
        ):
            raise RuntimeError(
                "Compilacion no limpia; "
                "no se activa Java."
            )

        described = subprocess.run(
            [
                java,
                "-cp",
                directory,
                "JavaEntropyProbe",
                "--describe",
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=environment,
            cwd="/",
            timeout=10.0,
            check=False,
        )

        if described.returncode == 11:
            raise RuntimeError(
                "getInstanceStrong no encontro "
                "un algoritmo disponible."
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
        "java_executable": java,
        "javac_executable": javac,
        "same_bin_directory": (
            pathlib.Path(java).parent
            == pathlib.Path(javac).parent
        ),
        "java_home_matches_executable": (
            pathlib.Path(
                metadata["java_home"]
            ).resolve()
            == pathlib.Path(java).parent.parent
        ),
    }


if __name__ == "__main__":
    try:
        report = inspect_java()

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

        raise SystemExit(1)

    print(
        json.dumps(
            report,
            ensure_ascii=True,
            indent=2,
            sort_keys=True,
        )
    )
    