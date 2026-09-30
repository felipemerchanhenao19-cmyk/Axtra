#!/usr/bin/env bash
# Instala AXTRA en Linux Mint (o Ubuntu). Uso, desde la carpeta de Axtra:
#     bash instalar_linux.sh
# 1) Instala los programas del sistema que Axtra necesita (pide tu contraseña una vez).
# 2) Crea el entorno virtual e instala las librerías de Python (instalar.py).
# 3) Opcional: instala Ollama (cerebro local gratis).
set -e
cd "$(dirname "$0")"

echo "=== AXTRA para Linux ==="
if ! command -v apt-get >/dev/null; then
    echo "Este instalador es para Linux Mint / Ubuntu (usa apt). En otra distribución instala a mano"
    echo "los paquetes de la lista de abajo y luego ejecuta: python3 instalar.py"
    exit 1
fi

if [ "${XDG_SESSION_TYPE:-x11}" = "wayland" ]; then
    echo "AVISO: estás en una sesión Wayland. El control del mouse, la ventana activa y la lectura de"
    echo "pantalla de Axtra necesitan X11. Cierra sesión y en la pantalla de inicio elige la sesión"
    echo "normal (X11 / Cinnamon), no la de Wayland."
    echo
fi

echo "1) Programas del sistema (te pedirá tu contraseña)..."
sudo apt-get update
sudo apt-get install -y \
    python3 python3-venv python3-pip python3-dev python3-tk \
    libportaudio2 portaudio19-dev ffmpeg flac \
    espeak-ng libespeak1 \
    pulseaudio-utils playerctl \
    xdotool xprintidle xclip \
    tesseract-ocr tesseract-ocr-spa tesseract-ocr-eng \
    git curl

echo
echo "2) Librerías de Python (10 a 20 minutos)..."
python3 instalar.py

echo
if ! command -v ollama >/dev/null; then
    read -r -p "3) ¿Instalo Ollama, el cerebro local gratis (unos 2 GB)? (s/n): " resp
    if [[ "$resp" =~ ^[sS] ]]; then
        curl -fsSL https://ollama.com/install.sh | sh
        echo "Ahora descarga y prueba el modelo con:  python3 axtra.py cerebro"
    fi
else
    echo "3) Ollama ya está instalado."
fi

echo
echo "Listo. Si traes tu .env y la carpeta data de Windows, cópialos a esta carpeta."
echo "Inicia Axtra con:  python3 axtra.py"
