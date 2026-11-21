"""Legacy y claves extendidas: datos públicos/ficticios, nunca fondos reales.
Vectores 1 y 3 de BIP32, autor Pieter Wuille, documento BSD-2-Clause:
https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki
Solo se incluyen sus pares m y m/0'; no toda la suite BIP32.
"""
import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from Crypto.Hash import RIPEMD160

import bip39_seed_report as r
import inspeccionar_reporte_cifrado as inspector

VECTORS = [('000102030405060708090a0b0c0d0e0f', 'xpub661MyMwAqRbcFtXgS5sYJABqqG9YLmC4Q1Rdap9gSE8NqtwybGhePY2gZ29ESFjqJoCu1Rupje8YtGqsefD265TMg7usUDFdp6W1EGMcet8', 'xprv9s21ZrQH143K3QTDL4LXw2F7HEK3wJUD2nW2nRk4stbPy6cq3jPPqjiChkVvvNKmPGJxWUtg6LnF5kejMRNNU3TGtRBeJgk33yuGBxrMPHi', 'xpub68Gmy5EdvgibQVfPdqkBBCHxA5htiqg55crXYuXoQRKfDBFA1WEjWgP6LHhwBZeNK1VTsfTFUHCdrfp1bgwQ9xv5ski8PX9rL2dZXvgGDnw', 'xprv9uHRZZhk6KAJC1avXpDAp4MDc3sQKNxDiPvvkX8Br5ngLNv1TxvUxt4cV1rGL5hj6KCesnDYUhd7oWgT11eZG7XnxHrnYeSvkzY7d2bhkJ7'), ('4b381541583be4423346c643850da4b320e46a87ae3d2a4e6da11eba819cd4acba45d239319ac14f863b8d5ab5a0d0c64d2e8a1e7d1457df2e5a3c51c73235be', 'xpub661MyMwAqRbcEZVB4dScxMAdx6d4nFc9nvyvH3v4gJL378CSRZiYmhRoP7mBy6gSPSCYk6SzXPTf3ND1cZAceL7SfJ1Z3GC8vBgp2epUt13', 'xprv9s21ZrQH143K25QhxbucbDDuQ4naNntJRi4KUfWT7xo4EKsHt2QJDu7KXp1A3u7Bi1j8ph3EGsZ9Xvz9dGuVrtHHs7pXeTzjuxBrCmmhgC6', 'xpub68NZiKmJWnxxS6aaHmn81bvJeTESw724CRDs6HbuccFQN9Ku14VQrADWgqbhhTHBaohPX4CjNLf9fq9MYo6oDaPPLPxSb7gwQN3ih19Zm4Y', 'xprv9uPDJpEQgRQfDcW7BkF7eTya6RPxXeJCqCJGHuCJ4GiRVLzkTXBAJMu2qaMWPrS7AANYqdq6vcBcBUdJCVVFceUvJFjaPdGZ2y9WACViL4L')]
PHRASE = " ".join(["abandon"] * 11 + ["about"])


