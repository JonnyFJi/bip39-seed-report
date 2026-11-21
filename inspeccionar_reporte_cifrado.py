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
import tempfile
import unicodedata

ROOT = Path(__file__).resolve().parent
PROFILE = "BIP39-revision"
report = None


class InspectionError(RuntimeError):
    pass


def _reject_plain_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Clave JSON duplicada.")
        result[key] = value
    return result


def _reject_plain_constant(_value):
    raise ValueError("Constante JSON no admitida.")


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
            data = json.loads(
                plain, object_pairs_hook=_reject_plain_duplicate_keys,
                parse_constant=_reject_plain_constant,
            )
        except (ValueError, RecursionError):
            raise InspectionError("El contenido no es un reporte JSON o TXT reconocido.") from None
        if type(data) is not dict:
            raise InspectionError("La raíz del reporte JSON debe ser un objeto.")
        actual = "json"
    if expected_format != "auto" and expected_format != actual:
        raise InspectionError("El formato interno no coincide con el esperado.")
    return actual, data


def verify_bip32_extended_keys(data):
    # Contraste de coherencia con la seed del reporte; no es una implementación independiente.
    import bip39_seed_report as backend
    block = data["bip32_extended_keys"]
    if type(block) is not dict or set(block) != {"root", "legacy_account"}:
        raise ValueError
    if data.get("input_mode") == backend.BIP32_DIRECT_MODE:
        seed_text = data["bip32_seed_hex"]
        seed = backend.parse_bip32_seed_hex(seed_text)
        if seed.hex() != seed_text:
            raise ValueError
    else:
        seed_text = data["bip39_seed_hex"]
        if (
            type(seed_text) is not str
            or len(seed_text) != 128
            or any(ch not in "0123456789abcdef" for ch in seed_text)
        ):
            raise ValueError
        seed = bytes.fromhex(seed_text)
    expected = backend.build_bip32_extended_keys(seed, data["network"])
    for name, expected_node in expected.items():
        node = block[name]
        if type(node) is not dict:
            raise ValueError
        for key, value in expected_node.items():
            if type(node[key]) is not str or node[key] != value:
                raise ValueError
    master, chain = backend.bip32_master_key(seed)
    if (data["bip32_master_key"] != master or data["bip32_chain_code"] != chain or
            data["bip32_root_key"] != master + chain):
        raise ValueError


