"""Micrófono: palabra de activación ("Hey Axtra"), grabación de frases y pitidos."""
import collections
import queue
import time

import numpy as np
import sounddevice as sd
import webrtcvad

from config import END_PAUSE, MIC_DEVICE, MIN_SPEECH_LEVEL, SAMPLE_RATE, WAKEWORD_THRESHOLD

FRAME_MS = 30
FRAME_SAMPLES = SAMPLE_RATE * FRAME_MS // 1000  # 480 muestras
WAKE_CHUNK = 1280  # 80 ms, lo que espera openWakeWord


def pick_microphone():
    """Elige el micrófono: el que diga JARVIS_MICROFONO, o si no, uno USB si hay, o el predeterminado."""
    try:
        devs = sd.query_devices()
        inputs = [(i, d["name"]) for i, d in enumerate(devs) if d.get("max_input_channels", 0) > 0]
        want = MIC_DEVICE.lower()
        chosen = None
        if want.isdigit():
            chosen = int(want) if any(i == int(want) for i, _ in inputs) else None
        elif want:
            chosen = next((i for i, n in inputs if want in n.lower()), None)
        if want and chosen is None:
            print(f"  (no encontré el micrófono '{MIC_DEVICE}'. Los que hay son:)")
            seen = set()
            for i, n in inputs:
                if n not in seen:
                    seen.add(n)
                    print(f"      [{i}] {n}")
            print("   Pon en .env JARVIS_MICROFONO= con el número o parte del nombre del correcto.")
        if chosen is not None:
            sd.default.device = (chosen, sd.default.device[1])
        idx = sd.default.device[0]
        name = sd.query_devices(idx)["name"] if idx is not None and idx >= 0 else "predeterminado"
        return name
    except Exception as e:
        return f"predeterminado ({e})"


# Nivel de ruido del cuarto: se aprende solo, para no tener que gritar con micrófonos de poca ganancia
_noise = collections.deque(maxlen=400)
_last_stall_msg = 0.0


def speech_threshold() -> float:
    if len(_noise) < 30:
        return MIN_SPEECH_LEVEL
    floor = float(np.median(_noise))
    return max(12.0, min(MIN_SPEECH_LEVEL, floor * 2.8))


def beep(freq: float = 880, duration: float = 0.15, volume: float = 0.3) -> None:
    """Pitido corto para indicar que Axtra está escuchando."""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), endpoint=False)
    tone = (volume * np.sin(2 * np.pi * freq * t)).astype(np.float32)
    fade = int(0.01 * SAMPLE_RATE)
    tone[:fade] *= np.linspace(0, 1, fade)
    tone[-fade:] *= np.linspace(1, 0, fade)
    sd.play(tone, SAMPLE_RATE)
    sd.wait()


def record_utterance(start_timeout: float = 5.0, max_seconds: float = 30.0,
                     silence_end: float = None, vad_level: int = 2,
                     min_speech_ms: int = 300):
    """Graba desde que empiezas a hablar hasta que haces silencio.

    Devuelve audio float32 (16 kHz) o None si no hablaste dentro de start_timeout.
    start_timeout=None espera indefinidamente.
    Ignora ruidos suaves (volumen menor a MIN_SPEECH_LEVEL) y sonidos muy cortos.
    """
    vad = webrtcvad.Vad(vad_level)
    max_frames = int(max_seconds * 1000 / FRAME_MS)
    start_frames = None if start_timeout is None else int(start_timeout * 1000 / FRAME_MS)
    end_frames = int((END_PAUSE if silence_end is None else silence_end) * 1000 / FRAME_MS)

    pre_roll = collections.deque(maxlen=10)  # guarda 300 ms antes de detectar voz
    frames = []
    started = False
    speech_run = 0
    silent_frames = 0
    waited = 0
    speech_frames = 0
    min_frames = max(1, min_speech_ms // FRAME_MS)

    q = queue.Queue()

    def _cb(indata, _frames, _time, _status):
        q.put(indata[:, 0].copy())

    global _last_stall_msg
    stalls = 0
    # Stream con "callback": si el micrófono deja de mandar sonido, no nos quedamos congelados
    # (y Ctrl+C siempre funciona).
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16",
                        blocksize=FRAME_SAMPLES, callback=_cb):
        while True:
            try:
                frame = q.get(timeout=2.0)
            except queue.Empty:
                stalls += 1
                if time.time() - _last_stall_msg > 60:
                    _last_stall_msg = time.time()
                    print("  ⚠ El micrófono no está enviando sonido. Revise que esté conectado, que no esté "
                          "silenciado (tecla del micrófono) y ejecute: python axtra.py microfono")
                if stalls >= 3:
                    return None   # se reabre el micrófono en el siguiente intento
                continue
            stalls = 0
            level = float(np.abs(frame).mean())
            loud = level >= speech_threshold()
            is_speech = loud and vad.is_speech(frame.tobytes(), SAMPLE_RATE)
            if not is_speech and not started:
                _noise.append(level)

            if not started:
                waited += 1
                pre_roll.append(frame)
                speech_run = speech_run + 1 if is_speech else 0
                if speech_run >= 5:  # 150 ms seguidos de voz = empezó a hablar
                    started = True
                    frames.extend(pre_roll)
                elif start_frames is not None and waited >= start_frames:
                    return None
            else:
                frames.append(frame)
                if is_speech:
                    speech_frames += 1
                silent_frames = 0 if is_speech else silent_frames + 1
                if silent_frames >= end_frames or len(frames) >= max_frames:
                    break

    if not frames or speech_frames + speech_run < min_frames:
        return None  # fue un ruido corto, no una frase
    audio = np.concatenate(frames).astype(np.float32) / 32768.0
    peak = float(np.max(np.abs(audio))) if len(audio) else 0.0
    if 0.0 < peak < 0.3:   # voz bajita o micrófono de poca ganancia: la subimos para que se entienda mejor
        audio = audio * min(8.0, 0.6 / peak)
    return audio


class WakeWordListener:
    """Escucha en segundo plano hasta oír "Hey Axtra" (funciona sin internet)."""

    def __init__(self, threshold: float = WAKEWORD_THRESHOLD):
        from openwakeword import utils
        from openwakeword.model import Model

        utils.download_models(model_names=["hey_jarvis"])  # solo descarga la primera vez
        self.model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
        self.threshold = threshold

    def wait(self) -> float:
        self.model.reset()
        q = queue.Queue()

        def _cb(indata, _frames, _time, _status):
            q.put(indata[:, 0].copy())

        stalls = 0
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16",
                            blocksize=WAKE_CHUNK, callback=_cb):
            while True:
                try:
                    data = q.get(timeout=2.0)
                except queue.Empty:
                    stalls += 1
                    if stalls >= 3:
                        print("  ⚠ El micrófono no está enviando sonido. Reabriendo...")
                        stalls = 0
                    continue
                stalls = 0
                scores = self.model.predict(data)
                score = max(scores.values())
                if score >= self.threshold:
                    return score
