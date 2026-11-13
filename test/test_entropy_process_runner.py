import os
import pathlib
import subprocess
import sys
import tempfile
import time
import unittest

from unittest.mock import patch

from entropy_policy import PROVIDER_ORDER

from entropy_coordinator import (
    ProviderGenerationError,
    ProviderProtocolError,
    ProviderTimeoutError,
    ProviderUnavailableError,
)

from entropy_process_runner import ProcessProviderRunner


HELPER = r"""
import argparse
import os
import subprocess
import sys
import time

p = argparse.ArgumentParser()
p.add_argument("mode")
p.add_argument("--provider", required=True)
p.add_argument("--bytes", type=int, required=True)
a = p.parse_args()

if a.mode == "ok":
    os.write(1, b"A" * a.bytes)

elif a.mode == "chunks":
    os.write(1, b"A" * 7)
    time.sleep(0.02)
    os.write(1, b"A" * (a.bytes - 7))

elif a.mode == "short":
    os.write(1, b"A" * (a.bytes - 1))

elif a.mode == "long":
    os.write(1, b"A" * (a.bytes + 1))

elif a.mode == "flood":
    while True:
        os.write(1, b"A" * 4096)

elif a.mode == "stderr":
    os.write(2, b"SECRET_SENTINEL")

elif a.mode == "generation_failed":
    sys.exit(10)

elif a.mode == "unavailable":
    sys.exit(11)

elif a.mode == "unknown_exit":
    sys.exit(9)

elif a.mode == "failed_with_output":
    os.write(1, b"A")
    sys.exit(10)

elif a.mode == "sleep":
    time.sleep(30)

elif a.mode == "closed_pipes":
    os.close(1)
    os.close(2)
    time.sleep(30)

elif a.mode == "inherited_pipes":
    subprocess.Popen(
        [
            sys.executable,
            "-I",
            "-S",
            "-c",
            "import time; time.sleep(30)",
        ]
    )
    os.write(1, b"A" * a.bytes)

elif a.mode == "env":
    blocked = (
        "NODE_OPTIONS",
        "JAVA_TOOL_OPTIONS",
        "PYTHONPATH",
        "LD_PRELOAD",
    )

    if any(k in os.environ for k in blocked):
        sys.exit(9)

    os.write(1, b"A" * a.bytes)

elif a.mode == "argv":
    valid = (
        a.provider in {
            "python_os",
            "java_secure_random",
            "javascript_webcrypto",
            "python_secrets",
        }
        and a.bytes == 32
    )

    if not valid:
        sys.exit(9)

    os.write(1, b"A" * 32)
"""


