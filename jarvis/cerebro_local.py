"""Instala y prueba el cerebro local de Jarvis (Ollama). Uso: python jarvis.py cerebro"""
import os
import shutil
import subprocess
import sys
import time

import requests

from config import LOCAL_MODEL, OLLAMA_URL


def main():
    print("=== Cerebro local de Jarvis ===\n")
    exe = shutil.which("ollama")
    if not exe:
        p = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe")
        if os.path.exists(p):
            exe = p
    if not exe:
        print("Ollama no está instalado. Instálalo con este comando y vuelve a ejecutar 'python jarvis.py cerebro':\n")
        print("    winget install -e --id Ollama.Ollama\n")
        print("(o descárgalo de ollama.com). Después cierra y abre la terminal.")
        sys.exit(1)

    try:
        requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
    except Exception:
        print("Encendiendo Ollama...")
        subprocess.Popen([exe, "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)

    print(f"Descargando el modelo {LOCAL_MODEL} (unos 2 GB, solo la primera vez)...\n")
    if subprocess.call([exe, "pull", LOCAL_MODEL]) != 0:
        sys.exit("No se pudo descargar el modelo. Revisa el internet y vuelve a intentar.")

    print("\nProbando el cerebro local (la primera respuesta tarda más porque lo carga en memoria)...")
    import llm

    llm._local_cache["t"] = 0
    t0 = time.time()
    ans = llm.local_chat("Eres JARVIS, un mayordomo británico. Responde en español, una frase.",
                         [{"role": "user", "content": "Preséntate brevemente."}], max_tokens=60)
    print(f"\nJarvis (local): {ans}\n({time.time() - t0:.0f} s)")
    t0 = time.time()
    ans = llm.local_chat("Eres JARVIS, un mayordomo británico. Responde en español, una frase.",
                         [{"role": "user", "content": "¿Qué opinas de aprender inglés?"}], max_tokens=60)
    print(f"Jarvis (local): {ans}\n({time.time() - t0:.0f} s, ya cargado)")
    print("\nCEREBRO LOCAL LISTO. Inicia Jarvis con: python jarvis.py")
    print("Si responde muy lento, pon en .env:  JARVIS_MODELO_LOCAL=qwen2.5:1.5b  y repite este comando.")


if __name__ == "__main__":
    main()