def payload(text):
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    number = 0
    for ch in text:
        number = number * 58 + alphabet.index(ch)
    raw = number.to_bytes((number.bit_length() + 7) // 8, "big")
    raw = b"\x00" * (len(text) - len(text.lstrip("1"))) + raw
    body, check = raw[:-4], raw[-4:]
    if hashlib.sha256(hashlib.sha256(body).digest()).digest()[:4] != check:
        raise ValueError("Checksum Base58Check incorrecto")
    return body


def context(network="testnet", passphrase=""):
    args = argparse.Namespace(words=None, entropy_bin="", entropy_hex="", mnemonic=PHRASE,
                              mnemonic_incomplete="", network=network, passphrase=passphrase,
                              audit_passphrase=False)
    return r.build_context(args)


class LegacyBip32Tests(unittest.TestCase):
    def verify(self, data):
        options = argparse.Namespace(format="json", network=data["network"], words=12, input_mode="mnemonic")
        with patch.object(inspector, "report", r):
            return inspector.verify_plain(json.dumps(data), options)

    def test_01_reference_vectors_root_and_hardened_account(self):
        for seed, root_pub, root_prv, account_pub, account_prv in VECTORS:
            with self.subTest(seed_length=len(seed)):
                block = r.build_bip32_extended_keys(bytes.fromhex(seed), "mainnet")
                self.assertEqual(block["root"]["extended_public_key"], root_pub)
                self.assertEqual(block["root"]["extended_private_key"], root_prv)
                self.assertEqual(block["legacy_account"]["extended_public_key"], account_pub)
                self.assertEqual(block["legacy_account"]["extended_private_key"], account_prv)

    def test_02_network_versions_depth_indexes_and_parent(self):
        seed = bytes.fromhex(VECTORS[0][0])
        for network, pub_ver, prv_ver in (
            ("mainnet", "0488b21e", "0488ade4"), ("testnet", "043587cf", "04358394"),
        ):
            block = r.build_bip32_extended_keys(seed, network)
            root_pub = payload(block["root"]["extended_public_key"])
            fingerprint = RIPEMD160.new(
                hashlib.sha256(root_pub[45:]).digest()
            ).digest()[:4]
            for name, depth, index, parent in (
                ("root", 0, 0, bytes(4)), ("legacy_account", 1, 0x80000000, fingerprint),
            ):
                for field, version in (("extended_public_key", pub_ver), ("extended_private_key", prv_ver)):
                    body = payload(block[name][field])
                    self.assertEqual(len(body), 78)
                    self.assertEqual(body[:4].hex(), version)
                    self.assertEqual(body[4], depth)
                    self.assertEqual(body[5:9], parent)
                    self.assertEqual(int.from_bytes(body[9:13], "big"), index)
                self.assertEqual(block[name]["network"], network)

    def test_03_extended_keys_round_trip(self):
        for network in ("mainnet", "testnet"):
            versions = r.bip32_network_parameters(network)["versions"]
            for node in r.build_bip32_extended_keys(bytes(range(32)), network).values():
                private = r.Bip32Slip10Secp256k1.FromExtendedKey(node["extended_private_key"], key_net_ver=versions)
                public = r.Bip32Slip10Secp256k1.FromExtendedKey(node["extended_public_key"], key_net_ver=versions)
                self.assertEqual(private.PrivateKey().ToExtended(), node["extended_private_key"])
                self.assertEqual(private.PublicKey().ToExtended(), node["extended_public_key"])
                self.assertEqual(public.PublicKey().ToExtended(), node["extended_public_key"])

    def test_04_existing_hex_fields_are_preserved(self):
        for network in ("mainnet", "testnet"):
            data = context(network)
            body = payload(data["bip32_extended_keys"]["root"]["extended_private_key"])
            self.assertEqual(body[45], 0)
            self.assertEqual(body[46:].hex(), data["bip32_master_key"])
            self.assertEqual(body[13:45].hex(), data["bip32_chain_code"])
            self.assertEqual(data["bip32_root_key"], data["bip32_master_key"] + data["bip32_chain_code"])

    def test_05_legacy_paths_and_p2pkh_encoding(self):
        for network, version in (("mainnet", 0), ("testnet", 111)):
            item = r.derive_addresses_bip32_legacy(bytes(range(32)), network)
            for chain, key in ((0, "addresses"), (1, "change_addresses")):
                self.assertEqual(len(item[key]), 10)
                for i, address in enumerate(item[key]):
                    self.assertEqual(address["path"], f"m/0'/{chain}/{i}")
                    self.assertEqual(address["index"], i)
                    public = bytes.fromhex(address["public_key_hex"])
                    expected_hash = RIPEMD160.new(
                        hashlib.sha256(public).digest()
                    ).digest()
                    self.assertEqual(payload(address["address"]), bytes([version]) + expected_hash)

    def test_06_legacy_wif_matches_private_derivation(self):
        seed = bytes(range(32))
        for network, version in (("mainnet", 128), ("testnet", 239)):
            item = r.derive_addresses_bip32_legacy(seed, network)
            root = r.bip32_root_node(seed, network)
            for chain, key in ((0, "addresses"), (1, "change_addresses")):
                for i, address in enumerate(item[key]):
                    node = root.DerivePath(f"m/0'/{chain}/{i}")
                    self.assertEqual(payload(address["private_key_wif"]),
                                     bytes([version]) + node.PrivateKey().Raw().ToBytes() + b"\x01")
                    self.assertEqual(address["public_key_hex"], node.PublicKey().RawCompressed().ToHex())

    def test_07_network_changes_encoding_not_legacy_key_material(self):
        seed = bytes(range(32))
        main = r.derive_addresses_bip32_legacy(seed, "mainnet")
        test = r.derive_addresses_bip32_legacy(seed, "testnet")
        for key in ("addresses", "change_addresses"):
            for a, b in zip(main[key], test[key]):
                self.assertEqual(a["public_key_hex"], b["public_key_hex"])
                self.assertEqual(a["path"], b["path"])
                self.assertNotEqual(a["address"], b["address"])
                self.assertNotEqual(a["private_key_wif"], b["private_key_wif"])

    def test_08_invalid_parameters_are_rejected(self):
        for count in (0, -1, True, 10.0, "10"):
            with self.assertRaises(ValueError):
                r.derive_addresses_bip32_legacy(bytes(range(32)), "testnet", count)
        for function in (r.bip32_network_parameters,):
            with self.assertRaises(ValueError):
                function("red-invalida")

    def test_09_context_has_one_hundred_addresses(self):
        for network in ("mainnet", "testnet"):
            data = context(network)
            self.assertEqual(set(data["derivations"]), {"BIP44", "BIP49", "BIP84", "BIP86", "BIP32_LEGACY"})
            self.assertEqual(sum(len(item[k]) for item in data["derivations"].values()
                                 for k in ("addresses", "change_addresses")), 100)
            self.verify(data)

    def test_10_inspector_rejects_wrong_extended_keys_and_metadata(self):
        data = context()
        for name, key, value in (
            ("root", "extended_public_key", "invalida"),
            ("root", "extended_private_key", data["bip32_extended_keys"]["legacy_account"]["extended_private_key"]),
            ("legacy_account", "network", "mainnet"),
            ("legacy_account", "path", "m/0"),
        ):
            candidate = json.loads(json.dumps(data))
            candidate["bip32_extended_keys"][name][key] = value
            with self.assertRaises(inspector.InspectionError):
                self.verify(candidate)
        candidate = context()
        candidate["bip32_master_key"] = "00" * 32
        with self.assertRaises(inspector.InspectionError):
            self.verify(candidate)

    def test_11_inspector_separates_old_schema_from_password_errors(self):
        for missing in ("legacy", "extended"):
            data = context()
            if missing == "legacy":
                del data["derivations"]["BIP32_LEGACY"]
            else:
                del data["bip32_extended_keys"]
            with self.assertRaises(inspector.InspectionError) as error:
                self.verify(data)
            self.assertIn("autenticó correctamente", str(error.exception))
            self.assertNotIn("No se pudo autenticar", str(error.exception))

    def test_12_compact_and_show_all_hide_new_extended_block(self):
        data = context()
        keys = data["bip32_extended_keys"]
        hidden = [keys["root"]["extended_public_key"], keys["root"]["extended_private_key"],
                  keys["legacy_account"]["extended_private_key"]]
        for kwargs in ({}, {"show_all": True}):
            text = r.format_report(data, **kwargs)
            for value in hidden:
                self.assertNotIn(value, text)
            legacy = data["derivations"]["BIP32_LEGACY"]
            self.assertIn(legacy["addresses"][0]["address"], text)
            for a in legacy["addresses"][1:] + legacy["change_addresses"]:
                self.assertNotIn(a["address"], text)

    def test_13_encrypted_exports_keep_legacy_and_extended_keys(self):
        data = context(passphrase="TREZOR")
        with tempfile.TemporaryDirectory(prefix="bip39-legacy-export-") as directory:
            for fmt in ("json", "txt"):
                path = r.export_seed_report(data, Path(directory) / ("prueba." + fmt), fmt,
                                            "clave-ficticia-larga")
                plain = r.decrypt_report_content(path.read_text(encoding="utf-8"), "clave-ficticia-larga")
                if fmt == "json":
                    self.assertEqual(json.loads(plain), data)
                    self.assertIn("seed no contrastada", self.verify(data))
                else:
                    for node in data["bip32_extended_keys"].values():
                        self.assertIn(node["extended_private_key"], plain)
                        self.assertIn(node["extended_public_key"], plain)
                    for item in data["derivations"].values():
                        for a in item["addresses"] + item["change_addresses"]:
                            self.assertIn(a["address"], plain)


if __name__ == "__main__":
    unittest.main(verbosity=2)
