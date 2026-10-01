#!/usr/bin/env bash
# Copia de seguridad diaria de tus datos (conversaciones, memoria, progreso). Guarda las últimas 14.
set -euo pipefail
DESTINO=/opt/axtra-respaldos
mkdir -p "$DESTINO"
VOL=$(docker volume ls -q | grep 'axtra_datos$' | head -1)
docker run --rm -v "$VOL":/datos:ro -v "$DESTINO":/respaldo alpine \
  tar czf "/respaldo/axtra-$(date +%F).tgz" -C /datos .
ls -1t "$DESTINO"/axtra-*.tgz | tail -n +15 | xargs -r rm --
echo "$(date '+%F %T') respaldo listo"
