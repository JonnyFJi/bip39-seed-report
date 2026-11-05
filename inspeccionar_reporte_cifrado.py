#!/usr/bin/env python3
"""Inspección local de reports. No garantiza borrado seguro ni privacidad total."""
import argparse
import ast
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unicodedata

ROOT = Path(__file__).resolve().parent
PROFILE = "BIP39-revision"
report = None


class InspectionError(RuntimeError):
    pass


def terminal_text(value):
    return "".join(repr(ch)[1:-1] if ch not in "\n\t" and
                   unicodedata.category(ch) in {"Cc", "Cf"} else ch for ch in str(value))


def read_plain(path):
    try:
        with path.open("rb") as handle:
            raw = handle.read(report.MAX_ENCRYPTED_REPORT_BYTES + 1)
    except OSError:
        raise InspectionError("No se pudo leer el archivo cifrado.") from None
    if len(raw) > report.MAX_ENCRYPTED_REPORT_BYTES:
        raise InspectionError("El archivo supera el límite admitido.")
    password = report.read_hidden_secret("Contraseña de exportación: ")
    try:
        return report.decrypt_report_content(raw.decode("utf-8"), password)
    except (ValueError, TypeError, RuntimeError, UnicodeError, RecursionError):
        raise InspectionError("No se pudo autenticar o descifrar. Comprueba la contraseña de exportación y el archivo.") from None
    finally:
        password = None


def parse_plain(plain, expected_format):
    if plain.lstrip("\ufeff\r\n ").startswith("Offline BIP39 Seed Report"):
        actual, data = "txt", None
    else:
        try:
            data = json.loads(plain)
        except (ValueError, RecursionError):
            raise InspectionError("El contenido no es un reporte JSON o TXT reconocido.") from None
        if type(data) is not dict:
            raise InspectionError("La raíz del reporte JSON debe ser un objeto.")
        actual = "json"
    if expected_format != "auto" and expected_format != actual:
        raise InspectionError("El formato interno no coincide con el esperado.")
    return actual, data


def verify_plain(plain, options):
    actual, data = parse_plain(plain, options.format)
    if actual == "txt":
        networks = [line.partition(":")[2].strip() for line in plain.splitlines()
                    if line.partition(":")[0].strip() == "Network"]
        if len(networks) != 1 or networks[0] not in {"mainnet", "testnet"}:
            raise InspectionError("Red de reporte TXT no admitida.")
        if options.network is not None and networks[0] != options.network:
            raise InspectionError("La red no coincide con la esperada.")
        return "TXT: autenticación, cabecera y red; no se comprueban BIP39, seed ni todas las derivaciones."
    try:
        if data["network"] not in {"mainnet", "testnet"} or type(data["passphrase_used"]) is not bool:
            raise ValueError
        if type(data["gap_limit"]) is not int or data["gap_limit"] != report.GAP_LIMIT:
            raise ValueError
        if data["input_mode"] not in {"words", "entropy_hex", "entropy_bin", "mnemonic", "mnemonic_incomplete"}:
            raise ValueError
        if options.network is not None and data["network"] != options.network:
            raise InspectionError("La red no coincide con la esperada.")
        if options.input_mode is not None and data["input_mode"] != options.input_mode:
            raise InspectionError("El modo de entrada no coincide con el esperado.")
        recovered = report.mnemonic_to_entropy(data["mnemonic"])
        count = len(data["mnemonic"].split())
        if options.words is not None and count != options.words:
            raise InspectionError("El número de palabras no coincide con el esperado.")
        if recovered["entropy"].hex() != data["entropy_hex"] or not recovered["checksum_valid"]:
            raise ValueError
        if data["entropy_bits"] != len(recovered["entropy"]) * 8:
            raise ValueError
        if not data["passphrase_used"]:
            if report.Mnemonic("english").to_seed(data["mnemonic"], "").hex() != data["bip39_seed_hex"]:
                raise ValueError
        if set(data["derivations"]) != {"BIP44", "BIP49", "BIP84", "BIP86"}:
            raise ValueError
        coin = 0 if data["network"] == "mainnet" else 1
        for family, item in data["derivations"].items():
            if len(item["addresses"]) != report.GAP_LIMIT:
                raise ValueError
            for index, address in enumerate(item["addresses"]):
                if (address["index"] != index or not address["address"] or
                    address["path"] != f"m/{family[3:]}'/{coin}'/0'/0/{index}"):
                    raise ValueError
    except InspectionError:
        raise
    except (ValueError, TypeError, KeyError, AttributeError, IndexError):
        raise InspectionError("Las comprobaciones internas del reporte no coinciden.") from None
    if data["passphrase_used"]:
        return "JSON: BIP39 y estructura comprobados; seed no contrastada con la passphrase BIP39 no vacía."
    return "JSON: BIP39, seed con passphrase vacía y estructura comprobados; no se verifican independientemente todas las direcciones."


