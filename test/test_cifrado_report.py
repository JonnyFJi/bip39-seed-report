#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import copy
import hashlib
import json
import os
import sys

import bip39_seed_report as report
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def comprobar(condicion, descripcion):
    if not condicion:
        raise AssertionError(descripcion)
    print(f"OK: {descripcion}", flush=True)


def debe_rechazar(contenido, password, descripcion):
    try:
        report.decrypt_report_content(contenido, password)
    except ValueError:
        print(f"OK: {descripcion}", flush=True)
        return

    raise AssertionError(
        f"No se rechazó una entrada inválida: {descripcion}"
    )


def main():
    texto = "Reporte de prueba sin secretos reales."
    password = "Contrase\u00f1a-\u00e9-de-prueba-no-utilizar"

    print(
        "Iniciando pruebas con datos ficticios. "
        "No se escribirán archivos de reporte.",
        flush=True,
    )

    print("Probando cifrado y descifrado...", flush=True)
    cifrado = report._encrypt_report_content(texto, password)
    recuperado = report.decrypt_report_content(cifrado, password)

    comprobar(
        recuperado == texto,
        "El descifrado recupera exactamente el texto original",
    )

    print("Probando salt y nonce nuevos...", flush=True)
    segundo_cifrado = report._encrypt_report_content(texto, password)

    primer_contenedor = json.loads(cifrado)
    segundo_contenedor = json.loads(segundo_cifrado)

    comprobar(
        primer_contenedor["kdf"]["salt_b64"]
        != segundo_contenedor["kdf"]["salt_b64"],
        "Dos cifrados utilizan salts diferentes",
    )

    comprobar(
        primer_contenedor["cipher"]["nonce_b64"]
        != segundo_contenedor["cipher"]["nonce_b64"],
        "Dos cifrados utilizan nonces diferentes",
    )

    debe_rechazar(
        cifrado,
        "password-incorrecto",
        "La contraseña incorrecta se rechaza",
    )

    campos = (
        ("ciphertext_b64", None, "ciphertext"),
        ("nonce_b64", "cipher", "nonce"),
        ("salt_b64", "kdf", "salt"),
    )

    for campo, seccion, nombre in campos:
        alterado = copy.deepcopy(primer_contenedor)

        if seccion is None:
            destino = alterado
        else:
            destino = alterado[seccion]

        datos = bytearray(
            base64.b64decode(destino[campo], validate=True)
        )

        if not datos:
            raise AssertionError(
                f"El campo {nombre} está inesperadamente vacío"
            )

        datos[0] ^= 1
        destino[campo] = base64.b64encode(datos).decode("ascii")

        debe_rechazar(
            json.dumps(alterado),
            password,
            f"La alteración del {nombre} se rechaza",
        )

    alterado = copy.deepcopy(primer_contenedor)
    alterado["kdf"]["n"] = 2**30

    debe_rechazar(
        json.dumps(alterado),
        password,
        "El perfil scrypt con N excesivo se rechaza",
    )

    print("Probando compatibilidad histórica...", flush=True)

    for password_historico in ("ascii-test", "\u00e9-test"):
        nonce = os.urandom(12)

        clave = hashlib.sha256(
            password_historico.encode("utf-8")
        ).digest()

        ciphertext = AESGCM(clave).encrypt(
            nonce,
            texto.encode("utf-8"),
            None,
        )

        historico = (
            "ENCRYPTED:"
            + base64.b64encode(nonce + ciphertext).decode("ascii")
        )

        comprobar(
            report.decrypt_report_content(
                historico,
                password_historico,
            ) == texto,
            f"Formato histórico recuperado: {password_historico!r}",
        )

        comprobar(
            report.decrypt_file_content(
                historico,
                password_historico,
            ) == texto,
            f"Alias compatible: {password_historico!r}",
        )

    print(
        "\nRESULTADO: las 12 comprobaciones finalizaron correctamente.",
        flush=True,
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nPRUEBA INTERRUMPIDA.", file=sys.stderr)
        sys.exit(130)
    except Exception as exc:
        print(
            f"\nPRUEBA FALLIDA: {type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        sys.exit(1)