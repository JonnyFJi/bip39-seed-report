import json
import unittest

from unittest.mock import patch

import inspect_java_entropy as inspection


VALID = {
    "inspection_version": 1,
    "java_version": "test-version",
    "runtime_version": "test-runtime",
    "java_vendor": "test-vendor",
    "java_home": "/test-jdk",
    "vm_name": "test-vm",
    "strong_algorithms": (
        "test-algorithm:test-provider"
    ),
    "algorithm": "test-algorithm",
    "provider": "test-provider",
}


class JavaInspectionTests(unittest.TestCase):
    def test_valid_metadata(self):
        self.assertEqual(
            inspection.parse_metadata(
                json.dumps(VALID)
            ),
            VALID,
        )

    def test_missing_and_extra_keys(self):
        missing = dict(VALID)
        del missing["algorithm"]

        extra = dict(
            VALID,
            unexpected="value",
        )

        for value in (
            missing,
            extra,
            [],
            None,
        ):
            with self.subTest(
                kind=type(value)
            ):
                with self.assertRaises(ValueError):
                    inspection.validate_metadata(
                        value
                    )

    def test_invalid_version(self):
        for version in (
            True,
            0,
            2,
            "1",
            None,
        ):
            with self.subTest(
                version=version
            ):
                with self.assertRaises(ValueError):
                    inspection.validate_metadata(
                        dict(
                            VALID,
                            inspection_version=version,
                        )
                    )

    def test_empty_fields(self):
        keys = (
            inspection.METADATA_KEYS
            - {"inspection_version"}
        )

        for key in keys:
            for value in (
                "",
                "   ",
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

    def test_non_text_fields(self):
        for value in (
            None,
            1,
            True,
            [],
        ):
            with self.subTest(
                value=value
            ):
                with self.assertRaises(ValueError):
                    inspection.validate_metadata(
                        dict(
                            VALID,
                            provider=value,
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
                    inspection.inspect_java()

                run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
