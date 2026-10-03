#!/usr/bin/env bash
# Copia de seguridad diaria: datos de Axtra (conversaciones, memoria, progreso) y de Apex Play (pedidos, uso).
# Guarda las últimas 14 de cada uno.
set -euo pipefail
DESTINO=/opt/axtra-respaldos
mkdir -p "$DESTINO"
for NOMBRE in axtra apex; do
  VOL=$(docker volume ls -q | grep "${NOMBRE}_datos$" | head -1 || true)
  [ -n "$VOL" ] || continue
  docker run --rm -v "$VOL":/datos:ro -v "$DESTINO":/respaldo alpine \
    tar czf "/respaldo/${NOMBRE}-$(date +%F).tgz" -C /datos .
  ls -1t "$DESTINO"/"${NOMBRE}"-*.tgz | tail -n +15 | xargs -r rm --
done
echo "$(date '+%F %T') respaldo listo"
