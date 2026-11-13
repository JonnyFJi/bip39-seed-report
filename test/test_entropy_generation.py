import itertools
import unittest

from dataclasses import (
    FrozenInstanceError,
    fields,
)

from unittest.mock import patch

import entropy_combiner as combiner
import entropy_generation as generation

from entropy_policy import (
    PROVIDER_ORDER,
    EntropyPolicyError,
    GenerationMode,
    ProviderStatus,
)

from entropy_coordinator import (
    CoordinatorCriticalError,
    ProviderProtocolError,
    ProviderUnavailableError,
)


OS, JAVA, JS, SECRETS = PROVIDER_ORDER

PAYLOADS = {
    p: bytes([i + 1]) * 32
    for i, p in enumerate(PROVIDER_ORDER)
}

WORD_BITS = {
    12: 128,
    15: 160,
    18: 192,
    21: 224,
    24: 256,
}


class ScenarioRunner:
    def __init__(self, scenarios):
        self.scenarios = list(scenarios)
        self.calls = []

    def acquire(
        self,
        provider_id,
        nbytes,
        *,
        timeout_seconds,
    ):
        index = (
            len(self.calls)
            // len(PROVIDER_ORDER)
        )

        if index >= len(self.scenarios):
            raise AssertionError(
                "Adquisicion adicional "
                "no autorizada en la prueba."
            )

        self.calls.append(
            (
                provider_id,
                nbytes,
                timeout_seconds,
            )
        )

        action = self.scenarios[index].get(
            provider_id,
            PAYLOADS[provider_id],
        )

        if isinstance(action, BaseException):
            raise action

        return action


