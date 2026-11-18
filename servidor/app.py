"""API de Axtra en la nube. La usa la app del celular.

Para probar en tu PC:  AXTRA_MODO=desarrollo uvicorn servidor.app:app --reload
En el servidor:        uvicorn servidor.app:app --host 0.0.0.0 --port 8080   (detrás de Cloudflare Access)
"""
import os
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
    if os.getenv("CONTENIDO_AGENTE", "1") == "1":
        from . import contenido
        contenido.iniciar_vigilante()   # arma y publica los videos aprobados a su hora
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


# ---------------- Negocios: los orbes que mueve Axtra (tarjeta madre) ----------------
@app.get("/api/negocios")
def negocios(u: str = Depends(usuario)):
    from .apex import config as apex_config, db as apex_db

    out = []
    for r in apex_config.restaurantes().values():
        abiertas = apex_db.mesas(r["id"])
        out.append({"id": r["id"], "nombre": r["nombre"], "uso": apex_db.uso_mes(r["id"]),
                    "tope_cop": r["topes"]["tope_cop_mes"], "mesas": len(r.get("mesas", [])),
                    "mesas_abiertas": sum(1 for m in r.get("mesas", []) if abiertas.get(m)),
                    "llamadas": len(apex_db.llamadas(r["id"]))})
    return out


# ---------------- Escáner de prospectos de Apex (solo con la sesión de Felipe) ----------------
class Escaneo(BaseModel):
    ciudad: str = Field(min_length=2, max_length=80)
    pais: str = Field("Colombia", min_length=2, max_length=60)


class Seguimiento(BaseModel):
    estado: str | None = Field(None, max_length=20)
    notas: str | None = Field(None, max_length=4000)
    siguiente: str | None = Field(None, max_length=20)


@app.post("/api/prospectos/escanear")
def prospectos_escanear(e: Escaneo, u: str = Depends(usuario)):
    from . import prospectos
    try:
        return {"escaneo": prospectos.escanear_en_fondo(e.ciudad.strip(), e.pais.strip())}
    except RuntimeError as err:
        raise HTTPException(409, str(err))


@app.get("/api/prospectos/escaneos")
def prospectos_escaneos(u: str = Depends(usuario)):
    from . import prospectos
    return prospectos.escaneos()


@app.get("/api/prospectos/opciones")
def prospectos_opciones(u: str = Depends(usuario)):
    from . import prospectos
    return prospectos.opciones()


def _filtros(request: Request) -> dict:
    q = request.query_params
    return {"pais": q.get("pais", ""), "ciudad": q.get("ciudad", ""), "nicho": q.get("nicho", ""), "tipo": q.get("tipo", ""),
            "flujo": q.get("flujo", ""), "estado": q.get("estado", ""), "texto": q.get("texto", "")[:80],
            "minimo": int(q.get("minimo") or 0) if (q.get("minimo") or "0").isdigit() else 0, "contacto": q.get("contacto") == "1"}


@app.get("/api/prospectos")
def prospectos_lista(request: Request, u: str = Depends(usuario)):
    from . import prospectos
    return prospectos.buscar(**_filtros(request))


