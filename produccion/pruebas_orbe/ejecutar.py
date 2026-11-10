"""Pruebas de voz del asistente de Apex Play contra el servidor publicado.
Genera la voz del cliente (edge-tts, varios acentos), la mezcla con ruido de restaurante, la envía a /v1/turno como lo
hace el celular y anota qué entendió, qué hizo con el pedido y cuánto tardó cada paso.
Uso: python ejecutar.py --restaurante demo --escenarios 40 --ritmo 7 --salida resultados.jsonl"""
import argparse, asyncio, io, json, os, random, re, subprocess, sys, time, unicodedata, wave
import numpy as np, requests, edge_tts

AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
from escenarios import E, VOCES

API = "https://api.axtra.chat"; ORIGEN = {"Origin": "https://api.axtra.chat"}
CA = "/root/.ccr/ca-bundle.crt" if os.path.exists("/root/.ccr/ca-bundle.crt") else True
PROXY = os.getenv("HTTPS_PROXY")
HZ = 16000


def norm(t): return "".join(c for c in unicodedata.normalize("NFD", (t or "").lower()) if unicodedata.category(c) != "Mn")


def wer(ref, hip):
    a, b = re.findall(r"\w+", norm(ref)), re.findall(r"\w+", norm(hip))
    if not a: return 0.0
    d = list(range(len(b) + 1))
    for i in range(1, len(a) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(b) + 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (a[i - 1] != b[j - 1]))
    return d[len(b)] / len(a)


async def tts(texto, voz, ritmo, f):
    for i in range(4):
        try: await edge_tts.Communicate(texto, voz, rate=ritmo, proxy=PROXY).save(f); return
        except Exception:
            await asyncio.sleep(2 * (i + 1))
    raise RuntimeError("tts")


def pcm(f):
    crudo = subprocess.check_output(["ffmpeg", "-v", "error", "-i", f, "-f", "s16le", "-ac", "1", "-ar", str(HZ), "-"])
    return np.frombuffer(crudo, dtype=np.int16).astype(np.float32) / 32768


CACHE = os.path.join(os.getenv("PRUEBAS_CACHE", "/tmp/claude-0/pruebas_orbe_cache")); os.makedirs(CACHE, exist_ok=True)


def voz_cliente(texto, voz, ritmo):
    f = os.path.join(CACHE, f"{abs(hash((texto, voz, ritmo))) % 10**12}.mp3")
    if not os.path.exists(f): asyncio.run(tts(texto, voz, ritmo, f))
    return pcm(f)


_BALBUCEO = None
def balbuceo(n):
    """Ruido de restaurante: varias conversaciones lejanas, platos y cubiertos."""
    global _BALBUCEO
    if _BALBUCEO is None:
        frases = [("Pásame la sal, por favor, que esto está delicioso", "es-CO-GonzaloNeural"), ("Did you see the game last night, it was crazy", "en-US-GuyNeural"),
                  ("Mesa cinco lista, sale el pedido", "es-MX-JorgeNeural"), ("On se retrouve demain matin à la plage", "fr-FR-HenriNeural"),
                  ("Y entonces le dije que no podía ir el sábado", "es-AR-ElenaNeural"), ("Quanto custa a cerveja aqui", "pt-BR-FranciscaNeural")]
        pistas = [voz_cliente(t, v, "+0%") for t, v in frases]
        largo = HZ * 30; b = np.zeros(largo, np.float32); rng = np.random.default_rng(3)
        for k in range(40):
            p = pistas[k % len(pistas)]; o = rng.integers(0, largo - len(p)); b[o:o + len(p)] += p * rng.uniform(0.3, 1.0)
        rosa = np.cumsum(rng.normal(0, 1, largo)).astype(np.float32); rosa -= np.convolve(rosa, np.ones(400) / 400, "same"); rosa /= np.abs(rosa).max()
        b += 0.15 * rosa
        for k in range(60):   # cubiertos y platos
            o = rng.integers(0, largo - 800); b[o:o + 800] += rng.normal(0, 1, 800) * np.exp(-np.arange(800) / 120) * rng.uniform(0.3, 1.2)
        _BALBUCEO = b / np.sqrt(np.mean(b ** 2))
    o = random.randint(0, len(_BALBUCEO) - n - 1); return _BALBUCEO[o:o + n]