class EntropyGenerationTests(unittest.TestCase):
    def generate(
        self,
        runner,
        words=12,
    ):
        return generation.generate_entropy_result(
            words,
            runner=runner,
            timeout_seconds=2.0,
        )

    def test_five_word_counts(self):
        for words, bits in WORD_BITS.items():
            with self.subTest(words=words):
                result = self.generate(
                    ScenarioRunner([{}]),
                    words,
                )

                self.assertEqual(
                    result.final.entropy_bits,
                    bits,
                )

                self.assertEqual(
                    len(result.final.entropy),
                    bits // 8,
                )

    def test_invalid_words_before_acquisition(self):
        invalid = (
            None,
            True,
            12.0,
            "12",
            0,
            11,
            13,
            25,
        )

        for words in invalid:
            with self.subTest(words=words):
                runner = ScenarioRunner([{}])

                with self.assertRaises(ValueError):
                    self.generate(
                        runner,
                        words,
                    )

                self.assertEqual(
                    runner.calls,
                    [],
                )

    def test_invalid_timeout_before_provider_calls(self):
        invalid = (
            0,
            -1,
            True,
            None,
            "2",
            float("nan"),
            float("inf"),
        )

        for timeout in invalid:
            runner = ScenarioRunner([{}])

            with self.subTest(timeout=timeout):
                with self.assertRaises(ValueError):
                    generation.generate_entropy_result(
                        12,
                        runner=runner,
                        timeout_seconds=timeout,
                    )

                self.assertEqual(
                    runner.calls,
                    [],
                )

    def test_one_acquisition_and_one_finalization(self):
        runner = ScenarioRunner([{}])
        original = generation.finalize_entropy

        with patch.object(
            generation,
            "finalize_entropy",
            wraps=original,
        ) as finalize:
            self.generate(runner)

        self.assertEqual(
            runner.calls,
            [
                (p, 32, 2.0)
                for p in PROVIDER_ORDER
            ],
        )

        self.assertEqual(
            finalize.call_count,
            1,
        )

    def test_new_acquisition_for_every_request(self):
        changed = {
            p: bytes([i + 9]) * 32
            for i, p in enumerate(PROVIDER_ORDER)
        }

        runner = ScenarioRunner(
            [
                {},
                changed,
            ]
        )

        first = self.generate(runner)
        second = self.generate(runner)

        self.assertEqual(
            len(runner.calls),
            8,
        )

        self.assertIsNot(
            first,
            second,
        )

        self.assertNotEqual(
            first.final.entropy,
            second.final.entropy,
        )

    def test_failed_new_request_never_returns_previous_result(self):
        failed = {
            p: ProviderUnavailableError()
            for p in PROVIDER_ORDER
        }

        runner = ScenarioRunner(
            [
                {},
                failed,
            ]
        )

        self.generate(runner)

        with self.assertRaises(
            EntropyPolicyError
        ):
            self.generate(runner)

        self.assertEqual(
            len(runner.calls),
            8,
        )

    def test_all_16_combinations_and_five_word_counts(self):
        for count in range(5):
            for combination in itertools.combinations(
                PROVIDER_ORDER,
                count,
            ):
                accepted = frozenset(
                    combination
                )

                scenario = {
                    p: (
                        PAYLOADS[p]
                        if p in accepted
                        else ProviderUnavailableError()
                    )
                    for p in PROVIDER_ORDER
                }

                expected = (
                    GenerationMode.REDUNDANT
                    if count >= 3
                    else GenerationMode.OS_BACKUP
                    if OS in accepted
                    else GenerationMode.REDUCED
                    if {JAVA, JS} <= accepted
                    else None
                )

                for words, bits in WORD_BITS.items():
                    with self.subTest(
                        accepted=combination,
                        words=words,
                    ):
                        runner = ScenarioRunner(
                            [scenario]
                        )

                        if expected is None:
                            with self.assertRaises(
                                EntropyPolicyError
                            ):
                                self.generate(
                                    runner,
                                    words,
                                )

                        else:
                            result = self.generate(
                                runner,
                                words,
                            )

                            self.assertEqual(
                                result.final.mode,
                                expected,
                            )

                            self.assertEqual(
                                len(result.final.entropy),
                                bits // 8,
                            )

                        self.assertEqual(
                            len(runner.calls),
                            4,
                        )

    def test_critical_acquisition_never_reaches_finalizer(self):
        runner = ScenarioRunner(
            [
                {
                    OS: ProviderProtocolError(),
                }
            ]
        )

        with patch.object(
            generation,
            "finalize_entropy",
        ) as finalize:
            with self.assertRaises(
                CoordinatorCriticalError
            ):
                self.generate(runner)

        finalize.assert_not_called()

        self.assertEqual(
            len(runner.calls),
            1,
        )

    def test_hash_failure_does_not_retry_or_fallback(self):
        runner = ScenarioRunner([{}])

        with patch.object(
            combiner.hashlib,
            "sha512",
            side_effect=RuntimeError("test"),
        ):
            with self.assertRaises(
                combiner.EntropyCombinerError
            ):
                self.generate(runner)

        self.assertEqual(
            len(runner.calls),
            4,
        )

    def test_backup_uses_acquired_os_prefix_without_hash(self):
        scenario = {
            JAVA: ProviderUnavailableError(),
            JS: ProviderUnavailableError(),
        }

        for words, bits in WORD_BITS.items():
            runner = ScenarioRunner(
                [scenario]
            )

            with patch.object(
                combiner.hashlib,
                "sha512",
                side_effect=AssertionError(
                    "forbidden"
                ),
            ):
                result = self.generate(
                    runner,
                    words,
                )

            self.assertEqual(
                result.final.entropy,
                PAYLOADS[OS][:bits // 8],
            )

            self.assertEqual(
                result.final.method,
                "python-os-prefix",
            )

            self.assertEqual(
                len(runner.calls),
                4,
            )

    def test_outcomes_include_accepted_but_omitted_provider(self):
        scenario = {
            JAVA: ProviderUnavailableError(),
            JS: ProviderUnavailableError(),
        }

        result = self.generate(
            ScenarioRunner([scenario])
        )

        statuses = {
            o.provider_id: o.status
            for o in result.outcomes
        }

        self.assertEqual(
            set(statuses),
            set(PROVIDER_ORDER),
        )

        self.assertIs(
            statuses[SECRETS],
            ProviderStatus.OK,
        )

        self.assertEqual(
            result.final.provider_ids,
            (OS,),
        )

    def test_result_repr_does_not_include_entropy(self):
        result = self.generate(
            ScenarioRunner([{}])
        )

        self.assertNotIn(
            repr(result.final.entropy),
            repr(result),
        )

    def test_result_is_frozen(self):
        result = self.generate(
            ScenarioRunner([{}])
        )

        with self.assertRaises(
            FrozenInstanceError
        ):
            result.final = None

    def test_result_does_not_retain_raw_contributions(self):
        result = self.generate(
            ScenarioRunner([{}])
        )

        self.assertEqual(
            {
                f.name
                for f in fields(result)
            },
            {
                "final",
                "outcomes",
            },
        )

        self.assertFalse(
            hasattr(
                result,
                "contributions",
            )
        )

    def test_keyboard_interrupt_is_not_a_retry(self):
        runner = ScenarioRunner(
            [
                {
                    OS: KeyboardInterrupt(),
                }
            ]
        )

        with patch.object(
            generation,
            "finalize_entropy",
        ) as finalize:
            with self.assertRaises(
                KeyboardInterrupt
            ):
                self.generate(runner)

        finalize.assert_not_called()

        self.assertEqual(
            len(runner.calls),
            1,
        )


if __name__ == "__main__":
    unittest.main()
