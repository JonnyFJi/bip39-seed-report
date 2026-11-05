"""Batería local secuencial. Sin red, instalaciones, commits o edición del programa.
Ejecutar manualmente desde la raíz: "$PY" test/ejecutar_bateria_local.py
"""
import ast
import csv
from datetime import datetime, timezone
import hashlib
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import runpy
import subprocess
import sys
import tempfile
import time
import traceback
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "bip39_seed_report.py"
EXPECTED_SHA256 = "b09fcc4f292283b8d5e6f4470dc3858a079b209b1c3ccb579be27cdec51b5174"
STAGES = [
    ("01_vectores", "bip39_seed_report.py", ["--run-tests", "--vectors-file", "test/vectors.json"]),
    ("02_cifrado", "test/test_cifrado_report.py", []),
    ("03_entrada", "test/test_entrada_segura.py", []),
    ("04_contenedor", "test/test_contenedor_report.py", []),
    ("05_escritura", "test/test_escritura_report.py", []),
    ("06_regresion", "test/test_regresion_vectores_ultima_palabra.py", []),
    ("07_ux", "test/test_ux_terminal_report.py", []),
    ("08_integral", "test/test_revision_integral_report.py", []),
    ("09_inspector", "test/test_inspeccionar_reporte_cifrado.py", []),
]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory():
    tree = ast.parse(SCRIPT.read_bytes())
    rows = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            rows.append({"function": node.name, "line": node.lineno})
        elif isinstance(node, ast.ClassDef):
            for method in node.body:
                if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    rows.append({"function": node.name + "." + method.name, "line": method.lineno})
    return rows


