"""Graba el demo real de Apex Play (celular) y la caja. Guarda marcas de tiempo de cada escena."""
import asyncio, json, time, os, glob, shutil
from playwright.async_api import async_playwright
V = os.path.dirname(os.path.abspath(__file__)) + "/"
S = os.path.dirname(V.rstrip("/")) + "/"
DUR = json.load(open(V + "voz_play/duraciones.json"))
OUT = V + "crudo_play/"; shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
PAD = 0.7
marcas = {}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
                                    args=["--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream", "--autoplay-policy=no-user-gesture-required", "--enable-unsafe-swiftshader", "--use-gl=swiftshader"])
        ctx = await b.new_context(viewport={"width": 560, "height": 1204}, device_scale_factor=1, is_mobile=True, has_touch=True, locale="es-CO",
                                  record_video_dir=OUT, record_video_size={"width": 560, "height": 1204})
        await ctx.route("**/cdn.jsdelivr.net/**", lambda r: r.fulfill(path=S + "mv/package/dist/model-viewer.min.js", content_type="text/javascript"))
        # Caja primero, en una tablet (para que el pedido llegue en vivo). La mesa 4 la abre el mesero.
        ctx2 = await b.new_context(viewport={"width": 960, "height": 667}, device_scale_factor=1, locale="es-CO",
                                   record_video_dir=OUT + "caja/", record_video_size={"width": 960, "height": 667})
        caja = await ctx2.new_page(); t_caja = time.monotonic()
        await caja.goto("http://localhost:8081/panel?r=video"); await caja.fill("#pin", "4321"); await caja.click("#entrar"); await caja.wait_for_timeout(1500)
        await caja.click('[data-m="4"]'); await caja.wait_for_timeout(1000)
        # Precarga del visor 3D (para que la torta aparezca de una vez en la grabación)
        tibia = await ctx.new_page(); await tibia.goto("http://localhost:8081/demo?r=video&mesa=9"); await tibia.wait_for_timeout(800)
        await tibia.click("#entrar", force=True); await tibia.wait_for_timeout(800); await tibia.click("[data-3d]"); await tibia.wait_for_timeout(9000); await tibia.close()
        pg = await ctx.new_page(); t0 = time.monotonic()
        rel = lambda: round(time.monotonic() - t0, 2)
        async def escena(k, acciones):
            marcas[k] = rel()
            await acciones()
            falta = DUR[k] + PAD - (rel() - marcas[k])
            if falta > 0: await pg.wait_for_timeout(int(falta * 1000))
        await pg.goto("http://localhost:8081/demo?r=video&mesa=4"); await pg.wait_for_timeout(1500)
        async def qr():
            await pg.wait_for_timeout(int((DUR["qr"] - 1.0) * 1000)); await pg.click("#entrar", force=True)
        async def carta():
            await pg.wait_for_timeout(2500); await pg.mouse.wheel(0, 260); await pg.wait_for_timeout(1600); await pg.mouse.wheel(0, -260)
        async def pedir():
            await pg.wait_for_timeout(300)
            await pg.click("[data-mas=bandeja]"); await pg.wait_for_timeout(1400)
            await pg.evaluate("document.querySelector('[data-mas=limonada]').scrollIntoView({behavior:'smooth', block:'center'})"); await pg.wait_for_timeout(1200)
            await pg.click("[data-mas=limonada]")
        async def tresd():
            await pg.evaluate("document.querySelector('[data-3d]').scrollIntoView({behavior:'smooth', block:'center'})"); await pg.wait_for_timeout(1100)
            await pg.click("[data-3d]"); await pg.wait_for_timeout(5600)     # el visor 3D tarda en pintar la torta
            marcas["tresd"] = rel() - 0.4
        async def oferta():
            await pg.click("#ar-cerrar"); await pg.wait_for_timeout(500)
            await pg.click("#ver-pedido"); await pg.wait_for_timeout(1300)
            await pg.click("#confirmar"); await pg.wait_for_timeout(int((DUR["oferta"] - 2.4) * 1000))
            marcas["envio"] = rel(); marcas["envio_caja"] = round(time.monotonic() - t_caja, 2)
            await pg.click("#oferta-si")
        await escena("qr", qr); await escena("carta", carta); await escena("pedir", pedir); await escena("tresd", tresd); await escena("oferta", oferta)
        marcas["enviado"] = rel(); await pg.wait_for_timeout(int((DUR["caja"] + PAD) * 1000))   # la caja se monta aparte
        async def idiomas():
            await pg.click("#otra-vez"); await pg.wait_for_timeout(1500)
            await pg.click("#idiomas-carta button:nth-child(2)"); await pg.wait_for_timeout(1500)
        await escena("idiomas", idiomas)
        marcas["fin"] = rel(); marcas["caja_offset"] = round(t0 - t_caja, 2)
        vid_pg, vid_caja = pg.video, caja.video
        await caja.wait_for_timeout(500); await ctx.close(); await ctx2.close(); await b.close()
        os.rename(await vid_pg.path(), OUT + "cliente.webm"); os.rename(await vid_caja.path(), OUT + "caja.webm")
        json.dump(marcas, open(OUT + "marcas.json", "w"), indent=1); print(marcas)
asyncio.run(main())
