#!/usr/bin/env python3
"""Verificacion local de exports de laboratorio; nunca usar con datos reales."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import bip39_seed_report as r
from mnemonic import Mnemonic

EXPECTED_ADDRESSES_PER_FAMILY = 10


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("file")
    p.add_argument("--format", choices=("json", "txt"), default="json")
    p.add_argument("--network", choices=("mainnet", "testnet"), default="testnet")
    p.add_argument("--words", type=int, choices=(12, 15, 18, 21, 24))
    p.add_argument("--input-mode", choices=("words", "entropy_hex", "entropy_bin", "mnemonic", "mnemonic_incomplete", "bip32_seed_hex"))
    p.add_argument("--test-passphrase", default="", help="Solo passphrase ficticia para contrastar la seed")
    a = p.parse_args()
    with Path(a.file).open("rb") as f:
        raw = f.read(r.MAX_ENCRYPTED_REPORT_BYTES + 1)
    require(len(raw) <= r.MAX_ENCRYPTED_REPORT_BYTES, "Archivo demasiado grande")
    password = r.read_hidden_secret("Contrasena del export de prueba: ")
    plain = r.decrypt_report_content(raw.decode("utf-8"), password)
    if a.input_mode == "bip32_seed_hex":
        import inspeccionar_reporte_cifrado as inspector

        require(a.words is None, "--words no aplica a BIP32 directo")
        require(not a.test_passphrase, "La passphrase BIP39 no aplica")
        inspector.report = r
        scope = inspector.verify_plain(
            plain,
            argparse.Namespace(
                format=a.format,
                network=a.network,
                words=None,
                input_mode=a.input_mode,
            ),
        )
        print("OK: export autenticado; no se imprime el secreto.")
        print(scope)
        return
    if a.format == "txt":
        lines = plain.lstrip("\ufeff\r\n ").splitlines()

        require(
            bool(lines)
            and lines[0].strip() == "Offline BIP39 Seed Report",
            "Cabecera de texto inesperada",
        )

        networks = [
            line.partition(":")[2].strip()
            for line in lines
            if ":" in line
            and line.partition(":")[0].strip() == "Network"
        ]

        require(
            networks == [a.network],
            "Red inesperada en texto",
        )

        print(
            "OK: export autenticado y contenido de texto reconocido; "
            "no se imprime el secreto"
        )
        return

    d = json.loads(plain)
    m = Mnemonic("english")
    if a.words is None:
        a.words = 12
    require(d["network"] == a.network, "Red inesperada")
    require(len(d["mnemonic"].split()) == a.words, "Longitud de mnemonic inesperada")
    require(m.check(d["mnemonic"]), "Mnemonic invalida")
    require(bytes(m.to_entropy(d["mnemonic"])).hex() == d["entropy_hex"], "Entropy no coincide")
    require(d["entropy_bits"] == {12:128,15:160,18:192,21:224,24:256}[a.words], "Bits inesperados")
    require(m.to_seed(d["mnemonic"], a.test_passphrase).hex() == d["bip39_seed_hex"], "Seed no coincide con la passphrase de prueba")
    require(d["passphrase_used"] == bool(a.test_passphrase), "Indicador de passphrase inesperado")

    if a.input_mode:
        require(d["input_mode"] == a.input_mode, "Modo de entrada inesperado")
    require(set(d["derivations"]) == {"BIP44", "BIP49", "BIP84", "BIP86", "BIP32_LEGACY"}, "Familias inesperadas")
    require(type(d["gap_limit"]) is int and d["gap_limit"] == EXPECTED_ADDRESSES_PER_FAMILY, "gap_limit inesperado")
    from inspeccionar_reporte_cifrado import verify_bip32_extended_keys
    verify_bip32_extended_keys(d)
    coin = 0 if a.network == "mainnet" else 1
    for family, deriv in d["derivations"].items():
        base_path = "m/0'" if family == "BIP32_LEGACY" else f"m/{int(family[3:])}'/{coin}'/0'"
        require(type(deriv) is dict, "Familia de tipo inesperado")
        for change_index, addresses_key, template_key in (
            (0, "addresses", "path_template"),
            (1, "change_addresses", "change_path_template"),
        ):
            require(
                deriv[template_key] == f"{base_path}/{change_index}/i",
                "Plantilla de ruta inesperada",
            )
            addresses = deriv[addresses_key]
            require(type(addresses) is list, "Lista de direcciones inesperada")
            require(len(addresses) == EXPECTED_ADDRESSES_PER_FAMILY,
                    "Cantidad de direcciones inesperada")
            for i, item in enumerate(addresses):
                require(type(item) is dict, "Entrada de direccion inesperada")
                require(type(item["index"]) is int and item["index"] == i,
                        "Indice inesperado")
                require(item["path"] == f"{base_path}/{change_index}/{i}",
                        "Ruta inesperada")
                require(type(item["address"]) is str and bool(item["address"].strip()),
                        "Direccion vacia o de tipo inesperado")
    print("OK: export autenticado; BIP39, seed y estructura de derivaciones verificados sin imprimir secretos")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("Verificacion cancelada", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print("FALLO de verificacion: " + type(exc).__name__ + "; revisar localmente sin publicar datos privados", file=sys.stderr)
        sys.exit(1)
