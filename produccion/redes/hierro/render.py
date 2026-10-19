"""Video «Orbi · Mark I» (vertical 1080x1920, 24 cuadros): python render.py <carpeta_trabajo> <salida.mp4>
Requiere <carpeta_trabajo>/voces (de voces.py)."""
import sys, os, json, subprocess, asyncio, time
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
W_ = os.path.abspath(sys.argv[1]) + "/"; SAL = sys.argv[2]; FPS = 24
LIN = json.load(open(W_ + "voces/linea.json")); DUR = LIN["dur"]
HTML = f'''<!doctype html><html><head><meta charset="utf-8">{open(AQUI + "../../videos/fuentes.html").read()}{open(AQUI + "../expediente/fuentes_noir.html").read()}<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }} html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #000; font-family: "Figtree", sans-serif; color: #fff; }}
#escena, #hud, #negro, #sello {{ position: absolute; inset: 0; }} #negro {{ background: #000; opacity: 0; }}
#titulo {{ position: absolute; left: 50%; top: 46%; width: 1080px; transform: translate(-50%, -50%); text-align: center; opacity: 0; }}
#titulo em {{ display: block; font: italic 700 40px "Playfair Display", Georgia, serif; color: #e8d9b0; margin-bottom: 20px; }}
#titulo b {{ display: block; font: 800 230px/0.9 "Figtree", sans-serif; letter-spacing: .04em;
  background: linear-gradient(100deg, #7a0a10 0%, #d2232a 30%, #fff1b8 48%, #ffffff 50%, #e6b54a 54%, #b0141c 75%, #5a0608 100%); background-size: 300% 100%; -webkit-background-clip: text; background-clip: text; color: transparent;
  filter: drop-shadow(0 0 30px rgba(255,90,60,.35)); }}
#titulo small {{ display: block; font: 600 46px "Figtree", sans-serif; letter-spacing: .6em; color: #f3cf6a; margin-top: 24px; padding-left: .6em; }}
#barras {{ position: absolute; inset: 0; pointer-events: none; }}
#barras::before, #barras::after {{ content: ""; position: absolute; left: 0; right: 0; height: 100px; background: #000; }} #barras::before {{ top: 0; }} #barras::after {{ bottom: 0; }}
#sub {{ position: absolute; left: 50%; top: 170px; width: max-content; max-width: 960px; transform: translateX(-50%); text-align: center; padding: 18px 34px 22px; font-size: 52px; font-weight: 800; line-height: 1.16;
  background: rgba(4,8,14,.72); border: 2px solid rgba(127,232,255,.35); border-radius: 14px; opacity: 0; }}
#sub small {{ display: block; font-size: 22px; letter-spacing: .3em; color: #9fdcff; margin-bottom: 6px; font-weight: 700; }}
#sub.orbi {{ border-color: #e6b54a; }} #sub.orbi small {{ color: #f3cf6a; }} #sub.sofia {{ font-style: italic; color: #d8f6ff; }} #sub.julian small {{ color: #ffc9a8; }}
#sello {{ display: flex; flex-direction: column; align-items: center; justify-content: center; background: radial-gradient(80% 50% at 50% 38%, rgba(90,10,16,.85) 0%, rgba(5,5,8,.97) 70%); opacity: 0; }}
#frase {{ font: 800 66px "Figtree", sans-serif; color: #f3cf6a; margin-top: 6px; text-align: center; opacity: 0; letter-spacing: .02em; }}
#logo {{ margin-top: 50px; text-align: center; opacity: 0; }} #logo b {{ font-size: 72px; font-weight: 800; }}
#logo b i {{ display: inline-block; width: 66px; height: 66px; border-radius: 18px; background: #2fbbe8; vertical-align: -8px; margin-right: 16px; position: relative; }}
#logo b i::after {{ content: ""; position: absolute; left: 25px; top: 17px; border-left: 26px solid #0b1626; border-top: 16px solid transparent; border-bottom: 16px solid transparent; }}
#logo span {{ display: block; font-size: 34px; color: #b9c3d0; margin-top: 16px; font-weight: 600; }}
#vineta {{ position: absolute; inset: 0; background: radial-gradient(75% 60% at 50% 48%, rgba(0,0,0,0) 50%, rgba(0,0,0,.65) 100%); pointer-events: none; }}
#grano {{ position: absolute; inset: 0; width: 100%; height: 100%; opacity: .05; mix-blend-mode: overlay; pointer-events: none; }}
</style></head><body>
<div id="escena"></div><svg id="hud" viewBox="0 0 1080 1920" width="1080" height="1920"></svg>
<div id="titulo"><em>Apex Play presenta</em><b>ORBI</b><small>MARK I</small></div>
<div id="sello"><div id="o-final"></div><div id="frase">Tecnología que atiende.</div><div id="logo"><b><i></i>Apex Play</b><span>El mesero virtual de tu restaurante</span></div></div>
<div id="vineta"></div><canvas id="grano" width="360" height="640"></canvas><div id="sub"></div><div id="negro"></div><div id="barras"></div>
<script>
const LINEA = {json.dumps(LIN, ensure_ascii=False)};
{open(AQUI + "../orbi.js").read()}
{open(AQUI + "../viernes/personajes.js").read()}
{open(AQUI + "armadura.js").read()}
{open(AQUI + "escena.js").read()}
</script></body></html>'''
open(W_ + "hierro.html", "w").write(HTML)
NCU = int(DUR * FPS)
async def pagina(p):
    br = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    pg = await br.new_page(viewport={"width": 1080, "height": 1920}); pg.on("pageerror", lambda e: print("ERR", e))
    await pg.goto("file://" + W_ + "hierro.html"); await pg.wait_for_timeout(1200); return br, pg
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