@app.get("/api/prospectos.csv")
def prospectos_csv(request: Request, u: str = Depends(usuario)):
    import csv, io
    from . import prospectos
    campos = ["puntaje", "nombre", "ciudad", "pais", "nicho", "tipo", "flujo", "turismo", "telefono", "web", "instagram", "email",
              "direccion", "horario", "razon_social", "nit", "renovado", "confianza", "estado", "siguiente", "notas", "lat", "lon"]
    b = io.StringIO(); w = csv.DictWriter(b, fieldnames=campos, extrasaction="ignore"); w.writeheader()
    for f in prospectos.buscar(**_filtros(request), limite=20000):
        w.writerow(f)
    return Response("\ufeff" + b.getvalue(), media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": 'attachment; filename="prospectos-apex.csv"'})


@app.patch("/api/prospectos/{pid}")
def prospectos_seguimiento(pid: str, s: Seguimiento, u: str = Depends(usuario)):
    from . import prospectos
    try:
        return prospectos.seguimiento(pid, s.estado, s.notas, s.siguiente)
    except ValueError as e:
        raise HTTPException(422, str(e))
    except KeyError:
        raise HTTPException(404, "no existe")


# ---------------- Agente de contenido (TikTok e Instagram), solo con la sesión de Felipe ----------------
class CambioPieza(BaseModel):
    estado: str | None = Field(None, max_length=20)
    gancho: str | None = Field(None, max_length=70)
    titulo: str | None = Field(None, max_length=80)
    descripcion: str | None = Field(None, max_length=1500)
    hashtags: list[str] | None = None
    escenas: list[dict] | None = None
    hora: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$")   # hora de Colombia


def _hilo(fn, *args):
    import threading
    threading.Thread(target=fn, args=args, daemon=True).start()


@app.get("/api/contenido")
def contenido_lista(u: str = Depends(usuario)):
    import time as _t
    from . import contenido
    contenido.sembrar()
    return {"piezas": contenido.piezas(desde=_t.time() - 3 * 86400), "instagram": contenido.instagram_listo(),
            "tiktok": contenido.tiktok_listo(), "tiktok_app": bool(os.getenv("TIKTOK_CLIENT_KEY"))}


@app.patch("/api/contenido/{pid}")
def contenido_cambiar(pid: int, c: CambioPieza, u: str = Depends(usuario)):
    import datetime as _dt
    from . import contenido
    campos = {k: v for k, v in c.model_dump().items() if v is not None and k != "hora"}
    if c.hora:
        campos["cuando"] = _dt.datetime.strptime(c.hora, "%Y-%m-%d %H:%M").replace(tzinfo=contenido.COLOMBIA).timestamp()
    try:
        return contenido.actualizar(pid, **campos)
    except KeyError:
        raise HTTPException(404, "no existe")
    except ValueError as e:
        raise HTTPException(422, str(e))


@app.post("/api/contenido/{pid}/video")
def contenido_video(pid: int, u: str = Depends(usuario)):
    from . import contenido
    try:
        contenido.pieza(pid)
    except KeyError:
        raise HTTPException(404, "no existe")
    contenido.actualizar(pid, error="armando el video…")

    def armar():
        try:
            contenido.armar_video(pid)
        except Exception as e:
            contenido.actualizar(pid, error=f"no se pudo armar el video: {e}"[:400])
    _hilo(armar)
    return {"ok": True}


@app.get("/api/contenido/{pid}/video")
def contenido_ver_video(pid: int, u: str = Depends(usuario)):
    from . import contenido
    try:
        p = contenido.pieza(pid)
    except KeyError:
        raise HTTPException(404, "no existe")
    f = contenido.carpeta_videos() / (p["video"] or "_")
    if not p["video"] or not f.exists():
        raise HTTPException(404, "todavía no tiene video")
    return FileResponse(f, media_type="video/mp4")


@app.post("/api/contenido/{pid}/publicar")
def contenido_publicar(pid: int, u: str = Depends(usuario)):
    from . import contenido
    try:
        if contenido.pieza(pid)["estado"] != "aprobada":
            contenido.actualizar(pid, estado="aprobada")
    except KeyError:
        raise HTTPException(404, "no existe")
    _hilo(contenido.publicar, pid)
    return {"ok": True}


@app.post("/api/contenido/proponer")
def contenido_proponer(u: str = Depends(usuario)):
    from . import contenido
    try:
        return {"nuevas": contenido.proponer(7, enrutador())}
    except Exception as e:
        raise HTTPException(502, f"no se pudieron proponer ideas: {e}")


TIKTOK_VUELTA = os.getenv("TIKTOK_REDIRECT", "https://axtra.chat/api/contenido/tiktok/vuelta")


@app.get("/api/contenido/tiktok/conectar")
def tiktok_conectar(u: str = Depends(usuario)):
    import secrets as _s
    from urllib.parse import urlencode
    from fastapi.responses import RedirectResponse
    from . import contenido
    if not os.getenv("TIKTOK_CLIENT_KEY"):
        raise HTTPException(503, "falta TIKTOK_CLIENT_KEY en el .env del servidor")
    estado = contenido.ajuste("tiktok_estado_oauth", _s.token_urlsafe(16))
    return RedirectResponse("https://www.tiktok.com/v2/auth/authorize/?" + urlencode({
        "client_key": os.getenv("TIKTOK_CLIENT_KEY"), "scope": "user.info.basic,video.upload", "response_type": "code",
        "redirect_uri": TIKTOK_VUELTA, "state": estado}))


@app.get("/api/contenido/tiktok/vuelta")
def tiktok_vuelta(code: str = "", state: str = "", u: str = Depends(usuario)):
    import hmac as _h
    from fastapi.responses import RedirectResponse
    from . import contenido
    if not code or not state or not _h.compare_digest(state, contenido.ajuste("tiktok_estado_oauth") or "-"):
        raise HTTPException(400, "la conexión con TikTok no es válida; intente de nuevo")
    try:
        contenido.tiktok_conectar(code, TIKTOK_VUELTA)
    except RuntimeError as e:
        raise HTTPException(502, str(e))
    return RedirectResponse("/contenido.html?tiktok=ok")


# ---------------- La app del celular ----------------
APP_DIR = config.BASE / "app_movil"
if APP_DIR.is_dir():
    app.mount("/", StaticFiles(directory=APP_DIR, html=True), name="app")
