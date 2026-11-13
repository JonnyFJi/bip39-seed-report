import contextlib
import io
import json
import os
import pathlib
import subprocess
import tempfile
import unittest

from unittest.mock import patch

import inspect_node_entropy as inspection


class NodeSelectionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(
            prefix="node-selection-test-"
        )

        self.addCleanup(self.tmp.cleanup)

        self.root = pathlib.Path(
            self.tmp.name
        )

        self.node = (
            self.root
            / "node test"
        )

        self.node.write_text(
            "test placeholder",
            encoding="ascii",
        )

        self.node.chmod(0o700)

        self.probe = (
            self.root
            / "probe.cjs"
        )

        self.probe.write_text(
            "test placeholder",
            encoding="ascii",
        )

        self.metadata = {
            "inspection_version": 1,
            "node_version": "v-test",
            "node_executable": str(
                self.node.resolve()
            ),
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

    def response(self):
        return subprocess.CompletedProcess(
            [],
            0,
            json.dumps(
                self.metadata
            ).encode("utf-8"),
            b"",
        )

    def test_default_uses_path(self):
        with patch.object(
            inspection.shutil,
            "which",
            return_value=str(self.node),
        ) as which:
            self.assertEqual(
                inspection._select_node_executable(),
                str(self.node.resolve()),
            )

        which.assert_called_once_with("node")

    def test_explicit_path_bypasses_lookup(self):
        with patch.object(
            inspection.shutil,
            "which",
        ) as which:
            self.assertEqual(
                inspection._select_node_executable(
                    str(self.node)
                ),
                str(self.node.resolve()),
            )

        which.assert_not_called()

    def test_missing_explicit_path_does_not_fallback(self):
        with patch.object(
            inspection.shutil,
            "which",
        ) as which:
            with self.assertRaises(
                FileNotFoundError
            ):
                inspection._select_node_executable(
                    str(
                        self.root
                        / "missing"
                    )
                )

        which.assert_not_called()

    def test_invalid_explicit_paths(self):
        values = (
            "",
            "node",
            "relative/node",
            "~/node",
            "\0",
            1,
            True,
        )

        for value in values:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    inspection._select_node_executable(
                        value
                    )

    def test_directory_is_rejected(self):
        with self.assertRaises(ValueError):
            inspection._select_node_executable(
                str(self.root)
            )

    def test_non_executable_is_rejected(self):
        with patch.object(
            inspection.os,
            "access",
            return_value=False,
        ):
            with self.assertRaises(ValueError):
                inspection._select_node_executable(
                    str(self.node)
                )

    @unittest.skipUnless(
        os.name == "posix",
        "Enlaces POSIX",
    )
    def test_symlink_is_resolved(self):
        link = (
            self.root
            / "node-link"
        )

        link.symlink_to(self.node)

        self.assertEqual(
            inspection._select_node_executable(
                str(link)
            ),
            str(self.node.resolve()),
        )

    def test_inspection_uses_explicit_executable(self):
        with patch.object(
            inspection,
            "PROBE_PATH",
            self.probe,
        ):
            with patch.object(
                inspection.subprocess,
                "run",
                return_value=self.response(),
            ) as run:
                with patch.object(
                    inspection.shutil,
                    "which",
                ) as which:
                    result = inspection.inspect_node(
                        node_executable=str(
                            self.node
                        )
                    )

        which.assert_not_called()

        command = run.call_args.args[0]

        self.assertEqual(
            command,
            [
                str(self.node.resolve()),
                str(self.probe),
                "--describe",
            ],
        )

        self.assertFalse(
            run.call_args.kwargs.get(
                "shell",
                False,
            )
        )

        self.assertEqual(
            run.call_args.kwargs["cwd"],
            "/",
        )

        self.assertEqual(
            result["selected_node_executable"],
            str(self.node.resolve()),
        )

        self.assertTrue(
            result["executable_matches"]
        )

    def test_missing_probe_does_not_launch_process(self):
        with patch.object(
            inspection,
            "PROBE_PATH",
            self.root / "missing.cjs",
        ):
            with patch.object(
                inspection.subprocess,
                "run",
            ) as run:
                with self.assertRaises(
                    RuntimeError
                ):
                    inspection.inspect_node(
                        node_executable=str(
                            self.node
                        )
                    )

        run.assert_not_called()

    def test_parser_default_and_explicit_path(self):
        parser = inspection.build_parser()

        self.assertIsNone(
            parser.parse_args([]).node
        )

        self.assertEqual(
            parser.parse_args(
                [
                    "--node",
                    str(self.node),
                ]
            ).node,
            str(self.node),
        )

    def test_abbreviated_option_is_rejected(self):
        with contextlib.redirect_stderr(
            io.StringIO()
        ):
            with self.assertRaises(
                SystemExit
            ) as caught:
                inspection.build_parser().parse_args(
                    [
                        "--no",
                        str(self.node),
                    ]
                )

        self.assertEqual(
            caught.exception.code,
            2,
        )

    def test_main_forwards_explicit_path(self):
        output = io.StringIO()

        with patch.object(
            inspection,
            "inspect_node",
            return_value={
                "test": True,
            },
        ) as inspect:
            with contextlib.redirect_stdout(
                output
            ):
                code = inspection.main(
                    [
                        "--node",
                        str(self.node),
                    ]
                )

        self.assertEqual(code, 0)

        inspect.assert_called_once_with(
            node_executable=str(self.node)
        )

        self.assertEqual(
            json.loads(output.getvalue()),
            {
                "test": True,
            },
        )

    def test_main_failure_does_not_retry(self):
        with patch.object(
            inspection,
            "inspect_node",
            side_effect=RuntimeError(
                "test failure"
            ),
        ) as inspect:
            with contextlib.redirect_stderr(
                io.StringIO()
            ):
                code = inspection.main(
                    [
                        "--node",
                        str(self.node),
                    ]
                )

        self.assertEqual(code, 1)

        self.assertEqual(
            inspect.call_count,
            1,
        )

    def test_environment_is_not_modified(self):
        before = dict(os.environ)

        with patch.object(
            inspection,
            "PROBE_PATH",
            self.probe,
        ):
            with patch.object(
                inspection.subprocess,
                "run",
                return_value=self.response(),
            ):
                inspection.inspect_node(
                    node_executable=str(
                        self.node
                    )
                )

        self.assertEqual(
            dict(os.environ),
            before,
        )


if __name__ == "__main__":
    unittest.main()
