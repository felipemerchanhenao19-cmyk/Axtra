"""Render cinematográfico 1920x1080 a 24 cuadros: python render.py play|domicilios <carpeta_trabajo> [trabajadores]
<carpeta_trabajo> trae: voz/ (voz.json y wav), fc/ y fk/ (cuadros de la grabación del celular y la caja), marcas.json, musica.wav.
Necesita fuentes.html (las @font-face de Figtree e Italiana)."""
import sys, os, json, subprocess, asyncio, qrcode, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import linea, escenas
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
PROD, W_ = sys.argv[1], os.path.abspath(sys.argv[2]) + "/"
OBREROS = int(sys.argv[3]) if len(sys.argv) > 3 else 3
FPS = 24
M = json.load(open(W_ + "marcas.json"))
SPEC = (escenas.play if PROD == "play" else escenas.domicilios)(M)
TL = linea.linea(PROD, W_ + "voz")
for e in TL: e["e"] = SPEC[e["id"]]
FIN = TL[-1]["fin"]; NCU = int(FIN * FPS)
ESC = next(e for e in TL if e["id"] == "contacto")["e"]
q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=0); q.add_data(ESC["qr"]); q.make()
mq = q.get_matrix(); n = len(mq)
QR = (f'<svg viewBox="0 0 {n} {n}" xmlns="http://www.w3.org/2000/svg" shape-rendering="crispEdges"><path d="'
      + "".join(f"M{x},{y}h1v1h-1z" for y, f in enumerate(mq) for x, v in enumerate(f) if v) + '" fill="#0b1626"/></svg>')
