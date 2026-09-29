"""Micrófono: palabra de activación ("Hey Jarvis"), grabación de frases y pitidos."""
import collections

import numpy as np
import sounddevice as sd
import webrtcvad

from config import END_PAUSE, MIN_SPEECH_LEVEL, SAMPLE_RATE, WAKEWORD_THRESHOLD

FRAME_MS = 30
FRAME_SAMPLES = SAMPLE_RATE * FRAME_MS // 1000  # 480 muestras
WAKE_CHUNK = 1280  # 80 ms, lo que espera openWakeWord


def beep(freq: float = 880, duration: float = 0.15, volume: float = 0.3) -> None:
    """Pitido corto para indicar que Jarvis está escuchando."""
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

    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16",
                        blocksize=FRAME_SAMPLES) as stream:
        while True:
            data, _ = stream.read(FRAME_SAMPLES)
            frame = data[:, 0].copy()
            loud = np.abs(frame).mean() >= MIN_SPEECH_LEVEL
            is_speech = loud and vad.is_speech(frame.tobytes(), SAMPLE_RATE)

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
    return np.concatenate(frames).astype(np.float32) / 32768.0


class WakeWordListener:
    """Escucha en segundo plano hasta oír "Hey Jarvis" (funciona sin internet)."""

    def __init__(self, threshold: float = WAKEWORD_THRESHOLD):
        from openwakeword import utils
        from openwakeword.model import Model

        utils.download_models(model_names=["hey_jarvis"])  # solo descarga la primera vez
        self.model = Model(wakeword_models=["hey_jarvis"], inference_framework="onnx")
        self.threshold = threshold

    def wait(self) -> float:
        self.model.reset()
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16",
                            blocksize=WAKE_CHUNK) as stream:
            while True:
                data, _ = stream.read(WAKE_CHUNK)
                scores = self.model.predict(data[:, 0])
                score = max(scores.values())
                if score >= self.threshold:
                    return score
