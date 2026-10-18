"""Renderiza las fotos de perfil (1080x1080 PNG) y una hoja de vista previa: python hacer.py <carpeta_salida>"""
import sys, os, asyncio
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"; SAL = os.path.abspath(sys.argv[1]) + "/"; os.makedirs(SAL, exist_ok=True)
NOMBRES = {"tejido": "1-Anillo-tejido", "tallado": "2-Planeta-tallado", "monolinea": "3-Monolinea", "cometa": "4-Cometa"}
JS = open(AQUI + "logos.js").read()
async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        br = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome")
        for f, n in NOMBRES.items():
            pg = await br.new_page(viewport={"width": 1080, "height": 1080}); pg.on("pageerror", lambda e: print("ERR", e))
            await pg.set_content(f'<html><body style="margin:0;background:#000"><div id="x" style="width:1080px;height:1080px"></div><script>{JS}; document.getElementById("x").innerHTML = {f}().replace("<svg ", \'<svg width="1080" height="1080" \');</script></body></html>')
            await pg.screenshot(path=SAL + f"Apex-perfil-{n}.png"); await pg.close()
        # vista previa: como se ve en Instagram (círculo grande y chiquito)
        cel = "".join(f'''<div class="c"><img src="file://{SAL}Apex-perfil-{n}.png" class="g"><div class="fila"><img src="file://{SAL}Apex-perfil-{n}.png" class="p"><div><b>apex.corporation</b><span>Opción {n.split("-")[0]} · {" ".join(n.split("-")[1:])}</span></div></div></div>''' for n in NOMBRES.values())
        pg2 = await br.new_page(viewport={"width": 1600, "height": 560})
        await pg2.goto("file://" + SAL)  # para permitir file:// en las imágenes
        await pg2.set_content(f'''<html><body style="margin:0;background:#fafafa;font-family:sans-serif;display:flex;gap:30px;padding:30px;box-sizing:border-box">
          <style>.c{{flex:1;display:flex;flex-direction:column;align-items:center;gap:22px}} .g{{width:340px;height:340px;border-radius:50%}} .fila{{display:flex;gap:12px;align-items:center;background:#fff;padding:12px 16px;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.1);width:340px;box-sizing:border-box}}
          .p{{width:56px;height:56px;border-radius:50%}} b{{display:block;font-size:16px}} span{{font-size:14px;color:#777}}</style>{cel}</body></html>''')
        await pg2.wait_for_timeout(500); await pg2.screenshot(path=SAL + "vista-previa.png")
        await br.close()
asyncio.run(main()); print("listo")
