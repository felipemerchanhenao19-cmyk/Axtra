"""Lanzador de JARVIS: usa automáticamente el entorno virtual.

    python jarvis.py            -> inicia Jarvis
    python jarvis.py registrar  -> registra tu voz
    python jarvis.py google     -> conecta Google Calendar y Gmail
    python jarvis.py cara       -> registra tu cara para que te salude
    python jarvis.py cerebro    -> descarga y prueba el cerebro local (Ollama, gratis)
    python jarvis.py gemini     -> prueba la conexión con Gemini
    python jarvis.py cerebros   -> prueba todos los cerebros gratis y la búsqueda en internet
    python jarvis.py microfono  -> muestra los micrófonos y qué tan fuerte te oye
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
if arg == "cerebros":
    sys.exit(subprocess.call([str(VENV_PY), "probar_cerebros.py"]))
if arg == "gemini":
    sys.exit(subprocess.call([str(VENV_PY), "-c",
        "import time, llm, config; t=time.time(); "
        "print('Probando Gemini con', config.GEMINI_MODEL, '...') if config.GEMINI_API_KEY else exit('Falta GEMINI_API_KEY en .env'); "
        "print('Jarvis (Gemini):', llm.gemini_chat('Eres JARVIS, mayordomo británico. Español, una frase.', "
        "[{'role':'user','content':'Preséntate brevemente.'}], 80)); print(f'({time.time()-t:.1f} s) GEMINI LISTO')"]))
if arg == "cerebro":
    sys.exit(subprocess.call([str(VENV_PY), "cerebro_local.py"]))
sys.exit(subprocess.call([str(VENV_PY), "main.py"]))
