"""Puerta pública de los orbes de negocios (api.axtra.chat). Contenedor aparte, sin Cloudflare Access y SIN
claves: el oído, el cerebro, la voz y los PIN los tiene Axtra (la tarjeta madre) y los presta por su ranura.

Para probar en tu PC:  APEX_MODO=desarrollo uvicorn servidor.apex.app:app --port 8081
"""
import asyncio
import base64
import hmac
import json
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


# ---------------- Vigilante: cierra conversaciones largas, quietas o de mesas cerradas ----------------
def revisar_sesiones():
    ahora = time.time()
    for s in db.sesiones_abiertas():
        r = config.restaurante(s["restaurante"])
        max_seg = (r["topes"]["minutos_por_sesion"] if r else 15) * 60
        motivo = None
        if ahora - (s["actividad"] or s["creada"]) > 300:
            motivo = "sin actividad"
        elif ahora - s["creada"] > max_seg:
            motivo = "tope de minutos por sesión"
        elif not (orbe.mesa_abierta(r, s["mesa"]) if r else db.mesa_abierta(s["restaurante"], s["mesa"])):
            motivo = "mesa cerrada"
        if motivo:
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
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type, X-Apex-Sesion, X-Apex-Secreto"
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
            "menu": [{k: p.get(k) for k in ("id", "nombre", "precio", "descripcion", "alergenos", "modelo3d", "foto",
                                              "grupo", "antes", "oferta")}
                     for p in r["menu"]]}


class PedidoSesion(BaseModel):
    restaurante: str = Field(max_length=60)
    mesa: str = Field(max_length=20)
    anterior: dict | None = None          # {sesion, secreto} para retomar desde el mismo teléfono


def _frases(r: dict) -> dict:
    return {k: f"/v1/frase/{r['id']}/{k}" for k in r["frases"]}


@app.post("/v1/sesion")
def crear_sesion(p: PedidoSesion, request: Request):
    r = _restaurante(p.restaurante)
    exigir_origen(request, r)
    limitar(f"sesion:{ip(request)}", 6, 60)
    limitar(f"sesion-mesa:{r['id']}:{p.mesa}", 4, 60)
    if p.mesa not in r.get("mesas", []):
        raise HTTPException(404, "mesa no existe")
    if not orbe.mesa_abierta(r, p.mesa):
        raise HTTPException(403, "mesa cerrada: pida al mesero que la abra")
    activa = db.sesion_activa(r["id"], p.mesa)
    if activa:
        propia = p.anterior and p.anterior.get("sesion") == activa["id"] and \
            hmac.compare_digest(str(p.anterior.get("secreto", "")), activa["secreto"])
        if not propia:
            raise HTTPException(409, "ya hay una conversación activa en esta mesa")
        db.terminar_sesion(activa["id"], "reemplazada")
    sid = uuid.uuid4().hex
    secreto = db.nueva_sesion(sid, r["id"], p.mesa)
    return {"sesion": sid, "secreto": secreto, "frases": _frases(r), "saludo": r["frases"]["saludo"],
            "sin_voz": db.gasto_mes(r["id"]) >= r["topes"]["tope_cop_mes"]}


class Credencial(BaseModel):
    sesion: str = Field(max_length=64)
    secreto: str = Field(max_length=64)


def _sesion(sid: str, secreto: str, request: Request, abierta: bool = True):
    s = db.sesion(sid or "")
    if not s or not hmac.compare_digest(str(secreto or ""), s["secreto"]):
        raise HTTPException(401, "sesión inválida")
    r = _restaurante(s["restaurante"])
    exigir_origen(request, r)
    if abierta and s["fin"]:
        raise HTTPException(410, f"la conversación terminó ({s['motivo_fin']})")
    return s, r


def _respuesta(r: dict, s, texto: str = "", frase: str = "", **extra) -> dict:
    """Lo que el orbe dirá: una frase grabada (gratis, por URL) o un audio nuevo (en base64)."""
    out = {"frase": None, "audio": None, "texto": r["frases"].get(frase, "") if frase else texto, **extra}
    if frase:
        out["frase"] = f"/v1/frase/{r['id']}/{frase}"
        return out
    try:
        out["audio"] = base64.b64encode(orbe.voz(r, texto, s["id"])).decode()
    except orbe.SinRanura:
        out.update(frase=f"/v1/frase/{r['id']}/sin_voz", sin_voz=True, texto=r["frases"]["sin_voz"])
    return out


def _puede_gastar(r: dict, s) -> bool:
    return db.gasto_mes(r["id"]) < r["topes"]["tope_cop_mes"] and s["turnos"] < r["topes"]["turnos_por_sesion"]


