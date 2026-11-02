"""Video «Apex · Páginas web» (vertical 1080x1920, 24 cuadros): python render.py <carpeta_trabajo> <salida.mp4>
Requiere <carpeta_trabajo>/voces (de voces.py)."""
import sys, os, json, subprocess, asyncio, time
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
W_ = os.path.abspath(sys.argv[1]) + "/"; SAL = sys.argv[2]; FPS = 24
LIN = json.load(open(W_ + "voces/linea.json")); DUR = LIN["dur"]
LOGO = lambda t, c="#fff": f'<svg viewBox="0 0 100 100" width="{t}" height="{t}"><path d="M50 12 L 20 86 M50 12 L 80 86" stroke="{c}" stroke-width="9" stroke-linecap="round" fill="none"/><circle cx="50" cy="56" r="11" fill="#2fbbe8"/><ellipse cx="50" cy="58" rx="36" ry="8" fill="none" stroke="{c}" stroke-width="3" transform="rotate(-12 50 58)"/></svg>'
SITIOS = [  # diseños de ejemplo (negocios ficticios)
  dict(n="Café Aroma", url="cafearoma.axtra.chat", fondo="#f7efe6", tinta="#3b2416", acento="#b5713a", suave="#ead7c3", lema="Café de especialidad, tostado aquí.", boton="Ver la carta", items=["Espresso", "Capuchino", "Postres"]),
  dict(n="Barbería Clásica", url="barberiaclasica.axtra.chat", fondo="#141414", tinta="#f2efe8", acento="#c9a24a", suave="#2a2722", lema="Estilo que se nota desde lejos.", boton="Reservar cita", items=["Corte", "Barba", "Combo"]),
  dict(n="Boutique Luna", url="boutiqueluna.axtra.chat", fondo="#fbf1f1", tinta="#1f2a44", acento="#d9778a", suave="#f2d9dc", lema="Moda que te acompaña todos los días.", boton="Ver colección", items=["Vestidos", "Blusas", "Accesorios"]),
]
def sitio(d, movil=False):
    tarj = "".join(f'<div class="card" style="background:{d["suave"]}"><div class="foto" style="background:radial-gradient(circle at 35% 30%, {d["acento"]}, {d["suave"]})"></div><b style="color:{d["tinta"]}">{x}</b></div>' for x in d["items"])
    return f'''<div class="web {"mov" if movil else ""}" style="background:{d["fondo"]};color:{d["tinta"]}">
      <div class="cab"><b style="color:{d["acento"]}">{d["n"]}</b>{"<span>☰</span>" if movil else "<nav><a>Inicio</a><a>Catálogo</a><a>Contacto</a></nav>"}</div>
      <div class="hero"><div><h2>{d["lema"]}</h2><div class="btns"><a style="background:{d["acento"]};color:#fff">{d["boton"]}</a><a style="border:2px solid {d["acento"]};color:{d["acento"]}">WhatsApp</a></div></div>
        <div class="arte" style="background:radial-gradient(circle at 40% 35%, {d["acento"]} 0%, {d["suave"]} 70%)"></div></div>
      <div class="cards">{tarj}</div></div>'''