def verify_plain(plain, options):
    actual, data = parse_plain(plain, options.format)
    if actual == "txt":
        networks = [line.partition(":")[2].strip() for line in plain.splitlines()
                    if line.partition(":")[0].strip() == "Network"]
        if len(networks) != 1 or networks[0] not in {"mainnet", "testnet"}:
            raise InspectionError("Red de reporte TXT no admitida.")
        if options.network is not None and networks[0] != options.network:
            raise InspectionError("La red no coincide con la esperada.")
        if options.input_mode == "bip32_seed_hex":
            if options.words is not None:
                raise InspectionError("--words no aplica a una entrada BIP32 directa.")
            modes = [
                value.strip()
                for line in plain.splitlines()
                for field, separator, value in [line.partition(":")]
                if separator and field.strip() == "Input mode"
            ]
            if modes != ["bip32_seed_hex"]:
                raise InspectionError("El modo de entrada TXT no coincide con el esperado.")
        return "TXT: autenticación, cabecera y red; no se comprueban BIP39, seed ni todas las derivaciones."
    try:
        if type(data["network"]) is not str or data["network"] not in {"mainnet", "testnet"}:
            raise ValueError
        gap = data["gap_limit"]
        if type(gap) is not int:
            raise ValueError
        if gap != report.GAP_LIMIT:
            raise InspectionError(
                f"Estructura de reporte no compatible: gap_limit={gap}; "
                f"esta versión espera {report.GAP_LIMIT}. "
                "El archivo se autenticó correctamente; esto no indica una contraseña incorrecta. "
                "Utiliza la versión del proyecto con la que se generó el reporte "
                "(para cinco direcciones por familia: pre-release baseline-5-2026-11-14)."
            )
        if (type(data["input_mode"]) is not str or
                data["input_mode"] not in {"words", "entropy_hex", "entropy_bin", "mnemonic", "mnemonic_incomplete", "bip32_seed_hex"}):
            raise ValueError
        if options.network is not None and data["network"] != options.network:
            raise InspectionError("La red no coincide con la esperada.")
        if options.input_mode is not None and data["input_mode"] != options.input_mode:
            raise InspectionError("El modo de entrada no coincide con el esperado.")

        direct = data["input_mode"] == "bip32_seed_hex"
        if direct:
            if options.words is not None:
                raise InspectionError("--words no aplica a una entrada BIP32 directa.")
            bip39_fields = {
                "mnemonic", "mnemonic_valid", "entropy_bits", "entropy_bin",
                "entropy_hex", "entropy_checksum", "checksum_valid",
                "passphrase_used", "bip39_seed_hex", "indicadores_mnemonic",
                "passphrase_audit", "entropy_generation",
            }
            if bip39_fields.intersection(data):
                raise ValueError
        else:
            if "bip32_seed_hex" in data or type(data["passphrase_used"]) is not bool:
                raise ValueError
            if type(data["mnemonic"]) is not str or not data["mnemonic"].strip():
                raise ValueError
            if type(data["entropy_hex"]) is not str or type(data["entropy_bits"]) is not int:
                raise ValueError
            recovered = report.mnemonic_to_entropy(data["mnemonic"])
            count = len(data["mnemonic"].split())
            if options.words is not None and count != options.words:
                raise InspectionError("El número de palabras no coincide con el esperado.")
            if recovered["entropy"].hex() != data["entropy_hex"] or not recovered["checksum_valid"]:
                raise ValueError
            if data["entropy_bits"] != len(recovered["entropy"]) * 8:
                raise ValueError
            if not data["passphrase_used"]:
                expected_seed = report.Mnemonic("english").to_seed(data["mnemonic"], "").hex()
                if expected_seed != data["bip39_seed_hex"]:
                    raise ValueError
        if type(data["derivations"]) is not dict:
            raise ValueError
        families = set(data["derivations"])
        if families == {"BIP44", "BIP49", "BIP84", "BIP86"}:
            raise InspectionError(
                "Estructura anterior: falta la sección BIP32_LEGACY. "
                "El archivo se autenticó correctamente; esto no indica una contraseña incorrecta."
            )
        if families != {"BIP44", "BIP49", "BIP84", "BIP86", "BIP32_LEGACY"}:
            raise ValueError
        if "bip32_extended_keys" not in data:
            raise InspectionError(
                "Estructura anterior o incompleta: faltan claves extendidas BIP32. "
                "El archivo se autenticó correctamente; esto no indica una contraseña incorrecta."
            )
        verify_bip32_extended_keys(data)
        coin = 0 if data["network"] == "mainnet" else 1
        for family, item in data["derivations"].items():
            if type(item) is not dict:
                raise ValueError
            base_path = "m/0'" if family == "BIP32_LEGACY" else f"m/{family[3:]}'/{coin}'/0'"
            if family == "BIP32_LEGACY":
                if (item["address_type"] != "P2PKH" or
                        item["xpub"] != data["bip32_extended_keys"]["legacy_account"]["extended_public_key"]):
                    raise ValueError
            if ("change_addresses" not in item or
                    "change_path_template" not in item):
                raise InspectionError(
                    "Estructura anterior o incompleta: faltan campos de cambio. "
                    "El archivo se autenticó correctamente; esto no indica una contraseña incorrecta. "
                    "Esta versión requiere recepción y cambio en las cinco secciones."
                )
            for change_index, addresses_key, template_key in (
                (0, "addresses", "path_template"),
                (1, "change_addresses", "change_path_template"),
            ):
                expected_template = f"{base_path}/{change_index}/i"
                if (type(item[template_key]) is not str or
                        item[template_key] != expected_template):
                    raise ValueError
                addresses = item[addresses_key]
                if type(addresses) is not list or len(addresses) != report.GAP_LIMIT:
                    raise ValueError
                for index, address in enumerate(addresses):
                    if type(address) is not dict:
                        raise ValueError
                    if type(address["index"]) is not int or address["index"] != index:
                        raise ValueError
                    if type(address["address"]) is not str or not address["address"].strip():
                        raise ValueError
                    if (type(address["path"]) is not str or
                            address["path"] != f"{base_path}/{change_index}/{index}"):
                        raise ValueError
    except InspectionError:
        raise
    except (ValueError, TypeError, KeyError, AttributeError, IndexError):
        raise InspectionError("Las comprobaciones internas del reporte no coinciden.") from None
    if direct:
        return (
            "JSON BIP32 directo: claves extendidas coherentes con la seed "
            "declarada y estructura comprobada; no se verifican "
            "independientemente todas las direcciones."
        )
    if data["passphrase_used"]:
        return "JSON: BIP39 y estructura comprobados; seed no contrastada con la passphrase BIP39 no vacía; claves extendidas coherentes con la seed declarada."
    return "JSON: BIP39, seed con passphrase vacía y estructura comprobados; claves extendidas coherentes con la seed declarada; no se verifican independientemente todas las direcciones."

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

