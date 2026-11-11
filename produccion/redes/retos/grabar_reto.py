"""Graba la pantalla REAL de api.axtra.chat/demo mientras el asistente real atiende. El «micrófono» recibe las frases del cliente
(audios preparados); todo lo demás —oído, cerebro, voz, pantalla— es el sistema en producción."""
import asyncio, base64, json, os, time, sys
from playwright.async_api import async_playwright
SAL = sys.argv[1]; os.makedirs(SAL + "/cuadros", exist_ok=True)
TURNOS = json.load(open(SAL + "/turnos.json"))
MIC = """
(() => { const C = new (window.AudioContext || window.webkitAudioContext)(); const dest = C.createMediaStreamDestination();
  const sil = C.createConstantSource(); sil.offset.value = 0; sil.connect(dest); sil.start();
  navigator.mediaDevices.getUserMedia = async () => { await C.resume(); return dest.stream; };
  window.__decir = async (b64) => { await C.resume(); const bin = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0)); const buf = await C.decodeAudioData(bin.buffer);
    const s = C.createBufferSource(); s.buffer = buf; s.connect(dest); s.start(); return buf.duration; }; })();
"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
                                    args=["--autoplay-policy=no-user-gesture-required", "--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        ctx = await b.new_context(viewport={"width": 560, "height": 1204}, device_scale_factor=1, is_mobile=True, has_touch=True, locale="es-CO")
        await ctx.add_init_script(MIC); pg = await ctx.new_page(); pg.on("pageerror", lambda e: print("ERR", e))
        t0 = time.monotonic(); rel = lambda: round(time.monotonic() - t0, 3); ev = []; n = [0]
        cdp = await ctx.new_cdp_session(pg)
        async def cuadro(d):
            open(f"{SAL}/cuadros/{n[0]:05d}.jpg", "wb").write(base64.b64decode(d["data"])); ev.append({"t": rel(), "cuadro": n[0]}); n[0] += 1
            await cdp.send("Page.screencastFrameAck", {"sessionId": d["sessionId"]})
        cdp.on("Page.screencastFrame", lambda d: asyncio.ensure_future(cuadro(d)))
        resp = []
        async def respuesta(r):
            if "/v1/turno" in r.url:
                try:
                    d = await r.json(); k = len(resp)
                    if d.get("audio"): open(f"{SAL}/orbi{k}.mp3", "wb").write(base64.b64decode(d["audio"]))
                    resp.append({"t": rel(), "k": k, "oido": d.get("oido"), "texto": d.get("texto"), "frase": d.get("frase"), "pedido": d.get("pedido"), "audio": bool(d.get("audio"))})
                    print("ORBI", k, d.get("texto"), "|", json.dumps(d.get("pedido"), ensure_ascii=False)[:160], flush=True)
                except Exception as e: print("resp?", e)
            if "/v1/frase/" in r.url:
                try: open(f"{SAL}/frase_{r.url.split('/v1/frase/')[1].split('?')[0].replace('/', '_')}.mp3", "wb").write(await r.body())
                except Exception: pass
        pg.on("response", lambda r: asyncio.ensure_future(respuesta(r)))
        await pg.goto("https://api.axtra.chat/demo"); await pg.wait_for_timeout(2500)
        await cdp.send("Page.startScreencast", {"format": "jpeg", "quality": 88, "everyNthFrame": 1})
        marcas = {"inicio": rel()}
        await pg.wait_for_timeout(1200); await pg.click("#entrar", force=True); marcas["entrar"] = rel()
        estado = lambda: pg.evaluate("orbe.estado")
        async def esperar(estados, tope=40):
            fin = time.monotonic() + tope
            while time.monotonic() < fin:
                e = await estado()
                if e in estados: return e
                await pg.wait_for_timeout(120)
            return await estado()
        await pg.wait_for_timeout(1500); print("estado tras entrar:", await esperar(["listo", "dormido", "escuchando"], 20), flush=True)
        linea = []
        for i, t in enumerate(TURNOS):
            await pg.wait_for_timeout(700)
            if await estado() != "escuchando": await pg.click("#orbe-arriba", force=True)
            await esperar(["escuchando"], 8); await pg.wait_for_timeout(450)
            d = await pg.evaluate("b => window.__decir(b)", base64.b64encode(open(f"{SAL}/c{i}.wav", "rb").read()).decode())
            ini = rel(); linea.append({"i": i, "txt": t, "ini": ini, "dur": d}); print("CLIENTE", i, ini, t, flush=True)
            await pg.wait_for_timeout(int(d * 1000) + 300)
            e = await esperar(["hablando"], 45); linea[-1]["habla"] = rel()
            e = await esperar(["listo", "dormido", "escuchando"], 45); linea[-1]["calla"] = rel(); print("  ->", e, linea[-1]["habla"], linea[-1]["calla"], flush=True)
        await pg.wait_for_timeout(3500); marcas["fin"] = rel()
        await cdp.send("Page.stopScreencast"); await pg.wait_for_timeout(300)
        json.dump({"marcas": marcas, "linea": linea, "respuestas": resp, "cuadros": ev}, open(SAL + "/registro.json", "w"), ensure_ascii=False, indent=1)
        await b.close()
asyncio.run(main())
