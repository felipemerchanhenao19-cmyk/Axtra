"""Propuesta de negocio de Apex Play y Apex Domicilios (PDF, sin precios). python propuesta.py <salida.pdf>"""
import sys, os, asyncio
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
FUENTES = open(AQUI + "../../videos/fuentes.html").read() + open(AQUI + "../expediente/fuentes_noir.html").read()
CHROME = next(p for p in ["/opt/pw-browsers/chromium-1243/chrome-linux64/chrome", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"] if os.path.exists(p))
LOGO = '''<svg viewBox="0 0 100 100" width="{t}" height="{t}"><path d="M50 12 L 20 86 M50 12 L 80 86" stroke="{c}" stroke-width="10" stroke-linecap="round" fill="none"/>
  <circle cx="50" cy="56" r="11" fill="#2a6fb0"/><ellipse cx="50" cy="58" rx="36" ry="8" fill="none" stroke="{c}" stroke-width="3" transform="rotate(-12 50 58)"/></svg>'''
def pie(n): return f'<div class="pie"><span>APEX CORPORATION · PROPUESTA DE NEGOCIO</span><span>{n:02d}</span></div>'
def sec(num, titulo, sub=""): return f'<div class="sec"><span>{num}</span>{titulo}</div>{f"<p class=lead>{sub}</p>" if sub else ""}'
def tarjetas(items, cols=2): return f'<div class="grid g{cols}">' + "".join(f'<div class="t"><b>{a}</b><p>{b}</p></div>' for a, b in items) + "</div>"
def pasos(items): return '<div class="pasos">' + "".join(f'<div><i>{i + 1:02d}</i><b>{a}</b><p>{b}</p></div>' for i, (a, b) in enumerate(items)) + "</div>"
CSS = '''<style>
@page { size: Letter; margin: 0; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font: 10.5pt/1.55 "Figtree", sans-serif; color: #0b1f3a; }
.pag { width: 8.5in; height: 11in; padding: 0.75in 0.8in 0.9in; position: relative; page-break-after: always; overflow: hidden; background: #fbfaf7; }
.pag:last-child { page-break-after: auto; }
.pie { position: absolute; left: 0.8in; right: 0.8in; bottom: 0.45in; display: flex; justify-content: space-between; font-size: 7.5pt; letter-spacing: .25em; color: #7a8aa0; border-top: 1px solid rgba(11,31,58,.18); padding-top: 8px; font-weight: 700; }
.sec { font: italic 700 25pt/1.1 "Playfair Display", Georgia, serif; margin: 0 0 10px; display: flex; align-items: baseline; gap: 14px; }
.sec span { font: 700 9pt "Figtree", sans-serif; letter-spacing: .25em; color: #2a6fb0; font-style: normal; }
.lead { font-size: 11.5pt; color: #34465e; margin-bottom: 18px; max-width: 6.3in; }
h3 { font-size: 8.5pt; letter-spacing: .28em; color: #5a6b82; font-weight: 800; margin: 20px 0 10px; text-transform: uppercase; }
.grid { display: grid; gap: 12px; } .g2 { grid-template-columns: 1fr 1fr; } .g3 { grid-template-columns: 1fr 1fr 1fr; }
.t { border: 1px solid rgba(11,31,58,.22); padding: 13px 15px; background: #fff; } .t b { display: block; font-size: 10.5pt; margin-bottom: 3px; } .t p { font-size: 9.5pt; color: #34465e; line-height: 1.45; }
.pasos { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0; border: 1px solid #0b1f3a; }
.pasos div { padding: 14px 14px 16px; border-right: 1px solid rgba(11,31,58,.2); } .pasos div:last-child { border-right: 0; }
.pasos i { display: block; font: italic 700 18pt "Playfair Display", serif; color: #2a6fb0; } .pasos b { display: block; font-size: 10pt; margin: 2px 0 4px; } .pasos p { font-size: 9pt; color: #34465e; line-height: 1.4; }
.oscuro { background: #0b1f3a; color: #fff; padding: 18px 22px; margin-top: 16px; } .oscuro b { color: #9fdcff; font-size: 8.5pt; letter-spacing: .25em; display: block; margin-bottom: 6px; } .oscuro p { font-size: 10.5pt; color: #dfe8f3; }
ul.l { list-style: none; } ul.l li { padding: 7px 0 7px 18px; border-bottom: 1px solid rgba(11,31,58,.12); position: relative; font-size: 10pt; } ul.l li::before { content: ""; position: absolute; left: 0; top: 14px; width: 8px; height: 2px; background: #2a6fb0; }
.arq { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0; border: 1px solid #0b1f3a; margin-top: 4px; }
.arq div { padding: 12px 14px; border-right: 1px solid rgba(11,31,58,.2); } .arq div:last-child { border-right: 0; } .arq b { display: block; font-size: 8pt; letter-spacing: .22em; color: #2a6fb0; margin-bottom: 6px; } .arq p { font-size: 9.3pt; color: #34465e; line-height: 1.5; }
</style>'''
P = []
# 1 · Portada
P.append(f'''<div class="pag" style="background:#0b1f3a;color:#fff;padding:1in 0.9in">
  <div style="display:flex;align-items:center;gap:14px">{LOGO.format(t=54, c="#fff")}<span style="font-size:11pt;letter-spacing:.38em;font-weight:700">APEX CORPORATION</span></div>
  <div style="position:absolute;top:3.1in;left:0.9in;right:0.9in">
    <div style="font-size:9pt;letter-spacing:.32em;color:#9fdcff;font-weight:700;margin-bottom:18px">PROPUESTA DE NEGOCIO · 2026</div>
    <div style="font:italic 700 46pt/1.04 'Playfair Display',serif">Infraestructura de<br>inteligencia artificial<br>para la <span style="color:#7fc4f0">gastronomía.</span></div>
    <div style="width:110px;height:3px;background:#fff;margin:30px 0 24px"></div>
    <p style="font-size:13pt;color:#c9d6e6;max-width:5.6in;line-height:1.5">Apex Play y Apex Domicilios: dos productos sobre una misma plataforma vertical SaaS que digitaliza la atención en mesa y convierte los domicilios en un canal propio del restaurante.</p></div>
  <div style="position:absolute;bottom:0.9in;left:0.9in;right:0.9in;display:flex;justify-content:space-between;font-size:8.5pt;letter-spacing:.25em;color:#9fb6d3;font-weight:700"><span>SOFTWARE E INTELIGENCIA ARTIFICIAL</span><span>COLOMBIA</span></div></div>''')
# 2 · Resumen ejecutivo y problema
P.append(f'''<div class="pag">{sec("01", "Resumen ejecutivo")}
  <p class="lead">Apex Corporation desarrolla software vertical para restaurantes de segmento medio. Nuestra plataforma combina inteligencia artificial conversacional, realidad aumentada y operación en tiempo real para resolver dos cuellos de botella del negocio: la atención en el salón y la venta a domicilio.</p>
  <div class="grid g3">
    <div class="t"><b>Modelo</b><p>SaaS B2B con ingresos por implementación y suscripción recurrente.</p></div>
    <div class="t"><b>Mercado objetivo</b><p>Restaurantes independientes de clase media, con foco en nichos de alta frecuencia.</p></div>
    <div class="t"><b>Distribución</b><p>Red nacional de asesores comerciales con modelo de canal basado en comisión.</p></div></div>
  {sec("02", "El problema")}
  <p class="lead">El restaurante independiente opera con márgenes estrechos y una infraestructura digital pensada para cadenas o para intermediarios.</p>
  {tarjetas([
    ("Fricción en el salón", "En hora pico la toma de pedidos se vuelve el cuello de botella: tiempos de espera altos, errores en las comandas y menor rotación de mesas."),
    ("Dependencia de marketplaces", "Las plataformas de domicilios retienen entre el 20 % y el 30 % de cada pedido y controlan la relación con el cliente final."),
    ("Pérdida de datos propios", "El restaurante no conserva la información de sus clientes: no puede hacer remarketing, fidelización ni análisis de recompra."),
    ("Venta sugerida inconsistente", "El upselling depende del mesero de turno. En los momentos de mayor demanda es lo primero que se pierde."),
    ("Conciliación manual de pagos", "Las transferencias se verifican a mano con capturas de pantalla, con riesgo de fraude y pérdida de tiempo operativo."),
    ("Costo de personal creciente", "Cubrir la demanda pico exige contratar personal adicional que el resto del día queda subutilizado."),
  ])}{pie(2)}</div>''')
# 3 · Solución y Apex Play
P.append(f'''<div class="pag">{sec("03", "La solución")}
  <p class="lead">Una sola plataforma, dos productos. Ambos comparten el mismo núcleo tecnológico: catálogo del restaurante, motor de IA conversacional y panel operativo en tiempo real.</p>
  {sec("04", "Apex Play · Mesero virtual")}
  <p class="lead" style="margin-bottom:14px">Un asistente de inteligencia artificial que atiende cada mesa desde el celular del comensal, sin descargar ninguna aplicación (zero-install).</p>
  <h3>Customer journey</h3>
  {pasos([("Escaneo", "El comensal escanea el código QR de su mesa."), ("Exploración", "Navega la carta visual y ve los platos en 3D sobre su mesa con realidad aumentada."),
          ("Pedido conversacional", "Pide por voz o con botones. La IA confirma, sugiere y resuelve dudas."), ("Envío a operación", "La orden llega estructurada a caja y cocina, con número de mesa.")])}
  <h3>Capacidades</h3>
  {tarjetas([
    ("IA conversacional por voz", "Comprende lenguaje natural, confirma cada ítem y permite corregir el pedido antes de enviarlo."),
    ("Upselling automatizado", "Ofrece de forma consistente bebidas, postres y promociones en cada interacción."),
    ("Realidad aumentada", "Visualización 3D de platos insignia para aumentar la intención de compra."),
    ("Experiencia multilingüe", "Atiende a turistas y visitantes en su idioma, sin personal adicional."),
    ("Catálogo dinámico", "Precios, agotados y promociones se actualizan al instante, sin reimprimir cartas."),
    ("Campañas de temporada", "La experiencia se adapta a fechas clave del calendario comercial."),
  ])}
  <div class="oscuro"><b>PROPUESTA DE VALOR</b><p>Mayor ticket promedio, mayor rotación de mesas y menor carga operativa en hora pico, con el mismo equipo humano enfocado en servicio y no en tomar pedidos.</p></div>{pie(3)}</div>''')
# 4 · Apex Domicilios
P.append(f'''<div class="pag">{sec("05", "Apex Domicilios · Canal D2C")}
  <p class="lead">Un canal de venta directa al consumidor (direct-to-consumer) con la marca del restaurante, que elimina la comisión por pedido y devuelve al negocio la propiedad de su cliente.</p>
  <h3>Flujo operativo</h3>
  {pasos([("Adquisición", "El cliente accede por un enlace propio desde Instagram, WhatsApp o Google."), ("Pedido asistido", "Arma su pedido con el asistente de IA, por voz o con botones."),
          ("Pago verificado", "Paga contra entrega o por Nequi; el sistema valida el comprobante automáticamente."), ("Seguimiento", "El cliente sigue su pedido en tiempo real hasta la entrega.")])}
  <h3>Capacidades</h3>
  {tarjetas([
    ("Cero take rate", "El restaurante conserva el 100 % del valor de cada pedido."),
    ("First-party data", "Cada pedido construye la base de clientes del negocio para fidelización y recompra."),
    ("Conciliación automática", "Lectura y validación de comprobantes de pago para reducir fraude y trabajo manual."),
    ("Logística propia", "Zonas de cobertura, tarifas por zona y pedido mínimo definidos por el restaurante."),
    ("Panel en tiempo real", "Alertas de nuevos pedidos, estados de preparación y contacto directo con el cliente."),
    ("Complemento de marketplaces", "Convive con las apps existentes y migra progresivamente a los clientes recurrentes."),
  ])}
  <div class="oscuro"><b>PROPUESTA DE VALOR</b><p>Mayor margen neto por pedido, control total de la relación con el cliente y un activo de datos que crece con cada venta.</p></div>{pie(4)}</div>''')
# 5 · Tecnología y modelo de negocio
P.append(f'''<div class="pag">{sec("06", "Arquitectura tecnológica")}
  <p class="lead">Plataforma cloud-native y multi-tenant: cada restaurante opera de forma aislada sobre una infraestructura común, lo que permite escalar sin aumentar la complejidad operativa.</p>
  <div class="arq">
    <div><b>EXPERIENCIA</b><p>Aplicación web progresiva, sin instalación. Interfaz por voz y por botones. Visor 3D y realidad aumentada.</p></div>
    <div><b>INTELIGENCIA</b><p>Reconocimiento de voz, modelos de lenguaje y síntesis de voz orquestados en tiempo real, con respaldo por botones si falla la conexión.</p></div>
    <div><b>OPERACIÓN</b><p>Panel de caja en tiempo real, gestión de catálogo, conciliación de pagos e implementación 100 % remota.</p></div></div>
  <ul class="l" style="margin-top:12px">
    <li><b>Seguridad:</b> tráfico cifrado, accesos protegidos y tratamiento de datos conforme a la Ley 1581 de 2012.</li>
    <li><b>Resiliencia:</b> degradación controlada; si la voz no está disponible, el pedido continúa por botones.</li>
    <li><b>Despliegue continuo:</b> mejoras y actualizaciones sin interrumpir la operación del restaurante.</li></ul>
  {sec("07", "Modelo de negocio")}
  <p class="lead">SaaS B2B con ingresos recurrentes y predecibles.</p>
  {tarjetas([
    ("Implementación (setup fee)", "Configuración del catálogo, modelos 3D, códigos QR y capacitación del equipo."),
    ("Suscripción recurrente (MRR)", "Acceso a la plataforma, soporte, mantenimiento y actualizaciones de temporada."),
    ("Expansión de ingresos", "Add-ons como modelos 3D adicionales y nuevas funcionalidades sobre la base instalada."),
    ("Métricas de gestión", "Seguimiento de MRR, churn, LTV/CAC y retención neta de ingresos (NRR)."),
  ])}{pie(5)}</div>''')
# 6 · Go-to-market, ventaja y cierre
P.append(f'''<div class="pag">{sec("08", "Estrategia go-to-market")}
  <ul class="l">
    <li><b>Perfil de cliente ideal (ICP):</b> restaurantes independientes de clase media, con flujo constante de clientes y nichos de alta frecuencia.</li>
    <li><b>Canal de distribución:</b> red nacional de asesores comerciales con comisión por resultado, lo que mantiene un costo de adquisición (CAC) variable.</li>
    <li><b>Atribución:</b> cada asesor tiene un código único que asigna la venta y su comisión.</li>
    <li><b>Expansión por fases:</b> consolidación en Colombia y, posteriormente, apertura de mercados hispanohablantes con socios locales.</li></ul>
  {sec("09", "Ventaja competitiva")}
  {tarjetas([
    ("Integración vertical", "Voz, IA, realidad aumentada, pagos y operación en una sola plataforma, difícil de replicar por partes."),
    ("Costos de cambio", "Catálogo, datos de clientes y procesos del restaurante quedan integrados en el sistema."),
    ("Activo de datos", "Cada interacción mejora las recomendaciones y el conocimiento del comportamiento de compra."),
    ("Marca y personaje", "Orbi, el asistente de Apex, crea una experiencia reconocible para el comensal."),
  ])}
  {sec("10", "Hoja de ruta")}
  {pasos([("Hoy", "Apex Play y Apex Domicilios operativos en Colombia."), ("Corto plazo", "Crecimiento de la red de asesores y de la base instalada."),
          ("Mediano plazo", "Analítica avanzada y herramientas de fidelización."), ("Largo plazo", "Expansión internacional y plataforma unificada.")])}
  <div class="oscuro" style="display:flex;justify-content:space-between;align-items:center;margin-top:22px"><div><b>AGENDE UNA REUNIÓN</b><p style="font-size:13pt;color:#fff;font-weight:700">Presencial o virtual · WhatsApp 310 789 7960</p></div>{LOGO.format(t=48, c="#fff")}</div>{pie(6)}</div>''')
HTML = f'<!doctype html><html><head><meta charset="utf-8">{FUENTES}{CSS}</head><body>{"".join(P)}</body></html>'
async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path=CHROME); pg = await br.new_page()
        await pg.set_content(HTML); await pg.wait_for_timeout(600)
        await pg.pdf(path=sys.argv[1], width="8.5in", height="11in", print_background=True); await br.close()
asyncio.run(main()); print("listo")
