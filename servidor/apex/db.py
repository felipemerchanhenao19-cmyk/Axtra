"""Base de datos de Apex Play (SQLite, separada de la de Axtra). Todo va por restaurante."""
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
        _conn = sqlite3.connect(config.DATA_DIR / "apex.db", check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.executescript("""
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS mesas (restaurante TEXT, mesa TEXT, abierta INTEGER DEFAULT 0,
                                              cambiada REAL, PRIMARY KEY (restaurante, mesa));
            CREATE TABLE IF NOT EXISTS sesiones (id TEXT PRIMARY KEY, secreto TEXT, restaurante TEXT, mesa TEXT,
                                                 modelo TEXT, creada REAL, call_id TEXT, fin REAL,
                                                 motivo_fin TEXT, uso TEXT, usd REAL DEFAULT 0,
                                                 carrito TEXT DEFAULT '[]');
            CREATE INDEX IF NOT EXISTS sesiones_mesa ON sesiones (restaurante, mesa, fin);
            CREATE INDEX IF NOT EXISTS sesiones_mes ON sesiones (restaurante, creada);
            CREATE TABLE IF NOT EXISTS pedidos (id INTEGER PRIMARY KEY AUTOINCREMENT, restaurante TEXT, mesa TEXT,
                                                sesion TEXT, items TEXT, total REAL, estado TEXT DEFAULT 'nuevo',
                                                creado REAL);
            CREATE TABLE IF NOT EXISTS llamadas (id INTEGER PRIMARY KEY AUTOINCREMENT, restaurante TEXT, mesa TEXT,
                                                 motivo TEXT, atendida INTEGER DEFAULT 0, creada REAL);
        """)
    return _conn


def _inicio_mes() -> float:
    hoy = datetime.now()
    return datetime(hoy.year, hoy.month, 1).timestamp()


# ---------------- Mesas ----------------
def mesa_abierta(rid: str, mesa: str) -> bool:
    f = conn().execute("SELECT abierta FROM mesas WHERE restaurante=? AND mesa=?", (rid, mesa)).fetchone()
    return bool(f and f["abierta"])


def cambiar_mesa(rid: str, mesa: str, abierta: bool):
    with _lock:
        conn().execute("INSERT INTO mesas VALUES (?,?,?,?) ON CONFLICT(restaurante, mesa) DO UPDATE SET "
                       "abierta=excluded.abierta, cambiada=excluded.cambiada", (rid, mesa, int(abierta), time.time()))
        if not abierta:   # al cerrar la mesa se corta su sesión
            conn().execute("UPDATE sesiones SET fin=?, motivo_fin='mesa cerrada' WHERE restaurante=? AND mesa=? "
                           "AND fin IS NULL", (time.time(), rid, mesa))
        conn().commit()


def mesas(rid: str) -> dict:
    return {f["mesa"]: bool(f["abierta"])
            for f in conn().execute("SELECT mesa, abierta FROM mesas WHERE restaurante=?", (rid,))}


# ---------------- Sesiones ----------------
def sesion_activa(rid: str, mesa: str):
    return conn().execute("SELECT * FROM sesiones WHERE restaurante=? AND mesa=? AND fin IS NULL "
                          "ORDER BY creada DESC LIMIT 1", (rid, mesa)).fetchone()


def nueva_sesion(sid: str, rid: str, mesa: str, modelo: str) -> str:
    secreto = secrets.token_urlsafe(24)
    with _lock:
        conn().execute("INSERT INTO sesiones (id, secreto, restaurante, mesa, modelo, creada) VALUES (?,?,?,?,?,?)",
                       (sid, secreto, rid, mesa, modelo, time.time()))
        conn().commit()
    return secreto


def sesion(sid: str):
    return conn().execute("SELECT * FROM sesiones WHERE id=?", (sid,)).fetchone()


def poner_call_id(sid: str, call_id: str):
    with _lock:
        conn().execute("UPDATE sesiones SET call_id=? WHERE id=? AND call_id IS NULL", (call_id, sid))
        conn().commit()


def terminar_sesion(sid: str, motivo: str, uso: dict = None, usd: float = 0.0):
    with _lock:
        conn().execute("UPDATE sesiones SET fin=COALESCE(fin, ?), motivo_fin=COALESCE(motivo_fin, ?), "
                       "uso=COALESCE(?, uso), usd=MAX(usd, ?) WHERE id=?",
                       (time.time(), motivo, json.dumps(uso) if uso else None, usd, sid))
        conn().commit()


def sesiones_abiertas():
    return conn().execute("SELECT * FROM sesiones WHERE fin IS NULL").fetchall()


def carrito(sid: str) -> list:
    f = sesion(sid)
    return json.loads(f["carrito"]) if f else []


def guardar_carrito(sid: str, items: list):
    with _lock:
        conn().execute("UPDATE sesiones SET carrito=? WHERE id=?", (json.dumps(items, ensure_ascii=False), sid))
        conn().commit()


def uso_mes(rid: str) -> dict:
    """Sesiones, minutos y dólares (estimados) del mes en curso para un restaurante."""
    ahora, inicio = time.time(), _inicio_mes()
    f = conn().execute("SELECT COUNT(*) n, COALESCE(SUM(COALESCE(fin, ?) - creada), 0) seg, COALESCE(SUM(usd), 0) usd "
                       "FROM sesiones WHERE restaurante=? AND creada>=?", (ahora, rid, inicio)).fetchone()
    return {"sesiones": f["n"], "minutos": round(f["seg"] / 60, 1), "usd": round(f["usd"], 4)}


# ---------------- Pedidos y llamadas al mesero ----------------
def nuevo_pedido(rid: str, mesa: str, sid: str, items: list, total: float) -> int:
    with _lock:
        c = conn().execute("INSERT INTO pedidos (restaurante, mesa, sesion, items, total, creado) VALUES (?,?,?,?,?,?)",
                           (rid, mesa, sid, json.dumps(items, ensure_ascii=False), total, time.time()))
        conn().commit()
        return c.lastrowid


def pedidos(rid: str, limite: int = 50) -> list:
    return [dict(f) | {"items": json.loads(f["items"])} for f in conn().execute(
        "SELECT * FROM pedidos WHERE restaurante=? ORDER BY id DESC LIMIT ?", (rid, limite))]


def cambiar_pedido(rid: str, pid: int, estado: str):
    with _lock:
        conn().execute("UPDATE pedidos SET estado=? WHERE restaurante=? AND id=?", (estado, rid, pid))
        conn().commit()


def llamar_mesero(rid: str, mesa: str, motivo: str):
    with _lock:
        conn().execute("INSERT INTO llamadas (restaurante, mesa, motivo, creada) VALUES (?,?,?,?)",
                       (rid, mesa, motivo, time.time()))
        conn().commit()


def llamadas(rid: str) -> list:
    return [dict(f) for f in conn().execute(
        "SELECT * FROM llamadas WHERE restaurante=? AND atendida=0 ORDER BY id DESC LIMIT 30", (rid,))]


def atender_llamada(rid: str, lid: int):
    with _lock:
        conn().execute("UPDATE llamadas SET atendida=1 WHERE restaurante=? AND id=?", (rid, lid))
        conn().commit()