FUENTES = open(AQUI + "fuentes.html").read()
ICONO = "pin" if PROD == "domicilios" else "play"
HTML = f'''<!doctype html><html><head><meta charset="utf-8">{FUENTES}<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 1920px; height: 1080px; overflow: hidden; background: #020409; font-family: "Figtree", sans-serif; color: #f4f7fb; }}
#mundo {{ position: absolute; inset: 0; transform-origin: 50% 50%; }}
#halo {{ position: absolute; inset: -10%; }}
#rayos {{ position: absolute; left: -20%; top: -40%; width: 140%; height: 180%; opacity: 0;
  background: repeating-linear-gradient(90deg, rgba(120,190,255,0) 0 160px, rgba(120,190,255,.05) 220px, rgba(120,190,255,0) 320px, rgba(120,190,255,0) 520px); filter: blur(18px); mix-blend-mode: screen; }}
.capa {{ position: absolute; opacity: 0; }}
.abs {{ position: absolute; left: 50%; top: 50%; }}
#escena3d {{ position: absolute; inset: 0; perspective: 2100px; perspective-origin: 50% 45%; }}
#orbe {{ left: 50%; top: 50%; width: 360px; height: 360px; border-radius: 50%;
  background: radial-gradient(circle at 35% 30%, #effbff 0 6%, #7fe0ff 18%, #2fbbe8 34%, #0c4a9b 68%, #061a3d 100%);
  box-shadow: 0 0 0 30px rgba(47,187,232,.07), 0 0 220px 70px rgba(47,187,232,.35); }}
#orbe .anillo {{ position: absolute; left: -22%; right: -22%; top: 41%; height: 18%; border: 3px solid rgba(170,232,255,.8); border-radius: 50%; }}
.dev {{ left: 50%; top: 50%; background: #05080d; transform-style: preserve-3d; }}
.dev img {{ display: block; width: 100%; height: 100%; object-fit: cover; }}
.dev .brillo {{ position: absolute; inset: 0; border-radius: inherit; pointer-events: none; }}
#cel {{ width: 452px; height: 935px; padding: 16px; border-radius: 76px; }}
#cel img {{ border-radius: 60px; }}
#cel .isla {{ position: absolute; left: 50%; top: 30px; width: 120px; height: 34px; margin-left: -60px; background: #000; border-radius: 20px; }}
#tab {{ width: 944px; height: 669px; padding: 22px; border-radius: 42px; }}
#tab img {{ border-radius: 20px; }}
#sombra {{ left: 50%; top: 50%; width: 520px; height: 140px; background: radial-gradient(closest-side, rgba(0,0,0,.85), rgba(0,0,0,0)); }}
#texto {{ width: 700px; }}
#texto.lado-izq {{ left: 170px; top: 50%; transform: translateY(-50%); }}
#texto.lado-der {{ left: 1070px; top: 50%; transform: translateY(-50%); }}
#kicker {{ font-size: 26px; font-weight: 700; text-transform: uppercase; color: #5fc9f1; letter-spacing: .4em; margin-bottom: 26px; }}
#titulo {{ font-size: 104px; font-weight: 800; line-height: 1.0; letter-spacing: -0.035em; }}
#sub {{ font-size: 36px; font-weight: 500; color: #9db0c5; margin-top: 30px; line-height: 1.35; }}
.w {{ display: inline-block; will-change: transform; }}
#bloque-grande {{ left: 0; right: 0; top: 50%; margin-top: -120px; text-align: center; opacity: 1; }}
#grande {{ font-size: 150px; font-weight: 800; letter-spacing: -0.04em; line-height: 1.05; }}
#grande2 {{ font-size: 50px; font-weight: 500; color: #9db0c5; margin-top: 24px; }}
#bloque-num {{ left: 0; right: 0; top: 50%; margin-top: -280px; text-align: center; }}
#numero {{ font-size: 400px; font-weight: 800; letter-spacing: -0.05em; line-height: 1; font-variant-numeric: tabular-nums;
  background: linear-gradient(180deg, #ffffff 30%, #8ddcf6 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }}
#num-pie {{ font-size: 56px; font-weight: 600; color: #c9d6e6; margin-top: 10px; }}
#marca {{ left: 50%; top: 50%; display: flex; align-items: center; gap: 44px; white-space: nowrap; }}
#marca .ico {{ width: 150px; height: 150px; border-radius: 40px; background: #2fbbe8; position: relative; box-shadow: 0 0 80px rgba(47,187,232,.6); }}
#marca .ico.play::after {{ content: ""; position: absolute; left: 58px; top: 42px; border-left: 52px solid #0b1626; border-top: 33px solid transparent; border-bottom: 33px solid transparent; }}
#marca .ico.pin::after {{ content: ""; position: absolute; left: 44px; top: 34px; width: 62px; height: 62px; border-radius: 50% 50% 50% 0; background: #0b1626; transform: rotate(-45deg); }}
#marca-txt {{ font-size: 170px; font-weight: 800; letter-spacing: -0.045em; background: linear-gradient(100deg, #ffffff 0%, #ffffff 42%, #a6e6ff 50%, #ffffff 58%, #ffffff 100%);
  background-size: 300% 100%; -webkit-background-clip: text; background-clip: text; color: transparent; padding: 0 10px; }}
#bloque-lema {{ left: 0; right: 0; top: 50%; margin-top: 210px; text-align: center; }}
#lema {{ font-size: 56px; font-weight: 500; color: #c9d6e6; }}
.chip {{ left: 50%; top: 50%; padding: 22px 34px; border-radius: 99px; font-size: 34px; font-weight: 700; white-space: nowrap;
  background: rgba(255,255,255,.08); border: 1.5px solid rgba(160,220,255,.35); backdrop-filter: blur(10px); box-shadow: 0 20px 60px rgba(0,0,0,.5); }}
#saludo {{ left: 50%; top: 50%; font-size: 340px; font-weight: 800; letter-spacing: -0.05em; color: rgba(141,220,246,.55); white-space: nowrap; }}
.fut {{ left: 50%; top: 50%; width: 420px; height: 250px; border-radius: 34px; background: linear-gradient(160deg, rgba(255,255,255,.12), rgba(255,255,255,.03));
  border: 1.5px solid rgba(160,220,255,.35); display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 18px; box-shadow: 0 30px 80px rgba(0,0,0,.5); }}
.fut i {{ font-style: normal; font-size: 80px; }} .fut b {{ font-size: 40px; font-weight: 700; }}
#fut-kicker {{ left: 0; right: 0; top: 150px; text-align: center; font-size: 28px; font-weight: 800; letter-spacing: .45em; color: #5fc9f1; }}
#fut-titulo {{ left: 0; right: 0; top: 760px; text-align: center; font-size: 96px; font-weight: 800; letter-spacing: -0.035em; }}
#contacto {{ inset: 0; display: flex; align-items: center; justify-content: center; gap: 140px; }}
#c-qr {{ display: flex; flex-direction: column; align-items: center; gap: 28px; }}
#c-qr .tarjeta {{ width: 470px; height: 470px; background: #fff; border-radius: 40px; padding: 36px; box-shadow: 0 0 0 10px rgba(47,187,232,.5), 0 0 120px rgba(47,187,232,.5); }}
#c-qr .tarjeta svg {{ width: 100%; height: 100%; display: block; }}
#c-qr span {{ font-size: 34px; font-weight: 700; letter-spacing: .02em; }}
#c-der h2 {{ font-size: 110px; font-weight: 800; letter-spacing: -0.04em; line-height: 1; }}
#c-der p {{ font-size: 42px; color: #9db0c5; margin-top: 22px; }}
#c-der .marca-c {{ font-size: 34px; font-weight: 800; color: #5fc9f1; letter-spacing: .02em; margin-bottom: 30px; }}
#c-der .wa {{ display: inline-flex; align-items: center; gap: 22px; margin-top: 48px; background: #fff; color: #0b1626; border-radius: 30px; padding: 22px 34px; }}
#c-der .wa i {{ width: 74px; height: 74px; border-radius: 22px; background: #25d366; display: grid; place-items: center; }}
#c-der .wa svg {{ width: 42px; height: 42px; fill: none; stroke: #fff; stroke-width: 2; stroke-linejoin: round; }}
#c-der .wa small {{ display: block; font-size: 24px; font-weight: 700; color: #3a4a5c; }} #c-der .wa b {{ font-size: 60px; font-weight: 800; }}
#c-der .pie {{ font-size: 22px; letter-spacing: .25em; text-transform: uppercase; color: #6f8299; margin-top: 60px; }}
#vineta {{ position: absolute; inset: 0; background: radial-gradient(75% 75% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,.78) 100%); pointer-events: none; }}
#grano {{ position: absolute; inset: 0; width: 100%; height: 100%; opacity: .06; mix-blend-mode: overlay; pointer-events: none; }}
#flash {{ position: absolute; inset: 0; background: radial-gradient(60% 60% at 50% 50%, #ffffff, rgba(200,235,255,.7)); opacity: 0; pointer-events: none; }}
#barras::before, #barras::after {{ content: ""; position: absolute; left: 0; right: 0; height: 0; background: #000; }}
</style></head><body>
<div id="mundo"><div id="halo"></div><div id="rayos"></div>
 <div id="escena3d">
  <div id="saludo" class="capa"></div>
  <div id="orbe" class="capa abs"><div class="anillo"></div></div>
  <div id="sombra" class="capa"></div>
  <div id="cel" class="capa dev"><img><div class="brillo"></div></div>
  <div id="tab" class="capa dev"><img><div class="brillo"></div></div>
  <div id="chip0" class="capa chip"></div><div id="chip1" class="capa chip"></div><div id="chip2" class="capa chip"></div>
  <div id="fut0" class="capa fut"><i>🍽️</i><b></b></div><div id="fut1" class="capa fut"><i>🛵</i><b></b></div><div id="fut2" class="capa fut"><i>📍</i><b></b></div>
 </div>
 <div id="fut-kicker" class="capa">MUY PRONTO</div><div id="fut-titulo" class="capa"></div>
 <div id="bloque-grande" class="capa"><div id="grande"></div><div id="grande2"></div></div>
 <div id="bloque-num" class="capa"><div id="numero"></div><div id="num-pie"></div></div>
 <div id="marca" class="capa"><span class="ico {ICONO}"></span><span id="marca-txt"></span></div>
 <div id="bloque-lema" class="capa"><div id="lema"></div></div>
 <div id="texto" class="capa"><div id="kicker"></div><div id="titulo"></div><div id="sub"></div></div>
 <div id="contacto" class="capa"><div id="c-qr"><div class="tarjeta">{QR}</div><span>↑ Pruébelo ahora</span></div>
  <div id="c-der"><div class="marca-c">{ESC["marca"]}</div><h2>Agende<br>una reunión.</h2><p>Presencial o virtual.</p>
  <div class="wa"><i><svg viewBox="0 0 24 24"><path d="M4 20l1.3-4A8 8 0 1 1 8 18.7z"/></svg></i><div><small>WhatsApp</small><b>310 789 7960</b></div></div>
  <div class="pie">Producción de Apex Corporation</div></div></div>
</div>
<div id="vineta"></div><canvas id="grano" width="480" height="270"></canvas><div id="flash"></div>
<script>
const TL = {json.dumps(TL, ensure_ascii=False)};
const DIR_C = "file://{W_}fc", DIR_K = "file://{W_}fk", N_C = {len(os.listdir(W_ + "fc"))}, N_K = {len(os.listdir(W_ + "fk"))};
{open(AQUI + "escenario.js").read()}
</script></body></html>'''
open(W_ + "escenario.html", "w").write(HTML)

