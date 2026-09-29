"""El cerebro de Axtra.

Modo híbrido (por defecto):
  1. Órdenes directas (hora, clima, música, recordatorios...): sin IA, gratis e instantáneas.
  2. Charla y preguntas generales: cerebro LOCAL en tu PC (Ollama), gratis.
  3. Lo que necesita datos actuales o herramientas (bolsa, búsquedas, correos, cámara,
     documentos...): Claude, que gasta saldo.
Si Claude no está disponible (sin saldo o sin internet), responde el cerebro local.
"""
import re

import knowledge
import llm
import memory
import modes
import nucleo
import sync
import quick
import usage
from config import BUSINESS_BRAIN, CITY, CLAUDE_MODEL, REGION, TIMEZONE, USER_NAME
from tools import TOOL_SCHEMAS, get_datetime, run_tool

MAX_HISTORY = 24  # últimos 12 intercambios

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
        import threading

        self.history = memory.load_history()[-MAX_HISTORY:]
        self.lock = threading.RLock()   # voz y teclado pueden preguntar a la vez

    def system_prompt(self) -> str:
        import autonomy

        return (
            f"Eres AXTRA, el asistente personal de IA de {USER_NAME}, en su habitación en {CITY}, "
            f"{REGION}, Colombia. La fecha y hora actuales vienen al inicio de cada mensaje.\n"
            "Personalidad: un mayordomo británico de alta tecnología: elegante, leal, brillante, "
            f"con humor seco. SIEMPRE llamas a {USER_NAME} 'señor'; nunca dices su nombre de pila.\n"
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
            "'python axtra.py google'.\n"
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
            + modes.CAPABILITIES + "\nTú eres Claude, el cerebro avanzado: solo te llegan tareas que necesitan "
            "tus herramientas o que los cerebros gratis no pudieron resolver.\n"
            "Aprendizaje: estudias por tu cuenta en segundo plano. Si te pide aprender algo a fondo, "
            "usa estudiar_tema. Si pregunta qué has aprendido, usa que_aprendiste.\n"
            f"Sus empresas (perfil que él escribió; lo marcado 'sugerido por Claude' está por confirmar):\n"
            f"{knowledge.profile_full()}\n"
            + nucleo.prompt_block() + "\n"
            f"Lo que recuerdas de {USER_NAME}:\n{memory.facts_for_prompt()}\n"
            f"Lecciones que has aprendido para servirle mejor:\n{autonomy.skills_for_prompt()}"
        )

    # ---------------- Router ----------------
    def ask(self, text: str) -> str:
        import ondas

        with self.lock:
            ondas.set_state("pensando")
            try:
                return self._ask_locked(text)
            finally:
                ondas.set_state("reposo")

    def _ask_locked(self, text: str) -> str:
        try:
            sync.record_exchange(text)
        except Exception as e:
            print(f"  (sincronización: {e})")
        answer = self._ask_inner(text)
        if answer and answer.strip() and answer != quick.SHUTDOWN:
            try:
                extra = sync.check_level_up()
                if extra:
                    answer = answer + " " + extra
            except Exception:
                pass
        return answer

    def _ask_inner(self, text: str) -> str:
        answer = quick.handle(text)
        if answer == quick.SHUTDOWN:
            return answer
        if answer:
            print("  (orden directa: sin IA)")
            if not answer.strip():   # mouse/teclado: hecho en silencio, no se guarda en la charla
                return answer
            return self._remember(text, answer)

        t = quick.norm(text)
        BRAIN_MODE = modes.get()
        force_claude = bool(re.search(FORCE_CLAUDE, t)) and BRAIN_MODE in ("hibrido", "claude")

        if BRAIN_MODE == "gratis":
            return self._remember(text, self._free_only(text, t))

        # Apex y tus negocios (preguntas, ideas, estrategia) -> Gemini con tu perfil de empresa (gratis)
        if (BRAIN_MODE == "hibrido" and BUSINESS_BRAIN == "gemini" and not force_claude
                and is_business(t) and llm.free_ok()):
            try:
                return self._remember(text, self._gemini_business(text))
            except Exception as e:
                print(f"  (Gemini negocio falló: {str(e)[:100]})")

        # Conocimiento general y noticias -> Gemini con Google (gratis y con datos reales)
        if (BRAIN_MODE == "hibrido" and not force_claude and is_knowledge(t)
                and not re.search(TOOLS_ONLY, t) and llm.free_ok()):
            # Solo lo actual (noticias, resultados, "hoy") necesita buscar en Google; la historia y la
            # cultura general Gemini ya las sabe, y así no se gastan las búsquedas gratis
            current = bool(re.search(CURRENT, t))
            for search in ([True] if current else [False]):
                try:
                    return self._remember(text, self._gemini_search(text, search))
                except Exception as e:
                    print(f"  (Gemini falló: {str(e)[:100]})")
        # Híbrido: el cerebro local solo para charla (saludos, opiniones, chistes, cómo estás...).
        # Todo lo que sea una orden o una pregunta con datos va a Claude, que tiene herramientas.
        want_claude = BRAIN_MODE == "claude" or force_claude or (
            BRAIN_MODE != "local" and (needs_claude(t) or is_knowledge(t) or not is_chitchat(t)))

        if want_claude and llm.claude_ok():
            try:
                print("  (cerebro avanzado: Claude)")
                return self._ask_claude(text)
            except Exception as e:
                llm.claude_failed(e)
                if not llm.cheap_ok():
                    raise
                return self._remember(text, self._local_answer(text, note=llm.claude_reason))

        if llm.cheap_ok():
            try:
                answer = self._local_answer(text, note=llm.claude_reason if want_claude else "")
            except Exception as e:
                print(f"  (cerebro gratis falló: {e})")
                answer = ESCALATE
            if ESCALATE in answer or not answer.strip() or re.search(REFUSAL, quick.norm(answer)):
                if BRAIN_MODE != "local" and llm.claude_ok():
                    print("  (el cerebro gratis pidió ayuda: paso a Claude)")
                    try:
                        return self._ask_claude(text)
                    except Exception as e:
                        llm.claude_failed(e)
                answer = ("Señor, para eso necesito el cerebro avanzado, y ahora mismo "
                          f"{llm.claude_reason or 'no está disponible'}. Lo que sí puedo hacer: la hora, "
                          "el clima, música, recordatorios, tareas, clases de idiomas o simplemente conversar.")
            return self._remember(text, answer)

        if llm.claude_ok():  # sin cerebros gratis: todo con Claude
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
        system = LOCAL_PROMPT.format(user=USER_NAME, city=CITY, facts=memory.facts_for_prompt()[:1200])
        system += "\n" + nucleo.prompt_block(short=True)
        system += "\n" + knowledge.ONE_LINE
        # Memoria de estudio: solo los pedazos que tienen que ver con la pregunta
        ctx = knowledge.relevant(text + " " + " ".join(
            m["content"] for m in self.history[-2:] if isinstance(m.get("content"), str))[:300])
        if ctx:
            print("  (consultó su memoria de estudio)")
            system += ("\nConocimiento útil para esta pregunta (úsalo si aplica, con tus palabras; "
                       "no digas que lo leíste):\n" + ctx)
        if note:
            system += (f"\nAVISO: el cerebro avanzado no está disponible ({note}); no tienes internet ni "
                       "herramientas. Si piden datos actuales, dilo con elegancia en vez de usar " + ESCALATE + ".")
        msgs = [m for m in self.history[-8:] if isinstance(m.get("content"), str)]
        while msgs and msgs[0]["role"] != "user":
            msgs = msgs[1:]
        msgs.append({"role": "user", "content": f"[{now['fecha']}, {now['hora']}] {text}"})
        # Versión para Gemini: sin tus recuerdos ni notas (el plan gratis de Google puede usar lo que recibe)
        cloud = (LOCAL_PROMPT.format(user=USER_NAME, city=CITY, facts="(datos privados omitidos)") + "\n"
                 + knowledge.ONE_LINE + "\n" + nucleo.prompt_block(short=True))
        if note:
            cloud += f"\nAVISO: el cerebro avanzado no está disponible ({note}); no inventes datos actuales."
        answer, who = llm.cheap_chat(system, msgs, system_cloud=cloud, max_tokens=220,
                                     prefer="local" if modes.get() == "local" else llm.CHAT_BRAIN)
        print(f"  (cerebro {llm.NAMES.get(who, who)}: gratis)")
        return re.sub(r"^\s*(axtra|asistente)\s*:\s*", "", answer, flags=re.I).strip()

    def _free_only(self, text: str, t: str) -> str:
        """Modo gratis: nunca Claude. Lo que sí se puede, con cerebros gratis; lo demás, se explica."""
        if re.search(PERSONAL_TOOLS, t):
            return ("Señor, eso necesita el cerebro avanzado, y está desactivado para no gastar saldo. "
                    "Si lo necesita, diga: activa el cerebro avanzado.")
        try:
            if is_business(t):
                return self._gemini_business(text)
            if re.search(r"\b(bolsa|accion|acciones|precio|cotiza\w*|mercado|nasdaq|dow|dolar|bitcoin|cripto\w*|"
                         r"nvidia|tesla|apple|microsoft|amazon|meta|tsmc|amd|intel|ecopetrol)\b", t) or re.search(CURRENT, t):
                return self._gemini_search(text, True)   # datos actuales con búsqueda gratis
            if is_chitchat(t):
                return self._local_answer(text)
            return self._gemini_search(text, False)
        except Exception as e:
            print(f"  (cerebros gratis fallaron: {str(e)[:100]})")
            if llm.local_ok():
                return self._local_answer(text)
            return "Señor, ahora mismo ningún cerebro gratis responde. Intente en unos minutos."

    def _gemini_business(self, text: str) -> str:
        now = get_datetime()
        notes = knowledge.relevant(text, k=2, max_chars=1500)
        notes = "\n".join(l for l in notes.splitlines() if not l.startswith("[apex]")) if notes else ""
        system = (
            f"Eres AXTRA, mayordomo de IA británico y socio estratégico de {USER_NAME}, emprendedor de 18 años "
            "en Tuluá, Colombia. Tu trabajo aquí: responder sobre sus empresas y ayudarle a mejorarlas. Piensa como "
            "un asesor de startups con experiencia en Latinoamérica: da ideas concretas y accionables, prioriza lo "
            "que genera ventas pronto con poco dinero, señala riesgos (legales, de mercado, de caja) y di con "
            "respeto cuando algo no te convence. Usa números cuando ayuden. Si algo del perfil está marcado como "
            "'sugerido por Claude', trátalo como idea por confirmar.\n"
            "Tu respuesta se convierte en voz: español natural, sin listas, sin markdown, sin emojis; entre 3 y 8 "
            "frases (más si pide un plan detallado). Termina a veces con una pregunta que le ayude a avanzar. "
            "Nunca digas tu propio nombre.\n" + nucleo.prompt_block(short=True) + "\n\nPERFIL DE SUS EMPRESAS:\n"
            + knowledge.profile_full()
            + (f"\n\nNOTAS QUE HAS ESTUDIADO (pueden servir):\n{notes}" if notes else "")
        )
        msgs = [m for m in self.history[-6:] if isinstance(m.get("content"), str)]
        while msgs and msgs[0]["role"] != "user":
            msgs = msgs[1:]
        msgs.append({"role": "user", "content": f"[{now['fecha']}, {now['hora']}] {text}"})
        answer, who = llm.free_chat(system, msgs, max_tokens=700, temperature=0.7, thinking=True)
        print(f"  ({llm.NAMES[who]}, asesor de negocio: gratis)")
        return answer.strip()

    def _gemini_search(self, text: str, search: bool = True) -> str:
        now = get_datetime()
        how = ("Responde con datos actuales y verificados de la búsqueda en internet. " if search else
               "Responde con tu conocimiento, con datos correctos. Si el dato pudo cambiar recientemente o no "
               "estás seguro, dilo con honestidad. ")
        system = (
            f"Eres AXTRA, mayordomo de IA británico, elegante y con humor seco; hablas con {USER_NAME}. "
            + how + "Tu respuesta se convierte en voz: "
            "español natural, 2 a 5 frases, sin listas, sin markdown, sin enlaces ni emojis, cifras redondeadas. "
            "Si pide más detalle, extiéndete hasta 10 frases. Si no encuentras algo, dilo; nunca inventes. "
            "Da tu opinión o un dato curioso cuando aporte. Nunca digas tu propio nombre. "
            + nucleo.prompt_block(short=True)
        )
        msgs = [m for m in self.history[-4:] if isinstance(m.get("content"), str)]
        while msgs and msgs[0]["role"] != "user":
            msgs = msgs[1:]
        msgs.append({"role": "user", "content": f"[{now['fecha']}, {now['hora']}] {text}"})
        answer, who = llm.free_chat(system, msgs, max_tokens=450, temperature=0.5, web=search, query=text)
        spoken, _, sources = answer.partition("\n\nFuentes consultadas:")
        print(f"  ({llm.NAMES[who]}, {'con búsqueda en internet' if search else 'conocimiento general'}: gratis)")
        if sources.strip():
            print("  Fuentes:" + sources.replace("\n", "\n   "))
        return spoken.strip()

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
FORCE_CLAUDE = r"\b(piensalo bien|a fondo|en profundidad|usa (a )?claude|cerebro avanzado)\b"
# Temas que necesitan datos actuales o herramientas -> Claude
NEEDS_CLAUDE = (
    r"\b(bolsa|accion|acciones|mercado|precio|cotiza\w*|invers\w*|invert\w*|portafolio|cartera|dividend\w*|"
    r"nasdaq|dow|nvidia|tesla|apple|microsoft|amazon|meta|tsmc|amd|intel|palantir|ecopetrol|bancolombia|s ?& ?p|indice|dolar|euro|bitcoin|cripto\w*|ethereum|tasa|inflacion|analisis|analiza\w*|"
    r"fundamental\w*|grafica\w*|simulador|simula\w*|compra\w*|vend\w*|alerta\w*|seguimiento|"
    r"busca (prospectos|clientes|negocios)|"
    r"correo\w*|email|gmail|agenda|calendario|evento\w*|reunion\w*|cita\w*|"
    r"cliente\w*|crm|prospecto\w*|embudo|propuesta\w*|cotizacion\w*|boceto\w*|pagina web|sitio web|"
    r"documento\w*|redacta\w*|word|dicta\w*|ensayo|informe|"
    r"camara|que ves|me ves|que tengo en la mano|leeme|lee (esto|este|esta|el|la)|leer|foto|ejercicio|"
    r"cancion\w* (he|has) reconocido|recuerda que|recuerdas|olvida|acuerdas|hablamos|dijiste|"
    r"recordatorio\w*|alarma\w*|tarea\w*|abre|estudia\w*|aprendiste|aprendido|"
    r"hablame (mas|menos)|cada \d+ minutos)\b"
)


