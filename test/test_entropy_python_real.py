import os
import subprocess
import sys
import unittest

from entropy_policy import (
    EntropyPolicyError,
    GenerationMode,
    ProviderStatus,
)

from entropy_coordinator import (
    acquire_contributions,
)

from entropy_process_runner import (
    ProcessProviderRunner,
)

from entropy_python_config import (
    HELPER_PATH,
    build_python_only_commands,
)


@unittest.skipUnless(
    os.name == "posix",
    "Ejecutor POSIX",
)
class PythonEntropyRealTests(unittest.TestCase):
    def test_each_real_python_provider_through_runner(self):
        runner = ProcessProviderRunner(
            build_python_only_commands()
        )

        for provider in (
            "python_os",
            "python_secrets",
        ):
            with self.subTest(
                provider=provider
            ):
                data = runner.acquire(
                    provider,
                    32,
                    timeout_seconds=5.0,
                )

                self.assertIs(
                    type(data),
                    bytes,
                )

                self.assertEqual(
                    len(data),
                    32,
                )

    def test_python_only_configuration_uses_os_backup(self):
        runner = ProcessProviderRunner(
            build_python_only_commands()
        )

        result = acquire_contributions(
            runner,
            timeout_seconds=5.0,
        )

        self.assertEqual(
            result.plan.mode,
            GenerationMode.OS_BACKUP,
        )

        self.assertEqual(
            tuple(result.contributions),
            ("python_os",),
        )

        self.assertEqual(
            len(
                result.contributions[
                    "python_os"
                ]
            ),
            32,
        )

        statuses = {
            o.provider_id: o.status
            for o in result.outcomes
        }

        self.assertIs(
            statuses["python_os"],
            ProviderStatus.OK,
        )

        self.assertIs(
            statuses["python_secrets"],
            ProviderStatus.OK,
        )

        self.assertIs(
            statuses["java_secure_random"],
            ProviderStatus.UNAVAILABLE,
        )

        self.assertIs(
            statuses["javascript_webcrypto"],
            ProviderStatus.UNAVAILABLE,
        )

        self.assertIn(
            "python_secrets",
            result.plan.omitted_provider_ids,
        )

        self.assertNotIn(
            "python_secrets",
            result.plan.failed_provider_ids,
        )

    def test_only_os_enabled_uses_backup(self):
        commands = (
            build_python_only_commands()
        )

        commands["python_secrets"] = None

        result = acquire_contributions(
            ProcessProviderRunner(commands),
            timeout_seconds=5.0,
        )

        self.assertEqual(
            result.plan.mode,
            GenerationMode.OS_BACKUP,
        )

        self.assertEqual(
            tuple(result.contributions),
            ("python_os",),
        )

    def test_only_secrets_enabled_is_not_authorized(self):
        commands = (
            build_python_only_commands()
        )

        commands["python_os"] = None

        with self.assertRaises(
            EntropyPolicyError
        ):
            acquire_contributions(
                ProcessProviderRunner(commands),
                timeout_seconds=5.0,
            )

    def test_invalid_cli_is_quiet(self):
        result = subprocess.run(
            [
                sys.executable,
                "-I",
                "-S",
                str(HELPER_PATH),
                "--help",
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=5.0,
            check=False,
        )

        self.assertEqual(
            result.returncode,
            12,
        )

        self.assertEqual(
            len(result.stdout),
            0,
        )

        self.assertEqual(
            len(result.stderr),
            0,
        )


if __name__ == "__main__":
    unittest.main()
