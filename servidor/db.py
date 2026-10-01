"""Base de datos del servidor (SQLite): conversaciones y gasto mensual por cerebro."""
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
