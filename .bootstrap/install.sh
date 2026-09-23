#!/usr/bin/env bash
set -euo pipefail

cat .bootstrap/part* > /tmp/gestor-clinica-payload.b64
base64 --decode /tmp/gestor-clinica-payload.b64 > /tmp/gestor-clinica-payload.tar.gz
tar -xzf /tmp/gestor-clinica-payload.tar.gz -C .

# El workflow CI se agrega después mediante la conexión GitHub autorizada.
# GITHUB_TOKEN no puede crear/modificar workflows sin permiso "workflows".
rm -f .github/workflows/ci.yml

test -f docker-compose.yml
test -f docker/postgres/init/001_schema.sql
test -f docker/postgres/init/002_app_extensions.sql
test -f src/auth/Dockerfile
test -f src/catalog/Dockerfile
test -f src/orders/Dockerfile
test -f src/payments/Dockerfile
test -f src/web/index.html
