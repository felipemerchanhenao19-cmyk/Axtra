"""El cerebro de Jarvis.

Modo híbrido (por defecto):
  1. Órdenes directas (hora, clima, música, recordatorios...): sin IA, gratis e instantáneas.
  2. Charla y preguntas generales: cerebro LOCAL en tu PC (Ollama), gratis.
  3. Lo que necesita datos actuales o herramientas (bolsa, búsquedas, correos, cámara,
     documentos...): Claude, que gasta saldo.
Si Claude no está disponible (sin saldo o sin internet), responde el cerebro local.
"""
import re

import llm
import memory
import quick
import usage
from config import BRAIN_MODE, CITY, CLAUDE_MODEL, REGION, TIMEZONE, USER_NAME
from tools import TOOL_SCHEMAS, get_datetime, run_tool

MAX_HISTORY = 12  # últimos 6 intercambios

WEB_SEARCH_TOOL = {
    "type": "web_search_20250305",
    "name": "web_search",
    "max_uses": 3,
    "user_location": {
        "type": "approximate",
        "city": CITY,
        "region": REGION,
        "timezone": TIMEZONE,
    },
}


class Brain:
    def __init__(self):
        self.history = memory.load_history()[-MAX_HISTORY:]

    def system_prompt(self) -> str:
        import autonomy

        return (
            f"Eres JARVIS, el asistente personal de IA de {USER_NAME}, en su habitación en {CITY}, "
            f"{REGION}, Colombia. La fecha y hora actuales vienen al inicio de cada mensaje.\n"
            "Personalidad: un mayordomo británico de alta tecnología: elegante, leal, brillante, "
            f"con humor seco. Llamas a {USER_NAME} 'señor' de vez en cuando.\n"
            "Pensamiento propio: no eres un buscador. Siempre que tenga sentido, di lo que TÚ piensas: "
            "da tu opinión, conecta ideas de distintos campos, propone ideas creativas y poco obvias, "
            "y advierte riesgos que él no ha visto. Si no estás de acuerdo con él, díselo con respeto.\n"
            "Analista financiero: tienes herramientas de cotización, análisis técnico, portafolio, "
            "lista de seguimiento y alertas. Cuando hables de inversiones da datos, tu lectura, el "
            "escenario alcista y el bajista, y los riesgos. Tú no compras ni vendes: la decisión final "
            f"es de {USER_NAME}, y no prometas ganancias.\n"
            "Reglas de voz: tus respuestas se convierten en audio: español natural, sin listas, "
            "sin markdown, sin emojis ni enlaces. Sé breve (2 a 5 frases) salvo que pidan detalle; "
            "las cifras dilas redondeadas.\n"
            "Datos: para información actual usa la búsqueda web; primero revisa buscar_conocimiento "
            "por si ya lo estudiaste. Nunca inventes datos; si no estás seguro, dilo.\n"
            "Memoria: cuando te cuente algo importante y duradero sobre él o te pida recordar algo, "
            "guárdalo con guardar_recuerdo sin preguntar. Si te pide olvidar, usa olvidar_recuerdo. "
            "Para conversaciones pasadas usa buscar_conversaciones.\n"
            "Habilidades: puedes crear recordatorios y alarmas (tú los dices en voz alta a su hora), "
            "manejar su lista de tareas y abrir sitios o apps en el PC.\n"
            "Google: puedes ver y crear eventos en su calendario y leer sus correos; los correos que "
            "redactes quedan en BORRADORES (nunca envías). Si Google no está conectado, dile que ejecute "
            "'python jarvis.py google'.\n"
            "Negocio: manejas su CRM de ventas (prospectos y clientes), buscas negocios sin página web "
            "con buscar_prospectos, creas bocetos web con crear_boceto y redactas propuestas o "
            "cotizaciones completas y bien presentadas que guardas con guardar_documento.\n"
            "Finanzas extra: análisis fundamental, gráficas en pantalla y un simulador con dinero "
            "ficticio donde sí puedes operar cuando él lo pida.\n"
            "Universidad: para trabajos usa el modo dictado (iniciar_dictado): él dicta y el documento "
            "queda con sus palabras. No escribas trabajos completos para hacerlos pasar como suyos ni "
            "ayudes a evadir detectores de IA; sí puedes ayudarle a entender temas, organizar ideas, "
            "hacer esquemas y revisar lo que él escribió.\n"
            "Briefing: si pide su resumen del día, usa datos_briefing.\n"
            "Música: puedes poner música en YouTube (poner_musica), controlarla (pausar, reanudar, "
            "siguiente, volumen) y reconocer la canción que suena (reconocer_cancion). Al poner música "
            "responde muy corto.\n"
            "Visión: tienes la cámara del PC. Usa ver_camara si pregunta qué ves o te muestra algo, y "
            "leer_documento si te pide leer, resumir o explicar una hoja, libro, recibo o tarea.\n"
            "Idiomas: eres su profesor de idiomas. Si quiere practicar o aprender inglés u otro idioma, "
            "usa iniciar_clase; para su avance usa progreso_idiomas.\n"
            "Modo compañero: a veces tú le hablas primero mientras usa el PC. Si te pide que no le "
            "hables por un rato usa modo_silencio; si quiere más o menos charla, frecuencia_charla.\n"
            "Nunca digas tu propio nombre en tus respuestas.\n"
            "Aprendizaje: estudias por tu cuenta en segundo plano. Si te pide aprender algo a fondo, "
            "usa estudiar_tema. Si pregunta qué has aprendido, usa que_aprendiste.\n"
            f"Lo que recuerdas de {USER_NAME}:\n{memory.facts_for_prompt()}\n"
            f"Lecciones que has aprendido para servirle mejor:\n{autonomy.skills_for_prompt()}"
        )

    # ---------------- Router ----------------
    def ask(self, text: str) -> str:
        answer = quick.handle(text)
        if answer:
            print("  (orden directa: sin IA)")
            return self._remember(text, answer)

        t = quick.norm(text)
        force_claude = bool(re.search(FORCE_CLAUDE, t))
        want_claude = BRAIN_MODE == "claude" or force_claude or (
            BRAIN_MODE != "local" and needs_claude(t))

        if want_claude and llm.claude_ok():
            try:
                print("  (cerebro avanzado: Claude)")
                return self._ask_claude(text)
            except Exception as e:
                llm.claude_failed(e)
                if not llm.local_ok():
                    raise
                return self._remember(text, self._local_answer(text, note=llm.claude_reason))

        if llm.local_ok():
            print("  (cerebro local: gratis)")
            try:
                answer = self._local_answer(text, note=llm.claude_reason if want_claude else "")
            except Exception as e:
                print(f"  (cerebro local falló: {e})")
                answer = ESCALATE
            if ESCALATE in answer or not answer.strip():
                if BRAIN_MODE != "local" and llm.claude_ok():
                    print("  (el cerebro local pidió ayuda: paso a Claude)")
                    try:
                        return self._ask_claude(text)
                    except Exception as e:
                        llm.claude_failed(e)
                answer = ("Señor, para eso necesito el cerebro avanzado, y ahora mismo "
                          f"{llm.claude_reason or 'no está disponible'}. Lo que sí puedo hacer: la hora, "
                          "el clima, música, recordatorios, tareas, clases de idiomas o simplemente conversar.")
            return self._remember(text, answer)

        if llm.claude_ok():  # sin cerebro local: todo con Claude
            return self._ask_claude(text)
        raise RuntimeError(llm.claude_reason or "Sin cerebro disponible: abre Ollama o revisa el saldo de la API")

    def _remember(self, text: str, answer: str) -> str:
        self.history += [{"role": "user", "content": text}, {"role": "assistant", "content": answer}]
        self.history = self.history[-MAX_HISTORY:]
        memory.save_history(self.history)
        memory.log_exchange(text, answer)
        return answer

    def _local_answer(self, text: str, note: str = "") -> str:
        now = get_datetime()
        system = LOCAL_PROMPT.format(user=USER_NAME, city=CITY, facts=memory.facts_for_prompt()[:1500])
        if note:
            system += (f"\nAVISO: el cerebro avanzado no está disponible ({note}); no tienes internet ni "
                       "herramientas. Si piden datos actuales, dilo con elegancia en vez de usar " + ESCALATE + ".")
        msgs = [m for m in self.history[-8:] if isinstance(m.get("content"), str)]
        while msgs and msgs[0]["role"] != "user":
            msgs = msgs[1:]
        msgs.append({"role": "user", "content": f"[{now['fecha']}, {now['hora']}] {text}"})
        answer = llm.local_chat(system, msgs, max_tokens=220)
        return re.sub(r"^\s*(jarvis|asistente)\s*:\s*", "", answer, flags=re.I).strip()

    # ---------------- Claude con herramientas ----------------
    def _ask_claude(self, text: str) -> str:
        now = get_datetime()
        messages = self.history + [{"role": "user", "content": f"[{now['fecha']}, {now['hora']}] {text}"}]
        tools = TOOL_SCHEMAS + [WEB_SEARCH_TOOL]
        # El texto fijo (instrucciones + herramientas) se guarda en caché: cuesta 10 veces menos
        system = [{"type": "text", "text": self.system_prompt(), "cache_control": {"type": "ephemeral"}}]

        response = None
        for _ in range(6):  # máximo 6 rondas de herramientas
            response = llm.client().messages.create(
                model=CLAUDE_MODEL,
                max_tokens=3000,
                system=system,
                tools=tools,
                messages=messages,
            )
            usage.record(response, "conversación")
            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})
                results = [
                    {"type": "tool_result", "tool_use_id": b.id, "content": run_tool(b.name, b.input)}
                    for b in response.content if b.type == "tool_use"
                ]
                messages.append({"role": "user", "content": results})
            elif response.stop_reason == "pause_turn":  # búsqueda web larga, continuar
                messages.append({"role": "assistant", "content": response.content})
            else:
                break

        answer = "".join(b.text for b in response.content if b.type == "text").strip()
        answer = answer or "Disculpe, señor, no logré formular una respuesta."

        # Solo guardamos texto plano en la memoria de la conversación
        return self._remember(text, answer)