@app.post("/v1/turno")
async def turno(request: Request):
    """El cliente habló: oído → cerebro (con herramientas) → voz. Llega el audio crudo del teléfono."""
    s, r = _sesion(request.headers.get("x-apex-sesion"), request.headers.get("x-apex-secreto"), request)
    limitar(f"turno:{s['id']}", 20, 60)
    limitar(f"turno-ip:{ip(request)}", 40, 60)
    audio = await request.body()
    if not audio or len(audio) > 4_000_000:
        raise HTTPException(413, "audio vacío o demasiado largo")
    if not _puede_gastar(r, s):
        return _respuesta(r, s, frase="sin_voz", sin_voz=True)
    db.contar_turno(s["id"])
    try:
        texto = await asyncio.to_thread(orbe.oir, r, s["id"], audio)
        if len(texto.strip(" .,¿?¡!")) < 2:
            return _respuesta(r, s, frase="repetir")
        res = await asyncio.to_thread(orbe.conversar, r, s, {"role": "user", "content": texto[:600]})
    except orbe.SinRanura:
        return _respuesta(r, s, frase="sin_voz", sin_voz=True)
    return await asyncio.to_thread(_respuesta, r, s, res["texto"], "", despedida=bool(res["confirmado"]),
                                   pedido=res["pedido"] or res["confirmado"], oido=texto[:600])


class Accion(Credencial):
    tipo: str = Field(pattern="^(pedir|quitar|confirmar|pedir_todo|mesero)$")
    plato_id: str = Field("", max_length=60)
    cantidad: int = Field(1, ge=1, le=20)


def _anotar(r: dict, s, accion: str, frase: str):
    """Deja en la conversación lo que pasó en la pantalla, para que el cerebro lo sepa si el cliente luego habla."""
    db.guardar_historial(s["id"], db.historial(s["id"]) + [
        {"role": "user", "content": f"[Acción en la pantalla] {accion}"},
        {"role": "assistant", "content": r["frases"][frase]}])


def _ya_dijo(r: dict, s, frase: str) -> bool:
    texto = r["frases"].get(frase)
    return bool(texto) and any(m.get("role") == "assistant" and m.get("content") == texto for m in db.historial(s["id"]))


@app.post("/v1/accion")
def accion(a: Accion, request: Request):
    """Botones del menú: «Pedir», «Quitar», «Confirmar pedido», «Pedir todo» y «Llamar al mesero».
    Responden con frases grabadas: no gastan cerebro ni voz nueva."""
    s, r = _sesion(a.sesion, a.secreto, request)
    limitar(f"accion:{s['id']}", 40, 60)
    ventas = r.get("ventas") or {}
    if a.tipo == "mesero":
        orbe.ejecutar(r, s, "llamar_mesero", {"motivo": "tocó «Llamar al mesero»"})
        return _respuesta(r, s, frase="mesero")
    if a.tipo == "pedir":
        res = orbe.ejecutar(r, s, "agregar_plato", {"plato_id": a.plato_id, "cantidad": a.cantidad})
        if not res.get("ok"):
            raise HTTPException(409, res.get("error", "no se pudo agregar"))
        sug, ids = ventas.get("sugerir") or {}, {p["id"] for p in res["platos"]}
        frase = "eleccion"
        if a.plato_id in sug.get("si_pide", []) and sug.get("ofrecer") not in ids and "sugerir" in r["frases"] \
                and not _ya_dijo(r, s, "sugerir"):
            frase = "sugerir"
        _anotar(r, s, f"Tocó «Pedir» en {res['agregado']}.", frase)
        return _respuesta(r, s, frase=frase, pedido=res, sugerir=sug.get("ofrecer") if frase == "sugerir" else None)
    if a.tipo == "quitar":
        res = orbe.ejecutar(r, s, "quitar_plato", {"plato_id": a.plato_id, "cantidad": a.cantidad})
        frase = "quitado" if "quitado" in r["frases"] else "eleccion"
        _anotar(r, s, f"Quitó {a.plato_id} de su pedido.", frase)
        return _respuesta(r, s, frase=frase, pedido=res)
    if a.tipo == "confirmar":
        # «Confirmar pedido»: si no lleva la oferta del día, el orbe la ofrece una vez; después envía a la caja.
        if a.plato_id:                                   # «Sí, agregarlo» en la oferta
            orbe.ejecutar(r, s, "agregar_plato", {"plato_id": a.plato_id, "cantidad": 1})
        pedido = orbe.ejecutar(r, s, "ver_pedido", {})
        if not pedido["platos"]:
            return _respuesta(r, s, frase="vacio", pedido=pedido)
        oferta = ventas.get("oferta")
        if oferta and "oferta" in r["frases"] and oferta not in {p["id"] for p in pedido["platos"]} \
                and not _ya_dijo(r, s, "oferta"):
            _anotar(r, s, "Tocó «Confirmar pedido».", "oferta")
            return _respuesta(r, s, frase="oferta", pedido=pedido, oferta=oferta)
        res = orbe.ejecutar(r, s, "confirmar_pedido", {})
        if not res.get("ok"):
            raise HTTPException(409, res.get("error", "no se pudo enviar"))
        frase = "enviado" if "enviado" in r["frases"] else "despedida"
        _anotar(r, s, "Confirmó el pedido.", frase)
        return _respuesta(r, s, frase=frase, pedido=res, despedida=True)
    # pedir_todo: repetir el pedido y pedir confirmación por voz
    pedido = orbe.ejecutar(r, s, "ver_pedido", {})
    if not pedido["platos"]:
        return _respuesta(r, s, frase="vacio", pedido=pedido)
    if not _puede_gastar(r, s):
        return _respuesta(r, s, frase="sin_voz", sin_voz=True, pedido=pedido)
    db.contar_turno(s["id"])
    try:
        res = orbe.conversar(r, s, {"role": "user", "content": "[Acción en la pantalla] Tocó «Pedir todo lo seleccionado». "
                                    "Repite el pedido de forma breve (platos, cantidades y total) y pregunta si lo confirma."})
    except orbe.SinRanura:
        return _respuesta(r, s, frase="sin_voz", sin_voz=True, pedido=pedido)
    return _respuesta(r, s, res["texto"], pedido=res["pedido"] or pedido, despedida=bool(res["confirmado"]))


