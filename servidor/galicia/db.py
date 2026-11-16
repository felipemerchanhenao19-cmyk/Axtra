"""Base de datos de Galicia (SQLite, un solo archivo en la carpeta de datos).

Es la fuente de la verdad: los Excel se generan desde aquí, nunca al revés.
Cada registro guarda cómo deshacerlo (tabla «acciones»), para el botón «Deshacer».
"""
import difflib
import json
import sqlite3
import threading
import time
import unicodedata
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from . import config

_lock = threading.RLock()
_conn = None

ESQUEMA = """
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS cuentas (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, tipo TEXT DEFAULT 'tarjeta',  -- tarjeta, cuenta, credito, efectivo
    banco TEXT DEFAULT '', ultimos4 TEXT DEFAULT '', titular TEXT DEFAULT '', cupo REAL, deuda REAL,
    dia_corte INTEGER, dia_pago INTEGER, activa INTEGER DEFAULT 1, notas TEXT DEFAULT '', creado REAL);
CREATE TABLE IF NOT EXISTS movimientos (
    id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT NOT NULL, tipo TEXT NOT NULL,           -- gasto | ingreso
    monto REAL NOT NULL, categoria TEXT DEFAULT 'Otros', ambito TEXT DEFAULT 'hacienda',   -- hacienda | personal
    actividad TEXT DEFAULT 'general', lote_id INTEGER, cuenta_id INTEGER, tercero TEXT DEFAULT '',
    nit TEXT DEFAULT '', factura TEXT DEFAULT '', cufe TEXT DEFAULT '', descripcion TEXT DEFAULT '',
    soporte TEXT DEFAULT '', origen TEXT DEFAULT 'chat', usuario TEXT DEFAULT '', creado REAL);
CREATE INDEX IF NOT EXISTS movimientos_fecha ON movimientos (fecha);
CREATE TABLE IF NOT EXISTS obligaciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL,
    tipo TEXT DEFAULT 'otro',             -- tarjeta, cuota, credito, impuesto, seguro, servicio, otro
    cuenta_id INTEGER, monto REAL, monto_minimo REAL, fecha TEXT NOT NULL,           -- próximo vencimiento
    frecuencia TEXT DEFAULT 'mensual',    -- unica, mensual, bimestral, trimestral, semestral, anual
    cuotas_total INTEGER, cuotas_pagadas INTEGER DEFAULT 0, saldo REAL, activa INTEGER DEFAULT 1,
    notas TEXT DEFAULT '', creado REAL);
CREATE TABLE IF NOT EXISTS pagos (
    id INTEGER PRIMARY KEY AUTOINCREMENT, obligacion_id INTEGER, fecha TEXT, monto REAL, movimiento_id INTEGER, creado REAL);
CREATE TABLE IF NOT EXISTS diferidos (                -- compras a cuotas que trae el extracto de cada tarjeta
    id INTEGER PRIMARY KEY AUTOINCREMENT, cuenta_id INTEGER, descripcion TEXT, fecha_compra TEXT,
    valor_cuota REAL, cuota_actual INTEGER, cuotas_total INTEGER, saldo REAL, actualizado TEXT);
CREATE TABLE IF NOT EXISTS lotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT NOT NULL, hectareas REAL, variedad TEXT DEFAULT '',
    fecha_siembra TEXT, estado TEXT DEFAULT 'activo', notas TEXT DEFAULT '', creado REAL);
CREATE TABLE IF NOT EXISTS labores (
    id INTEGER PRIMARY KEY AUTOINCREMENT, lote_id INTEGER, fecha TEXT, tipo TEXT, producto TEXT DEFAULT '',
    cantidad TEXT DEFAULT '', costo REAL, movimiento_id INTEGER, proxima TEXT, notas TEXT DEFAULT '', creado REAL);
CREATE TABLE IF NOT EXISTS cosechas (
    id INTEGER PRIMARY KEY AUTOINCREMENT, lote_id INTEGER, fecha TEXT, bultos REAL, precio_bulto REAL,
    comprador TEXT DEFAULT '', movimiento_id INTEGER, notas TEXT DEFAULT '', creado REAL);
CREATE TABLE IF NOT EXISTS animales (
    id INTEGER PRIMARY KEY AUTOINCREMENT, codigo TEXT NOT NULL, nombre TEXT DEFAULT '', sexo TEXT DEFAULT '',
    categoria TEXT DEFAULT '', raza TEXT DEFAULT '', nacimiento TEXT, madre TEXT DEFAULT '',
    estado TEXT DEFAULT 'activo', notas TEXT DEFAULT '', creado REAL);
CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT, animal_id INTEGER,       -- vacío = todo el hato
    fecha TEXT, tipo TEXT, detalle TEXT DEFAULT '', valor REAL, proxima TEXT, movimiento_id INTEGER, creado REAL);
CREATE TABLE IF NOT EXISTS leche (
    id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, litros REAL, vacas INTEGER, notas TEXT DEFAULT '', creado REAL);
CREATE TABLE IF NOT EXISTS liquidaciones_leche (
    id INTEGER PRIMARY KEY AUTOINCREMENT, desde TEXT, hasta TEXT, litros REAL, precio_litro REAL,
    descuentos REAL, neto REAL, comprador TEXT DEFAULT '', movimiento_id INTEGER, creado REAL);
CREATE TABLE IF NOT EXISTS reglas (                   -- lo que aprende: este proveedor siempre es de esta categoría
    clave TEXT PRIMARY KEY, categoria TEXT, ambito TEXT, actividad TEXT, veces INTEGER DEFAULT 1);
CREATE TABLE IF NOT EXISTS pendientes (               -- lo que la IA propone y espera un «Guardar»
    id INTEGER PRIMARY KEY AUTOINCREMENT, chat INTEGER, tipo TEXT, datos TEXT, creado REAL);
CREATE TABLE IF NOT EXISTS acciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT, usuario TEXT, descripcion TEXT, deshacer TEXT, deshecha INTEGER DEFAULT 0, creado REAL);
CREATE TABLE IF NOT EXISTS avisos (clave TEXT PRIMARY KEY, enviado REAL);
CREATE TABLE IF NOT EXISTS estado (clave TEXT PRIMARY KEY, valor TEXT);
"""

