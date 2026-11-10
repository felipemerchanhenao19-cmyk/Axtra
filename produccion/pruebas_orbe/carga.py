"""Simulador de carga de Apex Play: muchas personas pidiendo a la vez, sin gastar cupo de Groq.

Levanta el servidor de Apex de verdad (uvicorn, como en producción: un proceso) y una ranura de Axtra falsa
que tarda lo que tarda la real (oír 0,3 s · pensar 0,6 s por vuelta · voz 1,2 s). Opcional: --cupo_tokens_min
imita el límite por minuto del cerebro (Groq gratis ≈ 8.000 tokens/min por modelo) para ver dónde se cae.

Uso: python carga.py --personas 200 --mesas 50 --turnos 4 --llegada 60 [--hilos 6] [--cupo_tokens_min 8000]
"""
import argparse, asyncio, io, json, os, random, socket, statistics as st, subprocess, sys, tempfile, threading, time, wave
from collections import Counter, deque

import httpx

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ORIGEN = {"Origin": "https://api.axtra.chat"}


def libre() -> int:
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def ranura_falsa(puerto: int, lat: dict, cupo: int):
    """La ranura de Axtra con tiempos reales y, si se pide, un límite de tokens por minuto como el de Groq."""
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse, Response
    import uvicorn
    app, gasto, candado = FastAPI(), deque(), threading.Lock()

    @app.post("/oido")
    def oido():
        time.sleep(random.uniform(.8, 1.3) * lat["oido"])
        return {"texto": random.choice(["quiero un ajiaco", "dos limonadas de coco", "una bandeja paisa por favor"]), "segundos": 2.5, "proveedor": "groq"}

    @app.post("/pensar")
    async def pensar(request: Request):
        p = await request.json()
        tokens = (len(p["sistema"]) + len(json.dumps(p["mensajes"], ensure_ascii=False))) // 3 + 150
        if cupo:
            with candado:
                ahora = time.time()
                while gasto and ahora - gasto[0][0] > 60: gasto.popleft()
                if sum(t for _, t in gasto) + tokens > cupo:
                    return JSONResponse({"detail": "ningún cerebro respondió (429 límite por minuto)"}, 502)
                gasto.append((ahora, tokens))
        await asyncio.sleep(random.uniform(.7, 1.5) * lat["pensar"])
        ya = any(m.get("role") == "tool" for m in p["mensajes"][-3:])
        if not ya and p["mensajes"][-1].get("role") == "user":
            plato = random.choice(["ajiaco", "limonada", "bandeja"])
            return {"mensaje": {"role": "assistant", "content": "", "tool_calls": [{"id": "1", "type": "function", "function": {
                "name": "agregar_plato", "arguments": json.dumps({"plato_id": plato, "cantidad": 1})}}]},
                "uso": {"entrada": tokens, "salida": 30}, "proveedor": "groq"}
        return {"mensaje": {"role": "assistant", "content": "Listo, quedó en su pedido. ¿Algo más?", "tool_calls": []},
                "uso": {"entrada": tokens, "salida": 20}, "proveedor": "groq"}

    @app.post("/voz")
    def voz_():
        time.sleep(random.uniform(.7, 1.4) * lat["voz"])
        return Response(b"ID3" + os.urandom(18000), media_type="audio/mpeg", headers={"X-Proveedor": "edge", "X-Caracteres": "40"})

    @app.post("/pin")
    def pin():
        return {"ok": True}

    uvicorn.run(app, host="127.0.0.1", port=puerto, log_level="error")


