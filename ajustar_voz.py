"""Ajusta qué tan estricto es Axtra al reconocer tu voz (JARVIS_VOICE_THRESHOLD en .env).

    python axtra.py voz           -> pone el umbral en 0.50
    python axtra.py voz 0.45      -> pone el umbral en el valor que digas
    python axtra.py voz probar    -> mide tu voz con 5 frases y te recomienda un umbral
"""
import re
import sys
from pathlib import Path

ENV = Path(__file__).resolve().parent / ".env"
KEY = "JARVIS_VOICE_THRESHOLD"
DEFAULT = 0.50


def set_threshold(value: float) -> None:
    """Deja una sola línea JARVIS_VOICE_THRESHOLD=valor en el .env, sin tocar lo demás."""
    lines = ENV.read_text(encoding="utf-8-sig").splitlines() if ENV.exists() else []
    new_line = f"{KEY}={value:.2f}"
    out, placed = [], False
    for line in lines:
        if re.match(rf"\s*{KEY}\s*=", line):
            if not placed:
                out.append(new_line)   # reemplaza la primera en el mismo lugar
                placed = True
            continue                   # y borra las repetidas
        out.append(line)
    if not placed:
        out.append(new_line)
    ENV.write_text("\n".join(out) + "\n", encoding="utf-8")

    from dotenv import dotenv_values

    leido = dotenv_values(ENV).get(KEY)
    print(f"Listo: en el .env quedó {KEY}={leido}")
    print("Reinicia Axtra para que lo use.")


def probar(frases: int = 5) -> None:
    """Graba varias frases tuyas y muestra el puntaje de cada una."""
    from audio import beep, record_utterance
    from config import VOICE_THRESHOLD
    from voice_id import VoiceID

    print("Cargando el modelo de voz...")
    vid = VoiceID()
    if vid.voiceprint is None:
        sys.exit("Primero registra tu voz con: python axtra.py registrar")
    print(f"Umbral actual: {VOICE_THRESHOLD:.2f}")
    print(f"Di {frases} frases como le hablas normalmente a Axtra (por ejemplo \"Axtra, ¿qué hora es?\").\n")

    scores = []
    for i in range(1, frases + 1):
        input(f"[{i}/{frases}] Presiona Enter y habla después del pitido...")
        beep()
        audio = record_utterance(start_timeout=8)
        if audio is None:
            print("   No te escuché, sigamos.\n")
            continue
        s = vid.score(audio)
        scores.append(s)
        estado = "aceptada" if s >= VOICE_THRESHOLD else "RECHAZADA"
        nota = "  (muy corta: habla un poco más)" if s == 0.0 else ""
        print(f"   voz: {s:.2f} -> {estado}{nota}\n")

    validos = [s for s in scores if s > 0]
    if not validos:
        sys.exit("No pude medir tu voz. Revisa el micrófono con: python axtra.py microfono")
    recomendado = max(0.35, round(min(validos) - 0.05, 2))
    print(f"Tu voz dio entre {min(validos):.2f} y {max(validos):.2f}.")
    print(f"Umbral recomendado: {recomendado:.2f} (un poco por debajo de tu puntaje más bajo).")
    if recomendado < 0.45:
        print("Ojo: con un umbral tan bajo otra persona podría pasar. Vuelve a registrar tu voz "
              "(python axtra.py registrar) con el micrófono que usas siempre.")
    if input("¿Lo guardo en el .env? (s/n): ").strip().lower().startswith("s"):
        set_threshold(recomendado)


def main() -> None:
    arg = sys.argv[1].strip().lower() if len(sys.argv) > 1 else ""
    if arg.startswith("prob"):
        probar()
        return
    try:
        value = float(arg.replace(",", ".")) if arg else DEFAULT
    except ValueError:
        sys.exit(__doc__)
    if not 0.0 < value < 1.0:
        sys.exit("El umbral debe estar entre 0 y 1 (por ejemplo 0.50).")
    set_threshold(value)


if __name__ == "__main__":
    main()