def mezclar(voz, snr):
    voz = np.concatenate([np.zeros(int(HZ * 0.3), np.float32), voz, np.zeros(int(HZ * 0.4), np.float32)])
    if snr is not None:
        rv = np.sqrt(np.mean(voz[voz != 0] ** 2)); ruido = balbuceo(len(voz))
        voz = voz + ruido * rv / (10 ** (snr / 20))
    voz = voz / max(1.0, np.abs(voz).max() * 1.05)
    b = io.BytesIO(); w = wave.open(b, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(HZ)
    w.writeframes((voz * 32767).astype(np.int16).tobytes()); w.close(); return b.getvalue(), len(voz) / HZ


def evaluar(esp, r):
    fallas = []
    platos = {p["id"]: p["cantidad"] for p in (r.get("pedido") or {}).get("platos", [])}
    respuesta = norm(r.get("texto", ""))
    if "platos" in esp and platos != esp["platos"]: fallas.append(f"pedido {platos} ≠ {esp['platos']}")
    if esp.get("sin_agregar") and platos: fallas.append(f"agregó sin que lo pidiera: {platos}")
    if esp.get("menciona") and not any(norm(m) in respuesta for m in esp["menciona"]): fallas.append("no explicó lo esperado")
    for m in esp.get("no_dice", []):
        if norm(m) in respuesta: fallas.append(f"dijo «{m}»")
    if esp.get("nota"):                                          # el cambio («sin cebolla») debe quedar en la nota a cocina
        notas = norm(" ".join(p.get("nota", "") for p in (r.get("pedido") or {}).get("platos", [])))
        if not any(w in notas for w in (esp["nota"], "cebolla", "onion", "oignon")): fallas.append(f"la nota «sin {esp['nota']}» no llegó a cocina")
    if esp.get("confirmado") and not r.get("despedida"): fallas.append("no confirmó el pedido")
    return fallas


def sesion(rest, idioma):
    for i in range(6):
        r = requests.post(API + "/v1/sesion", json={"restaurante": rest, "mesa": "ejemplo", "idioma": idioma}, headers=ORIGEN, verify=CA, timeout=30)
        if r.status_code == 429: time.sleep(15); continue
        r.raise_for_status(); return r.json()
    raise RuntimeError("sin sesión")


def turno(s, wav):
    t0 = time.time()
    r = requests.post(API + "/v1/turno", data=wav, headers={**ORIGEN, "Content-Type": "audio/wav", "X-Apex-Sesion": s["sesion"], "X-Apex-Secreto": s["secreto"]},
                      verify=CA, timeout=60)
    total = time.time() - t0
    d = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
    return r.status_code, total, d


def main():
    a = argparse.ArgumentParser(); a.add_argument("--restaurante", default="demo"); a.add_argument("--escenarios", type=int, default=20)
    a.add_argument("--ritmo", type=float, default=7); a.add_argument("--salida", required=True); a.add_argument("--semilla", type=int, default=1)
    a.add_argument("--ruidos", default="none,15,8"); a.add_argument("--idiomas", default=",".join(E)); a.add_argument("--max_fallos_seguidos", type=int, default=6)
    a.add_argument("--pausas", type=int, default=0, help="si el servidor falla seguido: pausar 10 min (hasta N veces) en vez de parar")
    o = a.parse_args(); random.seed(o.semilla)
    ruidos = [None if x == "none" else float(x) for x in o.ruidos.split(",")]
    lista = [(l, esc) for l in o.idiomas.split(",") for esc in E[l]]
    seguidos = 0
    with open(o.salida, "a") as sal:
        for n in range(o.escenarios):
            idioma, esc = random.choice(lista); voz = random.choice(VOCES[idioma]); ritmo = random.choice(["-10%", "+0%", "+0%", "+15%"]); snr = random.choice(ruidos)
            try:
                s = sesion(o.restaurante, idioma)
            except Exception as e:
                print("sesión falló:", e, flush=True); time.sleep(30); continue
            for k, (texto, esp) in enumerate(esc):
                wav, dur = mezclar(voz_cliente(texto, voz, ritmo), snr)
                codigo, total, d = turno(s, wav)
                fallas = evaluar(esp, d) if codigo == 200 else [f"http {codigo}"]
                if d.get("sin_voz"): fallas.append("sin voz (tope o servicio caído)")
                fila = {"t": time.time(), "rest": o.restaurante, "idioma": idioma, "voz": voz, "ritmo": ritmo, "snr": snr, "texto": texto, "paso": k,
                        "audio_s": round(dur, 2), "http": codigo, "total_s": round(total, 2), "tiempos": d.get("tiempos"), "oido": d.get("oido"),
                        "wer": round(wer(texto, d.get("oido", "")), 3) if d.get("oido") is not None else None, "respuesta": d.get("texto"),
                        "pedido": {p["id"]: p["cantidad"] for p in (d.get("pedido") or {}).get("platos", [])},
                        "notas": [p.get("nota") for p in (d.get("pedido") or {}).get("platos", []) if p.get("nota")], "frase": bool(d.get("frase")),
                        "esperado": esp, "fallas": fallas}
                sal.write(json.dumps(fila, ensure_ascii=False) + "\n"); sal.flush()
                print(f"{n:4d} {idioma} {('limpio' if snr is None else f'{snr:.0f}dB'):6s} {total:5.2f}s {'OK ' if not fallas else 'MAL'} {texto[:40]} → {(d.get('oido') or '')[:40]} {fallas[:1]}", flush=True)
                seguidos = seguidos + 1 if codigo != 200 or d.get("sin_voz") else 0
                if seguidos >= o.max_fallos_seguidos:
                    if o.pausas <= 0:
                        print("Demasiadas fallas seguidas del servidor: paro para no saturarlo.", flush=True); return
                    o.pausas -= 1; seguidos = 0
                    print(f"PAUSA {time.strftime('%H:%M:%S', time.gmtime())}: el servidor rechaza; espero 10 minutos", flush=True); time.sleep(600)
                time.sleep(o.ritmo)
            try: requests.post(API + "/v1/sesion/fin", data=json.dumps({"sesion": s["sesion"], "secreto": s["secreto"], "motivo": "prueba"}), headers=ORIGEN, verify=CA, timeout=15)
            except Exception: pass


if __name__ == "__main__":
    main()
