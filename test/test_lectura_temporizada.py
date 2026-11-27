"""Regresión del lector temporizado Unix con una pseudoterminal real.

Usa solo datos ficticios. Requiere Linux.
"""
import os
import select
import signal
import subprocess
import sys
import time
import unittest
from pathlib import Path

if sys.platform.startswith("linux"):
    import pty
    import termios

ROOT = Path(__file__).resolve().parents[1]
TIMEOUT = 1
MARGIN = 3.0

CHILD = r"""
import sys
sys.path.insert(0, sys.argv[1])
import bip39_seed_report as report
try:
    value = report.timed_input("> ", timeout_seconds=int(sys.argv[2]))
except report.InputTimeoutError:
    sys.stderr.write("TIMEOUT\n")
    sys.exit(3)
sys.stderr.write("VALUE:" + value + "\n")
sys.exit(0)
"""


@unittest.skipUnless(sys.platform.startswith("linux"), "Requiere Linux.")
class TimedReaderPtyTests(unittest.TestCase):
    def _close_fd(self, fd):
        try:
            os.close(fd)
        except OSError:
            pass

    def _kill(self, proc):
        if proc.poll() is None:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        proc.wait(timeout=5)
        if proc.stderr is not None:
            proc.stderr.close()

    def _drain(self, delay=0.05):
        try:
            ready, _, _ = select.select([self.master], [], [], delay)
            if ready:
                return os.read(self.master, 4096)
        except OSError:
            pass
        return b""

    def _wait_for_prompt(self):
        seen = b""
        deadline = time.monotonic() + 20
        while b"> " not in seen:
            if time.monotonic() > deadline or self.proc.poll() is not None:
                detail = ""
                if self.proc.poll() is not None and self.proc.stderr is not None:
                    detail = self.proc.stderr.read().decode(errors="replace")[-500:]
                self.fail("El auxiliar no llegó al prompt. " + detail)
            seen += self._drain()

    def _start(self, noncanonical):
        master, slave = pty.openpty()
        self.addCleanup(self._close_fd, master)
        if noncanonical:
            attrs = termios.tcgetattr(slave)
            attrs[3] &= ~(termios.ICANON | termios.ECHO)
            attrs[6][termios.VMIN] = 1
            attrs[6][termios.VTIME] = 0
            termios.tcsetattr(slave, termios.TCSANOW, attrs)
        proc = subprocess.Popen(
            [sys.executable, "-B", "-c", CHILD, str(ROOT), str(TIMEOUT)],
            stdin=slave, stdout=slave, stderr=subprocess.PIPE,
            close_fds=True, start_new_session=True,
        )
        os.close(slave)
        self.addCleanup(self._kill, proc)
        self.master, self.proc = master, proc
        self._wait_for_prompt()

    def _wait_exit(self, limit, trickle=False):
        end = time.monotonic() + limit
        while time.monotonic() < end:
            code = self.proc.poll()
            if code is not None:
                return code
            if trickle:
                try:
                    os.write(self.master, b"x")
                except OSError:
                    pass
            self._drain(0.2)
        return self.proc.poll()

    def test_01_without_input_times_out_in_canonical_terminal(self):
        self._start(noncanonical=False)
        self.assertEqual(self._wait_exit(TIMEOUT + MARGIN), 3)

    def test_02_complete_line_is_returned_once(self):
        self._start(noncanonical=False)
        os.write(self.master, b"ok\n")
        self.assertEqual(self._wait_exit(MARGIN), 0)
        self.assertIn("VALUE:ok", self.proc.stderr.read().decode())

    def test_03_partial_line_without_enter_times_out(self):
        self._start(noncanonical=True)
        os.write(self.master, b"x")
        self.assertEqual(
            self._wait_exit(TIMEOUT + MARGIN), 3,
            "El lector siguió bloqueado tras vencer el plazo.",
        )

    def test_04_trickled_characters_do_not_extend_deadline(self):
        self._start(noncanonical=True)
        self.assertEqual(
            self._wait_exit(TIMEOUT + MARGIN, trickle=True), 3,
            "Los caracteres recibidos prolongaron el plazo.",
        )

    def test_05_noncanonical_complete_line_is_returned(self):
        self._start(noncanonical=True)
        os.write(self.master, b"ok\r")
        self.assertEqual(self._wait_exit(MARGIN), 0)
        self.assertIn("VALUE:ok", self.proc.stderr.read().decode())


if __name__ == "__main__":
    unittest.main(verbosity=2)