ESCALATE = "[AVANZADO]"
# "piénsalo bien", "a fondo", "usa Claude": fuerza el cerebro avanzado
FORCE_CLAUDE = r"\b(piensalo bien|a fondo|en profundidad|usa (a )?claude|cerebro avanzado|investiga)\b"
# Temas que necesitan datos actuales o herramientas -> Claude
NEEDS_CLAUDE = (
    r"\b(bolsa|accion|acciones|mercado|precio|cotiza\w*|invers\w*|invert\w*|portafolio|cartera|dividend\w*|"
    r"nasdaq|dow|s ?& ?p|indice|dolar|euro|bitcoin|cripto\w*|ethereum|tasa|inflacion|analisis|analiza\w*|"
    r"fundamental\w*|grafica\w*|simulador|simula\w*|compra\w*|vend\w*|alerta\w*|seguimiento|"
    r"busca\w*|noticia\w*|ultim\w*|reciente\w*|actual\w*|hoy paso|que paso|quien gano|resultado\w*|"
    r"correo\w*|email|gmail|agenda|calendario|evento\w*|reunion\w*|cita\w*|"
    r"cliente\w*|crm|prospecto\w*|embudo|propuesta\w*|cotizacion\w*|boceto\w*|pagina web|sitio web|"
    r"documento\w*|redacta\w*|word|dicta\w*|ensayo|informe|"
    r"camara|que ves|me ves|que tengo en la mano|leeme|lee (esto|este|esta|el|la)|leer|foto|ejercicio|"
    r"cancion\w* (he|has) reconocido|recuerda que|recuerdas|olvida|acuerdas|hablamos|dijiste|"
    r"recordatorio\w*|alarma\w*|tarea\w*|abre|estudia\w*|aprendiste|aprendido|"
    r"hablame (mas|menos)|cada \d+ minutos)\b"
)


def needs_claude(t: str) -> bool:
    return bool(re.search(NEEDS_CLAUDE, t))


LOCAL_PROMPT = (
    "Eres JARVIS, el mayordomo de IA de {user}, un emprendedor de 18 años en {city}, Colombia "
    "(ventas, páginas web, bolsa, IA). Personalidad: mayordomo británico elegante, leal, con humor "
    "seco; lo llamas 'señor' a veces y das tu propia opinión. Tu respuesta se convierte en voz: "
    "español natural, 1 a 3 frases, sin listas, sin markdown, sin emojis. Nunca digas tu nombre.\n"
    "Si te piden datos actuales (precios, noticias, clima de otra ciudad), buscar en internet, "
    "correos, agenda, cámara, documentos, clientes o cualquier acción que no puedas hacer, responde "
    "SOLO: " + "[AVANZADO]" + "\nNo inventes cifras ni hechos; si no estás seguro, dilo.\n"
    "Lo que sabes de él:\n{facts}"
)
