"""Órdenes directas: se ejecutan al instante y SIN IA (cero saldo, cero espera).

Hora, fecha, clima, música, abrir cosas, recordatorios, alarmas, tareas, gastos, silencio,
clases de idiomas y briefing. Si la frase no encaja con ninguna, devuelve None y decide el cerebro.
"""
import re
import unicodedata
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from config import CITY, TIMEZONE

NUMS = {"un": 1, "una": 1, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6,
        "siete": 7, "ocho": 8, "nueve": 9, "diez": 10, "once": 11, "doce": 12, "trece": 13,
        "catorce": 14, "quince": 15, "veinte": 20, "veinticinco": 25, "treinta": 30,
        "cuarenta": 40, "cuarenta y cinco": 45, "cincuenta": 50, "noventa": 90}
NUM_RE = r"(\d+(?:[.,]\d+)?|cuarenta y cinco|" + "|".join(sorted(NUMS, key=len, reverse=True)) + ")"
LANG_RE = r"(ingles|frances|portugues|aleman|italiano|mandarin|chino|japones)"
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre",
         "octubre", "noviembre", "diciembre"]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]


def norm(text: str) -> str:
    t = unicodedata.normalize("NFD", text.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    t = re.sub(r"[¿?¡!.,;:\"]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    # quita cortesías al inicio y al final: "oye jarvis, por favor ... gracias"
    t = re.sub(r"^((oye|hola|jarvis|por favor|porfa|podrias|puedes|me puedes|me podrias|"
               r"quiero que|necesito que|hazme el favor de?|dale)\s+)+", "", t)
    t = re.sub(r"(\s+(por favor|porfa|jarvis|gracias|senor))+$", "", t)
    return t.strip()


def _num(s: str) -> float:
    s = s.strip()
    return float(s.replace(",", ".")) if re.match(r"\d", s) else NUMS.get(s, 0)


def _now():
    return datetime.now(ZoneInfo(TIMEZONE))


def _minutes(t: str):
    """'en 20 minutos' / 'en media hora' / 'dentro de dos horas' -> minutos, o None."""
    if re.search(r"\b(en|dentro de) media hora\b", t):
        return 30
    if re.search(r"\b(en|dentro de) (un )?cuarto de hora\b", t):
        return 15
    m = re.search(r"\b(?:en|dentro de) " + NUM_RE + r" (minuto|minutos|hora|horas)\b", t)
    if m:
        n = _num(m.group(1))
        return n * 60 if m.group(2).startswith("hora") else n
    return None


def _clock(t: str, assume_morning: bool = False):
    """'a las 6 y media de la manana' / 'a las 18:30' / 'a las siete pm' -> 'HH:MM', o None."""
    m = re.search(r"\ba las? " + NUM_RE + r"(?:[: ](\d{2}))?(?: y (media|cuarto|" + NUM_RE[1:-1] + r"))?"
                  r"(?: (?:de la |en la |del )?(manana|madrugada|tarde|noche|am|pm|a m|p m))?", t)
    if not m:
        return None
    h = int(_num(m.group(1)))
    mins = int(m.group(2)) if m.group(2) else 0
    if m.group(3):
        mins = 30 if m.group(3) == "media" else 15 if m.group(3) == "cuarto" else int(_num(m.group(3)))
    period = (m.group(4) or "").replace(" ", "")
    if period in ("tarde", "noche", "pm") and h < 12:
        h += 12
    elif period in ("manana", "madrugada", "am") and h == 12:
        h = 0
    elif not period and h < 12 and not assume_morning:
        # sin "am/pm": la próxima vez que llegue esa hora (7 -> 7 a. m. o 7 p. m., la más cercana)
        now = _now()
        am = now.replace(hour=h, minute=mins, second=0, microsecond=0)
        if am <= now:
            pm = am + timedelta(hours=12)
            h = h + 12 if pm > now and pm < am + timedelta(days=1) else h
    if not (0 <= h < 24 and 0 <= mins < 60):
        return None
    _clock.span = m.span()
    return f"{h:02d}:{mins:02d}"


def _strip_time(t: str) -> str:
    t = re.sub(r"\b(en|dentro de) (media hora|(un )?cuarto de hora|" + NUM_RE + r" (minutos?|horas?))\b", "", t)
    t = re.sub(r"\b(hoy|manana|esta tarde|esta noche)\b", "", t)
    t = re.sub(r"^\s*(que|de)\s+", "", t.strip())
    return re.sub(r"\s+", " ", t).strip()


# ---------------- Respuestas ----------------
def _hora():
    n = _now()
    h = n.hour % 12 or 12
    parte = "de la mañana" if n.hour < 12 else "de la tarde" if n.hour < 19 else "de la noche"
    return f"Son las {h}:{n.minute:02d} {parte}, señor."


def _fecha():
    n = _now()
    return f"Hoy es {DIAS[n.weekday()]} {n.day} de {MESES[n.month - 1]} de {n.year}, señor."


def _clima(t):
    from tools import get_weather

    w = get_weather()
    a, d = w["ahora"], w["hoy"]
    if "llover" in t or "lluvia" in t:
        p = d["prob_lluvia_pct"]
        juicio = "Yo llevaría paraguas." if p >= 50 else "No parece necesario el paraguas." if p < 25 else "Hay algo de riesgo."
        return f"La probabilidad de lluvia hoy en {CITY} es de {p:.0f} por ciento. {juicio}"
    return (f"En {CITY} hay {a['temperatura_c']:.0f} grados, {a['estado']}, con sensación de "
            f"{a['sensacion_c']:.0f}. Hoy la máxima será de {d['maxima_c']:.0f} y la mínima de "
            f"{d['minima_c']:.0f}, con {d['prob_lluvia_pct']:.0f} por ciento de probabilidad de lluvia.")


def _recordatorio(t):
    import skills

    wake = re.search(r"\b(despiertame|levantame|pon (una |la )?alarma|ponme (una )?alarma)\b", t)
    if not wake and not re.search(r"\b(recuerdame|recordarme|avisame|pon(me)? un recordatorio)\b", t):
        return None
    mins = _minutes(t)
    hora = None if mins is not None else _clock(t, assume_morning=bool(wake))
    if mins is None and not hora:
        return None
    if wake:
        msg = "Hora de levantarse, señor. Buenos días."
    else:
        if hora:  # quita "a las 5 de la tarde" del mensaje
            a, b = _clock.span
            t = t[:a] + " " + t[b:]
        msg = re.sub(r"^.*?\b(recuerdame|recordarme|avisame|pon(me)? un recordatorio( para)?)\b", "", t)
        msg = _strip_time(msg) or "lo que me pidió"
    r = skills.crear_recordatorio(msg, minutos=mins, hora=hora)
    if "error" in r:
        return None
    que = "Alarma lista" if wake else "Hecho"
    return f"{que}, señor: {r['sonara']}." + ("" if wake else f" Le recordaré {msg}.")


def _tareas(t):
    import skills

    if re.fullmatch(r"(que|cuales) (tareas tengo|son mis tareas|tengo pendiente|pendientes tengo)( hoy)?|"
                    r"(mis|ver|lee|leeme|dime) (las |mis )?tareas|lista de tareas", t):
        p = skills.tareas("ver")["pendientes"]
        if not p:
            return "No tiene tareas pendientes, señor. Un lujo poco común."
        return f"Tiene {len(p)} pendiente{'s' if len(p) > 1 else ''}: " + "; ".join(p[:8]) + "."
    m = re.match(r"(?:agrega|anade|anota|apunta|pon)(?: a (?:mis|la lista de) tareas| una tarea| en mis tareas)?"
                 r"(?: que)? (.+?)(?: a (?:mis|la lista de) tareas| en mis tareas)?$", t)
    if m and "tarea" in t:
        texto = m.group(1).strip()
        skills.tareas("agregar", texto)
        return f"Anotado en sus tareas: {texto}."
    m = re.match(r"(?:ya (?:hice|termine)|marca como hecha|completa la tarea|tacha)(?: la tarea)? (?:de )?(.+)$", t)
    if m:
        antes = len(skills.tareas("ver")["pendientes"])
        r = skills.tareas("completar", m.group(1))
        return ("Tachada. Bien hecho, señor." if len(r["pendientes"]) < antes
                else f"No encontré una tarea con '{m.group(1)}'.")
    return None


def _musica(t):
    import media

    short = len(t.split()) <= 6
    acciones = [
        (r"(pausa|pausar|pon pausa|deten|para|detener|quita)( la)? (musica|cancion|video)|pausa", "pausar", "En pausa."),
        (r"(reanuda|reanudar|continua|sigue|quita la pausa|dale play|play)( la)?( musica| cancion)?", "reanudar", "Reanudando."),
        (r"(siguiente|la que sigue|cambia(la)?|salta(la)?|otra)( cancion)?", "siguiente", "Siguiente canción."),
        (r"(anterior|la de antes|devuelve(la)?)( cancion)?", "anterior", "La anterior."),
        (r"(sube|subele|subir)( el| al)? volumen( un poco| mas)?|mas (volumen|duro)", "subir_volumen", "Subiendo el volumen."),
        (r"(baja|bajale|bajar)( el| al)? volumen( un poco| mas)?|mas (bajo|pasito)", "bajar_volumen", "Bajando el volumen."),
        (r"(silencia|silencio|mutea|quita el sonido)", "silenciar", "Silenciado."),
    ]
    if short:
        for pat, acc, resp in acciones:
            if re.fullmatch(pat, t):
                media.control_musica(acc, 2 if "mucho" in t else 1)
                return resp
    if re.fullmatch(r"(que|como se llama (la|esta)) cancion (es esta|es|esta sonando|suena)?|"
                    r"(reconoce|identifica) (esta|la) cancion|que (esta sonando|suena)", t):
        r = media.reconocer_cancion()
        if r.get("cancion"):
            extra = f", del álbum {r['album']}" if r.get("album") else ""
            anio = f", de {r['anio']}" if r.get("anio") else ""
            return f"Es {r['cancion']}, de {r['artista']}{extra}{anio}."
        return r.get("resultado") or r.get("error") or "No logré reconocerla, señor."
    m = re.match(r"(?:pon|ponme|reproduce|coloca|quiero escuchar)(?: algo de| musica de| la cancion| canciones de|"
                 r" un poco de| musica| algo)? (.+)$", t)
    if m and not re.search(r"\b(alarma|recordatorio|tarea|pausa|volumen)\b", t):
        q = m.group(1).strip()
        r = media.poner_musica(q)
        return f"Enseguida, señor: {r.get('reproduciendo', q)}."
    return None


def _abrir(t):
    import skills

    m = re.fullmatch(r"(?:abre|abreme|abrir|entra a|ve a)(?: el| la| mi| los| las)? ([\w .-]{2,30})", t)
    if m and len(m.group(1).split()) <= 3:
        skills.abrir(m.group(1))
        return f"Abriendo {m.group(1)}."
    m = re.fullmatch(r"busca(?:me)? en google (.+)", t)
    if m:
        skills.abrir(m.group(1))
        return "Aquí tiene los resultados en pantalla."
    return None


def _gasto(t):
    if not re.search(r"\b(cuanto (he|has|llevo|llevas|hemos) gastado|cuanto gastaste|cuanto saldo|mi saldo|gasto de la api)\b", t):
        return None
    import usage

    g = usage.cuanto_he_gastado()
    txt = (f"Hoy van {g['hoy_usd'] * 100:.1f} centavos de dólar en Claude, y "
           f"{g['hoy_respuestas_gratis_cerebro_local'] + g['hoy_ordenes_directas_sin_ia']} respuestas gratis.")
    if g.get("dias_que_dura_5_usd_a_este_ritmo"):
        txt += f" A este ritmo, 5 dólares duran unos {g['dias_que_dura_5_usd_a_este_ritmo']:.0f} días."
    return txt


def _silencio(t):
    m = re.search(r"\bno me hables\b(?: (?:por|durante) (media hora|" + NUM_RE + r" (minutos?|horas?)))?", t)
    if not m:
        return None
    import companion

    mins = 60
    if m.group(1) == "media hora":
        mins = 30
    elif m.group(2):
        mins = _num(m.group(2)) * (60 if m.group(3).startswith("hora") else 1)
    companion.modo_silencio(mins)
    return f"Entendido. No lo interrumpiré durante {mins:.0f} minutos, salvo alarmas."


def _idiomas(t):
    import language

    m = re.search(r"\b(practicar|practiquemos|practica|clase|leccion|aprender|estudiar|hablemos|hablar)\b"
                  r"(?: \w+){0,3} (?:en |de |el )?" + LANG_RE, t)
    if m and not re.search(r"\b(como va|progreso|nivel tengo)\b", t):
        idioma = "mandarin" if m.group(2) == "chino" else m.group(2)
        nivel = next((v for k, v in (("basico", "A2"), ("principiante", "A1"), ("intermedio", "B1"),
                                     ("avanzado", "B2")) if k in t), "")
        tema = re.search(r"\b(?:para|sobre|de) (entrevistas?.*|negocios.*|viajes?.*|ventas.*|bolsa.*|tecnologia.*)$", t)
        language.iniciar_clase(idioma, nivel, tema.group(1) if tema else "")
        return "Con mucho gusto, señor. Empecemos la clase."
    m = re.search(r"\b(como va|progreso|nivel tengo)\b.*\b" + LANG_RE, t)
    if m:
        p = language.progreso_idiomas()
        k = "mandarin" if m.group(2) == "chino" else m.group(2)
        d = p.get(k)
        if not d:
            return f"Aún no hemos tenido clases de {language.LANGS[k][0]}. Diga: quiero practicar {language.LANGS[k][0]}."
        return (f"Lleva {d['clases']} clases y {d['minutos']:.0f} minutos de práctica, "
                f"{d['palabras_aprendidas']} palabras nuevas" + (f", nivel estimado {d['nivel']}." if d.get("nivel") else "."))
    return None


def _briefing(t):
    if not re.search(r"\b(briefing|resumen del dia|mi resumen|como pinta el dia|que tengo hoy)\b", t):
        return None
    import briefing
    import llm

    data = briefing.briefing_data()
    return llm.ask_text(briefing.BRIEFING_PROMPT, [{"role": "user", "content": briefing.to_json(data)}],
                        prefer="local", max_tokens=350, origen="briefing")


def _dictado(t):
    m = re.search(r"\b(?:quiero |vamos a |voy a )?(?:dictar|dictado)\b(?: de)?(?: (?:mi|un|el|una|la))?"
                  r"(?: (ensayo|trabajo|documento|informe|taller|resumen|carta))?(?: (?:de|sobre|llamado|titulado) (.+))?$", t)
    if not m:
        return None
    import dictation

    tipo = m.group(1) or "trabajo"
    titulo = (m.group(2) or "").strip() or f"{tipo} {_now():%Y-%m-%d}"
    dictation.iniciar_dictado(titulo.capitalize(), tipo)
    return f"Listo para su {tipo}, señor. Cuando termine diga: fin del dictado."


HANDLERS = [
    (lambda t: _hora() if re.fullmatch(r"(que hora es|que horas son|(dime|me dices|me das) la hora|la hora|hora)( ahora| ya)?", t) else None),
    (lambda t: _fecha() if re.fullmatch(r"(que (dia|fecha) es hoy|que (dia|fecha) es|a cuanto estamos( hoy)?|que dia estamos)", t) else None),
    (lambda t: _clima(t) if re.search(r"\b(clima|que tiempo hace|como esta el tiempo|va a llover|llovera|temperatura hace|cuantos grados)\b", t)
     and not re.search(r"\b(manana|semana| en (?!tulua)\w+)", t) else None),
    _silencio, _recordatorio, _tareas, _idiomas, _dictado, _gasto, _musica, _abrir, _briefing,
]


def handle(text: str):
    """Devuelve la respuesta si es una orden directa, o None si necesita un cerebro."""
    t = norm(text)
    if not t or len(t.split()) > 25:
        return None
    for h in HANDLERS:
        try:
            r = h(t)
        except Exception as e:
            print(f"  (orden directa falló: {e})")
            return None
        if r:
            import usage

            usage.record_local("directo")
            return r
    return None
