import hashlib
import itertools
import struct
import unittest

from dataclasses import (
    FrozenInstanceError,
    replace,
)

from types import MappingProxyType
from unittest.mock import patch

import entropy_combiner as combiner

from entropy_coordinator import AcquisitionResult

from entropy_policy import (
    PROVIDER_ORDER,
    GenerationMode,
    ProviderOutcome,
    ProviderStatus,
    select_generation_plan,
)


OS, JAVA, JS, SECRETS = PROVIDER_ORDER

PAYLOADS = {
    p: bytes([i + 1]) * 32
    for i, p in enumerate(PROVIDER_ORDER)
}

BITS = (
    128,
    160,
    192,
    224,
    256,
)

ALL_FOUR_VECTORS = {
    128: "f98ad0df691f71eba3150eb2b1785223",
    160: "a215185b046f2048e2360e369de7aed4ec8e4a71",
    192: "b35de49f7b2a348377cb777edbe817c317d0d3b04486e77a",
    224: "1bd7635be89ae34379af5e8dd63e6f82932bf345d066681df5a00806",
    256: "85cd38b30033bc4c6ef3fbaaf2395b9041eae0a84287f41de9bef7bad244017b",
}


def outcomes_for(
    accepted,
    failure=ProviderStatus.UNAVAILABLE,
):
    return tuple(
        ProviderOutcome(
            p,
            (
                ProviderStatus.OK
                if p in accepted
                else failure
            ),
        )
        for p in PROVIDER_ORDER
    )


def make_acquisition(
    accepted=PROVIDER_ORDER,
    payloads=None,
):
    outcomes = outcomes_for(
        frozenset(accepted)
    )

    plan = select_generation_plan(
        outcomes
    )

    values = (
        PAYLOADS
        if payloads is None
        else payloads
    )

    return AcquisitionResult(
        plan,
        outcomes,
        MappingProxyType(
            {
                p: values[p]
                for p in plan.provider_ids
            }
        ),
    )


