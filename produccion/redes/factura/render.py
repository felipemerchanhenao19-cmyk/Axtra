"""Video «La factura» (vertical 1080x1920, 24 cuadros): python render.py <carpeta_trabajo> <salida.mp4>"""
import sys, os, json, subprocess, asyncio, time
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
REDES = AQUI + "../"; VIDEOS = AQUI + "../../videos/"
W_ = os.path.abspath(sys.argv[1]) + "/"; SAL = sys.argv[2]; os.makedirs(W_ + "fk", exist_ok=True)
FPS, DUR = 24, 25.5
if not os.path.exists(W_ + "fk/00001.jpg"):
    subprocess.run(["ffmpeg", "-v", "error", "-i", VIDEOS + "grabaciones/domicilios/caja.webm", "-vf", "fps=24", "-q:v", "3", W_ + "fk/%05d.jpg"], check=True)
M = json.load(open(VIDEOS + "grabaciones/domicilios/marcas.json"))
VOZ = json.load(open(W_ + "voces/voz.json")) if os.path.exists(W_ + "voces/voz.json") else {}
HTML = f'''<!doctype html><html><head><meta charset="utf-8">{open(VIDEOS + "fuentes.html").read()}<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #050a14; font-family: "Figtree", sans-serif; color: #fff; }}
#mundo, #fondo {{ position: absolute; inset: 0; }} #mundo {{ transform-origin: 50% 45%; }}
.capa {{ position: absolute; opacity: 0; }} .c {{ left: 50%; top: 50%; }}
#titulo {{ text-align: center; width: 1000px; font: 400 128px/1.02 "Italiana", Georgia, serif; }}
#brillo {{ background: linear-gradient(100deg, #f3c97a 0%, #fff3d6 40%, #ffffff 50%, #fff3d6 60%, #e8b45f 100%); background-size: 300% 100%;
  -webkit-background-clip: text; background-clip: text; color: transparent; filter: drop-shadow(0 0 40px rgba(255,190,120,.45)); }}
#cel {{ width: 640px; height: 1240px; border-radius: 80px; background: #05080d; padding: 18px; box-shadow: 0 0 0 2px #2b3442, 0 60px 140px rgba(0,0,0,.7); }}
#cel .pan {{ width: 100%; height: 100%; border-radius: 64px; background: linear-gradient(#f7f8fa, #eceff3); color: #14202f; padding: 110px 44px; }}
.app {{ display: flex; align-items: center; gap: 18px; }} .app i {{ width: 70px; height: 70px; border-radius: 20px; background: #c9ced6; }}
.app b {{ font-size: 30px; }} .app span {{ display: block; font-size: 22px; color: #6b7684; font-weight: 500; }}
.liq h3 {{ font-size: 40px; margin: 70px 0 30px; }}
.fila {{ display: flex; justify-content: space-between; font-size: 30px; padding: 26px 18px; border-bottom: 2px solid #dde2e8; border-radius: 14px; }}
.fila b {{ font-variant-numeric: tabular-nums; }} #linea-com {{ color: #c8102e; font-weight: 800; }}
.total {{ font-size: 34px; font-weight: 800; }}
#rayas {{ position: absolute; inset: -20%; background: repeating-conic-gradient(from 0deg at 50% 60%, rgba(255,255,255,.0) 0deg 4deg, rgba(255,255,255,.22) 4deg 5deg); mix-blend-mode: screen; opacity: 0; }}
#veinti {{ font-size: 430px; font-weight: 800; letter-spacing: -.05em; line-height: 1; white-space: nowrap;
  background: linear-gradient(180deg, #ffd1dc 0%, #ff3d6e 60%, #b3002d 100%); -webkit-background-clip: text; background-clip: text; color: transparent; filter: drop-shadow(0 0 60px rgba(255,40,90,.5)); }}
#veinti-pie {{ left: 0; right: 0; top: 1190px; text-align: center; font-size: 52px; font-weight: 700; color: #ffc2d1; }}
#lagrimas {{ position: absolute; inset: 0; }} #lagrimas i {{ position: absolute; width: 28px; height: 40px; background: #7fd7ff; border-radius: 50% 50% 50% 50% / 60% 60% 40% 40%; box-shadow: 0 0 20px rgba(127,215,255,.7); }}
#orbi {{ width: 640px; height: 640px; }} #orbi svg, #o-final svg {{ width: 100%; height: 100%; }}
#pañuelo {{ width: 260px; height: 236px; }} #pañuelo svg {{ width: 100%; height: 100%; }}
#caja {{ width: 980px; padding: 20px; border-radius: 40px; background: #05080d; box-shadow: 0 0 0 2px #2b3442, 0 40px 120px rgba(0,0,0,.7), 0 0 120px rgba(47,187,232,.3); }}
#caja img {{ display: block; width: 100%; border-radius: 22px; }}
#caja .et {{ position: absolute; top: -78px; left: 10px; font-size: 32px; font-weight: 800; color: #8ddcf6; letter-spacing: .02em; }}
#sello {{ padding: 26px 46px; border: 10px solid #2ee59d; color: #2ee59d; border-radius: 26px; font-size: 92px; font-weight: 800; letter-spacing: -.02em; white-space: nowrap;
  background: rgba(5,30,20,.85); box-shadow: 0 0 80px rgba(46,229,157,.45); }}
#chat {{ left: 70px; right: 70px; top: 260px; height: 860px; border-radius: 46px; background: #0b141a; box-shadow: 0 40px 120px rgba(0,0,0,.6); overflow: hidden; }}
#chat .cab {{ display: flex; align-items: center; gap: 20px; background: #1f2c34; padding: 34px 36px; font-size: 36px; font-weight: 700; }}
#chat .cab i {{ width: 72px; height: 72px; border-radius: 50%; background: #6b7684; }} #chat .cab span {{ display: block; font-size: 24px; color: #8fa3ba; font-weight: 500; }}
#chat .cuerpo {{ padding: 40px 36px; display: flex; flex-direction: column; align-items: flex-end; gap: 26px; }}
.burbuja {{ background: #005c4b; border-radius: 30px 30px 6px 30px; padding: 24px 34px; font-size: 48px; font-weight: 600; transform-origin: 100% 100%; opacity: 0; }}
.burbuja small {{ font-size: 22px; color: #9fd3c7; margin-left: 18px; }}
#sub {{ left: 50%; max-width: 940px; text-align: center; padding: 22px 36px 26px; border-radius: 30px; font-size: 56px; font-weight: 800; line-height: 1.15; background: rgba(5,9,15,.88); }}
#sub small {{ display: block; font-size: 22px; letter-spacing: .3em; margin-bottom: 8px; }}
#sub.orbi {{ border: 3px solid #2fbbe8; }} #sub.orbi small {{ color: #5fc9f1; }}
#sub.dueno {{ border: 3px solid #ff5c8a; font-style: italic; }} #sub.dueno small {{ color: #ff8fb3; font-style: normal; }}
#sello-final {{ inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; background: radial-gradient(85% 55% at 50% 45%, #17406f 0%, #0b1626 60%, #050a14 100%); }}
#o-final {{ width: 720px; height: 720px; }}
#frase {{ font-size: 72px; font-weight: 800; letter-spacing: -.02em; margin-top: 10px; opacity: 0; }}
#logo {{ margin-top: 70px; text-align: center; opacity: 0; }} #logo b {{ font-size: 64px; font-weight: 800; }} #logo b i {{ display: inline-block; width: 60px; height: 60px; border-radius: 18px; background: #2fbbe8; vertical-align: -8px; margin-right: 16px; position: relative; }}
#logo b i::after {{ content: ""; position: absolute; left: 17px; top: 13px; width: 26px; height: 26px; border-radius: 50% 50% 50% 0; background: #0b1626; transform: rotate(-45deg); }}
#logo span {{ display: block; font-size: 26px; letter-spacing: .3em; color: #8fa3ba; margin-top: 14px; }}
#barras::before, #barras::after {{ content: ""; position: absolute; left: 0; right: 0; height: 200px; background: #000; }} #barras::before {{ top: 0; }} #barras::after {{ bottom: 0; }}
#barras {{ position: absolute; inset: 0; pointer-events: none; }}
#vineta {{ position: absolute; inset: 0; background: radial-gradient(80% 70% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,0,0,.7) 100%); }}
#grano {{ position: absolute; inset: 0; width: 100%; height: 100%; opacity: .06; mix-blend-mode: overlay; }}
#flash {{ position: absolute; inset: 0; background: #fff; opacity: 0; }}
</style></head><body>
<div id="fondo"></div>
<div id="mundo">
 <div id="titulo" class="capa c"><span id="brillo">Una historia de<br>amor y traición</span></div>
 <div id="cel" class="capa c"><div class="pan"><div class="app"><i></i><div><b>App de domicilios</b><span>Liquidación del mes</span></div></div>
  <div class="liq"><h3>Su restaurante · octubre</h3>
   <div class="fila"><span>Ventas por la app</span><b>$ 4.200.000</b></div>
   <div class="fila" id="linea-com"><span>Comisión (27 %)</span><b>− $ 1.134.000</b></div>
   <div class="fila total"><span>Usted recibe</span><b>$ 3.066.000</b></div></div></div></div>
 <div id="rayas"></div>
 <div id="veinti" class="capa c">27 %</div><div id="veinti-pie" class="capa">de cada pedido. Para la app.</div><div id="lagrimas" class="capa"></div>
 <div id="caja" class="capa c"><div class="et">Apex Domicilios · su caja</div><img></div>
 <div id="sello" class="capa c">0 % COMISIÓN</div>
 <div id="chat" class="capa"><div class="cab"><i></i><div>App de domicilios<span>en línea</span></div></div>
  <div class="cuerpo"><div class="burbuja" id="b1">No eres tú, soy yo.<small>8:14 p. m. ✓✓</small></div>
  <div class="burbuja" id="b2">Bueno, no.<small>8:14 p. m. ✓✓</small></div><div class="burbuja" id="b3">Eres tú.<small>8:14 p. m. ✓✓</small></div></div></div>
 <div id="pañuelo" class="capa c"></div>
 <div id="orbi" class="capa c"></div>
 <div id="sub" class="capa"></div>
 <div id="sello-final" class="capa"><div id="o-final"></div><div id="frase">¿Le traigo el postre?</div><div id="logo"><b><i></i>Apex Domicilios</b><span>APEX CORPORATION</span></div></div>
</div>
<div id="barras" style="opacity:0"></div><div id="vineta"></div><canvas id="grano" width="360" height="640"></canvas><div id="flash"></div>
<script>
const VOZ = {json.dumps(VOZ)}, DIR_K = "file://{W_}fk", N_K = {len(os.listdir(W_ + "fk"))}, CAJA0 = {M["caja_desde"] + 0.6};
{open(REDES + "orbi.js").read()}
{open(AQUI + "escena.js").read()}
</script></body></html>'''
open(W_ + "factura.html", "w").write(HTML)
NCU = int(DUR * FPS)
async def obrero(i, a, b):
    from playwright.async_api import async_playwright
    seg = W_ + f"seg{i}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", seg], stdin=subprocess.PIPE)
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args=["--allow-file-access-from-files"])
        pg = await br.new_page(viewport={"width": 1080, "height": 1920}); pg.on("pageerror", lambda e: print("ERR", e))
        await pg.goto("file://" + W_ + "factura.html"); await pg.wait_for_timeout(1000)
        for f in range(a, b):
            await pg.evaluate("([t,f]) => render(t,f)", [f / FPS, f]); ff.stdin.write(await pg.screenshot(type="jpeg", quality=93))
        await br.close()
    ff.stdin.close(); ff.wait(); return seg
