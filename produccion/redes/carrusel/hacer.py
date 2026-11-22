"""Carrusel de anuncio para Instagram (3 tarjetas 1080x1350, formato 4:5) de Apex Domicilios.
  python personaje.py /tmp/orbi_heroes/carrusel_p01.png   (Personaje 01 con delantal, fondo transparente)
  python hacer.py                                          →  entregables/redes/carrusel/apex-domicilios-1..3.png"""
import os, asyncio, base64, importlib.util
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
_s = importlib.util.spec_from_file_location("motor", AQUI + "../heroes/hacer.py"); motor = importlib.util.module_from_spec(_s); _s.loader.exec_module(motor)
RAIZ = motor.RAIZ; SAL = RAIZ + "entregables/redes/carrusel/"; P01 = motor.TRABAJO + "carrusel_p01.png"
LOGOS = open(RAIZ + "produccion/redes/perfil/logos.js").read()
b64 = lambda p: "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()

CSS = """
*{box-sizing:border-box;margin:0} body{width:1080px;height:1350px;overflow:hidden;font-family:Figtree;color:#fff;position:relative;background:#050a14}
.marca{position:absolute;top:54px;left:64px;display:flex;align-items:center;gap:18px;z-index:5}
.marca .l{width:84px;height:84px;border-radius:50%;overflow:hidden;box-shadow:0 0 0 3px rgba(127,224,255,.35)} .marca .l svg{width:100%;height:100%}
.marca b{font:800 34px Figtree;letter-spacing:-.5px} .marca span{display:block;font:600 21px Figtree;color:#9fdcff;letter-spacing:.14em;text-transform:uppercase}
.grad{position:absolute;inset:0;background:linear-gradient(135deg,#0b2f73 0%,#0e5fb8 45%,#18a7e0 100%)}
.estrellas{position:absolute;inset:0;background-image:radial-gradient(2px 2px at 12% 18%,rgba(255,255,255,.7),transparent),radial-gradient(2px 2px at 82% 12%,rgba(255,255,255,.6),transparent),
 radial-gradient(1.5px 1.5px at 66% 78%,rgba(255,255,255,.5),transparent),radial-gradient(1.5px 1.5px at 28% 86%,rgba(255,255,255,.5),transparent),radial-gradient(2px 2px at 92% 58%,rgba(255,255,255,.55),transparent)}
.anillo{position:absolute;width:1500px;height:420px;border-radius:50%;border:26px solid rgba(255,210,122,.16);transform:rotate(-14deg)}
.punto{position:absolute;bottom:40px;left:0;right:0;display:flex;justify-content:center;gap:12px} .punto i{width:12px;height:12px;border-radius:50%;background:rgba(255,255,255,.35)} .punto i.on{background:#fff}
"""

def tarjeta1():
    return f"""<div style="position:absolute;inset:0;background:radial-gradient(ellipse at 70% 30%,#5a3a22 0%,#2a1a10 45%,#0d0806 100%)"></div>
<div style="position:absolute;inset:0;background:
 radial-gradient(60px 60px at 14% 22%,rgba(255,190,110,.55),transparent 70%),radial-gradient(90px 90px at 30% 12%,rgba(255,170,80,.35),transparent 70%),
 radial-gradient(70px 70px at 8% 48%,rgba(255,200,130,.4),transparent 70%),radial-gradient(110px 110px at 46% 30%,rgba(255,160,70,.25),transparent 70%),
 radial-gradient(50px 50px at 22% 66%,rgba(255,210,150,.35),transparent 70%);filter:blur(6px)"></div>
<img src="{b64(P01)}" style="position:absolute;right:-330px;bottom:-60px;height:1240px;filter:drop-shadow(0 0 40px rgba(54,194,245,.25))">
<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(5,10,20,.88) 0%,rgba(5,10,20,.55) 46%,rgba(5,10,20,0) 72%)"></div>
<div class="marca"><div class="l">{{logo}}</div><div><b>Apex Domicilios</b><span>Apex Corporation</span></div></div>
<div style="position:absolute;left:64px;top:330px;width:900px">
  <div style="font:900 118px/0.92 Figtree;letter-spacing:-3px;text-transform:uppercase">Tu<br>restaurante</div>
  <div style="font:italic 800 96px/1.05 Playfair;color:#bfeeff;margin:10px 0 6px">con su propio link</div>
  <div style="font:900 104px/1 Figtree;letter-spacing:-2px;text-transform:uppercase;color:#7fe0ff;text-shadow:0 0 28px rgba(47,187,232,.95),0 0 70px rgba(47,187,232,.6)">sin comisiones</div>
  <div style="margin-top:70px;display:flex;align-items:center;gap:20px;font:800 54px Figtree">Solo necesitas
    <span style="display:inline-flex;width:100px;height:58px;border-radius:30px;background:#2fbbe8;align-items:center;justify-content:center;font-size:42px;box-shadow:0 0 24px rgba(47,187,232,.8)">→</span></div>
</div>"""

