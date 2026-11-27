"""Pruebas de preparar_runtimes_entropy.py con ejecutables simulados.

No usan secretos ni la red. Los ejecutables son programas Python temporales.
"""

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import preparar_runtimes_entropy as prep  # noqa: E402

JAVA_BODY = (
    "import sys\n"
    "sys.stderr.write('openjdk version \"11.0.0\"\\n')\n"
)
NODE_BODY = "print('v24.0.0')\n"
JAVAC_BODY = (
    "import json, pathlib, sys\n"
    "args = sys.argv[1:]\n"
    "if args == ['-version']:\n"
    "    print('javac 11.0.0')\n"
    "    raise SystemExit(0)\n"
    "pathlib.Path(__file__).with_name('javac_calls.json').write_text(json.dumps(args))\n"
    "if %(fail)s:\n"
    "    sys.stderr.write('error: fallo simulado\\n')\n"
    "    raise SystemExit(1)\n"
    "target = pathlib.Path(args[args.index('-d') + 1])\n"
    "for name in ('JavaEntropyProbe', 'JavaEntropyProvider'):\n"
    "    (target / (name + '.class')).write_bytes(b'falso-' + name.encode())\n"
)


def make_tool(path, body):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"#!{sys.executable}\n{body}", encoding="utf-8")
    path.chmod(0o755)


def snapshot(directory):
    return sorted(p.relative_to(directory).as_posix() for p in Path(directory).rglob("*"))


class Environment:
    def __init__(self, base, *, with_java=True, with_javac=True, with_node=True,
                 with_classes=False, with_sources=True, javac_fails=False):
        self.base = Path(base)
        self.root = self.base / "proyecto"
        if with_sources:
            for rel in prep.REQUIRED_FILES:
                target = self.root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("// ficticio\n", encoding="utf-8")
        else:
            self.root.mkdir(parents=True)
        jvm = self.base / "jvm" / "bin"
        if with_java:
            make_tool(jvm / "java", JAVA_BODY)
        if with_javac:
            make_tool(jvm / "javac", JAVAC_BODY % {"fail": "True" if javac_fails else "False"})
        node = self.base / "node" / "bin" / "node"
        if with_node:
            make_tool(node, NODE_BODY)
        self.config = prep.RuntimeConfig(
            root=self.root, java=jvm / "java", node=node,
            class_dir=self.root / "build" / "entropy_java",
            webcrypto=self.root / "entropy_helpers" / "webcrypto_provider.cjs",
        )
        if with_classes:
            self.config.class_dir.mkdir(parents=True)
            for name in prep.CLASS_NAMES:
                (self.config.class_dir / name).write_bytes(b"falso")

    @property
    def javac_log(self):
        return self.base / "jvm" / "bin" / "javac_calls.json"

    def commands(self):
        return {"proveedor": (str(self.config.java), "-x")}


def execute(env, **kwargs):
    out = io.StringIO()
    code = prep.run(env.config, out=out, build_commands=env.commands, **kwargs)
    return code, out.getvalue()


class ReadOnlyCheckTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_01_ready_environment_reports_ready(self):
        env = Environment(self.tmp.name, with_classes=True)
        code, text = execute(env)
        self.assertEqual(code, prep.EXIT_READY)
        self.assertIn("LISTO", text)
        self.assertNotIn("FALTA", text)
        self.assertIn("openjdk version", text)

    def test_02_missing_classes_explain_guide_and_exact_command(self):
        env = Environment(self.tmp.name)
        before = snapshot(env.root)
        code, text = execute(env)
        self.assertEqual(code, prep.EXIT_INCOMPLETE)
        self.assertIn("PREPARACIÓN INCOMPLETA", text)
        self.assertIn(prep.GUIDE, text)
        self.assertIn(prep.GUIDE_SECTION, text)
        self.assertIn("-encoding UTF-8 --release 11 -d build/entropy_java", text)
        self.assertIn("entropy_helpers/JavaEntropyProbe.java", text)
        self.assertIn("entropy_helpers/JavaEntropyProvider.java", text)
        self.assertIn("--compilar", text)
        self.assertIn("no demuestra por sí solo", text)
        self.assertEqual(snapshot(env.root), before)

    def test_03_read_only_mode_never_compiles(self):
        env = Environment(self.tmp.name)
        execute(env)
        self.assertFalse(env.javac_log.exists())
        self.assertFalse(env.config.class_dir.exists())

    def test_04_missing_javac_does_not_offer_assistant(self):
        env = Environment(self.tmp.name, with_javac=False)
        code, text = execute(env)
        self.assertEqual(code, prep.EXIT_INCOMPLETE)
        self.assertIn("[FALTA] R3", text)
        self.assertNotIn("Asistente opcional", text)
        self.assertIn("javac funcional", text)

    def test_05_missing_java_and_node_are_reported(self):
        env = Environment(self.tmp.name, with_java=False, with_node=False, with_classes=True)
        code, text = execute(env)
        self.assertEqual(code, prep.EXIT_INCOMPLETE)
        self.assertIn("[FALTA] R2", text)
        self.assertIn("[FALTA] R4", text)
        self.assertIn("no cree enlaces ni sustituya", text)

    def test_06_missing_sources_are_listed(self):
        env = Environment(self.tmp.name, with_sources=False, with_classes=True)
        code, text = execute(env)
        self.assertEqual(code, prep.EXIT_INCOMPLETE)
        self.assertIn("[FALTA] R1", text)
        self.assertIn("webcrypto_provider.cjs", text)

    def test_07_empty_class_file_counts_as_missing(self):
        env = Environment(self.tmp.name, with_classes=True)
        (env.config.class_dir / "JavaEntropyProvider.class").write_bytes(b"")
        code, text = execute(env)
        self.assertEqual(code, prep.EXIT_INCOMPLETE)
        self.assertIn("[FALTA] R5", text)

    def test_08_failing_version_query_is_missing(self):
        env = Environment(self.tmp.name, with_classes=True)
        make_tool(env.config.node, "import sys\nsys.exit(3)\n")
        code, text = execute(env)
        self.assertEqual(code, prep.EXIT_INCOMPLETE)
        self.assertIn("[FALTA] R4", text)

    def test_09_effective_commands_are_validated(self):
        env = Environment(self.tmp.name, with_classes=True)
        out = io.StringIO()
        broken = lambda: {"proveedor": ("relativo", "-x")}
        code = prep.run(env.config, out=out, build_commands=broken)
        self.assertEqual(code, prep.EXIT_INCOMPLETE)
        self.assertIn("[FALTA] R6", out.getvalue())

    def test_10_commands_not_evaluated_when_previous_checks_fail(self):
        env = Environment(self.tmp.name)
        code, text = execute(env)
        self.assertIn("[OMITIDO] R6", text)


class CompileAssistantTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)

    def test_11_compiles_with_documented_arguments_and_verifies(self):
        env = Environment(self.tmp.name)
        code, text = execute(env, compilar=True)
        self.assertEqual(code, prep.EXIT_READY)
        self.assertIn("LISTO", text)
        for name in prep.CLASS_NAMES:
            self.assertTrue((env.config.class_dir / name).is_file())
        args = json.loads(env.javac_log.read_text())
        self.assertEqual(args[:5], ["-encoding", "UTF-8", "--release", "11", "-d"])
        self.assertEqual(args[6:], list(prep.JAVA_SOURCES))
        self.assertIn("Hashes locales", text)

    def test_12_leaves_no_temporary_directories(self):
        env = Environment(self.tmp.name)
        execute(env, compilar=True)
        self.assertEqual(sorted(p.name for p in env.config.class_dir.parent.iterdir()),
                         ["entropy_java"])

    def test_13_refuses_incomplete_existing_directory_without_touching_it(self):
        env = Environment(self.tmp.name)
        env.config.class_dir.mkdir(parents=True)
        (env.config.class_dir / "otro.txt").write_text("conservar")
        before = snapshot(env.root)
        code, text = execute(env, compilar=True)
        self.assertEqual(code, prep.EXIT_ERROR)
        self.assertIn("ya existe pero está incompleto", text)
        self.assertEqual(snapshot(env.root), before)
        self.assertFalse(env.javac_log.exists())

    def test_14_existing_complete_classes_are_not_recompiled(self):
        env = Environment(self.tmp.name, with_classes=True)
        code, text = execute(env, compilar=True)
        self.assertEqual(code, prep.EXIT_READY)
        self.assertIn("no se recompila", text)
        self.assertFalse(env.javac_log.exists())
        self.assertEqual((env.config.class_dir / "JavaEntropyProvider.class").read_bytes(), b"falso")

    def test_15_failed_compilation_publishes_nothing(self):
        env = Environment(self.tmp.name, javac_fails=True)
        code, text = execute(env, compilar=True)
        self.assertEqual(code, prep.EXIT_ERROR)
        self.assertIn("La compilación falló", text)
        self.assertIn("fallo simulado", text)
        self.assertFalse(env.config.class_dir.exists())
        build = env.config.class_dir.parent
        self.assertEqual(list(build.iterdir()) if build.exists() else [], [])

    def test_16_missing_javac_refuses_without_creating_directories(self):
        env = Environment(self.tmp.name, with_javac=False)
        before = snapshot(env.root)
        code, text = execute(env, compilar=True)
        self.assertEqual(code, prep.EXIT_INCOMPLETE)
        self.assertIn("javac no encontrado", text)
        self.assertEqual(snapshot(env.root), before)

    def test_17_missing_source_refuses(self):
        env = Environment(self.tmp.name)
        (env.root / prep.JAVA_SOURCES[0]).unlink()
        code, text = execute(env, compilar=True)
        self.assertEqual(code, prep.EXIT_INCOMPLETE)
        self.assertIn("falta la fuente", text)
        self.assertFalse(env.javac_log.exists())

    def test_18_compiler_timeout_cleans_temporary_directory(self):
        env = Environment(self.tmp.name)

        def timing_out(*args, **kwargs):
            raise subprocess.TimeoutExpired(args[0], 1)

        out = io.StringIO()
        code = prep.run(env.config, compilar=True, out=out, runner=timing_out,
                        build_commands=env.commands)
        self.assertEqual(code, prep.EXIT_ERROR)
        self.assertFalse(env.config.class_dir.exists())
        self.assertEqual(list(env.config.class_dir.parent.iterdir()), [])


class ProjectConfigurationTests(unittest.TestCase):
    def test_19_reads_real_project_configuration(self):
        config, build_commands = prep.config_from_project(ROOT)
        self.assertTrue(config.java.is_absolute())
        self.assertTrue(config.node.is_absolute())
        self.assertEqual(config.javac.name, "javac")
        self.assertEqual(config.class_dir, ROOT / "build" / "entropy_java")
        self.assertEqual(config.webcrypto, ROOT / "entropy_helpers" / "webcrypto_provider.cjs")
        self.assertTrue(callable(build_commands))

    def test_20_documented_sources_and_helpers_exist_in_repository(self):
        for rel in prep.REQUIRED_FILES:
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_21_help_mentions_assistant_and_exits_zero(self):
        done = subprocess.run([sys.executable, "-B", str(ROOT / "preparar_runtimes_entropy.py"), "--help"],
                              capture_output=True, text=True, timeout=30)
        self.assertEqual(done.returncode, 0)
        self.assertIn("--compilar", done.stdout)

    def test_22_guide_documents_the_same_compile_flags(self):
        guide = (ROOT / prep.GUIDE).read_text(encoding="utf-8")
        for fragment in ("-encoding UTF-8", "--release 11", "-d build/entropy_java",
                         "JavaEntropyProbe.java", "JavaEntropyProvider.java"):
            self.assertIn(fragment, guide)


if __name__ == "__main__":
    unittest.main()
