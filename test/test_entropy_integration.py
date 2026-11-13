import itertools
import os
import pathlib
import sys
import tempfile
import unittest

from unittest.mock import patch

from entropy_policy import (
    CONTRIBUTION_BYTES,
    POLICY_VERSION,
    PROVIDER_ORDER,
    EntropyPolicyError,
    GenerationMode,
    ProviderStatus,
)

from entropy_coordinator import (
    CoordinatorCriticalError,
    acquire_contributions,
)

from entropy_process_runner import (
    ProcessProviderRunner,
)


OS, JAVA, JS, SECRETS = PROVIDER_ORDER

PAYLOADS = {
    p: bytes([i + 1]) * CONTRIBUTION_BYTES
    for i, p in enumerate(PROVIDER_ORDER)
}


HELPER = r"""
import argparse
import os
import sys
import time

p = argparse.ArgumentParser()
p.add_argument("mode")
p.add_argument("log_path")
p.add_argument("--provider", required=True)
p.add_argument("--bytes", type=int, required=True)
a = p.parse_args()

providers = (
    "python_os",
    "java_secure_random",
    "javascript_webcrypto",
    "python_secrets",
)

if a.provider not in providers or a.bytes != 32:
    sys.exit(12)

with open(a.log_path, "a", encoding="ascii") as log:
    log.write(a.provider + "\n")

payload = (
    bytes([providers.index(a.provider) + 1])
    * a.bytes
)

if a.mode == "ok":
    os.write(1, payload)

elif a.mode == "unavailable":
    sys.exit(11)

elif a.mode == "generation_failed":
    sys.exit(10)

elif a.mode == "timeout":
    time.sleep(30)

elif a.mode == "short":
    os.write(1, payload[:-1])

elif a.mode == "long":
    os.write(1, payload + b"X")

elif a.mode == "stderr":
    os.write(2, b"SECRET_SENTINEL")

elif a.mode == "unknown_exit":
    sys.exit(9)

elif a.mode == "failed_with_output":
    os.write(1, b"X")
    sys.exit(10)

else:
    sys.exit(12)
"""