TABLAS = {"cuentas", "movimientos", "obligaciones", "pagos", "diferidos", "lotes", "labores", "cosechas", "animales",
          "eventos", "leche", "liquidaciones_leche", "reglas", "pendientes"}


def conn() -> sqlite3.Connection:
    global _conn
    with _lock:
        if _conn is None:
            _conn = sqlite3.connect(config.DATA_DIR / "galicia.db", check_same_thread=False, isolation_level=None)
            _conn.row_factory = sqlite3.Row
            _conn.executescript(ESQUEMA)
        return _conn


def filas(sql: str, args=()) -> list:
    with _lock:
        return [dict(f) for f in conn().execute(sql, args).fetchall()]


def fila(sql: str, args=()):
    r = filas(sql, args)
    return r[0] if r else None


def ejecutar(sql: str, args=()):
    with _lock:
        return conn().execute(sql, args)


# ---------------- Fechas ----------------
def hoy() -> date:
    return datetime.now(ZoneInfo(config.ZONA_HORARIA)).date()


def fecha(valor, defecto: date = None) -> str:
    """Acepta 2026-11-16, 16/11/2026 o vacío (= hoy). Devuelve AAAA-MM-DD."""
    if not valor:
        return (defecto or hoy()).isoformat()
    texto = str(valor).strip()[:10]
    for formato in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(texto, formato).date().isoformat()
        except ValueError:
            pass
    raise ValueError(f"fecha no válida: {valor!r} (usa AAAA-MM-DD)")


