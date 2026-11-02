"""Regresión complementaria con material público/ficticio y UI simulada.
No sustituye ensayos de TTY, Windows ni vectores independientes completos.
"""
import argparse
import contextlib
import hashlib
import hmac
import io
import json
import selectors
import sys
import tempfile
import types
import unicodedata
from pathlib import Path
import unittest
from unittest.mock import Mock, patch

import bip39_seed_report as r

PUBLIC_MNEMONIC = " ".join(["abandon"] * 11 + ["about"])


def arguments(**changes):
    values = dict(words=None, entropy_bin="", entropy_hex="", mnemonic="",
                  mnemonic_incomplete="", network="testnet", passphrase="", audit_passphrase=False)
    values.update(changes)
    return argparse.Namespace(**values)


class RegressionIntegral(unittest.TestCase):
    def setUp(self):
        self.output = io.StringIO()
        self.capture = contextlib.redirect_stdout(self.output)
        self.capture.__enter__()
        self.addCleanup(self.capture.__exit__, None, None, None)

    def test_01_entropy_formats_and_lengths(self):
        for size in (16, 20, 24, 28, 32):
            value = bytes(range(size))
            r.validate_entropy_length(size * 8)
            self.assertEqual(r.binary_to_bytes(r.bytes_to_binary(value)), value)
            self.assertEqual(r.hex_to_bytes("0x" + value.hex().upper()), value)
            self.assertEqual(len(r.entropy_checksum_bits(value)), size // 4)
        for bad in (0, 8, 127, 129, 264):
            with self.assertRaises(ValueError):
                r.validate_entropy_length(bad)
        for bad in ("", "2" * 128, "0" * 127):
            with self.assertRaises(ValueError):
                r.binary_to_bytes(bad)
        for bad in ("", "0x", "xyz", "00"):
            with self.assertRaises(ValueError):
                r.hex_to_bytes(bad)

    def test_02_five_bip39_lengths_and_seed(self):
        for count, size in [(12, 16), (15, 20), (18, 24), (21, 28), (24, 32)]:
            entropy = bytes(size)
            phrase = r.entropy_to_mnemonic(entropy)
            self.assertEqual(len(phrase.split()), count)
            self.assertEqual(r.validate_mnemonic_text(phrase), phrase)
            recovered = r.mnemonic_to_entropy(phrase)
            self.assertEqual(recovered["entropy"], entropy)
            self.assertTrue(recovered["checksum_valid"])
            expected = hashlib.pbkdf2_hmac("sha512", phrase.encode(), b"mnemonicTREZOR", 2048)
            self.assertEqual(r.mnemonic_seed(phrase, "TREZOR"), expected)
        with self.assertRaises(ValueError):
            r.validate_mnemonic_text("palabra-ficticia")

    def test_03_generation_source_and_invalid_count(self):
        for count, size in [(12, 16), (15, 20), (18, 24), (21, 28), (24, 32)]:
            with patch.object(r.os, "urandom", return_value=bytes(size)) as source:
                self.assertEqual(r.generate_entropy(count), bytes(size))
                source.assert_called_once_with(size)
        with self.assertRaises(ValueError):
            r.generate_entropy(13)

    def test_04_nfkd_and_master_primitive(self):
        self.assertEqual(r.normalize_text("é"), "e\u0301")
        self.assertEqual(r.mnemonic_seed(PUBLIC_MNEMONIC, "é"), r.mnemonic_seed(PUBLIC_MNEMONIC, "e\u0301"))
        seed = bytes(range(16))
        digest = hmac.new(b"Bitcoin seed", seed, hashlib.sha512).digest()
        master, chain = r.bip32_master_key(seed)
        self.assertEqual(master + chain, digest.hex())

    def test_05_wordlist_effective_mismatch(self):
        class ChangedList:
            def __init__(self, _):
                self.wordlist = list(r.BIP39_OFFICIAL_WORDLIST)
                self.wordlist[0], self.wordlist[1] = self.wordlist[1], self.wordlist[0]
        with patch.object(r, "Mnemonic", ChangedList):
            self.assertFalse(r.verify_against_bip39_official(verbose=False))
        self.assertTrue(r.verify_against_bip39_official())

    def test_06_derivation_structure_both_networks(self):
        seed = r.mnemonic_seed(PUBLIC_MNEMONIC, "TREZOR")
        for network, coin_type in [("mainnet", "0'"), ("testnet", "1'")]:
            config = r.select_network(network)
            for purpose in (44, 49, 84, 86):
                item = getattr(r, f"derive_addresses_bip{purpose}")(
                    seed, config[f"bip{purpose}"], coin_type, 5)
                self.assertEqual(len(item["addresses"]), 5)
                self.assertEqual(item["path_template"], f"m/{purpose}'/{coin_type}/0'/0/i")
                for index, address in enumerate(item["addresses"]):
                    self.assertEqual(address["index"], index)
                    self.assertEqual(address["path"], f"m/{purpose}'/{coin_type}/0'/0/{index}")
                    self.assertTrue(address["address"])
                    self.assertTrue(address["private_key_wif"])
                    self.assertEqual(len(bytes.fromhex(address["public_key_hex"])), 33)
        with self.assertRaises(ValueError):
            r.select_network("red-ficticia")

    def test_07_resolve_generation_and_imports(self):
        variants = [(arguments(words=12), "words"),
                    (arguments(entropy_bin="0" * 128), "entropy_bin"),
                    (arguments(entropy_hex="00" * 16), "entropy_hex"),
                    (arguments(mnemonic=PUBLIC_MNEMONIC), "mnemonic")]
        for args, mode in variants:
            with self.subTest(mode=mode):
                entropy, phrase, recovered, actual = r.resolve_input(args)
                self.assertEqual(actual, mode)
                self.assertEqual(len(phrase.split()), 12)
                self.assertEqual(recovered["entropy"], entropy)
                self.assertTrue(recovered["checksum_valid"])
        with self.assertRaises(ValueError):
            r.resolve_input(arguments(words=12, entropy_hex="00" * 16))

    def test_08_recovery_selection_eof_and_cancel(self):
        for count in (11, 23):
            args = arguments(mnemonic_incomplete=" ".join(["abandon"] * count))
            with patch("builtins.input", return_value="1"):
                _, phrase, recovered, mode = r.resolve_input(args)
            self.assertEqual(mode, "mnemonic_incomplete")
            self.assertEqual(len(phrase.split()), count + 1)
            self.assertTrue(recovered["checksum_valid"])
        args = arguments(mnemonic_incomplete=" ".join(["abandon"] * 11))
        with patch("builtins.input", side_effect=EOFError):
            with self.assertRaises(RuntimeError):
                r.resolve_input(args)
        with patch("builtins.input", return_value="q"):
            with self.assertRaises(SystemExit) as stopped:
                r.resolve_input(args)
        self.assertEqual(stopped.exception.code, 0)

    def test_09_interactive_menu_and_network(self):
        args = arguments(network=None)
        with patch("builtins.input", side_effect=["1", "2", "2"]):
            with patch.object(r, "get_secure_passphrase", return_value="TREZOR"):
                _, phrase, _, mode = r.resolve_input(args, interactive=True)
        self.assertEqual(len(phrase.split()), 24)
        self.assertEqual(args.network, "testnet")
        self.assertEqual(args.passphrase, "TREZOR")
        self.assertEqual(mode, "words")

    def test_10_real_context_and_audit(self):
        data = r.build_context(arguments(mnemonic=PUBLIC_MNEMONIC, passphrase="TREZOR", audit_passphrase=True))
        self.assertEqual(data["mnemonic"], PUBLIC_MNEMONIC)
        self.assertEqual(data["entropy_hex"], "00" * 16)
        self.assertTrue(data["passphrase_used"])
        self.assertIn("report_notices", data)
        self.assertIn("passphrase_audit", data)
        self.assertEqual(set(data["derivations"]), {"BIP44", "BIP49", "BIP84", "BIP86"})

    def test_11_pattern_and_passphrase_indicators(self):
        ind = r.analizar_indicadores_mnemonic(PUBLIC_MNEMONIC)
        self.assertTrue(ind["valid"])
        self.assertEqual(ind["word_count"], 12)
        self.assertEqual(ind["unique_words"], 2)
        self.assertFalse(r.analizar_indicadores_mnemonic("ficticia")["valid"])
        self.assertFalse(r.audit_passphrase("")["present"])
        self.assertTrue(r.audit_passphrase("Aa1 !")["has_symbols"])

    def test_12_tty_policy(self):
        for stdin_ok, stdout_ok in [(False, True), (True, False), (False, False)]:
            with patch.object(r.sys, "stdin", Mock(isatty=Mock(return_value=stdin_ok))):
                with patch.object(r.sys, "stdout", Mock(isatty=Mock(return_value=stdout_ok))):
                    with self.assertRaises(RuntimeError):
                        r._require_tty()
        with patch.object(r.sys, "stdin", Mock(isatty=Mock(return_value=True))):
            with patch.object(r.sys, "stdout", Mock(isatty=Mock(return_value=True))):
                r._require_tty()

    def test_13_hidden_read_success_and_failure(self):
        with patch.object(r, "_require_tty"):
            with patch.object(r.getpass, "getpass", return_value="FICTICIO"):
                self.assertEqual(r.read_hidden_secret("Dato: "), "FICTICIO")
            with patch.object(r.getpass, "getpass", side_effect=r.getpass.GetPassWarning("simulada")):
                with self.assertRaises(RuntimeError):
                    r.read_hidden_secret("Dato: ")

    def test_14_unix_timed_reader_simulated(self):
        selector = Mock()
        selector.select.return_value = [(None, None)]
        with patch.object(selectors, "DefaultSelector", return_value=selector):
            with patch.object(r.sys, "stdin", io.StringIO("opcion\n")):
                self.assertEqual(r._read_line_with_timeout_unix("", 1), "opcion")
            selector.select.return_value = []
            with self.assertRaises(r.InputTimeoutError):
                r._read_line_with_timeout_unix("", 1)
            selector.select.return_value = [(None, None)]
            with patch.object(r.sys, "stdin", io.StringIO("")):
                with self.assertRaises(EOFError):
                    r._read_line_with_timeout_unix("", 1)
        self.assertTrue(selector.close.called)

    def test_15_windows_reader_simulated_not_windows_certification(self):
        fake = types.ModuleType("msvcrt")
        fake.kbhit = Mock(return_value=True)
        fake.getwch = Mock(side_effect=["a", "\b", "b", "\r"])
        with patch.dict(sys.modules, {"msvcrt": fake}):
            with patch.object(r.time, "monotonic", return_value=0):
                self.assertEqual(r._read_line_with_timeout_windows("", 5), "b")
            with patch.object(r.time, "monotonic", side_effect=[0, 10]):
                with self.assertRaises(r.InputTimeoutError):
                    r._read_line_with_timeout_windows("", 5)
            for signal, error in [("\x03", KeyboardInterrupt), ("\x1a", EOFError)]:
                fake.getwch = Mock(return_value=signal)
                with patch.object(r.time, "monotonic", return_value=0):
                    with self.assertRaises(error):
                        r._read_line_with_timeout_windows("", 5)

    def test_16_timed_dispatch_and_menu(self):
        with patch.object(r, "_require_tty"):
            with self.assertRaises(ValueError):
                r.timed_input("", 0)
            with patch.object(r, "_read_line_with_timeout_unix", return_value="c"):
                with patch.object(r.os, "name", "posix"):
                    self.assertEqual(r.timed_input("", 1), "c")
        self.assertEqual(r._normalize_choice(" Y "), "y")
        with patch.object(r, "timed_input", side_effect=["incorrecta", " Y "]):
            self.assertEqual(r.timed_menu_choice("", {"y", "n"}), "y")
        with self.assertRaises(ValueError):
            r.timed_menu_choice("", set())

    def test_17_display_cleanup_is_not_secure_erasure(self):
        class Terminal(io.StringIO):
            def isatty(self):
                return True
        terminal = Terminal()
        with patch.object(r.sys, "stdout", terminal):
            self.assertTrue(r.clear_sensitive_display(2))
            self.assertFalse(r.clear_sensitive_display(0))
        self.assertIn("\x1b", terminal.getvalue())
        broken = Mock(isatty=Mock(return_value=True), write=Mock(side_effect=OSError))
        with patch.object(r.sys, "stdout", broken):
            self.assertFalse(r.clear_sensitive_display())
        with patch("builtins.input", return_value=""):
            with patch.object(r, "clear_sensitive_display", return_value=False):
                r.show_sensitive_value_temporarily("DATO FICTICIO", "Laboratorio")

    def test_18_reviewable_hidden_input(self):
        def validate(value):
            if value != "bien":
                raise ValueError("dato ficticio inválido")
            return value.upper()
        with patch.object(r, "read_hidden_secret", side_effect=["mal", "bien"]):
            with patch.object(r, "timed_menu_choice", return_value="c"):
                self.assertEqual(r.get_reviewable_secure_input("", validate, "laboratorio"), "BIEN")
        for choices in (["r", "c"], ["v", "c"]):
            with patch.object(r, "read_hidden_secret", return_value="bien"):
                with patch.object(r, "timed_menu_choice", side_effect=choices):
                    with patch.object(r, "show_sensitive_value_temporarily"):
                        self.assertEqual(r.get_reviewable_secure_input("", validate, "laboratorio"), "BIEN")
        with patch.object(r, "read_hidden_secret", return_value="bien"):
            with patch.object(r, "timed_menu_choice", return_value="q"):
                with self.assertRaises(r.InputCancelledError):
                    r.get_reviewable_secure_input("", validate, "laboratorio")

    def test_19_confirmed_and_visible_input(self):
        with patch.object(r, "read_hidden_secret", side_effect=["a", "b", "é", "e\u0301"]):
            self.assertEqual(r.get_confirmed_secret("", "", r.normalize_text), "e\u0301")
        with patch.object(r, "timed_menu_choice", side_effect=["c", "r", "c"]):
            with patch("builtins.input", side_effect=["primero", "segundo"]):
                self.assertEqual(r.get_visible_input_with_acknowledgement("", str.upper, "laboratorio"), "SEGUNDO")
        with patch.object(r, "timed_menu_choice", return_value="q"):
            with self.assertRaises(r.InputCancelledError):
                r.get_visible_input_with_acknowledgement("", str, "laboratorio")

    def test_20_secret_wrappers(self):
        with patch.object(r, "read_hidden_secret", side_effect=["", "dato"]):
            self.assertEqual(r.get_secure_input(""), "dato")
        for function in (r.get_secure_mnemonic, r.get_secure_entropy_hex, r.get_secure_entropy_bin):
            with patch.object(r, "read_hidden_secret", return_value=" dato ficticio "):
                self.assertEqual(function(), "dato ficticio")
        with patch.object(r, "read_hidden_secret", side_effect=["", ""]):
            self.assertEqual(r.get_secure_passphrase(), "")

    def test_21_history_cleanup_simulated(self):
        fake = types.ModuleType("readline")
        fake.clear_history = Mock()
        with patch.dict(sys.modules, {"readline": fake}):
            r.attempt_clear_history()
        fake.clear_history.assert_called_once()

    def test_22_vector_file_positive_and_negative(self):
        seed = hashlib.pbkdf2_hmac("sha512", PUBLIC_MNEMONIC.encode(), b"mnemonicTREZOR", 2048).hex()
        with tempfile.TemporaryDirectory(prefix="bip39-integral-") as directory:
            path = Path(directory) / "vectors.json"
            path.write_text(json.dumps({"english": [["00" * 16, PUBLIC_MNEMONIC, seed]]}), encoding="utf-8")
            self.assertIn("english", r.load_vectors(path))
            r.run_bip39_test_vectors(path)
            for bad in ([], {"english": []}, {"otro": []}):
                path.write_text(json.dumps(bad), encoding="utf-8")
                with self.assertRaises(ValueError):
                    r.run_bip39_test_vectors(path)

    def test_23_cli_sensitive_options_rejected_even_empty(self):
        for option in ("--entropy-bin", "--entropy-hex", "--mnemonic", "--mnemonic-incomplete", "--passphrase"):
            for prefix in ([], ["-i"], ["--run-tests", "--allow-insecure-cli-secrets"]):
                with self.subTest(option=option, prefix=prefix):
                    with patch.object(sys, "argv", ["bip39_seed_report.py", *prefix, option, ""]):
                        with contextlib.redirect_stderr(io.StringIO()):
                            with self.assertRaises(SystemExit) as stopped:
                                r.main()
                    self.assertEqual(stopped.exception.code, 2)

    def test_24_cli_help_and_no_tty(self):
        with patch.object(sys, "argv", ["bip39_seed_report.py", "--help"]):
            with self.assertRaises(SystemExit) as stopped:
                r.main()
        self.assertEqual(stopped.exception.code, 0)
        with patch.object(sys, "argv", ["bip39_seed_report.py", "-w", "12"]):
            with patch.object(r.sys, "stdin", Mock(isatty=Mock(return_value=False))):
                with self.assertRaises(SystemExit) as stopped:
                    r.main()
        self.assertEqual(stopped.exception.code, 1)

    def test_25_password_abort_paths(self):
        for error in (KeyboardInterrupt, EOFError):
            with patch.object(sys, "argv", ["bip39_seed_report.py", "-w", "12"]):
                with patch.object(r, "verify_against_bip39_official", return_value=True):
                    with patch.object(r, "get_secure_input", side_effect=error):
                        with self.assertRaises(SystemExit) as stopped:
                            r.main()
            self.assertEqual(stopped.exception.code, 1)
        with patch.object(sys, "argv", ["bip39_seed_report.py", "-w", "12"]):
            with patch.object(r, "verify_against_bip39_official", return_value=True):
                with patch.object(r, "get_secure_input", side_effect=["a", "b"]):
                    with self.assertRaises(SystemExit) as stopped:
                        r.main()
        self.assertEqual(stopped.exception.code, 1)
        with patch.object(sys, "argv", ["bip39_seed_report.py", "-w", "12"]):
            with patch.object(r, "verify_against_bip39_official", return_value=True):
                with patch.object(r, "get_secure_input", return_value="x"):
                    with patch.object(r, "timed_menu_choice", return_value="n"):
                        with self.assertRaises(SystemExit) as stopped:
                            r.main()
        self.assertEqual(stopped.exception.code, 1)


    def test_26_print_report_wrapper(self):
        data = r.build_context(arguments(mnemonic=PUBLIC_MNEMONIC))
        before = json.dumps(data, sort_keys=True)
        r.print_report(data)
        self.assertIn("RESUMEN", self.output.getvalue())
        self.assertNotIn(PUBLIC_MNEMONIC, self.output.getvalue())
        self.assertEqual(json.dumps(data, sort_keys=True), before)

    def test_27_default_vectors_outside_project_directory(self):
        import os
        previous = Path.cwd()
        try:
            with tempfile.TemporaryDirectory(prefix="bip39-cwd-") as directory:
                os.chdir(directory)
                self.assertTrue(Path(r.DEFAULT_VECTORS_FILE).is_file())
                r.run_bip39_test_vectors(r.DEFAULT_VECTORS_FILE)
        finally:
            os.chdir(previous)
        self.assertEqual(Path.cwd(), previous)

    def test_28_empty_suite_cli_status_and_message(self):
        with tempfile.TemporaryDirectory(prefix="bip39-empty-suite-") as directory:
            path = Path(directory) / "empty.json"
            path.write_text("[]", encoding="utf-8")
            error = io.StringIO()
            with patch.object(sys, "argv", ["bip39_seed_report.py", "--run-tests", "--vectors-file", str(path)]):
                with contextlib.redirect_stderr(error):
                    with self.assertRaises(SystemExit) as stopped:
                        r.main()
        self.assertEqual(stopped.exception.code, 1)
        self.assertIn("Error en los vectores BIP39", error.getvalue())
        self.assertNotIn("OK (0 casos)", self.output.getvalue())



if __name__ == "__main__":
    unittest.main(verbosity=2)
