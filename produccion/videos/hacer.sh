#!/usr/bin/env bash
# Produce un video cinematográfico: ./hacer.sh play|domicilios
# Requisitos: python con playwright, numpy, scipy, qrcode; ffmpeg; Chromium en /opt/pw-browsers.
# Voz: con GOOGLE_TTS_API_KEY en el entorno usa la voz de Google (VOZ_GOOGLE, por defecto es-US-Studio-B);
#      sin ella, PIPER_DIR debe apuntar a piper (voz provisional).
set -euo pipefail
PROD=$1; AQUI=$(cd "$(dirname "$0")" && pwd); PY=${PY:-python3}
TRABAJO=${TRABAJO:-/tmp/apex-video-$PROD}; mkdir -p "$TRABAJO/fc" "$TRABAJO/fk"
cp "$AQUI/grabaciones/$PROD/marcas.json" "$TRABAJO/"
[ -f "$TRABAJO/fc/00001.jpg" ] || ffmpeg -v error -i "$AQUI/grabaciones/$PROD/cliente.webm" -vf fps=24 -q:v 3 "$TRABAJO/fc/%05d.jpg"
[ -f "$TRABAJO/fk/00001.jpg" ] || ffmpeg -v error -i "$AQUI/grabaciones/$PROD/caja.webm" -vf fps=24 -q:v 3 "$TRABAJO/fk/%05d.jpg"
$PY "$AQUI/voz_cine.py" "$PROD" "$TRABAJO/voz"
$PY "$AQUI/musica.py" "$PROD" "$TRABAJO/voz" "$TRABAJO/musica.wav"
$PY "$AQUI/render.py" "$PROD" "$TRABAJO" 3
NOMBRE=$([ "$PROD" = play ] && echo Apex-Play-cine || echo Apex-Domicilios-cine)
$PY "$AQUI/mezcla.py" "$PROD" "$TRABAJO" "$AQUI/../../entregables/$NOMBRE.mp4"
ffmpeg -v error -y -i "$AQUI/../../entregables/$NOMBRE.mp4" -c:v libx264 -preset slow -crf 24 -maxrate 2.2M -bufsize 4M -c:a aac -b:a 160k -movflags +faststart "$AQUI/../../entregables/$NOMBRE-whatsapp.mp4"
echo "Listo: entregables/$NOMBRE.mp4"
