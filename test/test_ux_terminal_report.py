"""UX con datos ficticios. No valida derivaciones criptográficas independientes."""
import argparse
import contextlib
import copy
import io
import json
from pathlib import Path
import shlex
import sys
import tempfile
import unittest
from unittest.mock import patch

import bip39_seed_report as report


def fictitious_context():
    data = {
        "coin_type_label": "Bitcoin", "network": "testnet", "input_mode": "words",
        "entropy_bits": 128, "entropy_bin": "ENTROPY_BIN_PRIVADA_FICTICIA",
        "entropy_hex": "ENTROPY_HEX_PRIVADA_FICTICIA", "entropy_checksum": "1010",
        "checksum_valid": True, "mnemonic": " ".join(["palabra-demo"] * 12),
        "mnemonic_valid": True, "passphrase_used": False,
        "bip39_seed_hex": "SEED_PRIVADA_FICTICIA", "bip32_root_key": "ROOT_PRIVADA_FICTICIA",
        "bip32_master_key": "MASTER_PRIVADA_FICTICIA",
        "bip32_chain_code": "CHAIN_CODE_PRIVADO_FICTICIO", "gap_limit": 5,
        "derivations": {},
        "indicadores_mnemonic": {
            "valid": True, "word_count": 12, "unique_words": 1,
            "repeated_total": 11, "repeated_word_count": 1,
            "consecutive_indexes": 0, "consecutive_repetitions": 11,
            "indicators": ["PATRON_FICTICIO"], "limitation": "LIMITACION_FICTICIA",
        },
    }
    for number, kind, key in [(44, "P2PKH", "xpub"), (49, "P2WPKH-P2SH", "ypub"),
                              (84, "P2WPKH", "zpub"), (86, "P2TR", None)]:
        item = {"path_template": f"m/{number}'/1'/0'/0/i", "address_type": kind,
                "addresses": [{"index": i, "path": f"m/{number}'/1'/0'/0/{i}",
                               "address": f"DIRECCION_FICTICIA_{number}_{i}",
                               "private_key_wif": f"WIF_PRIVADO_FICTICIO_{number}_{i}",
                               "public_key_hex": f"PUBLICA_FICTICIA_{number}_{i}"}
                              for i in range(5)]}
        if key:
            item[key] = "EXTENDIDA_FICTICIA_" + str(number)
        data["derivations"]["BIP" + str(number)] = item
    data["report_notices"] = report.build_report_notices(data)
    return data


