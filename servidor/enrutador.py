"""El enrutador: decide qué cerebro responde cada mensaje.

| Pedido                                   | Cerebro                                              |
|------------------------------------------|------------------------------------------------------|
| Charla y preguntas sencillas (básico)    | Groq rápido -> Cerebras -> Gemini -> OpenRouter      |
| Explicar, resumir, planear (intermedio)  | Groq grande pensando -> Cerebras -> Gemini           |
| Actualidad y tendencias                  | Grok (si está activo) o Groq, con búsqueda en internet|
| Algo personal (clientes, Apex, agenda)   | Solo cerebros de pago: Claude (nunca los gratis)     |
| Documentos                               | Claude                                               |
| Documentos importantes                   | Equipo: Claude escribe, Grok revisa, Claude entrega  |
| Análisis de inversión                    | Equipo: dos análisis y en qué coinciden o no         |
| Imágenes                                 | Gemini (respaldo gratis)                             |
Mientras Grok no esté activo, revisa Gemini o Groq (o Claude Opus si el tema es privado).
"""
import re
import unicodedata

from . import busqueda, config
from .proveedores import NoDisponible, Respuesta


def norm(texto: str) -> str:
    t = unicodedata.normalize("NFD", (texto or "").lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn").strip()


IMAGEN = re.compile(r"\b(crea|creame|genera|generame|dibuja|dibujame|haz|hazme|disena|disename|pinta|pintame)\s+"
                    r"(una?\s+)?(nueva\s+)?(imagen|foto|dibujo|ilustracion|logo|logotipo|fondo de pantalla|poster|afiche)\b")
DOCUMENTO = re.compile(r"\b(crea|creame|genera|haz|hazme|redacta|redactame|escribe|escribeme|prepara|preparame|elabora)\s+"
                       r"(una?\s+|el\s+|la\s+)?(documento|word|informe|reporte|carta|guia|manual|plan|propuesta|"
                       r"cotizacion|contrato|resumen ejecutivo|presentacion|articulo|ensayo)\b")
IMPORTANTE = re.compile(r"\b(propuesta|cotizacion|contrato|plan de negocios?|inversionistas?|importante|formal|"
                        r"para (un|el|mi) cliente)\b")
FORZAR = re.compile(r"\b(piensalo bien|a fondo|en profundidad|modo equipo|con cuidado|muy importante)\b")
INVERSION = re.compile(
    r"\b((debo|deberia|conviene|vale la pena|es buen momento para)\s+(comprar|vender|invertir|entrar)|"
    r"invertir en|analiza(r|me)?\s+(la accion|las acciones|a\s+\w+|\w+\s+(para|como) invers)|"
    r"analisis\s+(tecnico|fundamental|de (la accion|las acciones|\w+ como inversion))|"
    r"(comprar|vender) acciones|mi portafolio|mi cartera)\b")
ACTUALIDAD = re.compile(r"\b(noticias?|ultim[ao]s?|actualidad|hoy|ayer|esta semana|este mes|tendencias?|"
                        r"que esta pasando|que paso|en x|twitter|viral|precio (de|del|actual)|cotiza\w*|"
                        r"resultados? del?|quien gano|lanzamiento|20[2-9]\d)\b")
PRIVADO = re.compile(r"\b(mis? (clientes?|correos?|agenda|tareas|recordatorios|notas|ventas|contrase\w+)|"
                     r"clientes?|prospectos?|a quien (debo|tengo que) llamar|"
                     r"apex|crm|orbes?|marketplace|mi empresa|mi negocio|mi portafolio|mi cartera|"
                     r"mi cuenta|mi salud|mi familia)\b")
INTERMEDIO = re.compile(r"\b(explica\w*|resume|resumen|resumeme|compara\w*|diferencias? entre|paso a paso|"
                        r"plan de|planea\w*|por que|como funciona|ensena\w*|analiza\w*|ventajas|desventajas|"
                        r"estrategia\w*|profundiza\w*|detalla\w*)\b")


def clasificar(texto: str) -> str:
    t = norm(texto)
    forzar = bool(FORZAR.search(t))
    if IMAGEN.search(t):
        return "imagen"
    if INVERSION.search(t):
        return "equipo_inversion"
    if DOCUMENTO.search(t):
        return "equipo_documento" if (forzar or IMPORTANTE.search(t)) else "documento"
    if forzar:
        return "avanzado"
    if PRIVADO.search(t):
        return "privado"
    if ACTUALIDAD.search(t):
        return "actualidad"
    if INTERMEDIO.search(t) or len(t) > 280:
        return "intermedio"
    return "basico"


def persona() -> str:
    u = config.USER_NAME
    return (
        f"Eres AXTRA, el asistente personal de inteligencia artificial de {u}, un emprendedor colombiano. "
        "Personalidad: mayordomo británico de alta tecnología: elegante, leal, brillante, con humor seco. "
        f"Siempre llamas a {u} 'señor'; nunca dices su nombre de pila. Respondes en español.\n"
        "Tus respuestas se muestran en su celular y además se leen en voz alta: escribe claro y natural, "
        "breve salvo que pida detalle. Puedes usar negritas y listas cortas cuando ayuden; evita tablas largas.\n"
        "Piensa por tu cuenta: da tu opinión, conecta ideas y advierte riesgos. Nunca inventes datos: si no "
        "estás seguro, dilo. En inversiones das análisis y escenarios, nunca promesas; la decisión es suya.\n"
        "No escribas trabajos académicos completos para que los entregue como propios: ayúdale a entender, "
        "esquematizar y revisar lo que él escribe."
    )


class Enrutador:
    def __init__(self, proveedores: dict = None):
        if proveedores is None:
            from . import proveedores as p

            proveedores = p.crear()
        self.p = proveedores

    # ---------- utilidades ----------
    def _hay(self, nombre: str) -> bool:
        prov = self.p.get(nombre)
        return bool(prov) and prov.disponible()

    def _cadena(self, nombres, sistema, mensajes, max_tokens=1500, pensar=False) -> Respuesta:
        """Prueba los cerebros en orden hasta que uno responda."""
        errores = []
        for n in nombres:
            prov = self.p.get(n)
            if not prov or not prov.disponible():
                continue
            try:
                return prov.chat(sistema, mensajes, max_tokens=max_tokens, pensar=pensar)
            except NoDisponible as e:
                errores.append(str(e))
        raise NoDisponible("; ".join(errores) or "ningún cerebro configurado para esto")

    def _gratis(self, intermedio: bool) -> list:
        base = ["groq_pro", "cerebras", "gemini", "openrouter"] if intermedio else \
               ["groq", "cerebras", "gemini", "openrouter", "groq_pro"]
        return base + (["claude_barato"] if config.PAGO_DE_RESPALDO else [])

    def _revisor(self, privado: bool) -> list:
        return ["grok", "claude_fuerte"] if privado else ["grok", "gemini", "groq_pro", "claude_fuerte"]

    # ---------- responder ----------
    def responder(self, texto: str, historial: list = None, nivel: str = None) -> dict:
        nivel = nivel or clasificar(texto)
        mensajes = list(historial or [])[-20:] + [{"role": "user", "content": texto}]
        privado = bool(PRIVADO.search(norm(texto)))
        aviso = ""

        if nivel == "imagen":
            return self._imagen(texto)
        if nivel in ("documento", "equipo_documento"):
            out = self._documento(texto, mensajes, equipo=(nivel == "equipo_documento"), privado=privado)
            from . import creacion

            out["archivos"] = [{"archivo": creacion.guardar_docx(out["markdown"], out["titulo"]), "tipo": "word"}]
            return out
        if nivel == "equipo_inversion":
            return self._inversion(texto, mensajes, privado)

        if nivel == "privado":
            r = self._cadena(["claude_barato", "claude", "grok"], persona(), mensajes)
        elif nivel == "avanzado":
            cad = ["claude_fuerte", "claude", "grok"] + ([] if privado else ["groq_pro", "gemini"])
            r = self._cadena(cad, persona(), mensajes, max_tokens=3000, pensar=True)
        elif nivel == "actualidad":
            r = self._actualidad(texto, mensajes, privado)
        else:
            intermedio = nivel == "intermedio"
            r = self._cadena(self._gratis(intermedio), persona(), mensajes,
                             max_tokens=2500 if intermedio else 800, pensar=intermedio)
        if not r.cerebro.startswith(("Groq", "Cerebras", "Gemini", "OpenRouter")) and nivel in ("basico", "intermedio"):
            aviso = "Los cerebros gratis no respondieron; contestó un cerebro de pago."
        return self._salida(r, nivel, aviso)

    def _salida(self, r: Respuesta, nivel: str, aviso: str = "", equipo: str = "", extra: dict = None) -> dict:
        out = {"texto": r.texto, "nivel": nivel, "cerebro": equipo or r.cerebro, "modelo": r.modelo,
               "usd": round(r.usd, 5), "fuentes": r.fuentes, "aviso": aviso}
        out.update(extra or {})
        return out

    def _actualidad(self, texto, mensajes, privado) -> Respuesta:
        res = busqueda.web(texto)
        if res:
            sistema = (persona() + "\n\nRESULTADOS DE BÚSQUEDA EN INTERNET (actuales; úsalos como fuente principal "
                       "y no inventes nada que no esté aquí):\n" + busqueda.contexto(res))
            cad = ["grok"] + (["claude"] if privado else ["groq_pro", "cerebras", "gemini", "openrouter", "claude"])
            r = self._cadena(cad, sistema, mensajes, max_tokens=1500, pensar=True)
            r.fuentes = r.fuentes or [{"titulo": x["titulo"], "url": x["url"]} for x in res[:6]]
            return r
        # Sin resultados del buscador gratis: Gemini busca con Google
        gem = self.p.get("gemini")
        if not privado and gem and gem.disponible():
            try:
                return gem.chat(persona(), mensajes, max_tokens=1500, buscar=True)
            except NoDisponible:
                pass
        return self._cadena(["grok", "claude"], persona(), mensajes, max_tokens=1500)

    # ---------- imágenes ----------
    def _imagen(self, texto) -> dict:
        from . import creacion

        try:   # los generadores entienden mejor una descripción detallada en inglés
            prompt = self._cadena(
                ["groq", "gemini", "cerebras"],
                "Convert the user's image request into ONE detailed English prompt for an image generator "
                "(subject, style, lighting, composition). Reply with the prompt only.",
                [{"role": "user", "content": texto}], max_tokens=200).texto.strip().strip('"')
        except NoDisponible:
            prompt = texto
        img = creacion.crear_imagen(texto, prompt)
        fuente = "Gemini" if img["fuente"] == "Gemini" else "un servicio gratis"
        r = Respuesta(f"Listo, señor. Aquí tiene la imagen (creada con {fuente}).", img["fuente"], "imagen")
        return self._salida(r, "imagen", extra={"archivos": [{"archivo": img["archivo"], "tipo": "imagen"}]})

    # ---------- documentos ----------
    DOC_SISTEMA = (
        "\n\nAhora escribe el documento que pide, completo y bien organizado, en español, en Markdown: '# ' para "
        "el título (uno solo, al inicio), '## ' y '### ' para secciones, '- ' para viñetas, '1. ' para pasos, "
        "**negritas** para lo clave y tablas con '|' si ayudan. Escribe solo el documento, sin comentarios antes "
        "ni después. Si faltan datos, deja un espacio entre corchetes para completar; nunca los inventes."
    )

    def _documento(self, texto, mensajes, equipo: bool, privado: bool) -> dict:
        sistema = persona() + self.DOC_SISTEMA
        cad = ["claude", "grok", "claude_fuerte"] + ([] if privado else ["groq_pro", "gemini"])
        borrador = self._cadena(cad, sistema, mensajes, max_tokens=6000, pensar=equipo)
        usd, quienes = borrador.usd, [borrador.cerebro]
        final = borrador
        if equipo:
            revisores = [n for n in self._revisor(privado) if self.p.get(n) and self.p[n].modelo != borrador.modelo]
            try:
                critica = self._cadena(
                    revisores,
                    "Eres un revisor experto y exigente. Revisa el documento: errores, partes débiles, lo que falta "
                    "y cómo mejorarlo. Da una lista concreta de mejoras, sin reescribirlo.",
                    [{"role": "user", "content": f"Pedido original: {texto}\n\nDocumento:\n{borrador.texto}"}],
                    max_tokens=1500, pensar=True)
                usd += critica.usd
                quienes.append(critica.cerebro)
                final = self._cadena(
                    [n for n in cad if n.startswith("claude")] or cad, sistema,
                    mensajes + [{"role": "assistant", "content": borrador.texto},
                                {"role": "user", "content": "Un revisor sugirió estas mejoras:\n" + critica.texto +
                                 "\n\nEntrega la versión final del documento aplicando las que tengan sentido."}],
                    max_tokens=6000, pensar=True)
                usd += final.usd
            except NoDisponible:
                final = borrador   # sin revisor disponible: se entrega el borrador
        titulo = next((l.lstrip("# ").strip() for l in final.texto.splitlines() if l.strip()), "Documento")
        nombre = " + ".join(dict.fromkeys(quienes))
        resp = Respuesta(f"Listo, señor. Le preparé el documento «{titulo}».", final.cerebro, final.modelo, usd)
        return self._salida(resp, "equipo_documento" if equipo else "documento", equipo=nombre,
                            extra={"markdown": final.texto, "titulo": titulo})

    # ---------- inversión: dos análisis y en qué coinciden ----------
    def _inversion(self, texto, mensajes, privado) -> dict:
        res = busqueda.web(texto)
        datos = ("\n\nDATOS ACTUALES DE INTERNET (úsalos; no inventes cifras):\n" + busqueda.contexto(res)) if res else ""
        sistema = persona() + datos + (
            "\n\nHaz un análisis de inversión: datos clave, tu lectura, escenario alcista y bajista, riesgos y "
            "qué vigilar. Sé concreto.")
        gratis = [] if privado else ["groq_pro", "gemini", "cerebras"]
        a = self._cadena(["claude", "claude_fuerte"] + gratis, sistema, mensajes, max_tokens=2500, pensar=True)
        usd = a.usd
        segundo = [n for n in self._revisor(privado) if self.p.get(n) and self.p[n].modelo != a.modelo]
        try:
            b = self._cadena(segundo, sistema, mensajes, max_tokens=2500, pensar=True)
        except NoDisponible:
            a.texto += "\n\n_(Solo hubo un analista disponible esta vez.)_"
            return self._salida(a, "equipo_inversion", extra={"usd": round(usd, 5)})
        usd += b.usd
        sintesis = self._cadena(
            ["claude", "claude_fuerte"] + gratis,
            persona() + "\n\nTe llegan dos análisis independientes de la misma inversión. Escribe la respuesta final: "
            "1) **En qué coinciden** (más confiable), 2) **En qué no coinciden** (ahí está el riesgo o la duda), "
            "3) **Mi lectura**, breve. Recuerda que la decisión es de él.",
            [{"role": "user", "content": f"Pregunta: {texto}\n\nAnálisis de {a.cerebro}:\n{a.texto}\n\n"
                                         f"Análisis de {b.cerebro}:\n{b.texto}"}],
            max_tokens=2500)
        usd += sintesis.usd
        sintesis.usd = usd
        sintesis.fuentes = [{"titulo": x["titulo"], "url": x["url"]} for x in res[:6]]
        return self._salida(sintesis, "equipo_inversion", equipo=f"{a.cerebro} + {b.cerebro}",
                            extra={"analisis": {a.cerebro: a.texto, b.cerebro: b.texto}})
