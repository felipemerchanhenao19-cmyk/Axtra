"""API de Axtra en la nube. La usa la app del celular.

Para probar en tu PC:  AXTRA_MODO=desarrollo uvicorn servidor.app:app --reload
En el servidor:        uvicorn servidor.app:app --host 0.0.0.0 --port 8080   (detrás de Cloudflare Access)
"""
import re
from contextlib import asynccontextmanager

from fastapi import Body, Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import config, db, idiomas, oido, push, recordatorios, seguridad, voz
from .enrutador import Enrutador
from .proveedores import NoDisponible



@asynccontextmanager
async def _vida(app):
    recordatorios.iniciar_vigilante()   # entrega los recordatorios a su hora
    yield


app = FastAPI(title="Axtra", docs_url=None, redoc_url=None, openapi_url=None, lifespan=_vida)
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


# ---------------- Voz, oído e idiomas ----------------
class PedidoVoz(BaseModel):
    texto: str = Field(min_length=1, max_length=5000)
    idioma: str | None = None     # None = voz de Axtra en español; "ruso", "ingles"... = voz nativa
    lento: bool = False


@app.post("/api/voz")
def hablar(p: PedidoVoz, u: str = Depends(usuario)):
    try:
        audio = voz.sintetizar(p.texto, p.idioma if p.idioma in voz.IDIOMAS else None, p.lento)
    except Exception as e:
        raise HTTPException(503, f"la voz no está disponible: {e}")
    return Response(audio, media_type="audio/mpeg", headers={"Cache-Control": "no-store"})


def _codigos(idioma: str):
    if idioma in voz.IDIOMAS:
        return voz.IDIOMAS[idioma][0], voz.IDIOMAS[idioma][2]
    return "es", "es-CO"


@app.post("/api/escuchar")
def escuchar(audio: bytes = Body(..., media_type="audio/wav"), idioma: str = "", u: str = Depends(usuario)):
    if len(audio) > 8_000_000:
        raise HTTPException(413, "audio demasiado largo")
    try:
        return {"texto": oido.transcribir(audio, *_codigos(idioma))}
    except (ValueError, RuntimeError) as e:
        raise HTTPException(422, str(e))


@app.post("/api/idiomas/pronunciacion")
def pronunciacion(idioma: str, objetivo: str, guia: str = "", audio: bytes = Body(..., media_type="audio/wav"),
                  u: str = Depends(usuario)):
    if idioma not in voz.IDIOMAS:
        raise HTTPException(400, "idioma no disponible")
    if len(audio) > 8_000_000 or len(objetivo) > 500:
        raise HTTPException(413, "demasiado largo")
    try:
        oido_texto = oido.transcribir(audio, *_codigos(idioma))
    except (ValueError, RuntimeError) as e:
        raise HTTPException(422, str(e))
    r = idiomas.evaluar(objetivo, idioma, oido_texto)
    r["consejo"] = idiomas.consejo(enrutador(), objetivo, guia, r)
    db.registrar_practica(idioma, objetivo, r["puntaje"])
    r["progreso"] = idiomas.progreso(idioma)
    return r


@app.get("/api/idiomas/progreso")
def progreso_idiomas(u: str = Depends(usuario)):
    return [idiomas.progreso(i) for i in db.idiomas_practicados()]


# ---------------- Datos del Axtra del PC ----------------
CLAVES_PC = {"recuerdos", "crm", "tareas", "recordatorios", "idiomas_pc", "perfil", "sincronizacion", "protocolo"}


@app.post("/api/pc/sincronizar")
async def sincronizar_pc(request: Request, u: str = Depends(usuario)):
    if u != "pc" and not config.MODO_DESARROLLO:
        raise HTTPException(403, "solo el Axtra del PC puede subir datos")
    cuerpo = await request.body()
    if len(cuerpo) > 5_000_000:
        raise HTTPException(413, "demasiados datos")
    try:
        import json

        datos = json.loads(cuerpo)
    except ValueError:
        raise HTTPException(400, "JSON inválido")
    if not isinstance(datos, dict):
        raise HTTPException(400, "JSON inválido")
    validos = {k: v for k, v in datos.items() if k in CLAVES_PC}
    db.guardar_pc(validos)
    return {"ok": True, "guardado": sorted(validos)}


@app.get("/api/aprendizaje")
def aprendizaje(u: str = Depends(usuario)):
    return {"protocolo": db.leer_pc("protocolo", []), "sincronizacion": db.leer_pc("sincronizacion", {}),
            "ultima_sincronizacion": db.ultima_sincronizacion()}


# ---------------- Recordatorios y notificaciones ----------------
@app.get("/api/recordatorios")
def lista_recordatorios(u: str = Depends(usuario)):
    return db.recordatorios_pendientes()


@app.delete("/api/recordatorios/{rid}")
def borrar_recordatorio(rid: int, u: str = Depends(usuario)):
    db.borrar_recordatorio(rid)
    return {"ok": True}


@app.get("/api/push/clave")
def clave_push(u: str = Depends(usuario)):
    return {"clave": push.clave_publica()}


class Suscripcion(BaseModel):
    endpoint: str = Field(max_length=2000)
    keys: dict


@app.post("/api/push/suscribir")
def suscribir(s: Suscripcion, u: str = Depends(usuario)):
    if not s.endpoint.startswith("https://") or not {"p256dh", "auth"} <= set(s.keys):
        raise HTTPException(400, "suscripción inválida")
    db.guardar_suscripcion({"endpoint": s.endpoint, "keys": {k: s.keys[k] for k in ("p256dh", "auth")}})
    return {"ok": True}


@app.post("/api/push/probar")
def probar_push(u: str = Depends(usuario)):
    return {"enviadas": push.enviar("Axtra", "Las notificaciones funcionan, señor.")}


# ---------------- La app del celular ----------------
APP_DIR = config.BASE / "app_movil"
if APP_DIR.is_dir():
    app.mount("/", StaticFiles(directory=APP_DIR, html=True), name="app")
