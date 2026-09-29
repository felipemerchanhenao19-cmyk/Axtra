import numpy as np, sounddevice as sd
from openwakeword.model import Model

print("Microfono:", sd.query_devices(kind="input")["name"])
m = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
print("Habla y di 'Hey Jarvis'. Ctrl+C para salir.\n")
with sd.InputStream(samplerate=16000, channels=1, dtype="int16", blocksize=1280) as s:
    while True:
        d, _ = s.read(1280)
        x = d[:, 0]
        nivel = int(np.abs(x).mean())
        score = max(m.predict(x).values())
        barra = "#" * min(nivel // 50, 40)
        print(f"volumen {nivel:5d} {barra:<40} jarvis {score:.2f}   ", end="\r")