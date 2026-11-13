import argparse
import contextlib
import io
import json
import sys
import types
import unittest

from unittest.mock import patch

import bip39_seed_report as report
import entropy_cli_support as support

from entropy_combiner import (
    COMBINER_VERSION,
    FinalEntropyResult,
)

from entropy_generation import (
    EntropyGenerationResult,
)

from entropy_policy import (
    PROVIDER_ORDER,
    GenerationMode,
    ProviderOutcome,
    ProviderStatus,
    select_generation_plan,
)


OS, JAVA, JS, SECRETS = PROVIDER_ORDER

PUBLIC_ENTROPY = bytes(16)


def fake_result(accepted=PROVIDER_ORDER):
    accepted = frozenset(accepted)

    outcomes = tuple(
        ProviderOutcome(
            p,
            (
                ProviderStatus.OK
                if p in accepted
                else ProviderStatus.UNAVAILABLE
            ),
        )
        for p in PROVIDER_ORDER
    )

    plan = select_generation_plan(outcomes)

    final = FinalEntropyResult(
        mode=plan.mode,
        provider_ids=plan.provider_ids,
        entropy_bits=128,
        method=(
            "python-os-prefix"
            if plan.mode is GenerationMode.OS_BACKUP
            else "sha512-framed"
        ),
        combiner_version=COMBINER_VERSION,
        entropy=PUBLIC_ENTROPY,
    )

    return EntropyGenerationResult(
        final=final,
        outcomes=outcomes,
    )