@unittest.skipUnless(
    os.name == "posix",
    "Integracion con ejecutor POSIX",
)
class EntropyIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(
            prefix="entropy-integration-"
        )

        self.addCleanup(self.tmp.cleanup)

        self.directory = pathlib.Path(
            self.tmp.name
        )

        self.helper = (
            self.directory
            / "fake integration provider.py"
        )

        self.helper.write_text(
            HELPER,
            encoding="utf-8",
        )

        self.sequence = 0

    def make_runner(self, modes=None):
        modes = {} if modes is None else modes

        self.sequence += 1

        log_path = (
            self.directory
            / f"calls-{self.sequence}.txt"
        )

        commands = {}

        for p in PROVIDER_ORDER:
            mode = modes.get(p, "ok")

            commands[p] = (
                None
                if mode is None
                else (
                    sys.executable,
                    "-I",
                    "-S",
                    str(self.helper),
                    mode,
                    str(log_path),
                )
            )

        return (
            ProcessProviderRunner(commands),
            log_path,
        )

    def read_calls(self, path):
        if not path.exists():
            return []

        return path.read_text(
            encoding="ascii"
        ).splitlines()

    def acquire(self, runner, timeout=3.0):
        return acquire_contributions(
            runner,
            timeout_seconds=timeout,
        )

    def test_all_16_real_process_combinations(self):
        expected = {
            frozenset({OS}): GenerationMode.OS_BACKUP,
            frozenset({OS, JAVA}): GenerationMode.OS_BACKUP,
            frozenset({OS, JS}): GenerationMode.OS_BACKUP,
            frozenset({OS, SECRETS}): GenerationMode.OS_BACKUP,
            frozenset({JAVA, JS}): GenerationMode.REDUCED,
            frozenset({OS, JAVA, JS}): GenerationMode.REDUNDANT,
            frozenset({OS, JAVA, SECRETS}): GenerationMode.REDUNDANT,
            frozenset({OS, JS, SECRETS}): GenerationMode.REDUNDANT,
            frozenset({JAVA, JS, SECRETS}): GenerationMode.REDUNDANT,
            frozenset(PROVIDER_ORDER): GenerationMode.REDUNDANT,
        }

        checked = 0

        for count in range(5):
            for combination in itertools.combinations(
                PROVIDER_ORDER,
                count,
            ):
                accepted = frozenset(combination)

                modes = {
                    p: (
                        "ok"
                        if p in accepted
                        else "unavailable"
                    )
                    for p in PROVIDER_ORDER
                }

                runner, log = self.make_runner(
                    modes
                )

                with self.subTest(
                    accepted=combination
                ):
                    if accepted not in expected:
                        with self.assertRaises(
                            EntropyPolicyError
                        ):
                            self.acquire(runner)

                    else:
                        result = self.acquire(
                            runner
                        )

                        self.assertEqual(
                            result.plan.mode,
                            expected[accepted],
                        )

                        selected = (
                            {OS}
                            if (
                                result.plan.mode
                                is GenerationMode.OS_BACKUP
                            )
                            else accepted
                        )

                        selected_order = tuple(
                            p
                            for p in PROVIDER_ORDER
                            if p in selected
                        )

                        self.assertEqual(
                            tuple(result.contributions),
                            selected_order,
                        )

                        self.assertEqual(
                            result.plan.provider_ids,
                            tuple(result.contributions),
                        )

                        self.assertEqual(
                            result.plan.failed_provider_ids,
                            tuple(
                                p
                                for p in PROVIDER_ORDER
                                if p not in accepted
                            ),
                        )

                        self.assertEqual(
                            result.plan.omitted_provider_ids,
                            tuple(
                                p
                                for p in PROVIDER_ORDER
                                if p not in selected
                            ),
                        )

                        self.assertEqual(
                            result.plan.policy_version,
                            POLICY_VERSION,
                        )

                        for p in selected:
                            self.assertEqual(
                                result.contributions[p],
                                PAYLOADS[p],
                            )

                        statuses = {
                            o.provider_id: o.status
                            for o in result.outcomes
                        }

                        for p in PROVIDER_ORDER:
                            expected_status = (
                                ProviderStatus.OK
                                if p in accepted
                                else ProviderStatus.UNAVAILABLE
                            )

                            self.assertEqual(
                                statuses[p],
                                expected_status,
                            )

                    self.assertEqual(
                        self.read_calls(log),
                        list(PROVIDER_ORDER),
                    )

                    checked += 1

        self.assertEqual(checked, 16)

    def test_each_individual_generation_failure_is_tolerated(self):
        for failed in PROVIDER_ORDER:
            with self.subTest(failed=failed):
                runner, log = self.make_runner(
                    {
                        failed: "generation_failed",
                    }
                )

                result = self.acquire(runner)

                self.assertEqual(
                    result.plan.mode,
                    GenerationMode.REDUNDANT,
                )

                self.assertEqual(
                    set(result.contributions),
                    set(PROVIDER_ORDER) - {failed},
                )

                self.assertEqual(
                    self.read_calls(log),
                    list(PROVIDER_ORDER),
                )

    def test_backup_keeps_original_os_payload_without_second_call(self):
        runner, log = self.make_runner(
            {
                JAVA: "generation_failed",
                JS: "unavailable",
            }
        )

        result = self.acquire(runner)

        self.assertEqual(
            result.plan.mode,
            GenerationMode.OS_BACKUP,
        )

        self.assertEqual(
            dict(result.contributions),
            {
                OS: PAYLOADS[OS],
            },
        )

        self.assertEqual(
            self.read_calls(log).count(OS),
            1,
        )

        self.assertIn(
            SECRETS,
            result.plan.omitted_provider_ids,
        )

        self.assertNotIn(
            SECRETS,
            result.plan.failed_provider_ids,
        )

    def test_java_pair_without_python_providers(self):
        runner, log = self.make_runner(
            {
                OS: "generation_failed",
                SECRETS: "unavailable",
            }
        )

        result = self.acquire(runner)

        self.assertEqual(
            result.plan.mode,
            GenerationMode.REDUCED,
        )

        self.assertEqual(
            dict(result.contributions),
            {
                JAVA: PAYLOADS[JAVA],
                JS: PAYLOADS[JS],
            },
        )

        self.assertEqual(
            self.read_calls(log),
            list(PROVIDER_ORDER),
        )

    def test_failure_categories_remain_distinct(self):
        runner, _ = self.make_runner(
            {
                JAVA: "generation_failed",
                JS: "unavailable",
            }
        )

        result = self.acquire(runner)

        statuses = {
            o.provider_id: o.status
            for o in result.outcomes
        }

        self.assertEqual(
            statuses[JAVA],
            ProviderStatus.GENERATION_FAILED,
        )

        self.assertEqual(
            statuses[JS],
            ProviderStatus.UNAVAILABLE,
        )

    def test_java_timeout_continues_with_other_three(self):
        runner, _ = self.make_runner(
            {
                JAVA: "timeout",
            }
        )

        result = self.acquire(
            runner,
            timeout=0.5,
        )

        self.assertEqual(
            result.plan.mode,
            GenerationMode.REDUNDANT,
        )

        statuses = {
            o.provider_id: o.status
            for o in result.outcomes
        }

        self.assertEqual(
            statuses[JAVA],
            ProviderStatus.TIMEOUT,
        )

        self.assertNotIn(
            JAVA,
            result.contributions,
        )

    def test_os_timeout_continues_with_other_three(self):
        runner, _ = self.make_runner(
            {
                OS: "timeout",
            }
        )

        result = self.acquire(
            runner,
            timeout=0.5,
        )

        self.assertEqual(
            result.plan.mode,
            GenerationMode.REDUNDANT,
        )

        self.assertNotIn(
            OS,
            result.contributions,
        )

    def test_two_python_timeouts_keep_java_pair(self):
        runner, log = self.make_runner(
            {
                OS: "timeout",
                SECRETS: "timeout",
            }
        )

        result = self.acquire(
            runner,
            timeout=0.5,
        )

        self.assertEqual(
            result.plan.mode,
            GenerationMode.REDUCED,
        )

        self.assertEqual(
            set(result.contributions),
            {JAVA, JS},
        )

        self.assertEqual(
            self.read_calls(log),
            list(PROVIDER_ORDER),
        )

    def test_protocol_errors_are_critical_in_every_position(self):
        modes = (
            "short",
            "long",
            "stderr",
            "unknown_exit",
            "failed_with_output",
        )

        for position, provider in enumerate(
            PROVIDER_ORDER
        ):
            for mode in modes:
                with self.subTest(
                    provider=provider,
                    mode=mode,
                ):
                    runner, log = self.make_runner(
                        {
                            provider: mode,
                        }
                    )

                    with self.assertRaises(
                        CoordinatorCriticalError
                    ) as caught:
                        self.acquire(runner)

                    self.assertNotIn(
                        "SECRET_SENTINEL",
                        str(caught.exception),
                    )

                    self.assertEqual(
                        self.read_calls(log),
                        list(
                            PROVIDER_ORDER[
                                :position + 1
                            ]
                        ),
                    )

    def test_critical_error_does_not_fallback_to_available_java_pair(self):
        runner, log = self.make_runner(
            {
                OS: "unavailable",
                SECRETS: "stderr",
            }
        )

        with self.assertRaises(
            CoordinatorCriticalError
        ):
            self.acquire(runner)

        self.assertEqual(
            self.read_calls(log),
            list(PROVIDER_ORDER),
        )

    def test_all_disabled_stops_without_launching_helpers(self):
        runner, log = self.make_runner(
            {
                p: None
                for p in PROVIDER_ORDER
            }
        )

        with self.assertRaises(
            EntropyPolicyError
        ):
            self.acquire(runner)

        self.assertEqual(
            self.read_calls(log),
            [],
        )

    def test_disabled_python_providers_keep_java_pair(self):
        runner, log = self.make_runner(
            {
                OS: None,
                SECRETS: None,
            }
        )

        result = self.acquire(runner)

        self.assertEqual(
            result.plan.mode,
            GenerationMode.REDUCED,
        )

        self.assertEqual(
            self.read_calls(log),
            [JAVA, JS],
        )

    def test_result_repr_excludes_payloads(self):
        runner, _ = self.make_runner()

        result = self.acquire(runner)

        for payload in PAYLOADS.values():
            self.assertNotIn(
                repr(payload),
                repr(result),
            )

    def test_keyboard_interrupt_does_not_continue_to_other_providers(self):
        runner, _ = self.make_runner()

        with patch.object(
            runner,
            "acquire",
            wraps=runner.acquire,
        ) as calls:
            with patch(
                "entropy_process_runner.selectors.DefaultSelector",
                side_effect=KeyboardInterrupt,
            ):
                with self.assertRaises(
                    KeyboardInterrupt
                ):
                    self.acquire(runner)

        self.assertEqual(
            calls.call_count,
            1,
        )

        self.assertEqual(
            calls.call_args.args[0],
            OS,
        )


if __name__ == "__main__":
    unittest.main()
