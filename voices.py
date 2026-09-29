"""Catálogo de voces de Axtra y la voz elegida (se guarda aunque lo apagues).

Por voz: "muéstrame las voces", "usa la voz 3", "voz más grave", "habla más rápido",
"activa el filtro Axtra", "desactiva el filtro".
"""
import json
import re

from config import DATA_DIR, TTS_PITCH, TTS_RATE, TTS_VOICE

PATH = DATA_DIR / "voz.json"

# (voz de edge-tts, velocidad, tono, descripción). Todas gratis.
CATALOG = [
    ("es-ES-AlvaroNeural", "-8%", "-12Hz", "mayordomo español, grave y pausado (la clásica)"),
    ("es-ES-AlvaroNeural", "-12%", "-20Hz", "mayordomo español muy grave, estilo película"),
    ("en-US-AndrewMultilingualNeural", "-5%", "-8Hz", "voz multilingüe, cálida y natural"),
    ("en-US-BrianMultilingualNeural", "-5%", "-10Hz", "voz multilingüe, joven y tranquila"),
    ("es-MX-JorgeNeural", "-5%", "-8Hz", "mexicano neutro, claro"),
    ("es-CO-GonzaloNeural", "+0%", "-5Hz", "colombiano, cercano"),
    ("es-AR-TomasNeural", "-5%", "-8Hz", "argentino, seguro"),
    ("es-CL-LorenzoNeural", "-5%", "-8Hz", "chileno, sereno"),
    ("es-US-AlonsoNeural", "-5%", "-8Hz", "latino de EE. UU., neutro"),
    ("es-ES-ElviraNeural", "-5%", "+0Hz", "voz femenina española, elegante"),
]
DEFAULT = {"voz": TTS_VOICE, "velocidad": TTS_RATE, "tono": TTS_PITCH, "filtro": True, "numero": 0}


def _load() -> dict:
    try:
        d = json.loads(PATH.read_text(encoding="utf-8"))
        return {**DEFAULT, **d}
    except (FileNotFoundError, json.JSONDecodeError):
        return dict(DEFAULT)


def _save(d: dict) -> None:
    PATH.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def current():
    """(voz, velocidad, tono) actuales."""
    d = _load()
    return d["voz"], d["velocidad"], d["tono"]


def filter_on() -> bool:
    return bool(_load().get("filtro", True))


def choose(n: int) -> str:
    if not 1 <= n <= len(CATALOG):
        return f"Tengo voces del 1 al {len(CATALOG)}, señor."
    v, r, p, desc = CATALOG[n - 1]
    d = _load()
    d.update(voz=v, velocidad=r, tono=p, numero=n)
    _save(d)
    return f"Listo, señor. Ahora uso la voz {n}: {desc}."


def _shift(value: str, delta: int, unit: str) -> str:
    m = re.match(r"([+-]?\d+)", value or "0")
    n = int(m.group(1)) if m else 0
    n = max(-50, min(50, n + delta))
    return f"{n:+d}{unit}"


def adjust(what: str) -> str:
    d = _load()
    if what == "grave":
        d["tono"] = _shift(d["tono"], -5, "Hz")
    elif what == "aguda":
        d["tono"] = _shift(d["tono"], +5, "Hz")
    elif what == "rapido":
        d["velocidad"] = _shift(d["velocidad"], +5, "%")
    elif what == "lento":
        d["velocidad"] = _shift(d["velocidad"], -5, "%")
    elif what == "filtro_on":
        d["filtro"] = True
    elif what == "filtro_off":
        d["filtro"] = False
    elif what == "reset":
        d = dict(DEFAULT)
    _save(d)
    return {"grave": "Un poco más grave.", "aguda": "Un poco más aguda.", "rapido": "Hablaré un poco más rápido.",
            "lento": "Hablaré un poco más despacio.", "filtro_on": "Filtro Axtra activado.",
            "filtro_off": "Filtro desactivado: voz natural.", "reset": "Volví a mi voz original."}[what]


def catalog_text() -> str:
    return " ".join(f"Voz {i + 1}: {c[3]}." for i, c in enumerate(CATALOG))


# ---------------- Filtro Axtra ----------------
def apply_filter(mp3_path: str):
    """Ecualiza la voz y le da un eco muy leve, estilo IA de película. Devuelve la ruta de un .wav
    o None si no se pudo (entonces se reproduce la voz normal)."""
    try:
        import numpy as np
        import soundfile as sf

        audio, sr = sf.read(mp3_path, dtype="float32", always_2d=False)
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        x = audio.copy()
        try:
            from scipy.signal import butter, lfilter

            b, a = butter(2, 90 / (sr / 2), "highpass")          # quita el retumbo
            x = lfilter(b, a, x)
            b, a = butter(2, [2500 / (sr / 2), 6000 / (sr / 2)], "bandpass")
            x = x + 0.18 * lfilter(b, a, x)                        # un poco de "presencia" metálica
        except Exception:
            pass
        out = x.copy()
        for delay_ms, gain in ((23, 0.16), (41, 0.10), (67, 0.06)):   # eco corto de sala
            d = int(sr * delay_ms / 1000)
            out[d:] += gain * x[:-d]
        peak = float(np.max(np.abs(out))) or 1.0
        out = (out / peak * 0.92).astype("float32")
        wav = str(mp3_path).rsplit(".", 1)[0] + "_fx.wav"
        sf.write(wav, out, sr)
        return wav
    except Exception as e:
        print(f"  (filtro de voz no disponible: {str(e)[:80]})")
        return None


# ---------------- Muestra de voces ----------------
pending_demo = False


def demo(tts) -> None:
    """Dice una frase con cada voz para que Felipe elija."""
    global pending_demo
    pending_demo = False
    try:
        for i, (v, r, p, desc) in enumerate(CATALOG, 1):
            tts.preview = (v, r, p)
            tts.say(f"Voz {i}. {desc}. A su servicio, señor.")
            if tts.last_interrupt:
                break
    finally:
        tts.preview = None
    tts.say("Esas son mis voces. Diga, por ejemplo: usa la voz dos.")
