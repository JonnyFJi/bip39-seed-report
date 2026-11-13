import itertools
import unittest

from entropy_policy import (
    CONTRIBUTION_BYTES,
    POLICY_VERSION,
    PROVIDER_ORDER,
    EntropyPolicyError,
    GenerationMode,
    ProviderOutcome,
    ProviderStatus,
    select_generation_plan,
)


OS, JAVA, JS, SECRETS = PROVIDER_ORDER


class EntropyPolicyTests(unittest.TestCase):
    def make_outcomes(
        self,
        accepted,
        failed_status=ProviderStatus.GENERATION_FAILED,
    ):
        accepted = frozenset(accepted)

        return [
            ProviderOutcome(
                p,
                (
                    ProviderStatus.OK
                    if p in accepted
                    else failed_status
                ),
            )
            for p in PROVIDER_ORDER
        ]

    def test_all_16_combinations(self):
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

                with self.subTest(accepted=combination):
                    outcomes = self.make_outcomes(accepted)

                    if accepted not in expected:
                        with self.assertRaises(EntropyPolicyError):
                            select_generation_plan(outcomes)

                    else:
                        plan = select_generation_plan(outcomes)

                        self.assertEqual(
                            plan.mode,
                            expected[accepted],
                        )

                        selected = (
                            {OS}
                            if plan.mode is GenerationMode.OS_BACKUP
                            else accepted
                        )

                        self.assertEqual(
                            plan.provider_ids,
                            tuple(
                                p
                                for p in PROVIDER_ORDER
                                if p in selected
                            ),
                        )

                        self.assertEqual(
                            plan.omitted_provider_ids,
                            tuple(
                                p
                                for p in PROVIDER_ORDER
                                if p not in selected
                            ),
                        )

                        self.assertEqual(
                            plan.failed_provider_ids,
                            tuple(
                                p
                                for p in PROVIDER_ORDER
                                if p not in accepted
                            ),
                        )

                        self.assertEqual(
                            plan.policy_version,
                            POLICY_VERSION,
                        )

                    checked += 1

        self.assertEqual(checked, 16)

    def test_every_individual_failure_is_tolerated(self):
        for failed in PROVIDER_ORDER:
            with self.subTest(failed=failed):
                accepted = set(PROVIDER_ORDER) - {failed}

                plan = select_generation_plan(
                    self.make_outcomes(accepted)
                )

                self.assertEqual(
                    plan.mode,
                    GenerationMode.REDUNDANT,
                )

                self.assertEqual(
                    set(plan.provider_ids),
                    accepted,
                )

    def test_os_backup_does_not_use_other_accepted_provider(self):
        plan = select_generation_plan(
            self.make_outcomes({OS, JAVA})
        )

        self.assertEqual(plan.provider_ids, (OS,))
        self.assertIn(JAVA, plan.omitted_provider_ids)
        self.assertNotIn(JAVA, plan.failed_provider_ids)

    def test_result_order_does_not_change_plan(self):
        outcomes = self.make_outcomes(PROVIDER_ORDER)
        expected = select_generation_plan(outcomes)

        for permutation in itertools.permutations(outcomes):
            self.assertEqual(
                select_generation_plan(permutation),
                expected,
            )

    def test_failure_statuses_are_not_accepted(self):
        statuses = (
            ProviderStatus.UNAVAILABLE,
            ProviderStatus.TIMEOUT,
            ProviderStatus.GENERATION_FAILED,
        )

        for status in statuses:
            with self.subTest(status=status):
                plan = select_generation_plan(
                    self.make_outcomes({OS}, status)
                )

                self.assertEqual(
                    plan.mode,
                    GenerationMode.OS_BACKUP,
                )

                self.assertEqual(
                    plan.provider_ids,
                    (OS,),
                )

    def test_missing_result_is_rejected(self):
        outcomes = self.make_outcomes(PROVIDER_ORDER)

        with self.assertRaises(EntropyPolicyError):
            select_generation_plan(outcomes[:-1])

    def test_duplicate_result_is_rejected(self):
        outcomes = self.make_outcomes(PROVIDER_ORDER)

        with self.assertRaises(EntropyPolicyError):
            select_generation_plan(
                outcomes + [outcomes[0]]
            )

    def test_unknown_provider_is_rejected(self):
        with self.assertRaises(ValueError):
            ProviderOutcome(
                "unknown",
                ProviderStatus.OK,
            )

    def test_non_text_provider_is_rejected(self):
        with self.assertRaises(TypeError):
            ProviderOutcome(
                None,
                ProviderStatus.OK,
            )

    def test_invalid_status_is_rejected(self):
        with self.assertRaises(TypeError):
            ProviderOutcome(
                OS,
                "ok",
            )

    def test_invalid_outcome_is_rejected(self):
        with self.assertRaises(TypeError):
            select_generation_plan([None])

    def test_critical_error_stops_even_if_all_providers_succeed(self):
        with self.assertRaises(EntropyPolicyError):
            select_generation_plan(
                self.make_outcomes(PROVIDER_ORDER),
                critical_error=True,
            )

    def test_critical_error_argument_must_be_boolean(self):
        with self.assertRaises(TypeError):
            select_generation_plan(
                self.make_outcomes(PROVIDER_ORDER),
                critical_error="false",
            )

    def test_contribution_size(self):
        self.assertEqual(CONTRIBUTION_BYTES, 32)


if __name__ == "__main__":
    unittest.main()
