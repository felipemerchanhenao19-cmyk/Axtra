"""Graba el demo real de Apex Domicilios (celular) y la caja (tablet)."""
import asyncio, json, time, os, shutil
from playwright.async_api import async_playwright
V = os.path.dirname(os.path.abspath(__file__)) + "/"
S = os.path.dirname(V.rstrip("/")) + "/"
DUR = json.load(open(V + "voz_domicilios/duraciones.json"))
OUT = V + "crudo_domicilios/"; shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
PAD = 0.7; R = "videodom"
marcas = {}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
                                    args=["--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream", "--autoplay-policy=no-user-gesture-required", "--enable-unsafe-swiftshader", "--use-gl=swiftshader"])
        ctx = await b.new_context(viewport={"width": 560, "height": 1204}, device_scale_factor=1, is_mobile=True, has_touch=True, locale="es-CO",
                                  record_video_dir=OUT, record_video_size={"width": 560, "height": 1204})
        await ctx.route("**/cdn.jsdelivr.net/**", lambda r: r.fulfill(path=S + "mv/package/dist/model-viewer.min.js", content_type="text/javascript"))
        ctx2 = await b.new_context(viewport={"width": 960, "height": 667}, device_scale_factor=1, locale="es-CO",
                                   record_video_dir=OUT + "caja/", record_video_size={"width": 960, "height": 667})
        caja = await ctx2.new_page(); t_caja = time.monotonic()
        await caja.goto(f"http://localhost:8081/panel?r={R}"); await caja.fill("#pin", "4321"); await caja.click("#entrar"); await caja.wait_for_timeout(1500)
        pg = await ctx.new_page(); t0 = time.monotonic()
        rel = lambda: round(time.monotonic() - t0, 2)
        async def escena(k, acciones):
            ini = time.monotonic(); marcas[k] = rel()
            await acciones()
            falta = DUR[k] + PAD - (time.monotonic() - ini)
            if falta > 0: await pg.wait_for_timeout(int(falta * 1000))
        await pg.goto(f"http://localhost:8081/domicilios?r={R}"); await pg.wait_for_timeout(1500)
        async def link():
            await pg.wait_for_timeout(int((DUR["link"] - 0.8) * 1000)); await pg.click("#entrar", force=True)
        async def carta():
            await pg.wait_for_timeout(1200); await pg.click("[data-mas=bandeja]"); await pg.wait_for_timeout(1500)
            await pg.evaluate("document.querySelector('[data-mas=limonada]').scrollIntoView({behavior:'smooth', block:'center'})"); await pg.wait_for_timeout(1000)
            await pg.click("[data-mas=limonada]")
        async def oferta():
            await pg.wait_for_timeout(300); await pg.click("#ver-pedido"); await pg.wait_for_timeout(1300); await pg.click("#continuar")
        async def datos():
            await pg.click("#oferta-no"); await pg.wait_for_timeout(900)
            await pg.type("#f-nombre", "Ana Pérez", delay=45); await pg.type("#f-tel", "300 123 4567", delay=40)
            await pg.type("#f-dir", "Calle 10 # 20-30", delay=40); await pg.type("#f-barrio", "Centro", delay=45)
            await pg.select_option("#f-zona", "z2"); await pg.check("input[value=contra_entrega]"); await pg.check("#f-acepto")
            await pg.evaluate("document.querySelector('#hacer-pedido').scrollIntoView({behavior:'smooth', block:'center'})")
        async def recibido():
            marcas["envio_caja"] = round(time.monotonic() - t_caja, 2); await pg.click("#hacer-pedido")
        await escena("link", link); await escena("carta", carta); await escena("oferta", oferta); await escena("datos", datos); await escena("recibido", recibido)
        # Caja: el pedido suena y el cajero cambia el estado (tiempos medidos desde el envío)
        desde = marcas["envio_caja"] + 0.4; marcas["caja_desde"] = desde
        async def hasta(seg):
            falta = desde + seg - (time.monotonic() - t_caja)
            if falta > 0: await caja.wait_for_timeout(int(falta * 1000))
        await hasta(DUR["caja"] * 0.6); await caja.select_option("select[data-p]", "preparando")
        await hasta(DUR["caja"] * 0.8); await caja.select_option("select[data-p]", "en_camino")
        await hasta(DUR["caja"] + PAD)
        async def seguimiento():
            await pg.evaluate("document.querySelector('#pasos-dom').scrollIntoView({behavior:'smooth', block:'center'})"); await pg.wait_for_timeout(700)
            await pg.evaluate("revisar()")
        await escena("seguimiento", seguimiento)
        marcas["fin"] = rel()
        vp, vc = pg.video, caja.video
        await ctx.close(); await ctx2.close(); await b.close()
        os.rename(await vp.path(), OUT + "cliente.webm"); os.rename(await vc.path(), OUT + "caja.webm")
        json.dump(marcas, open(OUT + "marcas.json", "w"), indent=1); print(marcas)
asyncio.run(main())