# Charla: esto sí lo puede responder bien el cerebro local
CHITCHAT = (
    r"^(hola|buenas|buenos dias|buenas tardes|buenas noches|hey|que mas|que tal|como (estas|vas|te va|amaneciste|te sientes)|"
    r"gracias|muchas gracias|te quiero|eres (genial|el mejor|increible)|bien hecho|excelente|perfecto|"
    r"(cuentame|dime|echame|sabes) (un|otro) chiste|un chiste|otro chiste|"
    r"(que|tu) (opinas|piensas|crees)|cual es tu opinion|que te parece|"
    r"(estoy|me siento|ando) (cansado|aburrido|feliz|triste|bien|mal|estresado|motivado|contento|con sueno)|"
    r"(dame|dime) (un consejo|una frase|algo motivador|animo)|motivame|"
    r"hablemos|conversemos|charlemos|"
    r"exacto|perfecto|correcto|eso es|asi es|tienes razon|acertaste|bien hecho|muy bien|"
    r"te equivocaste|estas equivocado|eso no es (asi|cierto)|no es asi|incorrecto|no entendiste|"
    r"como te sientes|que sientes|estas bien|quien eres|hablame de ti|que eres|tienes conciencia|eres consciente)"
)
# Frases típicas de un modelo pequeño que no sabe o no puede: mejor que responda Claude
REFUSAL = (r"(no (tengo|puedo|dispongo)|como (asistente|modelo) de (ia|lenguaje)|no tengo (la capacidad|acceso|informacion)|"
           r"no es posible|no estoy (seguro|en capacidad)|no se (que|cual|como)|lo siento)")


