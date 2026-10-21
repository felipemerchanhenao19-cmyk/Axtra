"""Piezas en blanco y azul marino (1080x1350): reclutamiento de asesores, venta a restaurantes y tarifario.
python hacer.py <carpeta_salida>"""
import sys, os, asyncio
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"; SAL = os.path.abspath(sys.argv[1]) + "/"; os.makedirs(SAL, exist_ok=True)
FUENTES = open(AQUI + "../../videos/fuentes.html").read() + open(AQUI + "../expediente/fuentes_noir.html").read()
LOGO = '''<svg viewBox="0 0 100 100" width="{t}" height="{t}"><path d="M50 12 L 20 86 M50 12 L 80 86" stroke="#0b1f3a" stroke-width="10" stroke-linecap="round" fill="none"/>
  <circle cx="50" cy="56" r="11" fill="url(#lg)"/><defs><radialGradient id="lg" cx="35%" cy="30%"><stop offset="0" stop-color="#7fd0f5"/><stop offset="1" stop-color="#0b1f3a"/></radialGradient></defs>
  <ellipse cx="50" cy="58" rx="36" ry="8" fill="none" stroke="#0b1f3a" stroke-width="3" transform="rotate(-12 50 58)"/></svg>'''
CSS = '''<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { width: 1080px; height: 1350px; background: #fbfaf7; color: #0b1f3a; font-family: "Figtree", sans-serif; position: relative; overflow: hidden; }
.marco { position: absolute; top: 36px; left: 36px; right: 36px; bottom: 236px; border: 2px solid #0b1f3a; }
.marco::after { content: ""; position: absolute; inset: 10px; border: 1px solid rgba(11,31,58,.25); }
.pie-azul { position: absolute; left: 0; right: 0; bottom: 0; height: 200px; background: #0b1f3a; }
.cab { position: absolute; top: 90px; left: 100px; right: 100px; display: flex; align-items: center; gap: 18px; }
.cab b { font-size: 26px; letter-spacing: .32em; font-weight: 700; }
.cab span { margin-left: auto; font-size: 20px; letter-spacing: .25em; color: #5a6b82; font-weight: 600; }
h1 { font: italic 700 86px/1.02 "Playfair Display", Georgia, serif; letter-spacing: -.01em; }
h1 em { font-style: italic; color: #2a6fb0; }
.linea { width: 120px; height: 3px; background: #0b1f3a; margin: 34px 0; }
.sub { font-size: 30px; line-height: 1.45; color: #34465e; max-width: 820px; }
.et { font-size: 20px; letter-spacing: .3em; font-weight: 700; color: #5a6b82; margin-bottom: 18px; }
.cta { position: absolute; left: 100px; right: 100px; bottom: 62px; display: flex; align-items: center; justify-content: space-between; color: #fff; }
.cta div { font-size: 26px; letter-spacing: .04em; } .cta div b { display: block; font-size: 44px; font-weight: 800; letter-spacing: .02em; margin-top: 6px; }
.cta i { font-style: normal; font-size: 22px; letter-spacing: .28em; border: 2px solid #fff; padding: 16px 26px; font-weight: 700; }
</style>'''
def pagina(cuerpo, etiqueta, cta_txt, cta_dato, boton):
    return f'''<!doctype html><html><head><meta charset="utf-8">{FUENTES}{CSS}</head><body><div class="marco"></div>
    <div class="cab">{LOGO.format(t=64)}<b>APEX CORPORATION</b><span>{etiqueta}</span></div>{cuerpo}
    <div class="pie-azul"></div><div class="cta"><div>{cta_txt}<b>{cta_dato}</b></div><i>{boton}</i></div></body></html>'''
WA = "WhatsApp 310 789 7960"
# 1 · Reclutamiento
reclutar = pagina('''<div style="position:absolute;top:220px;left:100px;right:100px">
  <div class="et">CONVOCATORIA · TODO EL PAÍS</div>
  <h1>Buscamos asesores<br>comerciales con<br><em>experiencia.</em></h1><div class="linea"></div>
  <p class="sub">Ofrezca software e inteligencia artificial a restaurantes. Usted trabaja con su red; nosotros ponemos la tecnología.</p>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:26px;margin-top:46px">
    <div style="border:2px solid #0b1f3a;padding:30px 32px"><div class="et" style="margin-bottom:10px">APEX PLAY</div><div style="font:800 54px Figtree">20 %</div><div style="font-size:24px;color:#34465e;margin-top:6px">de cada venta<br>(de $140.000 a $360.000)</div></div>
    <div style="border:2px solid #0b1f3a;padding:30px 32px;background:#0b1f3a;color:#fff"><div class="et" style="margin-bottom:10px;color:#9fb6d3">APEX DOMICILIOS</div><div style="font:800 54px Figtree">$100.000</div><div style="font-size:24px;color:#c9d6e6;margin-top:6px">por cada<br>restaurante vendido</div></div>
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px 40px;margin-top:40px;font-size:25px;color:#34465e">
    <div>— Horario flexible</div><div>— Capacitación y material de venta</div><div>— Código personal de asesor</div><div>— Presentación formal</div></div></div>''',
  "SE BUSCA", "¿Le interesa?", "Responda este mensaje", "ÚNASE")
