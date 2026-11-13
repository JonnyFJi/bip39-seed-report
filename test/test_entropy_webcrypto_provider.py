import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

from unittest.mock import patch

import entropy_all_config as config

from entropy_policy import (
    PROVIDER_ORDER,
    EntropyPolicyError,
    GenerationMode,
    ProviderStatus,
)

from entropy_coordinator import (
    CoordinatorCriticalError,
    ProviderProtocolError,
    acquire_contributions,
)

from entropy_process_runner import (
    ProcessProviderRunner,
)


OS, JAVA, JS, SECRETS = PROVIDER_ORDER

JS_TEST = (
    pathlib.Path(__file__).resolve().parent
    / "js"
    / "test_webcrypto_provider.cjs"
)


@unittest.skipUnless(
    sys.platform.startswith("linux"),
    "Proveedores Linux",
)
class WebCryptoProviderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for path in (
            config.NODE_EXECUTABLE,
            config.WEBCRYPTO_HELPER,
            JS_TEST,
        ):
            if not path.is_file():
                raise RuntimeError(
                    "Falta un archivo necesario "
                    "para la etapa Web Crypto."
                )

    def commands(self):
        return config.build_all_provider_commands()

    def acquire(self, commands):
        return acquire_contributions(
            ProcessProviderRunner(commands),
            timeout_seconds=10.0,
        )

    def invoke(
        self,
        args,
        *,
        stdout=subprocess.PIPE,
    ):
        return subprocess.run(
            [
                str(config.NODE_EXECUTABLE),
                str(config.WEBCRYPTO_HELPER),
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

    def test_configuration_enables_all_four(self):
        commands = self.commands()

        self.assertEqual(
            set(commands),
            set(PROVIDER_ORDER),
        )

        self.assertTrue(
            all(
                commands[p] is not None
                for p in PROVIDER_ORDER
            )
        )

        self.assertEqual(
            commands[JS],
            (
                str(config.NODE_EXECUTABLE),
                str(config.WEBCRYPTO_HELPER),
            ),
        )

        self.assertNotEqual(
            commands[JS][0],
            "/usr/bin/node",
        )

    def test_webcrypto_returns_32_binary_bytes(self):
        data = ProcessProviderRunner(
            self.commands()
        ).acquire(
            JS,
            32,
            timeout_seconds=10.0,
        )

        self.assertIs(type(data), bytes)
        self.assertEqual(len(data), 32)

    def test_all_four_real_providers_connected(self):
        result = self.acquire(
            self.commands()
        )

        self.assertEqual(
            result.plan.mode,
            GenerationMode.REDUNDANT,
        )

        self.assertEqual(
            result.plan.provider_ids,
            PROVIDER_ORDER,
        )

        self.assertEqual(
            tuple(result.contributions),
            PROVIDER_ORDER,
        )

        self.assertEqual(
            result.plan.failed_provider_ids,
            (),
        )

        self.assertEqual(
            result.plan.omitted_provider_ids,
            (),
        )

        self.assertTrue(
            all(
                o.status is ProviderStatus.OK
                for o in result.outcomes
            )
        )

        for data in result.contributions.values():
            self.assertEqual(len(data), 32)

    def test_each_disabled_provider_keeps_other_three(self):
        for disabled in PROVIDER_ORDER:
            with self.subTest(
                disabled=disabled
            ):
                commands = self.commands()
                commands[disabled] = None

                result = self.acquire(commands)

                self.assertEqual(
                    result.plan.mode,
                    GenerationMode.REDUNDANT,
                )

                self.assertEqual(
                    set(result.contributions),
                    set(PROVIDER_ORDER) - {disabled},
                )

                self.assertEqual(
                    result.plan.failed_provider_ids,
                    (disabled,),
                )

    def test_real_java_javascript_pair_without_python(self):
        commands = self.commands()

        commands[OS] = None
        commands[SECRETS] = None

        result = self.acquire(commands)

        self.assertEqual(
            result.plan.mode,
            GenerationMode.REDUCED,
        )

        self.assertEqual(
            set(result.contributions),
            {JAVA, JS},
        )

    def test_os_backup_with_both_python_providers_available(self):
        commands = self.commands()

        commands[JAVA] = None
        commands[JS] = None

        result = self.acquire(commands)

        self.assertEqual(
            result.plan.mode,
            GenerationMode.OS_BACKUP,
        )

        self.assertEqual(
            tuple(result.contributions),
            (OS,),
        )

        self.assertIn(
            SECRETS,
            result.plan.omitted_provider_ids,
        )

        self.assertNotIn(
            SECRETS,
            result.plan.failed_provider_ids,
        )

    def test_webcrypto_alone_is_not_authorized(self):
        commands = self.commands()

        for provider in (
            OS,
            JAVA,
            SECRETS,
        ):
            commands[provider] = None

        with self.assertRaises(
            EntropyPolicyError
        ):
            self.acquire(commands)

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
                JS,
                "--bytes",
                "31",
            ],
            [
                "--provider",
                JS,
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
                    JS,
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

    def test_missing_helper_is_configuration_error(self):
        with patch.object(
            config,
            "WEBCRYPTO_HELPER",
            pathlib.Path(
                "/nonexistent-webcrypto-helper"
            ),
        ):
            with self.assertRaises(ValueError):
                config.build_all_provider_commands()

    def test_missing_isolated_node_does_not_fallback_to_system_node(self):
        with tempfile.TemporaryDirectory(
            prefix="missing-node-test-"
        ) as directory:
            with patch.object(
                config,
                "NODE_EXECUTABLE",
                (
                    pathlib.Path(directory)
                    / "missing-node"
                ),
            ):
                result = self.acquire(
                    self.commands()
                )

        self.assertEqual(
            result.plan.mode,
            GenerationMode.REDUNDANT,
        )

        self.assertNotIn(
            JS,
            result.contributions,
        )

        statuses = {
            o.provider_id: o.status
            for o in result.outcomes
        }

        self.assertIs(
            statuses[JS],
            ProviderStatus.UNAVAILABLE,
        )

    def test_profile_change_is_critical_not_os_fallback(self):
        source = (
            config.WEBCRYPTO_HELPER.read_text(
                encoding="utf-8"
            )
        )

        original = (
            'const EXPECTED_NODE_VERSION = '
            '"v24.22.2";'
        )

        self.assertEqual(
            source.count(original),
            1,
        )

        modified = source.replace(
            original,
            (
                'const EXPECTED_NODE_VERSION = '
                '"v0.0.0";'
            ),
            1,
        )

        with tempfile.TemporaryDirectory(
            prefix="webcrypto-profile-test-"
        ) as directory:
            path = (
                pathlib.Path(directory)
                / "changed-profile.cjs"
            )

            path.write_text(
                modified,
                encoding="utf-8",
            )

            commands = self.commands()

            commands[JS] = (
                str(config.NODE_EXECUTABLE),
                str(path),
            )

            with self.assertRaises(
                ProviderProtocolError
            ):
                ProcessProviderRunner(
                    commands
                ).acquire(
                    JS,
                    32,
                    timeout_seconds=10.0,
                )

            with self.assertRaises(
                CoordinatorCriticalError
            ):
                self.acquire(commands)

    def test_javascript_unit_checks(self):
        result = subprocess.run(
            [
                str(config.NODE_EXECUTABLE),
                str(JS_TEST),
                str(config.WEBCRYPTO_HELPER),
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
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

        self.assertEqual(
            result.returncode,
            0,
        )

        self.assertEqual(
            len(result.stderr),
            0,
        )

        self.assertEqual(
            json.loads(
                result.stdout.decode("utf-8")
            ),
            {
                "checks": 14,
                "ok": True,
            },
        )


if __name__ == "__main__":
    unittest.main()
