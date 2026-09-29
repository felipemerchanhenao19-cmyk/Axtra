"""Estado de la batería en Windows (sin librerías extra)."""
import ctypes
import os
import time

_cache = {"t": 0.0, "v": False}


def on_battery() -> bool:
    """True si el portátil está funcionando con batería (cargador desconectado)."""
    if os.name != "nt":
        return False
    if time.time() - _cache["t"] < 20:
        return _cache["v"]

    class SPS(ctypes.Structure):
        _fields_ = [("ACLineStatus", ctypes.c_byte), ("BatteryFlag", ctypes.c_byte),
                    ("BatteryLifePercent", ctypes.c_byte), ("SystemStatusFlag", ctypes.c_byte),
                    ("BatteryLifeTime", ctypes.c_ulong), ("BatteryFullLifeTime", ctypes.c_ulong)]
    s = SPS()
    v = False
    try:
        if ctypes.windll.kernel32.GetSystemPowerStatus(ctypes.byref(s)):
            v = s.ACLineStatus == 0
    except Exception:
        v = False
    _cache.update(t=time.time(), v=v)
    return v