def show_graphical_text(root, tk, ttk, plain):
    root.title("Reporte privado — visor de solo lectura")
    root.geometry("1000x650")
    root.minsize(560, 300)
    root.columnconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)

    toolbar = ttk.Frame(root, padding=8)
    toolbar.grid(row=0, column=0, sticky="ew")
    toolbar.columnconfigure(1, weight=1)

    ttk.Label(toolbar, text="Buscar:").grid(row=0, column=0)
    query = ttk.Entry(toolbar)
    query.grid(row=0, column=1, sticky="ew", padx=6)
    status = ttk.Label(toolbar, text="")
    status.grid(row=0, column=3, padx=6)
    ttk.Button(toolbar, text="Cerrar", command=root.quit).grid(row=0, column=4)

    panel = ttk.Frame(root, padding=(8, 0, 8, 8))
    panel.grid(row=1, column=0, sticky="nsew")
    panel.columnconfigure(0, weight=1)
    panel.rowconfigure(0, weight=1)

    text = tk.Text(panel, wrap="none", undo=False, exportselection=False)
    vertical = ttk.Scrollbar(panel, orient="vertical", command=text.yview)
    horizontal = ttk.Scrollbar(panel, orient="horizontal", command=text.xview)
    text.configure(yscrollcommand=vertical.set, xscrollcommand=horizontal.set)
    text.grid(row=0, column=0, sticky="nsew")
    vertical.grid(row=0, column=1, sticky="ns")
    horizontal.grid(row=1, column=0, sticky="ew")

    text.insert("1.0", plain)
    text.configure(state="disabled")
    text.tag_configure("match", background="#ffe066", foreground="#111111")
    for event in ("<<Copy>>", "<<Cut>>", "<<Paste>>"):
        text.bind(event, lambda _event: "break")

    next_start = "1.0"

    def reset_search(_event=None):
        nonlocal next_start
        next_start = "1.0"
        text.tag_remove("match", "1.0", "end")
        status.configure(text="")

    def find_next(_event=None):
        nonlocal next_start
        term = query.get()
        text.tag_remove("match", "1.0", "end")
        if not term:
            status.configure(text="")
            return "break"

        count = tk.IntVar(master=root)
        match = text.search(
            term, next_start, stopindex="end", nocase=True, count=count,
        )
        wrapped = False
        if not match and next_start != "1.0":
            match = text.search(
                term, "1.0", stopindex="end", nocase=True, count=count,
            )
            wrapped = bool(match)

        if match:
            next_start = text.index(f"{match}+{count.get()}c")
            text.tag_add("match", match, next_start)
            text.see(match)
            status.configure(text="Desde el inicio" if wrapped else "Encontrado")
        else:
            status.configure(text="Sin coincidencias")
        return "break"

    ttk.Button(toolbar, text="Siguiente", command=find_next).grid(row=0, column=2)
    query.bind("<KeyRelease>", reset_search)
    query.bind("<Return>", find_next)
    query.bind("<KeyRelease-Return>", lambda _event: "break")
    root.bind("<Escape>", lambda _event: root.quit())
    root.protocol("WM_DELETE_WINDOW", root.quit)

    root.deiconify()
    query.focus_set()
    root.mainloop()


