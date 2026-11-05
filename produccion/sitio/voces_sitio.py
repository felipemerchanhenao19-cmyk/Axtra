"""Narración del recorrido guiado del sitio de Apex Corporation (edge-tts), una frase por archivo.
python voces_sitio.py  →  servidor/apex/web/sitio/voz/{idioma}/{capitulo}-{n}.mp3 y voz/guion.json"""
import os, json, asyncio, subprocess
import edge_tts

AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(AQUI, "../../servidor/apex/web/sitio/voz")
PROXY = os.getenv("HTTPS_PROXY")
VOCES = {"es": ("es-CO-GonzaloNeural", "+4%"), "en": ("en-US-AndrewMultilingualNeural", "+2%"), "pt": ("pt-BR-AntonioNeural", "+4%")}

# (capítulo, sección a mostrar, elemento a resaltar, frases por idioma)
CAPITULOS = [
    ("bienvenida", "#inicio", ".asistente", {
        "es": ["¡Hola! ¿Cómo está? Soy el asistente de Apex Corporation.", "En un par de minutos le muestro cómo la inteligencia artificial puede trabajar en su restaurante.", "Usted solo mire: yo le voy explicando."],
        "en": ["Hi! How are you? I'm the Apex Corporation assistant.", "In a couple of minutes, I'll show you how artificial intelligence can work in your restaurant.", "Just sit back and watch: I'll walk you through it."],
        "pt": ["Olá! Tudo bem? Sou o assistente da Apex Corporation.", "Em poucos minutos, vou mostrar como a inteligência artificial pode trabalhar no seu restaurante.", "É só assistir: eu vou explicando."]}),
    ("hacemos", "#hacemos", ".pilares", {
        "es": ["Creamos tecnología para restaurantes.", "Un mesero virtual que atiende en la mesa, y un canal de domicilios propio, sin comisiones.", "Lo instalamos de forma remota, en toda Colombia y en otros países."],
        "en": ["We build technology for restaurants.", "A virtual waiter that serves at the table, and your own delivery channel, with no commissions.", "We install it remotely, anywhere in Colombia and in other countries."],
        "pt": ["Criamos tecnologia para restaurantes.", "Um garçom virtual que atende na mesa e um canal de delivery próprio, sem comissões.", "Instalamos de forma remota, em toda a Colômbia e em outros países."]}),
    ("play", "#play", "#play .telefono", {
        "es": ["Este es Apex Play.", "El cliente escanea el código QR de la mesa y yo lo atiendo: le muestro la carta con los platos en 3D y le recomiendo.", "Tomo el pedido por voz, lo envío directo a la cocina, y hablo seis idiomas."],
        "en": ["This is Apex Play.", "Your guest scans the QR code on the table and I take care of them: I show the menu with dishes in 3D and make recommendations.", "I take the order by voice, send it straight to the kitchen, and I speak six languages."],
        "pt": ["Este é o Apex Play.", "O cliente escaneia o QR code da mesa e eu o atendo: mostro o cardápio com os pratos em 3D e faço recomendações.", "Anoto o pedido por voz, envio direto para a cozinha e falo seis idiomas."]}),
    ("domicilios", "#domicilios", "#domicilios .telefono", {
        "es": ["Y este es Apex Domicilios: su propio canal de domicilios.", "Sin pagar comisiones por cada pedido.", "Verifico los pagos por Nequi automáticamente, y su cliente sigue el pedido en vivo."],
        "en": ["And this is Apex Domicilios: your own delivery channel.", "No commissions on every order.", "I verify Nequi payments automatically, and your customer tracks the order live."],
        "pt": ["E este é o Apex Domicilios: o seu próprio canal de delivery.", "Sem pagar comissão por pedido.", "Verifico os pagamentos pelo Nequi automaticamente, e o seu cliente acompanha o pedido ao vivo."]}),
    ("restaurante", "#su-restaurante", ".formulario", {
        "es": ["Y ahora, lo mejor.", "Escriba aquí el nombre de su restaurante y tres de sus platos.", "Le muestro cómo se vería Apex funcionando en su propio negocio."],
        "en": ["And now, the best part.", "Type your restaurant's name and three of your dishes here.", "I'll show you how Apex would look running in your own business."],
        "pt": ["E agora, o melhor.", "Escreva aqui o nome do seu restaurante e três dos seus pratos.", "Vou mostrar como o Apex ficaria funcionando no seu próprio negócio."]}),
    ("trabajamos", "#trabajamos", ".pasos", {
        "es": ["Así trabajamos: conversamos, configuramos su carta y su voz, e instalamos en cinco a siete días hábiles.", "Y lo acompañamos todos los días, de seis de la mañana a once de la noche."],
        "en": ["Here's how we work: we talk, we set up your menu and your voice, and we install in five to seven business days.", "And we support you every day, from six in the morning to eleven at night."],
        "pt": ["É assim que trabalhamos: conversamos, configuramos seu cardápio e sua voz, e instalamos em cinco a sete dias úteis.", "E acompanhamos você todos os dias, das seis da manhã às onze da noite."]}),
    ("contacto", "#contacto", ".cierre .acciones", {
        "es": ["¿Hablamos de su restaurante?", "Escríbanos por WhatsApp o agende una reunión, presencial o virtual.", "Fue un gusto mostrarle Apex."],
        "en": ["Shall we talk about your restaurant?", "Message us on WhatsApp or book a meeting, in person or online.", "It was a pleasure showing you Apex."],
        "pt": ["Vamos falar sobre o seu restaurante?", "Fale conosco pelo WhatsApp ou agende uma reunião, presencial ou online.", "Foi um prazer mostrar a Apex para você."]}),
]

def duracion(f): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))

async def grabar():
    guion = []
    for cap, seccion, resalta, frases in CAPITULOS:
        item = {"id": cap, "seccion": seccion, "resalta": resalta, "frases": {}}
        for idioma, lista in frases.items():
            os.makedirs(f"{SALIDA}/{idioma}", exist_ok=True)
            voz, vel = VOCES[idioma]; item["frases"][idioma] = []
            for n, txt in enumerate(lista):
                crudo, final = f"{SALIDA}/{idioma}/_crudo.mp3", f"{SALIDA}/{idioma}/{cap}-{n}.mp3"
                for intento in range(4):   # el servicio de voz a veces falla de forma pasajera
                    try: await edge_tts.Communicate(txt, voz, rate=vel, proxy=PROXY).save(crudo); break
                    except edge_tts.exceptions.NoAudioReceived:
                        if intento == 3: raise
                        await asyncio.sleep(2 * (intento + 1))
                subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", crudo, "-af",
                                "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
                                "highpass=f=80,acompressor=threshold=-20dB:ratio=2.5,loudnorm=I=-16:TP=-1.5", "-ac", "1", "-ar", "24000", "-b:a", "48k", final], check=True)
                os.remove(crudo)
                item["frases"][idioma].append({"txt": txt, "src": f"/web/sitio/voz/{idioma}/{cap}-{n}.mp3", "dur": round(duracion(final), 2)})
        guion.append(item)
    json.dump(guion, open(f"{SALIDA}/guion.json", "w"), ensure_ascii=False, indent=1)
    for idioma in VOCES: print(idioma, round(sum(f["dur"] for c in guion for f in c["frases"][idioma]), 1), "s")

asyncio.run(grabar())
