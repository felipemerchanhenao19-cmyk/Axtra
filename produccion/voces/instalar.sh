#!/usr/bin/env bash
# Instala el clonador de voces (gratis, local) en /home/user/voz-env y descarga los modelos.
# Hace falta red hacia: pypi.org, huggingface.co y sus CDN (us.aws.cdn.hf.co, cas-bridge.xethub.hf.co).
# Ocupa unos 6 GB. Tarda 5–10 minutos la primera vez.
set -euo pipefail
ENV=${VOZ_ENV:-/home/user/voz-env}
export HF_HUB_DISABLE_XET=1
if [ ! -x "$ENV/bin/python" ]; then uv venv -p python3.11 "$ENV" -q; fi
VIRTUAL_ENV="$ENV" uv pip install -q --python "$ENV/bin/python" torch==2.6.0 torchaudio==2.6.0 chatterbox-tts==0.1.7 faster-whisper num2words "setuptools<81"
"$ENV/bin/python" - <<'EOF'
import warnings; warnings.filterwarnings("ignore")
from chatterbox.mtl_tts import ChatterboxMultilingualTTS; ChatterboxMultilingualTTS.from_pretrained(device="cpu")
from faster_whisper import WhisperModel; WhisperModel("small", device="cpu", compute_type="int8")
print("Clonador de voces listo.")
EOF
