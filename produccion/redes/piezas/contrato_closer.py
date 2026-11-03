"""Contrato de prestación de servicios comerciales para closers de venta de Apex (PDF en azul marino y dorado).
Uso: python contrato_closer.py <salida.pdf> [--nombre ... --cc ... --ciudad ... --codigo ... --correo ... --whatsapp ... --fecha ... --numero ... --cc-apex ...]
Sin datos, los campos quedan en línea para llenar a mano. Las condiciones comerciales están en el texto de las cláusulas 4, 5, 10 y 11 y en el Anexo 2."""
import os, argparse, asyncio
from html import escape

AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
FUENTES = open(AQUI + "../../videos/fuentes.html").read() + open(AQUI + "../expediente/fuentes_noir.html").read()
CHROME = next(c for c in ["/opt/pw-browsers/chromium-1243/chrome-linux64/chrome", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"] if os.path.exists(c))

ap = argparse.ArgumentParser()
ap.add_argument("salida")
for k in ["nombre", "cc", "ciudad", "codigo", "correo", "whatsapp", "fecha", "numero", "cc-apex"]:
    ap.add_argument("--" + k, default="")
A = ap.parse_args()
def campo(v): return f'<b class="v">{escape(v)}</b>' if v else '<span class="l"></span>'
def fila(etiqueta, v): return f'<div class="fila"><i>{etiqueta}</i>{campo(v)}</div>'

LOGO = ('<svg viewBox="0 0 100 100" width="46" height="46"><rect x="1" y="1" width="98" height="98" rx="18" fill="#16253d" stroke="#c9a86b" stroke-width="2"/>'
        '<path d="M27 73 L50 27 L73 73 M36 55 H64" stroke="#c9a86b" stroke-width="7" fill="none" stroke-linejoin="round"/></svg>')

CAPITULOS = [
  ("I", "Objeto y naturaleza del contrato", [
    ("Objeto", "EL CLOSER se obliga a prestar, con autonomía y por su propia cuenta, servicios de prospección, presentación y cierre de ventas de los productos de software e inteligencia artificial de APEX —Apex Play, Apex Domicilios y los demás que APEX autorice por escrito (en adelante, «LOS PRODUCTOS»)— a restaurantes y negocios del sector gastronómico (en adelante, «LOS CLIENTES»), de forma remota y dentro del territorio colombiano."),
    ("Naturaleza independiente", "Este contrato es de naturaleza civil y comercial. No genera relación laboral, subordinación, horario de trabajo, salario ni prestaciones sociales. EL CLOSER organiza libremente su tiempo, lugar y métodos de trabajo; utiliza sus propios equipos y medios (celular, computador e internet) y asume sus gastos. EL CLOSER es responsable de sus aportes al Sistema de Seguridad Social Integral y de sus obligaciones tributarias, en los términos que señale la ley."),
    ("Vigencia", "El contrato tiene una duración de seis (6) meses contados desde la fecha de inicio y se prorrogará automáticamente por periodos iguales, salvo que una de las partes manifieste por escrito su intención de no renovarlo."),
  ]),
  ("II", "Obligaciones de las partes", [
    ("Actividad mínima semanal", "EL CLOSER realizará como mínimo cinco (5) llamadas efectivas por semana calendario, de lunes a domingo. Se entiende por llamada efectiva la conversación sostenida con el dueño, gerente o administrador de un restaurante, en la que se presenta a APEX y se indaga su interés. Las llamadas deben hacerse a restaurantes distintos y no asignados a otro closer."),
    ("Reporte semanal de llamadas", "Cada semana, a más tardar el domingo a las 8:00 p. m., EL CLOSER enviará a APEX, por WhatsApp o al correo apexcorporation@axtra.chat, el reporte de sus llamadas en el formato del Anexo 1, con la siguiente información por cada llamada: (a) fecha; (b) nombre del restaurante y ciudad; (c) nombre y cargo de la persona contactada; (d) teléfono de contacto; (e) estado: «INTERESADO» o «NO INTERESADO»; y (f) observaciones: motivo de la respuesta y próximo paso acordado, por ejemplo la fecha de la reunión o de la demostración. La información reportada debe ser veraz y verificable; APEX podrá confirmarla directamente con los restaurantes."),
    ("Gestión de prospectos interesados", "Cuando un restaurante quede en estado «INTERESADO», EL CLOSER agendará una presentación o demostración, que podrá realizar por videollamada o WhatsApp con el material oficial, y hará el seguimiento hasta el cierre o la negativa definitiva. APEX brindará apoyo comercial cuando EL CLOSER lo solicite."),
    ("Reglas de venta", "EL CLOSER se obliga a: (a) ofrecer LOS PRODUCTOS únicamente con los precios, condiciones y materiales oficiales de APEX; (b) no conceder descuentos, plazos ni beneficios no autorizados por escrito; (c) no prometer funcionalidades, resultados ni tiempos distintos a los informados por APEX; (d) informar al cliente que, para iniciar la instalación, debe pagar a APEX como mínimo el cincuenta por ciento (50&nbsp;%) de su valor y el saldo al finalizarla; (e) identificarse siempre como closer de APEX y tratar a los clientes con respeto, sin desacreditar a la competencia; y (f) registrar cada venta cerrada enviando a APEX los datos del restaurante y de su responsable, el producto, el plan y el número de mesas, cuando aplique."),
    ("Manejo de dinero", "Todo pago de LOS CLIENTES se realizará exclusivamente a las cuentas de APEX. EL CLOSER no está autorizado para recibir dinero, anticipos ni pagos de ningún tipo a nombre de APEX. Si EL CLOSER recibe dinero de clientes, se apropia de sumas de APEX o incurre en cualquier otra conducta ilegal o fraudulenta, APEX terminará el contrato de inmediato, exigirá la devolución de esas sumas y presentará la denuncia penal correspondiente ante las autoridades competentes, sin perjuicio de las demás acciones legales a que haya lugar."),
    ("Obligaciones de APEX", "APEX se obliga a: (a) entregar a EL CLOSER su código personal, el acceso a la demostración, el material de venta y la tabla de precios vigente; (b) brindar apoyo comercial por WhatsApp o correo, de lunes a domingo entre las 6:00 a. m. y las 11:00 p. m.; (c) realizar la instalación de LOS PRODUCTOS vendidos dentro de los plazos informados al cliente; (d) informar a EL CLOSER cuando se confirme el pago de cada venta; y (e) liquidar y pagar las comisiones en los términos de este contrato."),
  ]),
  ("III", "Comisiones", [
    ("Valor de las comisiones", "Como única remuneración, EL CLOSER recibirá: (a) <b>Apex Play:</b> el treinta y cinco por ciento (35&nbsp;%) del valor de la instalación efectivamente pagado por el cliente; y (b) <b>Apex Domicilios:</b> doscientos mil pesos ($200.000) por cada restaurante cuya instalación haya sido pagada. La comisión se calcula sin incluir impuestos, costos de envío ni servicios contratados después de la instalación. Las mensualidades de LOS CLIENTES no generan comisión. El Anexo 2 presenta los valores de referencia."),
    ("Causación de la comisión", "La comisión se causa únicamente cuando el cliente ha pagado a APEX el cien por ciento (100&nbsp;%) del valor de la instalación. Para iniciar la instalación, el cliente debe pagar como mínimo el cincuenta por ciento (50&nbsp;%); ese anticipo por sí solo no genera comisión. Las llamadas, reuniones o prospectos interesados sin pago total tampoco generan remuneración. La comisión se paga completa, en un solo pago."),
    ("Plazo y forma de pago", "APEX pagará la comisión en un plazo de entre ocho (8) y quince (15) días calendario, contados desde la fecha en que el cliente complete el pago del cien por ciento (100&nbsp;%) de la instalación, mediante transferencia bancaria o Nequi y previa presentación de la cuenta de cobro de EL CLOSER. APEX practicará las retenciones que ordene la ley."),
    ("Atribución de clientes", "Cada venta se atribuye al closer cuyo código quede registrado primero en la base de APEX. Los restaurantes reportados por EL CLOSER en estado «INTERESADO» quedan asignados a su nombre por sesenta (60) días; si la venta se cierra en ese plazo, la comisión le corresponde aunque APEX intervenga en el cierre. En caso de conflicto entre closers, APEX decidirá según la fecha del primer reporte."),
    ("Política de no devoluciones", "APEX no realiza devoluciones de dinero a LOS CLIENTES por ningún concepto, incluidos el anticipo y el saldo de la instalación. EL CLOSER deberá informarlo al cliente antes del cierre y no podrá ofrecer devoluciones ni garantías de reembolso. Una vez causada, la comisión de EL CLOSER no se ve afectada si el cliente cancela posteriormente el servicio."),
  ]),
  ("IV", "Confidencialidad, propiedad y datos", [
    ("Confidencialidad", "EL CLOSER guardará reserva sobre toda la información no pública de APEX a la que acceda: precios internos, márgenes, clientes y prospectos, demostraciones, material de capacitación, estrategias comerciales y funcionamiento de LOS PRODUCTOS. No podrá revelarla, copiarla ni usarla para fines distintos a este contrato. Esta obligación se mantiene durante tres (3) años después de terminado el contrato."),
    ("No desvío de clientes", "Durante la vigencia del contrato y por doce (12) meses después de su terminación, EL CLOSER no ofrecerá a los clientes y prospectos que conoció por medio de APEX productos o servicios competidores, ni los inducirá a terminar su relación con APEX."),
    ("Propiedad intelectual y uso de marca", "Las marcas, nombres, logotipos, personajes (incluido «Orbi»), software, imágenes, videos y materiales de venta son propiedad exclusiva de APEX. EL CLOSER solo podrá usarlos para la promoción autorizada, sin modificarlos, y no podrá crear perfiles, páginas o anuncios a nombre de APEX sin autorización escrita. Tampoco intentará acceder al código, los servidores o los sistemas internos de APEX."),
    ("Protección de datos personales", "EL CLOSER tratará los datos de los restaurantes y de sus representantes conforme a la Ley 1581 de 2012, solo para los fines de este contrato, y no enviará mensajes masivos ni no solicitados. EL CLOSER autoriza a APEX a tratar sus datos personales para la gestión del contrato y el pago de comisiones."),
  ]),
  ("V", "Terminación y disposiciones finales", [
    ("Terminación", "Cualquiera de las partes podrá terminar el contrato en cualquier momento, con aviso escrito de ocho (8) días calendario. APEX podrá terminarlo de inmediato, sin indemnización, si EL CLOSER: (a) no cumple la actividad mínima o no envía el reporte durante dos (2) semanas consecutivas; (b) reporta información falsa; (c) recibe dinero de clientes o incurre en cualquier conducta ilegal o fraudulenta; o (d) incumple las cláusulas 15, 16 o 17. Al terminar, los prospectos asignados quedan liberados, EL CLOSER devolverá o eliminará el material de APEX y APEX pagará las comisiones causadas, incluidas las de ventas cerradas por EL CLOSER cuyo pago total se complete dentro de los treinta (30) días siguientes a la terminación, salvo que esta obedezca a las causales (b), (c) o (d)."),
    ("Cláusula penal", "El incumplimiento de las cláusulas 8, 15, 16 o 17 obligará a EL CLOSER a pagar a APEX, a título de pena, la suma de dos millones de pesos ($2.000.000), sin perjuicio del cobro de los perjuicios adicionales que se demuestren."),
    ("Disposiciones finales", "(a) Este contrato se rige por las leyes de la República de Colombia. (b) Las diferencias se resolverán primero por arreglo directo dentro de los quince (15) días siguientes a su notificación y, en su defecto, mediante conciliación. (c) Las notificaciones se harán por escrito a los correos o números de WhatsApp registrados en el cuadro de datos. (d) Las partes aceptan la firma por medios electrónicos, incluida la respuesta «ACEPTO» por WhatsApp o correo, conforme a la Ley 527 de 1999. (e) Este documento, con sus anexos, reemplaza cualquier acuerdo verbal o mensaje anterior sobre la misma materia."),
  ]),
]
EXTRA = {
  4: '<div class="clave"><div><strong>5</strong><span>llamadas efectivas por semana</span></div><div><strong>Domingo · 8:00 p. m.</strong><span>entrega del reporte semanal</span></div><div><strong>2 estados</strong><span>Interesado · No interesado</span></div></div>',
  10: '<div class="clave"><div><strong>35&nbsp;%</strong><span>Apex Play · sobre la instalación</span></div><div><strong>$200.000</strong><span>Apex Domicilios · por restaurante</span></div><div><strong>8 a 15 días</strong><span>pago tras el 100&nbsp;% del cliente</span></div></div>',
}

n = 0; cuerpo = ""
for num, titulo, clausulas in CAPITULOS:
    cuerpo += f'<div class="cap"><small>CAPÍTULO {num}</small><h2>{titulo}</h2></div>'
    for t, texto in clausulas:
        n += 1
        cuerpo += f'<p class="cl"><b class="n">Cláusula {n}.</b> <b class="t">{t.upper()}.</b> {texto}</p>' + EXTRA.get(n, "")

filas_reporte = "".join(f'<tr><td class="c">{i}</td><td></td><td></td><td></td><td></td><td class="est"><span class="cb"></span> I &nbsp; <span class="cb"></span> NI</td><td></td></tr>' for i in range(1, 8))
PLAY = [("Hasta 15 mesas", "$700.000", "$350.000", "$245.000"), ("16 a 20 mesas", "$900.000", "$450.000", "$315.000"),
        ("21 a 32 mesas", "$1.400.000", "$700.000", "$490.000"), ("Más de 32 mesas", "Desde $1.800.000", "Desde $900.000", "Desde $630.000")]
filas_com = "".join(f'<tr><td><b>Apex Play</b> · {a}</td><td>{b}</td><td>{c}</td><td class="oro">{d}</td></tr>' for a, b, c, d in PLAY)
filas_com += '<tr><td><b>Apex Domicilios</b> · Instalación</td><td>Desde $450.000</td><td>Desde $225.000</td><td class="oro">$200.000</td></tr>'

CSS = """<style>
@page { size: Letter; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font: 9.1pt/1.45 "Figtree", sans-serif; color: #1d2738; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
.portada { background: #0f1b2e; color: #fff; border-radius: 10px; padding: 22px 26px 24px; position: relative; overflow: hidden; }
.portada::after { content: ""; position: absolute; right: -150px; bottom: -150px; width: 240px; height: 240px; border: 1.5px solid rgba(201,168,107,.35); border-radius: 50%; }
.marca { display: flex; align-items: center; gap: 12px; }
.marca b { display: block; letter-spacing: .32em; font-size: 9.6pt; font-weight: 700; }
.marca span { display: block; font-size: 6.6pt; letter-spacing: .26em; color: #c9a86b; margin-top: 3px; font-weight: 700; }
.portada h1 { font: italic 700 23pt/1.12 "Playfair Display", Georgia, serif; margin: 20px 0 8px; max-width: 5.2in; }
.portada .sub { font-size: 7.4pt; letter-spacing: .3em; color: #d9bf8c; font-weight: 700; }
.portada .num { position: absolute; top: 24px; right: 26px; text-align: right; font-size: 7.6pt; color: #c9d3e0; line-height: 2; }
.portada .num b { color: #fff; }
.datos { display: grid; grid-template-columns: 1fr 1fr; margin: 12px 0 10px; border: 1px solid #d8c49b; border-radius: 8px; overflow: hidden; background: #fcfaf5; }
.datos > div { padding: 10px 14px 12px; } .datos > div + div { border-left: 1px solid #e6d7b8; }
.datos h4 { font-size: 7.2pt; letter-spacing: .28em; color: #a8823f; margin-bottom: 5px; }
.fila { display: flex; gap: 6px; font-size: 8.5pt; margin: 4px 0; align-items: baseline; }
.fila i { font-style: normal; color: #5d6b80; min-width: 96px; }
.fila .l { flex: 1; border-bottom: 1px solid #9aa6b8; height: 11px; }
.fila .v { flex: 1; color: #0f1b2e; }
.intro { text-align: justify; }
.cap { margin: 12px 0 6px; break-after: avoid; }
.cap small { display: block; font-size: 6.8pt; letter-spacing: .32em; color: #a8823f; font-weight: 700; }
.cap h2 { font: italic 700 14pt "Playfair Display", Georgia, serif; color: #0f1b2e; padding-bottom: 4px; border-bottom: 1.2px solid #c9a86b; }
.cl { margin: 0 0 6px; text-align: justify; }
.cl b.n { color: #a8823f; } .cl b.t { color: #0f1b2e; letter-spacing: .02em; }
.clave { display: grid; grid-template-columns: repeat(3, 1fr); border: 1px solid #0f1b2e; border-radius: 8px; overflow: hidden; margin: 1px 0 9px; break-inside: avoid; }
.clave div { padding: 7px 12px 8px; } .clave div + div { border-left: 1px solid #d9dfe8; }
.clave div:nth-child(2) { background: #0f1b2e; border-left: 0; } .clave div:nth-child(2) strong { color: #d9bf8c; } .clave div:nth-child(2) span { color: #c9d3e0; }
.clave strong { display: block; font-size: 12.5pt; font-weight: 800; color: #0f1b2e; } .clave span { font-size: 7.4pt; color: #5d6b80; }
.cierre { margin-top: 8px; text-align: justify; break-inside: avoid; }
.firmas { display: grid; grid-template-columns: 1fr 1fr; gap: 44px; margin-top: 6px; break-inside: avoid; }
.firmas > div { font-size: 8.3pt; line-height: 1.6; }
.firmas .raya { height: 42px; border-bottom: 1.2px solid #0f1b2e; margin-bottom: 5px; }
.firmas h5 { font-size: 7.2pt; letter-spacing: .26em; color: #a8823f; margin-bottom: 3px; }
.anexo { break-before: page; }
.anexo .linea { display: flex; gap: 18px; font-size: 8.5pt; margin: 4px 0 10px; } .anexo .linea span { flex: 1; } .anexo .linea .l { display: inline-block; width: 60%; border-bottom: 1px solid #9aa6b8; height: 10px; }
table { width: 100%; border-collapse: collapse; font-size: 8pt; }
th { background: #0f1b2e; color: #fff; font-weight: 700; padding: 6px 6px; text-align: left; font-size: 7.2pt; letter-spacing: .03em; }
td { border: 1px solid #c8cfda; height: 27px; padding: 3px 6px; vertical-align: middle; }
td.c { text-align: center; color: #a8823f; font-weight: 700; } td.est { font-size: 7.4pt; white-space: nowrap; }
.cb { display: inline-block; width: 8px; height: 8px; border: 1px solid #0f1b2e; vertical-align: -1px; }
.nota { font-size: 7.6pt; color: #5d6b80; margin-top: 6px; }
.resumen { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top: 10px; }
.resumen div { border: 1px solid #d8c49b; border-radius: 6px; padding: 7px 10px; font-size: 7.6pt; color: #5d6b80; background: #fcfaf5; }
.resumen div b { display: block; height: 16px; border-bottom: 1px solid #9aa6b8; margin-top: 6px; }
.com td { height: 24px; } td.oro { color: #a8823f; font-weight: 800; }
</style>"""

HTML = f"""<!doctype html><html><head><meta charset="utf-8">{FUENTES}{CSS}</head><body>
<div class="portada">
  <div class="marca">{LOGO}<div><b>APEX CORPORATION</b><span>SOFTWARE E INTELIGENCIA ARTIFICIAL</span></div></div>
  <div class="num">CONTRATO N.º <b>{escape(A.numero) if A.numero else "________"}</b><br>FECHA DE INICIO <b>{escape(A.fecha) if A.fecha else "________"}</b></div>
  <h1>Contrato de prestación de servicios comerciales</h1>
  <div class="sub">CLOSER DE VENTAS · MODALIDAD REMOTA · REMUNERACIÓN POR COMISIÓN</div>
</div>
<div class="datos">
  <div><h4>APEX</h4>{fila("Representante", "Juan Felipe Merchán Henao")}{fila("C.C.", A.cc_apex)}{fila("Domicilio", "Tuluá, Valle del Cauca")}{fila("Correo", "apexcorporation@axtra.chat")}{fila("WhatsApp", "310 789 7960")}</div>
  <div><h4>EL CLOSER</h4>{fila("Nombre", A.nombre)}{fila("C.C.", A.cc)}{fila("Ciudad / zona", A.ciudad)}{fila("Código de closer", A.codigo)}{fila("Correo", A.correo)}{fila("WhatsApp", A.whatsapp)}</div>
</div>
<p class="intro">Entre los suscritos, de una parte, <b>JUAN FELIPE MERCHÁN HENAO</b>, mayor de edad, identificado como aparece en el cuadro de datos, domiciliado en Tuluá (Valle del Cauca), quien obra en nombre propio y como titular de la marca comercial <b>APEX CORPORATION</b>, en adelante «APEX»; y de otra parte, la persona identificada como closer en el cuadro de datos, en adelante «EL CLOSER», se celebra el presente contrato de prestación de servicios comerciales, que se rige por las siguientes cláusulas:</p>
{cuerpo}
<p class="cierre">En constancia, las partes firman el presente contrato, junto con sus anexos, en la fecha de inicio indicada. EL CLOSER declara que lo leyó, lo entendió y lo acepta en su totalidad.</p>
<div class="firmas">
  <div><div class="raya"></div><h5>EL CLOSER</h5>Nombre: {escape(A.nombre) if A.nombre else ""}<br>C.C.: {escape(A.cc) if A.cc else ""}<br>Fecha:</div>
  <div><div class="raya"></div><h5>APEX CORPORATION</h5>Nombre: Juan Felipe Merchán Henao<br>C.C.: {escape(A.cc_apex) if A.cc_apex else ""}<br>Fecha:</div>
</div>
<div class="anexo">
  <div class="cap" style="margin-top:0"><small>ANEXO 1</small><h2>Formato de reporte semanal de llamadas</h2></div>
  <div class="linea"><span>Closer: {campo(A.nombre)}</span><span>Código: {campo(A.codigo)}</span><span>Semana: del <span class="l" style="width:22%"></span> al <span class="l" style="width:22%"></span></span></div>
  <table><tr><th style="width:4%">N.º</th><th style="width:9%">Fecha</th><th style="width:21%">Restaurante y ciudad</th><th style="width:17%">Contacto y cargo</th><th style="width:12%">Teléfono</th><th style="width:12%">Estado</th><th>Observaciones y próximo paso</th></tr>{filas_reporte}</table>
  <p class="nota"><b>I</b> = Interesado · <b>NI</b> = No interesado. Mínimo cinco (5) llamadas efectivas por semana. Envío: cada domingo antes de las 8:00 p. m., por WhatsApp o a apexcorporation@axtra.chat.</p>
  <div class="resumen"><div>Llamadas efectivas<b></b></div><div>Interesados<b></b></div><div>Reuniones agendadas<b></b></div><div>Ventas cerradas<b></b></div></div>
  <div class="cap" style="margin-top:22px"><small>ANEXO 2</small><h2>Tabla de comisiones</h2></div>
  <table class="com"><tr><th style="width:34%">Producto y plan</th><th>Valor de instalación</th><th>Anticipo para iniciar · 50&nbsp;%</th><th>Comisión del closer</th></tr>{filas_com}</table>
  <p class="nota">Valores de referencia según la tarifa vigente. En Apex Play la comisión es el 35&nbsp;% del valor de instalación efectivamente pagado. La comisión se paga completa, en un solo pago, entre 8 y 15 días después de que el cliente pague el 100&nbsp;% de la instalación. Las mensualidades no generan comisión.</p>
</div>
</body></html>"""

PIE = ('<div style="width:100%;font-family:Arial,Helvetica,sans-serif;font-size:7px;color:#7a8698;padding:0 17mm;display:flex;justify-content:space-between;align-items:center">'
       '<span style="letter-spacing:.2em;color:#a8823f;font-weight:700">APEX CORPORATION</span><span>Contrato de prestación de servicios comerciales · Closer de ventas</span>'
       '<span>Iniciales: ______ / ______ &nbsp;·&nbsp; Página <span class="pageNumber"></span> de <span class="totalPages"></span></span></div>')

async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path=CHROME); pg = await br.new_page()
        await pg.set_content(HTML); await pg.wait_for_timeout(600)
        await pg.pdf(path=A.salida, format="Letter", print_background=True, display_header_footer=True, header_template="<div></div>", footer_template=PIE,
                     margin={"top": "15mm", "bottom": "18mm", "left": "17mm", "right": "17mm"})
        await br.close()
asyncio.run(main()); print("listo", A.salida)
