"""Instala y prueba el cerebro local de Axtra (Ollama). Uso: python axtra.py cerebro"""
import os
import shutil
import subprocess
import sys
import time

import requests

from config import LOCAL_MODEL, OLLAMA_URL


def main():
    print("=== Cerebro local de Axtra ===\n")
    exe = shutil.which("ollama")
    if not exe:
        p = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe")
        if os.path.exists(p):
            exe = p
    if not exe:
        print("Ollama no está instalado. Instálalo con este comando y vuelve a ejecutar 'python axtra.py cerebro':\n")
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
    ans = llm.local_chat("Eres AXTRA, un mayordomo británico. Responde en español, una frase.",
                         [{"role": "user", "content": "Preséntate brevemente."}], max_tokens=60)
    print(f"\nAxtra (local): {ans}\n({time.time() - t0:.0f} s)")
    t0 = time.time()
    ans = llm.local_chat("Eres AXTRA, un mayordomo británico. Responde en español, una frase.",
                         [{"role": "user", "content": "¿Qué opinas de aprender inglés?"}], max_tokens=60)
    print(f"Axtra (local): {ans}\n({time.time() - t0:.0f} s, ya cargado)")
    print("\nCEREBRO LOCAL LISTO. Inicia Axtra con: python axtra.py")
    print("Otros modelos para probar (cambia JARVIS_MODELO_LOCAL en .env y repite este comando):")
    print("  gemma3:4b    -> buen español y conversación (un poco más pesado)")
    print("  qwen3:4b     -> más inteligente")
    print("  qwen2.5:1.5b -> el más rápido y liviano")


if __name__ == "__main__":
    main()
