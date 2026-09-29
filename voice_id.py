"""Reconocimiento de la voz del dueño (solo Felipe puede darle órdenes)."""
import numpy as np

from config import SAMPLE_RATE, VOICE_THRESHOLD, VOICEPRINT_PATH


class VoiceID:
    def __init__(self):
        from resemblyzer import VoiceEncoder

        self.encoder = VoiceEncoder(device="cpu", verbose=False)
        self.voiceprint = np.load(VOICEPRINT_PATH) if VOICEPRINT_PATH.exists() else None

    def embed(self, audio: np.ndarray):
        """Convierte un audio en una "huella de voz" (vector de 256 números)."""
        from resemblyzer import preprocess_wav

        wav = preprocess_wav(audio, source_sr=SAMPLE_RATE)
        if len(wav) < SAMPLE_RATE * 0.5:  # menos de medio segundo de voz: no sirve
            return None
        return self.encoder.embed_utterance(wav)

    def score(self, audio: np.ndarray) -> float:
        if self.voiceprint is None:
            return 0.0
        emb = self.embed(audio)
        if emb is None:
            return 0.0
        return float(np.dot(emb, self.voiceprint))

    def is_owner(self, audio: np.ndarray):
        s = self.score(audio)
        return s >= VOICE_THRESHOLD, s

    @staticmethod
    def save_voiceprint(embeddings) -> np.ndarray:
        mean = np.mean(np.stack(embeddings), axis=0)
        mean = mean / np.linalg.norm(mean)
        np.save(VOICEPRINT_PATH, mean)
        return mean