def worker():
    if len(sys.argv) < 4:
        return 3
    target = Path(sys.argv[2]).resolve()
    record = Path(sys.argv[3]).resolve()
    arguments = sys.argv[4:]
    hits = {}
    unit_results = []
    process = os.getpid()
    filenames = {str(SCRIPT), "bip39_seed_report.py"}
    def profile(frame, event, arg):
        if event == "call" and frame.f_code.co_filename in filenames:
            line = str(frame.f_code.co_firstlineno)
            hits[line] = hits.get(line, 0) + 1
    original = unittest.TextTestRunner.run
    def recording_run(self, test):
        result = original(self, test)
        unit_results.append({"methods": result.testsRun, "failures": len(result.failures),
                             "errors": len(result.errors),
                             "skipped": [{"test": str(case), "reason": reason} for case, reason in result.skipped]})
        return result
    unittest.TextTestRunner.run = recording_run
    sys.path.insert(0, str(ROOT))
    os.chdir(ROOT)
    sys.argv = [str(target), *arguments]
    code = 0
    sys.setprofile(profile)
    try:
        runpy.run_path(str(target), run_name="__main__")
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 1)
    except KeyboardInterrupt:
        code = 130
    except BaseException:
        traceback.print_exc()
        code = 1
    finally:
        sys.setprofile(None)
        unittest.TextTestRunner.run = original
        if os.getpid() == process:
            record.write_text(json.dumps({"exit_code": code, "calls_by_line": hits,
                                          "unittest": unit_results}, indent=2), encoding="utf-8")
    return code


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--worker":
            return worker()
        print("Uso: python test/ejecutar_bateria_local.py (sin opciones)", file=sys.stderr)
        return 3
    required = [ROOT / relative for _, relative, _ in STAGES]
    required.extend([
        ROOT / "requirements.txt",
        ROOT / "bip39_seed_report.py.sha256",
        ROOT / "test/vectors.json",
        ROOT / "inspeccionar_reporte_cifrado.py",
    ])
    missing = [str(p.relative_to(ROOT)) for p in required if not p.is_file()]
    if missing:
        print("Preparación incompleta; faltan: " + ", ".join(missing), file=sys.stderr)
        return 3
    if digest(SCRIPT) != EXPECTED_SHA256:
        print("El hash del script difiere de la versión para la que se preparó esta batería. Detener y comparar.", file=sys.stderr)
        return 3
    checksum = (ROOT / "bip39_seed_report.py.sha256").read_text(encoding="ascii").split()
    if len(checksum) != 2 or checksum != [EXPECTED_SHA256, "bip39_seed_report.py"]:
        print("Checksum local incorrecto o con formato inesperado.", file=sys.stderr)
        return 3
    for path in set(required):
        if path.suffix == ".py":
            try:
                compile(path.read_bytes(), str(path), "exec")
            except SyntaxError:
                print("Error de sintaxis en " + str(path.relative_to(ROOT)), file=sys.stderr)
                return 3
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = str(ROOT)
    check = subprocess.run([sys.executable, "-c", "import mnemonic, bip_utils, cryptography"],
                           cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if check.returncode:
        print("Falló la importación de dependencias en este intérprete:\n" + check.stdout, file=sys.stderr)
        return 3
    output = ROOT / "output"
    output.mkdir(exist_ok=True)
    results_dir = Path(tempfile.mkdtemp(prefix="bateria_local_", dir=output))
    os.chmod(results_dir, 0o700)
    manifest = {str(path.relative_to(ROOT)): digest(path) for path in set(required)}
    environment = {
        "recorded_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version, "implementation": platform.python_implementation(),
        "system": platform.system(), "release": platform.release(), "machine": platform.machine(),
        "script_sha256": digest(SCRIPT),
        "packages": {p: metadata.version(p) for p in ("mnemonic", "bip-utils", "cryptography", "pip")},
    }
    os_release = Path("/etc/os-release")
    if os_release.is_file():
        environment["os_release"] = os_release.read_text(encoding="utf-8")
    (results_dir / "entorno.json").write_text(json.dumps(environment, indent=2), encoding="utf-8")
    (results_dir / "hashes_antes.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    checked = subprocess.run([sys.executable, "-m", "pip", "check"], cwd=ROOT, env=env,
                             stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    (results_dir / "00_pip_check.log").write_text(checked.stdout, encoding="utf-8")
    if checked.returncode:
        print("pip check falló. Registro: " + str(results_dir))
        return 3
    summary = []
    for label, relative, args in STAGES:
        print("Ejecutando " + label + " …", flush=True)
        record = results_dir / (label + ".json")
        started = time.monotonic()
        command = [sys.executable, str(Path(__file__).resolve()), "--worker", str(ROOT / relative), str(record), *args]
        try:
            proc = subprocess.run(command, cwd=ROOT, env=env, stdin=subprocess.DEVNULL,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  text=True, errors="replace", timeout=900)
            returncode = proc.returncode
            text = proc.stdout
        except subprocess.TimeoutExpired as exc:
            returncode = 124
            text = (exc.stdout.decode(errors="replace") if isinstance(exc.stdout, bytes) else exc.stdout or "") + "\nTIMEOUT: ensayo no completado.\n"
        duration = time.monotonic() - started
        (results_dir / (label + ".log")).write_text(text, encoding="utf-8")
        info = json.loads(record.read_text()) if record.is_file() else {"calls_by_line": {}, "unittest": []}
        skipped = sum(len(item["skipped"]) for item in info["unittest"])
        row = {"stage": label, "exit_code": returncode, "seconds": round(duration, 3),
               "skipped": skipped, "status": "FALLO" if returncode else ("OK_CON_OMISIONES" if skipped else "OK")}
        summary.append(row)
        print(f"  {row['status']} · código {returncode} · {row['seconds']} s", flush=True)
        if returncode:
            print("Se detiene la batería en el primer fallo; revisar el log antes de cambiar código.")
            break
    functions = inventory()
    for row in functions:
        stages = []
        for label, _, _ in STAGES:
            record = results_dir / (label + ".json")
            if record.is_file() and str(row["line"]) in json.loads(record.read_text())["calls_by_line"]:
                stages.append(label)
        row["called"] = bool(stages)
        row["stages"] = ";".join(stages)
        row["scope"] = ("Simulación msvcrt en Linux; no consola Windows real"
                        if row["function"] == "_read_line_with_timeout_windows"
                        else "Entrada registrada; consultar prueba y mocks; no implica cobertura de ramas")
    with (results_dir / "funciones.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["function", "line", "called", "stages", "scope"])
        writer.writeheader(); writer.writerows(functions)
    after = {name: (digest(ROOT / name) if (ROOT / name).is_file() else None) for name in manifest}
    (results_dir / "hashes_despues.json").write_text(json.dumps(after, indent=2), encoding="utf-8")
    unchanged = after == manifest
    missing_functions = [row["function"] for row in functions if not row["called"]]
    failed = any(row["exit_code"] for row in summary)
    incomplete = len(summary) != len(STAGES) or bool(missing_functions) or any(row["skipped"] for row in summary)
    code = 1 if failed or not unchanged else (2 if incomplete else 0)
    result = {"stages": summary, "protected_files_unchanged": unchanged,
              "functions_total": len(functions), "functions_called": len(functions) - len(missing_functions),
              "functions_not_called": missing_functions, "exit_code": code,
              "manual_terminal_tests": "PENDIENTES; ver guía; no se autoaprueban",
              "meaning": "Las funciones llamadas no equivalen a todas las ramas, plataformas o validez criptográfica independiente."}
    (results_dir / "resumen.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("\nResultados: " + str(results_dir))
    print(f"Funciones/métodos alcanzados: {result['functions_called']}/{result['functions_total']}")
    print("Archivos protegidos sin cambios: " + str(unchanged))
    if missing_functions:
        print("No alcanzadas: " + ", ".join(missing_functions))
    print("Código final: " + str(code) + ". Las comprobaciones manuales se registran por separado.")
    return code


if __name__ == "__main__":
    sys.exit(main())