def wav_corto() -> bytes:
    b = io.BytesIO(); w = wave.open(b, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
    w.writeframes(os.urandom(16000 * 2 * 2)); w.close(); return b.getvalue()


async def persona(cl: httpx.AsyncClient, k: int, o, audio: bytes, filas: list, t0: float):
    await asyncio.sleep(random.uniform(0, o.llegada))
    cab = {**ORIGEN, "cf-connecting-ip": f"10.0.{k // 250}.{k % 250}"}      # cada persona con su celular
    try:
        r = await cl.post("/v1/sesion", json={"restaurante": "demo", "mesa": str(1 + k % o.mesas)}, headers=cab)
        s = r.json() if r.status_code == 200 else None
    except httpx.HTTPError as e:
        filas.append({"tipo": "sesion", "codigo": type(e).__name__, "s": 0, "t": time.time() - t0}); return
    if not s:
        filas.append({"tipo": "sesion", "codigo": r.status_code, "s": 0, "t": time.time() - t0}); return
    for _ in range(o.turnos):
        a = time.time()
        try:
            r = await cl.post("/v1/turno", content=audio, headers={**cab, "Content-Type": "audio/wav", "X-Apex-Sesion": s["sesion"],
                                                                   "X-Apex-Secreto": s["secreto"]})
            d = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
            codigo = "sin_voz" if d.get("sin_voz") else r.status_code
        except httpx.HTTPError as e:
            codigo = type(e).__name__
        filas.append({"tipo": "turno", "codigo": codigo, "s": time.time() - a, "t": time.time() - t0})
        await asyncio.sleep(random.uniform(*o.pausa))                 # la persona mira la carta y vuelve a hablar


def p(v, q): v = sorted(v); return v[min(len(v) - 1, int(q * len(v)))] if v else 0


async def correr(o, base: str):
    audio, filas, t0 = wav_corto(), [], time.time()
    async with httpx.AsyncClient(base_url=base, timeout=60, limits=httpx.Limits(max_connections=1000)) as cl:
        await asyncio.gather(*(persona(cl, k, o, audio, filas, t0) for k in range(o.personas)))
    dur = time.time() - t0
    turnos = [f for f in filas if f["tipo"] == "turno"]; buenos = [f["s"] for f in turnos if f["codigo"] == 200]
    print(f"\n{o.personas} personas en {o.mesas} mesas · {o.turnos} turnos c/u · llegan en {o.llegada:.0f} s · hilos {o.hilos or 'por defecto'}"
          f" · cupo cerebro {o.cupo_tokens_min or 'sin límite'} tokens/min")
    print(f"  duración {dur:.0f} s · turnos {len(turnos)} ({len(turnos) / dur:.1f}/s) · resultado {dict(Counter(str(f['codigo']) for f in filas))}")
    if buenos:
        print(f"  tiempo de respuesta (servidor + ranura): mediana {st.median(buenos):.2f} s · p90 {p(buenos, .9):.2f} s · p99 {p(buenos, .99):.2f} s · máx {max(buenos):.2f} s")
    return {"personas": o.personas, "hilos": o.hilos, "cupo": o.cupo_tokens_min, "turnos": len(turnos), "ok": len(buenos),
            "mediana": st.median(buenos) if buenos else None, "p90": p(buenos, .9), "codigos": dict(Counter(str(f["codigo"]) for f in filas))}


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--personas", type=int, default=200); a.add_argument("--mesas", type=int, default=50)
    a.add_argument("--turnos", type=int, default=4); a.add_argument("--llegada", type=float, default=60)
    a.add_argument("--pausa", type=float, nargs=2, default=[8, 20]); a.add_argument("--hilos", type=int, default=0)
    a.add_argument("--cupo_tokens_min", type=int, default=0); a.add_argument("--salida", default="")
    o = a.parse_args()
    pr, pa = libre(), libre()
    threading.Thread(target=ranura_falsa, args=(pr, {"oido": .3, "pensar": .6, "voz": 1.2}, o.cupo_tokens_min), daemon=True).start()
    datos = tempfile.mkdtemp(prefix="apex-carga-")
    env = {**os.environ, "APEX_DATOS": datos, "RANURA_URL": f"http://127.0.0.1:{pr}", "PYTHONPATH": RAIZ,
           **({"APEX_HILOS": str(o.hilos)} if o.hilos else {})}
    srv = subprocess.Popen([sys.executable, "-m", "uvicorn", "servidor.apex.app:app", "--host", "127.0.0.1", "--port", str(pa), "--log-level", "error"],
                           cwd=RAIZ, env=env)
    try:
        for _ in range(100):
            try:
                if httpx.get(f"http://127.0.0.1:{pa}/v1/menu/demo", timeout=2).status_code == 200: break
            except httpx.HTTPError: pass
            time.sleep(.2)
        res = asyncio.run(correr(o, f"http://127.0.0.1:{pa}"))
        if o.salida:
            with open(o.salida, "a") as f: f.write(json.dumps(res, ensure_ascii=False) + "\n")
    finally:
        srv.terminate()


if __name__ == "__main__":
    main()