# 2 · Venta a restaurantes
vender = pagina('''<div style="position:absolute;top:220px;left:100px;right:100px">
  <div class="et">SOFTWARE E IA PARA RESTAURANTES</div>
  <h1>Tecnología<br>que <em>atiende.</em></h1><div class="linea"></div>
  <p class="sub">Su restaurante, atendido por inteligencia artificial: más ventas, menos esperas y clientes que vuelven.</p>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:26px;margin-top:50px">
    <div style="border:2px solid #0b1f3a;padding:34px 34px 38px"><div style="font:italic 700 46px 'Playfair Display',serif">Apex Play</div><div style="font-size:22px;letter-spacing:.2em;color:#5a6b82;margin:8px 0 22px;font-weight:700">MESERO VIRTUAL</div>
      <div style="font-size:25px;line-height:1.7;color:#34465e">Carta por QR en cada mesa<br>Pedidos directo a cocina<br>Platos en 3D y realidad aumentada<br>Habla con el cliente</div></div>
    <div style="border:2px solid #0b1f3a;padding:34px 34px 38px;background:#0b1f3a;color:#fff"><div style="font:italic 700 46px 'Playfair Display',serif">Apex Domicilios</div><div style="font-size:22px;letter-spacing:.2em;color:#9fb6d3;margin:8px 0 22px;font-weight:700">SU CANAL PROPIO</div>
      <div style="font-size:25px;line-height:1.7;color:#c9d6e6">Pedidos sin comisiones<br>Pagos por Nequi verificados<br>Sus clientes, su base de datos<br>Panel en tiempo real</div></div>
  </div></div>''',
  "SOLUCIONES", "Agende una reunión presencial o virtual", WA, "AGENDAR")
# 3 · Tarifario
fila = lambda a, b, fuerte=False: f'<div style="display:flex;justify-content:space-between;padding:15px 0;border-bottom:1px solid rgba(11,31,58,.18);font-size:27px{";font-weight:800" if fuerte else ""}"><span>{a}</span><span style="font-weight:800">{b}</span></div>'
tarifas = pagina(f'''<div style="position:absolute;top:200px;left:100px;right:100px">
  <h1 style="font-size:74px">Tarifas <em>2026</em></h1><div class="linea" style="margin:26px 0 30px"></div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:56px">
    <div><div style="font:italic 700 42px 'Playfair Display',serif;margin-bottom:6px">Apex Play</div><div class="et" style="margin-bottom:8px">INSTALACIÓN SEGÚN MESAS</div>
      {fila("Hasta 15 mesas", "$700.000")}{fila("16 a 20 mesas", "$900.000")}{fila("21 a 32 mesas", "$1.400.000")}{fila("Más de 32 mesas", "Desde $1.800.000")}
      <div style="font-size:23px;line-height:1.55;color:#34465e;margin-top:22px">Incluye 8 platos en 3D con realidad aumentada.<br>Plato 3D adicional: <b>$50.000</b><br>Suscripción con actualizaciones de temporada.</div></div>
    <div><div style="font:italic 700 42px 'Playfair Display',serif;margin-bottom:6px">Apex Domicilios</div><div class="et" style="margin-bottom:8px">CANAL PROPIO DE PEDIDOS</div>
      {fila("Instalación", "Desde $450.000")}{fila("Mensualidad", "$120.000")}
      <div style="background:#0b1f3a;color:#fff;padding:26px 28px;margin-top:24px"><div style="font-size:20px;letter-spacing:.28em;color:#9fb6d3;font-weight:700">CLIENTES FUNDADORES</div>
        <div style="font:800 40px Figtree;margin:8px 0 4px">$60.000 / mes</div><div style="font-size:22px;color:#c9d6e6">50 % de descuento durante todo el primer año</div></div>
      <div style="font-size:23px;line-height:1.55;color:#34465e;margin-top:22px">Incluye lector de comprobantes Nequi.<br>Sin comisiones por pedido.</div></div>
  </div></div>''',
  "TARIFAS", "Cotice su restaurante", WA, "COTIZAR")
async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
        for n, h in [("1-Reclutamiento-asesores", reclutar), ("2-Apex-para-restaurantes", vender), ("3-Tarifario", tarifas)]:
            pg = await br.new_page(viewport={"width": 1080, "height": 1350}); await pg.set_content(h); await pg.wait_for_timeout(400)
            await pg.screenshot(path=SAL + f"Apex-{n}.png"); await pg.close()
        await br.close()
asyncio.run(main()); print("listo")