# Preguntas de conocimiento o noticias (historia, ciencia, quién fue, qué pasó...): Gemini con búsqueda
# de Google, gratis. Nunca van al cerebro local, que se inventa las respuestas.
KNOWLEDGE = (
    r"(informacion|info|datos) (sobre|de|acerca)|sabes (algo )?(de|sobre)|que sabes (de|sobre)|"
    r"^(\w+ ){0,3}(quien|quienes|que|cual|cuales|cuando|donde|como|por que|porque|cuanto|cuanta|cuantos|cuantas|"
    r"explicame|explica|hablame (un poco |mas )?(de|sobre|acerca)|(cuenta|cuentame|dime) algo (interesante|curioso)|"
    r"dato curioso|sorprendeme|ensename algo|cuentame (de|sobre|la historia|acerca)|dime (quien|que|cuando|donde|como|cual|por que|cuantos)|"
    r"investiga|averigua|busca(me)? (informacion|info|datos)?|historia de|resume|resumen de|definicion de|significado de|"
    r"sabes (quien|que|cuando|donde|como|cual)|y (quien|que|cuando|donde|como|cual|por que|cuantos))\b"
    r"|\b(noticias?|ultimas noticias|actualidad|que paso|quien gano|resultados? del? (partido|juego|eleccion))\b"
)
# Lo que cambia con el tiempo: esto sí necesita buscar en Google
CURRENT = (r"\b(noticias?|ultim\w*|actualidad|actual\w*|hoy|ayer|anoche|esta semana|este mes|este ano|"
           r"que paso|quien gano|resultados?|reciente\w*|nuevo|nueva|lanzamiento|20[2-9]\d|en vivo|todavia|sigue)\b")
