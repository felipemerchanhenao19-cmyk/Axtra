"""Base de datos del servidor (SQLite): conversaciones y gasto mensual por cerebro."""
import json
import sqlite3
import threading
import time
import uuid
from datetime import datetime

from . import config

_lock = threading.Lock()
_conn = None


def conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(config.DATA_DIR / "axtra.db", check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.executescript("""
            PRAGMA journal_mode=WAL;
            CREATE TABLE IF NOT EXISTS gastos (mes TEXT, proveedor TEXT, usd REAL DEFAULT 0,
                                               PRIMARY KEY (mes, proveedor));
            CREATE TABLE IF NOT EXISTS chats (id TEXT PRIMARY KEY, titulo TEXT, creado REAL, actualizado REAL);
            CREATE TABLE IF NOT EXISTS mensajes (id INTEGER PRIMARY KEY AUTOINCREMENT, chat_id TEXT, rol TEXT,
                                                 texto TEXT, cerebro TEXT, creado REAL);
            CREATE INDEX IF NOT EXISTS mensajes_chat ON mensajes (chat_id, id);
            CREATE TABLE IF NOT EXISTS datos_pc (clave TEXT PRIMARY KEY, valor TEXT, actualizado REAL);
            CREATE TABLE IF NOT EXISTS recordatorios (id INTEGER PRIMARY KEY AUTOINCREMENT, mensaje TEXT,
                                                      cuando REAL, enviado INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS suscripciones (endpoint TEXT PRIMARY KEY, datos TEXT, creado REAL);
            CREATE TABLE IF NOT EXISTS practicas (idioma TEXT, frase TEXT, mejor REAL, intentos INTEGER,
                                                  ultima REAL, PRIMARY KEY (idioma, frase));
        """)
    return _conn


def _mes() -> str:
    return datetime.now().strftime("%Y-%m")


# ---------- Gasto ----------
def sumar_gasto(proveedor: str, usd: float) -> None:
    if usd <= 0:
        return
    with _lock:
        conn().execute("INSERT INTO gastos (mes, proveedor, usd) VALUES (?, ?, ?) "
                       "ON CONFLICT (mes, proveedor) DO UPDATE SET usd = usd + excluded.usd",
                       (_mes(), proveedor, usd))
        conn().commit()


def gasto_mes(proveedor: str) -> float:
    row = conn().execute("SELECT usd FROM gastos WHERE mes = ? AND proveedor = ?", (_mes(), proveedor)).fetchone()
    return row["usd"] if row else 0.0


# ---------- Conversaciones ----------
def nuevo_chat(titulo: str) -> str:
    chat_id = uuid.uuid4().hex[:12]
    now = time.time()
    with _lock:
        conn().execute("INSERT INTO chats VALUES (?, ?, ?, ?)", (chat_id, titulo[:80], now, now))
        conn().commit()
    return chat_id


def existe_chat(chat_id: str) -> bool:
    return conn().execute("SELECT 1 FROM chats WHERE id = ?", (chat_id,)).fetchone() is not None


def guardar_mensaje(chat_id: str, rol: str, texto: str, cerebro: str = "") -> None:
    now = time.time()
    with _lock:
        conn().execute("INSERT INTO mensajes (chat_id, rol, texto, cerebro, creado) VALUES (?, ?, ?, ?, ?)",
                       (chat_id, rol, texto, cerebro, now))
        conn().execute("UPDATE chats SET actualizado = ? WHERE id = ?", (now, chat_id))
        conn().commit()


def historial(chat_id: str, n: int = 20) -> list:
    """Últimos n mensajes como [{"role": "user"/"assistant", "content": texto}]."""
    rows = conn().execute("SELECT rol, texto FROM mensajes WHERE chat_id = ? ORDER BY id DESC LIMIT ?",
                          (chat_id, n)).fetchall()
    return [{"role": r["rol"], "content": r["texto"]} for r in reversed(rows)]


def chats(n: int = 50) -> list:
    rows = conn().execute("SELECT id, titulo, actualizado FROM chats ORDER BY actualizado DESC LIMIT ?", (n,))
    return [dict(r) for r in rows]


def mensajes(chat_id: str) -> list:
    rows = conn().execute("SELECT rol, texto, cerebro, creado FROM mensajes WHERE chat_id = ? ORDER BY id",
                          (chat_id,))
    return [dict(r) for r in rows]


def borrar_chat(chat_id: str) -> None:
    with _lock:
        conn().execute("DELETE FROM mensajes WHERE chat_id = ?", (chat_id,))
        conn().execute("DELETE FROM chats WHERE id = ?", (chat_id,))
        conn().commit()


# ---------- Idiomas ----------
def registrar_practica(idioma: str, frase: str, puntaje: float) -> None:
    with _lock:
        conn().execute("INSERT INTO practicas VALUES (?, ?, ?, 1, ?) ON CONFLICT (idioma, frase) DO UPDATE SET "
                       "mejor = max(mejor, excluded.mejor), intentos = intentos + 1, ultima = excluded.ultima",
                       (idioma, frase, puntaje, time.time()))
        conn().commit()


def practicas(idioma: str) -> dict:
    row = conn().execute("SELECT count(*) AS practicadas, sum(mejor >= 80) AS dominadas, avg(mejor) AS promedio "
                         "FROM practicas WHERE idioma = ?", (idioma,)).fetchone()
    return {"practicadas": row["practicadas"] or 0, "dominadas": row["dominadas"] or 0,
            "promedio": round(row["promedio"] or 0, 1)}


def idiomas_practicados() -> list:
    return [r["idioma"] for r in conn().execute("SELECT DISTINCT idioma FROM practicas ORDER BY idioma")]


# ---------- Datos que sube el Axtra del PC ----------
def guardar_pc(datos: dict) -> None:
    now = time.time()
    with _lock:
        for clave, valor in datos.items():
            conn().execute("INSERT INTO datos_pc VALUES (?, ?, ?) ON CONFLICT (clave) DO UPDATE SET "
                           "valor = excluded.valor, actualizado = excluded.actualizado",
                           (clave, json.dumps(valor, ensure_ascii=False), now))
        conn().commit()


def leer_pc(clave: str, defecto=None):
    row = conn().execute("SELECT valor FROM datos_pc WHERE clave = ?", (clave,)).fetchone()
    return json.loads(row["valor"]) if row else defecto


def ultima_sincronizacion():
    row = conn().execute("SELECT max(actualizado) AS t FROM datos_pc").fetchone()
    return row["t"] if row else None


# ---------- Recordatorios y notificaciones ----------
def crear_recordatorio(mensaje: str, cuando: float) -> int:
    with _lock:
        cur = conn().execute("INSERT INTO recordatorios (mensaje, cuando) VALUES (?, ?)", (mensaje, cuando))
        conn().commit()
        return cur.lastrowid


def recordatorios_pendientes() -> list:
    rows = conn().execute("SELECT id, mensaje, cuando FROM recordatorios WHERE enviado = 0 ORDER BY cuando")
    return [dict(r) for r in rows]


def recordatorios_vencidos(ahora: float) -> list:
    rows = conn().execute("SELECT id, mensaje, cuando FROM recordatorios WHERE enviado = 0 AND cuando <= ?", (ahora,))
    return [dict(r) for r in rows]


def marcar_enviado(rid: int) -> None:
    with _lock:
        conn().execute("UPDATE recordatorios SET enviado = 1 WHERE id = ?", (rid,))
        conn().commit()


def borrar_recordatorio(rid: int) -> None:
    with _lock:
        conn().execute("DELETE FROM recordatorios WHERE id = ?", (rid,))
        conn().commit()


def guardar_suscripcion(sub: dict) -> None:
    with _lock:
        conn().execute("INSERT OR REPLACE INTO suscripciones VALUES (?, ?, ?)",
                       (sub["endpoint"], json.dumps(sub), time.time()))
        conn().commit()


def suscripciones() -> list:
    return [json.loads(r["datos"]) for r in conn().execute("SELECT datos FROM suscripciones")]


def borrar_suscripcion(endpoint: str) -> None:
    with _lock:
        conn().execute("DELETE FROM suscripciones WHERE endpoint = ?", (endpoint,))
        conn().commit()