class TerminalUXTests(unittest.TestCase):
    def setUp(self):
        self.data = fictitious_context()

    def commands(self, text):
        lines = text.splitlines()
        first = lines.index("1. Verificar sin imprimir el contenido privado:")
        second = lines.index("2. Descifrar y mostrar el contenido privado completo:")
        return [lines[first + 1], lines[second + 2]]

    def test_01_compact_hides_secrets_and_patterns(self):
        text = report.format_report(self.data)
        for value in [self.data["mnemonic"], self.data["entropy_bin"], self.data["entropy_hex"],
                      self.data["bip39_seed_hex"], self.data["bip32_root_key"],
                      "WIF_PRIVADO_FICTICIO", "PUBLICA_FICTICIA", "PATRON_FICTICIO",
                      "LIMITACION_FICTICIA", "[OCULTO", "GAP limit"]:
            self.assertNotIn(value, text)
        self.assertIn("BIP39: válido · 12 palabras", text)

    def test_02_compact_keeps_first_address_and_xpubs(self):
        text = report.format_report(self.data)
        for family, item in self.data["derivations"].items():
            self.assertIn(item["addresses"][0]["address"], text)
            for address in item["addresses"][1:]:
                self.assertNotIn(address["address"], text)
            for key in ("xpub", "ypub", "zpub"):
                if key in item:
                    self.assertIn(item[key], text)

    def test_03_show_all_reveals_only_first_address(self):
        text = report.format_report(self.data, show_all=True)
        for key in ("mnemonic", "entropy_hex", "entropy_bin", "bip39_seed_hex", "bip32_root_key"):
            self.assertIn(self.data[key], text)
        for item in self.data["derivations"].values():
            self.assertIn(item["addresses"][0]["private_key_wif"], text)
            self.assertIn(item["addresses"][0]["public_key_hex"], text)
            for address in item["addresses"][1:]:
                self.assertNotIn(address["address"], text)
                self.assertNotIn(address["private_key_wif"], text)
        self.assertNotIn("GAP limit", text)
        self.assertNotIn("ADVERTENCIA, este script:", text)

    def test_04_txt_keeps_full_content_and_notices(self):
        text = report.format_report(self.data, terminal_mode=False, hide_sensitive=False)
        for key in ("mnemonic", "entropy_hex", "bip39_seed_hex", "bip32_root_key"):
            self.assertIn(self.data[key], text)
        for item in self.data["derivations"].values():
            for address in item["addresses"]:
                self.assertIn(address["address"], text)
                self.assertIn(address["private_key_wif"], text)
        self.assertIn("GAP limit", text)
        self.assertIn("no realiza descubrimiento", text)
        self.assertIn("ADVERTENCIA, este script:", text)

    def test_05_formatters_do_not_mutate_context(self):
        before = copy.deepcopy(self.data)
        report.format_report(self.data)
        report.format_report(self.data, show_all=True)
        report.format_report(self.data, terminal_mode=False)
        report.format_export_help(Path("output/reporte.json"), self.data, "json")
        self.assertEqual(self.data, before)

    def test_06_notices_structure_and_input_modes(self):
        for mode in ("words", "entropy_hex", "entropy_bin", "mnemonic", "mnemonic_incomplete"):
            with self.subTest(mode=mode):
                notices = report.build_report_notices({"input_mode": mode})
                self.assertEqual(set(notices), {"version", "general", "input", "privacy"})
                self.assertEqual(notices["version"], 1)
                self.assertTrue(all(isinstance(notices[k], list) for k in ("general", "input", "privacy")))
                self.assertIn("GAP limit", " ".join(notices["general"]))
                if mode != "words":
                    self.assertIn("importado", " ".join(notices["input"]))

    def test_07_json_export_preserves_every_context_field(self):
        before = copy.deepcopy(self.data)
        with patch.object(report, "_encrypt_report_content", return_value="CIFRADO_FICTICIO") as enc:
            with patch.object(report, "_write_report_payload", return_value=Path("final.json")) as write:
                final = report.export_seed_report(self.data, "base.json", "json", "clave-ficticia")
        enc.assert_called_once()
        self.assertEqual(json.loads(enc.call_args.args[0]), before)
        write.assert_called_once_with("base.json", "CIFRADO_FICTICIO", sequential=True)
        self.assertEqual(final, Path("final.json"))
        self.assertEqual(self.data, before)

    def test_08_txt_export_uses_full_report_once(self):
        expected = report.format_report(self.data, terminal_mode=False, hide_sensitive=False) + "\n"
        with patch.object(report, "_encrypt_report_content", return_value="CIFRADO_FICTICIO") as enc:
            with patch.object(report, "_write_report_payload", return_value=Path("final.txt")):
                report.export_seed_report(self.data, "base.txt", "txt", "clave-ficticia")
        enc.assert_called_once_with(expected, "clave-ficticia")

    def test_09_build_context_adds_notices_without_losing_fields(self):
        args = argparse.Namespace(network="testnet", passphrase="", audit_passphrase=False)
        recovered = {"entropy_bin": "0" * 128, "entropy_hex": "00" * 16, "checksum_valid": True}
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(report, "resolve_input", return_value=(bytes(16), self.data["mnemonic"], recovered, "words")))
            seed = stack.enter_context(patch.object(report, "mnemonic_seed", return_value=bytes(64)))
            stack.enter_context(patch.object(report, "bip32_master_key", return_value=("00" * 32, "11" * 32)))
            stack.enter_context(patch.object(report, "select_network", return_value={"coin_type": "1'", **{k: k for k in ("bip44", "bip49", "bip84", "bip86")}}))
            for n in (44, 49, 84, 86):
                stack.enter_context(patch.object(report, f"derive_addresses_bip{n}", return_value=self.data["derivations"]["BIP" + str(n)]))
            stack.enter_context(patch.object(report, "analizar_indicadores_mnemonic", return_value=self.data["indicadores_mnemonic"]))
            result = report.build_context(args)
        self.assertEqual(len(result), 19)
        self.assertEqual(result["bip32_root_key"], "00" * 32 + "11" * 32)
        self.assertEqual(result["derivations"], self.data["derivations"])
        self.assertIn("report_notices", result)
        seed.assert_called_once()

    def test_10_footer_quotes_real_path_and_formats(self):
        path = "output/carpeta con espacios/reporte_'003.json"
        for fmt in ("json", "txt"):
            text = report.format_export_help(path, self.data, fmt, windows=False)
            verify, reveal = map(shlex.split, self.commands(text))
            self.assertEqual(verify[2], path)
            self.assertEqual(verify[verify.index("--format") + 1], fmt)
            self.assertEqual(reveal[-1], path)
            self.assertEqual(verify[verify.index("--words") + 1], "12")
            self.assertNotIn(self.data["mnemonic"], text)
            self.assertNotIn(self.data["bip39_seed_hex"], text)

    def test_11_footer_nonempty_passphrase_does_not_put_secret_in_argv(self):
        self.data["passphrase_used"] = True
        text = report.format_export_help("output/reporte.json", self.data, "json", windows=False)
        verify, reveal = map(shlex.split, self.commands(text))
        self.assertEqual(verify[1], "-c")
        self.assertNotIn("--test-passphrase", text)
        self.assertIn("no contrasta la seed", text)
        compile(verify[2], "auth_command", "exec")
        compile(reveal[2], "reveal_command", "exec")

    def test_12_powershell_quote_builder(self):
        command = report._quote_terminal_command(["python.exe", "-c", "print('dato')", "a'b.json"], windows=True)
        self.assertTrue(command.startswith("& "))
        self.assertIn("'a''b.json'", command)
        self.assertIn("print(''dato'')", command)

    def invoke_main(self, *, export_error=False, verify_ok=True, run_tests=False):
        output = io.StringIO()
        calls = []
        argv = ["bip39_seed_report.py", "--run-tests"] if run_tests else ["bip39_seed_report.py", "-w", "12", "-n", "testnet"]
        def export(*args, **kwargs):
            calls.append("export")
            if export_error:
                raise OSError("fallo-ficticio")
            return Path("output/final_003.json")
        with contextlib.ExitStack() as stack:
            stack.enter_context(patch.object(sys, "argv", argv))
            stack.enter_context(patch.object(report, "CRYPTO_AVAILABLE", True))
            verify = stack.enter_context(patch.object(report, "verify_against_bip39_official", side_effect=lambda **kw: calls.append("verify") or verify_ok))
            secret = stack.enter_context(patch.object(report, "get_secure_input", side_effect=lambda *a, **k: calls.append("password") or "clave-ficticia-larga"))
            stack.enter_context(patch.object(report, "build_context", side_effect=lambda *a, **k: calls.append("context") or copy.deepcopy(self.data)))
            stack.enter_context(patch.object(report, "print_report", side_effect=lambda *a, **k: calls.append("print")))
            exp = stack.enter_context(patch.object(report, "export_seed_report", side_effect=export))
            stack.enter_context(patch.object(report, "attempt_clear_history"))
            tests = stack.enter_context(patch.object(report, "run_bip39_test_vectors"))
            with contextlib.redirect_stdout(output):
                try:
                    report.main()
                    code = 0
                except SystemExit as exc:
                    code = exc.code
        return code, output.getvalue(), calls, verify, secret, exp, tests

    def test_13_main_keeps_processing_order_and_final_path(self):
        code, text, calls, *_ = self.invoke_main()
        self.assertEqual(code, 0)
        self.assertEqual(calls, ["verify", "password", "password", "context", "print", "export"])
        self.assertIn("Archivo: output/final_003.json", text)
        self.assertIn("REVISAR EL REPORTE", text)

    def test_14_export_failure_never_prints_success_footer(self):
        code, text, *_ = self.invoke_main(export_error=True)
        self.assertEqual(code, 1)
        self.assertIn("No se pudo completar la exportación", text)
        self.assertNotIn("✓ Reporte cifrado guardado", text)
        self.assertNotIn("REVISAR EL REPORTE", text)

    def test_15_wordlist_failure_stops_before_password_and_export(self):
        code, text, calls, verify, secret, exp, _ = self.invoke_main(verify_ok=False)
        self.assertEqual(code, 1)
        secret.assert_not_called()
        exp.assert_not_called()
        self.assertNotIn("hash local correcto", text)

    def test_16_run_tests_does_not_enter_interactive_flow(self):
        code, _, calls, verify, secret, exp, tests = self.invoke_main(run_tests=True)
        self.assertEqual(code, 0)
        verify.assert_not_called()
        secret.assert_not_called()
        exp.assert_not_called()
        tests.assert_called_once()

    def test_17_real_encrypted_json_and_txt_roundtrip(self):
        with tempfile.TemporaryDirectory(prefix="bip39-ux-tests-") as directory:
            for fmt in ("json", "txt"):
                with self.subTest(format=fmt):
                    final = report.export_seed_report(self.data, Path(directory) / ("reporte." + fmt), fmt, "clave-ficticia-larga")
                    encrypted = final.read_text(encoding="utf-8")
                    self.assertNotIn(self.data["bip39_seed_hex"], encrypted)
                    plain = report.decrypt_report_content(encrypted, "clave-ficticia-larga")
                    if fmt == "json":
                        self.assertEqual(json.loads(plain), self.data)
                    else:
                        self.assertEqual(plain, report.format_report(self.data, terminal_mode=False, hide_sensitive=False) + "\n")

    def test_18_wordlist_checks_are_not_disabled_by_silent_success(self):
        class MnemonicFake:
            def __init__(self, _):
                self.wordlist = list(report.BIP39_OFFICIAL_WORDLIST)
        with patch.object(report, "Mnemonic", MnemonicFake):
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertTrue(report.verify_against_bip39_official(verbose=False))
            self.assertEqual(output.getvalue(), "")
            with patch.object(report, "BIP39_OFFICIAL_SHA256", "incorrecto"):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    self.assertFalse(report.verify_against_bip39_official(verbose=False))
                self.assertIn("ERROR", output.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