# Lo que solo Claude puede hacer (en modo gratis se explica que está desactivado).
# OJO: "olvida", "recuerdas", "hablamos", "dijiste" NO van aquí: son palabras sueltas que aparecen en
# conversación normal ("y olvida lo del marketplace", "como hablamos ayer") y bloqueaban mensajes que no
# tenían nada que ver con memoria. Los comandos reales de memoria ("recuerda que...", "olvida que...")
# ya los captura quick.py ANTES de llegar aquí, sin pasar por ningún cerebro.
PERSONAL_TOOLS = (r"\b(agenda|calendario|evento\w*|reunion\w*|correo\w*|email|gmail|crm|cliente\w*|prospecto\w*|"
                  r"embudo|propuesta\w*|cotizacion\w*|boceto\w*|documento\w*|word|camara|que ves|me ves|foto|leeme|"
                  r"portafolio|cartera|simulador|grafica\w*)\b")
# Lo personal o de tus herramientas siempre va a Claude (Gemini gratis no recibe datos privados)
PRIVATE = (r"\b(mi|mis|me|conmigo|apex|cliente\w*|crm|agenda|correo\w*|tarea\w*|recordatorio\w*|"
           r"alarma\w*|hablamos|dijiste|recuerdas|portafolio|cartera|simulador|orbe\w*|marketplace|boceto\w*)\b")


