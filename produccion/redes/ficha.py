"""Ficha del personaje y foto de perfil: python ficha.py <salida_dir>"""
import sys, os, asyncio, json
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
OUT = os.path.abspath(sys.argv[1]) + "/"; os.makedirs(OUT, exist_ok=True)
FUENTES = open(AQUI + "../videos/fuentes.html").read()
JS = open(AQUI + "orbi.js").read()
EXP = [("normal", "A su servicio"), ("feliz", "Pedido enviado"), ("sarcastico", "¿27 %? Qué generosos"), ("sorprendido", "¿Otra ronda?"),
       ("triste", "La libreta perdió el pedido"), ("enojado", "Mesa 7, minuto 14"), ("guino", "¿Le traigo el postre?"), ("orgulloso", "40 mesas a la vez")]
FICHA = f'''<!doctype html><html><head><meta charset="utf-8">{FUENTES}<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ width: 1920px; height: 1080px; overflow: hidden; font-family: "Figtree", sans-serif; color: #f4f7fb;
  background: radial-gradient(60% 80% at 22% 50%, #17406f 0%, #0b1626 55%, #050a14 100%); }}
.izq {{ position: absolute; left: 70px; top: 70px; width: 640px; }}
.izq .heroe {{ width: 560px; height: 560px; margin-left: 20px; }}
.kicker {{ font-size: 22px; font-weight: 800; letter-spacing: .4em; color: #5fc9f1; }}
h1 {{ font-size: 130px; font-weight: 800; letter-spacing: -0.04em; line-height: 1; margin-top: 6px; }}
.lema {{ font-size: 32px; color: #9db0c5; margin-top: 10px; }}
.der {{ position: absolute; left: 760px; top: 70px; right: 70px; }}
.rasgos {{ display: grid; grid-template-columns: 1fr 1fr; gap: 14px 30px; margin-bottom: 36px; }}
.rasgos div {{ font-size: 21px; color: #c9d6e6; line-height: 1.4; }} .rasgos b {{ display: block; font-size: 15px; letter-spacing: .25em; text-transform: uppercase; color: #5fc9f1; margin-bottom: 2px; }}
.grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px; }}
.exp {{ background: rgba(255,255,255,.05); border: 1px solid rgba(160,220,255,.18); border-radius: 26px; padding: 10px 10px 14px; text-align: center; }}
.exp svg {{ width: 200px; height: 200px; }}
.exp b {{ display: block; font-size: 19px; text-transform: capitalize; }} .exp span {{ font-size: 15px; color: #8fa3ba; }}
.pie {{ position: absolute; left: 70px; bottom: 40px; font-size: 16px; letter-spacing: .3em; text-transform: uppercase; color: #5f7590; }}
</style></head><body>
<div class="izq"><div class="kicker">APEX CORPORATION PRESENTA</div><h1>Orbi</h1><div class="lema">El mesero virtual. Nunca descansa, nunca olvida un pedido.</div><div class="heroe" id="heroe"></div></div>
<div class="der">
 <div class="rasgos">
  <div><b>Personalidad</b>Elegante, rápido y un poco engreído. Sarcástico con las apps de domicilios y con la libreta de papel.</div>
  <div><b>Voz</b>Cálida, segura y con chispa. Habla de usted, como un mesero de restaurante fino.</div>
  <div><b>Frase</b>«¿Le traigo el postre?»</div>
  <div><b>Rasgos</b>El anillo es su bandeja; el corbatín, su uniforme. Brilla más cuando vende.</div>
 </div>
 <div class="grid" id="grid"></div>
</div>
<div class="pie">Personaje oficial · Apex Play · Apex Domicilios</div>
<script>{JS}
document.getElementById("heroe").innerHTML = orbi("normal");
document.getElementById("grid").innerHTML = {json.dumps(EXP, ensure_ascii=False)}.map(([k, t]) => `<div class="exp">${{orbi(k)}}<b>${{k === "guino" ? "Guiño" : k === "sarcastico" ? "Sarcástico" : k}}</b><span>${{t}}</span></div>`).join("");
</script></body></html>'''
PERFIL = f'''<!doctype html><html><head><meta charset="utf-8"><style>
* {{ margin: 0; }} body {{ width: 1080px; height: 1080px; overflow: hidden; background: radial-gradient(70% 70% at 50% 45%, #17406f 0%, #0b1626 60%, #050a14 100%);
  display: grid; place-items: center; }} #o {{ width: 900px; height: 900px; }}
</style></head><body><div id="o"></div><script>{JS} document.getElementById("o").innerHTML = orbi("guino");</script></body></html>'''
async def m():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
        for nombre, html, w, h in (("Orbi-ficha.png", FICHA, 1920, 1080), ("Orbi-perfil.png", PERFIL, 1080, 1080)):
            pg = await b.new_page(viewport={"width": w, "height": h}); pg.on("pageerror", lambda e: print("ERR", e))
            await pg.set_content(html); await pg.wait_for_timeout(600); await pg.screenshot(path=OUT + nombre); await pg.close()
        await b.close()
asyncio.run(m()); print("listo", OUT)
