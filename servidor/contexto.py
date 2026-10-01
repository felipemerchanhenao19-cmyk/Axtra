"""Lo que Axtra sabe de ti (subido desde el Axtra del PC). SOLO se agrega para cerebros de pago."""
import json
from datetime import datetime
from zoneinfo import ZoneInfo

from . import config, db


def _recortar(texto: str, n: int) -> str:
    return texto if len(texto) <= n else texto[:n] + "…"


def privado() -> str:
    partes = []
    recuerdos = db.leer_pc("recuerdos", [])
    if recuerdos:
        partes.append("Lo que recuerdas de él:\n" + "\n".join(
            f"- {r.get('texto', '')} ({r.get('fecha', '')})" for r in recuerdos[-80:]))
    perfil = db.leer_pc("perfil", "")
    if perfil:
        partes.append("Perfil de sus empresas (lo marcado 'sugerido por Claude' está por confirmar):\n"
                      + _recortar(perfil, 8000))
    crm = db.leer_pc("crm", [])
    if crm:
        filas = [{k: c.get(k) for k in ("nombre", "negocio", "telefono", "estado", "proximo_contacto", "notas")
                  if c.get(k)} for c in crm[-60:]]
        partes.append("Su CRM de ventas (clientes y prospectos):\n" + _recortar(json.dumps(filas, ensure_ascii=False), 6000))
    tareas = [t for t in db.leer_pc("tareas", []) if not t.get("hecha")]
    if tareas:
        partes.append("Tareas pendientes:\n" + "\n".join(f"- {t.get('texto', '')}" for t in tareas[:30]))
    sync = db.leer_pc("sincronizacion", {})
    if sync.get("total") is not None:
        partes.append(f"Sincronización contigo: {sync['total']} % (nivel {sync.get('nivel', '')}).")
    if not partes:
        return ""
    ahora = datetime.now(ZoneInfo(config.ZONA_HORARIA)).strftime("%Y-%m-%d %H:%M")
    return (f"\n\nDATOS PRIVADOS DE {config.USER_NAME.upper()} (sincronizados desde su Axtra del PC; "
            f"hoy es {ahora}). Úsalos para responderle; no los repitas si no hace falta:\n\n" + "\n\n".join(partes))
