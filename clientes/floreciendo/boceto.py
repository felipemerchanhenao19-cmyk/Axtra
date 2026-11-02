"""Boceto de la portada de Floreciendo Tuluá (computador + celular). python boceto.py <salida.png>"""
import sys, os, asyncio, base64
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
FUENTES = open(AQUI + "../../produccion/videos/fuentes.html").read() + open(AQUI + "../../produccion/redes/expediente/fuentes_noir.html").read()
LOGO = "data:image/png;base64," + base64.b64encode(open(AQUI + "logo.png", "rb").read()).decode()
CHROME = next(c for c in ["/opt/pw-browsers/chromium-1243/chrome-linux64/chrome", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"] if os.path.exists(c))
# Ramo dibujado en línea dorada (sin fotos todavía: las pone la floristería)
def flor(x, y, r, rot, c="#c9a24a", relleno="#f6e3e3"):
    pet = "".join(f'<ellipse cx="0" cy="{-r * 0.55}" rx="{r * 0.32}" ry="{r * 0.55}" transform="rotate({a})" fill="{relleno}" stroke="{c}" stroke-width="1.6"/>' for a in range(0, 360, 60))
    return f'<g transform="translate({x} {y}) rotate({rot})">{pet}<circle r="{r * 0.2}" fill="#e8c97a" stroke="{c}" stroke-width="1.4"/></g>'
def hoja(x, y, rot, s=1): return f'<path d="M0 0 Q 18 -30 0 -62 Q -18 -30 0 0Z" transform="translate({x} {y}) rotate({rot}) scale({s})" fill="#eef3ea" stroke="#c9a24a" stroke-width="1.4"/>'
RAMO = f'''<svg viewBox="0 0 400 460" xmlns="http://www.w3.org/2000/svg">
  <circle cx="200" cy="200" r="185" fill="#f8eded"/><circle cx="200" cy="200" r="185" fill="none" stroke="#c9a24a" stroke-width="1.5"/><circle cx="200" cy="200" r="196" fill="none" stroke="#e3cf9c" stroke-width="1" stroke-dasharray="3 6"/>
  <path d="M200 420 L 190 260 M200 420 L 230 270 M200 420 L 160 280 M200 420 L 250 300" stroke="#9fae8a" stroke-width="3" fill="none"/>
  {hoja(170, 300, -40, 1.2)}{hoja(240, 310, 40, 1.1)}{hoja(140, 230, -70)}{hoja(270, 230, 70)}{hoja(205, 190, 8, .9)}
  {flor(150, 200, 52, 10)}{flor(255, 190, 58, -12, relleno="#fbeaea")}{flor(205, 135, 48, 30, relleno="#fff4f4")}{flor(115, 140, 34, 0)}{flor(300, 125, 32, 20)}{flor(205, 250, 40, -20, relleno="#f3dada")}
  <path d="M150 370 L 250 370 L 232 430 L 168 430Z" fill="#fff" stroke="#c9a24a" stroke-width="2"/><path d="M168 380 Q 200 400 232 380" stroke="#c9a24a" stroke-width="1.5" fill="none"/>
</svg>'''
CHIPS = ["Cumpleaños", "Aniversarios", "Amor y amistad", "Condolencias"]
def portada(movil):
    nav = "" if movil else '<nav><a>Inicio</a><a>Arreglos</a><a>Ocasiones</a><a>Contacto</a></nav>'
    return f'''<div class="sitio {"m" if movil else "d"}">
  <header><img src="{LOGO}" class="logo"><div class="marca"><b>Floreciendo Tuluá</b><span>Composiciones florales hechas arte</span></div>{nav}{"<i class=menu>☰</i>" if movil else ""}</header>
  <section class="hero"><div class="txt"><div class="et">FLORISTERÍA EN TULUÁ · DOMICILIOS</div>
    <h1>Flores que dicen<br><em>lo que sientes.</em></h1>
    <p>Arreglos y composiciones florales para cumpleaños, aniversarios y cada momento especial. Hechos a mano y entregados a domicilio en Tuluá.</p>
    <div class="bot"><a class="b1">Ver arreglos</a><a class="b2">Pedir por WhatsApp</a></div>
    <div class="chips">{"".join(f"<span>{c}</span>" for c in CHIPS)}</div></div>
    <div class="ramo">{RAMO}</div></section>
  <footer><span>◎ @flores_tulua</span><span>✆ 316 107 20 20</span>{"" if movil else "<span>Entregas el mismo día</span>"}</footer></div>'''
HTML = f'''<!doctype html><html><head><meta charset="utf-8">{FUENTES}<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ width: 1800px; height: 1100px; background: linear-gradient(135deg, #efe7dd, #e6ddd2); font-family: "Figtree", sans-serif; position: relative; overflow: hidden; }}
.nav {{ }}
.pc {{ position: absolute; left: 60px; top: 70px; width: 1320px; height: 900px; border-radius: 16px; overflow: hidden; box-shadow: 0 40px 90px rgba(60,40,20,.25); background: #fff; }}
.barra {{ height: 44px; background: #f1ece6; display: flex; align-items: center; gap: 8px; padding: 0 18px; }} .barra i {{ width: 12px; height: 12px; border-radius: 50%; background: #d9cfc4; }}
.barra span {{ margin-left: 24px; background: #fff; border-radius: 8px; padding: 6px 18px; font-size: 14px; color: #8a7d70; width: 520px; }}
.cel {{ position: absolute; right: 70px; top: 120px; width: 390px; height: 820px; border-radius: 52px; background: #1d1a18; padding: 14px; box-shadow: 0 40px 90px rgba(60,40,20,.35); }}
.cel .pant {{ width: 100%; height: 100%; border-radius: 40px; overflow: hidden; background: #fff; }}
.sitio {{ background: #fdfaf6; color: #3b2f26; height: 100%; display: flex; flex-direction: column; }}
header {{ display: flex; align-items: center; gap: 14px; padding: 20px 56px; border-bottom: 1px solid #efe5d6; }}
.logo {{ width: 62px; height: 62px; border-radius: 50%; object-fit: cover; box-shadow: 0 0 0 2px #e3cf9c; }}
.marca b {{ display: block; font: 400 26px "Italiana", serif; letter-spacing: .08em; color: #a8812f; }} .marca span {{ font-size: 11px; letter-spacing: .25em; color: #9b8a78; text-transform: uppercase; }}
nav {{ margin-left: auto; display: flex; gap: 34px; font-size: 15px; color: #6b5b4d; }} nav a:first-child {{ color: #a8812f; border-bottom: 2px solid #c9a24a; padding-bottom: 4px; }}
.hero {{ flex: 1; display: grid; grid-template-columns: 1.1fr 1fr; align-items: center; gap: 30px; padding: 30px 70px; background: radial-gradient(60% 70% at 80% 50%, #fbeeee 0%, rgba(253,250,246,0) 70%); }}
.et {{ font-size: 13px; letter-spacing: .3em; color: #a8812f; font-weight: 700; margin-bottom: 18px; }}
h1 {{ font: 400 66px/1.05 "Italiana", serif; color: #3b2f26; }} h1 em {{ font: italic 700 64px/1.1 "Playfair Display", serif; background: linear-gradient(90deg, #a8812f, #d9b45e, #a8812f); -webkit-background-clip: text; background-clip: text; color: transparent; }}
.hero p {{ font-size: 18px; line-height: 1.6; color: #6b5b4d; margin: 22px 0 28px; max-width: 520px; }}
.bot {{ display: flex; gap: 14px; }} .bot a {{ padding: 16px 30px; border-radius: 40px; font-weight: 700; font-size: 16px; }}
.b1 {{ background: linear-gradient(90deg, #b48a35, #d9b45e); color: #fff; box-shadow: 0 10px 24px rgba(180,138,53,.35); }} .b2 {{ border: 1.5px solid #c9a24a; color: #a8812f; }}
.chips {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 30px; }} .chips span {{ padding: 8px 16px; border-radius: 20px; background: #f8eded; color: #8a5a5a; font-size: 14px; }}
.ramo svg {{ width: 100%; max-height: 640px; }}
footer {{ display: flex; justify-content: center; gap: 48px; padding: 18px; background: #3b2f26; color: #e8d6a8; font-size: 15px; letter-spacing: .05em; }}
.m header {{ padding: 46px 20px 14px; }} .m .logo {{ width: 46px; height: 46px; }} .m .marca b {{ font-size: 19px; }} .m .marca span {{ font-size: 7.5px; }} .menu {{ margin-left: auto; font-style: normal; font-size: 24px; color: #a8812f; }}
.m .hero {{ display: flex; flex-direction: column-reverse; padding: 10px 22px 18px; gap: 6px; text-align: center; }}
.m .ramo svg {{ width: 230px; }} .m .et {{ font-size: 9px; margin-bottom: 10px; }} .m h1 {{ font-size: 38px; }} .m h1 em {{ font-size: 36px; }}
.m .hero p {{ font-size: 13.5px; margin: 12px 0 16px; }} .m .bot {{ flex-direction: column; gap: 10px; }} .m .bot a {{ padding: 13px; font-size: 14px; }}
.m .chips {{ justify-content: center; margin-top: 16px; gap: 6px; }} .m .chips span {{ font-size: 11px; padding: 6px 11px; }}
.m footer {{ gap: 18px; font-size: 12px; padding: 14px 14px 26px; }}
.titulo {{ position: absolute; left: 60px; bottom: 34px; font-size: 14px; letter-spacing: .28em; color: #8a7d70; font-weight: 700; }}
</style></head><body>
<div class="pc"><div class="barra"><i></i><i></i><i></i><span>floreciendotulua.com</span></div><div style="height:856px">{portada(False)}</div></div>
<div class="cel"><div class="pant">{portada(True)}</div></div>
<div class="titulo">BOCETO · PORTADA DE LA PÁGINA WEB · FLORECIENDO TULUÁ</div>
</body></html>'''
async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path=CHROME); pg = await br.new_page(viewport={"width": 1800, "height": 1100}, device_scale_factor=1.5)
        await pg.set_content(HTML); await pg.wait_for_timeout(600); await pg.screenshot(path=sys.argv[1]); await br.close()
asyncio.run(main()); print("listo")
