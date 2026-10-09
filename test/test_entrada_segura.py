#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import contextlib
import io
import sys
import warnings
from unittest.mock import patch

import bip39_seed_report as report


def comprobar(condicion, descripcion):
    if not condicion:
        raise AssertionError(descripcion)
    print(f"OK: {descripcion}", flush=True)


def probar_getpass_warning():
    print("\nPrueba: rechazo de GetPassWarning", flush=True)

    fallback_alcanzado = []

    def getpass_simulado(prompt):
        warnings.warn(
            "Advertencia simulada: no se puede desactivar el eco.",
            report.getpass.GetPassWarning,
            stacklevel=2,
        )
        fallback_alcanzado.append(True)
        return "NO-DEBE-SER-ACEPTADO"

    with patch.object(report, "_require_tty") as tty_simulada:
        with patch.object(
            report.getpass,
            "getpass",
            side_effect=getpass_simulado,
        ) as lector_simulado:
            try:
                report.read_hidden_secret("Secreto ficticio: ")
            except RuntimeError as exc:
                comprobar(
                    isinstance(
                        exc.__cause__,
                        report.getpass.GetPassWarning,
                    ),
                    "El rechazo proviene de GetPassWarning, no de falta de TTY",
                )
            else:
                raise AssertionError(
                    "Se aceptó una entrada pese a GetPassWarning."
                )

            comprobar(
                tty_simulada.call_count == 1,
                "La comprobación de TTY fue invocada",
            )

            comprobar(
                lector_simulado.call_count == 1,
                "La prueba alcanzó la llamada a getpass",
            )

    comprobar(
        not fallback_alcanzado,
        "La advertencia detuvo el flujo antes del fallback simulado",
    )


def probar_unicode():
    print("\nPrueba: normalización Unicode de passphrase", flush=True)

    compuesta = "Prueba-caf\u00e9"
    descompuesta = "Prueba-cafe\u0301"

    comprobar(
        compuesta != descompuesta,
        "Las representaciones originales son distintas",
    )

    comprobar(
        report.normalize_text(compuesta)
        == report.normalize_text(descompuesta),
        "Ambas representaciones coinciden tras NFKD",
    )

    salida = io.StringIO()

    with patch.object(
        report,
        "read_hidden_secret",
        side_effect=[compuesta, descompuesta],
    ) as lector:
        with contextlib.redirect_stdout(salida):
            confirmada = report.get_secure_passphrase()

        comprobar(
            lector.call_count == 2,
            "La confirmación acepta equivalencia Unicode sin reintento",
        )

    comprobar(
        confirmada == report.normalize_text(compuesta),
        "La passphrase confirmada se devuelve normalizada",
    )

    salida = io.StringIO()

    with patch.object(
        report,
        "read_hidden_secret",
        side_effect=[
            "valor-uno",
            "valor-dos",
            compuesta,
            descompuesta,
        ],
    ) as lector:
        with contextlib.redirect_stdout(salida):
            confirmada = report.get_secure_passphrase()

        comprobar(
            lector.call_count == 4,
            "Tras una discrepancia se solicita un segundo par de valores",
        )

    comprobar(
        confirmada == report.normalize_text(compuesta),
        "El reintento conserva la normalización Unicode",
    )

    mnemonic_publica = (
        "abandon abandon abandon abandon abandon abandon "
        "abandon abandon abandon abandon abandon about"
    )

    seed_compuesta = report.mnemonic_seed(
        mnemonic_publica,
        compuesta,
    )

    seed_descompuesta = report.mnemonic_seed(
        mnemonic_publica,
        descompuesta,
    )

    comprobar(
        seed_compuesta == seed_descompuesta,
        "Las passphrases equivalentes producen la misma seed",
    )


def main():
    print(
        "Pruebas con datos ficticios; no se crearán reportes.",
        flush=True,
    )

    probar_getpass_warning()
    probar_unicode()

    print(
        "\nRESULTADO: las pruebas de GetPassWarning y Unicode pasaron.",
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
