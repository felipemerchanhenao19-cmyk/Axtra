"""Cuadros clave (storyboard) de «Viernes, 8 p. m.»: python guion_board.py <salida_dir>"""
import sys, os, asyncio
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
OUT = os.path.abspath(sys.argv[1]) + "/"; os.makedirs(OUT, exist_ok=True)
FUENTES = open(AQUI + "../../videos/fuentes.html").read()
JS = open(AQUI + "../orbi.js").read() + open(AQUI + "personajes.js").read()
CSS = """<style>* { margin: 0; box-sizing: border-box; } body { width: 1080px; height: 1920px; overflow: hidden; font-family: "Figtree", sans-serif; background: #000; }
#s { position: absolute; inset: 0; } svg.full { position: absolute; inset: 0; width: 1080px; height: 1920px; }
.g { position: absolute; } .b { position: absolute; background: #fff; color: #14202f; font-weight: 800; font-size: 46px; padding: 18px 28px; border-radius: 30px; box-shadow: 0 10px 30px rgba(0,0,0,.4); white-space: nowrap; }
.b.o { background: #0b1626; color: #fff; border: 3px solid #2fbbe8; } .b.p { background: #fbf6e6; color: #4a3b2a; border: 3px solid #c9bd98; font-style: italic; }
.titulo { position: absolute; left: 0; right: 0; top: 140px; text-align: center; color: #fff; font-weight: 800; font-size: 74px; letter-spacing: .12em; text-shadow: 0 6px 30px rgba(0,0,0,.6); }
.chip { position: absolute; background: rgba(5,9,15,.85); color: #fff; font-weight: 800; font-size: 40px; padding: 14px 26px; border-radius: 20px; border: 3px solid #ff5c6e; }
.chip.ok { border-color: #2ee59d; }
.velo { position: absolute; inset: 0; background: radial-gradient(70% 50% at 50% 55%, rgba(0,0,0,0), rgba(0,0,0,.75)); }
.logo { position: absolute; left: 0; right: 0; bottom: 230px; text-align: center; color: #fff; } .logo b { font-size: 70px; font-weight: 800; } .logo div { font-size: 64px; font-weight: 800; margin-bottom: 24px; }
</style>"""
def S(x, y, esc, contenido): return f'<svg class="g" style="left:{x - 300 * esc}px;top:{y - 300 * esc}px;width:{600 * esc}px;height:{600 * esc}px" viewBox="-300 -300 600 600">{contenido}</svg>'
def orb(x, y, tam, expr): return f'<div class="g" style="left:{x - tam / 2}px;top:{y - tam / 2}px;width:{tam}px;height:{tam}px" data-orbi="{expr}"></div>'
P = lambda **k: "persona({" + ",".join(f'{a}:{repr(b) if isinstance(b, str) else b}' for a, b in k.items()) + "})"
def esc(cuerpo_js, html_extra, luz=1, velo=False):
    return f'''<!doctype html><html><head><meta charset="utf-8">{FUENTES}{CSS}</head><body><div id="s"></div>{html_extra}{'<div class="velo"></div>' if velo else ''}
    <script>{JS}
    const capas = {cuerpo_js};
    document.getElementById("s").innerHTML = `<svg class="full" viewBox="0 0 1080 1920">${{restaurante(0, {luz})}}${{capas}}</svg>`;
    document.querySelectorAll("[data-orbi]").forEach(d => d.innerHTML = orbi(d.dataset.orbi));
    document.querySelectorAll("[data-svg]").forEach(d => d.innerHTML = eval(d.dataset.svg));
    </script></body></html>'''
