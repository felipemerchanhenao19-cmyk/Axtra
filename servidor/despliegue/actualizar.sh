#!/usr/bin/env bash
# Si hay cambios nuevos en GitHub, los descarga y reinicia Axtra (cron cada 10 minutos).
set -euo pipefail
DIR=/opt/axtra
RAMA="${RAMA:-main}"
cd "$DIR"
git fetch -q origin "$RAMA"
if [ "$(git rev-parse HEAD)" != "$(git rev-parse "origin/$RAMA")" ]; then
  echo "$(date '+%F %T') actualizando a $(git rev-parse --short "origin/$RAMA")"
  git pull -q --ff-only origin "$RAMA"
  cd servidor/despliegue && docker compose up -d --build && docker image prune -f >/dev/null
fi
