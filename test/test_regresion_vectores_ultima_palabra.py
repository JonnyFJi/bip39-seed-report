import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import bip39_seed_report as report


class RegresionVectoresYUltimaPalabra(unittest.TestCase):
    def setUp(self):
        self.phrase = " ".join(["abandon"] * 11 + ["about"])
        self.seed = hashlib.pbkdf2_hmac(
            "sha512", self.phrase.encode(), b"mnemonicTREZOR", 2048
        ).hex()
        self.vector = ["00" * 16, self.phrase, self.seed]

    def execute(self, payload):
        output = io.StringIO()
        with patch.object(report, "load_vectors", return_value=payload):
            with contextlib.redirect_stdout(output):
                report.run_bip39_test_vectors("fixture.json")
        return output.getvalue()

    def test_01_empty_and_wrong_structures(self):
        for payload in [[], {}, {"english": []}, {"english": {}},
                        {"spanish": [self.vector]}, None, False, 0, "",
                        {"english": None}, [{}], [self.vector[:2]]]:
            with self.subTest(payload_type=type(payload).__name__):
                with self.assertRaises(ValueError):
                    self.execute(payload)

    def test_02_valid_three_and_four_fields(self):
        for payload in [[self.vector], {"english": [self.vector]},
                        [self.vector + ["cuarto-campo-no-verificado"]]]:
            with self.subTest(root_type=type(payload).__name__):
                self.assertIn("OK (1 casos)", self.execute(payload))

    def test_03_invalid_fields(self):
        for vector in [["gg" * 16, self.phrase, self.seed],
                       ["00" * 15, self.phrase, self.seed],
                       ["00 " * 16, self.phrase, self.seed],
                       [self.vector[0], self.phrase, "11" * 63],
                       [self.vector[0], False, self.seed],
                       [*self.vector, False], [*self.vector, " "]]:
            with self.subTest(field_types=[type(x).__name__ for x in vector]):
                with self.assertRaises(ValueError):
                    self.execute([vector])

    def test_04_validate_entire_structure_first(self):
        with patch.object(report, "entropy_to_mnemonic") as conversion:
            with self.assertRaises(ValueError):
                self.execute([self.vector, []])
            conversion.assert_not_called()

    def test_05_mismatches_do_not_print_success(self):
        for name, value in [("entropy_to_mnemonic", "incorrecta"),
                            ("mnemonic_seed", bytes(64)),
                            ("mnemonic_to_entropy", {"entropy": bytes([1]) * 16})]:
            with self.subTest(function=name):
                output = io.StringIO()
                with patch.object(report, "load_vectors", return_value=[self.vector]):
                    with patch.object(report, name, return_value=value):
                        with contextlib.redirect_stdout(output):
                            with self.assertRaises(AssertionError):
                                report.run_bip39_test_vectors("fixture.json")
                self.assertNotIn("Test vectors BIP39: OK", output.getvalue())

    def test_06_file_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "vectors.json"
            with self.assertRaises(ValueError):
                report.run_bip39_test_vectors(path)
            for data in [b"{", b"\xff"]:
                path.write_bytes(data)
                with self.assertRaises(ValueError):
                    report.run_bip39_test_vectors(path)
        with patch.object(report, "load_vectors", side_effect=PermissionError):
            with self.assertRaises(ValueError):
                report.run_bip39_test_vectors("fixture.json")

    def test_07_last_word_real_checks(self):
        for count, expected, bits in [(11, 128, 4), (23, 8, 8)]:
            prefix = " ".join(["abandon"] * count)
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                candidates = report.find_last_word(prefix)
            self.assertEqual(len(candidates), expected)
            self.assertEqual(len(candidates), len(set(candidates)))
            self.assertIn(f"Checksum: {bits} bits", output.getvalue())
            self.assertIn("no es la cantidad", output.getvalue())
            self.assertTrue(all(report.Mnemonic("english").check(
                prefix + " " + candidate) for candidate in candidates))

    def test_08_last_word_invalid_length(self):
        with self.assertRaises(ValueError):
            report.find_last_word("abandon")


    def test_09_detects_success_printed_before_failure(self):
        def faulty_runner(_vectors_path):
            print("Test vectors BIP39: OK (1 casos)")
            raise AssertionError("Discrepancia ficticia para probar la captura.")

        case = type(self)("test_05_mismatches_do_not_print_success")
        result = unittest.TestResult()
        with patch.object(report, "run_bip39_test_vectors", side_effect=faulty_runner):
            case.run(result)

        self.assertEqual(result.testsRun, 1)
        self.assertEqual(len(result.failures), 3)
        self.assertEqual(result.errors, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
