"""Puerta pública de Apex Play (api.axtra.chat). Contenedor aparte de Axtra, sin Cloudflare Access.

Para probar en tu PC:  APEX_MODO=desarrollo uvicorn servidor.apex.app:app --port 8081
"""
import hmac
import re
import threading
import time
import uuid
from collections import defaultdict, deque
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import config, db, orbe

WEB = config.BASE / "web"


# ---------------- Vigilante: corta sesiones largas, abandonadas o de mesas cerradas ----------------
def revisar_sesiones():
    ahora = time.time()
    for s in db.sesiones_abiertas():
        r = config.restaurante(s["restaurante"])
        max_seg = (r["topes"]["minutos_por_sesion"] if r else 8) * 60
        motivo = None
        if not s["call_id"] and ahora - s["creada"] > 90:
            motivo = "no conectó"
        elif ahora - s["creada"] > max_seg:
            motivo = "tope de minutos por sesión"
        elif not db.mesa_abierta(s["restaurante"], s["mesa"]):
            motivo = "mesa cerrada"
        if motivo:
            if s["call_id"]:
                orbe.colgar(s["call_id"])
            db.terminar_sesion(s["id"], motivo)


def _vigilante():
    while True:
        try:
            revisar_sesiones()
        except Exception:
            pass
        time.sleep(15)


@asynccontextmanager
async def _vida(app):
    threading.Thread(target=_vigilante, daemon=True).start()
    yield


app = FastAPI(title="Apex Play", docs_url=None, redoc_url=None, openapi_url=None, lifespan=_vida)


# ---------------- Orígenes permitidos (CORS) ----------------
def origenes(r: dict) -> set:
    o = {d.rstrip("/").lower() for d in r.get("dominios", [])}
    if config.MODO_DESARROLLO:
        o |= {"http://localhost:8081", "http://127.0.0.1:8081"}
    return o


def todos_los_origenes() -> set:
    out = set()
    for r in config.restaurantes().values():
        out |= origenes(r)
    return out


@app.middleware("http")
async def cors(request: Request, call_next):
    origen = (request.headers.get("origin") or "").rstrip("/").lower()
    permitido = origen and origen in todos_los_origenes()
    if request.method == "OPTIONS" and request.url.path.startswith("/v1/"):
        resp = Response(status_code=204 if permitido else 403)
    else:
        resp = await call_next(request)
    if permitido:
        resp.headers["Access-Control-Allow-Origin"] = origen
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        resp.headers["Access-Control-Max-Age"] = "600"
    resp.headers["Vary"] = "Origin"
    return resp


def exigir_origen(request: Request, r: dict):
    origen = (request.headers.get("origin") or "").rstrip("/").lower()
    if origen not in origenes(r):
        raise HTTPException(403, "origen no permitido para este restaurante")


# ---------------- Límite de peticiones ----------------
_cubos = defaultdict(deque)
_cubos_lock = threading.Lock()


def ip(request: Request) -> str:
    return request.headers.get("cf-connecting-ip") or (request.client.host if request.client else "?")


def limitar(clave: str, maximo: int, ventana: float):
    ahora = time.time()
    with _cubos_lock:
        q = _cubos[clave]
        while q and ahora - q[0] > ventana:
            q.popleft()
        if len(q) >= maximo:
            raise HTTPException(429, "demasiadas peticiones, espere un momento")
        q.append(ahora)


# ---------------- Público: menú y sesión del orbe ----------------
def _restaurante(rid: str) -> dict:
    r = config.restaurante(rid)
    if not r:
        raise HTTPException(404, "restaurante no existe")
    return r


@app.get("/salud")
def salud():
    return {"ok": True}


@app.get("/v1/menu/{rid}")
def menu(rid: str, request: Request):
    limitar(f"menu:{ip(request)}", 60, 60)
    r = _restaurante(rid)
    return {"id": r["id"], "nombre": r["nombre"], "moneda": r.get("moneda", "COP"),
            "menu": [{k: p.get(k) for k in ("id", "nombre", "precio", "descripcion", "alergenos", "modelo3d", "foto")}
                     for p in r["menu"]]}