def tarjeta2():
    item = lambda a, b: f"""<div style="display:flex;align-items:center;gap:48px;margin-bottom:84px">
      <div style="flex:none;width:118px;height:118px;border:9px solid #fff;border-radius:16px;position:relative">
        <div style="position:absolute;left:22px;top:-6px;width:46px;height:88px;border-right:15px solid #fff;border-bottom:15px solid #fff;transform:rotate(40deg) translate(18px,-6px);border-radius:3px"></div></div>
      <div style="font:900 72px/1.04 Figtree;letter-spacing:-1px">{a}<br>{b}</div></div>"""
    return f"""<div class="grad"></div><div class="estrellas"></div><div class="anillo" style="left:-260px;top:880px"></div>
<div class="marca"><div class="l">{{logo}}</div><div><b>Apex Domicilios</b><span>Apex Corporation</span></div></div>
<div style="position:absolute;left:96px;top:300px;right:60px">{item("Tu menú", "con precios")}{item("Dirección y zona", "de domicilios")}{item("WhatsApp y", "correo electrónico")}</div>
<div style="position:absolute;left:96px;bottom:110px;font:600 32px Figtree;color:#d6f3ff">Pagos con Wompi o revisando el comprobante. Tú eliges.</div>"""

def tarjeta3():
    return f"""<div class="grad"></div><div class="estrellas"></div><div class="anillo" style="left:-210px;top:930px"></div>
<div class="marca"><div class="l">{{logo}}</div><div><b>Apex Domicilios</b><span>Apex Corporation</span></div></div>
<div style="position:absolute;top:220px;left:0;right:0;text-align:center">
  <div style="display:inline-block;background:#fff;border-radius:22px;padding:6px 46px 14px;font:900 150px/1 Figtree;letter-spacing:-4px;
    background-clip:padding-box;color:#0e5fb8;box-shadow:0 18px 50px rgba(0,0,0,.25)"><span style="background:linear-gradient(90deg,#0b3f9a,#18a7e0);-webkit-background-clip:text;color:transparent">¡LISTO!</span></div>
  <div style="font:800 46px Figtree;margin-top:46px">Recibe pedidos y</div>
  <div style="font:900 100px/0.98 Figtree;letter-spacing:-2px;text-transform:uppercase;margin-top:10px">empieza a<br>vender más</div>
</div>
<div style="position:absolute;left:0;right:0;top:850px;display:flex;justify-content:center;gap:22px">
  {''.join(f'<div style="background:rgba(5,10,20,.42);border:2px solid rgba(191,238,255,.45);border-radius:26px;padding:22px 26px;text-align:center;width:300px"><div style="font:900 52px Figtree;color:{c}">{a}</div><div style="font:600 25px Figtree;color:#d6f3ff;margin-top:4px">{b}</div></div>'
           for a, b, c in [("0 %", "de comisión", "#ffd27a"), ("24/7", "soporte", "#7fe0ff"), ("Auto", "aviso «ya salió»", "#9dffbf")])}
</div>
<div style="position:absolute;left:90px;right:90px;top:1095px;background:linear-gradient(90deg,#ffd27a,#ffb347);color:#1b1205;border-radius:28px;padding:26px 30px;text-align:center;box-shadow:0 16px 44px rgba(0,0,0,.3)">
  <div style="font:900 44px/1.1 Figtree">🎄 Diciembre: 1.er mes GRATIS</div>
  <div style="font:700 28px Figtree;margin-top:6px">para los primeros 5 restaurantes · luego $120.000/mes</div></div>"""

async def main():
    from playwright.async_api import async_playwright
    os.makedirs(SAL, exist_ok=True); fuentes = open(RAIZ + "produccion/videos/fuentes.html").read()
    vox = importlib.util.spec_from_file_location("vox", AQUI + "../voxel/hacer.py"); v = importlib.util.module_from_spec(vox); vox.loader.exec_module(v); playfair = v.playfair()
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path=motor.CHROME)
        for i, f in enumerate([tarjeta1, tarjeta2, tarjeta3], 1):
            pg = await br.new_page(viewport={"width": 1080, "height": 1350}); pg.on("pageerror", lambda e: print("ERR", e))
            html = f"<!doctype html><html><head><meta charset='utf-8'>{fuentes}{playfair}<style>{CSS}</style></head><body>{f()}<script>{LOGOS}; document.querySelectorAll('.l').forEach(e => e.innerHTML = tejido());</script></body></html>"
            await pg.set_content(html.replace("{logo}", "")); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(400)
            await pg.screenshot(path=SAL + f"apex-domicilios-{i}.png"); await pg.close()
        await br.close()
    print("listo", SAL)

if __name__ == "__main__": asyncio.run(main())
