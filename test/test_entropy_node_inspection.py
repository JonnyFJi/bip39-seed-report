import json
import unittest

from unittest.mock import patch

import inspect_node_entropy as inspection


VALID = {
    "inspection_version": 1,
    "node_version": "v-test",
    "node_executable": "/test/bin/node",
    "platform": "linux",
    "architecture": "x64",
    "openssl_version": "test-openssl",
    "crypto_module_available": True,
    "webcrypto_get_random_values": True,
    "fips_mode": 0,
    "shared_openssl": False,
    "configured_openssl": True,
    "exec_argv": [],
}


class NodeInspectionTests(unittest.TestCase):
    def test_valid_metadata(self):
        self.assertEqual(
            inspection.parse_metadata(
                json.dumps(VALID)
            ),
            VALID,
        )

    def test_missing_and_extra_keys(self):
        missing = dict(VALID)
        del missing["node_version"]

        values = (
            missing,
            dict(
                VALID,
                unexpected=True,
            ),
            [],
            None,
        )

        for value in values:
            with self.subTest(
                kind=type(value)
            ):
                with self.assertRaises(ValueError):
                    inspection.validate_metadata(
                        value
                    )

    def test_invalid_version(self):
        for value in (
            True,
            0,
            2,
            "1",
            None,
        ):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    inspection.validate_metadata(
                        dict(
                            VALID,
                            inspection_version=value,
                        )
                    )

    def test_required_text_and_absolute_path(self):
        for key in inspection.TEXT_FIELDS:
            for value in (
                "",
                " ",
                None,
                1,
            ):
                with self.subTest(
                    key=key,
                    value=value,
                ):
                    changed = dict(VALID)
                    changed[key] = value

                    with self.assertRaises(
                        ValueError
                    ):
                        inspection.validate_metadata(
                            changed
                        )

        with self.assertRaises(ValueError):
            inspection.validate_metadata(
                dict(
                    VALID,
                    node_executable="node",
                )
            )

    def test_optional_openssl_version(self):
        inspection.validate_metadata(
            dict(
                VALID,
                openssl_version=None,
            )
        )

        for value in (
            "",
            1,
            True,
        ):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    inspection.validate_metadata(
                        dict(
                            VALID,
                            openssl_version=value,
                        )
                    )

    def test_boolean_fields(self):
        for key in inspection.BOOLEAN_FIELDS:
            for value in (
                1,
                "true",
                None,
            ):
                with self.subTest(
                    key=key,
                    value=value,
                ):
                    changed = dict(VALID)
                    changed[key] = value

                    with self.assertRaises(
                        ValueError
                    ):
                        inspection.validate_metadata(
                            changed
                        )

    def test_optional_build_flags(self):
        for key in (
            inspection.OPTIONAL_BOOLEAN_FIELDS
        ):
            for value in (
                True,
                False,
                None,
            ):
                changed = dict(VALID)
                changed[key] = value

                inspection.validate_metadata(
                    changed
                )

            for value in (
                1,
                "true",
            ):
                changed = dict(VALID)
                changed[key] = value

                with self.assertRaises(ValueError):
                    inspection.validate_metadata(
                        changed
                    )

    def test_fips_indicator(self):
        for value in (
            None,
            0,
            1,
        ):
            inspection.validate_metadata(
                dict(
                    VALID,
                    fips_mode=value,
                )
            )

        for value in (
            True,
            2,
            "0",
        ):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    inspection.validate_metadata(
                        dict(
                            VALID,
                            fips_mode=value,
                        )
                    )

    def test_runtime_arguments(self):
        inspection.validate_metadata(
            dict(
                VALID,
                exec_argv=["--test-only"],
            )
        )

        for value in (
            None,
            "--flag",
            [1],
        ):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    inspection.validate_metadata(
                        dict(
                            VALID,
                            exec_argv=value,
                        )
                    )

    def test_duplicate_keys(self):
        with self.assertRaises(ValueError):
            inspection.parse_metadata(
                '{"provider":"a","provider":"b"}'
            )

    def test_invalid_json(self):
        with self.assertRaises(ValueError):
            inspection.parse_metadata(
                "not-json"
            )

    def test_inconsistent_capabilities(self):
        with self.assertRaises(ValueError):
            inspection.validate_metadata(
                dict(
                    VALID,
                    crypto_module_available=False,
                )
            )

        inspection.validate_metadata(
            dict(
                VALID,
                crypto_module_available=False,
                webcrypto_get_random_values=False,
            )
        )

    def test_missing_runtime_does_not_launch_processes(self):
        with patch.object(
            inspection.shutil,
            "which",
            return_value=None,
        ):
            with patch.object(
                inspection.subprocess,
                "run",
            ) as run:
                with self.assertRaises(
                    RuntimeError
                ):
                    inspection.inspect_node()

                run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
