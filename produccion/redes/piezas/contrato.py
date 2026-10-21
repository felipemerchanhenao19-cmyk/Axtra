"""Acuerdo de confidencialidad y compromiso de asesor comercial independiente (PDF). python contrato.py <salida.pdf>"""
import sys, os, asyncio
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
FUENTES = open(AQUI + "../../videos/fuentes.html").read() + open(AQUI + "../expediente/fuentes_noir.html").read()
L = lambda n="": f'<span class="l" style="min-width:{n or 200}px"></span>'
CL = [
 ("Objeto", "El ASESOR se compromete a promover, de manera independiente, los productos de APEX CORPORATION (Apex Play y Apex Domicilios) ante restaurantes, y a guardar reserva sobre la información que reciba con ocasión de esta labor."),
 ("Información confidencial", "Es toda información no pública a la que el ASESOR acceda, entre otras: precios internos y condiciones comerciales; listas y datos de clientes y prospectos; funcionamiento interno de los productos; demostraciones no públicas; material de capacitación, guiones y estrategias de venta; y cualquier información que APEX CORPORATION señale como reservada."),
 ("Obligaciones del asesor", "El ASESOR se obliga a: (a) usar la información confidencial únicamente para promover los productos de APEX CORPORATION; (b) no revelarla, copiarla ni compartirla con terceros sin autorización escrita; (c) no intentar acceder al código, los servidores ni los sistemas internos de APEX CORPORATION; (d) no copiar ni reproducir los productos, ni ayudar a un tercero a hacerlo; (e) devolver o eliminar el material cuando termine el vínculo."),
 ("Excepciones", "No se considera confidencial la información que sea de dominio público sin culpa del ASESOR, que el ASESOR ya conociera legítimamente antes de recibirla, o que deba revelarse por orden de autoridad competente, caso en el cual se avisará previamente a APEX CORPORATION."),
 ("Clientes y no desvío", "Los restaurantes presentados por el ASESOR a través de su código quedan registrados a su nombre. Durante la vigencia del vínculo y por doce (12) meses después, el ASESOR no ofrecerá a esos restaurantes productos competidores de los de APEX CORPORATION ni los desviará a otra empresa del mismo tipo de servicio."),
 ("Propiedad intelectual", "Las marcas, nombres, logotipos, personajes (incluido «Orbi»), imágenes, videos, software y material de venta son de propiedad exclusiva de APEX CORPORATION. El ASESOR solo puede usarlos para la promoción autorizada, sin modificarlos."),
 ("Naturaleza independiente", "El vínculo es de prestación de servicios independiente y de naturaleza comercial. No genera relación laboral, subordinación, horario, salario ni prestaciones. El ASESOR organiza su tiempo y asume sus propios gastos, y es responsable de sus obligaciones tributarias y de seguridad social."),
 ("Comisiones", "Apex Domicilios: $100.000 por restaurante vendido. Apex Play: 20 % del valor de la instalación. Mientras el ASESOR esté en etapa junior, recibe el 50 % de esas comisiones hasta completar tres (3) ventas cerradas; desde la cuarta vende solo y recibe la comisión completa. La comisión se causa y se paga únicamente cuando el restaurante haya pagado a APEX CORPORATION. Todo pago del restaurante se hace directamente a las cuentas de APEX CORPORATION, nunca al ASESOR. Si el restaurante cancela o se le devuelve el dinero dentro de los treinta (30) días siguientes al pago, la comisión se descuenta de pagos futuros."),
 ("Datos personales", "El ASESOR tratará los datos de restaurantes y personas conforme a la Ley 1581 de 2012 y solo para los fines de este acuerdo. El ASESOR autoriza a APEX CORPORATION a tratar sus datos personales para la gestión del vínculo y el pago de comisiones."),
 ("Duración y terminación", "El acuerdo rige desde su aceptación y hasta que cualquiera de las partes lo termine con aviso por escrito (incluido WhatsApp). Las obligaciones de confidencialidad se mantienen durante tres (3) años después de terminado el vínculo."),
 ("Incumplimiento", "El incumplimiento de las cláusulas de confidencialidad o de no desvío obliga al ASESOR a pagar a APEX CORPORATION una cláusula penal de DOS MILLONES DE PESOS ($2.000.000), sin perjuicio de la indemnización de los perjuicios mayores que se demuestren y de las acciones legales que correspondan."),
 ("Ley aplicable y aceptación", "Este acuerdo se rige por las leyes de la República de Colombia. Las partes aceptan que su firma pueda hacerse por medios electrónicos, incluidos WhatsApp o correo, conforme a la Ley 527 de 1999."),
]
cl = "".join(f'<div class="c"><b>CLÁUSULA {i + 1}. {t.upper()}.</b> {x}</div>' for i, (t, x) in enumerate(CL))
HTML = f'''<!doctype html><html><head><meta charset="utf-8">{FUENTES}<style>
@page {{ size: Letter; margin: 22mm 20mm; }}
* {{ box-sizing: border-box; }} body {{ font: 11.5pt/1.5 "Figtree", sans-serif; color: #0b1f3a; margin: 0; }}
h1 {{ font: italic 700 22pt/1.15 "Playfair Display", Georgia, serif; text-align: center; margin: 0 0 4px; }}
.sub {{ text-align: center; letter-spacing: .25em; font-size: 9pt; color: #5a6b82; font-weight: 700; margin-bottom: 14px; }}
.reg {{ border-top: 2px solid #0b1f3a; border-bottom: 1px solid #0b1f3a; padding: 8px 0; margin-bottom: 14px; text-align: center; font-size: 9.5pt; letter-spacing: .12em; color: #34465e; }}
.c {{ margin: 0 0 9px; text-align: justify; }} .c b {{ color: #0b1f3a; }}
p {{ margin: 0 0 9px; text-align: justify; }}
.l {{ display: inline-block; border-bottom: 1px solid #0b1f3a; height: 1em; margin: 0 4px; }}
.firmas {{ display: grid; grid-template-columns: 1fr 1fr; gap: 36px; margin-top: 30px; break-inside: avoid; }}
.firmas div {{ border-top: 1px solid #0b1f3a; padding-top: 6px; font-size: 10pt; line-height: 1.6; }}
</style></head><body>
<h1>Acuerdo de confidencialidad<br>y compromiso de asesor comercial</h1>
<div class="sub">APEX CORPORATION · SOFTWARE E INTELIGENCIA ARTIFICIAL</div>
<div class="reg">ASESOR: {L(190)} &nbsp; C.C.: {L(120)} &nbsp; CIUDAD / ZONA: {L(110)} &nbsp; CÓDIGO: {L(90)}</div>
<p>Entre <b>APEX CORPORATION</b>, en adelante APEX CORPORATION, y la persona identificada arriba, en adelante el ASESOR, se celebra este acuerdo, que se rige por las siguientes cláusulas:</p>
{cl}
<p style="margin-top:14px">Para constancia, el ASESOR declara que leyó y entendió este acuerdo, y lo acepta firmándolo o respondiendo «ACEPTO» al mensaje por el cual se le envió, en la fecha indicada.</p>
<div class="firmas"><div><b>EL ASESOR</b><br>Nombre: {L(150)}<br>C.C.: {L(150)}<br>Fecha: {L(150)}</div><div><b>APEX CORPORATION</b><br>Nombre: {L(150)}<br>Cargo: {L(150)}<br>Fecha: {L(150)}</div></div>
</body></html>'''
async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome"); pg = await br.new_page()
        await pg.set_content(HTML); await pg.wait_for_timeout(500); await pg.pdf(path=sys.argv[1], format="Letter", print_background=True, prefer_css_page_size=True); await br.close()
asyncio.run(main()); print("listo")