def launch_graphical_viewer(path, options):
    try:
        import tkinter as tk
        from tkinter import messagebox, ttk
    except ImportError:
        raise InspectionError("Tk no está disponible en este intérprete.") from None

    root = None
    plain = None
    try:
        root = tk.Tk()
        root.withdraw()

        if not messagebox.askyesno(
            "Mostrar contenido privado",
            "El reporte contiene secretos. Solo ábrelo en una sesión privada.\n\n"
            "Si continúas, vuelve a la terminal para introducir la contraseña. "
            "El contenido del reporte se mostrará únicamente en la ventana.\n\n"
            "¿Continuar?",
            parent=root,
            default=messagebox.NO,
        ):
            return False

        plain = read_plain(path)
        parse_plain(plain, options.format)
        show_graphical_text(root, tk, ttk, plain)
        return True
    except tk.TclError:
        raise InspectionError(
            "No se pudo iniciar o completar el visor gráfico. "
            "No se abrirá una alternativa en terminal."
        ) from None
    finally:
        plain = None
        if root is not None:
            try:
                root.destroy()
            except tk.TclError:
                pass


def launch_external_editor(path, options):
    opener = shutil.which("xdg-open")
    if opener is None:
        raise InspectionError(
            "No está disponible xdg-open. No se ha descifrado el reporte."
        )

    print(
        "\nADVERTENCIA: se creará una copia temporal sin cifrar.\n"
        "La aplicación externa puede permitir copiar, editar o guardar el "
        "reporte, y puede conservar copias o restaurar la sesión.\n"
        "El inspector intentará retirar su copia temporal, pero no puede "
        "garantizar el borrado seguro ni eliminar copias de la aplicación.\n"
        "Un cierre forzado puede dejar la copia en el equipo.\n"
        "Para leer sin crear este archivo temporal, usa la opción 4."
    )

    try:
        answer = report.timed_input(
            "¿Abrir en la aplicación externa? [s/N]: ",
            timeout_seconds=report.DEFAULT_DECISION_TIMEOUT_SECONDS,
        )
    except report.InputTimeoutError:
        print("Tiempo de confirmación agotado. No se ha descifrado el reporte.")
        return False

    if answer.strip().lower() != "s":
        print("Apertura cancelada. No se ha descifrado el reporte.")
        return False

    plain = read_plain(path)
    directory = None
    copy_path = None
    try:
        parse_plain(plain, options.format)

        directory = tempfile.TemporaryDirectory(prefix="bip39-editor-")
        copy_path = Path(directory.name) / "reporte.txt"
        fd = os.open(copy_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(plain)
        plain = None

        try:
            result = subprocess.run(
                [opener, str(copy_path)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except OSError:
            raise InspectionError(
                "No se pudo iniciar la aplicación externa."
            ) from None

        if result.returncode != 0:
            raise InspectionError(
                "La aplicación externa no confirmó la apertura del archivo."
            )

        input(
            "\nCierra el documento en la aplicación externa y luego pulsa Enter "
            "para retirar la copia temporal: "
        )
    finally:
        plain = None
        if directory is not None:
            try:
                directory.cleanup()
            except OSError:
                raise InspectionError(
                    "No se pudo retirar la copia temporal sin cifrar. "
                    "Revisa esta ruta local: " + terminal_text(copy_path)
                ) from None

    print("Copia temporal retirada. La aplicación externa pudo conservar otras copias.")
    return True


def menu(path, options):
    timeout = report.DEFAULT_DECISION_TIMEOUT_SECONDS

    while True:
        print("\nINSPECCIÓN DE REPORTE CIFRADO")
        print("Archivo: " + terminal_text(path.name))
        print("[1] Verificar sin mostrar contenido privado")
        print("[2] Revisar en ventana temporal")
        print("[3] Revelar en esta terminal, con advertencia")
        print("[4] Visor gráfico de solo lectura")
        print("[5] Abrir en editor externo — ADVERTENCIA: crea una copia temporal sin cifrar")
        print("[Q] Salir")
        print(f"Tienes {timeout} segundos para seleccionar una opción y pulsar Enter.")

        try:
            choice = report.timed_input(
                "Opción [1/2/3/4/5/Q]: ", timeout_seconds=timeout
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

            elif choice == "4":
                if launch_graphical_viewer(path, options):
                    print("\nInspección finalizada.")
                    return 0

            elif choice == "5":
                if launch_external_editor(path, options):
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
    parser.add_argument("--input-mode", choices=("words", "entropy_hex", "entropy_bin", "mnemonic", "mnemonic_incomplete", "bip32_seed_hex"))
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