class PedidoSesion(BaseModel):
    restaurante: str = Field(max_length=60)
    mesa: str = Field(max_length=20)
    anterior: dict | None = None          # {sesion, secreto} para retomar desde el mismo teléfono


@app.post("/v1/sesion")
def crear_sesion(p: PedidoSesion, request: Request):
    r = _restaurante(p.restaurante)
    exigir_origen(request, r)
    limitar(f"sesion:{ip(request)}", 6, 60)
    limitar(f"sesion-mesa:{r['id']}:{p.mesa}", 4, 60)
    if p.mesa not in r.get("mesas", []):
        raise HTTPException(404, "mesa no existe")
    if not db.mesa_abierta(r["id"], p.mesa):
        raise HTTPException(403, "mesa cerrada: pida al mesero que la abra")
    activa = db.sesion_activa(r["id"], p.mesa)
    if activa:
        propia = p.anterior and p.anterior.get("sesion") == activa["id"] and \
            hmac.compare_digest(str(p.anterior.get("secreto", "")), activa["secreto"])
        if not propia:
            raise HTTPException(409, "ya hay una conversación activa en esta mesa")
        if activa["call_id"]:
            orbe.colgar(activa["call_id"])
        db.terminar_sesion(activa["id"], "reemplazada")
    uso, topes = db.uso_mes(r["id"]), r["topes"]
    if uso["sesiones"] >= topes["sesiones_mes"] or uso["minutos"] >= topes["minutos_mes"] or uso["usd"] >= topes["usd_mes"]:
        raise HTTPException(429, "el orbe alcanzó su límite del mes; un mesero lo atenderá")
    try:
        t = orbe.crear_token(r, p.mesa)
    except Exception as e:
        raise HTTPException(502, f"no se pudo iniciar la voz ({e})")
    sid = uuid.uuid4().hex
    secreto = db.nueva_sesion(sid, r["id"], p.mesa, r["modelo"])
    return {"sesion": sid, "secreto": secreto, "token": t["token"], "expira": t["expira"], "modelo": r["modelo"],
            "max_segundos": topes["minutos_por_sesion"] * 60,
            "frases": {k: r[k] for k in ("saludo", "eleccion", "despedida")}}


class Credencial(BaseModel):
    sesion: str = Field(max_length=64)
    secreto: str = Field(max_length=64)


def _sesion(c: Credencial, request: Request, abierta: bool = True):
    s = db.sesion(c.sesion)
    if not s or not hmac.compare_digest(c.secreto, s["secreto"]):
        raise HTTPException(401, "sesión inválida")
    r = _restaurante(s["restaurante"])
    exigir_origen(request, r)
    if abierta and s["fin"]:
        raise HTTPException(410, f"la conversación terminó ({s['motivo_fin']})")
    return s, r


class Llamada(Credencial):
    call_id: str = Field(max_length=120)


@app.post("/v1/sesion/llamada")
def registrar_llamada(c: Llamada, request: Request):
    s, _ = _sesion(c, request)
    if not re.fullmatch(r"[A-Za-z0-9_\-]{4,120}", c.call_id):
        raise HTTPException(400, "call_id inválido")
    db.poner_call_id(s["id"], c.call_id)
    return {"ok": True}


class Herramienta(Credencial):
    nombre: str = Field(max_length=40)
    argumentos: dict | str | None = None


@app.post("/v1/herramienta")
def herramienta(h: Herramienta, request: Request):
    limitar(f"herr:{ip(request)}", 60, 60)
    s, r = _sesion(h, request)
    return orbe.ejecutar(r, s, h.nombre, orbe.argumentos(h.argumentos))


TOPE_TOKENS = 2_000_000


