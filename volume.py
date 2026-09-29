"""Volumen real de Windows (no teclas a ciegas): leer, subir, bajar, fijar, silenciar.

Axtra SIEMPRE se asegura de poder ser escuchado antes de hablar: si el PC quedó silenciado o con el
volumen casi en cero, lo sube a un nivel audible. Así nunca queda "mudo" por un silencio accidental.
"""
MIN_AUDIBLE = 0.12
RESTORE_TO = 0.35


def _endpoint():
    """Control de volumen de los parlantes (pycaw). None si no está disponible."""
    try:
        from pycaw.pycaw import AudioUtilities

        dev = AudioUtilities.GetSpeakers()
        ev = getattr(dev, "EndpointVolume", None)       # pycaw nuevo
        if ev is not None:
            return ev
        from ctypes import POINTER, cast

        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import IAudioEndpointVolume

        iface = dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)   # pycaw antiguo
        return cast(iface, POINTER(IAudioEndpointVolume))
    except Exception:
        return None


def _com():
    try:
        import comtypes

        comtypes.CoInitialize()
    except Exception:
        pass


def get():
    """(porcentaje 0-100, silenciado) o None si no se puede leer."""
    _com()
    ev = _endpoint()
    if ev is None:
        return None
    try:
        return round(ev.GetMasterVolumeLevelScalar() * 100), bool(ev.GetMute())
    except Exception:
        return None


def set_level(pct: float) -> bool:
    _com()
    ev = _endpoint()
    if ev is None:
        return False
    try:
        ev.SetMasterVolumeLevelScalar(max(0.0, min(1.0, pct / 100)), None)
        ev.SetMute(0, None)
        return True
    except Exception:
        return False


def change(delta_pct: float) -> bool:
    g = get()
    if g is None:
        return False
    return set_level(g[0] + delta_pct)


def mute(on: bool = True) -> bool:
    _com()
    ev = _endpoint()
    if ev is None:
        return False
    try:
        ev.SetMute(1 if on else 0, None)
        return True
    except Exception:
        return False


def ensure_audible() -> None:
    """Antes de que Axtra hable: quita el silencio y sube el volumen si está casi en cero."""
    g = get()
    if g is None:
        return
    pct, muted = g
    if muted:
        mute(False)
        print("  (el PC estaba silenciado: quité el silencio para que me escuche)")
    if pct < MIN_AUDIBLE * 100:
        set_level(RESTORE_TO * 100)
        print(f"  (el volumen estaba en {pct}%: lo subí a {int(RESTORE_TO * 100)}% para que me escuche)")


def status_text() -> str:
    g = get()
    if g is None:
        return "No puedo leer el volumen de Windows en este momento, señor."
    pct, muted = g
    return f"El volumen está en {pct} por ciento" + (", silenciado." if muted else ".")
