"""Video «Expediente 27» (vertical 1080x1920, 24 cuadros): python render.py <carpeta_trabajo> <salida.mp4>
Requiere <carpeta_trabajo>/voces (de voces.py)."""
import sys, os, json, subprocess, asyncio, time
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
W_ = os.path.abspath(sys.argv[1]) + "/"; SAL = sys.argv[2]; FPS = 24
LIN = json.load(open(W_ + "voces/linea.json")); DUR = LIN["dur"]
HTML = f'''<!doctype html><html><head><meta charset="utf-8">{open(AQUI + "../../videos/fuentes.html").read()}{open(AQUI + "fuentes_noir.html").read()}<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }} html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #000; font-family: "Figtree", sans-serif; color: #fff; }}
#escena, #lluvia, #tinte, #flash, #negro, #sello {{ position: absolute; inset: 0; }}
#tinte {{ mix-blend-mode: soft-light; }} #flash {{ background: #e8f0ff; mix-blend-mode: screen; opacity: 0; }} #negro {{ background: #000; opacity: 0; }}
#titulo {{ position: absolute; left: 50%; top: 46%; width: 1000px; transform: translate(-50%, -50%); text-align: center; opacity: 0; }}
#titulo em {{ display: block; font: italic 700 44px "Playfair Display", Georgia, serif; color: #c9b38a; margin-bottom: 30px; letter-spacing: .04em; }}
#titulo b {{ display: inline-block; font: 400 128px/1 "Special Elite", "Courier New", monospace; color: #f2e8d0; text-shadow: 0 0 30px rgba(255,220,160,.35), 3px 3px 0 #5a1a22; white-space: nowrap; }}
#cursor {{ display: inline-block; width: 14px; height: 110px; background: #f2e8d0; vertical-align: -10px; margin-left: 6px; }}
#titulo small {{ display: block; font: 400 40px "Special Elite", monospace; color: #ff8fa0; letter-spacing: .25em; margin-top: 34px; }}
#barras {{ position: absolute; inset: 0; pointer-events: none; }}
#barras::before, #barras::after {{ content: ""; position: absolute; left: 0; right: 0; height: 110px; background: #000; }} #barras::before {{ top: 0; }} #barras::after {{ bottom: 0; }}
#sub {{ position: absolute; left: 50%; top: 210px; width: max-content; max-width: 940px; transform: translateX(-50%); text-align: center; padding: 22px 36px 26px; font-size: 50px; font-weight: 800; line-height: 1.18;
  background: rgba(6,8,12,.9); border: 3px solid rgba(255,255,255,.3); border-radius: 6px; opacity: 0; }}
#sub small {{ display: block; font: 400 22px "Special Elite", monospace; letter-spacing: .22em; color: #c9d6e6; margin-bottom: 8px; }}
#sub.narra {{ background: #e9dfc6; color: #1c1612; font: 400 50px/1.2 "Special Elite", monospace; border: 0; box-shadow: 8px 8px 0 rgba(0,0,0,.6); transform: translateX(-50%) rotate(-1deg); }} #sub.narra small {{ color: #6e1f1f; }}
#sub.orbi {{ border-color: #2fbbe8; }} #sub.orbi small {{ color: #5fc9f1; }} #sub.aure {{ border-color: #c9a65a; }} #sub.aure small {{ color: #e8c27a; }}
#sub.comi {{ border-color: #e83fb5; font-style: italic; }} #sub.comi small {{ color: #ff8fd3; font-style: normal; }}
#sello {{ display: flex; flex-direction: column; align-items: center; justify-content: center; background: radial-gradient(80% 50% at 50% 42%, #1a2233 0%, #07090f 70%); opacity: 0; }}
#sello::before {{ content: ""; position: absolute; inset: 0; background: repeating-linear-gradient(170deg, rgba(255,230,180,.05) 0 26px, rgba(0,0,0,0) 26px 60px); }}
#frase {{ font: 400 76px "Special Elite", monospace; color: #f2e8d0; min-height: 90px; margin-top: 6px; }}
#logo {{ margin-top: 50px; text-align: center; opacity: 0; }} #logo b {{ font-size: 70px; font-weight: 800; }}
#logo b i {{ display: inline-block; width: 64px; height: 64px; border-radius: 18px; background: #2fbbe8; vertical-align: -8px; margin-right: 16px; position: relative; }}
#logo b i::after {{ content: ""; position: absolute; left: 19px; top: 14px; width: 26px; height: 26px; border-radius: 50% 50% 50% 0; background: #0b1626; transform: rotate(-45deg); }}
#logo span {{ display: block; font-size: 34px; color: #9db0c5; margin-top: 16px; font-weight: 600; }}
#vineta {{ position: absolute; inset: 0; background: radial-gradient(75% 60% at 50% 48%, rgba(0,0,0,0) 45%, rgba(0,0,0,.8) 100%); pointer-events: none; }}
#grano {{ position: absolute; inset: 0; width: 100%; height: 100%; opacity: .09; mix-blend-mode: overlay; pointer-events: none; }}
</style></head><body>
<div id="escena"></div><svg id="lluvia" viewBox="0 0 1080 1920" width="1080" height="1920"></svg><div id="tinte"></div><div id="flash"></div>
<div id="titulo"><em>Apex Domicilios presenta</em><b><span id="tecla"></span><span id="cursor"></span></b><small>Un caso de Orbi</small></div>
<div id="sub"></div>
<div id="sello"><div id="o-final"></div><div id="frase"></div><div id="logo"><b><i></i>Apex Domicilios</b><span>Sus domicilios, sin comisiones</span></div></div>
<div id="vineta"></div><canvas id="grano" width="360" height="640"></canvas><div id="negro"></div><div id="barras"></div>
<script>
const LINEA = {json.dumps(LIN, ensure_ascii=False)};
{open(AQUI + "../orbi.js").read()}
{open(AQUI + "../viernes/personajes.js").read()}
{open(AQUI + "../comision/personajes_comi.js").read()}
{open(AQUI + "personajes_noir.js").read()}
{open(AQUI + "escena.js").read()}
</script></body></html>'''
open(W_ + "expediente.html", "w").write(HTML)
NCU = int(DUR * FPS)
async def pagina(p):
    br = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    pg = await br.new_page(viewport={"width": 1080, "height": 1920}); pg.on("pageerror", lambda e: print("ERR", e))
    await pg.goto("file://" + W_ + "expediente.html"); await pg.wait_for_timeout(1200); return br, pg
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
