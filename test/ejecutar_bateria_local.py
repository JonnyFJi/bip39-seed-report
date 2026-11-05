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
    ("10_ejecutor", "test/test_ejecutar_bateria_local.py", []),
]


NON_UNITTEST_STAGES = frozenset({"01_vectores", "02_cifrado", "03_entrada"})
MAX_WORKER_RECORD_BYTES = 4 * 1024 * 1024


class WorkerRecordError(ValueError):
    pass


def validate_worker_record(info, returncode, *, requires_unittest):
    if type(info) is not dict or set(info) != {"exit_code", "calls_by_line", "unittest"}:
        raise WorkerRecordError("Estructura de registro no admitida.")
    if type(info["exit_code"]) is not int or info["exit_code"] != returncode:
        raise WorkerRecordError("Código registrado distinto del proceso o de tipo no admitido.")
    hits, runs = info["calls_by_line"], info["unittest"]
    if type(hits) is not dict or type(runs) is not list:
        raise WorkerRecordError("Inventario o resultados de tipo no admitido.")
    for line, count in hits.items():
        if (type(line) is not str or not line.isascii() or not line.isdecimal()
                or line.startswith("0") or type(count) is not int or count <= 0):
            raise WorkerRecordError("Entrada de inventario no admitida.")
    counters = ("methods", "failures", "errors", "expected_failures", "unexpected_successes")
    totals = {name: 0 for name in counters}
    totals["skipped"] = 0
    empty_suite = requires_unittest and not runs
    for run in runs:
        if type(run) is not dict or set(run) != set(counters) | {"skipped"}:
            raise WorkerRecordError("Resultado unittest incompleto o no admitido.")
        if any(type(run[name]) is not int or run[name] < 0 for name in counters):
            raise WorkerRecordError("Contador unittest no admitido.")
        if type(run["skipped"]) is not list:
            raise WorkerRecordError("Lista de omisiones no admitida.")
        for item in run["skipped"]:
            if (type(item) is not dict or set(item) != {"test", "reason"}
                    or any(type(item[key]) is not str for key in ("test", "reason"))):
                raise WorkerRecordError("Detalle de omisión no admitido.")
        for name in counters:
            totals[name] += run[name]
        totals["skipped"] += len(run["skipped"])
        empty_suite = empty_suite or run["methods"] == 0
    totals["empty_suite"] = bool(empty_suite)
    totals["incomplete"] = bool(empty_suite or totals["skipped"] or totals["expected_failures"])
    return totals


def load_worker_record(path, returncode, *, requires_unittest):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Clave duplicada.")
            result[key] = value
        return result

    def reject_constant(_value):
        raise ValueError("Constante no admitida.")

    try:
        with path.open("rb") as handle:
            raw = handle.read(MAX_WORKER_RECORD_BYTES + 1)
        if len(raw) > MAX_WORKER_RECORD_BYTES:
            raise WorkerRecordError("Registro demasiado grande.")
        info = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                          parse_constant=reject_constant)
    except WorkerRecordError:
        raise
    except (OSError, ValueError, UnicodeError, RecursionError):
        raise WorkerRecordError("Registro ausente, ilegible o JSON no admitido.") from None
    return info, validate_worker_record(info, returncode, requires_unittest=requires_unittest)


def stage_outcome(returncode, totals, record_error=None):
    failed = bool(record_error or totals["failures"] or totals["errors"]
                  or totals["unexpected_successes"])
    effective_code = returncode or (1 if failed else 0)
    if effective_code:
        return effective_code, "FALLO"
    if totals["empty_suite"]:
        return 0, "INCOMPLETO"
    if totals["incomplete"]:
        return 0, "OK_CON_OMISIONES"
    return 0, "OK"


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
                             "expected_failures": len(result.expectedFailures),
                             "unexpected_successes": len(result.unexpectedSuccesses),
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
        code = int(exc.code) if isinstance(exc.code, int) else (0 if exc.code is None else 1)
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
    validated_records = {}
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
        record_error = None
        totals = {"methods": 0, "failures": 0, "errors": 0, "skipped": 0,
                  "expected_failures": 0, "unexpected_successes": 0,
                  "empty_suite": False, "incomplete": False}
        try:
            info, totals = load_worker_record(
                record, returncode, requires_unittest=label not in NON_UNITTEST_STAGES,
            )
            validated_records[label] = info
        except WorkerRecordError as exc:
            record_error = str(exc)
        effective_code, status = stage_outcome(returncode, totals, record_error)
        row = {"stage": label, "exit_code": effective_code,
               "process_exit_code": returncode, "seconds": round(duration, 3),
               **totals, "record_error": record_error, "status": status}
        summary.append(row)
        print(f"  {row['status']} · código {effective_code} · {row['seconds']} s", flush=True)
        if record_error:
            print("  Registro rechazado: " + record_error, flush=True)
        if effective_code:
            print("Se detiene la batería en el primer fallo; revisar el log y el resumen antes de cambiar código.")
            break
    functions = inventory()
    for row in functions:
        stages = []
        for label, info in validated_records.items():
            if str(row["line"]) in info["calls_by_line"]:
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
    incomplete = len(summary) != len(STAGES) or bool(missing_functions) or any(row["incomplete"] for row in summary)
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
