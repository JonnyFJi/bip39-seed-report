"""Inspector: fixtures ficticias, backend simulado y un round-trip real."""
import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

import inspeccionar_reporte_cifrado as v

PHRASE = " ".join(["abandon"] * 11 + ["about"])


def fixture():
    data = {"network": "testnet", "input_mode": "words", "mnemonic": PHRASE,
            "entropy_hex": "00" * 16, "entropy_bits": 128, "passphrase_used": False,
            "gap_limit": 5,
            "bip39_seed_hex": hashlib.pbkdf2_hmac("sha512", PHRASE.encode(), b"mnemonic", 2048).hex(),
            "derivations": {}}
    for purpose in (44, 49, 84, 86):
        data["derivations"]["BIP" + str(purpose)] = {"addresses": [
            {"index": i, "path": f"m/{purpose}'/1'/0'/0/{i}", "address": f"DATO_FICTICIO_{purpose}_{i}"}
            for i in range(5)]}
    return data


class InspectorTests(unittest.TestCase):
    def setUp(self):
        self.data = fixture()
        self.options = argparse.Namespace(format="auto", words=None, network=None, input_mode=None)
        self.backend = types.SimpleNamespace(
            MAX_ENCRYPTED_REPORT_BYTES=4096, GAP_LIMIT=5,
            DEFAULT_DECISION_TIMEOUT_SECONDS=360,
            InputTimeoutError=TimeoutError,
            timed_input=Mock(side_effect=AssertionError(
                "La lectura temporizada debe simularse en cada prueba.")),
            read_hidden_secret=Mock(return_value="CLAVE_FICTICIA"),
            decrypt_report_content=Mock(return_value=json.dumps(self.data)),
            mnemonic_to_entropy=Mock(return_value={"entropy": bytes(16), "checksum_valid": True}),
            Mnemonic=lambda _: types.SimpleNamespace(to_seed=lambda *a: bytes.fromhex(self.data["bip39_seed_hex"])))
        self.patch_backend = patch.object(v, "report", self.backend)
        self.patch_backend.start(); self.addCleanup(self.patch_backend.stop)
        self.tmp = tempfile.TemporaryDirectory(prefix="bip39-inspector-tests-")
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "archivo 'ficticio'.json"
        self.path.write_text("CIFRADO_FICTICIO", encoding="utf-8")

    def test_01_read_authenticates_without_printing(self):
        capture = io.StringIO()
        with contextlib.redirect_stdout(capture):
            value = v.read_plain(self.path)
        self.assertEqual(json.loads(value), self.data)
        self.assertNotIn(PHRASE, capture.getvalue())
        self.backend.read_hidden_secret.assert_called_once()

    def test_02_size_limit_before_password(self):
        self.path.write_bytes(b"x" * 4097)
        with self.assertRaises(v.InspectionError):
            v.read_plain(self.path)
        self.backend.read_hidden_secret.assert_not_called()

    def test_03_auth_error_has_no_plaintext_or_backend_message(self):
        self.backend.decrypt_report_content.side_effect = ValueError("DATO_PRIVADO_FICTICIO")
        with self.assertRaises(v.InspectionError) as error:
            v.read_plain(self.path)
        self.assertNotIn("DATO_PRIVADO_FICTICIO", str(error.exception))

    def test_04_verify_json_and_expectations(self):
        message = v.verify_plain(json.dumps(self.data), self.options)
        self.assertIn("passphrase vacía", message)
        self.options.network = "mainnet"
        with self.assertRaises(v.InspectionError):
            v.verify_plain(json.dumps(self.data), self.options)

    def test_05_nonempty_passphrase_is_not_requested_or_compared(self):
        self.data["passphrase_used"] = True
        self.backend.Mnemonic = Mock(side_effect=AssertionError("No calcular seed vacía"))
        message = v.verify_plain(json.dumps(self.data), self.options)
        self.assertIn("seed no contrastada", message)
        self.backend.Mnemonic.assert_not_called()

    def test_06_txt_scope_and_format(self):
        plain = "Offline BIP39 Seed Report\nNetwork : testnet\nDATO_FICTICIO\n"
        self.assertIn("TXT", v.verify_plain(plain, self.options))
        self.options.format = "json"
        with self.assertRaises(v.InspectionError):
            v.verify_plain(plain, self.options)

    def test_07_reveal_default_no_never_decrypts(self):
        with patch("builtins.input", return_value=""), contextlib.redirect_stdout(io.StringIO()):
            self.assertFalse(v.reveal_here(self.path, self.options))
        self.backend.read_hidden_secret.assert_not_called()
        self.backend.decrypt_report_content.assert_not_called()

    def test_08_reveal_requires_yes_and_escapes_controls(self):
        self.backend.decrypt_report_content.return_value = "Offline BIP39 Seed Report\n\x1b]52;FICTICIO\x07\n"
        capture = io.StringIO()
        with patch("builtins.input", return_value="y"), contextlib.redirect_stdout(capture):
            self.assertTrue(v.reveal_here(self.path, self.options))
        self.assertNotIn("\x1b", capture.getvalue())
        self.assertNotIn("\x07", capture.getvalue())

    def test_09_window_command_is_argument_list_without_password(self):
        command = v.viewer_command(self.path, self.options, "/usr/bin/gnome-terminal")
        self.assertIn("--window", command)
        self.assertIn("--wait", command)
        self.assertIn("--", command)
        self.assertIn(str(self.path), command)
        self.assertIn("--visor-interno", command)
        self.assertNotIn("CLAVE_FICTICIA", command)
        self.assertNotIn(PHRASE, command)

    def test_10_window_missing_does_not_decrypt(self):
        with patch.object(v.shutil, "which", return_value=None):
            with self.assertRaises(v.InspectionError):
                v.launch_window(self.path, self.options)
        self.backend.read_hidden_secret.assert_not_called()

    def test_11_profile_checked_before_launch(self):
        identifier = "11111111-1111-1111-1111-111111111111"
        def which(name):
            return "/usr/bin/" + name
        with patch.object(v.shutil, "which", side_effect=which):
            with patch.dict(os.environ, {"DISPLAY": ":FICTICIO"}):
                with patch.object(v, "read_setting", side_effect=[[identifier], v.PROFILE, "close"]):
                    with patch.object(v.subprocess, "run", return_value=types.SimpleNamespace(stdout="false\n")):
                        self.assertEqual(v.checked_terminal_profile(), "/usr/bin/gnome-terminal")

    def test_12_hold_profile_is_rejected(self):
        with patch.object(v.shutil, "which", side_effect=lambda n: "/usr/bin/" + n):
            with patch.dict(os.environ, {"DISPLAY": ":FICTICIO"}):
                with patch.object(v, "read_setting", side_effect=[["11111111-1111-1111-1111-111111111111"], v.PROFILE, "hold"]):
                    with self.assertRaises(v.InspectionError):
                        v.checked_terminal_profile()

    def test_13_launch_has_no_shell_and_suppresses_client_output(self):
        with patch.object(v, "checked_terminal_profile", return_value="/usr/bin/gnome-terminal"):
            with patch.object(v.subprocess, "run", return_value=types.SimpleNamespace(returncode=0)) as launch:
                with contextlib.redirect_stdout(io.StringIO()):
                    v.launch_window(self.path, self.options)
        self.assertIs(launch.call_args.kwargs["stdout"], subprocess.DEVNULL)
        self.assertIs(launch.call_args.kwargs["stderr"], subprocess.DEVNULL)
        self.assertNotIn("shell", launch.call_args.kwargs)
        self.backend.read_hidden_secret.assert_not_called()

    def test_14_window_failure_returns_to_menu_without_reveal(self):
        with patch.object(self.backend, "timed_input", side_effect=["2", "q"]):
            with patch.object(v, "launch_window", side_effect=v.InspectionError("Fallo ficticio")):
                with patch.object(v, "reveal_here") as reveal:
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(v.menu(self.path, self.options), 0)
        reveal.assert_not_called()
        self.backend.read_hidden_secret.assert_not_called()

    def test_15_verify_menu_does_not_print_plaintext(self):
        capture = io.StringIO()
        with patch.object(self.backend, "timed_input", side_effect=["1", "q"]), contextlib.redirect_stdout(capture):
            self.assertEqual(v.menu(self.path, self.options), 0)
        self.assertIn("OK: reporte autenticado", capture.getvalue())
        self.assertNotIn(PHRASE, capture.getvalue())
        self.assertNotIn("DATO_FICTICIO_44_0", capture.getvalue())

    def test_16_menu_quit_does_not_read_file(self):
        with patch.object(self.backend, "timed_input", return_value="q"), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(v.menu(self.path, self.options), 0)
        self.backend.read_hidden_secret.assert_not_called()

    def test_17_auth_failure_does_not_auto_reveal(self):
        self.backend.decrypt_report_content.side_effect = ValueError("ERROR FICTICIO")
        capture = io.StringIO()
        with patch.object(self.backend, "timed_input", side_effect=["1", "q"]), patch.object(v, "reveal_here") as reveal:
            with contextlib.redirect_stdout(capture):
                v.menu(self.path, self.options)
        reveal.assert_not_called()
        self.assertNotIn("Traceback", capture.getvalue())
        self.assertNotIn("OK: reporte autenticado", capture.getvalue())

    def test_18_invalid_json_and_structure_rejected(self):
        for value in ("{", "[]", '{"network":"testnet"}'):
            with self.subTest(value=value):
                with self.assertRaises(v.InspectionError):
                    v.verify_plain(value, self.options)

    def test_19_cancellation_is_not_a_reveal(self):
        with patch.object(self.backend, "timed_input", side_effect=EOFError), patch.object(v, "reveal_here") as reveal:
            with contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(EOFError):
                    v.menu(self.path, self.options)
        reveal.assert_not_called()

    def test_20_real_cipher_read_without_plaintext_file(self):
        import bip39_seed_report as real
        plain = json.dumps(self.data)
        encrypted = real._encrypt_report_content(plain, "clave-ficticia-larga")
        self.path.write_text(encrypted, encoding="utf-8")
        capture = io.StringIO()
        with patch.object(v, "report", real), patch.object(real, "read_hidden_secret", return_value="clave-ficticia-larga"):
            with contextlib.redirect_stdout(capture):
                recovered = v.read_plain(self.path)
        self.assertEqual(json.loads(recovered), self.data)
        self.assertEqual(list(Path(self.tmp.name).iterdir()), [self.path])
        self.assertNotIn(PHRASE, capture.getvalue())

    def test_21_window_completed_closes_menu(self):
        with patch.object(self.backend, "timed_input", side_effect=["2"]) as choose:
            with patch.object(v, "launch_window", return_value=True) as launch:
                with patch.object(v, "reveal_here") as reveal:
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(v.menu(self.path, self.options), 0)
        choose.assert_called_once_with("Opción [1/2/3/Q]: ", timeout_seconds=360)
        launch.assert_called_once_with(self.path, self.options)
        reveal.assert_not_called()
        self.backend.read_hidden_secret.assert_not_called()

    def test_22_window_nonzero_returns_to_menu_without_reveal(self):
        with patch.object(self.backend, "timed_input", side_effect=["2", "q"]) as choose:
            with patch.object(v, "launch_window", return_value=False):
                with patch.object(v, "reveal_here") as reveal:
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(v.menu(self.path, self.options), 0)
        self.assertEqual(choose.call_count, 2)
        reveal.assert_not_called()
        self.backend.read_hidden_secret.assert_not_called()

    def test_23_reveal_completed_closes_menu(self):
        with patch.object(self.backend, "timed_input", side_effect=["3"]) as choose:
            with patch.object(v, "reveal_here", return_value=True) as reveal:
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(v.menu(self.path, self.options), 0)
        choose.assert_called_once()
        reveal.assert_called_once_with(self.path, self.options)

    def test_24_reveal_declined_returns_to_menu(self):
        with patch.object(self.backend, "timed_input", side_effect=["3", "q"]) as choose:
            with patch("builtins.input", return_value="n") as confirm:
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(v.menu(self.path, self.options), 0)
        self.assertEqual(choose.call_count, 2)
        confirm.assert_called_once_with("¿Revelar aquí? [y/N]: ")
        self.backend.read_hidden_secret.assert_not_called()
        self.backend.decrypt_report_content.assert_not_called()

    def test_25_menu_timeout_does_not_read_or_reveal(self):
        capture = io.StringIO()
        with patch.object(self.backend, "timed_input", side_effect=TimeoutError) as choose:
            with patch.object(v, "read_plain") as read:
                with patch.object(v, "launch_window") as launch:
                    with patch.object(v, "reveal_here") as reveal:
                        with contextlib.redirect_stdout(capture):
                            self.assertEqual(v.menu(self.path, self.options), 1)
        choose.assert_called_once_with("Opción [1/2/3/Q]: ", timeout_seconds=360)
        read.assert_not_called()
        launch.assert_not_called()
        reveal.assert_not_called()
        self.backend.read_hidden_secret.assert_not_called()
        self.assertIn("Tiempo de selección agotado", capture.getvalue())

    def test_26_verify_then_timeout_does_not_repeat_operation(self):
        with patch.object(self.backend, "timed_input", side_effect=["1", TimeoutError]) as choose:
            with patch.object(v, "read_plain", return_value=json.dumps(self.data)) as read:
                with patch.object(v, "reveal_here") as reveal:
                    with contextlib.redirect_stdout(io.StringIO()):
                        self.assertEqual(v.menu(self.path, self.options), 1)
        self.assertEqual(choose.call_count, 2)
        for call in choose.call_args_list:
            self.assertEqual(call.kwargs, {"timeout_seconds": 360})
        read.assert_called_once_with(self.path)
        reveal.assert_not_called()

    def test_27_invalid_choice_returns_to_timed_menu(self):
        capture = io.StringIO()
        with patch.object(self.backend, "timed_input", side_effect=["9", "q"]) as choose:
            with contextlib.redirect_stdout(capture):
                self.assertEqual(v.menu(self.path, self.options), 0)
        self.assertEqual(choose.call_count, 2)
        self.assertIn("Opción inválida", capture.getvalue())
        self.backend.read_hidden_secret.assert_not_called()

    def test_28_launch_returns_explicit_status(self):
        for code, expected in ((0, True), (1, False), (-15, False)):
            with self.subTest(returncode=code):
                with patch.object(v, "checked_terminal_profile", return_value="/usr/bin/gnome-terminal"):
                    with patch.object(v.subprocess, "run", return_value=types.SimpleNamespace(returncode=code)):
                        with contextlib.redirect_stdout(io.StringIO()):
                            self.assertIs(v.launch_window(self.path, self.options), expected)
        self.backend.read_hidden_secret.assert_not_called()

    def test_29_launch_oserror_is_controlled(self):
        with patch.object(v, "checked_terminal_profile", return_value="/usr/bin/gnome-terminal"):
            with patch.object(v.subprocess, "run", side_effect=OSError("Fallo ficticio")):
                with self.assertRaises(v.InspectionError):
                    v.launch_window(self.path, self.options)
        self.backend.read_hidden_secret.assert_not_called()

    def test_30_keyboard_interrupt_does_not_reveal(self):
        with patch.object(self.backend, "timed_input", side_effect=KeyboardInterrupt):
            with patch.object(v, "reveal_here") as reveal:
                with contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaises(KeyboardInterrupt):
                        v.menu(self.path, self.options)
        reveal.assert_not_called()
        self.backend.read_hidden_secret.assert_not_called()

    def test_31_timed_reader_failure_has_no_unlimited_fallback(self):
        with patch.object(self.backend, "timed_input", side_effect=RuntimeError("Fallo ficticio")):
            with patch("builtins.input") as unlimited:
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(v.menu(self.path, self.options), 1)
        unlimited.assert_not_called()
        self.backend.read_hidden_secret.assert_not_called()

    def test_32_reveal_auth_failure_returns_to_menu(self):
        self.backend.decrypt_report_content.side_effect = ValueError("PRIVADO_FICTICIO")
        capture = io.StringIO()
        with patch.object(self.backend, "timed_input", side_effect=["3", "q"]) as choose:
            with patch("builtins.input", return_value="y"):
                with contextlib.redirect_stdout(capture):
                    self.assertEqual(v.menu(self.path, self.options), 0)
        self.assertEqual(choose.call_count, 2)
        self.backend.read_hidden_secret.assert_called_once()
        self.backend.decrypt_report_content.assert_called_once()
        self.assertNotIn("PRIVADO_FICTICIO", capture.getvalue())
        self.assertNotIn("Traceback", capture.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
