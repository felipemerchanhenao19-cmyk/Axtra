"""Boceto de la página de Apex Corporation: portada en computador y celular + página completa.
python boceto.py <carpeta_salida>"""
import sys, os, base64
from playwright.sync_api import sync_playwright

AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
SALIDA = sys.argv[1] if len(sys.argv) > 1 else AQUI
FUENTES = open(AQUI + "../videos/fuentes.html").read() + open(AQUI + "../redes/expediente/fuentes_noir.html").read()
CHROME = next(c for c in ["/opt/pw-browsers/chromium-1243/chrome-linux64/chrome", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"] if os.path.exists(c))
DOMINIO = "apex.axtra.chat"

# Copia del sitio con las fuentes incrustadas y la animación quieta (para fotografiarla cuadro a cuadro)
html = open(AQUI + "index.html").read().replace("<!--FUENTES-->", FUENTES + "<script>window.SIN_ANIMAR = true</script>")
TEMP = AQUI + "_boceto.html"
open(TEMP, "w").write(html)

def foto(b, ancho, alto, escala, nombre, completa=False):
    pg = b.new_page(viewport={"width": ancho, "height": alto}, device_scale_factor=escala)
    pg.goto("file://" + TEMP); pg.wait_for_timeout(400)
    for i in range(90): pg.evaluate(f"cuadro({2 + i / 30})")   # deja girar a Saturno hasta un ángulo bonito
    ruta = f"{SALIDA}/{nombre}.png"
    pg.screenshot(path=ruta, full_page=completa)
    pg.close()
    return ruta

def datos(ruta): return "data:image/png;base64," + base64.b64encode(open(ruta, "rb").read()).decode()

with sync_playwright() as p:
    b = p.chromium.launch(executable_path=CHROME)
    pc = foto(b, 1440, 900, 1, "_pc")
    cel = foto(b, 390, 800, 2, "_cel")
    completa = foto(b, 1440, 900, 1, "Apex-Corporation-pagina-completa", completa=True)
    completa_cel = foto(b, 390, 844, 2, "_cel_completa", completa=True)
    # Composición: navegador de computador + celular
    lamina = f'''<!doctype html><html><head><meta charset="utf-8">{FUENTES}<style>
      * {{ box-sizing: border-box; margin: 0; }}
      body {{ width: 1800px; height: 1100px; overflow: hidden; position: relative; font-family: Figtree, sans-serif;
             background: radial-gradient(900px 700px at 30% 30%, #1b2a44, transparent 70%), radial-gradient(700px 600px at 90% 90%, rgba(191,155,95,.25), transparent 70%), #0a1120; }}
      .pc {{ position: absolute; left: 70px; top: 90px; width: 1340px; border-radius: 16px; overflow: hidden; box-shadow: 0 50px 100px rgba(0,0,0,.55), 0 0 0 1px rgba(191,155,95,.25); background: #0a1120; }}
      .barra {{ height: 46px; background: #e9e2d4; display: flex; align-items: center; gap: 8px; padding: 0 18px; }}
      .barra i {{ width: 12px; height: 12px; border-radius: 50%; background: #cfc5b3; }}
      .barra span {{ margin-left: 22px; background: #fff; border-radius: 8px; padding: 6px 18px; font-size: 14px; color: #5d6678; width: 560px; }}
      .pc img {{ width: 100%; display: block; }}
      .cel {{ position: absolute; right: 80px; top: 150px; width: 380px; border-radius: 56px; padding: 13px; background: linear-gradient(145deg, #2a3446, #070b13);
              box-shadow: 0 50px 100px rgba(0,0,0,.6), inset 0 0 0 1px rgba(255,255,255,.1); }}
      .cel .pant {{ border-radius: 44px; overflow: hidden; background: #0a1120; padding-top: 44px; position: relative; }}
      .cel .pant::before {{ content: "9:41"; position: absolute; top: 14px; left: 34px; color: #eef3fa; font-size: 15px; font-weight: 700; }}
      .cel .pant::after {{ content: "●●● ▮"; position: absolute; top: 15px; right: 30px; color: #eef3fa; font-size: 11px; letter-spacing: 2px; }}
      .cel img {{ width: 100%; display: block; }}
      .cel::after {{ content: ""; position: absolute; top: 24px; left: 50%; width: 96px; height: 28px; border-radius: 16px; background: #04070d; transform: translateX(-50%); }}
      .rotulo {{ position: absolute; left: 70px; top: 32px; color: #dcc08c; font-size: 15px; font-weight: 700; letter-spacing: .24em; }}
      .rotulo span {{ color: #9aa6ba; font-weight: 500; letter-spacing: .08em; margin-left: 14px; }}
    </style></head><body>
      <div class="rotulo">APEX CORPORATION · BOCETO DE LA PÁGINA WEB <span>{DOMINIO}</span></div>
      <div class="pc"><div class="barra"><i></i><i></i><i></i><span>🔒 {DOMINIO}</span></div><img src="{datos(pc)}"></div>
      <div class="cel"><div class="pant"><img src="{datos(cel)}"></div></div>
    </body></html>'''
    pg = b.new_page(viewport={"width": 1800, "height": 1100})
    pg.set_content(lamina); pg.wait_for_timeout(300)
    pg.screenshot(path=f"{SALIDA}/Apex-Corporation-boceto.png")
    b.close()

for f in [TEMP, pc, cel]: os.remove(f)
print("listo:", SALIDA)
