"""Inspección estática sanitizada; no lee .env ni contactos externos."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def main():
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    login = (ROOT / "src/web/index.html").read_text(encoding="utf-8")
    result = {
        "tipo": "inspección estática local; no corrida remota ni configuración efectiva cloud",
        "puertos_publicados": re.findall(r'^\s+- "(\d+:\d+)"', compose, re.M),
        "dockerfile_usuarios": {p.parent.name: re.findall(r"^USER (.+)$", p.read_text(), re.M) for p in (ROOT/"docker").glob("*/Dockerfile")},
        "ci_permisos_solo_lectura": "contents: read" in ci,
        "ci_guards_deploy": re.findall(r'if \[ -z "\$([A-Z_]+)" \]; then\s+echo [^\n]+\s+exit (\d)', ci),
        "formulario_sin_valores_precargados": all(not re.search(rf'<input\b[^>]*id="{id}"[^>]*\bvalue=', login) for id in ["login-email", "login-password"]),
        "secretos_default_existen_en_codigo": "dev-only-secret" in (ROOT/"src/common/config.py").read_text(),
        "cuenta_bootstrap_existe_en_sql": "USR_ADMIN" in (ROOT/"docker/postgres/init/002_app_extensions.sql").read_text(),
    }
    output = ROOT/"docs/seguridad/evidencias/devsecops/configuracion.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Inspección estática guardada; sin leer valores de entorno.")


if __name__ == "__main__":
    main()