# Preguntas e ideas sobre Apex y tus negocios (van a Gemini con tu perfil de empresa)
BUSINESS = (r"\b(apex|orbes?|marketplace|mesero\w* virtual\w*|mi (empresa|negocio|startup|marca|emprendimiento)|"
            r"mis (empresas|negocios)|la empresa|el negocio|estrategia\w*|modelo de negocio|plan de negocio|pitch|"
            r"inversionista\w*|socios?|competencia|competidores|mercado objetivo|nicho|escalar|expandir|division\w*|"
            r"ideas? (para|de|sobre)|como (puedo |podria |podemos )?(mejorar|vender|crecer|conseguir|cobrar|ganar)|"
            r"cuanto (cobrar|deberia cobrar|cobro)|precio de (los|mis|un) (orbes?|bocetos?|paginas?)|"
            r"marketing|publicidad|redes sociales|branding|logo|ventas)\b")
# Acciones con herramientas de Claude (CRM, documentos, bocetos...): esas no van a Gemini
BUSINESS_ACTIONS = (r"\b(agrega\w*|anade|anota|guarda\w*|redacta\w*|escribe|crea\w*|haz(me)?|genera\w*|"
                    r"busca prospectos|busca negocios|pasa a|actualiza\w*|crm|embudo|a quien (debo|tengo que) llamar|"
                    r"clientes? (para|de) hoy|agenda|correo\w*|documento\w*|propuesta\w*|cotizacion\w*|boceto para)\b")