def reference_output(acquisition, bits):
    plan = acquisition.plan

    if plan.mode is GenerationMode.OS_BACKUP:
        return acquisition.contributions[
            OS
        ][:bits // 8]

    fields = [
        b"sha512-framed-v1",
        b"redundant-with-os-backup-and-java-pair-v1",
        b"bip39-initial-entropy",
        plan.mode.value.encode("ascii"),
        struct.pack(">H", bits),
        struct.pack(
            ">B",
            len(plan.provider_ids),
        ),
    ]

    for provider_id in plan.provider_ids:
        fields.extend(
            [
                provider_id.encode("ascii"),
                acquisition.contributions[
                    provider_id
                ],
            ]
        )

    encoded = (
        b"BSR-ENTROPY\x00"
        + b"".join(
            struct.pack(
                ">I",
                len(value),
            ) + value
            for value in fields
        )
    )

    return hashlib.sha512(
        encoded
    ).digest()[:bits // 8]


class EntropyCombinerTests(unittest.TestCase):
    def finalize(
        self,
        acquisition=None,
        bits=256,
    ):
        if acquisition is None:
            acquisition = make_acquisition()

        return combiner.finalize_entropy(
            acquisition,
            entropy_bits=bits,
        )

    def test_known_vectors_all_four_and_all_lengths(self):
        for bits, expected in (
            ALL_FOUR_VECTORS.items()
        ):
            with self.subTest(bits=bits):
                self.assertEqual(
                    self.finalize(
                        bits=bits
                    ).entropy.hex(),
                    expected,
                )

    def test_known_vectors_reduced_and_without_os(self):
        reduced = self.finalize(
            make_acquisition(
                {JAVA, JS}
            )
        )

        self.assertEqual(
            reduced.entropy.hex(),
            "eaa6bd7d16fd4da2214c8f92877ca5c24f53cc7695fba728555918023b839aec",
        )

        three = self.finalize(
            make_acquisition(
                {JAVA, JS, SECRETS}
            ),
            128,
        )

        self.assertEqual(
            three.entropy.hex(),
            "787fdb86fe1d06e36a75682f550407df",
        )

    def test_all_16_combinations_and_five_lengths(self):
        full = make_acquisition()

        for count in range(5):
            for values in itertools.combinations(
                PROVIDER_ORDER,
                count,
            ):
                accepted = frozenset(values)

                allowed = (
                    count >= 3
                    or OS in accepted
                    or {JAVA, JS} <= accepted
                )

                with self.subTest(
                    accepted=values
                ):
                    if not allowed:
                        forged = replace(
                            full,
                            outcomes=outcomes_for(
                                accepted
                            ),
                        )

                        with self.assertRaises(
                            combiner.EntropyCombinerError
                        ):
                            self.finalize(forged)

                        continue

                    acquisition = make_acquisition(
                        accepted
                    )

                    for bits in BITS:
                        result = self.finalize(
                            acquisition,
                            bits,
                        )

                        self.assertEqual(
                            len(result.entropy),
                            bits // 8,
                        )

                        self.assertEqual(
                            result.entropy,
                            reference_output(
                                acquisition,
                                bits,
                            ),
                        )

                        self.assertEqual(
                            result.provider_ids,
                            acquisition.plan.provider_ids,
                        )

                        self.assertEqual(
                            result.mode,
                            acquisition.plan.mode,
                        )

    def test_contribution_insertion_order_does_not_change_result(self):
        acquisition = make_acquisition()

        reversed_values = dict(
            reversed(
                tuple(
                    acquisition.contributions.items()
                )
            )
        )

        self.assertEqual(
            self.finalize(
                replace(
                    acquisition,
                    contributions=reversed_values,
                )
            ),
            self.finalize(acquisition),
        )

    def test_outcome_order_does_not_change_result(self):
        acquisition = make_acquisition()
        expected = self.finalize(acquisition)

        for outcomes in itertools.permutations(
            acquisition.outcomes
        ):
            self.assertEqual(
                self.finalize(
                    replace(
                        acquisition,
                        outcomes=outcomes,
                    )
                ),
                expected,
            )

    def test_each_selected_contribution_participates(self):
        baseline = self.finalize().entropy

        for provider_id in PROVIDER_ORDER:
            values = dict(PAYLOADS)

            original = values[provider_id]

            values[provider_id] = (
                bytes([original[0] ^ 1])
                + original[1:]
            )

            with self.subTest(
                provider=provider_id
            ):
                self.assertNotEqual(
                    self.finalize(
                        make_acquisition(
                            payloads=values
                        )
                    ).entropy,
                    baseline,
                )

    def test_backup_is_exact_prefix_with_leading_zeros(self):
        values = dict(PAYLOADS)

        values[OS] = (
            b"\0" * 16
            + bytes(range(16))
        )

        acquisition = make_acquisition(
            {OS, SECRETS},
            values,
        )

        for bits in BITS:
            result = self.finalize(
                acquisition,
                bits,
            )

            self.assertEqual(
                result.entropy,
                values[OS][:bits // 8],
            )

            self.assertEqual(
                result.method,
                "python-os-prefix",
            )

    def test_backup_does_not_call_hash_or_generators(self):
        acquisition = make_acquisition(
            {OS}
        )

        with patch.object(
            combiner.hashlib,
            "sha512",
            side_effect=AssertionError(
                "not allowed"
            ),
        ):
            self.assertEqual(
                self.finalize(
                    acquisition,
                    128,
                ).entropy,
                PAYLOADS[OS][:16],
            )

    def test_redundant_uses_one_sha512_instance(self):
        original = hashlib.sha512

        with patch.object(
            combiner.hashlib,
            "sha512",
            wraps=original,
        ) as constructor:
            result = self.finalize()

        constructor.assert_called_once_with()

        self.assertEqual(
            result.method,
            "sha512-framed",
        )

    def test_hash_failure_never_falls_back(self):
        with patch.object(
            combiner.hashlib,
            "sha512",
            side_effect=RuntimeError(
                "SECRET_SENTINEL"
            ),
        ):
            with self.assertRaises(
                combiner.EntropyCombinerError
            ) as caught:
                self.finalize()

        self.assertNotIn(
            "SECRET_SENTINEL",
            str(caught.exception),
        )

    def test_invalid_output_lengths(self):
        for bits in (
            True,
            None,
            "128",
            128.0,
            0,
            64,
            512,
        ):
            with self.subTest(bits=bits):
                with self.assertRaises(
                    ValueError
                ):
                    self.finalize(bits=bits)

    def test_wrong_acquisition_type(self):
        for value in (
            None,
            {},
            object(),
        ):
            with self.assertRaises(
                combiner.EntropyCombinerError
            ):
                combiner.finalize_entropy(
                    value,
                    entropy_bits=128,
                )

    def test_forged_plan_is_rejected(self):
        acquisition = make_acquisition()

        changes = (
            {
                "policy_version": "other",
            },
            {
                "provider_ids": (OS,),
            },
            {
                "omitted_provider_ids": (JAVA,),
            },
            {
                "failed_provider_ids": (JS,),
            },
            {
                "mode": GenerationMode.OS_BACKUP,
            },
            {
                "mode": "redundante",
            },
        )

        for change in changes:
            with self.subTest(change=change):
                forged = replace(
                    acquisition,
                    plan=replace(
                        acquisition.plan,
                        **change,
                    ),
                )

                with self.assertRaises(
                    combiner.EntropyCombinerError
                ):
                    self.finalize(forged)

    def test_duplicate_outcomes_are_rejected(self):
        acquisition = make_acquisition()

        forged = replace(
            acquisition,
            outcomes=(
                acquisition.outcomes
                + (acquisition.outcomes[0],)
            ),
        )

        with self.assertRaises(
            combiner.EntropyCombinerError
        ):
            self.finalize(forged)

    def test_missing_outcomes_are_rejected(self):
        acquisition = make_acquisition()

        with self.assertRaises(
            combiner.EntropyCombinerError
        ):
            self.finalize(
                replace(
                    acquisition,
                    outcomes=acquisition.outcomes[:-1],
                )
            )

    def test_wrong_outcome_container_or_element(self):
        acquisition = make_acquisition()

        for outcomes in (
            list(acquisition.outcomes),
            (None,),
        ):
            with self.assertRaises(
                combiner.EntropyCombinerError
            ):
                self.finalize(
                    replace(
                        acquisition,
                        outcomes=outcomes,
                    )
                )

    def test_invalid_contribution_lengths(self):
        acquisition = make_acquisition()

        for data in (
            b"",
            b"A" * 31,
            b"A" * 33,
        ):
            values = dict(
                acquisition.contributions
            )

            values[OS] = data

            with self.assertRaises(
                combiner.EntropyCombinerError
            ):
                self.finalize(
                    replace(
                        acquisition,
                        contributions=values,
                    )
                )

    def test_invalid_contribution_types(self):
        acquisition = make_acquisition()

        for data in (
            bytearray(32),
            "A" * 32,
            None,
        ):
            values = dict(
                acquisition.contributions
            )

            values[OS] = data

            with self.assertRaises(
                combiner.EntropyCombinerError
            ):
                self.finalize(
                    replace(
                        acquisition,
                        contributions=values,
                    )
                )

    def test_missing_or_extra_contributions(self):
        acquisition = make_acquisition(
            {OS, SECRETS}
        )

        cases = (
            {},
            {
                OS: PAYLOADS[OS],
                SECRETS: PAYLOADS[SECRETS],
            },
        )

        for values in cases:
            with self.assertRaises(
                combiner.EntropyCombinerError
            ):
                self.finalize(
                    replace(
                        acquisition,
                        contributions=values,
                    )
                )

    def test_constant_identical_inputs_are_not_filtered(self):
        acquisition = make_acquisition(
            payloads={
                p: b"\0" * 32
                for p in PROVIDER_ORDER
            }
        )

        self.assertEqual(
            self.finalize(acquisition).entropy,
            reference_output(
                acquisition,
                256,
            ),
        )

    def test_result_hides_entropy_in_repr_and_is_frozen(self):
        result = self.finalize()

        self.assertNotIn(
            repr(result.entropy),
            repr(result),
        )

        with self.assertRaises(
            FrozenInstanceError
        ):
            result.entropy = b"A" * 32

    def test_inputs_are_not_modified(self):
        acquisition = make_acquisition()

        before = dict(
            acquisition.contributions
        )

        self.finalize(acquisition)

        self.assertEqual(
            dict(acquisition.contributions),
            before,
        )

    def test_failure_reason_does_not_change_selected_entropy(self):
        acquisition = make_acquisition(
            {OS, JAVA, SECRETS}
        )

        outcomes = outcomes_for(
            {OS, JAVA, SECRETS},
            ProviderStatus.TIMEOUT,
        )

        changed = replace(
            acquisition,
            outcomes=outcomes,
        )

        self.assertEqual(
            self.finalize(acquisition),
            self.finalize(changed),
        )

    def test_version_and_purpose_are_bound_to_hash(self):
        expected = self.finalize().entropy

        with patch.object(
            combiner,
            "PURPOSE",
            "test-other-purpose",
        ):
            self.assertNotEqual(
                self.finalize().entropy,
                expected,
            )

        with patch.object(
            combiner,
            "COMBINER_VERSION",
            "test-other-version",
        ):
            self.assertNotEqual(
                self.finalize().entropy,
                expected,
            )

    def test_inconsistent_hash_digest_is_rejected(self):
        class BrokenHasher:
            def update(self, value):
                pass

            def digest(self):
                return b"A" * 32

        with patch.object(
            combiner.hashlib,
            "sha512",
            return_value=BrokenHasher(),
        ):
            with self.assertRaises(
                combiner.EntropyCombinerError
            ):
                self.finalize()


if __name__ == "__main__":
    unittest.main()