def g(x, y, s, js): return f'`<g transform="translate({x} {y}) scale({s})">${{{js}}}</g>`'
def suma(*partes): return " + ".join(partes)
CUADROS = {
 "1_calma": esc(suma(g(540, 1330, 1.25, "mesa(0,0)"), g(540, 1560, 1.4, "julian({bandeja:true, platos:0})")),
               '<div class="titulo">VIERNES · 8:00 P.M.</div>'),
 "2_avalancha": esc(suma(g(250, 1220, 0.75, P(piel="#f2c9a0", pelo="largo", colorPelo="#5a3a1a", camisa="#c0392b", brazo=1, boca=0.9, cejas="enojo")),
                         g(250, 1260, 0.8, "mesa(0,0)"),
                         g(830, 1200, 0.72, P(piel="#a8714a", pelo="corto", camisa="#2e8b57", brazo=1, boca=0.9)), g(830, 1240, 0.78, "mesa(0,0)"),
                         g(820, 1520, 0.8, P(piel="#f6d5b5", pelo="moño", colorPelo="#2b1d14", camisa="#8e44ad", brazo=1, boca=0.85, cejas="enojo")), g(820, 1570, 0.85, "mesa(0,0)"),
                         g(430, 1640, 1.25, "julian({sudor:true, ojos:'grandes', boca:'o', bandeja:true, platos:3, inclina:-14})")),
                    '<div class="b" style="left:70px;top:820px">¡Mesero!</div><div class="b" style="left:640px;top:800px">¡La carta!</div><div class="b" style="left:560px;top:1160px">¡Otra cerveza!</div><div class="chip" style="left:60px;top:150px">MESAS OCUPADAS: 12</div>'),
 "3_don_papel": esc(suma(g(780, 1220, 0.8, P(piel="#a8714a", pelo="calvo", camisa="#2e8b57", boca=0.9, cejas="enojo")), g(780, 1260, 0.85, "mesa(0,0)"),
                         g(360, 1620, 1.2, "julian({sudor:true, ojos:'grandes', boca:'triste'})"), g(250, 1060, 1.0, "donPapel({boca:0.8})")),
                    '<div class="b p" style="left:60px;top:600px;white-space:normal;width:560px">«Anótalo todo en mí, muchacho. Así se ha hecho toda la vida.»</div><div class="b" style="left:600px;top:870px">¡Yo pedí carne!</div><div class="chip" style="left:60px;top:150px">PEDIDOS PERDIDOS: 3</div>'),
 "4_derrota": esc(suma(g(540, 1330, 1.25, "mesa(0,0)"), g(540, 1600, 1.4, "julian({ojos:'cerrados', boca:'triste', sudor:true})")),
                  '<div class="b" style="left:290px;top:900px">Ya no puedo más…</div>', luz=0.35, velo=True),
 "5_aparece": esc(suma(g(540, 1420, 1.3, "mesa(0,0)"), g(840, 1650, 1.0, "julian({ojos:'grandes', boca:'o'})"), g(200, 1560, 0.85, "donPapel({cara:'enojo', boca:0.6})")),
                  orb(540, 1020, 520, "normal") + '<div class="b o" style="left:250px;top:560px">Buenas noches. ¿Me permite?</div><div class="b p" style="left:60px;top:1760px">¿Y este quién es?</div>', luz=0.6),
 "6_orbi_atiende": esc(suma(g(230, 1240, 0.75, P(piel="#f2c9a0", pelo="largo", colorPelo="#5a3a1a", camisa="#c0392b", boca=0.2)), g(230, 1280, 0.8, "mesa(0,0)"),
                            g(850, 1240, 0.75, P(piel="#a8714a", pelo="corto", camisa="#2e8b57", boca=0.15)), g(850, 1280, 0.8, "mesa(0,0)"),
                            g(540, 1640, 0.9, P(piel="#f6d5b5", pelo="moño", camisa="#8e44ad", boca=0.1)), g(540, 1690, 0.95, "mesa(0,0)")),
                       orb(540, 700, 400, "feliz") + '<div class="b o" style="left:300px;top:930px">¿Le traigo el postre?</div><div class="b" style="left:640px;top:1430px">¡Claro!</div><div class="chip ok" style="left:60px;top:150px">PEDIDOS PERDIDOS: 0</div>'),
 "7_final": esc(suma(g(780, 1600, 1.3, "julian({bandeja:true, platos:3})")),
                orb(330, 1250, 520, "guino") + '<div class="b" style="left:520px;top:1060px">¿De dónde saliste?</div><div class="b o" style="left:90px;top:860px">De la mesa siete.</div><div class="logo" style="bottom:120px"><b>Apex Play</b></div>'),
}
async def m():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
        for k, html in CUADROS.items():
            pg = await b.new_page(viewport={"width": 1080, "height": 1920}); pg.on("pageerror", lambda e: print("ERR", e))
            await pg.set_content(html); await pg.wait_for_timeout(300); await pg.screenshot(path=OUT + k + ".png"); await pg.close()
        await b.close()
asyncio.run(m())
