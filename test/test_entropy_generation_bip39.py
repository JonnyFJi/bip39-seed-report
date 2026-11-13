import hmac
import sys
import unittest

import bip39_seed_report as report

from entropy_all_config import (
    build_all_provider_commands,
)

from entropy_generation import (
    generate_entropy_result,
)

from entropy_policy import (
    PROVIDER_ORDER,
    EntropyPolicyError,
    GenerationMode,
)

from entropy_process_runner import (
    ProcessProviderRunner,
)


OS, JAVA, JS, SECRETS = PROVIDER_ORDER

WORD_BITS = {
    12: 128,
    15: 160,
    18: 192,
    21: 224,
    24: 256,
}


class CountingRunner:
    def __init__(self, delegate):
        self.delegate = delegate
        self.calls = []

    def acquire(
        self,
        provider_id,
        nbytes,
        *,
        timeout_seconds,
    ):
        self.calls.append(
            (
                provider_id,
                nbytes,
            )
        )

        return self.delegate.acquire(
            provider_id,
            nbytes,
            timeout_seconds=timeout_seconds,
        )


class DeterministicRunner:
    def acquire(
        self,
        provider_id,
        nbytes,
        *,
        timeout_seconds,
    ):
        return (
            bytes(
                [
                    PROVIDER_ORDER.index(
                        provider_id
                    ) + 1
                ]
            )
            * nbytes
        )


@unittest.skipUnless(
    sys.platform.startswith("linux"),
    "Recorrido real Linux",
)
class EntropyGenerationBip39Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not report.verify_against_bip39_official(
            verbose=False
        ):
            raise RuntimeError(
                "No se verifico la wordlist BIP39 local."
            )

    def verify_roundtrip(
        self,
        result,
        words,
    ):
        entropy = result.final.entropy

        self.assertEqual(
            len(entropy),
            WORD_BITS[words] // 8,
        )

        phrase = report.entropy_to_mnemonic(
            entropy
        )

        self.assertEqual(
            len(phrase.split()),
            words,
        )

        normalized = (
            report.validate_mnemonic_text(
                phrase
            )
        )

        self.assertTrue(
            hmac.compare_digest(
                normalized.encode("utf-8"),
                phrase.encode("utf-8"),
            )
        )

        recovered = (
            report.mnemonic_to_entropy(
                phrase
            )
        )

        self.assertTrue(
            recovered["checksum_valid"]
        )

        self.assertTrue(
            hmac.compare_digest(
                recovered["entropy"],
                entropy,
            )
        )

    def verify_real_mode(
        self,
        commands,
        expected_mode,
        expected_ids,
    ):
        runner = CountingRunner(
            ProcessProviderRunner(commands)
        )

        for operation, words in enumerate(
            WORD_BITS,
            start=1,
        ):
            with self.subTest(words=words):
                result = generate_entropy_result(
                    words,
                    runner=runner,
                    timeout_seconds=10.0,
                )

                self.assertEqual(
                    result.final.mode,
                    expected_mode,
                )

                self.assertEqual(
                    result.final.provider_ids,
                    expected_ids,
                )

                self.verify_roundtrip(
                    result,
                    words,
                )

                self.assertEqual(
                    len(runner.calls),
                    operation * 4,
                )

                self.assertEqual(
                    runner.calls[-4:],
                    [
                        (p, 32)
                        for p in PROVIDER_ORDER
                    ],
                )

    def test_deterministic_full_flow_and_bip39(self):
        runner = DeterministicRunner()

        for words in WORD_BITS:
            with self.subTest(words=words):
                result = generate_entropy_result(
                    words,
                    runner=runner,
                    timeout_seconds=2.0,
                )

                self.verify_roundtrip(
                    result,
                    words,
                )

    def test_four_real_providers_all_five_lengths(self):
        self.verify_real_mode(
            build_all_provider_commands(),
            GenerationMode.REDUNDANT,
            PROVIDER_ORDER,
        )

    def test_real_java_javascript_pair_all_five_lengths(self):
        commands = build_all_provider_commands()

        commands[OS] = None
        commands[SECRETS] = None

        self.verify_real_mode(
            commands,
            GenerationMode.REDUCED,
            (JAVA, JS),
        )

    def test_only_os_backup_all_five_lengths(self):
        commands = build_all_provider_commands()

        for provider in (
            JAVA,
            JS,
            SECRETS,
        ):
            commands[provider] = None

        self.verify_real_mode(
            commands,
            GenerationMode.OS_BACKUP,
            (OS,),
        )

    def test_os_backup_omits_accepted_secrets_all_five_lengths(self):
        commands = build_all_provider_commands()

        commands[JAVA] = None
        commands[JS] = None

        self.verify_real_mode(
            commands,
            GenerationMode.OS_BACKUP,
            (OS,),
        )

    def test_all_disabled_does_not_produce_a_result(self):
        commands = {
            p: None
            for p in PROVIDER_ORDER
        }

        runner = CountingRunner(
            ProcessProviderRunner(commands)
        )

        with self.assertRaises(
            EntropyPolicyError
        ):
            generate_entropy_result(
                12,
                runner=runner,
                timeout_seconds=10.0,
            )

        self.assertEqual(
            runner.calls,
            [
                (p, 32)
                for p in PROVIDER_ORDER
            ],
        )


if __name__ == "__main__":
    unittest.main()
