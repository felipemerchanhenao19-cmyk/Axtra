"""Lanzador de AXTRA: usa automáticamente el entorno virtual.

    python axtra.py            -> inicia Axtra
    python axtra.py registrar  -> registra tu voz
    python axtra.py google     -> conecta Google Calendar y Gmail
    python axtra.py cara       -> registra tu cara para que te salude
    python axtra.py cerebro    -> descarga y prueba el cerebro local (Ollama, gratis)
    python axtra.py gemini     -> prueba la conexión con Gemini
    python axtra.py cerebros   -> prueba todos los cerebros gratis y la búsqueda en internet
    python axtra.py microfono  -> muestra los micrófonos y qué tan fuerte te oye
    python axtra.py voz        -> pone el umbral de tu voz en 0.50 (o "voz 0.45", "voz probar")
"""
import os
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
VENV_PY = BASE / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

if not VENV_PY.exists():
    sys.exit("Primero ejecuta:  python instalar.py")

arg = sys.argv[1].lower() if len(sys.argv) > 1 else ""
os.chdir(BASE)
if arg.startswith("reg"):
    sys.exit(subprocess.call([str(VENV_PY), "enroll.py"]))
if arg == "cara":
    sys.exit(subprocess.call([str(VENV_PY), "-c", "import vision; vision.enroll_face()"]))
if arg == "google":
    sys.exit(subprocess.call([str(VENV_PY), "-c", "import google_services as g; g.connect_interactive()"]))
if arg.startswith("micro"):
    sys.exit(subprocess.call([str(VENV_PY), "probar_microfono.py"]))
if arg == "voz":
    sys.exit(subprocess.call([str(VENV_PY), "ajustar_voz.py"] + sys.argv[2:]))
if arg == "cerebros":
    sys.exit(subprocess.call([str(VENV_PY), "probar_cerebros.py"]))
if arg == "gemini":
    sys.exit(subprocess.call([str(VENV_PY), "-c",
        "import time, llm, config; t=time.time(); "
        "print('Probando Gemini con', config.GEMINI_MODEL, '...') if config.GEMINI_API_KEY else exit('Falta GEMINI_API_KEY en .env'); "
        "print('Axtra (Gemini):', llm.gemini_chat('Eres AXTRA, mayordomo británico. Español, una frase.', "
        "[{'role':'user','content':'Preséntate brevemente.'}], 80)); print(f'({time.time()-t:.1f} s) GEMINI LISTO')"]))
if arg == "cerebro":
    sys.exit(subprocess.call([str(VENV_PY), "cerebro_local.py"]))
sys.exit(subprocess.call([str(VENV_PY), "main.py"]))
