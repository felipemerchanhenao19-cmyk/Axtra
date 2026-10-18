"""Guiones de la semana 1 en PDF: python guiones.py <salida.pdf>"""
import sys, os, asyncio, json, re
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
SAL = os.path.abspath(sys.argv[1])
FUENTES = open(AQUI + "../videos/fuentes.html").read()
JS = open(AQUI + "orbi.js").read()

V = [
 dict(n=1, dia="Lunes", titulo="Mesa 7, minuto 14", prod="Apex Play", dur="25 s", genero="Thriller de suspenso", tipo="Mixto: filmado + pantalla real", exp="enojado",
  idea="Un cliente lleva 14 minutos con la mano levantada. Orbi lo atiende en 10 segundos.",
  planos=[("0–2", "Negro. Barras de cine.", "Texto: «BASADO EN HECHOS REALES». Golpe grave."),
          ("2–5", "Detalle, cámara lenta: una mano levantada.", "Texto: «MESA 7 · MINUTO 14». Tic-tac de reloj y música de suspenso."),
          ("5–8", "Plano general: el mesero pasa de largo con cinco platos.", "El cliente baja la mano, derrotado."),
          ("8–10", "Cambio de foco del cliente al hablador QR de la mesa.", "La música se detiene. Silencio."),
          ("10–14", "Pantalla real del celular. Orbi aparece con su «ding».", "ORBI: «Buenas noches. ¿Qué se le antoja?»"),
          ("14–18", "Primer plano del cliente sonriendo. Orbi feliz.", "ORBI: «Enviado a cocina.» Texto: «10 SEGUNDOS»."),
          ("18–22", "El mesero llega jadeando, libreta en mano.", "MESERO: «¿Ya lo atendieron?» CLIENTE: «Sí. Orbi.» El mesero mira el celular con celos."),
          ("22–25", "Sello Apex.", "")],
  copy="La mesa 7 sobrevivió. ¿Y las suyas? 🙋"),
 dict(n=2, dia="Martes", titulo="La factura", prod="Apex Domicilios", dur="25 s", genero="Telenovela", tipo="Mixto: filmado + Orbi animado", exp="sarcastico",
  idea="El dueño descubre cuánto le cobró la app este mes. Drama. Violines. Orbi al rescate.",
  planos=[("0–2", "Negro.", "Texto: «UNA HISTORIA DE AMOR Y TRAICIÓN». Acorde de telenovela."),
          ("2–6", "El dueño mira el celular. Tres zoom dramáticos seguidos.", "Violín. Gesto de dolor exagerado."),
          ("6–9", "Pantalla completa: «27 %» gigante.", "DUEÑO (al celular): «¿Por qué me haces esto?»"),
          ("9–14", "Orbi entra flotando con un pañuelo.", "ORBI: «Ya, ya. Nadie debería pagar por cocinar.»"),
          ("14–19", "Pantalla real: un domicilio entra a la caja de Apex.", "Texto: «0 % DE COMISIÓN»."),
          ("19–22", "El dueño, digno, le habla a la app.", "DUEÑO: «No eres tú, soy yo… Bueno, no. Eres tú.»"),
          ("22–25", "Sello Apex.", "")],
  copy="Terminamos. Y esta vez es definitivo 💔 #ApexDomicilios"),
 dict(n=3, dia="Miércoles", titulo="El indeciso, en su hábitat natural", prod="Apex Play", dur="30 s", genero="Documental de naturaleza", tipo="Mixto: filmado + pantalla real", exp="orgulloso",
  idea="Orbi narra en susurros, como en un documental, la vida del cliente que nunca sabe qué pedir.",
  planos=[("0–2", "Negro.", "Texto: «APEX DOCUMENTALES PRESENTA»."),
          ("2–8", "Plano lento: un cliente lee la carta sin fin.", "ORBI (susurro): «Aquí observamos al indeciso común. Lleva veinte minutos en la misma página.»"),
          ("8–12", "Su acompañante bosteza.", "ORBI: «Su manada empieza a perder la paciencia.»"),
          ("12–20", "Pantalla real: Orbi recomienda y la torta gira en 3D.", "ORBI: «Y entonces… ocurre.»"),
          ("20–25", "Llegan a la mesa tres platos.", "ORBI: «Vino por un café. Pidió tres cosas. La naturaleza es sabia.»"),
          ("25–30", "Sello Apex.", "")],
  copy="Todos tenemos un amigo así. Etiquételo 👇"),
 dict(n=4, dia="Jueves", titulo="Uan bandeja paisa, plis", prod="Apex Play", dur="25 s", genero="Película de espías", tipo="Mixto: filmado + pantalla real", exp="guino",
  idea="Llega un turista. El mesero intenta hablar inglés. Orbi habla seis idiomas.",
  planos=[("0–2", "Negro.", "Texto: «MISIÓN: IMPOSIBLE… DE PEDIR». Música de espías."),
          ("2–8", "Turista en la mesa. El mesero, nervioso.", "MESERO: «Ehh… uan bandeja… güit frijols?» El turista no entiende nada."),
          ("8–12", "Orbi aparece en el celular.", "ORBI: «Permítame.» Luego, en inglés: «Good evening! Would you like the house special?»"),
          ("12–17", "Montaje rápido: la carta cambia a portugués, alemán y ruso.", "Un «ding» por cada idioma."),
          ("17–21", "El mesero, solo en la cocina, practica inglés en el celular.", "ORBI: «Tranquilo. Yo hablo seis.»"),
          ("21–25", "Sello Apex.", "")],
  copy="El inglés del mesero vs. el de Orbi 🌎"),
 dict(n=5, dia="Viernes", titulo="La entrevista", prod="Apex Play", dur="30 s", genero="Falso documental de oficina", tipo="Mixto: filmado + Orbi en pantalla", exp="orgulloso",
  idea="El dueño le hace una entrevista de trabajo a Orbi. Miradas a cámara incluidas.",
  planos=[("0–2", "Negro.", "Texto: «RECURSOS HUMANOS»."),
          ("2–6", "El dueño frente a un celular en un trípode, con Orbi en pantalla.", "DUEÑO: «¿Experiencia?» ORBI: «Atendí 40 mesas al mismo tiempo. Anoche.»"),
          ("6–10", "Primer plano de Orbi.", "DUEÑO: «¿Trabaja fines de semana?» ORBI: «¿Qué es un fin de semana?»"),
          ("10–15", "Orbi sarcástico.", "DUEÑO: «¿Se le olvidan los pedidos?» ORBI: «Siguiente pregunta.»"),
          ("15–20", "Plano de los dos.", "DUEÑO: «¿Cuánto pide de salario?» ORBI: «Menos de lo que se le pierde en una noche con la libreta.»"),
          ("20–23", "El dueño mira a cámara. Dos segundos de silencio.", ""),
          ("23–27", "Orbi feliz.", "DUEÑO: «¿Cuándo puede empezar?» ORBI: «Ya empecé. La mesa 3 pidió postre.»"),
          ("27–30", "Sello Apex.", "")],
  copy="Contratado. Sin preguntas 🤝 #ApexPlay"),
 dict(n=6, dia="Sábado", titulo="El plan", prod="Apex Corporation", dur="30 s", genero="Película de atracos", tipo="Filmado: detrás de cámaras con Felipe", exp="guino",
  idea="Así montamos un restaurante en cinco días, contado como el plan de un gran golpe.",
  planos=[("0–2", "Negro.", "Texto: «EL PLAN»."),
          ("2–6", "Escritorio en penumbra con fotos de la carta, como el plano de un banco.", "ORBI: «El objetivo: un restaurante. El plazo: cinco días.»"),
          ("6–12", "Montaje rápido con letreros por día.", "«DÍA 1: LA CARTA» · «DÍA 2: EL ASISTENTE» · «DÍA 3: LOS HABLADORES» · «DÍA 4: LA CAJA»."),
          ("12–20", "Cámara lenta: los habladores en las mesas y la gente escaneando.", "Música de tensión que sube."),
          ("20–25", "Llega el primer pedido real a la caja. «Ding». Celebración contenida.", "ORBI: «Nadie salió herido. Excepto la libreta.»"),
          ("25–30", "Sello Apex.", "Texto: «¿SU RESTAURANTE ES EL PRÓXIMO?»")],
  copy="Cinco días. Un restaurante. Cero libretas 🎯"),
 dict(n=7, dia="Domingo", titulo="El juicio a la libreta", prod="Apex Play y Domicilios", dur="30 s", genero="Drama de tribunales", tipo="Mixto: filmado + Orbi animado", exp="enojado",
  idea="La libreta del mesero va a juicio por todos sus crímenes. Orbi es el fiscal.",
  planos=[("0–2", "Negro.", "Texto: «CASO N.º 001: EL PUEBLO CONTRA LA LIBRETA»."),
          ("2–6", "Una libreta sola sobre una mesa, con luz dramática desde arriba.", "Golpe de martillo."),
          ("6–14", "Orbi de fiscal, con lentes.", "ORBI: «Su señoría: la acusada perdió tres pedidos solo el sábado. Confundió "
           "«sin cebolla» con «con cebolla». Y su letra… nadie la entiende.»"),
          ("14–18", "Prueba: una hoja de libreta con garabatos ilegibles. Zoom.", "Murmullos en la sala."),
          ("18–22", "Silencio. Una página se mueve con el viento.", "ORBI: «¿Cómo se declara la acusada?»"),
          ("22–26", "El dueño, de juez.", "JUEZ: «Culpable. Sentenciada… a anotar el mercado.» Martillo."),
          ("26–30", "Sello Apex.", "")],
  copy="Justicia para los pedidos perdidos ⚖️"),
]
FIRMA = [("Apertura de cine", "0 a 2 s. Pantalla negra, barras de cine y un título dramático con golpe de sonido. Detiene el dedo que pasa videos."),
         ("Corte seco a la comedia", "Cámara en mano, ritmo rápido y luz natural. El contraste entre lo épico y lo cotidiano es el chiste."),
         ("Entrada de Orbi", "Siempre con el mismo «ding» y un destello azul. La gente debe reconocer el sonido."),
         ("El remate", "Un último chiste después del chiste: la mirada del mesero, la cara del dueño."),
         ("Sello Apex", "1,5 s. Orbi guiña: «¿Le traigo el postre?» y aparece el logo. Igual en todos los videos.")]

