#!/usr/bin/env python3
"""Comprueba y, si se solicita, prepara los runtimes de entropy.

Uso desde la raíz del proyecto:

    python3 preparar_runtimes_entropy.py             # solo lectura
    python3 preparar_runtimes_entropy.py --compilar  # asistente opcional

Sin opciones no modifica nada: comprueba fuentes, Java, javac, Node, las
clases Java compiladas y la construcción de los comandos efectivos, e indica
cómo continuar. Con --compilar compila las dos fuentes Java con el mismo
comando de la guía (docs/INSTALACION_LINUX.md), sin sobrescribir compilados
existentes. No instala runtimes, no usa la red y no usa sudo.

Códigos de salida: 0 listo; 1 error o compilación detenida; 3 preparación
incompleta.
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent

GUIDE = "docs/INSTALACION_LINUX.md"
GUIDE_SECTION = "Preparación adicional de runtimes para entropy"

JAVA_SOURCES = (
    "entropy_helpers/JavaEntropyProbe.java",
    "entropy_helpers/JavaEntropyProvider.java",
)
CLASS_NAMES = ("JavaEntropyProbe.class", "JavaEntropyProvider.class")
REQUIRED_FILES = (
    "entropy_python_config.py",
    "entropy_java_config.py",
    "entropy_all_config.py",
    "entropy_helpers/python_entropy_provider.py",
    "entropy_helpers/JavaEntropyProbe.java",
    "entropy_helpers/JavaEntropyProvider.java",
    "entropy_helpers/node_entropy_probe.cjs",
    "entropy_helpers/webcrypto_provider.cjs",
)

EXIT_READY = 0
EXIT_ERROR = 1
EXIT_INCOMPLETE = 3
VERSION_TIMEOUT = 10
COMPILE_TIMEOUT = 120


@dataclass(frozen=True)
class RuntimeConfig:
    root: Path
    java: Path
    node: Path
    class_dir: Path
    webcrypto: Path

    @property
    def javac(self):
        return self.java.with_name("javac")


@dataclass
class Check:
    ident: str
    title: str
    state: str
    detail: str = ""
    action: str = ""


class ConfigError(Exception):
    pass


def config_from_project(root):
    """Lee las rutas de los módulos de configuración del proyecto."""
    root = Path(root)
    added = str(root)
    sys.path.insert(0, added)
    try:
        import entropy_java_config as java_config
        import entropy_all_config as all_config
    except Exception as error:
        raise ConfigError(f"No se pudo leer la configuración: {error}") from error
    finally:
        try:
            sys.path.remove(added)
        except ValueError:
            pass
    config = RuntimeConfig(
        root=root,
        java=Path(str(java_config.JAVA_EXECUTABLE)),
        node=Path(str(all_config.NODE_EXECUTABLE)),
        class_dir=Path(java_config.CLASS_DIRECTORY),
        webcrypto=Path(all_config.WEBCRYPTO_HELPER),
    )
    return config, all_config.build_all_provider_commands


def executable_ok(path):
    path = Path(path)
    return path.is_file() and os.access(path, os.X_OK)


def query_version(path, flag):
    try:
        done = subprocess.run(
            [str(path), flag],
            capture_output=True,
            text=True,
            timeout=VERSION_TIMEOUT,
            stdin=subprocess.DEVNULL,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return None, f"no se pudo ejecutar: {error}"
    lines = (done.stdout + done.stderr).strip().splitlines()
    first = lines[0].strip() if lines else ""
    if done.returncode != 0:
        return None, f"código {done.returncode}: {first}"
    return first, ""


def relative_class_dir(config):
    try:
        return config.class_dir.relative_to(config.root).as_posix()
    except ValueError:
        return str(config.class_dir)


def compile_commands_text(config):
    target = relative_class_dir(config)
    return [
        f"mkdir -p {shlex.quote(target)}",
        " ".join(
            [
                shlex.quote(str(config.javac)),
                "-encoding UTF-8 --release 11",
                f"-d {shlex.quote(target)}",
                *JAVA_SOURCES,
            ]
        ),
    ]


def runtime_check(ident, title, path, flag, label):
    if not executable_ok(path):
        return Check(
            ident, title, "FALTA", f"{label} no encontrado o no ejecutable: {path}",
            f"Revise la ruta configurada y prepare {label} según la guía; "
            "no cree enlaces ni sustituya ejecutables del sistema.",
        )
    version, problem = query_version(path, flag)
    if version is None:
        return Check(ident, title, "FALTA", f"{label} no respondió a {flag}: {problem}",
                     "Revise el runtime antes de continuar.")
    return Check(ident, title, "OK", f"{version} ({path})")


def run_checks(config, build_commands=None):
    checks = []
    missing = [rel for rel in REQUIRED_FILES if not (config.root / rel).is_file()]
    checks.append(
        Check("R1", "Fuentes y auxiliares de la revisión",
              "FALTA" if missing else "OK",
              "faltan: " + ", ".join(missing) if missing else f"{len(REQUIRED_FILES)} archivos presentes",
              "Revise la copia o la revisión elegida; no descargue un auxiliar aislado "
              "desde una rama mutable." if missing else "")
    )
    checks.append(runtime_check("R2", "Java", config.java, "-version", "Java"))
    checks.append(runtime_check("R3", "Compilador javac", config.javac, "-version", "javac"))
    checks.append(runtime_check("R4", "Node", config.node, "--version", "Node"))
    absent = [
        n for n in CLASS_NAMES
        if not (config.class_dir / n).is_file() or (config.class_dir / n).stat().st_size == 0
    ]
    checks.append(
        Check("R5", "Clases Java compiladas",
              "FALTA" if absent else "OK",
              f"faltan en {config.class_dir}: " + ", ".join(absent) if absent
              else f"presentes en {config.class_dir}",
              "compile" if absent else "")
    )
    if all(c.state == "OK" for c in checks) and build_commands is not None:
        try:
            commands = build_commands()
            problems = []
            for provider, command in commands.items():
                if not command:
                    problems.append(f"{provider}: sin comando")
                    continue
                executable = Path(command[0])
                if not executable.is_absolute() or not executable_ok(executable):
                    problems.append(f"{provider}: ejecutable ausente o no absoluto")
            if problems:
                checks.append(Check("R6", "Comandos efectivos", "FALTA", "; ".join(problems),
                                    "Revise entropy_*_config.py."))
            else:
                checks.append(Check("R6", "Comandos efectivos", "OK",
                                    f"{len(commands)} proveedores con ejecutables presentes"))
        except Exception as error:
            checks.append(Check("R6", "Comandos efectivos", "FALTA", str(error),
                                "Revise entropy_*_config.py."))
    else:
        checks.append(Check("R6", "Comandos efectivos", "OMITIDO",
                            "se evalúan cuando las comprobaciones anteriores están en OK"))
    return checks


def report(checks, config, out):
    print("Comprobación de runtimes de entropy (solo lectura)", file=out)
    for check in checks:
        detail = f" — {check.detail}" if check.detail else ""
        print(f"[{check.state}] {check.ident} {check.title}{detail}", file=out)
    pending = [c for c in checks if c.state != "OK"]
    print(file=out)
    if not pending:
        print("LISTO: la preparación está completa; se puede continuar.", file=out)
        return
    print("PREPARACIÓN INCOMPLETA: no continúe con la generación redundante ni con la batería.", file=out)
    classes_missing = any(c.ident == "R5" and c.state == "FALTA" for c in checks)
    javac_ready = any(c.ident == "R3" and c.state == "OK" for c in checks)
    for check in pending:
        if check.action and check.action != "compile":
            print(f"- {check.ident}: {check.action}", file=out)
    if classes_missing:
        print("- R5: faltan las clases Java compiladas. Esto no demuestra por sí solo que Java "
              "esté desinstalado.", file=out)
        print(f"  Manual: sección «{GUIDE_SECTION}», paso 3, de {GUIDE}. "
              "Desde la raíz del proyecto:", file=out)
        for line in compile_commands_text(config):
            print(f"    {line}", file=out)
        if javac_ready:
            print("  Asistente opcional: python3 preparar_runtimes_entropy.py --compilar", file=out)
        else:
            print("  Antes hace falta un javac funcional (JDK compatible; ver R3).", file=out)
    print("Este programa no instala Java, javac ni Node, no usa la red y no usa sudo.", file=out)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compile_java(config, out, runner=subprocess.run):
    if config.class_dir.exists() or config.class_dir.is_symlink():
        if all((config.class_dir / n).is_file() for n in CLASS_NAMES):
            print(f"Las clases ya existen en {config.class_dir}; no se recompila.", file=out)
            return EXIT_READY
        print(f"Detener: {config.class_dir} ya existe pero está incompleto. "
              "Revíselo antes de recompilar; este asistente no borra ni sobrescribe "
              "compilados.", file=out)
        return EXIT_ERROR
    problems = []
    if not executable_ok(config.javac):
        problems.append(f"javac no encontrado o no ejecutable: {config.javac}")
    problems += [f"falta la fuente {rel}" for rel in JAVA_SOURCES
                 if not (config.root / rel).is_file()]
    if problems:
        for problem in problems:
            print(f"No se puede compilar: {problem}", file=out)
        print(f"Prepare un JDK compatible según {GUIDE}; este asistente no instala runtimes.", file=out)
        return EXIT_INCOMPLETE
    build_dir = config.class_dir.parent
    temp_dir = build_dir / f".{config.class_dir.name}_{os.getpid()}"
    try:
        build_dir.mkdir(parents=True, exist_ok=True)
        temp_dir.mkdir()
    except OSError as error:
        print(f"No se pudo preparar la carpeta de salida: {error}", file=out)
        return EXIT_ERROR
    command = [str(config.javac), "-encoding", "UTF-8", "--release", "11",
               "-d", str(temp_dir), *JAVA_SOURCES]
    print("Compilando con el comando de la guía; la salida se publica solo si termina bien:", file=out)
    for line in compile_commands_text(config)[1:]:
        print(f"  {line}", file=out)
    try:
        done = runner(command, cwd=config.root, capture_output=True, text=True,
                      timeout=COMPILE_TIMEOUT, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError) as error:
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"La compilación no pudo ejecutarse: {error}", file=out)
        return EXIT_ERROR
    produced = [temp_dir / n for n in CLASS_NAMES]
    if done.returncode != 0 or not all(p.is_file() and p.stat().st_size > 0 for p in produced):
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"La compilación falló (código {done.returncode}); no se creó {config.class_dir}.", file=out)
        for line in (done.stderr or "").strip().splitlines()[:20]:
            print(f"  {line}", file=out)
        return EXIT_ERROR
    try:
        os.rename(temp_dir, config.class_dir)
    except OSError as error:
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"No se pudo publicar la carpeta de clases: {error}", file=out)
        return EXIT_ERROR
    print("Compilación terminada con código 0. Hashes locales (no se exige igualar los históricos):", file=out)
    for name in CLASS_NAMES:
        print(f"  {sha256(config.class_dir / name)}  {relative_class_dir(config)}/{name}", file=out)
    return EXIT_READY


def run(config, *, compilar=False, build_commands=None, out=None, runner=subprocess.run):
    out = sys.stdout if out is None else out
    if compilar:
        code = compile_java(config, out, runner=runner)
        if code != EXIT_READY:
            return code
        print(file=out)
    checks = run_checks(config, build_commands)
    report(checks, config, out)
    return EXIT_READY if all(c.state == "OK" for c in checks) else EXIT_INCOMPLETE


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Comprueba los runtimes de entropy (solo lectura por defecto).")
    parser.add_argument(
        "--compilar", action="store_true",
        help="compila las fuentes Java con el comando de la guía si faltan las clases")
    args = parser.parse_args(argv)
    sys.dont_write_bytecode = True
    try:
        config, build_commands = config_from_project(ROOT)
    except ConfigError as error:
        print(error, file=sys.stderr)
        return EXIT_ERROR
    return run(config, compilar=args.compilar, build_commands=build_commands)


if __name__ == "__main__":
    sys.exit(main())
