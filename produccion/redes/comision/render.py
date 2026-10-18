"""Video «La Comisión» (vertical 1080x1920, 24 cuadros): python render.py <carpeta_trabajo> <salida.mp4>
Requiere <carpeta_trabajo>/voces (de voces.py)."""
import sys, os, json, subprocess, asyncio, time
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
W_ = os.path.abspath(sys.argv[1]) + "/"; SAL = sys.argv[2]; FPS = 24
LIN = json.load(open(W_ + "voces/linea.json")); DUR = LIN["dur"]
HTML = f'''<!doctype html><html><head><meta charset="utf-8">{open(AQUI + "../../videos/fuentes.html").read()}<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }} html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #000; font-family: "Figtree", sans-serif; color: #fff; }}
#escena, #tinte, #sello {{ position: absolute; inset: 0; }}
#tinte {{ opacity: 0; }}
#rayas {{ position: absolute; inset: -20%; background: repeating-conic-gradient(from 0deg at 50% 45%, rgba(255,255,255,0) 0deg 4deg, rgba(255,255,255,.22) 4deg 5deg); mix-blend-mode: screen; opacity: 0; }}
#titulo {{ position: absolute; left: 50%; top: 50%; width: 1000px; text-align: center; opacity: 0; }}
#brillo {{ display: block; font: 400 150px/1 "Italiana", Georgia, serif; background: linear-gradient(100deg, #f3c97a 0%, #fff3d6 40%, #fff 50%, #fff3d6 60%, #e8b45f 100%); background-size: 300% 100%; -webkit-background-clip: text; background-clip: text; color: transparent; filter: drop-shadow(0 0 40px rgba(255,190,120,.45)); }}
#titulo small {{ display: block; font-size: 36px; letter-spacing: .3em; color: #ffc2d1; margin-top: 26px; text-transform: uppercase; font-weight: 700; }}
body.t {{ }}
#barras {{ position: absolute; inset: 0; pointer-events: none; opacity: 0; }}
#barras::before, #barras::after {{ content: ""; position: absolute; left: 0; right: 0; height: 190px; background: #000; }} #barras::before {{ top: 0; }} #barras::after {{ bottom: 0; }}
#chip {{ position: absolute; left: 50%; top: 120px; color: #ffb3c1 !important; font-size: 64px !important; transform: translateX(-50%); background: rgba(5,9,15,.85); border: 4px solid #ff5c6e; color: #fff; font-weight: 800; font-size: 44px;
  padding: 14px 30px; border-radius: 22px; white-space: nowrap; opacity: 0; }} #chip.ok {{ border-color: #2ee59d; color: #b8ffe0; }}
#sub {{ position: absolute; left: 50%; top: 250px; max-width: 960px; text-align: center; padding: 20px 34px 24px; border-radius: 30px; font-size: 54px; font-weight: 800; line-height: 1.15;
  background: rgba(5,9,15,.88); border: 3px solid rgba(255,255,255,.35); opacity: 0; }}
#sub small {{ display: block; font-size: 22px; letter-spacing: .28em; color: #c9d6e6; margin-bottom: 6px; }}
#sub.orbi {{ border-color: #2fbbe8; }} #sub.orbi small {{ color: #5fc9f1; }} #sub.comi {{ border-color: #e83fb5; font-style: italic; }} #sub.comi small {{ color: #ff8fd3; font-style: normal; }} #sub.rosa {{ border-color: #2a9d8f; }} #sub.rosa small {{ color: #7fd3c7; }}
#sello {{ display: flex; flex-direction: column; align-items: center; justify-content: center; background: radial-gradient(85% 55% at 50% 45%, #17406f 0%, #0b1626 60%, #050a14 100%); opacity: 0; }}
#o-final {{ width: 720px; height: 720px; }} #o-final svg {{ width: 100%; height: 100%; }}
#frase {{ font-size: 72px; font-weight: 800; margin-top: 10px; opacity: 0; }}
#logo {{ margin-top: 60px; text-align: center; opacity: 0; }} #logo b {{ font-size: 70px; font-weight: 800; }}
#logo b i {{ display: inline-block; width: 64px; height: 64px; border-radius: 18px; background: #2fbbe8; vertical-align: -8px; margin-right: 16px; position: relative; }}
#logo b i::after {{ content: ""; position: absolute; left: 19px; top: 14px; width: 26px; height: 26px; border-radius: 50% 50% 50% 0; background: #0b1626; transform: rotate(-45deg); }}
#logo span {{ display: block; font-size: 34px; color: #9db0c5; margin-top: 16px; font-weight: 600; }}
#vineta {{ position: absolute; inset: 0; background: radial-gradient(80% 70% at 50% 50%, rgba(0,0,0,0) 60%, rgba(0,0,0,.55) 100%); pointer-events: none; }}
#grano {{ position: absolute; inset: 0; width: 100%; height: 100%; opacity: .05; mix-blend-mode: overlay; pointer-events: none; }}
</style></head><body>
<div id="escena"></div><div id="tinte"></div><div id="rayas"></div>
<div id="titulo"><span id="brillo">La Comisión</span><small>Capítulo 1 · El reencuentro</small></div>
<div id="chip">− 27 %</div><div id="sub"></div>
<div id="sello"><div id="o-final"></div><div id="frase">¿Le traigo el postre?</div><div id="logo"><b><i></i>Apex Domicilios</b><span>Sus domicilios, sin comisiones</span></div></div>
<div id="vineta"></div><canvas id="grano" width="360" height="640"></canvas>
<script>
const LINEA = {json.dumps(LIN, ensure_ascii=False)};
{open(AQUI + "../orbi.js").read()}
{open(AQUI + "../viernes/personajes.js").read()}
{open(AQUI + "personajes_comi.js").read()}
{open(AQUI + "escena.js").read()}
</script></body></html>'''
open(W_ + "comision.html", "w").write(HTML)
NCU = int(DUR * FPS)
async def pagina(p):
    br = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    pg = await br.new_page(viewport={"width": 1080, "height": 1920}); pg.on("pageerror", lambda e: print("ERR", e))
    await pg.goto("file://" + W_ + "comision.html"); await pg.wait_for_timeout(900); return br, pg
