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
            "gap_limit": 10,
            "bip39_seed_hex": hashlib.pbkdf2_hmac("sha512", PHRASE.encode(), b"mnemonic", 2048).hex(),
            "derivations": {}}
    for purpose in (44, 49, 84, 86):
        item = {}
        for chain, key, template_key in (
            (0, "addresses", "path_template"),
            (1, "change_addresses", "change_path_template"),
        ):
            item[template_key] = f"m/{purpose}'/1'/0'/{chain}/i"
            item[key] = [
                {"index": i, "path": f"m/{purpose}'/1'/0'/{chain}/{i}",
                 "address": (f"DATO_FICTICIO_{purpose}_{i}" if chain == 0
                             else f"CAMBIO_FICTICIO_{purpose}_{i}")}
                for i in range(10)]
        data["derivations"]["BIP" + str(purpose)] = item
    import bip39_seed_report as backend
    seed = bytes.fromhex(data["bip39_seed_hex"])
    data["bip32_extended_keys"] = backend.build_bip32_extended_keys(seed, data["network"])
    master, chain = backend.bip32_master_key(seed)
    data["bip32_master_key"] = master
    data["bip32_chain_code"] = chain
    data["bip32_root_key"] = master + chain
    data["derivations"]["BIP32_LEGACY"] = backend.derive_addresses_bip32_legacy(seed, data["network"])
    return data


