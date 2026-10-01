"""API de Axtra en la nube. La usa la app del celular.

Para probar en tu PC:  AXTRA_MODO=desarrollo uvicorn servidor.app:app --reload
En el servidor:        uvicorn servidor.app:app --host 0.0.0.0 --port 8080   (detrás de Cloudflare Access)
"""
import re

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from . import config, db, seguridad
from .enrutador import Enrutador
from .proveedores import NoDisponible

app = FastAPI(title="Axtra", docs_url=None, redoc_url=None, openapi_url=None)
_enrutador = None


def enrutador() -> Enrutador:
    global _enrutador
    if _enrutador is None:
        _enrutador = Enrutador()
    return _enrutador


def usuario(request: Request) -> str:
    try:
        return seguridad.usuario_de(dict(request.headers), dict(request.cookies))
    except PermissionError as e:
        raise HTTPException(401, str(e))


class Pedido(BaseModel):
    texto: str = Field(min_length=1, max_length=20000)
    chat_id: str | None = None
    nivel: str | None = None     # para forzar un nivel desde la app (p. ej. "imagen" con el botón)


NIVELES = {"basico", "intermedio", "avanzado", "actualidad", "privado", "documento", "equipo_documento",
           "equipo_inversion", "imagen"}


@app.get("/api/salud")
def salud():
    return {"ok": True}


@app.get("/api/estado")
def estado(u: str = Depends(usuario)):
    e = enrutador()
    return {
        "usuario": config.USER_NAME,
        "cerebros": {k: p.disponible() for k, p in e.p.items()},
        "gasto_mes_usd": {"claude": round(db.gasto_mes("claude"), 4), "grok": round(db.gasto_mes("grok"), 4)},
        "topes_usd": {"claude": config.TOPE_CLAUDE_USD, "grok": config.TOPE_GROK_USD},
    }


@app.post("/api/chat")
def chat(p: Pedido, u: str = Depends(usuario)):
    texto = p.texto.strip()
    chat_id = p.chat_id if p.chat_id and db.existe_chat(p.chat_id) else db.nuevo_chat(texto)
    historial = db.historial(chat_id)
    nivel = p.nivel if p.nivel in NIVELES else None
    try:
        r = enrutador().responder(texto, historial, nivel=nivel)
    except NoDisponible as e:
        r = {"texto": "Señor, ahora mismo no tengo un cerebro disponible para esto. "
                      f"Detalle: {e}", "nivel": nivel or "", "cerebro": "", "usd": 0, "fuentes": [], "aviso": ""}
    db.guardar_mensaje(chat_id, "user", texto)
    db.guardar_mensaje(chat_id, "assistant", r.get("markdown") or r["texto"], r.get("cerebro", ""))
    for a in r.get("archivos", []):
        a["url"] = f"/api/archivos/{a['archivo']}"
    r["chat_id"] = chat_id
    return r


@app.get("/api/chats")
def lista_chats(u: str = Depends(usuario)):
    return db.chats()


@app.get("/api/chats/{chat_id}")
def ver_chat(chat_id: str, u: str = Depends(usuario)):
    if not db.existe_chat(chat_id):
        raise HTTPException(404, "no existe")
    return {"id": chat_id, "mensajes": db.mensajes(chat_id)}


@app.delete("/api/chats/{chat_id}")
def borrar_chat(chat_id: str, u: str = Depends(usuario)):
    db.borrar_chat(chat_id)
    return {"ok": True}


@app.get("/api/archivos/{nombre}")
def archivo(nombre: str, u: str = Depends(usuario)):
    if not re.fullmatch(r"[\w.-]+", nombre):
        raise HTTPException(404, "no existe")
    ruta = (config.FILES_DIR / nombre).resolve()
    if not ruta.is_file() or ruta.parent != config.FILES_DIR.resolve():
        raise HTTPException(404, "no existe")
    return FileResponse(ruta, filename=nombre if ruta.suffix == ".docx" else None)
