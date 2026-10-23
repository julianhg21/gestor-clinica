"""Reproduce pruebas locales sin credenciales ni URLs de ambientes externos.

--database habilita exclusivamente el contenedor aislado validado por las pruebas.
No crea contenedores, no despliega, no usa .env y no publica resultados.
"""
import argparse
import hashlib
import json
import os
import platform
from pathlib import Path
import re
import shutil
import subprocess
import sys
from datetime import datetime, timedelta, timezone

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/seguridad/evidencias"
ZONE = timezone(timedelta(hours=-6))


def now():
    return datetime.now(ZONE).isoformat()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", action="store_true")
    args = parser.parse_args()
    env = dict(os.environ)
    for name in ("STAGING_BASE_URL", "SMOKE_BASE_URL", "AUDIT_DB_CONTAINER"):
        env.pop(name, None)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    if args.database:
        env["AUDIT_DB_CONTAINER"] = "duality-audit-postgres-20261023"
    for category in ("devsecops", "autenticacion", "autorizacion", "sesiones", "bases-datos", "integridad-concurrencia", "contenedores", "vulnerabilidades", "respaldos", "infraestructura"):
        (OUTPUT / category).mkdir(parents=True, exist_ok=True)
    runs = []
    commands = [
        ("devsecops/final", [sys.executable, "-m", "pytest", "-p", "pytest_html.plugin", "-p", "pytest_metadata.plugin", "-p", "no:cacheprovider", "--junitxml="+str(OUTPUT / "devsecops/final.xml"), "--html="+str(OUTPUT / "devsecops/final.html"), "--self-contained-html"], "C01-C05,C07-C11", "R01,R03,R05", "Sin fallos; omisiones externas explícitas"),
        ("autenticacion/frontend", [shutil.which("node") or "node", "tests/security_frontend.cjs"], "C06", "R04", "Texto hostil codificado; sin inyección de etiquetas"),
        ("infraestructura/compose", ["docker", "compose", "config", "--quiet"], "C17", "R07", "Configuración sintácticamente válida"),
    ]
    for name, command, controls, risks, expected in commands:
        start = now()
        result = subprocess.run(command, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
        # Defensa adicional: no conservar JWT aun si una futura prueba imprime uno.
        clean = re.sub(r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+", "[JWT REDACTADO]", result.stdout)
        (OUTPUT / (name+".txt")).write_text(clean, encoding="utf-8")
        runs.append(dict(inicio=start, fin=now(), comando=command, control=controls, riesgo=risks, esperado=expected, codigo_salida=result.returncode, resultado_archivo=name+".txt", limite="Pruebas de API con dobles de Redis/BD; SQL real solo con --database; sin producción ni staging"))
        print(name, "exit", result.returncode, flush=True)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    branch = subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip()
    files = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT, text=True).splitlines()
    hashes = {f: hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files if (ROOT/f).is_file() and not f.startswith("docs/")}
    report = dict(fecha=now(), zona="America/Guatemala (UTC-06:00)", commit_base=commit, rama=branch, cambios_sin_commit=True, ambiente=platform.platform(), python=sys.version.split()[0], base_real=args.database, ejecuciones=runs, sha256_fuentes=hashes)
    (OUTPUT / "ejecuciones.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return int(any(r["codigo_salida"] for r in runs))


if __name__ == "__main__":
    raise SystemExit(main())