def reveal_here(path, options, *, confirm=True):
    print("ATENCIÓN: mostrará secretos y pueden quedar en scrollback o grabaciones.")
    if confirm and input("¿Revelar aquí? [y/N]: ").strip().lower() != "y":
        print("Revelación cancelada.")
        return False
    plain = read_plain(path)
    try:
        parse_plain(plain, options.format)
        print(terminal_text(plain))
    finally:
        plain = None
    return True


def read_setting(arguments):
    try:
        result = subprocess.run(arguments, check=True, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, text=True, timeout=10)
        return ast.literal_eval(result.stdout.strip())
    except (OSError, subprocess.SubprocessError, ValueError, SyntaxError):
        raise InspectionError("No se pudo consultar el perfil de GNOME Terminal.") from None


def checked_terminal_profile():
    terminal, settings = shutil.which("gnome-terminal"), shutil.which("gsettings")
    if not terminal or not settings:
        raise InspectionError("Falta gnome-terminal o gsettings; no se revelará el reporte aquí.")
    if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
        raise InspectionError("No se detecta una sesión gráfica disponible.")
    profiles = read_setting([settings, "get", "org.gnome.Terminal.ProfilesList", "list"])
    if type(profiles) is not list:
        raise InspectionError("Lista de perfiles GNOME no admitida.")
    matches = []
    for profile in profiles:
        if not isinstance(profile, str) or not re.fullmatch(r"[0-9a-fA-F-]{36}", profile):
            raise InspectionError("Identificador de perfil no admitido.")
        schema = "org.gnome.Terminal.Legacy.Profile:/org/gnome/terminal/legacy/profiles:/:" + profile + "/"
        if read_setting([settings, "get", schema, "visible-name"]) == PROFILE:
            matches.append(schema)
    if len(matches) != 1:
        raise InspectionError("Crea un único perfil GNOME llamado BIP39-revision antes de usar la ventana.")
    schema = matches[0]
    if read_setting([settings, "get", schema, "exit-action"]) != "close":
        raise InspectionError("El perfil BIP39-revision debe cerrar la terminal al terminar; no mantener ni reiniciar.")
    # gsettings prints true/false, not Python literals: query this key separately.
    try:
        result = subprocess.run([settings, "get", schema, "use-custom-command"], check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        raise InspectionError("No se pudo comprobar el comando del perfil.") from None
    if result.stdout.strip() != "false":
        raise InspectionError("Desactiva el comando personalizado del perfil BIP39-revision.")
    return terminal


def viewer_command(path, options, terminal):
    command = [terminal, "--window", "--wait", "--profile", PROFILE,
               "--working-directory", str(ROOT), "--title", "Revisión de reporte cifrado",
               "--", sys.executable, str(Path(__file__).resolve()), str(path),
               "--visor-interno", "--format", options.format]
    return command


def launch_window(path, options):
    terminal = checked_terminal_profile()
    try:
        result = subprocess.run(viewer_command(path, options, terminal),
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        raise InspectionError("No se pudo abrir la ventana. No se ha revelado el reporte en esta terminal.") from None

    if result.returncode:
        print("Apertura o revisión no completada; pudo haber un error o cancelación.")
        return False

    print("La operación de ventana finalizó; no equivale a una verificación independiente del reporte.")
    return True


def menu(path, options):
    timeout = report.DEFAULT_DECISION_TIMEOUT_SECONDS

    while True:
        print("\nINSPECCIÓN DE REPORTE CIFRADO")
        print("Archivo: " + terminal_text(path.name))
        print("[1] Verificar sin mostrar contenido privado")
        print("[2] Revisar en ventana temporal")
        print("[3] Revelar en esta terminal, con advertencia")
        print("[Q] Salir")
        print(f"Tienes {timeout} segundos para seleccionar una opción y pulsar Enter.")

        try:
            choice = report.timed_input(
                "Opción [1/2/3/Q]: ", timeout_seconds=timeout
            ).strip().lower()
        except report.InputTimeoutError:
            print("\nTiempo de selección agotado. Inspección finalizada.")
            print("No se ha iniciado otra operación.")
            return 1
        except (ValueError, RuntimeError, OSError):
            print("ERROR: no se pudo leer la selección con tiempo límite. Inspección finalizada.")
            return 1

        if choice == "q":
            return 0

        try:
            if choice == "1":
                plain = read_plain(path)
                try:
                    scope = verify_plain(plain, options)
                finally:
                    plain = None
                print("OK: reporte autenticado; no se imprime el contenido privado.")
                print(scope)

            elif choice == "2":
                if launch_window(path, options):
                    print("Inspección finalizada.")
                    return 0
                print("Puedes elegir otra operación explícitamente en el menú.")

            elif choice == "3":
                if reveal_here(path, options):
                    print("\nInspección finalizada.")
                    return 0

            else:
                print("Opción inválida.")

        except InspectionError as exc:
            print("ERROR: " + str(exc))
        except (ValueError, RuntimeError, OSError, TypeError, KeyError):
            print("ERROR: operación no completada; revisar el archivo y el entorno.")


def main():
    global report
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archivo", type=Path)
    parser.add_argument("--format", choices=("auto", "json", "txt"), default="auto")
    parser.add_argument("--words", type=int, choices=(12, 15, 18, 21, 24))
    parser.add_argument("--network", choices=("mainnet", "testnet"))
    parser.add_argument("--input-mode", choices=("words", "entropy_hex", "entropy_bin", "mnemonic", "mnemonic_incomplete"))
    parser.add_argument("--visor-interno", action="store_true", help=argparse.SUPPRESS)
    options = parser.parse_args()
    if not sys.platform.startswith("linux"):
        raise InspectionError("Esta primera versión del inspector está preparada para Linux.")
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        raise InspectionError("La inspección requiere una terminal interactiva; no redirigir su salida.")
    if report is None:
        import bip39_seed_report as report
    path = options.archivo.expanduser().resolve()
    if not path.is_file():
        raise InspectionError("No existe un archivo cifrado legible en la ruta indicada.")
    if options.visor_interno:
        print("REVISIÓN DE REPORTE — no garantiza borrado seguro al cerrar.")
        try:
            reveal_here(path, options, confirm=False)
            input("\nPresiona Enter para terminar la revisión…")
            return 0
        except InspectionError as exc:
            print("ERROR: " + str(exc))
            input("Presiona Enter para cerrar…")
            return 1
    return menu(path, options)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (KeyboardInterrupt, EOFError):
        print("\nInspección cancelada; no se activa una revelación alternativa.")
        sys.exit(1)
    except (InspectionError, ImportError, OSError, ValueError, RuntimeError) as exc:
        print("ERROR: " + str(exc) if isinstance(exc, InspectionError) else
              "ERROR: no se pudo completar la inspección; comprueba el entorno.", file=sys.stderr)
        sys.exit(1)
