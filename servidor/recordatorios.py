"""Recordatorios desde el celular: "recuérdame en 20 minutos sacar la ropa", "despiértame mañana a las 6:30".
A su hora llegan como notificación al teléfono (aunque la app esté cerrada)."""
import re
import threading
import time
import unicodedata
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from . import config, db

PEDIDO = re.compile(r"\b(recuerdame|recordarme|recuerdeme|avisame|aviseme|despiertame|despierteme|"
                    r"pon(me|ga)? una alarma|programa una alarma|alarma para)\b")
LISTAR = re.compile(r"\b(que|cuales|mis) recordatorios\b|\brecordatorios (tengo|pendientes)\b")
NUM = {"un": 1, "una": 1, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "diez": 10, "quince": 15,
       "veinte": 20, "treinta": 30, "media": 0.5}


def _norm(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def _ahora() -> datetime:
    return datetime.now(ZoneInfo(config.ZONA_HORARIA))


def es_pedido(texto: str) -> bool:
    t = _norm(texto)
    return bool(PEDIDO.search(t) or LISTAR.search(t))


def interpretar(texto: str, ahora: datetime = None):
    """Devuelve (mensaje, fecha) o (mensaje, None) si no dijo cuándo."""
    ahora = ahora or _ahora()
    t = _norm(texto)
    cuando, quitar = None, []
    m = re.search(r"\ben (\d+(?:[.,]\d+)?|un|una|uno|dos|tres|cuatro|cinco|diez|quince|veinte|treinta|media) "
                  r"(minutos?|mins?|horas?|dias?)\b(?: y media)?", t)
    if m:
        n = m.group(1)
        n = float(n.replace(",", ".")) if n[0].isdigit() else NUM[n]
        if m.group(0).endswith("y media"):
            n += 0.5
        unidad = m.group(2)
        cuando = ahora + (timedelta(minutes=n) if unidad.startswith("min") else
                          timedelta(hours=n) if unidad.startswith("hora") else timedelta(days=n))
        quitar.append(m.group(0))
    m = re.search(r"\b(?:(hoy|manana|pasado manana) )?(?:a las|a la) (\d{1,2})(?::(\d{2}))?"
                  r"(?: ?(am|pm|a\.? ?m\.?|p\.? ?m\.?|de la manana|de la tarde|de la noche))?", t)
    if m and not cuando:
        dia, h, mi, suf = m.group(1), int(m.group(2)), int(m.group(3) or 0), (m.group(4) or "").replace(".", "").replace(" ", "")
        if suf in ("pm", "delatarde", "delanoche") and h < 12:
            h += 12
        if suf in ("am", "delamanana") and h == 12:
            h = 0
        base = ahora + timedelta(days={"manana": 1, "pasado manana": 2}.get(dia, 0))
        cuando = base.replace(hour=h % 24, minute=mi, second=0, microsecond=0)
        if not dia and not suf and cuando <= ahora and h < 12:
            cuando += timedelta(hours=12)        # "a las 6" ya pasó en la mañana: las 6 de la tarde
        if cuando <= ahora:
            cuando += timedelta(days=1)
        quitar.append(m.group(0))
    elif re.search(r"\bmanana\b", t) and not cuando and re.search(r"despiert", t):
        cuando = (ahora + timedelta(days=1)).replace(hour=6, minute=0, second=0, microsecond=0)
    # El mensaje: lo que queda sin las palabras de la orden ni la hora
    msg = t
    for q in quitar:
        msg = msg.replace(q, " ")
    msg = PEDIDO.sub(" ", msg)
    msg = re.sub(r"^\W*(axtra\W+)?(por favor\W+)?", "", msg)
    msg = re.sub(r"\b(que|de|para|por favor|hoy|manana)\b\s*$", "", msg.strip())
    msg = re.sub(r"^(que|de|para)\s+", "", msg.strip()).strip(" ,.;:¡!¿?")
    if re.search(r"despiert", t) and not msg:
        msg = "Hora de despertar, señor."
    return (msg or "Recordatorio"), cuando


def _hora_bonita(f: datetime) -> str:
    hoy = _ahora().date()
    dia = "hoy" if f.date() == hoy else "mañana" if f.date() == hoy + timedelta(days=1) else f.strftime("el %d/%m")
    h = f.hour % 12 or 12
    return f"{dia} a las {h}:{f.minute:02d} {'a. m.' if f.hour < 12 else 'p. m.'}"


def responder(texto: str) -> str:
    t = _norm(texto)
    if LISTAR.search(t) and not PEDIDO.search(t):
        pend = db.recordatorios_pendientes()
        if not pend:
            return "No tiene recordatorios pendientes, señor."
        tz = ZoneInfo(config.ZONA_HORARIA)
        return "Sus recordatorios:\n" + "\n".join(
            f"- {r['mensaje']} — {_hora_bonita(datetime.fromtimestamp(r['cuando'], tz))}" for r in pend)
    msg, cuando = interpretar(texto)
    if not cuando:
        return f"Con gusto, señor. ¿Cuándo le recuerdo «{msg}»? Por ejemplo: «en 20 minutos» o «a las 6:30 p. m.»."
    db.crear_recordatorio(msg, cuando.timestamp())
    return f"Listo, señor. Le recordaré «{msg}» {_hora_bonita(cuando)}. Le llegará una notificación al celular."


# ---------------- Entrega ----------------
def _revisar() -> None:
    from . import push

    for r in db.recordatorios_vencidos(time.time()):
        push.enviar("Axtra · Recordatorio", r["mensaje"])
        db.marcar_enviado(r["id"])


def iniciar_vigilante() -> None:
    def bucle():
        while True:
            try:
                _revisar()
            except Exception as e:
                print(f"  (recordatorios: {e})")
            time.sleep(20)

    threading.Thread(target=bucle, daemon=True, name="recordatorios").start()
