#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${STAGING_DEPLOY_HOOKS:-}" ]]; then
  echo "ERROR: STAGING_DEPLOY_HOOKS no está definido." >&2
  exit 1
fi

normalized="$(printf '%s' "$STAGING_DEPLOY_HOOKS" | tr ', ' '\n\n')"
count=0
while IFS= read -r hook; do
  [[ -z "$hook" ]] && continue
  count=$((count + 1))
  echo "Activando deploy hook de staging #$count..."
  curl --fail --silent --show-error --request POST "$hook" >/dev/null
done <<< "$normalized"

if [[ "$count" -eq 0 ]]; then
  echo "ERROR: No se encontró ningún deploy hook válido." >&2
  exit 1
fi

echo "Se activaron $count despliegue(s) de staging."