async def obrero(i, a, b):
    from playwright.async_api import async_playwright
    seg = W_ + f"seg{i}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-r", str(FPS), seg], stdin=subprocess.PIPE)
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
                                     args=["--allow-file-access-from-files", "--disable-web-security"])
        pg = await br.new_page(viewport={"width": 1920, "height": 1080})
        pg.on("pageerror", lambda e: print("ERR", e))
        await pg.goto("file://" + W_ + "escenario.html"); await pg.wait_for_timeout(1200)
        for f in range(a, b):
            await pg.evaluate("([t,f]) => render(t,f)", [f / FPS, f])
            ff.stdin.write(await pg.screenshot(type="jpeg", quality=94))
            if (f - a) % 240 == 0: print(f"obrero {i}: {f - a}/{b - a}", flush=True)
        await br.close()
    ff.stdin.close(); ff.wait(); return seg

async def todo(solo=None):
    if solo is not None:   # prueba: un cuadro por segundo indicado → PNG
        from playwright.async_api import async_playwright
        async with async_playwright() as p:
            br = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args=["--allow-file-access-from-files"])
            pg = await br.new_page(viewport={"width": 1920, "height": 1080}); pg.on("pageerror", lambda e: print("ERR", e))
            await pg.goto("file://" + W_ + "escenario.html"); await pg.wait_for_timeout(1200)
            for t in solo:
                await pg.evaluate("([t,f]) => render(t,f)", [t, int(t * FPS)]); await pg.screenshot(path=W_ + f"prueba_{t:05.1f}.jpg", type="jpeg", quality=85)
            await br.close()
        return
    trozo = NCU // OBREROS + 1
    segs = await asyncio.gather(*[obrero(i, i * trozo, min(NCU, (i + 1) * trozo)) for i in range(OBREROS)])
    open(W_ + "segs.txt", "w").write("".join(f"file '{s}'\n" for s in segs))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", W_ + "segs.txt", "-c", "copy", W_ + "imagen.mp4"], check=True)

if os.getenv("PRUEBA"):
    asyncio.run(todo([float(x) for x in os.getenv("PRUEBA").split(",")]))
else:
    t0 = time.time(); asyncio.run(todo()); print("imagen lista", NCU, "cuadros en", round(time.time() - t0), "s")
