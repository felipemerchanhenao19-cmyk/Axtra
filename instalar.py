"""Instalador de AXTRA en Python puro (Windows y Linux).

Uso (desde una terminal abierta en la carpeta axtra):
    python instalar.py
En Linux es mejor usar  bash instalar_linux.sh , que antes instala los programas del sistema.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
VENV = BASE / "venv"
VENV_PY = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
WINDOWS = os.name == "nt"

# (paquete pip, ¿es obligatorio?)
PAQUETES = [
    ("truststore", True),
    ("anthropic", True),
    ("python-dotenv", True),
    ("requests", True),
    ("tzdata", True),
    ("numpy", True),
    ("sounddevice", True),
    ("webrtcvad-wheels", True),
    ("onnxruntime", True),
    ("openwakeword", True),
    ("faster-whisper", True),
    ("edge-tts", True),
    ("SpeechRecognition", False),
    ("pygame-ce", True),
    ("matplotlib", False),
    ("python-docx", False),
    ("google-auth", False),
    ("google-auth-oauthlib", False),
    ("shazamio", False),
    ("pyttsx3", False),
    ("ddgs", False),
    ("soundfile", False),
    ("comtypes", False),
    ("pycaw", False),
    ("pyautogui", False),
    ("pyperclip", False),
    ("pillow", False),
    ("uiautomation", False),
    ("winsdk", False),
    ("pytesseract", False),
    ("opencv-contrib-python-headless==4.10.0.84", False),
    ("scipy", False),
    ("librosa", False),
    ("torch", False),  # solo para reconocer tu voz
]
# Solo existen en Windows (volumen, botones y lectura de pantalla de Windows)
SOLO_WINDOWS = {"comtypes", "pycaw", "uiautomation", "winsdk"}
# Solo en Linux: lee el texto de la pantalla con Tesseract
SOLO_LINUX = {"pytesseract"}
if WINDOWS:
    PAQUETES = [(p, o) for p, o in PAQUETES if p not in SOLO_LINUX]
else:
    PAQUETES = [(p, o) for p, o in PAQUETES if p not in SOLO_WINDOWS]


def run(cmd):
    print("  >", " ".join(str(c) for c in cmd))
    return subprocess.call([str(c) for c in cmd]) == 0


def main():
    os.chdir(BASE)
    v = sys.version_info
    print(f"=== Instalando AXTRA con Python {v.major}.{v.minor} ===\n")
    if v < (3, 10):
        sys.exit("Necesitas Python 3.10 o superior.")
    if v >= (3, 14):
        print("Aviso: Python muy nuevo. Algunas librerías de IA podrían no tener versión aún.\n")

    if not VENV_PY.exists():
        print("1) Creando entorno virtual (carpeta venv)...")
        if not run([sys.executable, "-m", "venv", VENV]):
            sys.exit("No se pudo crear el entorno virtual.")
    else:
        print("1) Entorno virtual ya existe.")

    print("\n2) Actualizando pip...")
    run([VENV_PY, "-m", "pip", "install", "--upgrade", "pip"])

    print("\n3) Instalando librerías (puede tardar 10-20 minutos)...")
    fallos = []
    for paquete, obligatorio in PAQUETES:
        print(f"\n--- {paquete} ---")
        extra = []
        if paquete == "torch" and not WINDOWS:
            # En Linux pip baja por defecto la versión para tarjetas NVIDIA (varios GB); esta es la liviana
            extra = ["--index-url", "https://download.pytorch.org/whl/cpu"]
        if not run([VENV_PY, "-m", "pip", "install", paquete] + extra):
            fallos.append((paquete, obligatorio))

    print("\n--- resemblyzer (reconocimiento de voz) ---")
    if not run([VENV_PY, "-m", "pip", "install", "resemblyzer", "--no-deps"]):
        fallos.append(("resemblyzer", False))

    env = BASE / ".env"
    if not env.exists():
        shutil.copy(BASE / ".env.example", env)

    print("\n" + "=" * 55)
    obligatorios = [p for p, o in fallos if o]
    opcionales = [p for p, o in fallos if not o]
    if not fallos:
        print("TODO INSTALADO CORRECTAMENTE")
    if opcionales:
        print(f"No se instalaron (opcionales): {', '.join(opcionales)}")
        print("  -> Axtra funcionará, pero SIN reconocer tu voz.")
        print("     Pon JARVIS_REQUIRE_VOICE_MATCH=0 en el archivo .env")
    if obligatorios:
        print(f"FALLARON (obligatorios): {', '.join(obligatorios)}")
        print("  -> Tu versión de Python es muy nueva para estas librerías.")
        if WINDOWS:
            print("     Solución: instala Python 3.12 al lado del tuyo (no borra nada):")
            print("        winget install -e --id Python.Python.3.12")
            print("     Borra la carpeta venv y ejecuta:  py -3.12 instalar.py")
        else:
            print("     Revisa que corriste primero:  bash instalar_linux.sh")
    elif not WINDOWS:
        print("\nSiguientes pasos:")
        print("  1. Abre el archivo .env (nano .env  o  xed .env) y pega tus claves")
        print("  2. python3 axtra.py registrar   (registra tu voz)")
        print("  3. Cerebro local gratis (opcional, recomendado):")
        print("        curl -fsSL https://ollama.com/install.sh | sh")
        print("        python3 axtra.py cerebro")
        print("  4. python3 axtra.py             (inicia Axtra)")
    else:
        print("\nSiguientes pasos:")
        print("  1. Abre el archivo .env con el Bloc de notas y pega tu clave de Anthropic")
        print("  2. python axtra.py registrar   (registra tu voz)")
        print("  3. Cerebro local gratis (opcional, recomendado):")
        print("        winget install -e --id Ollama.Ollama")
        print("        python axtra.py cerebro")
        print("  4. python axtra.py             (inicia Axtra)")
    print("=" * 55)


if __name__ == "__main__":
    main()
