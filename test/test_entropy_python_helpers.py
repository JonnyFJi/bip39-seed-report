import pathlib
import secrets
import sys
import unittest

from unittest.mock import patch

from entropy_helpers import (
    python_entropy_provider as helper,
)

import entropy_python_config as config

from entropy_policy import PROVIDER_ORDER


class PythonEntropyHelperTests(unittest.TestCase):
    def args(self, provider="python_os"):
        return [
            "--provider",
            provider,
            "--bytes",
            "32",
        ]

    def test_os_calls_urandom_once(self):
        expected = b"A" * 32

        with patch.object(
            helper.os,
            "urandom",
            return_value=expected,
        ) as call:
            self.assertEqual(
                helper.generate_bytes(
                    "python_os",
                    32,
                ),
                expected,
            )

        call.assert_called_once_with(32)

    def test_secrets_range_and_fixed_width(self):
        values = (
            0,
            1,
            (1 << 256) - 1,
        )

        for value in values:
            with self.subTest(value=value):
                with patch.object(
                    secrets,
                    "randbelow",
                    return_value=value,
                ) as call:
                    data = helper.generate_bytes(
                        "python_secrets",
                        32,
                    )

                call.assert_called_once_with(
                    1 << 256
                )

                self.assertEqual(
                    data,
                    value.to_bytes(32, "big"),
                )

                self.assertEqual(
                    len(data),
                    32,
                )

    def test_invalid_requests(self):
        cases = (
            ("unknown", 32),
            ("python_os", 31),
            ("python_os", True),
        )

        for provider, size in cases:
            with self.subTest(
                provider=provider,
                size=size,
            ):
                with self.assertRaises(ValueError):
                    helper.generate_bytes(
                        provider,
                        size,
                    )

    def test_invalid_os_payloads(self):
        values = (
            b"",
            b"A" * 31,
            b"A" * 33,
            bytearray(32),
            "A" * 32,
        )

        for value in values:
            with self.subTest(
                kind=type(value)
            ):
                with patch.object(
                    helper.os,
                    "urandom",
                    return_value=value,
                ):
                    with self.assertRaises(
                        helper.ProtocolFailure
                    ):
                        helper.generate_bytes(
                            "python_os",
                            32,
                        )

    def test_invalid_secrets_values(self):
        values = (
            -1,
            1 << 256,
            True,
            "1",
        )

        for value in values:
            with self.subTest(value=value):
                with patch.object(
                    secrets,
                    "randbelow",
                    return_value=value,
                ):
                    with self.assertRaises(
                        helper.ProtocolFailure
                    ):
                        helper.generate_bytes(
                            "python_secrets",
                            32,
                        )

    def test_terminal_refused_before_generation(self):
        with patch.object(
            helper.os,
            "isatty",
            return_value=True,
        ):
            with patch.object(
                helper,
                "generate_bytes",
            ) as generate:
                self.assertEqual(
                    helper.main(self.args()),
                    12,
                )

                generate.assert_not_called()

    def test_invalid_arguments_do_not_generate(self):
        invalid = (
            [],
            ["--help"],
            [
                "--provider",
                "unknown",
                "--bytes",
                "32",
            ],
            [
                "--provider",
                "python_os",
                "--bytes",
                "31",
            ],
            self.args() + ["extra"],
        )

        with patch.object(
            helper.os,
            "isatty",
            return_value=False,
        ):
            with patch.object(
                helper,
                "generate_bytes",
            ) as generate:
                for args in invalid:
                    with self.subTest(args=args):
                        self.assertEqual(
                            helper.main(args),
                            12,
                        )

                generate.assert_not_called()

    def test_error_codes_are_quiet(self):
        cases = (
            (
                helper.ProviderUnavailable(),
                11,
            ),
            (
                OSError("SECRET_SENTINEL"),
                10,
            ),
            (
                NotImplementedError(),
                10,
            ),
            (
                helper.ProtocolFailure(),
                12,
            ),
            (
                RuntimeError("SECRET_SENTINEL"),
                12,
            ),
        )

        with patch.object(
            helper.os,
            "isatty",
            return_value=False,
        ):
            with patch.object(
                helper.os,
                "write",
            ) as write:
                for error, code in cases:
                    with self.subTest(
                        error=type(error)
                    ):
                        with patch.object(
                            helper,
                            "generate_bytes",
                            side_effect=error,
                        ):
                            self.assertEqual(
                                helper.main(self.args()),
                                code,
                            )

                write.assert_not_called()

    def test_unavailable_generator(self):
        with patch.object(
            helper.os,
            "urandom",
            None,
        ):
            with self.assertRaises(
                helper.ProviderUnavailable
            ):
                helper.generate_bytes(
                    "python_os",
                    32,
                )

        with patch.object(
            secrets,
            "randbelow",
            None,
        ):
            with self.assertRaises(
                helper.ProviderUnavailable
            ):
                helper.generate_bytes(
                    "python_secrets",
                    32,
                )

    def test_partial_binary_writes(self):
        payload = b"A" * 32
        chunks = []

        def write(fd, view):
            self.assertEqual(fd, 1)

            count = min(
                5,
                len(view),
            )

            chunks.append(
                bytes(view[:count])
            )

            return count

        with patch.object(
            helper.os,
            "isatty",
            return_value=False,
        ):
            with patch.object(
                helper,
                "generate_bytes",
                return_value=payload,
            ):
                with patch.object(
                    helper.os,
                    "write",
                    side_effect=write,
                ):
                    self.assertEqual(
                        helper.main(self.args()),
                        0,
                    )

        self.assertEqual(
            b"".join(chunks),
            payload,
        )

    def test_write_failure_does_not_retry_generation(self):
        with patch.object(
            helper.os,
            "isatty",
            return_value=False,
        ):
            with patch.object(
                helper,
                "generate_bytes",
                return_value=b"A" * 32,
            ) as generate:
                with patch.object(
                    helper.os,
                    "write",
                    side_effect=BrokenPipeError,
                ):
                    self.assertEqual(
                        helper.main(self.args()),
                        12,
                    )

                generate.assert_called_once()

    def test_keyboard_interrupt_propagates(self):
        with patch.object(
            helper.os,
            "isatty",
            return_value=False,
        ):
            with patch.object(
                helper,
                "generate_bytes",
                side_effect=KeyboardInterrupt,
            ):
                with self.assertRaises(
                    KeyboardInterrupt
                ):
                    helper.main(self.args())

    def test_configuration_contains_only_two_enabled_commands(self):
        commands = (
            config.build_python_only_commands()
        )

        self.assertEqual(
            set(commands),
            set(PROVIDER_ORDER),
        )

        self.assertIsNone(
            commands["java_secure_random"]
        )

        self.assertIsNone(
            commands["javascript_webcrypto"]
        )

        self.assertEqual(
            commands["python_os"],
            commands["python_secrets"],
        )

        command = commands["python_os"]

        self.assertTrue(
            pathlib.Path(
                command[0]
            ).is_absolute()
        )

        self.assertEqual(
            command[1:3],
            ("-I", "-S"),
        )

        self.assertEqual(
            command[3],
            str(config.HELPER_PATH),
        )

    def test_invalid_configuration(self):
        invalid = (
            "python3",
            "",
            "\0",
            1,
        )

        for executable in invalid:
            with self.subTest(
                executable=executable
            ):
                with self.assertRaises(ValueError):
                    config.build_python_only_commands(
                        python_executable=executable
                    )

        with patch.object(
            config,
            "HELPER_PATH",
            pathlib.Path(
                "/nonexistent-test-helper"
            ),
        ):
            with self.assertRaises(ValueError):
                config.build_python_only_commands()


if __name__ == "__main__":
    unittest.main()
