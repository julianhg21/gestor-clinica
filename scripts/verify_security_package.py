"""Valida estructura y patrones sensibles, y conserva hashes de cierre local.

No lee .env, historial Git, bases ni servicios externos. No certifica ausencia
total de secretos: revisa solo los patrones y archivos declarados.
"""
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/seguridad"
EVIDENCE = DOCS / "evidencias"


def main():
    required = ["auditoria-inicial", "matriz-cumplimiento", "inventario-activos", "matriz-riesgos", "matriz-accesos", "matriz-trazabilidad", "politica-seguridad", "controles-implementados", "plan-pruebas", "resultados-pruebas", "gestion-incidentes", "respaldos-recuperacion", "gestion-cambios", "proveedores-cloud", "informe-final", "INFORME-PARA-DOCUMENTO-UNIVERSITARIO"]
    missing = [name for name in required if not (DOCS/(name+".md")).is_file()]
    controls = json.loads((DOCS/"controles.json").read_text(encoding="utf-8"))
    states = {"Implementado y validado", "Parcialmente implementado", "Propuesto"}
    assert len({c["id"] for c in controls}) == len(controls) == 40
    assert all(c["estado"] in states for c in controls)
    broken = []
    for path in DOCS.rglob("*.md"):
        for link in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if not re.match(r"https?://|#", link):
                if not (path.parent/link.split("#")[0]).exists():
                    broken.append(str(path.relative_to(ROOT))+": "+link)
    # Solo reportes de evidencia, no código que contiene datos sintéticos de tests.
    patterns = {
        "JWT compacto": r"eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
        "Clave privada PEM": r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        "Contraseña académica": re.escape("Admin"+"123!"),
        "Contraseña sintética de prueba": re.escape("Synthetic"+"123!")+"|"+re.escape("Incorrect"+"123!"),
        "Hash PBKDF2 materializado": r"pbkdf2_sha256\$\d+\$[A-Za-z0-9_-]+\$[A-Za-z0-9_-]+",
        "Patrón credencial proveedor": r"(?:ghp_|github_pat_|AKIA)[A-Za-z0-9_]{16,}",
    }
    findings = []
    scanned = []
    for path in EVIDENCE.rglob("*"):
        if path.suffix.lower() not in {".txt", ".md", ".json", ".xml", ".html"} or path.name in {"revision-secretos.json", "MANIFEST-SHA256.json"}:
            continue
        scanned.append(str(path.relative_to(ROOT)))
        content = path.read_text(encoding="utf-8", errors="replace")
        for name, pattern in patterns.items():
            if re.search(pattern, content):
                findings.append({"archivo":str(path.relative_to(ROOT)), "patron":name})
    stamp = datetime.now(timezone(timedelta(hours=-6))).isoformat()
    review = dict(fecha=stamp, procedimiento="python scripts/verify_security_package.py", alcance="Evidencias textuales locales; PNG revisados visualmente al capturarlos; no historial ni código fuente completo", patrones=list(patterns), archivos_revisados=scanned, hallazgos=findings, documentos_faltantes=missing, enlaces_rotos=broken, limite="Búsqueda por patrones, no certificación ni detector universal; no se conservan coincidencias ni valores")
    (EVIDENCE/"revision-secretos.json").write_text(json.dumps(review,ensure_ascii=False,indent=2),encoding="utf-8")
    # Crear antes de enumerar para que el listado de cambios incluya los propios índices.
    manifest_path=EVIDENCE/"MANIFEST-SHA256.json"
    if not manifest_path.exists():
        manifest_path.write_text("{}\n",encoding="utf-8")
    changed_path=EVIDENCE/"archivos-cambiados.txt"
    changed_path.touch(exist_ok=True)
    names=subprocess.check_output(["git","ls-files","--modified","--others","--exclude-standard"],cwd=ROOT,text=True).splitlines()
    changed_path.write_text("Cambios locales sin commit; lista git ls-files --modified --others --exclude-standard\n"+"\n".join(sorted(set(names)))+"\n",encoding="utf-8")
    allnames=subprocess.check_output(["git","ls-files","--cached","--others","--exclude-standard"],cwd=ROOT,text=True).splitlines()
    hashes={}
    for name in sorted(set(allnames)):
        path=ROOT/name
        if path.is_file() and path != manifest_path:
            hashes[name]={"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"conservado":datetime.fromtimestamp(path.stat().st_mtime,timezone(timedelta(hours=-6))).isoformat()}
    branch=subprocess.check_output(["git","branch","--show-current"],cwd=ROOT,text=True).strip()
    assert branch=="auditoria-ciberseguridad"
    manifest=dict(fecha=stamp,rama=branch,nota="Hashes al cierre; el manifiesto se excluye a sí mismo. Conservado = mtime, no inicio inferido de ejecución. Hashes del código al ejecutar pruebas: ejecuciones.json.",archivos=hashes)
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"{len(controls)} controles; {len(scanned)} evidencias textuales; {len(findings)} patrones sensibles; {len(missing)} documentos faltantes; {len(broken)} enlaces rotos")
    return int(bool(findings or missing or broken))


if __name__ == "__main__":
    raise SystemExit(main())