def navegador(d): return f'<div class="sitio"><div class="barra"><i></i><i></i><i></i><span>{d["url"]}</span></div>{sitio(d)}</div>'
HTML = f'''<!doctype html><html><head><meta charset="utf-8">{open(AQUI + "../../videos/fuentes.html").read()}{open(AQUI + "../expediente/fuentes_noir.html").read()}<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }} html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #050b16; font-family: "Figtree", sans-serif; color: #fff; }}
#fondo {{ position: absolute; inset: 0; background: radial-gradient(90% 60% at 50% 40%, #12305a 0%, #071324 55%, #03070e 100%); }}
#luz1, #luz2 {{ position: absolute; width: 900px; height: 900px; border-radius: 50%; filter: blur(80px); opacity: .35; }}
#luz1 {{ left: -200px; top: 200px; background: #1f6fb3; }} #luz2 {{ right: -260px; top: 900px; background: #b48a35; opacity: .18; }}
.esc {{ position: absolute; inset: 0; opacity: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
.et {{ font-size: 24px; letter-spacing: .35em; color: #9fdcff; font-weight: 700; }}
h1 {{ font: italic 700 92px/1.05 "Playfair Display", Georgia, serif; text-align: center; }} h1 em {{ color: #e8c97a; }}
.nav {{ width: 820px; height: 560px; border-radius: 22px; background: #0d1626; border: 2px solid rgba(159,220,255,.45); overflow: hidden; box-shadow: 0 60px 120px rgba(0,0,0,.6), 0 0 60px rgba(47,187,232,.25); }}
.nav .b {{ height: 54px; background: #18243a; display: flex; align-items: center; gap: 10px; padding: 0 22px; }} .nav .b i {{ width: 14px; height: 14px; border-radius: 50%; background: #2c3b55; }}
.nav .b span {{ margin-left: 20px; background: #0d1626; border-radius: 10px; padding: 8px 20px; font-size: 22px; color: #7f93ad; width: 520px; }}
.cursor {{ display: inline-block; width: 3px; height: 24px; background: #9fdcff; vertical-align: -4px; }}
.vacio {{ height: 566px; display: flex; flex-direction: column; align-items: center; justify-content: center; color: #8ea3bf; font-size: 34px; gap: 18px; }} .vacio b {{ font-size: 140px; color: #ff6b7a; }}
.barrido {{ background: linear-gradient(100deg, #fff 0%, #fff 42%, #ffe9b0 50%, #fff 58%, #fff 100%); background-size: 300% 100%; -webkit-background-clip: text; background-clip: text; color: transparent; }}
#marca .nombre {{ font-size: 64px; letter-spacing: .3em; font-weight: 800; margin-top: 40px; padding-left: .3em; }}
.cel {{ width: 420px; height: 840px; border-radius: 60px; background: #0b0f17; border: 3px solid #2a3446; padding: 16px; box-shadow: 0 60px 120px rgba(0,0,0,.6); }}
.cel .p {{ width: 100%; height: 100%; border-radius: 46px; overflow: hidden; background: #0b1626; position: relative; }}
#software .orbe {{ width: 300px; height: 300px; margin: 120px auto 0; }} #software .orbe svg {{ width: 100%; height: 100%; }}
#software .menu {{ position: absolute; left: 24px; right: 24px; bottom: 40px; display: grid; gap: 14px; }} #software .menu div {{ background: #12233d; border-radius: 18px; padding: 18px 20px; font-size: 22px; display: flex; justify-content: space-between; color: #cfe3f5; }}
.lado {{ font-size: 30px; color: #c9d6e6; margin-top: 50px; text-align: center; max-width: 820px; line-height: 1.4; }}
#webs {{ perspective: 1800px; }} .carr {{ position: relative; width: 1080px; height: 760px; transform-style: preserve-3d; }}
.sitio {{ position: absolute; left: 50%; top: 50%; width: 700px; height: 560px; border-radius: 18px; overflow: hidden; box-shadow: 0 50px 100px rgba(0,0,0,.6); background: #fff; }}
.barra {{ height: 40px; background: #e9e6e1; display: flex; align-items: center; gap: 8px; padding: 0 16px; }} .barra i {{ width: 11px; height: 11px; border-radius: 50%; background: #c9c3bb; }} .barra span {{ margin-left: 14px; background: #fff; border-radius: 8px; padding: 4px 14px; font-size: 15px; color: #7a7066; }}
.web {{ height: calc(100% - 40px); display: flex; flex-direction: column; }} .web .cab {{ display: flex; align-items: center; padding: 18px 28px; font-size: 26px; }} .web .cab b {{ font: italic 700 30px "Playfair Display", serif; }}
.web nav {{ margin-left: auto; display: flex; gap: 22px; font-size: 16px; opacity: .75; }} .web .cab span {{ margin-left: auto; font-size: 28px; }}
.web .hero {{ display: grid; grid-template-columns: 1.2fr 1fr; gap: 20px; padding: 10px 28px; align-items: center; flex: 1; }} .web h2 {{ font: 700 36px/1.12 "Playfair Display", serif; }}
.btns {{ display: flex; gap: 10px; margin-top: 18px; }} .btns a {{ padding: 10px 18px; border-radius: 30px; font-size: 15px; font-weight: 700; }}
.arte {{ height: 200px; border-radius: 20px; }} .cards {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; padding: 0 28px 24px; }}
.card {{ border-radius: 14px; padding: 10px; }} .card .foto {{ height: 70px; border-radius: 10px; margin-bottom: 8px; }} .card b {{ font-size: 15px; }}
.mov .hero {{ grid-template-columns: 1fr; text-align: center; padding: 10px 18px; }} .mov h2 {{ font-size: 30px; }} .mov .btns {{ justify-content: center; flex-direction: column; }} .mov .arte {{ height: 160px; order: -1; margin-bottom: 14px; }}
.mov .cards {{ grid-template-columns: 1fr 1fr; padding: 0 18px 18px; }} .mov .cards .card:last-child {{ display: none; }}
#funciones {{ flex-direction: row; gap: 50px; justify-content: center; }} .chips {{ display: flex; flex-direction: column; gap: 26px; }}
.chip {{ display: flex; align-items: center; gap: 18px; background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.18); border-radius: 20px; padding: 22px 26px; font-size: 30px; font-weight: 700; width: 420px; }}
.chip i {{ width: 52px; height: 52px; border-radius: 14px; background: #2fbbe8; display: flex; align-items: center; justify-content: center; font-style: normal; color: #071324; font-size: 30px; font-weight: 900; }}
#precio .joven {{ font-size: 34px; color: #c9d6e6; text-align: center; line-height: 1.4; max-width: 820px; }}
#precio .grande {{ font: italic 700 96px/1.05 "Playfair Display", serif; text-align: center; margin: 60px 0 30px; }}
#precio .desde {{ font-size: 40px; letter-spacing: .1em; color: #c9d6e6; }} #precio .desde b {{ display: block; text-align: center; font-size: 130px; font-weight: 900; letter-spacing: 0; }}
.brillo {{ background: linear-gradient(100deg, #d9b45e 0%, #f3d58c 42%, #fff 50%, #f3d58c 58%, #d9b45e 100%); background-size: 300% 100%; -webkit-background-clip: text; background-clip: text; color: transparent; }}
#cierre .lema {{ font: italic 700 64px "Playfair Display", serif; margin: 34px 0 60px; text-align: center; }}
#cierre .dato {{ font-size: 40px; font-weight: 700; margin: 10px 0; opacity: 0; }} #cierre .dato span {{ color: #9fdcff; }}
#sub {{ position: absolute; left: 50%; bottom: 210px; transform: translateX(-50%); width: 940px; text-align: center; font-size: 46px; font-weight: 800; line-height: 1.2; text-shadow: 0 4px 18px rgba(0,0,0,.8); opacity: 0; }}
.nota {{ position: absolute; bottom: 140px; font-size: 20px; letter-spacing: .25em; color: #7f93ad; }}
#barras::before, #barras::after {{ content: ""; position: absolute; left: 0; right: 0; height: 90px; background: #000; z-index: 50; }} #barras::before {{ top: 0; }} #barras::after {{ bottom: 0; }}
#vineta {{ position: absolute; inset: 0; background: radial-gradient(75% 60% at 50% 48%, rgba(0,0,0,0) 50%, rgba(0,0,0,.6) 100%); }}
#grano {{ position: absolute; inset: 0; width: 100%; height: 100%; opacity: .06; mix-blend-mode: overlay; }}
</style></head><body><div id="fondo"></div><div id="luz1"></div><div id="luz2"></div>
<div class="esc" id="gancho"><h1 style="margin-bottom:60px">¿Tu negocio aún<br>no tiene <em>página web</em>?</h1><div class="nav"><div class="b"><i></i><i></i><i></i><span>tunegocio.com<span class="cursor"></span></span></div><div class="vacio"><b>404</b>Página no encontrada</div></div></div>
<div class="esc" id="marca"><div class="logo">{LOGO(300)}</div><div class="nombre barrido">APEX CORPORATION</div></div>
<div class="esc" id="software"><div class="et">SOFTWARE E IA</div><div class="cel" style="margin-top:40px"><div class="p"><div class="orbe"></div><div class="menu"><div><span>Bandeja paisa</span><b>Pedir</b></div><div><span>Limonada de coco</span><b>Pedir</b></div><div><span>Postre de la casa</span><b>Pedir</b></div></div></div></div>
  <div class="lado">Para la industria gastronómica</div></div>
<div class="esc" id="webs"><div class="et">PÁGINAS WEB</div><div class="carr">{"".join(navegador(d) for d in SITIOS)}</div><div class="nota">DISEÑOS DE EJEMPLO</div></div>
<div class="esc" id="funciones"><div class="cel" style="width:380px;height:780px"><div class="p">{sitio(SITIOS[0], True)}</div></div>
  <div class="chips"><div class="chip"><i>1</i>Catálogo con fotos</div><div class="chip"><i>2</i>Botón de WhatsApp</div><div class="chip"><i>3</i>Diseño para celular</div></div></div>
<div class="esc" id="precio"><div class="joven">Somos una empresa joven<br>que apenas está comenzando.</div><div class="grande">Menos de la <em class="brillo">mitad</em><br>de lo normal.</div><div class="desde">PÁGINAS WEB DESDE<b class="brillo">$99.000</b></div></div>
<div class="esc" id="cierre"><div class="logo">{LOGO(230)}</div><div class="nombre barrido" style="font-size:54px;letter-spacing:.3em;font-weight:800;margin-top:30px">APEX CORPORATION</div><div class="lema">Tecnología para tu negocio.</div>
  <div class="dato"><span>Instagram</span> @apex_corporationn</div><div class="dato"><span>WhatsApp</span> 310 789 7960</div></div>
<div id="vineta"></div><canvas id="grano" width="360" height="640"></canvas><div id="sub"></div><div id="barras"></div>
<script>
const LINEA = {json.dumps(LIN, ensure_ascii=False)};
{open(AQUI + "../orbi.js").read()}
{open(AQUI + "escena.js").read()}
</script></body></html>'''
open(W_ + "webs.html", "w").write(HTML)
NCU = int(DUR * FPS)
async def pagina(p):
    br = await p.chromium.launch(executable_path=next(c for c in ["/opt/pw-browsers/chromium-1243/chrome-linux64/chrome", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"] if os.path.exists(c)))
    pg = await br.new_page(viewport={"width": 1080, "height": 1920}); pg.on("pageerror", lambda e: print("ERR", e))
    await pg.goto("file://" + W_ + "webs.html"); await pg.wait_for_timeout(1200); return br, pg
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