class InspectorTests(unittest.TestCase):
    def setUp(self):
        self.data = fixture()
        self.options = argparse.Namespace(format="auto", words=None, network=None, input_mode=None)
        self.backend = types.SimpleNamespace(
            MAX_ENCRYPTED_REPORT_BYTES=4096, GAP_LIMIT=10,
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
        choose.assert_called_once_with("Opción [1/2/3/4/5/Q]: ", timeout_seconds=360)
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
        choose.assert_called_once_with("Opción [1/2/3/4/5/Q]: ", timeout_seconds=360)
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


    def test_33_duplicate_root_keys_rejected(self):
        plain = json.dumps(self.data)[:-1] + ', "network": "testnet"}'
        with self.assertRaises(v.InspectionError):
            v.verify_plain(plain, self.options)

    def test_34_duplicate_nested_keys_rejected(self):
        original = json.dumps(self.data)
        plain = original.replace('"index": 0', '"index": 0, "index": 0', 1)
        self.assertNotEqual(plain, original)
        with self.assertRaises(v.InspectionError):
            v.verify_plain(plain, self.options)

    def test_35_nonstandard_json_constants_rejected(self):
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token):
                plain = json.dumps(self.data)[:-1] + ', "extra": ' + token + '}'
                with self.assertRaises(v.InspectionError):
                    v.verify_plain(plain, self.options)

    def test_36_entropy_bits_require_exact_integer(self):
        for value in (128.0, True, "128", None):
            with self.subTest(value=value):
                data = json.loads(json.dumps(self.data))
                data["entropy_bits"] = value
                with self.assertRaises(v.InspectionError):
                    v.verify_plain(json.dumps(data), self.options)

    def test_37_derivations_require_objects(self):
        for replace_root in (True, False):
            with self.subTest(replace_root=replace_root):
                data = json.loads(json.dumps(self.data))
                if replace_root:
                    data["derivations"] = list(data["derivations"])
                else:
                    data["derivations"]["BIP44"] = []
                with self.assertRaises(v.InspectionError):
                    v.verify_plain(json.dumps(data), self.options)

    def test_38_addresses_require_array_of_objects(self):
        for value in ({}, [None] * 10):
            with self.subTest(value=value):
                data = json.loads(json.dumps(self.data))
                data["derivations"]["BIP44"]["addresses"] = value
                with self.assertRaises(v.InspectionError):
                    v.verify_plain(json.dumps(data), self.options)

    def test_39_indexes_reject_booleans_and_floats(self):
        for position, value in ((0, False), (1, True), (0, 0.0), (0, "0")):
            with self.subTest(position=position, value=value):
                data = json.loads(json.dumps(self.data))
                data["derivations"]["BIP44"]["addresses"][position]["index"] = value
                with self.assertRaises(v.InspectionError):
                    v.verify_plain(json.dumps(data), self.options)

    def test_40_addresses_require_nonblank_text(self):
        for value in (123, True, ["ficticia"], {"x": "ficticia"}, "", " \t "):
            with self.subTest(value=value):
                data = json.loads(json.dumps(self.data))
                data["derivations"]["BIP44"]["addresses"][0]["address"] = value
                with self.assertRaises(v.InspectionError):
                    v.verify_plain(json.dumps(data), self.options)

    def test_41_valid_extensions_remain_accepted(self):
        self.data["extra_notice"] = {"text": "DATO_FICTICIO", "version": 1}
        self.assertIn("BIP39", v.verify_plain(json.dumps(self.data), self.options))

    def test_42_reveal_rejects_duplicate_json_without_printing(self):
        marker = "SECRETO_FICTICIO_NO_IMPRIMIR"
        self.backend.decrypt_report_content.return_value = (
            '{"x":"' + marker + '","x":"otro"}'
        )
        capture = io.StringIO()
        with patch("builtins.input", return_value="y"):
            with contextlib.redirect_stdout(capture):
                with self.assertRaises(v.InspectionError):
                    v.reveal_here(self.path, self.options)
        self.assertNotIn(marker, capture.getvalue())

    def test_43_previous_gap_limit_is_a_structure_mismatch(self):
        data = json.loads(json.dumps(self.data))
        data["gap_limit"] = 5
        for item in data["derivations"].values():
            item["addresses"] = item["addresses"][:5]
        with self.assertRaises(v.InspectionError) as error:
            v.verify_plain(json.dumps(data), self.options)
        message = str(error.exception)
        self.assertIn("gap_limit=5", message)
        self.assertIn("esta versión espera 10", message)
        self.assertIn("no indica una contraseña incorrecta", message)
        self.assertNotIn("No se pudo autenticar", message)
        self.assertNotIn(PHRASE, message)

    def test_44_address_count_must_match_gap_limit(self):
        for count in (0, 5, 9, 11):
            with self.subTest(count=count):
                data = json.loads(json.dumps(self.data))
                data["derivations"]["BIP44"]["addresses"] = [
                    {"index": i, "path": f"m/44'/1'/0'/0/{i}",
                     "address": f"DATO_FICTICIO_44_{i}"}
                    for i in range(count)]
                with self.assertRaises(v.InspectionError):
                    v.verify_plain(json.dumps(data), self.options)

    def test_45_menu_separates_old_structure_from_authentication_failure(self):
        data = json.loads(json.dumps(self.data))
        data["gap_limit"] = 5
        self.backend.decrypt_report_content.return_value = json.dumps(data)
        capture = io.StringIO()
        with patch.object(self.backend, "timed_input", side_effect=["1", "q"]):
            with contextlib.redirect_stdout(capture):
                self.assertEqual(v.menu(self.path, self.options), 0)
        text = capture.getvalue()
        self.assertIn("Estructura de reporte no compatible", text)
        self.assertNotIn("No se pudo autenticar", text)
        self.assertNotIn("OK: reporte autenticado", text)
        self.assertNotIn(PHRASE, text)

    def test_46_fixture_uses_the_real_gap_limit(self):
        import bip39_seed_report as real
        self.assertEqual(real.GAP_LIMIT, 10)
        self.assertEqual(self.data["gap_limit"], real.GAP_LIMIT)
        for item in self.data["derivations"].values():
            self.assertEqual(len(item["addresses"]), real.GAP_LIMIT)

    def test_47_missing_change_fields_have_a_structure_message(self):
        for key in ("change_addresses", "change_path_template"):
            with self.subTest(key=key):
                data = fixture()
                del data["derivations"]["BIP44"][key]
                with self.assertRaises(v.InspectionError) as error:
                    v.verify_plain(json.dumps(data), self.options)
                self.assertIn("faltan campos de cambio", str(error.exception))
                self.assertIn("no indica una contraseña incorrecta", str(error.exception))

    def test_48_change_requires_ten_objects(self):
        for value in (None, {}, [], [None] * 10,
                      fixture()["derivations"]["BIP44"]["change_addresses"][:9],
                      fixture()["derivations"]["BIP44"]["change_addresses"] + [{}]):
            with self.subTest(value=value):
                data = fixture()
                data["derivations"]["BIP44"]["change_addresses"] = value
                with self.assertRaises(v.InspectionError):
                    v.verify_plain(json.dumps(data), self.options)

    def test_49_change_paths_cannot_use_receiving_branch(self):
        for position in (0, 9):
            data = fixture()
            data["derivations"]["BIP84"]["change_addresses"][position]["path"] = (
                f"m/84'/1'/0'/0/{position}")
            with self.assertRaises(v.InspectionError):
                v.verify_plain(json.dumps(data), self.options)

    def test_50_change_indexes_and_addresses_are_strict(self):
        for key, value in (("index", False), ("index", 0.0), ("index", "0"),
                           ("index", 1), ("address", " "), ("address", True)):
            with self.subTest(key=key, value=value):
                data = fixture()
                data["derivations"]["BIP86"]["change_addresses"][0][key] = value
                with self.assertRaises(v.InspectionError):
                    v.verify_plain(json.dumps(data), self.options)

    def test_51_both_path_templates_are_checked(self):
        for key in ("path_template", "change_path_template"):
            data = fixture()
            data["derivations"]["BIP49"][key] = "m/49'/0'/0'/0/i"
            with self.assertRaises(v.InspectionError):
                v.verify_plain(json.dumps(data), self.options)

    def test_52_menu_rejects_receiving_only_without_authentication_error(self):
        data = fixture()
        for item in data["derivations"].values():
            del item["change_addresses"]
            del item["change_path_template"]
        self.backend.decrypt_report_content.return_value = json.dumps(data)
        capture = io.StringIO()
        with patch.object(self.backend, "timed_input", side_effect=["1", "q"]):
            with patch.object(v, "reveal_here") as reveal:
                with contextlib.redirect_stdout(capture):
                    self.assertEqual(v.menu(self.path, self.options), 0)
        reveal.assert_not_called()
        self.assertIn("faltan campos de cambio", capture.getvalue())
        self.assertNotIn("No se pudo autenticar", capture.getvalue())
        self.assertNotIn(PHRASE, capture.getvalue())

    def test_53_bip32_direct_encrypted_json_and_txt_roundtrip(self):
        import bip39_seed_report as real

        data = real.build_bip32_direct_context(bytes(range(16)), "testnet")
        password = "clave-ficticia-de-laboratorio"

        for fmt in ("json", "txt"):
            with self.subTest(format=fmt):
                options = argparse.Namespace(
                    format=fmt, words=None, network="testnet",
                    input_mode="bip32_seed_hex",
                )
                path = real.export_seed_report(
                    data, Path(self.tmp.name) / f"directo.{fmt}", fmt, password,
                )
                with (
                    patch.object(v, "report", real),
                    patch.object(real, "read_hidden_secret", return_value=password),
                ):
                    plain = v.read_plain(path)
                    scope = v.verify_plain(plain, options)
                    if fmt == "json":
                        self.assertIn("JSON BIP32 directo", scope)
                        self.assertEqual(json.loads(plain), data)
                    else:
                        self.assertIn("TXT:", scope)
                        self.assertIn("no se comprueban", scope)
                        self.assertIn(
                            f"BIP32 seed hex   : {data['bip32_seed_hex']}", plain,
                        )
                        options.input_mode = "bip32_seed_hex"
                        wrong_mode = plain.replace(
                            "Input mode      : bip32_seed_hex",
                            "Input mode      : words",
                            1,
                        )
                        self.assertNotEqual(wrong_mode, plain)
                        with self.assertRaisesRegex(v.InspectionError, "modo de entrada TXT"):
                            v.verify_plain(wrong_mode, options)

    def test_54_bip32_direct_json_rejects_incoherent_content(self):
        import bip39_seed_report as real

        data = real.build_bip32_direct_context(bytes(range(16)), "testnet")
        options = argparse.Namespace(
            format="json", words=None, network="testnet",
            input_mode="bip32_seed_hex",
        )
        variants = (
            {**data, "mnemonic": PHRASE},
            {**data, "bip32_seed_hex": "ff" * 16},
        )

        with patch.object(v, "report", real):
            for candidate in variants:
                with self.assertRaisesRegex(v.InspectionError, "comprobaciones internas"):
                    v.verify_plain(json.dumps(candidate), options)
            options.words = 12
            with self.assertRaisesRegex(v.InspectionError, "--words no aplica"):
                v.verify_plain(json.dumps(data), options)

    def test_55_graphical_viewer_unavailable_does_not_read(self):
        with patch.dict("sys.modules", {"tkinter": None}):
            with patch.object(v, "read_plain") as read:
                with self.assertRaisesRegex(v.InspectionError, "Tk no está disponible"):
                    v.launch_graphical_viewer(Path("ficticio.json"), argparse.Namespace())
        read.assert_not_called()

    def _mock_graphical_modules(self):
        class FakeTclError(Exception):
            pass

        root = Mock()
        messagebox = types.SimpleNamespace(NO="no", askyesno=Mock())
        tk = types.ModuleType("tkinter")
        tk.Tk = Mock(return_value=root)
        tk.TclError = FakeTclError
        tk.messagebox = messagebox
        tk.ttk = Mock()
        return tk, root, messagebox.askyesno

    def test_56_graphical_viewer_no_display_does_not_read(self):
        tk, _root, ask = self._mock_graphical_modules()
        tk.Tk.side_effect = tk.TclError("pantalla no disponible")
        with patch.dict("sys.modules", {"tkinter": tk}):
            with patch.object(v, "read_plain") as read:
                with self.assertRaisesRegex(v.InspectionError, "visor gráfico"):
                    v.launch_graphical_viewer(Path("ficticio.json"), argparse.Namespace())
        ask.assert_not_called()
        read.assert_not_called()

    def test_57_graphical_viewer_declined_does_not_read(self):
        tk, root, ask = self._mock_graphical_modules()
        ask.return_value = False
        with patch.dict("sys.modules", {"tkinter": tk}):
            with patch.object(v, "read_plain") as read:
                with patch.object(v, "show_graphical_text") as show:
                    self.assertFalse(
                        v.launch_graphical_viewer(
                            Path("ficticio.json"), argparse.Namespace(),
                        )
                    )
        read.assert_not_called()
        show.assert_not_called()
        root.destroy.assert_called_once_with()

    def test_58_graphical_viewer_authentication_failure_does_not_show(self):
        tk, root, ask = self._mock_graphical_modules()
        ask.return_value = True
        path = Path("ficticio.json")
        options = argparse.Namespace(format="auto")
        with patch.dict("sys.modules", {"tkinter": tk}):
            with patch.object(
                v, "read_plain", side_effect=v.InspectionError("No se pudo autenticar"),
            ) as read, patch.object(v, "show_graphical_text") as show:
                with self.assertRaisesRegex(v.InspectionError, "No se pudo autenticar"):
                    v.launch_graphical_viewer(path, options)
        read.assert_called_once_with(path)
        show.assert_not_called()
        root.destroy.assert_called_once_with()

    def test_59_graphical_viewer_passes_text_without_printing_or_writing(self):
        samples = (
            ("json", '{"marker": "SOLO-VENTANA-FICTICIA"}'),
            ("txt", "Offline BIP39 Seed Report\nSOLO-VENTANA-FICTICIA\n"),
        )
        for expected_format, plain in samples:
            with self.subTest(expected_format=expected_format):
                tk, root, ask = self._mock_graphical_modules()
                ask.return_value = True
                options = argparse.Namespace(format=expected_format)
                output = io.StringIO()
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory) / "ficticio.cifrado"
                    original = b"CONTENEDOR-FICTICIO"
                    path.write_bytes(original)
                    with patch.dict("sys.modules", {"tkinter": tk}):
                        with patch.object(v, "read_plain", return_value=plain) as read:
                            with patch.object(v, "show_graphical_text") as show:
                                with contextlib.redirect_stdout(output):
                                    self.assertTrue(v.launch_graphical_viewer(path, options))
                    read.assert_called_once_with(path)
                    show.assert_called_once_with(root, tk, tk.ttk, plain)
                    self.assertEqual(path.read_bytes(), original)
                    self.assertEqual(list(Path(directory).iterdir()), [path])
                self.assertEqual(output.getvalue(), "")
                root.destroy.assert_called_once_with()

    def test_60_menu_option_four_uses_only_graphical_viewer(self):
        path = Path("ficticio.json")
        options = argparse.Namespace(format="auto")
        for opened, choices in ((True, ["4"]), (False, ["4", "q"])):
            with self.subTest(opened=opened):
                backend = types.SimpleNamespace(
                    DEFAULT_DECISION_TIMEOUT_SECONDS=30,
                    timed_input=Mock(side_effect=choices),
                )
                output = io.StringIO()
                with patch.object(v, "report", backend):
                    with patch.object(v, "launch_graphical_viewer", return_value=opened) as viewer:
                        with patch.object(v, "launch_window") as terminal_window:
                            with patch.object(v, "reveal_here") as reveal:
                                with contextlib.redirect_stdout(output):
                                    self.assertEqual(v.menu(path, options), 0)
                viewer.assert_called_once_with(path, options)
                terminal_window.assert_not_called()
                reveal.assert_not_called()
                self.assertEqual(backend.timed_input.call_count, len(choices))
                self.assertIn("[4] Visor gráfico de solo lectura", output.getvalue())


    def test_61_external_editor_missing_does_not_prompt_or_read(self):
        with patch.object(v.shutil, "which", return_value=None):
            with patch.object(v, "report") as backend:
                with patch.object(v, "read_plain") as read:
                    with self.assertRaisesRegex(v.InspectionError, "xdg-open"):
                        v.launch_external_editor(Path("ficticio.json"), self.options)
        backend.timed_input.assert_not_called()
        read.assert_not_called()

    def test_62_external_editor_declined_or_timed_out_creates_no_copy(self):
        class FakeTimeout(Exception):
            pass

        for timed_out in (False, True):
            with self.subTest(timed_out=timed_out):
                confirm = Mock(return_value="")
                if timed_out:
                    confirm.side_effect = FakeTimeout
                backend = types.SimpleNamespace(
                    DEFAULT_DECISION_TIMEOUT_SECONDS=360,
                    InputTimeoutError=FakeTimeout,
                    timed_input=confirm,
                )
                output = io.StringIO()
                with patch.object(v.shutil, "which", return_value="/usr/bin/xdg-open"):
                    with patch.object(v, "report", backend):
                        with patch.object(v, "read_plain") as read:
                            with patch.object(v.tempfile, "TemporaryDirectory") as temp:
                                with contextlib.redirect_stdout(output):
                                    self.assertFalse(
                                        v.launch_external_editor(
                                            Path("ficticio.json"), self.options,
                                        )
                                    )
                read.assert_not_called()
                temp.assert_not_called()
                self.assertIn("ADVERTENCIA", output.getvalue())

    def test_63_external_editor_bad_auth_or_format_creates_no_copy(self):
        cases = (
            (v.InspectionError("No se pudo autenticar"), None, "autenticar"),
            (None, '{"marker": "FICTICIO"}', "formato interno"),
        )
        for error, plain, expected in cases:
            with self.subTest(expected=expected):
                backend = types.SimpleNamespace(
                    DEFAULT_DECISION_TIMEOUT_SECONDS=360,
                    timed_input=Mock(return_value="s"),
                )
                options = argparse.Namespace(format="txt")
                with patch.object(v.shutil, "which", return_value="/usr/bin/xdg-open"):
                    with patch.object(v, "report", backend):
                        with patch.object(v, "read_plain", return_value=plain, side_effect=error):
                            with patch.object(v.tempfile, "TemporaryDirectory") as temp:
                                with patch.object(v.subprocess, "run") as run:
                                    with contextlib.redirect_stdout(io.StringIO()):
                                        with self.assertRaisesRegex(v.InspectionError, expected):
                                            v.launch_external_editor(Path("ficticio.json"), options)
                temp.assert_not_called()
                run.assert_not_called()

    def test_64_external_editor_permissions_and_cleanup(self):
        plain = '{"marker": "SOLO-EDITOR-FICTICIO"}'
        for status in (0, 1):
            with self.subTest(status=status):
                opened = []
                original = b"CONTENEDOR-FICTICIO"
                backend = types.SimpleNamespace(
                    DEFAULT_DECISION_TIMEOUT_SECONDS=360,
                    timed_input=Mock(return_value="s"),
                )

                def fake_open(argv, **kwargs):
                    self.assertEqual(len(argv), 2)
                    self.assertEqual(argv[0], "/usr/bin/xdg-open")
                    self.assertEqual(kwargs["stdin"], subprocess.DEVNULL)
                    copy = Path(argv[1])
                    opened.append(copy)
                    self.assertEqual(copy.name, "reporte.txt")
                    self.assertEqual(copy.stat().st_mode & 0o777, 0o600)
                    self.assertEqual(copy.parent.stat().st_mode & 0o077, 0)
                    self.assertEqual(copy.read_bytes(), plain.encode("utf-8"))
                    return types.SimpleNamespace(returncode=status)

                def finish(_prompt):
                    self.assertTrue(opened[0].is_file())
                    return ""

                output = io.StringIO()
                with tempfile.TemporaryDirectory() as folder:
                    path = Path(folder) / "original.json"
                    path.write_bytes(original)
                    options = argparse.Namespace(format="json")
                    with (
                        patch.object(v.shutil, "which", return_value="/usr/bin/xdg-open"),
                        patch.object(v, "report", backend),
                        patch.object(v, "read_plain", return_value=plain) as read,
                        patch.object(v.subprocess, "run", side_effect=fake_open),
                        patch("builtins.input", side_effect=finish) as done,
                        contextlib.redirect_stdout(output),
                    ):
                        if status == 0:
                            self.assertTrue(v.launch_external_editor(path, options))
                        else:
                            with self.assertRaisesRegex(v.InspectionError, "no confirmó"):
                                v.launch_external_editor(path, options)
                    read.assert_called_once_with(path)
                    self.assertEqual(done.call_count, int(status == 0))
                    self.assertEqual(path.read_bytes(), original)

                self.assertEqual(len(opened), 1)
                self.assertFalse(opened[0].parent.exists())
                self.assertNotIn(plain, output.getvalue())

    def test_65_menu_option_five_uses_only_external_editor(self):
        path = Path("ficticio.json")
        backend = types.SimpleNamespace(
            DEFAULT_DECISION_TIMEOUT_SECONDS=360,
            timed_input=Mock(return_value="5"),
        )
        output = io.StringIO()
        with (
            patch.object(v, "report", backend),
            patch.object(v, "launch_external_editor", return_value=True) as editor,
            patch.object(v, "launch_graphical_viewer") as graphical,
            patch.object(v, "launch_window") as terminal_window,
            patch.object(v, "reveal_here") as reveal,
            contextlib.redirect_stdout(output),
        ):
            self.assertEqual(v.menu(path, self.options), 0)

        editor.assert_called_once_with(path, self.options)
        graphical.assert_not_called()
        terminal_window.assert_not_called()
        reveal.assert_not_called()
        self.assertIn(
            "[5] Abrir en editor externo — ADVERTENCIA: crea una copia temporal sin cifrar",
            output.getvalue(),
        )


    def test_66_external_editor_failure_paths_and_cleanup(self):
        real_temporary_directory = tempfile.TemporaryDirectory
        real_fdopen = os.fdopen
        plain = '{"marker": "SECRETO-FICTICIO-SOLO-PRUEBA"}'
        options = argparse.Namespace(format="json")

        class FailingWriter:
            def __init__(self, handle):
                self.handle = handle

            def __enter__(self):
                return self

            def write(self, _text):
                self.handle.write("FRAGMENTO-FICTICIO")
                self.handle.flush()
                raise OSError("fallo ficticio de escritura")

            def __exit__(self, exc_type, exc, traceback):
                self.handle.close()
                return False

        cases = (
            ("launch", v.InspectionError),
            ("interrupt", KeyboardInterrupt),
            ("eof", EOFError),
            ("write", OSError),
            ("cleanup", v.InspectionError),
        )

        for scenario, expected_error in cases:
            with self.subTest(scenario=scenario):
                backend = types.SimpleNamespace(
                    DEFAULT_DECISION_TIMEOUT_SECONDS=360,
                    timed_input=Mock(return_value="s"),
                )
                allocated = []
                output = io.StringIO()

                with real_temporary_directory(prefix="bip39-editor-test-") as folder:
                    original = Path(folder) / "original.cifrado"
                    original_bytes = b"CONTENEDOR-FICTICIO-SIN-CAMBIOS"
                    original.write_bytes(original_bytes)

                    def allocate(**kwargs):
                        directory = real_temporary_directory(dir=folder, **kwargs)
                        allocated.append(directory)
                        if scenario == "cleanup":
                            return types.SimpleNamespace(
                                name=directory.name,
                                cleanup=Mock(
                                    side_effect=OSError("fallo ficticio de limpieza"),
                                ),
                            )
                        return directory

                    def open_writer(fd, *args, **kwargs):
                        handle = real_fdopen(fd, *args, **kwargs)
                        if scenario == "write":
                            return FailingWriter(handle)
                        return handle

                    def launch(_argv, **_kwargs):
                        if scenario == "launch":
                            raise OSError("fallo ficticio del abridor")
                        return types.SimpleNamespace(returncode=0)

                    def finish(_prompt):
                        copy = Path(allocated[0].name) / "reporte.txt"
                        self.assertTrue(copy.is_file())
                        if scenario == "interrupt":
                            raise KeyboardInterrupt
                        if scenario == "eof":
                            raise EOFError
                        return ""

                    try:
                        with (
                            patch.object(v.shutil, "which", return_value="/usr/bin/xdg-open"),
                            patch.object(v, "report", backend),
                            patch.object(v, "read_plain", return_value=plain),
                            patch.object(v.tempfile, "TemporaryDirectory", side_effect=allocate),
                            patch.object(v.os, "fdopen", side_effect=open_writer),
                            patch.object(v.subprocess, "run", side_effect=launch) as run,
                            patch("builtins.input", side_effect=finish) as done,
                            contextlib.redirect_stdout(output),
                        ):
                            with self.assertRaises(expected_error) as caught:
                                v.launch_external_editor(original, options)

                        self.assertEqual(original.read_bytes(), original_bytes)
                        self.assertEqual(len(allocated), 1)
                        directory = Path(allocated[0].name)

                        if scenario == "cleanup":
                            self.assertTrue((directory / "reporte.txt").is_file())
                            self.assertIn(
                                "No se pudo retirar la copia temporal",
                                str(caught.exception),
                            )
                            self.assertIn(
                                str(directory / "reporte.txt"),
                                str(caught.exception),
                            )
                        else:
                            self.assertFalse(directory.exists())

                        self.assertEqual(run.call_count, int(scenario != "write"))
                        self.assertEqual(
                            done.call_count,
                            int(scenario in {"interrupt", "eof", "cleanup"}),
                        )
                        self.assertNotIn(plain, output.getvalue())
                        self.assertNotIn(plain, str(caught.exception))
                        self.assertNotIn("Copia temporal retirada.", output.getvalue())
                    finally:
                        for directory in allocated:
                            directory.cleanup()


if __name__ == "__main__":
    unittest.main(verbosity=2)