def sumar_meses(d: date, meses: int) -> date:
    m = d.month - 1 + meses
    anio, mes = d.year + m // 12, m % 12 + 1
    dias = [31, 29 if anio % 4 == 0 and (anio % 100 or anio % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    return date(anio, mes, min(d.day, dias[mes - 1]))


MESES_FRECUENCIA = {"mensual": 1, "bimestral": 2, "trimestral": 3, "semestral": 6, "anual": 12}


def siguiente_fecha(actual: str, frecuencia: str) -> str:
    return sumar_meses(date.fromisoformat(actual), MESES_FRECUENCIA.get(frecuencia, 1)).isoformat()


# ---------------- Texto ----------------
def normal(texto: str) -> str:
    t = unicodedata.normalize("NFD", str(texto or "").lower())
    return " ".join("".join(c for c in t if unicodedata.category(c) != "Mn").split())


def buscar(tabla: str, referencia, campos=("nombre",), extra: str = "") -> dict:
    """Encuentra una fila por id o por nombre aproximado («la visa de bancolombia», «lote 2»)."""
    assert tabla in TABLAS
    if referencia in (None, ""):
        return None
    todas = filas(f"SELECT * FROM {tabla} {extra}")
    texto = str(referencia).strip()
    if texto.isdigit():
        for f in todas:
            if f["id"] == int(texto):
                return f
    buscado = normal(texto)
    nombres = {}
    for f in todas:
        juntos = normal(" ".join(str(f.get(c) or "") for c in campos))
        nombres[f["id"]] = juntos
        if juntos == buscado or normal(f.get(campos[0]) or "") == buscado:
            return f
    candidatas = [f for f in todas if buscado in nombres[f["id"]] or nombres[f["id"]] in buscado]
    if len(candidatas) == 1:
        return candidatas[0]
    pool = candidatas or todas
    mejor = difflib.get_close_matches(buscado, [nombres[f["id"]] for f in pool], n=1, cutoff=0.5)
    if mejor:
        return next(f for f in pool if nombres[f["id"]] == mejor[0])
    return None


# ---------------- Registro con «deshacer» ----------------
class Accion:
    """Agrupa los cambios de una orden para poder deshacerlos juntos."""

    def __init__(self, usuario: str, descripcion: str):
        self.usuario, self.descripcion, self.pasos = usuario, descripcion, []

    def insertar(self, tabla: str, datos: dict) -> int:
        assert tabla in TABLAS
        datos = {k: v for k, v in datos.items() if v is not None}
        if tabla not in ("reglas", "diferidos"):
            datos.setdefault("creado", time.time())
        columnas = ", ".join(datos)
        marcas = ", ".join("?" for _ in datos)
        cur = ejecutar(f"INSERT INTO {tabla} ({columnas}) VALUES ({marcas})", tuple(datos.values()))
        self.pasos.append({"borrar": [tabla, cur.lastrowid]})
        return cur.lastrowid

    def actualizar(self, tabla: str, id_: int, cambios: dict):
        assert tabla in TABLAS
        antes = fila(f"SELECT * FROM {tabla} WHERE id=?", (id_,))
        if not antes or not cambios:
            return
        self.pasos.append({"restaurar": [tabla, id_, {k: antes[k] for k in cambios}]})
        sets = ", ".join(f"{k}=?" for k in cambios)
        ejecutar(f"UPDATE {tabla} SET {sets} WHERE id=?", (*cambios.values(), id_))

    def guardar(self) -> int:
        if not self.pasos:
            return 0
        cur = ejecutar("INSERT INTO acciones (usuario, descripcion, deshacer, creado) VALUES (?,?,?,?)",
                       (self.usuario, self.descripcion, json.dumps(self.pasos), time.time()))
        return cur.lastrowid


def deshacer(accion_id: int = None, usuario: str = None) -> str:
    """Deshace una acción (o la última de ese usuario). Devuelve qué se deshizo."""
    with _lock:
        if accion_id:
            a = fila("SELECT * FROM acciones WHERE id=? AND deshecha=0", (accion_id,))
        else:
            a = fila("SELECT * FROM acciones WHERE usuario=? AND deshecha=0 ORDER BY id DESC LIMIT 1", (usuario,))
        if not a:
            return ""
        for paso in reversed(json.loads(a["deshacer"])):
            if "borrar" in paso:
                tabla, id_ = paso["borrar"]
                assert tabla in TABLAS
                ejecutar(f"DELETE FROM {tabla} WHERE id=?", (id_,))
            elif "restaurar_fila" in paso:            # una fila que se borró: vuelve tal cual
                tabla, datos = paso["restaurar_fila"]
                assert tabla in TABLAS
                ejecutar(f"INSERT OR REPLACE INTO {tabla} ({', '.join(datos)}) VALUES ({', '.join('?' for _ in datos)})",
                         tuple(datos.values()))
            else:
                tabla, id_, antes = paso["restaurar"]
                assert tabla in TABLAS
                sets = ", ".join(f"{k}=?" for k in antes)
                ejecutar(f"UPDATE {tabla} SET {sets} WHERE id=?", (*antes.values(), id_))
        ejecutar("UPDATE acciones SET deshecha=1 WHERE id=?", (a["id"],))
        return a["descripcion"]


# ---------------- Lo que aprende ----------------
def clave_tercero(nit: str = "", tercero: str = "") -> str:
    nit = "".join(c for c in str(nit or "") if c.isdigit())[:9]       # sin dígito de verificación
    return f"nit:{nit}" if len(nit) >= 6 else (f"t:{normal(tercero)}" if tercero else "")


def regla(nit: str = "", tercero: str = ""):
    clave = clave_tercero(nit, tercero)
    return fila("SELECT * FROM reglas WHERE clave=?", (clave,)) if clave else None


def aprender(nit: str, tercero: str, categoria: str, ambito: str, actividad: str):
    clave = clave_tercero(nit, tercero)
    if clave:
        ejecutar("""INSERT INTO reglas (clave, categoria, ambito, actividad) VALUES (?,?,?,?)
                    ON CONFLICT(clave) DO UPDATE SET categoria=excluded.categoria, ambito=excluded.ambito,
                    actividad=excluded.actividad, veces=veces+1""", (clave, categoria, ambito, actividad))


# ---------------- Pendientes (propuestas de la IA) ----------------
def guardar_pendiente(chat: int, tipo: str, datos: dict) -> int:
    return ejecutar("INSERT INTO pendientes (chat, tipo, datos, creado) VALUES (?,?,?,?)",
                    (chat, tipo, json.dumps(datos, ensure_ascii=False), time.time())).lastrowid


def pendiente(id_: int):
    p = fila("SELECT * FROM pendientes WHERE id=?", (id_,))
    if p:
        p["datos"] = json.loads(p["datos"])
    return p


def ultimo_pendiente(chat: int, tipo: str = "factura"):
    p = fila("SELECT * FROM pendientes WHERE chat=? AND tipo=? AND creado>? ORDER BY id DESC LIMIT 1",
             (chat, tipo, time.time() - 86400))
    if p:
        p["datos"] = json.loads(p["datos"])
    return p


def cambiar_pendiente(id_: int, datos: dict):
    ejecutar("UPDATE pendientes SET datos=? WHERE id=?", (json.dumps(datos, ensure_ascii=False), id_))


def borrar_pendiente(id_: int):
    ejecutar("DELETE FROM pendientes WHERE id=?", (id_,))


# ---------------- Avisos y estado ----------------
def ya_avisado(clave: str) -> bool:
    return fila("SELECT 1 AS x FROM avisos WHERE clave=?", (clave,)) is not None


def marcar_avisado(clave: str):
    ejecutar("INSERT OR IGNORE INTO avisos (clave, enviado) VALUES (?,?)", (clave, time.time()))


def leer_estado(clave: str, defecto: str = "") -> str:
    f = fila("SELECT valor FROM estado WHERE clave=?", (clave,))
    return f["valor"] if f else defecto


def poner_estado(clave: str, valor: str):
    ejecutar("INSERT INTO estado (clave, valor) VALUES (?,?) ON CONFLICT(clave) DO UPDATE SET valor=excluded.valor",
             (clave, valor))


def duplicado_factura(cufe: str = "", nit: str = "", factura: str = ""):
    if cufe:
        f = fila("SELECT * FROM movimientos WHERE cufe=?", (cufe,))
        if f:
            return f
    if nit and factura:
        n = "".join(c for c in nit if c.isdigit())[:9]
        for f in filas("SELECT * FROM movimientos WHERE factura=?", (factura,)):
            if "".join(c for c in f["nit"] if c.isdigit())[:9] == n:
                return f
    return None


def parecido(fecha_: str, monto: float, dias: int = 3):
    """¿Ya hay un movimiento por el mismo valor en fechas cercanas? (para no duplicar lo del extracto)"""
    d = date.fromisoformat(fecha_)
    return fila("SELECT * FROM movimientos WHERE ABS(monto-?)<1 AND fecha BETWEEN ? AND ?",
                (monto, (d - timedelta(days=dias)).isoformat(), (d + timedelta(days=dias)).isoformat()))
