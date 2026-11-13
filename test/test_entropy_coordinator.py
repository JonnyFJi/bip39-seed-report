import itertools
import unittest

from entropy_policy import (
    CONTRIBUTION_BYTES,
    PROVIDER_ORDER,
    EntropyPolicyError,
    GenerationMode,
    ProviderStatus,
)

from entropy_coordinator import (
    CoordinatorCriticalError,
    ProviderGenerationError,
    ProviderProtocolError,
    ProviderTimeoutError,
    ProviderUnavailableError,
    acquire_contributions,
)


OS, JAVA, JS, SECRETS = PROVIDER_ORDER

PAYLOADS = {
    p: bytes([i + 1]) * CONTRIBUTION_BYTES
    for i, p in enumerate(PROVIDER_ORDER)
}


class FakeRunner:
    def __init__(self, responses=None):
        self.responses = dict(
            PAYLOADS if responses is None else responses
        )
        self.calls = []

    def acquire(
        self,
        provider_id,
        nbytes,
        *,
        timeout_seconds,
    ):
        self.calls.append(
            (provider_id, nbytes, timeout_seconds)
        )

        response = self.responses[provider_id]

        if isinstance(response, BaseException):
            raise response

        return response


class EntropyCoordinatorTests(unittest.TestCase):
    def acquire(self, runner):
        return acquire_contributions(
            runner,
            timeout_seconds=2.0,
        )

    def test_all_providers_and_request_contract(self):
        runner = FakeRunner()
        result = self.acquire(runner)

        self.assertEqual(
            result.plan.mode,
            GenerationMode.REDUNDANT,
        )

        self.assertEqual(
            dict(result.contributions),
            PAYLOADS,
        )

        self.assertEqual(
            runner.calls,
            [
                (p, 32, 2.0)
                for p in PROVIDER_ORDER
            ],
        )

    def test_all_16_availability_combinations(self):
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

                runner = FakeRunner(
                    {
                        p: (
                            PAYLOADS[p]
                            if p in accepted
                            else ProviderUnavailableError()
                        )
                        for p in PROVIDER_ORDER
                    }
                )

                with self.subTest(accepted=combination):
                    if accepted not in expected:
                        with self.assertRaises(
                            EntropyPolicyError
                        ):
                            self.acquire(runner)

                    else:
                        result = self.acquire(runner)

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

                        self.assertEqual(
                            set(result.contributions),
                            selected,
                        )

                        self.assertEqual(
                            tuple(result.contributions),
                            result.plan.provider_ids,
                        )

                        for p in selected:
                            self.assertEqual(
                                result.contributions[p],
                                PAYLOADS[p],
                            )

                    self.assertEqual(
                        len(runner.calls),
                        4,
                    )

                    checked += 1

        self.assertEqual(checked, 16)

    def test_expected_failures_have_distinct_statuses(self):
        cases = (
            (
                ProviderUnavailableError,
                ProviderStatus.UNAVAILABLE,
            ),
            (
                ProviderTimeoutError,
                ProviderStatus.TIMEOUT,
            ),
            (
                ProviderGenerationError,
                ProviderStatus.GENERATION_FAILED,
            ),
        )

        for error, expected in cases:
            with self.subTest(error=error):
                responses = dict(PAYLOADS)
                responses[JAVA] = error("do not expose")

                result = self.acquire(
                    FakeRunner(responses)
                )

                statuses = {
                    o.provider_id: o.status
                    for o in result.outcomes
                }

                self.assertEqual(
                    statuses[JAVA],
                    expected,
                )

                self.assertEqual(
                    result.plan.mode,
                    GenerationMode.REDUNDANT,
                )

                self.assertNotIn(
                    JAVA,
                    result.contributions,
                )

    def test_os_backup_reuses_original_bytes_without_retry(self):
        responses = dict(PAYLOADS)
        responses[JAVA] = ProviderTimeoutError()
        responses[JS] = ProviderUnavailableError()

        runner = FakeRunner(responses)
        result = self.acquire(runner)

        self.assertEqual(
            result.plan.mode,
            GenerationMode.OS_BACKUP,
        )

        self.assertEqual(
            dict(result.contributions),
            {OS: PAYLOADS[OS]},
        )

        self.assertEqual(
            [
                p
                for p, _, _ in runner.calls
            ].count(OS),
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

    def test_java_pair_can_continue_without_python(self):
        responses = dict(PAYLOADS)
        responses[OS] = ProviderGenerationError()
        responses[SECRETS] = ProviderGenerationError()

        result = self.acquire(
            FakeRunner(responses)
        )

        self.assertEqual(
            result.plan.mode,
            GenerationMode.REDUCED,
        )

        self.assertEqual(
            set(result.contributions),
            {JAVA, JS},
        )

    def test_invalid_payload_is_critical(self):
        invalid_payloads = (
            b"",
            b"x" * 31,
            b"x" * 33,
            "x" * 32,
            bytearray(32),
            None,
        )

        for invalid in invalid_payloads:
            with self.subTest(
                kind=type(invalid),
                size=(
                    len(invalid)
                    if invalid is not None
                    else None
                ),
            ):
                responses = dict(PAYLOADS)
                responses[OS] = invalid

                runner = FakeRunner(responses)

                with self.assertRaises(
                    CoordinatorCriticalError
                ):
                    self.acquire(runner)

                self.assertEqual(
                    len(runner.calls),
                    1,
                )

    def test_protocol_error_is_critical_and_message_is_hidden(self):
        responses = dict(PAYLOADS)
        responses[OS] = ProviderProtocolError(
            "SECRET_SENTINEL"
        )

        runner = FakeRunner(responses)

        with self.assertRaises(
            CoordinatorCriticalError
        ) as caught:
            self.acquire(runner)

        self.assertNotIn(
            "SECRET_SENTINEL",
            str(caught.exception),
        )

        self.assertEqual(
            len(runner.calls),
            1,
        )

    def test_unexpected_error_is_critical_not_unavailable(self):
        responses = dict(PAYLOADS)
        responses[OS] = ValueError(
            "SECRET_SENTINEL"
        )

        runner = FakeRunner(responses)

        with self.assertRaises(
            CoordinatorCriticalError
        ) as caught:
            self.acquire(runner)

        self.assertNotIn(
            "SECRET_SENTINEL",
            str(caught.exception),
        )

        self.assertEqual(
            len(runner.calls),
            1,
        )

    def test_keyboard_interrupt_is_not_a_fallback(self):
        responses = dict(PAYLOADS)
        responses[OS] = KeyboardInterrupt()

        runner = FakeRunner(responses)

        with self.assertRaises(KeyboardInterrupt):
            self.acquire(runner)

        self.assertEqual(
            len(runner.calls),
            1,
        )

    def test_timeout_validation_precedes_execution(self):
        invalid_timeouts = (
            0,
            -1,
            True,
            "2",
            None,
            float("nan"),
            float("inf"),
        )

        for invalid in invalid_timeouts:
            with self.subTest(timeout=invalid):
                runner = FakeRunner()

                with self.assertRaises(ValueError):
                    acquire_contributions(
                        runner,
                        timeout_seconds=invalid,
                    )

                self.assertEqual(
                    runner.calls,
                    [],
                )

    def test_payload_is_not_in_result_repr(self):
        responses = dict(PAYLOADS)

        responses[OS] = b"SECRET_SENTINEL".ljust(
            32,
            b"!",
        )

        result = self.acquire(
            FakeRunner(responses)
        )

        self.assertNotIn(
            "SECRET_SENTINEL",
            repr(result),
        )

    def test_contributions_mapping_cannot_be_modified(self):
        result = self.acquire(FakeRunner())

        with self.assertRaises(TypeError):
            result.contributions[OS] = b"x" * 32

    def test_constant_payloads_are_not_filtered_by_appearance(self):
        result = self.acquire(
            FakeRunner(
                {
                    p: b"\0" * 32
                    for p in PROVIDER_ORDER
                }
            )
        )

        self.assertEqual(
            result.plan.mode,
            GenerationMode.REDUNDANT,
        )

        self.assertEqual(
            len(result.contributions),
            4,
        )


if __name__ == "__main__":
    unittest.main()