@unittest.skipUnless(
    os.name == "posix",
    "Ejecutor POSIX",
)
class EntropyProcessRunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(
            prefix="entropy-runner-test-"
        )

        cls.addClassCleanup(cls.tmp.cleanup)

        cls.helper = (
            pathlib.Path(cls.tmp.name)
            / "fake provider.py"
        )

        cls.helper.write_text(
            HELPER,
            encoding="utf-8",
        )

    def runner(self, mode="ok"):
        command = (
            sys.executable,
            "-I",
            "-S",
            str(self.helper),
            mode,
        )

        return ProcessProviderRunner(
            {
                p: command
                for p in PROVIDER_ORDER
            }
        )

    def acquire(self, runner, timeout=3.0):
        return runner.acquire(
            "python_os",
            32,
            timeout_seconds=timeout,
        )

    def captured_run(
        self,
        runner,
        error,
        timeout=3.0,
        interrupt=False,
    ):
        spawned = []
        original = subprocess.Popen

        def spawn(*args, **kwargs):
            proc = original(*args, **kwargs)
            spawned.append(proc)
            return proc

        with patch(
            "entropy_process_runner.subprocess.Popen",
            side_effect=spawn,
        ):
            if interrupt:
                with patch(
                    "entropy_process_runner.selectors.DefaultSelector",
                    side_effect=KeyboardInterrupt,
                ):
                    with self.assertRaises(error):
                        self.acquire(
                            runner,
                            timeout,
                        )

            else:
                with self.assertRaises(error):
                    self.acquire(
                        runner,
                        timeout,
                    )

        self.assertEqual(len(spawned), 1)

        proc = spawned[0]

        self.assertIsNotNone(proc.returncode)
        self.assertTrue(proc.stdout.closed)
        self.assertTrue(proc.stderr.closed)

    def test_valid_binary_and_space_in_helper_path(self):
        self.assertEqual(
            self.acquire(self.runner()),
            b"A" * 32,
        )

    def test_partial_reads(self):
        self.assertEqual(
            self.acquire(self.runner("chunks")),
            b"A" * 32,
        )

    def test_request_arguments(self):
        self.assertEqual(
            self.acquire(self.runner("argv")),
            b"A" * 32,
        )

    def test_invalid_lengths_and_exit_codes(self):
        modes = (
            "short",
            "long",
            "unknown_exit",
            "failed_with_output",
        )

        for mode in modes:
            with self.subTest(mode=mode):
                self.captured_run(
                    self.runner(mode),
                    ProviderProtocolError,
                )

    def test_output_flood_is_rejected(self):
        self.captured_run(
            self.runner("flood"),
            ProviderProtocolError,
        )

    def test_stderr_is_not_exposed(self):
        with self.assertRaises(
            ProviderProtocolError
        ) as caught:
            self.acquire(
                self.runner("stderr")
            )

        self.assertNotIn(
            "SECRET_SENTINEL",
            str(caught.exception),
        )

    def test_declared_generation_failure(self):
        self.captured_run(
            self.runner("generation_failed"),
            ProviderGenerationError,
        )

    def test_declared_unavailability(self):
        self.captured_run(
            self.runner("unavailable"),
            ProviderUnavailableError,
        )

    def test_timeout_and_direct_child_cleanup(self):
        start = time.monotonic()

        self.captured_run(
            self.runner("sleep"),
            ProviderTimeoutError,
            timeout=0.3,
        )

        self.assertLess(
            time.monotonic() - start,
            5.0,
        )

    def test_timeout_after_pipes_are_closed(self):
        self.captured_run(
            self.runner("closed_pipes"),
            ProviderTimeoutError,
            timeout=0.3,
        )

    def test_timeout_with_inherited_pipes(self):
        self.captured_run(
            self.runner("inherited_pipes"),
            ProviderTimeoutError,
            timeout=0.5,
        )

    def test_keyboard_interrupt_cleans_direct_child(self):
        self.captured_run(
            self.runner("sleep"),
            KeyboardInterrupt,
            interrupt=True,
        )

    def test_missing_executable(self):
        missing = str(
            pathlib.Path(self.tmp.name)
            / "missing"
        )

        runner = ProcessProviderRunner(
            {
                p: (missing,)
                for p in PROVIDER_ORDER
            }
        )

        with self.assertRaises(
            ProviderUnavailableError
        ):
            self.acquire(runner)

    def test_disabled_provider(self):
        runner = ProcessProviderRunner(
            {
                p: None
                for p in PROVIDER_ORDER
            }
        )

        with self.assertRaises(
            ProviderUnavailableError
        ):
            self.acquire(runner)

    def test_no_shell(self):
        command = (
            sys.executable,
            "-I",
            "-S",
            str(self.helper),
            "ok; exit 0",
        )

        runner = ProcessProviderRunner(
            {
                p: command
                for p in PROVIDER_ORDER
            }
        )

        with self.assertRaises(
            ProviderProtocolError
        ):
            self.acquire(runner)

    def test_parent_environment_is_not_inherited(self):
        variables = (
            "NODE_OPTIONS",
            "JAVA_TOOL_OPTIONS",
            "PYTHONPATH",
            "LD_PRELOAD",
        )

        with patch.dict(
            os.environ,
            {
                k: "test-only"
                for k in variables
            },
        ):
            self.assertEqual(
                self.acquire(self.runner("env")),
                b"A" * 32,
            )

    def test_invalid_configuration(self):
        with self.assertRaises(ValueError):
            ProcessProviderRunner({})

        invalid_commands = (
            "python",
            (),
            ("python",),
            (sys.executable, 1),
            (sys.executable, "\0"),
        )

        for invalid in invalid_commands:
            with self.subTest(command=invalid):
                with self.assertRaises(ValueError):
                    ProcessProviderRunner(
                        {
                            p: invalid
                            for p in PROVIDER_ORDER
                        }
                    )

    def test_invalid_request(self):
        runner = self.runner()

        for size in (0, 31, 33, True, "32"):
            with self.subTest(size=size):
                with self.assertRaises(ValueError):
                    runner.acquire(
                        "python_os",
                        size,
                        timeout_seconds=3.0,
                    )

        invalid_timeouts = (
            0,
            -1,
            True,
            None,
            "3",
            float("nan"),
            float("inf"),
        )

        for timeout in invalid_timeouts:
            with self.subTest(timeout=timeout):
                with self.assertRaises(ValueError):
                    self.acquire(
                        runner,
                        timeout,
                    )

        with self.assertRaises(ValueError):
            runner.acquire(
                "unknown",
                32,
                timeout_seconds=3.0,
            )


if __name__ == "__main__":
    unittest.main()