@app.get("/v1/frase/{rid}/{nombre}")
def frase(rid: str, nombre: str, request: Request):
    """Frases fijas del restaurante: se generan una vez y quedan guardadas (no vuelven a costar)."""
    r = _restaurante(rid)
    limitar(f"frase:{ip(request)}", 120, 60)
    if nombre not in r["frases"]:
        raise HTTPException(404, "frase no existe")
    try:
        audio = orbe.voz(r, r["frases"][nombre])
    except orbe.SinRanura:
        raise HTTPException(503, "voz no disponible")
    return Response(audio, media_type="audio/mpeg", headers={"Cache-Control": "public, max-age=3600"})


@app.post("/v1/sesion/fin")
async def terminar(request: Request):
    """Llega con sendBeacon (texto plano), por eso se lee el cuerpo a mano."""
    try:
        datos = json.loads(await request.body())
        c = Credencial(sesion=datos["sesion"], secreto=datos["secreto"])
    except Exception:
        raise HTTPException(400, "cuerpo inválido")
    s, _ = _sesion(c.sesion, c.secreto, request, abierta=False)
    db.terminar_sesion(s["id"], str(datos.get("motivo") or "terminó")[:40])
    return {"ok": True}


# ---------------- Panel del mesero (PIN) ----------------
def _panel(request: Request, rid: str) -> dict:
    r = _restaurante(rid)
    limitar(f"panel:{ip(request)}", 120, 60)
    dado = request.headers.get("x-apex-pin", "")[:20]
    fallos = _cubos[f"pin-mal:{ip(request)}"]
    if len([t for t in fallos if time.time() - t < 600]) >= 8:      # bloqueado ANTES de probar otro PIN
        raise HTTPException(429, "demasiados intentos, espere 10 minutos")
    try:
        bien = len(dado) >= 4 and orbe.pin_correcto(r["id"], dado)
    except orbe.SinRanura:
        raise HTTPException(503, "Axtra no responde o el restaurante no tiene PIN (APEX_PIN_... en el .env de Axtra)")
    if not bien:
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


@app.get("/qr")
def qr():
    return FileResponse(WEB / "qr.html")


@app.get("/v1/mesas/{rid}")
def mesas_publicas(rid: str, request: Request):
    """Para la página de códigos QR: nombre y mesas del restaurante (nada privado)."""
    limitar(f"menu:{ip(request)}", 60, 60)
    r = _restaurante(rid)
    return {"id": r["id"], "nombre": r["nombre"], "mesas": r.get("mesas", [])}


@app.get("/panel")
def panel():
    return FileResponse(WEB / "panel.html")


app.mount("/web", StaticFiles(directory=WEB), name="web")


@app.exception_handler(HTTPException)
async def errores(request: Request, e: HTTPException):
    return JSONResponse({"error": e.detail}, status_code=e.status_code, headers=getattr(e, "headers", None))
