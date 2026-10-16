from fastapi import FastAPI, Body
from fastapi.responses import Response
app = FastAPI()
@app.post("/pin")
def pin(d: dict): return {"ok": d.get("pin") == "4321"}
@app.post("/oido")
def oido(audio: bytes = Body(..., media_type="application/octet-stream"), idioma: str = "es", pista: str = ""):
    import io, wave
    w = wave.open(io.BytesIO(audio))          # falla si no es un WAV válido
    seg = w.getnframes() / w.getframerate()
    open("/tmp/claude-0/ultimo.wav", "wb").write(audio)
    print("WAV OK", w.getframerate(), "Hz", w.getnchannels(), "canal", round(seg, 2), "s", flush=True)
    print("idioma", idioma, "pista", pista[:60], flush=True)
    return {"texto": {"en": "two ajiacos please"}.get(idioma, "quiero un ajiaco"), "segundos": seg, "proveedor": "groq"}
@app.post("/pensar")
def pensar(d: dict):
    ya = any(m.get("role") == "tool" for m in d["mensajes"][-2:])
    if ya: return {"mensaje": {"role":"assistant","content":"Excelente, un ajiaco santafereño.","tool_calls":[]}, "uso":{"entrada":10,"salida":5}, "proveedor":"groq"}
    return {"mensaje": {"role":"assistant","content":"","tool_calls":[{"id":"c1","type":"function","function":{"name":"agregar_plato","arguments":"{\"plato_id\":\"ajiaco\"}"}}]}, "uso":{"entrada":10,"salida":5}, "proveedor":"groq"}
@app.post("/voz")
def voz(d: dict): return Response(b"ID3", media_type="audio/mpeg", headers={"X-Proveedor":"edge","X-Caracteres":str(len(d["texto"]))})
