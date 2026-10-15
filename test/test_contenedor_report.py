#!/usr/bin/env python3
"""Regresion del contenedor: solo datos ficticios, sin reportes en disco."""
import base64
import contextlib
import copy
import hashlib
import io
import json
import os
import unittest
from unittest.mock import patch

import bip39_seed_report as report
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class KDFReached(Exception):
    pass


def b64(data):
    return base64.b64encode(data).decode("ascii")


class ContainerTests(unittest.TestCase):
    def setUp(self):
        self.password = "Solo-laboratorio-no-usar-2026"
        self.container = {
            "format": report.ENCRYPTED_REPORT_FORMAT,
            "version": report.ENCRYPTED_REPORT_VERSION,
            "cipher": {
                "name": report.ENCRYPTED_REPORT_CIPHER,
                "nonce_b64": b64(b"n" * report.AES_GCM_NONCE_BYTES),
            },
            "kdf": {
                "name": report.ENCRYPTED_REPORT_KDF,
                "n": report.SCRYPT_N,
                "r": report.SCRYPT_R,
                "p": report.SCRYPT_P,
                "dklen": report.SCRYPT_DKLEN,
                "salt_b64": b64(b"s" * report.SCRYPT_SALT_BYTES),
            },
            "ciphertext_b64": b64(b"t" * report.AES_GCM_TAG_BYTES),
        }

    def reject(self, value, expected=ValueError):
        text = json.dumps(value) if isinstance(value, (dict, list)) else value
        with patch.object(report, "_derive_scrypt_key",
                          side_effect=AssertionError("KDF invocada antes del rechazo")) as kdf:
            with self.assertRaises(expected):
                report.decrypt_report_content(text, self.password)
            kdf.assert_not_called()

    def reaches_kdf(self, text):
        with patch.object(report, "_derive_scrypt_key", side_effect=KDFReached) as kdf:
            with self.assertRaises(KDFReached):
                report.decrypt_report_content(text, self.password)
            kdf.assert_called_once()

    def test_01_valid_structure_reaches_kdf(self):
        self.reaches_kdf(json.dumps(self.container))

    def test_02_input_type(self):
        for value in (None, 123, True, b"{}"):
            with self.subTest(type=type(value).__name__):
                self.reject(value, TypeError)

    def test_03_invalid_json_and_root(self):
        for text in ("", "{", "[]", "null", "true", "42", '"texto"'):
            with self.subTest(text=text):
                self.reject(text)

    def test_04_duplicate_keys(self):
        raw = json.dumps(self.container)
        cases = [
            raw.replace('"version": 1', '"version": 1, "version": 1', 1),
            raw.replace('"n": 262144', '"n": 262144, "n": 262144', 1),
            raw.replace('"name": "AES-256-GCM"',
                        '"name": "AES-256-GCM", "name": "AES-256-GCM"', 1),
            raw.replace('"version": 1', '"version": 1, "ver\u0073ion": 1', 1),
        ]
        for i, text in enumerate(cases):
            self.assertNotEqual(text, raw, "Fixture de duplicados no construida")
            with self.subTest(case=i):
                self.reject(text)

    def test_05_nonstandard_constants(self):
        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant):
                self.reject('{"version": ' + constant + '}')

    def test_06_missing_and_extra_keys(self):
        for section in (None, "cipher", "kdf"):
            target = self.container if section is None else self.container[section]
            for key in target:
                c = copy.deepcopy(self.container)
                obj = c if section is None else c[section]
                del obj[key]
                with self.subTest(section=section, missing=key):
                    self.reject(c)
            c = copy.deepcopy(self.container)
            obj = c if section is None else c[section]
            obj["unexpected"] = "dato ficticio"
            with self.subTest(section=section, extra=True):
                self.reject(c)

    def test_07_metadata_and_types(self):
        for field, values in (("format", ("otro", None, 1, [])),
                              ("version", (0, 2, True, "1", 1.0, None))):
            for value in values:
                c = copy.deepcopy(self.container)
                c[field] = value
                with self.subTest(field=field, value=value):
                    self.reject(c)
        for section in ("cipher", "kdf"):
            for value in (None, [], "texto", 7):
                c = copy.deepcopy(self.container)
                c[section] = value
                with self.subTest(section=section, value=value):
                    self.reject(c)
            c = copy.deepcopy(self.container)
            c[section]["name"] = "no-admitido"
            self.reject(c)

    def test_08_kdf_parameters(self):
        for key in ("n", "r", "p", "dklen"):
            for value in (True, None, "1", 1.0, 0, self.container["kdf"][key] + 1):
                c = copy.deepcopy(self.container)
                c["kdf"][key] = value
                with self.subTest(key=key, value=value):
                    self.reject(c)

    def test_09_base64_types_and_encoding(self):
        for section, key in ((None, "ciphertext_b64"), ("cipher", "nonce_b64"),
                             ("kdf", "salt_b64")):
            for value in (None, 12, [], {}, "%%%", "é", "a==="):
                c = copy.deepcopy(self.container)
                obj = c if section is None else c[section]
                obj[key] = value
                with self.subTest(section=section, key=key, value=value):
                    self.reject(c)

    def test_10_salt_and_nonce_lengths(self):
        for section, key, size in (("cipher", "nonce_b64", report.AES_GCM_NONCE_BYTES),
                                   ("kdf", "salt_b64", report.SCRYPT_SALT_BYTES)):
            for length in (0, size - 1, size + 1):
                c = copy.deepcopy(self.container)
                c[section][key] = b64(b"x" * length)
                with self.subTest(key=key, length=length):
                    self.reject(c)

    def test_11_ciphertext_boundaries_scaled(self):
        with patch.object(report, "MAX_REPORT_PLAINTEXT_BYTES", 32):
            for length in (0, report.AES_GCM_TAG_BYTES - 1, 49):
                c = copy.deepcopy(self.container)
                c["ciphertext_b64"] = b64(b"x" * length)
                with self.subTest(reject_length=length):
                    self.reject(c)
            for length in (16, 48):
                c = copy.deepcopy(self.container)
                c["ciphertext_b64"] = b64(b"x" * length)
                self.reaches_kdf(json.dumps(c))

    def test_12_container_boundaries_scaled(self):
        with patch.object(report, "MAX_ENCRYPTED_REPORT_BYTES", 1024):
            raw = json.dumps(self.container)
            self.assertLess(len(raw), 1024)
            self.reaches_kdf(raw + " " * (1024 - len(raw)))
            self.reject(raw + " " * (1025 - len(raw)))
            self.reject("é" * 600)
            self.reject("\ud800")

    def test_13_deep_json(self):
        self.reject("[" * 2000 + "]" * 2000)

    def test_14_plaintext_rejected_before_kdf_scaled(self):
        with patch.object(report, "MAX_REPORT_PLAINTEXT_BYTES", 32):
            for value in ("x" * 33, "é" * 17, "\ud800", None):
                expected = TypeError if value is None else ValueError
                with self.subTest(type=type(value).__name__):
                    with patch.object(report, "_derive_scrypt_key") as kdf:
                        with self.assertRaises(expected):
                            report._encrypt_report_content(value, self.password)
                        kdf.assert_not_called()

    def test_15_boundary_roundtrip_with_stub_kdf(self):
        with patch.object(report, "MAX_REPORT_PLAINTEXT_BYTES", 32):
            with patch.object(report, "_derive_scrypt_key", return_value=b"k" * 32):
                for content in ("", "x" * 32, "é" * 16):
                    encrypted = report._encrypt_report_content(content, self.password)
                    self.assertEqual(report.decrypt_report_content(encrypted, self.password), content)

    def test_16_real_scrypt_unicode_roundtrip(self):
        original_kdf = report._derive_scrypt_key
        content = "Texto ficticio: café; no contiene claves."
        with patch.object(report, "_derive_scrypt_key", wraps=original_kdf) as kdf:
            encrypted = report._encrypt_report_content(content, self.password)
            recovered = report.decrypt_report_content(encrypted, self.password)
            self.assertEqual(content, recovered)
            self.assertEqual(kdf.call_count, 2)

    def test_17_legacy_compatibility_and_alias(self):
        for password in ("legacy-ascii", "legacy-é"):
            for content in ("", "Prueba-é"):
                nonce = os.urandom(report.AES_GCM_NONCE_BYTES)
                key = hashlib.sha256(password.encode("utf-8")).digest()
                ciphertext = AESGCM(key).encrypt(nonce, content.encode("utf-8"), None)
                encrypted = "ENCRYPTED:" + b64(nonce + ciphertext)
                with self.subTest(unicode_password="é" in password, empty=not content):
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(report.decrypt_report_content(encrypted, password), content)
                        self.assertEqual(report.decrypt_file_content(encrypted, password), content)

    def test_18_legacy_malformed(self):
        for payload in ("%%%", b64(b"x" * 12), b64(b"x" * 27)):
            with self.subTest(payload_size=len(payload)):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.reject("ENCRYPTED:" + payload)
        with patch.object(report, "MAX_REPORT_PLAINTEXT_BYTES", 32):
            with contextlib.redirect_stdout(io.StringIO()):
                self.reject("ENCRYPTED:" + b64(b"x" * 61))


if __name__ == "__main__":
    unittest.main(verbosity=2)