async def obrero(i, a, b):
    from playwright.async_api import async_playwright
    seg = W_ + f"seg{i}.mp4"
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", seg], stdin=subprocess.PIPE)
    async with async_playwright() as p:
        br, pg = await pagina(p)
        for f in range(a, b): await pg.evaluate("([t,f]) => render(t,f)", [f / FPS, f]); ff.stdin.write(await pg.screenshot(type="jpeg", quality=93))
        await br.close()
    ff.stdin.close(); ff.wait(); return seg
async def prueba(ts):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        br, pg = await pagina(p)
        for t in ts: await pg.evaluate("([t,f]) => render(t,f)", [t, int(t * FPS)]); await pg.screenshot(path=W_ + f"p_{t:05.2f}.jpg", type="jpeg", quality=80)
        await br.close()
async def todo():
    n = 3; tr = NCU // n + 1
    segs = await asyncio.gather(*[obrero(i, i * tr, min(NCU, (i + 1) * tr)) for i in range(n)])
    open(W_ + "segs.txt", "w").write("".join(f"file '{s}'\n" for s in segs))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", W_ + "segs.txt", "-c", "copy", W_ + "imagen.mp4"], check=True)
    subprocess.run([sys.executable, AQUI + "sonido.py", W_], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", W_ + "imagen.mp4", "-i", W_ + "sonido.wav", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", SAL], check=True)
if os.getenv("PRUEBA"): asyncio.run(prueba([float(x) for x in os.getenv("PRUEBA").split(",")]))
else: t0 = time.time(); asyncio.run(todo()); print("listo", SAL, round(time.time() - t0), "s")