@app.post("/v1/sesion/fin")
async def terminar(request: Request):
    """Llega con sendBeacon (texto plano), por eso se lee el cuerpo a mano."""
    import json

    try:
        datos = json.loads(await request.body())
        c = Credencial(sesion=datos["sesion"], secreto=datos["secreto"])
    except Exception:
        raise HTTPException(400, "cuerpo inválido")
    s, _ = _sesion(c, request, abierta=False)
    bruto = datos.get("uso") if isinstance(datos.get("uso"), dict) else {}
    uso = {k: max(0, min(TOPE_TOKENS, int(bruto.get(k, 0) or 0))) for k in
           ("audio_in", "audio_in_cache", "audio_out", "texto_in", "texto_in_cache", "texto_out")}
    if s["call_id"] and not s["fin"]:
        orbe.colgar(s["call_id"])
    db.terminar_sesion(s["id"], "terminó", uso, orbe.costo(s["modelo"], uso))
    return {"ok": True}


# ---------------- Panel del mesero (PIN) ----------------
def _panel(request: Request, rid: str) -> dict:
    r = _restaurante(rid)
    limitar(f"panel:{ip(request)}", 120, 60)
    esperado = config.pin(r)
    dado = request.headers.get("x-apex-pin", "")
    if len(esperado) < 4:
        raise HTTPException(503, "panel sin PIN configurado (APEX_PIN_... en apex.env)")
    if not hmac.compare_digest(dado.encode(), esperado.encode()):
        limitar(f"pin-mal:{ip(request)}", 8, 600)
        raise HTTPException(401, "PIN incorrecto")
    return r


@app.get("/v1/panel/{rid}")
def panel_estado(rid: str, request: Request):
    r = _panel(request, rid)
    abiertas = db.mesas(rid)
    activas = {s["mesa"] for s in db.sesiones_abiertas() if s["restaurante"] == rid}
    return {"restaurante": r["nombre"], "moneda": r.get("moneda", "COP"),
            "mesas": [{"mesa": m, "abierta": abiertas.get(m, False), "hablando": m in activas} for m in r["mesas"]],
            "pedidos": db.pedidos(rid), "llamadas": db.llamadas(rid),
            "uso_mes": db.uso_mes(rid), "topes": r["topes"]}


class CambioMesa(BaseModel):
    mesa: str = Field(max_length=20)
    abierta: bool


@app.post("/v1/panel/{rid}/mesa")
def panel_mesa(rid: str, c: CambioMesa, request: Request):
    r = _panel(request, rid)
    if c.mesa not in r["mesas"]:
        raise HTTPException(404, "mesa no existe")
    if not c.abierta:
        s = db.sesion_activa(rid, c.mesa)
        if s and s["call_id"]:
            orbe.colgar(s["call_id"])
    db.cambiar_mesa(rid, c.mesa, c.abierta)
    return {"ok": True}


class CambioPedido(BaseModel):
    estado: str = Field(pattern="^(nuevo|preparando|entregado|cancelado)$")


@app.post("/v1/panel/{rid}/pedido/{pid}")
def panel_pedido(rid: str, pid: int, c: CambioPedido, request: Request):
    _panel(request, rid)
    db.cambiar_pedido(rid, pid, c.estado)
    return {"ok": True}


@app.post("/v1/panel/{rid}/llamada/{lid}")
def panel_llamada(rid: str, lid: int, request: Request):
    _panel(request, rid)
    db.atender_llamada(rid, lid)
    return {"ok": True}


# ---------------- Páginas: demo del menú y panel ----------------
@app.get("/")
def inicio():
    return RedirectResponse("/demo?r=demo&mesa=1")


@app.get("/demo")
def demo():
    return FileResponse(WEB / "index.html")


@app.get("/panel")
def panel():
    return FileResponse(WEB / "panel.html")


app.mount("/web", StaticFiles(directory=WEB), name="web")


@app.exception_handler(HTTPException)
async def errores(request: Request, e: HTTPException):
    return JSONResponse({"error": e.detail}, status_code=e.status_code, headers=getattr(e, "headers", None))
