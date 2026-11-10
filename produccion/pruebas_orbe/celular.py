"""Prueba de punta a punta del celular: Chromium con un micrófono falso que dice una frase, el servidor de Apex local
y una ranura falsa que guarda cuánto audio le llegó. Mide: ¿detecta el fin de la frase? ¿cuánto silencio sobra?"""
import asyncio, json, os, subprocess, sys, tempfile, threading, time, wave, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import carga, edge_tts, numpy as np
RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")); AQUI = os.getenv("PRUEBAS_CACHE", "/tmp/pruebas_orbe_celular"); os.makedirs(AQUI, exist_ok=True)
llegados = []

def ranura(puerto):
    from fastapi import FastAPI, Request
    from fastapi.responses import Response
    import uvicorn
    app = FastAPI()
    @app.post("/oido")
    async def oido(request: Request):
        b = await request.body(); w = wave.open(io.BytesIO(b)); n = w.getnframes(); hz = w.getframerate()
        x = np.frombuffer(w.readframes(n), np.int16).astype(float) / 32768
        voz = np.where(np.abs(x) > 0.02)[0]
        llegados.append({"t": time.time(), "dur": n / hz, "kb": len(b) / 1024, "silencio_final": (n - voz[-1]) / hz if len(voz) else None,
                         "silencio_inicial": voz[0] / hz if len(voz) else None})
        return {"texto": "quiero un ajiaco", "segundos": n / hz, "proveedor": "groq"}
    @app.post("/pensar")
    async def pensar(request: Request):
        return {"mensaje": {"role": "assistant", "content": "Claro, ¿algo más?", "tool_calls": []}, "uso": {}, "proveedor": "groq"}
    @app.post("/voz")
    def voz():
        return Response(open(os.path.join(AQUI, "silencio.mp3"), "rb").read(), media_type="audio/mpeg", headers={"X-Proveedor": "edge", "X-Caracteres": "5"})
    uvicorn.run(app, host="127.0.0.1", port=puerto, log_level="error")

async def preparar():
    f = os.path.join(AQUI, "frase.mp3")
    if not os.path.exists(f): await edge_tts.Communicate("Hola, quiero un ajiaco santafereño y una limonada de coco, por favor", "es-CO-SalomeNeural", proxy=os.getenv("HTTPS_PROXY")).save(f)
    # micrófono falso: 1,5 s de silencio, la frase, 4 s de silencio (Chromium repite el archivo)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-t", "1.5", "-i", "anullsrc=r=48000:cl=mono", "-i", f, "-f", "lavfi", "-t", "4", "-i", "anullsrc=r=48000:cl=mono",
                    "-filter_complex", "[1]aresample=48000,aformat=channel_layouts=mono[v];[0][v][2]concat=n=3:v=0:a=1", "-ar", "48000", "-ac", "1", os.path.join(AQUI, "mic.wav")], check=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-t", "0.3", "-i", "anullsrc=r=24000:cl=mono", os.path.join(AQUI, "silencio.mp3")], check=True)
    w = wave.open(os.path.join(AQUI, "mic.wav")); print("micrófono falso:", w.getnframes() / w.getframerate(), "s")

asyncio.run(preparar())
pr, pa = carga.libre(), 8081
threading.Thread(target=ranura, args=(pr,), daemon=True).start()
env = {**os.environ, "APEX_DATOS": tempfile.mkdtemp(), "RANURA_URL": f"http://127.0.0.1:{pr}", "PYTHONPATH": RAIZ, "APEX_MODO": "desarrollo"}
srv = subprocess.Popen([sys.executable, "-m", "uvicorn", "servidor.apex.app:app", "--host", "127.0.0.1", "--port", str(pa), "--log-level", "error"], cwd=RAIZ, env=env)
time.sleep(3)
from playwright.sync_api import sync_playwright
try:
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=os.getenv("CHROMIUM") or None, args=["--use-fake-ui-for-media-stream", "--use-fake-device-for-media-stream", f"--use-file-for-fake-audio-capture={AQUI}/mic.wav",
                                    "--autoplay-policy=no-user-gesture-required"])
        pg = b.new_page(); pg.context.grant_permissions(["microphone"])
        errores = []; pg.on("pageerror", lambda e: errores.append(str(e)))
        pg.goto(f"http://127.0.0.1:{pa}/demo?mesa=3"); pg.wait_for_timeout(1500)
        pg.on("console", lambda m: errores.append("consola: " + m.text))
        pg.evaluate("document.querySelector('#entrar').click()"); pg.wait_for_timeout(4000)
        for i in range(4):
            antes = len(llegados)
            pg.evaluate("document.querySelector('#orbe-arriba').click()")
            for _ in range(120):
                if len(llegados) > antes: break
                pg.wait_for_timeout(100)
            pg.wait_for_timeout(2500)
        print("errores de la página:", errores[:3])
        b.close()
finally:
    srv.terminate()
for l in llegados: print({k: round(v, 2) if isinstance(v, float) else v for k, v in l.items() if k != "t"})
