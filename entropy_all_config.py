"""Configuracion de etapa: los cuatro proveedores, con Node.js aislado."""

from __future__ import annotations

import pathlib

from entropy_java_config import (
    build_python_java_commands,
)


NODE_EXECUTABLE = (
    pathlib.Path.home()
    / ".local"
    / "opt"
    / "bip39-node"
    / "node-v24.22.2-linux-x64"
    / "bin"
    / "node"
)

WEBCRYPTO_HELPER = (
    pathlib.Path(__file__).resolve().parent
    / "entropy_helpers"
    / "webcrypto_provider.cjs"
)


def build_all_provider_commands():
    if not WEBCRYPTO_HELPER.is_file():
        raise ValueError(
            "No se encontro webcrypto_provider.cjs."
        )

    commands = build_python_java_commands()

    commands["javascript_webcrypto"] = (
        str(NODE_EXECUTABLE),
        str(WEBCRYPTO_HELPER),
    )

    return commands