class EntropyCliIntegrationTests(unittest.TestCase):
    def args(self, **changes):
        values = dict(
            words=12,
            entropy_bin="",
            entropy_hex="",
            mnemonic="",
            mnemonic_incomplete="",
            network="testnet",
            passphrase="",
            audit_passphrase=False,
            entropy_mode="redundant",
            entropy_timeout=10.0,
        )

        values.update(changes)

        return argparse.Namespace(**values)

    def parser(self):
        created = []

        def capture(*args, **kwargs):
            parser = argparse.ArgumentParser(
                *args,
                **kwargs,
            )

            created.append(parser)
            return parser

        proxy = types.SimpleNamespace(
            ArgumentParser=capture,
            ArgumentTypeError=argparse.ArgumentTypeError,
        )

        with patch.object(
            report,
            "argparse",
            proxy,
        ):
            with patch.object(
                sys,
                "argv",
                [
                    "bip39_seed_report.py",
                    "--help",
                ],
            ):
                with contextlib.redirect_stdout(
                    io.StringIO()
                ):
                    with self.assertRaises(
                        SystemExit
                    ) as caught:
                        report.main()

        self.assertEqual(
            caught.exception.code,
            0,
        )

        self.assertEqual(
            len(created),
            1,
        )

        return created[0]

    def build(self, args):
        item = {
            "path_template": "test",
            "address_type": "test",
            "addresses": [
                {
                    "index": 0,
                    "path": "test",
                    "address": "test-address",
                    "private_key_wif": "test-private",
                    "public_key_hex": "test-public",
                }
            ],
        }

        with contextlib.ExitStack() as stack:
            for name in (
                "derive_addresses_bip44",
                "derive_addresses_bip49",
                "derive_addresses_bip84",
                "derive_addresses_bip86",
            ):
                stack.enter_context(
                    patch.object(
                        report,
                        name,
                        return_value=item,
                    )
                )

            return report.build_context(args)

    def test_legacy_generator_still_calls_os_directly(self):
        with patch.object(
            report.os,
            "urandom",
            return_value=PUBLIC_ENTROPY,
        ) as call:
            self.assertEqual(
                report.generate_entropy(12),
                PUBLIC_ENTROPY,
            )

        call.assert_called_once_with(16)

    def test_cli_default_and_explicit_current(self):
        parser = self.parser()

        default = parser.parse_args(
            ["-w", "12"]
        )

        self.assertEqual(
            default.entropy_mode,
            "redundant",
        )

        self.assertEqual(
            default.entropy_timeout,
            10.0,
        )

        explicit = parser.parse_args(
            [
                "-w",
                "12",
                "--entropy-mode",
                "current",
            ]
        )

        self.assertEqual(
            explicit.entropy_mode,
            "current",
        )

    def test_cli_rejects_invalid_timeouts(self):
        parser = self.parser()

        for value in (
            "0",
            "-1",
            "nan",
            "inf",
            "not-a-number",
        ):
            with self.subTest(value=value):
                with contextlib.redirect_stderr(
                    io.StringIO()
                ):
                    with self.assertRaises(
                        SystemExit
                    ) as caught:
                        parser.parse_args(
                            [
                                "--entropy-timeout",
                                value,
                            ]
                        )

                self.assertEqual(
                    caught.exception.code,
                    2,
                )

    def test_explicit_current_delegates_once_without_backends(self):
        args = self.args(
            entropy_mode="current"
        )

        with patch.object(
            report,
            "generate_entropy",
            return_value=PUBLIC_ENTROPY,
        ) as current:
            with patch.object(
                support,
                "_run_redundant",
            ) as redundant:
                report.resolve_input(args)

        current.assert_called_once_with(12)
        redundant.assert_not_called()

        info = args._entropy_generation_metadata

        self.assertEqual(
            info["actual_mode"],
            "actual_explicito",
        )

        self.assertEqual(
            info["provider_statuses"][JAVA],
            "not_attempted",
        )

    def test_redundant_never_calls_legacy(self):
        args = self.args()

        with patch.object(
            support,
            "_run_redundant",
            return_value=fake_result(),
        ) as redundant:
            with patch.object(
                report,
                "generate_entropy",
            ) as current:
                entropy, _, _, mode = (
                    report.resolve_input(args)
                )

        redundant.assert_called_once_with(
            12,
            10.0,
        )

        current.assert_not_called()

        self.assertEqual(
            entropy,
            PUBLIC_ENTROPY,
        )

        self.assertEqual(mode, "words")

        self.assertEqual(
            args._entropy_generation_metadata[
                "actual_mode"
            ],
            "redundante",
        )

    def test_reduced_mode_metadata_and_warning(self):
        args = self.args()

        with patch.object(
            support,
            "_run_redundant",
            return_value=fake_result(
                {JAVA, JS}
            ),
        ):
            report.resolve_input(args)

        info = args._entropy_generation_metadata

        self.assertEqual(
            info["actual_mode"],
            "redundante_reducido",
        )

        self.assertIn(
            "AVISO: continuidad",
            "\n".join(
                support.format_generation_metadata(
                    info
                )
            ),
        )

    def test_automatic_backup_does_not_call_legacy_again(self):
        args = self.args()

        with patch.object(
            support,
            "_run_redundant",
            return_value=fake_result(
                {OS, SECRETS}
            ),
        ):
            with patch.object(
                report,
                "generate_entropy",
            ) as current:
                report.resolve_input(args)

        current.assert_not_called()

        info = args._entropy_generation_metadata

        self.assertEqual(
            info["actual_mode"],
            "actual_respaldo",
        )

        self.assertIn(
            SECRETS,
            info["providers_omitted"],
        )

        self.assertNotIn(
            SECRETS,
            info["providers_failed"],
        )

        self.assertIn(
            "AVISO: cambio automatico",
            "\n".join(
                support.format_generation_metadata(
                    info
                )
            ),
        )

    def test_redundant_failure_does_not_call_current(self):
        args = self.args()

        with patch.object(
            support,
            "_run_redundant",
            side_effect=RuntimeError(
                "test failure"
            ),
        ):
            with patch.object(
                report,
                "generate_entropy",
            ) as current:
                with self.assertRaises(
                    RuntimeError
                ):
                    report.resolve_input(args)

        current.assert_not_called()

        self.assertIsNone(
            args._entropy_generation_metadata
        )

    def test_namespace_without_new_options_preserves_legacy(self):
        args = self.args()

        del args.entropy_mode
        del args.entropy_timeout

        with patch.object(
            report,
            "generate_entropy",
            return_value=PUBLIC_ENTROPY,
        ) as current:
            report.resolve_input(args)

        current.assert_called_once_with(12)

    def test_imported_hex_unchanged_and_stale_metadata_cleared(self):
        args = self.args(
            words=None,
            entropy_hex=PUBLIC_ENTROPY.hex(),
        )

        args._entropy_generation_metadata = {
            "old": True,
        }

        with patch.object(
            support,
            "generate_for_report",
        ) as generate:
            entropy, _, _, mode = (
                report.resolve_input(args)
            )

        generate.assert_not_called()

        self.assertEqual(
            entropy,
            PUBLIC_ENTROPY,
        )

        self.assertEqual(
            mode,
            "entropy_hex",
        )

        self.assertIsNone(
            args._entropy_generation_metadata
        )

    def test_imported_binary_unchanged(self):
        args = self.args(
            words=None,
            entropy_bin="0" * 128,
        )

        with patch.object(
            support,
            "generate_for_report",
        ) as generate:
            entropy, _, _, mode = (
                report.resolve_input(args)
            )

        generate.assert_not_called()

        self.assertEqual(
            entropy,
            PUBLIC_ENTROPY,
        )

        self.assertEqual(
            mode,
            "entropy_bin",
        )

    def test_imported_mnemonic_unchanged(self):
        phrase = report.entropy_to_mnemonic(
            PUBLIC_ENTROPY
        )

        args = self.args(
            words=None,
            mnemonic=phrase,
        )

        with patch.object(
            support,
            "generate_for_report",
        ) as generate:
            _, actual, _, mode = (
                report.resolve_input(args)
            )

        generate.assert_not_called()

        self.assertEqual(actual, phrase)
        self.assertEqual(mode, "mnemonic")

    def test_incomplete_mnemonic_branch_is_preserved(self):
        phrase = report.entropy_to_mnemonic(
            PUBLIC_ENTROPY
        )

        words = phrase.split()

        args = self.args(
            words=None,
            mnemonic_incomplete=" ".join(
                words[:-1]
            ),
        )

        with patch.object(
            report,
            "find_last_word",
            return_value=[words[-1]],
        ):
            with patch.object(
                support,
                "generate_for_report",
            ) as generate:
                with contextlib.redirect_stdout(
                    io.StringIO()
                ):
                    _, actual, _, mode = (
                        report.resolve_input(args)
                    )

        generate.assert_not_called()

        self.assertEqual(actual, phrase)

        self.assertEqual(
            mode,
            "mnemonic_incomplete",
        )

    def test_automatic_context_contains_generation_metadata(self):
        with patch.object(
            support,
            "_run_redundant",
            return_value=fake_result(),
        ):
            data = self.build(self.args())

        self.assertEqual(
            data["input_mode"],
            "words",
        )

        self.assertEqual(
            data["entropy_generation"][
                "actual_mode"
            ],
            "redundante",
        )

        self.assertEqual(
            len(data["derivations"]),
            4,
        )

    def test_imported_context_has_no_automatic_metadata(self):
        args = self.args(
            words=None,
            entropy_hex=PUBLIC_ENTROPY.hex(),
        )

        with patch.object(
            support,
            "generate_for_report",
        ) as generate:
            data = self.build(args)

        generate.assert_not_called()

        self.assertNotIn(
            "entropy_generation",
            data,
        )

    def test_terminal_text_and_json_include_correct_mode(self):
        with patch.object(
            support,
            "_run_redundant",
            return_value=fake_result(),
        ):
            data = self.build(self.args())

        compact = (
            report.format_terminal_summary(data)
        )

        full = report.format_report(
            data,
            terminal_mode=False,
            hide_sensitive=False,
        )

        self.assertIn(
            "Modo ejecutado: redundante",
            compact,
        )

        self.assertIn(
            "Modo ejecutado: redundante",
            full,
        )

        self.assertNotIn(
            data["mnemonic"],
            compact,
        )

        self.assertNotIn(
            data["entropy_hex"],
            compact,
        )

        restored = json.loads(
            json.dumps(data)
        )

        self.assertEqual(
            restored["entropy_generation"],
            data["entropy_generation"],
        )

    def test_metadata_has_only_approved_fields(self):
        with patch.object(
            support,
            "_run_redundant",
            return_value=fake_result(),
        ):
            _, info = support.generate_for_report(
                12,
                mode="redundant",
                timeout_seconds=10.0,
                current_generator=(
                    lambda words: PUBLIC_ENTROPY
                ),
            )

        self.assertEqual(
            set(info),
            {
                "version",
                "requested_mode",
                "actual_mode",
                "method",
                "policy_version",
                "combiner_version",
                "entropy_bits",
                "providers_used",
                "providers_omitted",
                "providers_failed",
                "provider_statuses",
            },
        )

        self.assertEqual(info["version"], 1)
        self.assertEqual(info["entropy_bits"], 128)

        self.assertEqual(
            info["providers_used"],
            list(PROVIDER_ORDER),
        )

        self.assertEqual(info["providers_omitted"], [])
        self.assertEqual(info["providers_failed"], [])

        self.assertEqual(
            info["provider_statuses"],
            {
                provider_id: "ok"
                for provider_id in PROVIDER_ORDER
            },
        )

        serialized = json.dumps(
            info,
            sort_keys=True,
        )

        self.assertNotIn(
            PUBLIC_ENTROPY.hex(),
            serialized,
        )

        self.assertEqual(
            json.loads(serialized),
            info,
        )


if __name__ == "__main__":
    unittest.main()
