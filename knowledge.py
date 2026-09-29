"""Conocimiento para los cerebros: el perfil de Felipe y sus empresas (carpeta perfil/) y las notas
que Axtra estudia solo (data/conocimiento/). El cerebro local recibe solo los pedazos que tienen
que ver con la pregunta, para ser más listo sin volverse lento."""
import re
import unicodedata

from config import BASE_DIR, DATA_DIR

PROFILE_DIR = BASE_DIR / "perfil"
NOTES_DIR = DATA_DIR / "conocimiento"
STOP = set("""para como cuando donde esta estas este esto esos esas estos pero porque sobre entre
tiene tengo tienes hacer puede puedes quiero quieres dime cual cuales cuanto cuanta mucho muy mas
menos todo todos toda todas algo alguna alguno ahora hola axtra senor favor tambien desde hasta
solo sola cada otro otra otros otras eres somos tener hace haces sabes saber decir digame mismo
cuentame cuenta hablame explicame opinas piensas crees quisiera necesito gustaria
cosa cosas bien dias noche tarde manana""".split())
SYNONYMS = {"empresa": ["apex"], "negocio": ["apex"], "negocios": ["apex"], "orbe": ["orbes"],
            "orbes": ["orbe"], "tienda": ["marketplace"], "zapatos": ["calzado"], "tenis": ["calzado"],
            "pagina": ["boceto", "web"], "paginas": ["boceto", "web"]}
_cache = {"key": None, "chunks": []}


def _norm(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def _words(t: str) -> set:
    return {w[:6] for w in re.findall(r"[a-z0-9]{4,}", _norm(t)) if w not in STOP}


def _files():
    files = sorted(PROFILE_DIR.glob("*.md"))
    if NOTES_DIR.exists():
        files += sorted(NOTES_DIR.glob("*.md"), reverse=True)[:60]  # las 60 notas más recientes
    return files


def _chunks():
    files = _files()
    key = tuple((str(f), f.stat().st_mtime) for f in files)
    if key == _cache["key"]:
        return _cache["chunks"]
    chunks = []
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        title = f.stem.replace("_", " ")
        for sec in re.split(r"\n(?=#)", text):
            sec = sec.strip()
            head = sec.splitlines()[0].strip("# ") if sec else ""
            piece = ""
            for line in sec.splitlines() + [None]:  # pedazos de ~700 letras sin cortar líneas
                if line is None or len(piece) + len(line) > 700:
                    if len(piece.strip()) > 40:
                        chunks.append({"src": title, "text": piece.strip(),
                                       "words": _words(title + " " + head + " " + piece)})
                    piece = (f"({head}) " if head and line is not None else "")
                if line is not None:
                    piece += line + "\n"
    _cache.update(key=key, chunks=chunks)
    return chunks


def relevant(query: str, k: int = 2, max_chars: int = 1400) -> str:
    """Los pedazos de conocimiento más relacionados con la pregunta (o '' si ninguno)."""
    q = _words(query)
    for w in list(q):
        for s in SYNONYMS.get(w, []):
            q.add(s[:6])
    if not q:
        return ""
    need = 1 if len(q) <= 2 else 2
    scored = []
    for c in _chunks():
        score = len(q & c["words"])
        if score >= need:
            scored.append((score, c))
    scored.sort(key=lambda x: -x[0])
    out, total = [], 0
    for _, c in scored[:k]:
        piece = f"[{c['src']}] {c['text']}"
        if total + len(piece) > max_chars:
            piece = piece[:max_chars - total]
        out.append(piece)
        total += len(piece)
        if total >= max_chars:
            break
    return "\n".join(out)


def profile_full() -> str:
    """Todo el perfil de empresas (para Claude, que lo guarda en caché y cuesta poco)."""
    return "\n\n".join(f.read_text(encoding="utf-8", errors="ignore") for f in sorted(PROFILE_DIR.glob("*.md")))


ONE_LINE = ("Felipe dirige Apex Corporation: agentes de IA personalizados para negocios. Enfoque actual (el único "
            "activo): orbes de IA + realidad aumentada para restaurantes (luego cualquier negocio). Apex "
            "Marketplace y las páginas web para negocios están EN PAUSA, no son prioridad. Apex Closure (ventas) "
            "sigue activa aparte.")
