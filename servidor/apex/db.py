"""Base de datos de los orbes (SQLite). Todo va separado por restaurante.
Axtra (la tarjeta madre) la lee para su pantalla «Negocios»."""
import json
import secrets
import sqlite3
import threading
import time
from datetime import datetime

from . import config

_lock = threading.Lock()
_conn = None


def conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(config.DATA_DIR / "orbes.db", check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.executescript("""
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS mesas (restaurante TEXT, mesa TEXT, abierta INTEGER DEFAULT 0,
                                              cambiada REAL, PRIMARY KEY (restaurante, mesa));
            CREATE TABLE IF NOT EXISTS sesiones (id TEXT PRIMARY KEY, secreto TEXT, restaurante TEXT, mesa TEXT,
                                                 creada REAL, actividad REAL, fin REAL, motivo_fin TEXT,
                                                 turnos INTEGER DEFAULT 0, historial TEXT DEFAULT '[]',
                                                 carrito TEXT DEFAULT '[]');
            CREATE INDEX IF NOT EXISTS sesiones_mesa ON sesiones (restaurante, mesa, fin);
            CREATE INDEX IF NOT EXISTS sesiones_mes ON sesiones (restaurante, creada);
            CREATE TABLE IF NOT EXISTS consumos (id INTEGER PRIMARY KEY AUTOINCREMENT, restaurante TEXT,
                                                 sesion TEXT, pieza TEXT, proveedor TEXT, cantidad REAL,
                                                 cop REAL, creado REAL);
            CREATE INDEX IF NOT EXISTS consumos_mes ON consumos (restaurante, creado);
            CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY AUTOINCREMENT, restaurante TEXT, mesa TEXT,
                                                sesion TEXT, items TEXT, total REAL, estado TEXT DEFAULT 'nuevo',
                                                creado REAL);
            CREATE TABLE IF NOT EXISTS llamadas (id INTEGER PRIMARY KEY AUTOINCREMENT, restaurante TEXT, mesa TEXT,
                                                 motivo TEXT, atendida INTEGER DEFAULT 0, creada REAL);
        """)
    return _conn


def inicio_mes() -> float:
    hoy = datetime.now()
    return datetime(hoy.year, hoy.month, 1).timestamp()


def _ejecutar(sql: str, args=()):
    with _lock:
        c = conn().execute(sql, args)
        conn().commit()
        return c


# ---------------- Mesas ----------------
def mesa_abierta(rid: str, mesa: str) -> bool:
    f = conn().execute("SELECT abierta FROM mesas WHERE restaurante=? AND mesa=?", (rid, mesa)).fetchone()
    return bool(f and f["abierta"])


def cambiar_mesa(rid: str, mesa: str, abierta: bool):
    _ejecutar("INSERT INTO mesas VALUES (?,?,?,?) ON CONFLICT(restaurante, mesa) DO UPDATE SET "
              "abierta=excluded.abierta, cambiada=excluded.cambiada", (rid, mesa, int(abierta), time.time()))
    if not abierta:   # al cerrar la mesa se corta su conversación
        _ejecutar("UPDATE sesiones SET fin=?, motivo_fin='mesa cerrada' WHERE restaurante=? AND mesa=? AND fin IS NULL",
                  (time.time(), rid, mesa))


def mesas(rid: str) -> dict:
    return {f["mesa"]: bool(f["abierta"])
            for f in conn().execute("SELECT mesa, abierta FROM mesas WHERE restaurante=?", (rid,))}


# ---------------- Sesiones ----------------
def sesion_activa(rid: str, mesa: str):
    return conn().execute("SELECT * FROM sesiones WHERE restaurante=? AND mesa=? AND fin IS NULL "
                          "ORDER BY creada DESC LIMIT 1", (rid, mesa)).fetchone()


def nueva_sesion(sid: str, rid: str, mesa: str) -> str:
    secreto, ahora = secrets.token_urlsafe(24), time.time()
    _ejecutar("INSERT INTO sesiones (id, secreto, restaurante, mesa, creada, actividad) VALUES (?,?,?,?,?,?)",
              (sid, secreto, rid, mesa, ahora, ahora))
    return secreto


def sesion(sid: str):
    return conn().execute("SELECT * FROM sesiones WHERE id=?", (sid,)).fetchone()


def terminar_sesion(sid: str, motivo: str):
    _ejecutar("UPDATE sesiones SET fin=COALESCE(fin, ?), motivo_fin=COALESCE(motivo_fin, ?) WHERE id=?",
              (time.time(), motivo, sid))


def sesiones_abiertas():
    return conn().execute("SELECT * FROM sesiones WHERE fin IS NULL").fetchall()


def contar_turno(sid: str):
    _ejecutar("UPDATE sesiones SET turnos=turnos+1, actividad=? WHERE id=?", (time.time(), sid))


def historial(sid: str) -> list:
    f = sesion(sid)
    return json.loads(f["historial"]) if f else []


def guardar_historial(sid: str, mensajes: list):
    # Se recorta empezando en un mensaje del cliente, para no partir una llamada a herramienta de su respuesta.
    if len(mensajes) > 24:
        corte = next((i for i in range(len(mensajes) - 24, len(mensajes)) if mensajes[i].get("role") == "user"), 0)
        mensajes = mensajes[corte:]
    _ejecutar("UPDATE sesiones SET historial=?, actividad=? WHERE id=?",
              (json.dumps(mensajes, ensure_ascii=False), time.time(), sid))


def carrito(sid: str) -> list:
    f = sesion(sid)
    return json.loads(f["carrito"]) if f else []


def guardar_carrito(sid: str, items: list):
    _ejecutar("UPDATE sesiones SET carrito=? WHERE id=?", (json.dumps(items, ensure_ascii=False), sid))


# ---------------- Consumo y costo en pesos ----------------
def consumo(rid: str, sid: str, pieza: str, proveedor: str, cantidad: float, cop: float):
    _ejecutar("INSERT INTO consumos (restaurante, sesion, pieza, proveedor, cantidad, cop, creado) "
              "VALUES (?,?,?,?,?,?,?)", (rid, sid, pieza, proveedor, cantidad, cop, time.time()))


def gasto_mes(rid: str) -> float:
    f = conn().execute("SELECT COALESCE(SUM(cop), 0) cop FROM consumos WHERE restaurante=? AND creado>=?",
                       (rid, inicio_mes())).fetchone()
    return round(f["cop"], 2)


def uso_mes(rid: str) -> dict:
    ini = inicio_mes()
    s = conn().execute("SELECT COUNT(*) n, COALESCE(SUM(turnos), 0) t FROM sesiones WHERE restaurante=? AND creada>=?",
                       (rid, ini)).fetchone()
    p = conn().execute("SELECT COUNT(*) n, COALESCE(SUM(total), 0) v FROM pedidos WHERE restaurante=? AND creado>=? "
                       "AND estado!='cancelado'", (rid, ini)).fetchone()
    piezas = {f["pieza"]: round(f["cop"], 2) for f in conn().execute(
        "SELECT pieza, SUM(cop) cop FROM consumos WHERE restaurante=? AND creado>=? GROUP BY pieza", (rid, ini))}
    return {"conversaciones": s["n"], "turnos": s["t"], "pedidos": p["n"], "ventas": p["v"],
            "gasto_cop": gasto_mes(rid), "gasto_por_pieza": piezas}


# ---------------- Pedidos y llamadas al mesero ----------------
def nuevo_pedido(rid: str, mesa: str, sid: str, items: list, total: float) -> int:
    return _ejecutar("INSERT INTO pedidos (restaurante, mesa, sesion, items, total, creado) VALUES (?,?,?,?,?,?)",
                     (rid, mesa, sid, json.dumps(items, ensure_ascii=False), total, time.time())).lastrowid


def pedidos(rid: str, limite: int = 50) -> list:
    return [dict(f) | {"items": json.loads(f["items"])} for f in conn().execute(
        "SELECT * FROM pedidos WHERE restaurante=? ORDER BY id DESC LIMIT ?", (rid, limite))]


def cambiar_pedido(rid: str, pid: int, estado: str):
    _ejecutar("UPDATE pedidos SET estado=? WHERE restaurante=? AND id=?", (estado, rid, pid))


def llamar_mesero(rid: str, mesa: str, motivo: str):
    _ejecutar("INSERT INTO llamadas (restaurante, mesa, motivo, creada) VALUES (?,?,?,?)",
              (rid, mesa, motivo, time.time()))


def llamadas(rid: str) -> list:
    return [dict(f) for f in conn().execute(
        "SELECT * FROM llamadas WHERE restaurante=? AND atendida=0 ORDER BY id DESC LIMIT 30", (rid,))]


def atender_llamada(rid: str, lid: int):
    _ejecutar("UPDATE llamadas SET atendida=1 WHERE restaurante=? AND id=?", (rid, lid))
