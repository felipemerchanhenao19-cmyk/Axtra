"""Lanzador de JARVIS: usa automáticamente el entorno virtual.

    python jarvis.py            -> inicia Jarvis
    python jarvis.py registrar  -> registra tu voz
    python jarvis.py google     -> conecta Google Calendar y Gmail
    python jarvis.py cara       -> registra tu cara para que te salude
    python jarvis.py cerebro    -> descarga y prueba el cerebro local (Ollama, gratis)
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
if arg == "cerebro":
    sys.exit(subprocess.call([str(VENV_PY), "cerebro_local.py"]))
sys.exit(subprocess.call([str(VENV_PY), "main.py"]))
