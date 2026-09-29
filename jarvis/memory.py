"""Memoria permanente de Jarvis (se guarda en la carpeta data, solo en tu PC).

- recuerdos.json: datos importantes sobre ti (proyectos, clientes, gustos, metas).
- historial.json: la conversación reciente, para retomar donde quedaron al reiniciar.
- conversaciones/AAAA-MM-DD.txt: registro diario de lo que hablan, para buscar después.
"""
import json
import threading
import unicodedata
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from config import DATA_DIR, TIMEZONE

FACTS_PATH = DATA_DIR / "recuerdos.json"
HISTORY_PATH = DATA_DIR / "historial.json"
LOG_DIR = DATA_DIR / "conversaciones"
LOG_DIR.mkdir(exist_ok=True)
MAX_FACTS = 200
_lock = threading.RLock()


def _now():
    return datetime.now(ZoneInfo(TIMEZONE))


def _simple(s: str) -> str:
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def _load(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def _save(path, data):
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


# ---------- Recuerdos ----------
def get_facts() -> list:
    return _load(FACTS_PATH, [])


def remember(texto: str) -> dict:
    with _lock:
        return _remember(texto)


def _remember(texto: str) -> dict:
    facts = get_facts()
    texto = texto.strip()
    if any(_simple(f["texto"]) == _simple(texto) for f in facts):
        return {"ok": True, "nota": "ya lo sabía"}
    facts.append({"texto": texto, "fecha": _now().strftime("%Y-%m-%d")})
    _save(FACTS_PATH, facts[-MAX_FACTS:])
    return {"ok": True, "guardado": texto}


def forget(texto: str) -> dict:
    with _lock:
        return _forget(texto)


def _forget(texto: str) -> dict:
    facts = get_facts()
    key = _simple(texto)
    words = [w for w in key.split() if len(w) > 3] or key.split()
    keep, removed = [], []
    for f in facts:
        (removed if words and all(w in _simple(f["texto"]) for w in words) else keep).append(f)
    _save(FACTS_PATH, keep)
    return {"ok": bool(removed), "olvidados": [f["texto"] for f in removed]}


def facts_for_prompt() -> str:
    facts = get_facts()
    if not facts:
        return "(todavía no tienes recuerdos guardados)"
    return "\n".join(f"- {f['texto']} ({f['fecha']})" for f in facts)


# ---------- Historial reciente ----------
def load_history() -> list:
    return _load(HISTORY_PATH, [])


def save_history(history: list) -> None:
    _save(HISTORY_PATH, history)


# ---------- Registro de conversaciones ----------
def log_exchange(user: str, answer: str) -> None:
    now = _now()
    path = LOG_DIR / f"{now:%Y-%m-%d}.txt"
    with _lock, path.open("a", encoding="utf-8") as f:
        f.write(f"[{now:%H:%M}] Felipe: {user}\n[{now:%H:%M}] Jarvis: {answer}\n\n")


def search_conversations(palabras: str, dias: int = 30) -> dict:
    """Busca en las conversaciones de los últimos días."""
    keys = [w for w in _simple(palabras).split() if len(w) > 2]
    hits = []
    for d in range(int(dias)):
        day = _now() - timedelta(days=d)
        path = LOG_DIR / f"{day:%Y-%m-%d}.txt"
        if not path.exists():
            continue
        for block in path.read_text(encoding="utf-8").split("\n\n"):
            if keys and all(k in _simple(block) for k in keys):
                hits.append(f"{day:%Y-%m-%d} {block.strip()}")
                if len(hits) >= 8:
                    return {"resultados": hits}
    return {"resultados": hits or ["No encontré conversaciones sobre eso."]}


TOOL_SCHEMAS = [
    {
        "name": "guardar_recuerdo",
        "description": (
            "Guarda para siempre un dato importante sobre Felipe: proyectos, clientes, metas, "
            "gustos, personas, decisiones o cosas que te pida recordar. Escríbelo como una frase "
            "clara y completa."
        ),
        "input_schema": {
            "type": "object",
            "properties": {"texto": {"type": "string"}},
            "required": ["texto"],
        },
    },
    {
        "name": "olvidar_recuerdo",
        "description": "Borra recuerdos que Felipe pida olvidar o que ya no sean ciertos.",
        "input_schema": {
            "type": "object",
            "properties": {"texto": {"type": "string", "description": "palabras clave del recuerdo"}},
            "required": ["texto"],
        },
    },
    {
        "name": "buscar_conversaciones",
        "description": "Busca en conversaciones pasadas (por ejemplo: '¿qué hablamos ayer de TSMC?').",
        "input_schema": {
            "type": "object",
            "properties": {
                "palabras": {"type": "string"},
                "dias": {"type": "integer", "description": "cuántos días atrás buscar (máx. 90)"},
            },
            "required": ["palabras"],
        },
    },
]

FUNCS = {
    "guardar_recuerdo": lambda texto: remember(texto),
    "olvidar_recuerdo": lambda texto: forget(texto),
    "buscar_conversaciones": lambda palabras, dias=30: search_conversations(palabras, min(int(dias), 90)),
}
