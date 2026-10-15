#!/usr/bin/env python3
"""Pruebas de escritura con datos ficticios y carpetas temporales."""
import concurrent.futures
import errno
import json
import multiprocessing
import os
from pathlib import Path
import stat
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

import bip39_seed_report as report


def _worker_export(base, number, barrier, queue):
    try:
        with patch.object(report, "_encrypt_report_content",
                          side_effect=lambda content, password: "FICTICIO:" + content):
            barrier.wait(timeout=30)
            path = report.export_seed_report({"worker": number}, base, "json", "ficticia")
            queue.put((True, number, str(path)))
    except Exception as exc:
        queue.put((False, number, type(exc).__name__))


class WriteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="bip39-write-tests-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = self.root / "reporte.json"

    def assert_no_temporaries(self):
        self.assertEqual(list(self.root.glob(".bip39-report-*.tmp")), [])

    def test_01_exact_write(self):
        self.assertIsNone(report.write_secure_file(self.path, "dato ficticio", encrypt=False))
        self.assertEqual(self.path.read_text(), "dato ficticio")
        self.assert_no_temporaries()

    def test_02_existing_file_preserved(self):
        self.path.write_text("anterior")
        with self.assertRaises(FileExistsError):
            report.write_secure_file(self.path, "nuevo", encrypt=False)
        self.assertEqual(self.path.read_text(), "anterior")
        self.assert_no_temporaries()

    def test_03_export_sequential_and_encrypt_once(self):
        self.path.write_text("anterior")
        with patch.object(report, "_encrypt_report_content", return_value="FICTICIO") as enc:
            final = report.export_seed_report({"test": True}, self.path, "json", "ficticia")
            enc.assert_called_once()
        self.assertEqual(final.name, "reporte_001.json")
        self.assertEqual(final.read_text(), "FICTICIO")
        self.assertEqual(self.path.read_text(), "anterior")
        self.assert_no_temporaries()

    def test_04_forced_collision_between_attempt_and_link(self):
        original_link = os.link
        created = False
        def collision(src, dst):
            nonlocal created
            if not created:
                created = True
                Path(dst).write_text("otro proceso ficticio")
            return original_link(src, dst)
        with patch.object(report, "_encrypt_report_content", return_value="FICTICIO") as enc:
            with patch.object(report.os, "link", side_effect=collision):
                final = report.export_seed_report({}, self.path, "json", "ficticia")
            enc.assert_called_once()
        self.assertEqual(self.path.read_text(), "otro proceso ficticio")
        self.assertEqual(final.name, "reporte_001.json")
        self.assert_no_temporaries()

    def test_05_missing_hardlink_support_fails_closed(self):
        with patch.object(report.os, "link", side_effect=OSError(errno.EOPNOTSUPP, "simulado")):
            with self.assertRaises(OSError):
                report.write_secure_file(self.path, "ficticio", encrypt=False)
        self.assertFalse(self.path.exists())
        self.assert_no_temporaries()

    def test_06_fsync_failure_does_not_publish(self):
        with patch.object(report.os, "fsync", side_effect=OSError("simulado")):
            with self.assertRaises(OSError):
                report.write_secure_file(self.path, "ficticio", encrypt=False)
        self.assertFalse(self.path.exists())
        self.assert_no_temporaries()

    @unittest.skipUnless(os.name == "posix", "Permisos POSIX")
    def test_07_mode_0600(self):
        report.write_secure_file(self.path, "ficticio", encrypt=False)
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o600)

    @unittest.skipUnless(os.name == "posix", "fchmod POSIX")
    def test_08_permission_failure_does_not_publish(self):
        with patch.object(report.os, "fchmod", side_effect=OSError("simulado")):
            with self.assertRaises(OSError):
                report.write_secure_file(self.path, "ficticio", encrypt=False)
        self.assertFalse(self.path.exists())
        self.assert_no_temporaries()

    def test_09_existing_symlink_not_followed(self):
        target = self.root / "objetivo"
        target.write_text("no tocar")
        try:
            self.path.symlink_to(target)
        except OSError:
            self.skipTest("Creacion de symlink no disponible")
        with self.assertRaises(FileExistsError):
            report.write_secure_file(self.path, "nuevo", encrypt=False)
        self.assertTrue(self.path.is_symlink())
        self.assertEqual(target.read_text(), "no tocar")

    def test_10_broken_symlink_occupied(self):
        target = self.root / "ausente"
        try:
            self.path.symlink_to(target)
        except OSError:
            self.skipTest("Creacion de symlink no disponible")
        self.assertEqual(report.generate_sequential_path(self.path).name, "reporte_001.json")
        with patch.object(report, "_encrypt_report_content", return_value="FICTICIO"):
            final = report.export_seed_report({}, self.path, "json", "ficticia")
        self.assertEqual(final.name, "reporte_001.json")
        self.assertFalse(target.exists())
        self.assertTrue(self.path.is_symlink())

    def test_11_thread_race_exact_one_winner(self):
        barrier = threading.Barrier(8)
        def worker(i):
            barrier.wait(timeout=20)
            try:
                report.write_secure_file(self.path, str(i), encrypt=False)
                return i
            except FileExistsError:
                return None
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            winners = [i for i in pool.map(worker, range(8)) if i is not None]
        self.assertEqual(len(winners), 1)
        self.assertEqual(self.path.read_text(), str(winners[0]))
        self.assert_no_temporaries()

    @unittest.skipUnless(sys.platform.startswith("linux"), "Procesos: ensayo Linux con fork")
    def test_12_process_exports_unique(self):
        ctx = multiprocessing.get_context("fork")
        barrier = ctx.Barrier(4)
        queue = ctx.Queue()
        processes = [ctx.Process(target=_worker_export,
                     args=(str(self.path), i, barrier, queue)) for i in range(4)]
        try:
            for proc in processes:
                proc.start()
            results = [queue.get(timeout=45) for _ in processes]
            for proc in processes:
                proc.join(timeout=10)
                self.assertFalse(proc.is_alive())
                self.assertEqual(proc.exitcode, 0)
            self.assertTrue(all(item[0] for item in results), repr(results))
            paths = [Path(item[2]) for item in results]
            self.assertEqual(len(set(paths)), 4)
            for _, i, name in results:
                payload = Path(name).read_text()
                self.assertTrue(payload.startswith("FICTICIO:"))
                self.assertEqual(json.loads(payload[len("FICTICIO:"):]), {"worker": i})
            self.assert_no_temporaries()
        finally:
            for proc in processes:
                if proc.pid is not None:
                    if proc.is_alive():
                        proc.terminate()
                    proc.join(timeout=5)
            queue.close()

    def test_13_attempt_limit(self):
        with patch.object(report, "MAX_REPORT_PATH_ATTEMPTS", 2):
            self.path.write_text("base")
            (self.root / "reporte_001.json").write_text("uno")
            with patch.object(report, "_encrypt_report_content", return_value="FICTICIO"):
                with self.assertRaises(FileExistsError):
                    report.export_seed_report({}, self.path, "json", "ficticia")
        self.assertEqual(self.path.read_text(), "base")
        self.assertEqual((self.root / "reporte_001.json").read_text(), "uno")
        self.assert_no_temporaries()

    def test_14_new_directory_with_spaces(self):
        path = self.root / "carpeta con espacios" / "reporte.json"
        report.write_secure_file(path, "ficticio", encrypt=False)
        self.assertEqual(path.read_text(), "ficticio")

    def test_15_completed_file_before_publication(self):
        original_link = os.link
        def inspect(src, dst):
            self.assertEqual(Path(src).read_text(), "contenido completo")
            self.assertFalse(Path(dst).exists())
            return original_link(src, dst)
        with patch.object(report.os, "link", side_effect=inspect):
            report.write_secure_file(self.path, "contenido completo", encrypt=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
