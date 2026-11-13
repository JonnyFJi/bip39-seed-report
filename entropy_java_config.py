"""Configuracion de etapa: Python y Java; JavaScript deshabilitado."""

from __future__ import annotations

import pathlib

from entropy_python_config import (
    build_python_only_commands,
)


JAVA_EXECUTABLE = (
    "/usr/lib/jvm/"
    "java-11-openjdk-amd64/"
    "bin/java"
)

CLASS_DIRECTORY = (
    pathlib.Path(__file__).resolve().parent
    / "build"
    / "entropy_java"
)

CLASS_FILE = (
    CLASS_DIRECTORY
    / "JavaEntropyProvider.class"
)


def build_python_java_commands():
    if not CLASS_FILE.is_file():
        raise ValueError(
            "Falta compilar JavaEntropyProvider.java."
        )

    commands = build_python_only_commands()

    commands["java_secure_random"] = (
        JAVA_EXECUTABLE,
        "-cp",
        str(CLASS_DIRECTORY),
        "JavaEntropyProvider",
    )

    return commands
