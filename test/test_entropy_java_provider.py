import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

from unittest.mock import patch

import entropy_java_config as config

from entropy_policy import (
    EntropyPolicyError,
    GenerationMode,
    ProviderStatus,
)

from entropy_coordinator import (
    CoordinatorCriticalError,
    ProviderProtocolError,
    ProviderUnavailableError,
    acquire_contributions,
)

from entropy_process_runner import (
    ProcessProviderRunner,
)


JAVA = "java_secure_random"


@unittest.skipUnless(
    sys.platform.startswith("linux"),
    "Auxiliar Java para Linux",
)
class JavaEntropyProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not pathlib.Path(
            config.JAVA_EXECUTABLE
        ).is_file():
            raise RuntimeError(
                "No se encontro el Java configurado."
            )

        if not config.CLASS_FILE.is_file():
            raise RuntimeError(
                "Compila el auxiliar Java "
                "antes de estas pruebas."
            )

    def commands(self):
        return config.build_python_java_commands()

    def invoke(
        self,
        args,
        *,
        stdout=subprocess.PIPE,
    ):
        return subprocess.run(
            [
                config.JAVA_EXECUTABLE,
                "-cp",
                str(config.CLASS_DIRECTORY),
                "JavaEntropyProvider",
                *args,
            ],
            stdin=subprocess.DEVNULL,
            stdout=stdout,
            stderr=subprocess.PIPE,
            env={
                "PATH": os.defpath,
                "LANG": "C",
                "LC_ALL": "C",
            },
            cwd="/",
            timeout=10.0,
            check=False,
        )

    def security_commands(self, path):
        commands = self.commands()

        commands[JAVA] = (
            config.JAVA_EXECUTABLE,
            (
                "-Djava.security.properties="
                + str(path)
            ),
            "-cp",
            str(config.CLASS_DIRECTORY),
            "JavaEntropyProvider",
        )

        return commands

    def test_configuration_enables_python_and_java(self):
        commands = self.commands()

        for provider in (
            "python_os",
            "python_secrets",
            JAVA,
        ):
            self.assertIsNotNone(
                commands[provider]
            )

        self.assertIsNone(
            commands["javascript_webcrypto"]
        )

        self.assertEqual(
            commands[JAVA][0],
            config.JAVA_EXECUTABLE,
        )

        self.assertEqual(
            commands[JAVA][-1],
            "JavaEntropyProvider",
        )

    def test_java_returns_32_binary_bytes(self):
        data = ProcessProviderRunner(
            self.commands()
        ).acquire(
            JAVA,
            32,
            timeout_seconds=10.0,
        )

        self.assertIs(
            type(data),
            bytes,
        )

        self.assertEqual(
            len(data),
            32,
        )

    def test_three_real_providers_use_redundant_mode(self):
        result = acquire_contributions(
            ProcessProviderRunner(
                self.commands()
            ),
            timeout_seconds=10.0,
        )

        self.assertEqual(
            result.plan.mode,
            GenerationMode.REDUNDANT,
        )

        self.assertEqual(
            set(result.contributions),
            {
                "python_os",
                JAVA,
                "python_secrets",
            },
        )

        for data in result.contributions.values():
            self.assertEqual(
                len(data),
                32,
            )

        statuses = {
            o.provider_id: o.status
            for o in result.outcomes
        }

        self.assertIs(
            statuses[JAVA],
            ProviderStatus.OK,
        )

        self.assertIs(
            statuses["javascript_webcrypto"],
            ProviderStatus.UNAVAILABLE,
        )

    def test_java_alone_does_not_authorize_generation(self):
        commands = self.commands()

        commands["python_os"] = None
        commands["python_secrets"] = None

        with self.assertRaises(
            EntropyPolicyError
        ):
            acquire_contributions(
                ProcessProviderRunner(commands),
                timeout_seconds=10.0,
            )

    def test_invalid_cli_is_quiet(self):
        cases = (
            [],
            ["--help"],
            [
                "--provider",
                "python_os",
                "--bytes",
                "32",
            ],
            [
                "--provider",
                JAVA,
                "--bytes",
                "31",
            ],
            [
                "--provider",
                JAVA,
                "--bytes",
                "32",
                "extra",
            ],
        )

        for args in cases:
            with self.subTest(args=args):
                result = self.invoke(args)

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

    def test_non_pipe_stdout_is_refused(self):
        with open(
            os.devnull,
            "wb",
        ) as target:
            result = self.invoke(
                [
                    "--provider",
                    JAVA,
                    "--bytes",
                    "32",
                ],
                stdout=target,
            )

        self.assertEqual(
            result.returncode,
            12,
        )

        self.assertEqual(
            len(result.stderr),
            0,
        )

    def test_unavailable_algorithm_is_reported(self):
        with tempfile.TemporaryDirectory(
            prefix="java-security-test-"
        ) as directory:
            path = (
                pathlib.Path(directory)
                / "test.security"
            )

            path.write_text(
                "securerandom.strongAlgorithms="
                "MissingEntropyTest:SUN\n",
                encoding="ascii",
            )

            runner = ProcessProviderRunner(
                self.security_commands(path)
            )

            with self.assertRaises(
                ProviderUnavailableError
            ):
                runner.acquire(
                    JAVA,
                    32,
                    timeout_seconds=10.0,
                )

    def test_algorithm_change_is_critical(self):
        with tempfile.TemporaryDirectory(
            prefix="java-security-test-"
        ) as directory:
            path = (
                pathlib.Path(directory)
                / "test.security"
            )

            path.write_text(
                "securerandom.strongAlgorithms="
                "DRBG:SUN\n",
                encoding="ascii",
            )

            runner = ProcessProviderRunner(
                self.security_commands(path)
            )

            with self.assertRaises(
                ProviderProtocolError
            ):
                runner.acquire(
                    JAVA,
                    32,
                    timeout_seconds=10.0,
                )

    def test_algorithm_change_does_not_trigger_os_fallback(self):
        with tempfile.TemporaryDirectory(
            prefix="java-security-test-"
        ) as directory:
            path = (
                pathlib.Path(directory)
                / "test.security"
            )

            path.write_text(
                "securerandom.strongAlgorithms="
                "DRBG:SUN\n",
                encoding="ascii",
            )

            runner = ProcessProviderRunner(
                self.security_commands(path)
            )

            with self.assertRaises(
                CoordinatorCriticalError
            ):
                acquire_contributions(
                    runner,
                    timeout_seconds=10.0,
                )

    def test_missing_class_is_configuration_error(self):
        with patch.object(
            config,
            "CLASS_FILE",
            pathlib.Path(
                "/nonexistent-java-entropy-class"
            ),
        ):
            with self.assertRaises(ValueError):
                config.build_python_java_commands()


if __name__ == "__main__":
    unittest.main()
