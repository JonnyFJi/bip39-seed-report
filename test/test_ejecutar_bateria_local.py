"""Regresión del protocolo de la batería con registros y programas ficticios."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "battery_under_test", Path(__file__).with_name("ejecutar_bateria_local.py")
)
battery = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(battery)


def record(*, methods=1, failures=0, errors=0, skipped=None,
           expected_failures=0, unexpected_successes=0, code=0):
    return {"exit_code": code, "calls_by_line": {"1": 1}, "unittest": [{
        "methods": methods, "failures": failures, "errors": errors,
        "skipped": [] if skipped is None else skipped,
        "expected_failures": expected_failures,
        "unexpected_successes": unexpected_successes,
    }]}


class BatteryRecordTests(unittest.TestCase):
    def totals(self, value, code=0, requires=True):
        return battery.validate_worker_record(value, code, requires_unittest=requires)

    def run_worker(self, program):
        with tempfile.TemporaryDirectory(prefix="battery-regression-") as directory:
            target = Path(directory) / "fictitious.py"
            path = Path(directory) / "record.json"
            target.write_text(program, encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-B", str(Path(battery.__file__).resolve()),
                 "--worker", str(target), str(path)],
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, text=True, timeout=20,
            )
            data, totals = battery.load_worker_record(
                path, result.returncode, requires_unittest=False,
            )
        return result.returncode, data, totals

    def test_01_valid_record(self):
        totals = self.totals(record())
        self.assertEqual(totals["methods"], 1)
        self.assertEqual(battery.stage_outcome(0, totals), (0, "OK"))

    def test_02_invalid_root(self):
        for value in (None, [], False, "x", {}, {**record(), "extra": 1}):
            with self.subTest(value=value):
                with self.assertRaises(battery.WorkerRecordError):
                    self.totals(value)

    def test_03_exit_code_type_and_mismatch(self):
        for value in (False, "0", 0.0, 1):
            with self.subTest(value=value):
                with self.assertRaises(battery.WorkerRecordError):
                    self.totals(record(code=value))

    def test_04_invalid_inventory(self):
        for value in ([], {"0": 1}, {"1": True}, {"1": 0}, {"x": 1}):
            with self.subTest(value=value):
                data = record()
                data["calls_by_line"] = value
                with self.assertRaises(battery.WorkerRecordError):
                    self.totals(data)

    def test_05_invalid_unittest_counts(self):
        for name in ("methods", "failures", "errors", "expected_failures", "unexpected_successes"):
            for value in (-1, False, 1.0, "1"):
                with self.subTest(name=name, value=value):
                    data = record()
                    data["unittest"][0][name] = value
                    with self.assertRaises(battery.WorkerRecordError):
                        self.totals(data)
        data = record()
        del data["unittest"][0]["methods"]
        with self.assertRaises(battery.WorkerRecordError):
            self.totals(data)

    def test_06_invalid_skip_details(self):
        for value in ({}, [None], [{"test": "x"}], [{"test": "x", "reason": 1}]):
            with self.subTest(value=value):
                with self.assertRaises(battery.WorkerRecordError):
                    self.totals(record(skipped=value))

    def test_07_missing_unittest_run_is_incomplete(self):
        data = record()
        data["unittest"] = []
        totals = self.totals(data)
        self.assertTrue(totals["incomplete"])
        self.assertEqual(battery.stage_outcome(0, totals), (0, "INCOMPLETO"))

    def test_08_zero_methods_are_incomplete(self):
        self.assertEqual(battery.stage_outcome(0, self.totals(record(methods=0))),
                         (0, "INCOMPLETO"))

    def test_09_failure_even_if_process_exits_zero(self):
        self.assertEqual(battery.stage_outcome(0, self.totals(record(failures=1))),
                         (1, "FALLO"))

    def test_10_error_even_if_process_exits_zero(self):
        self.assertEqual(battery.stage_outcome(0, self.totals(record(errors=1))),
                         (1, "FALLO"))

    def test_11_omissions_remain_incomplete(self):
        for data in (record(skipped=[{"test": "x", "reason": "ficticia"}]),
                     record(expected_failures=1)):
            with self.subTest(data=data):
                totals = self.totals(data)
                self.assertTrue(totals["incomplete"])
                self.assertEqual(battery.stage_outcome(0, totals), (0, "OK_CON_OMISIONES"))

    def test_12_unexpected_success_is_failure(self):
        self.assertEqual(battery.stage_outcome(0, self.totals(record(unexpected_successes=1))),
                         (1, "FALLO"))

    def test_13_non_unittest_stage_can_have_no_runs(self):
        data = record()
        data["unittest"] = []
        self.assertEqual(battery.stage_outcome(0, self.totals(data, requires=False)), (0, "OK"))

    def test_14_invalid_or_missing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.json"
            with self.assertRaises(battery.WorkerRecordError):
                battery.load_worker_record(path, 0, requires_unittest=True)
            for raw in (b"{", b"\xff", b'{"x":NaN}', b'{"x":1,"x":2}'):
                path.write_bytes(raw)
                with self.assertRaises(battery.WorkerRecordError):
                    battery.load_worker_record(path, 0, requires_unittest=True)
            path.write_bytes(b"x" * 17)
            with patch.object(battery, "MAX_WORKER_RECORD_BYTES", 16):
                with self.assertRaises(battery.WorkerRecordError):
                    battery.load_worker_record(path, 0, requires_unittest=True)

    def test_15_valid_file_and_controlled_record_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "record.json"
            path.write_text(json.dumps(record()), encoding="utf-8")
            data, totals = battery.load_worker_record(path, 0, requires_unittest=True)
        self.assertEqual(data, record())
        self.assertEqual(battery.stage_outcome(0, totals, "Registro rechazado"), (1, "FALLO"))

    def test_16_worker_normalizes_false_exit(self):
        code, data, _ = self.run_worker("import sys; sys.exit(False)\n")
        self.assertEqual(code, 0)
        self.assertIs(type(data["exit_code"]), int)

    def test_17_real_captured_failure_cannot_be_ok(self):
        program = ("import unittest\n"
                   "class Fictitious(unittest.TestCase):\n"
                   "    def test_failure(self): self.fail('fallo ficticio')\n"
                   "unittest.main(exit=False)\n")
        code, _, totals = self.run_worker(program)
        self.assertEqual(code, 0)
        self.assertEqual(totals["failures"], 1)
        self.assertEqual(battery.stage_outcome(code, totals), (1, "FALLO"))

    def test_18_real_empty_suite_is_incomplete(self):
        code, data, _ = self.run_worker("import unittest; unittest.main(exit=False)\n")
        totals = self.totals(data, code)
        self.assertEqual(battery.stage_outcome(code, totals), (0, "INCOMPLETO"))

    def test_19_worker_normalizes_true_exit(self):
        code, data, totals = self.run_worker("import sys; sys.exit(True)\n")
        self.assertEqual(code, 1)
        self.assertIs(type(data["exit_code"]), int)
        self.assertEqual(battery.stage_outcome(code, totals), (1, "FALLO"))

    def test_20_real_success_keeps_zero(self):
        program = ("import unittest\n"
                   "class Fictitious(unittest.TestCase):\n"
                   "    def test_success(self): self.assertEqual(1, 1)\n"
                   "unittest.main()\n")
        code, data, totals = self.run_worker(program)
        self.assertEqual(totals["methods"], 1)
        self.assertIs(type(data["exit_code"]), int)
        self.assertEqual(battery.stage_outcome(code, totals), (0, "OK"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