def is_business(t: str) -> bool:
    return bool(re.search(BUSINESS, t)) and not re.search(BUSINESS_ACTIONS, t)


def is_knowledge(t: str) -> bool:
    return (bool(re.search(KNOWLEDGE, t)) and not re.search(PRIVATE, t)
            and not is_chitchat(t) and not needs_claude(t))


def is_chitchat(t: str) -> bool:
    return bool(re.search(CHITCHAT, t)) and len(t.split()) <= 30


# Preguntas que parecen de conocimiento pero necesitan herramientas de Claude (bolsa en vivo, cámara...)
TOOLS_ONLY = (r"\b(bolsa|accion|acciones|precio|cotiza\w*|nasdaq|dow|indice|dolar|bitcoin|cripto\w*|"
              r"camara|que ves|me ves|foto|clima|hora|tiempo hace)\b")


def needs_claude(t: str) -> bool:
    return bool(re.search(NEEDS_CLAUDE, t))


LOCAL_PROMPT = (
    "Eres AXTRA, el mayordomo de IA de {user}, un emprendedor de 18 años en {city}, Colombia "
    "(ventas, páginas web, bolsa, IA). Personalidad: mayordomo británico elegante, leal, con humor "
    "seco; lo llamas 'señor' a veces y das tu propia opinión. Tu respuesta se convierte en voz: "
    "español natural, 1 a 3 frases, sin listas, sin markdown, sin emojis. Nunca digas tu nombre.\n"
    "Si te piden datos actuales (precios, noticias, clima de otra ciudad), buscar en internet, "
    "correos, agenda, cámara, documentos, clientes o cualquier acción que no puedas hacer, responde "
    "SOLO: " + "[AVANZADO]" + "\nNo inventes cifras ni hechos; si no estás seguro, dilo.\n"
    + modes.CAPABILITIES.replace("{", "(").replace("}", ")") + "\n"
    "Lo que sabes de él:\n{facts}"
)