async def prueba(ts):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome", args=["--allow-file-access-from-files"])
        pg = await br.new_page(viewport={"width": 1080, "height": 1920}); pg.on("pageerror", lambda e: print("ERR", e))
        await pg.goto("file://" + W_ + "factura.html"); await pg.wait_for_timeout(1000)
        for t in ts: await pg.evaluate("([t,f]) => render(t,f)", [t, int(t * FPS)]); await pg.screenshot(path=W_ + f"p_{t:05.2f}.jpg", type="jpeg", quality=80)
        await br.close()
async def todo():
    n = 3; tr = NCU // n + 1
    segs = await asyncio.gather(*[obrero(i, i * tr, min(NCU, (i + 1) * tr)) for i in range(n)])
    open(W_ + "segs.txt", "w").write("".join(f"file '{s}'\n" for s in segs))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", W_ + "segs.txt", "-c", "copy", W_ + "imagen.mp4"], check=True)
    subprocess.run([sys.executable, AQUI + "sonido.py", W_ + "sonido.wav", W_ + "voces"], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", W_ + "imagen.mp4", "-i", W_ + "sonido.wav", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", SAL], check=True)
if os.getenv("PRUEBA"): asyncio.run(prueba([float(x) for x in os.getenv("PRUEBA").split(",")]))
else: t0 = time.time(); asyncio.run(todo()); print("listo", SAL, round(time.time() - t0), "s")