EMOJI = re.compile("[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F]")
def video(v):
    filas = "".join(f'<tr><td class="t">{t}</td><td>{a}</td><td>{b}</td></tr>' for t, a, b in v["planos"])
    return f'''<section class="hoja"><div class="cab"><div><div class="k">Video {v["n"]} · {v["dia"]} · {v["prod"]}</div><h2>{v["titulo"]}</h2>
    <div class="meta"><span>{v["genero"]}</span><span>{v["dur"]}</span><span>{v["tipo"]}</span></div></div><div class="o" data-e="{v["exp"]}"></div></div>
    <p class="idea">{v["idea"]}</p>
    <table><thead><tr><th>Seg.</th><th>Plano</th><th>Qué se ve y se escucha</th></tr></thead><tbody>{filas}</tbody></table>
    <div class="copy"><b>Texto de la publicación</b>{EMOJI.sub("", v["copy"]).strip()}<br><span>#Apex #Restaurantes #Colombia #MeseroVirtual #Orbi</span></div>
    <div class="pie">Apex Corporation · Guiones semana 1</div></section>'''

HTML = f'''<!doctype html><html><head><meta charset="utf-8">{FUENTES}<style>
@page {{ size: Letter; margin: 0; }}
* {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }}
body {{ font-family: "Figtree", sans-serif; color: #14202f; font-size: 10.5pt; }}
.hoja {{ width: 8.5in; height: 11in; padding: .6in .65in .5in; display: flex; flex-direction: column; gap: 14px; break-after: page; position: relative; overflow: hidden; }}
.portada {{ background: radial-gradient(80% 60% at 50% 35%, #17406f 0%, #0b1626 60%, #050a14 100%); color: #fff; justify-content: center; }}
.portada .k {{ color: #8ddcf6; }} .portada h1 {{ font-size: 64pt; font-weight: 800; letter-spacing: -.04em; line-height: .95; margin-top: 10px; }}
.portada p {{ color: #b9c6d6; font-size: 13pt; max-width: 5.5in; margin-top: 14px; }}
.portada .o {{ width: 3.4in; height: 3.4in; margin: 0 auto 10px; }}
.k {{ font-size: 8.5pt; font-weight: 800; letter-spacing: .28em; text-transform: uppercase; color: #1d9fd1; }}
h2 {{ font-size: 28pt; font-weight: 800; letter-spacing: -.03em; line-height: 1.05; margin-top: 4px; }}
h3 {{ font-size: 15pt; font-weight: 800; margin-bottom: 8px; }}
.cab {{ display: grid; grid-template-columns: 1fr 1.25in; gap: 16px; align-items: center; }}
.cab .o {{ width: 1.25in; height: 1.25in; }}
.meta {{ display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap; }} .meta span {{ background: #e8f6fc; color: #0b4f73; border-radius: 99px; padding: 3px 10px; font-size: 8.5pt; font-weight: 700; }}
.idea {{ font-size: 12pt; color: #24364a; border-left: 3px solid #2fbbe8; padding: 4px 0 4px 12px; }}
table {{ width: 100%; border-collapse: collapse; font-size: 9.6pt; }}
th {{ text-align: left; font-size: 7.5pt; letter-spacing: .2em; text-transform: uppercase; color: #6b7a8c; border-bottom: 2px solid #0b1626; padding: 0 8px 6px 0; }}
td {{ padding: 8px 8px 8px 0; border-bottom: 1px solid #e3e8ef; vertical-align: top; line-height: 1.4; }}
td.t {{ font-weight: 800; color: #1d9fd1; white-space: nowrap; width: .55in; }} td:nth-child(2) {{ width: 2.3in; color: #3d4b5c; }}
.copy {{ margin-top: auto; background: #0b1626; color: #fff; border-radius: 12px; padding: 12px 16px; font-size: 11pt; }}
.copy b {{ display: block; font-size: 7.5pt; letter-spacing: .22em; text-transform: uppercase; color: #8ddcf6; margin-bottom: 4px; }} .copy span {{ font-size: 8.5pt; color: #8fa3ba; }}
.pie {{ font-size: 7pt; letter-spacing: .22em; text-transform: uppercase; color: #8a95a3; text-align: right; }}
.pasos {{ display: grid; gap: 10px; }} .pasos > div {{ display: grid; grid-template-columns: .35in 1fr; gap: 10px; align-items: start; }}
.pasos i {{ font-style: normal; font-weight: 800; font-size: 18pt; color: #2fbbe8; line-height: 1; }} .pasos b {{ display: block; font-size: 11.5pt; }} .pasos span {{ color: #4b5a6c; }}
.cal {{ width: 100%; border-collapse: collapse; }} .cal td {{ padding: 9px 8px 9px 0; }}
.nota {{ background: #f2f8fb; border-radius: 12px; padding: 12px 16px; font-size: 10pt; color: #24364a; line-height: 1.5; }}
.nota b {{ color: #0b1626; }}
</style></head><body>
<section class="hoja portada"><div class="o" data-e="guino"></div><div class="k">Apex Corporation · Redes sociales</div><h1>Orbi<br>en escena.</h1>
<p>Siete videos para Instagram y TikTok, uno por día. Cómicos, profesionales y con carácter: cada uno abre como una película y termina con Orbi pidiendo el postre.</p></section>
<section class="hoja"><div class="k">La fórmula</div><h2>Así se ve un video de Orbi</h2>
<p class="idea">Formato vertical 9:16, entre 25 y 30 segundos. Siempre la misma estructura, para que la gente lo reconozca sin ver el nombre.</p>
<div class="pasos">{"".join(f'<div><i>{i+1}</i><div><b>{t}</b><span>{d}</span></div></div>' for i, (t, d) in enumerate(FIRMA))}</div>
<h3 style="margin-top:14px">Calendario de la semana</h3>
<table class="cal"><tbody>{"".join(f'<tr><td class="t">{v["dia"]}</td><td><b>{v["titulo"]}</b></td><td>{v["prod"]} · {v["genero"]}</td></tr>' for v in V)}</tbody></table>
<div class="nota"><b>Para grabar:</b> un celular, un trípode y una luz pequeña. Actores: tú (dueño / juez), un amigo de mesero y otro de cliente. Ideal grabar todo en un mismo restaurante aliado una tarde (de 3 a 5 p. m.). Las pantallas del sistema ya las tenemos grabadas; Orbi animado lo pongo yo encima.<br>
<b>Publicar:</b> de lunes a domingo a las 12:30 p. m. o a las 7:00 p. m. Los primeros 60 minutos, responder todos los comentarios.</div>
<div class="pie">Apex Corporation · Guiones semana 1</div></section>
{"".join(video(v) for v in V)}
<script>{JS} document.querySelectorAll(".o").forEach((d) => d.innerHTML = orbi(d.dataset.e));</script>
</body></html>'''
async def m():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
        pg = await b.new_page(viewport={"width": 816, "height": 1056}); pg.on("pageerror", lambda e: print("ERR", e))
        await pg.set_content(HTML); await pg.wait_for_timeout(800)
        print("desborde:", await pg.evaluate("[...document.querySelectorAll('.hoja')].map(h=>h.scrollHeight-h.clientHeight)"))
        await pg.pdf(path=SAL, format="Letter", print_background=True); await b.close()
asyncio.run(m())
import pymupdf
d = pymupdf.open(SAL); print(len(d), "páginas", sorted({f[2] for pg in d for f in pg.get_fonts()}))
for i in (0, 1, 2, 6): d[i].get_pixmap(dpi=70).save(os.path.dirname(SAL) + f"/_g{i}.png")
