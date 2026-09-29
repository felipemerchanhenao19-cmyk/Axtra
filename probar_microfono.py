"""Muestra los micrófonos y mide qué tan fuerte te oye cada uno. Uso: python axtra.py microfono"""
import time

import numpy as np
import sounddevice as sd

from audio import pick_microphone

print("=== Micrófonos del PC ===\n")
devs = sd.query_devices()
for i, d in enumerate(devs):
    if d.get("max_input_channels", 0) > 0:
        print(f"  [{i}] {d['name']}")
print(f"\nAxtra usará: {pick_microphone()}")
print("\nHabla normal durante 4 segundos (di: 'Hola Axtra, ¿cómo estás?')...")
time.sleep(0.5)
rec = sd.rec(int(4 * 16000), samplerate=16000, channels=1, dtype="int16")
sd.wait()
x = np.abs(rec[:, 0].astype(np.float32))
frames = x[: len(x) // 480 * 480].reshape(-1, 480).mean(axis=1)
voz, ruido = float(np.percentile(frames, 90)), float(np.percentile(frames, 20))
print(f"\nNivel de tu voz: {voz:.0f}   ruido del cuarto: {ruido:.0f}")
if voz < 40:
    print("-> Te oye MUY bajo. Sube el volumen del micrófono en Windows: Configuración > Sistema > Sonido >")
    print("   Entrada > tu micrófono > Volumen de entrada al 80-100%. O elige otro con JARVIS_MICROFONO en .env")
elif voz < 120:
    print("-> Te oye bajo pero Axtra se adapta solo. Mejor si subes un poco el volumen de entrada.")
else:
    print("-> Te oye bien.")
if ruido > voz * 0.5:
    print("-> Hay mucho ruido comparado con tu voz: acércate al micrófono o baja la música/ventilador.")
print("\nPara elegir un micrófono, pon en .env una parte de su nombre, por ejemplo:  JARVIS_MICROFONO=USB")
