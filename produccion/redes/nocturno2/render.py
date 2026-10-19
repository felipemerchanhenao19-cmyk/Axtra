"""Video «Mesero nocturno» (vertical 1080x1920, 24 cuadros): python render.py <carpeta_trabajo> <salida.mp4>
Requiere <carpeta_trabajo>/voces (de voces.py)."""
import sys, os, json, subprocess, asyncio, time
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
W_ = os.path.abspath(sys.argv[1]) + "/"; SAL = sys.argv[2]; FPS = 24
LIN = json.load(open(W_ + "voces/linea.json")); DUR = LIN["dur"]
HTML = f'''<!doctype html><html><head><meta charset="utf-8">{open(AQUI + "../../videos/fuentes.html").read()}{open(AQUI + "../expediente/fuentes_noir.html").read()}<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }} html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #000; font-family: "Figtree", sans-serif; color: #fff; }}
#escena, #lluvia, #tinte, #negro, #sello {{ position: absolute; inset: 0; }}
#tinte {{ mix-blend-mode: soft-light; }} #negro {{ background: #000; opacity: 0; }}
#titulo {{ position: absolute; left: 50%; top: 46%; width: 1080px; transform: translate(-50%, -50%); text-align: center; opacity: 0; }}
#titulo em {{ display: block; font: italic 700 40px "Playfair Display", Georgia, serif; color: #e8d9b0; margin-bottom: 26px; }}
#titulo b {{ display: block; font: italic 800 150px/0.92 "Figtree", sans-serif; letter-spacing: -.02em; color: #ffd84a; text-shadow: 0 0 24px rgba(255,190,40,.7), 0 0 80px rgba(255,60,40,.5); }}
#titulo small {{ display: block; font: 400 34px "Special Elite", monospace; color: #ff8a7a; letter-spacing: .3em; margin-top: 30px; }}
#barras {{ position: absolute; inset: 0; pointer-events: none; }}
#barras::before, #barras::after {{ content: ""; position: absolute; left: 0; right: 0; height: 120px; background: #000; }} #barras::before {{ top: 0; }} #barras::after {{ bottom: 0; }}
#sub {{ position: absolute; left: 50%; top: 190px; width: max-content; max-width: 960px; transform: translateX(-50%); text-align: center; padding: 18px 34px 22px; font-size: 54px; font-weight: 800; line-height: 1.16;
  color: #ffe9a8; text-shadow: 0 3px 0 #000, 0 0 18px rgba(0,0,0,.9); opacity: 0; }}
#sub small {{ display: block; font: 400 24px "Special Elite", monospace; letter-spacing: .3em; color: #ff8a7a; margin-bottom: 8px; }}
#sub.narra {{ font: 400 52px/1.2 "Special Elite", monospace; color: #f2e8d0; }} #sub.lento {{ font-size: 76px; font-style: italic; color: #fff; }}
#sello {{ display: flex; flex-direction: column; align-items: center; justify-content: center; background: radial-gradient(80% 50% at 50% 40%, rgba(60,10,20,.75) 0%, rgba(5,4,7,.95) 70%); opacity: 0; }}
#frase {{ font: italic 800 64px "Figtree", sans-serif; color: #ffd84a; text-shadow: 0 0 24px rgba(255,190,40,.5); margin-top: 10px; text-align: center; line-height: 1.1; opacity: 0; }}
#logo {{ margin-top: 54px; text-align: center; opacity: 0; }} #logo b {{ font-size: 72px; font-weight: 800; }}
#logo b i {{ display: inline-block; width: 66px; height: 66px; border-radius: 18px; background: #2fbbe8; vertical-align: -8px; margin-right: 16px; position: relative; }}
#logo b i::after {{ content: ""; position: absolute; left: 25px; top: 17px; border-left: 26px solid #0b1626; border-top: 16px solid transparent; border-bottom: 16px solid transparent; }}
#logo span {{ display: block; font-size: 34px; color: #b9c3d0; margin-top: 16px; font-weight: 600; }}
#gancho {{ position: absolute; left: 50%; top: 79%; text-align: center; font: 900 128px/0.95 "Figtree", sans-serif; color: #fff; background: #d1121f; padding: 26px 46px 34px; border-radius: 10px;
  box-shadow: 0 20px 60px rgba(0,0,0,.6); opacity: 0; }} #gancho span {{ display: block; font-size: 42px; letter-spacing: .3em; color: #ffd6d9; margin-bottom: 10px; }}
#vineta {{ position: absolute; inset: 0; background: radial-gradient(75% 60% at 50% 48%, rgba(0,0,0,0) 45%, rgba(0,0,0,.75) 100%); pointer-events: none; }}
#grano {{ position: absolute; inset: 0; width: 100%; height: 100%; opacity: .1; mix-blend-mode: overlay; pointer-events: none; }}
</style></head><body>
<div id="escena"></div><svg id="lluvia" viewBox="0 0 1080 1920" width="1080" height="1920"></svg><div id="tinte"></div>
<div id="titulo"><em>Apex Play presenta</em><b>MESERO<br>NOCTURNO</b><small>Noche 31</small></div>
<div id="sello"><div id="o-final"></div><div id="frase">El mesero que<br>nunca cierra turno.</div><div id="logo"><b><i></i>Apex Play</b><span>El mesero virtual de tu restaurante</span></div></div>
<div id="vineta"></div><canvas id="grano" width="360" height="640"></canvas><div id="sub"></div><div id="gancho"><span>MESA 4</span>40 MIN<br>ESPERANDO</div><div id="negro"></div><div id="barras"></div>
<script>
const LINEA = {json.dumps(LIN, ensure_ascii=False)};
{open(AQUI + "../orbi.js").read()}
{open(AQUI + "../viernes/personajes.js").read()}
{open(AQUI + "personajes_taxi.js").read()}
{open(AQUI + "escena.js").read()}
</script></body></html>'''
open(W_ + "nocturno.html", "w").write(HTML)
NCU = int(DUR * FPS)
async def pagina(p):
    br = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
    pg = await br.new_page(viewport={"width": 1080, "height": 1920}); pg.on("pageerror", lambda e: print("ERR", e))
    await pg.goto("file://" + W_ + "nocturno.html"); await pg.wait_for_timeout(1200); return br, pg
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
