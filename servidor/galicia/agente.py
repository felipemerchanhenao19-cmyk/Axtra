"""El asistente: entiende lo que le escriben (o dicen) y usa las herramientas para registrar y consultar."""
import json
from collections import defaultdict, deque

from . import cerebro, config, db, herramientas

_HISTORIAL = defaultdict(lambda: deque(maxlen=12))       # chat → últimos mensajes (solo texto)
MAX_VUELTAS = 6


def _contexto() -> str:
    cuentas = db.filas("SELECT nombre, banco, ultimos4 FROM cuentas WHERE activa=1")
    lotes = db.filas("SELECT nombre, variedad, estado FROM lotes ORDER BY estado, id DESC LIMIT 20")
    obligaciones = db.filas("SELECT nombre, fecha, monto FROM obligaciones WHERE activa=1 ORDER BY fecha LIMIT 30")
    animales = db.fila("SELECT COUNT(*) AS n FROM animales WHERE estado='activo'")["n"]
    partes = [
        "Tarjetas y cuentas: " + ("; ".join(f"{c['nombre']} ({c['banco']} {c['ultimos4']})".strip() for c in cuentas) or "ninguna aún"),
        "Lotes de papa: " + ("; ".join(f"{l['nombre']} ({l['variedad'] or 's/v'}, {l['estado']})" for l in lotes) or "ninguno aún"),
        "Vencimientos activos: " + ("; ".join(f"{o['nombre']} {o['fecha']}" for o in obligaciones) or "ninguno"),
        f"Animales activos registrados: {animales}",
    ]
    return "\n".join(partes)


def sistema(usuario: str, chat: int) -> str:
    hoy = db.hoy()
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    pendiente = db.ultimo_pendiente(chat)
    texto_pendiente = ""
    if pendiente and pendiente["tipo"] == "factura":
        d = {k: pendiente["datos"].get(k) for k in herramientas.CAMPOS_PENDIENTE}
        texto_pendiente = (f"\nHay una FACTURA esperando revisión (sin guardar): {json.dumps(d, ensure_ascii=False)}. "
                           "Si el mensaje la corrige o pide guardarla, usa ajustar_factura.")
    return f"""Eres el asistente contable y administrativo de la {config.NOMBRE} (Colombia). La manejan una pareja;
ahora te escribe {usuario}. La hacienda tiene cultivo de papa, ganado y venta de leche. Hoy es {dias[hoy.weekday()]} {hoy.isoformat()}.

Tu trabajo: registrar todo lo que te cuenten (gastos, ingresos, pagos, tarjetas, cuotas, labores del cultivo, leche,
ganado) usando las herramientas, y responder preguntas con los datos guardados.

Reglas:
- Español colombiano, claro y corto (es un chat de celular). Valores como $350.000.
- Montos: «350 mil» = 350000, «1,2 millones» = 1200000, «un palo» = 1000000.
- NUNCA inventes datos ni cifras: consulta con las herramientas. Si falta el valor de algo que hay que registrar, pregúntalo.
- Separa siempre hacienda de personal: mercado, ropa, salud, colegio, restaurante, gastos de la casa = personal.
  Abonos, semilla, fumigos, jornales, sal, veterinario, combustible de la finca = hacienda.
- Si con un mensaje se pagan varias cosas, registra cada una por separado.
- Fechas relativas («ayer», «el viernes») conviértelas a AAAA-MM-DD.
- El pago de una tarjeta o cuota ya registrada va con pagar_obligacion, no con registrar_movimiento.
- Después de registrar, confirma en UNA línea qué quedó (valor, a qué se cargó). No repitas todo el detalle.
- Si una herramienta devuelve error, explícalo sencillo y pregunta lo necesario.
- Categorías de gasto: {", ".join(config.CATEGORIAS_GASTO)}. De ingreso: {", ".join(config.CATEGORIAS_INGRESO)}.

Lo registrado hasta ahora:
{_contexto()}{texto_pendiente}"""


def responder(texto: str, usuario: str, chat: int, origen: str = "chat") -> dict:
    """Devuelve {"texto", "archivos", "acciones", "refrescar"}. Lanza cerebro.SinCerebro si no hay IA disponible."""
    ctx = {"usuario": usuario, "chat": chat, "origen": origen}
    historial = _HISTORIAL[chat]
    mensajes = [{"role": "system", "content": sistema(usuario, chat)}, *historial, {"role": "user", "content": texto}]
    respuesta = ""
    for _ in range(MAX_VUELTAS):
        m = cerebro.chat(mensajes, herramientas.esquemas())
        if not m["tool_calls"]:
            respuesta = m["content"].strip()
            break
        mensajes.append({"role": "assistant", "content": m["content"] or "", "tool_calls": m["tool_calls"]})
        for llamada in m["tool_calls"]:
            nombre = llamada["function"]["name"]
            try:
                argumentos = json.loads(llamada["function"].get("arguments") or "{}")
            except ValueError:
                argumentos = {}
            resultado = herramientas.ejecutar(nombre, argumentos, ctx)
            mensajes.append({"role": "tool", "tool_call_id": llamada["id"],
                             "content": json.dumps(resultado, ensure_ascii=False, default=str)[:6000]})
    else:
        respuesta = "Listo." if ctx.get("acciones") else "No logré terminar eso, ¿me lo dices de otra forma?"
    historial.append({"role": "user", "content": texto})
    historial.append({"role": "assistant", "content": respuesta or "Listo."})
    return {"texto": respuesta or "Listo.", "archivos": ctx.get("archivos", []), "acciones": ctx.get("acciones", []),
            "refrescar": ctx.get("refrescar", [])}


def olvidar(chat: int):
    _HISTORIAL.pop(chat, None)
