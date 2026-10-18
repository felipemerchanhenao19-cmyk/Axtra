"""Graba las voces con Microsoft (edge-tts) y arma la línea de tiempo: python voces.py <carpeta>"""
import sys, os, json, asyncio, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guion
import edge_tts
OUT = os.path.abspath(sys.argv[1]) + "/"; os.makedirs(OUT, exist_ok=True)
PROXY = os.getenv("HTTPS_PROXY")
async def grabar():
    for i, (esc, quien, txt, _) in enumerate(guion.LINEAS):
        voz, vel, tono = guion.REPARTO[quien]
        await edge_tts.Communicate(txt, voz, rate=vel, pitch=tono, proxy=PROXY).save(OUT + f"l{i:02d}.mp3")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", OUT + f"l{i:02d}.mp3", "-af",
                        "silenceremove=start_periods=1:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_threshold=-50dB,areverse,"
                        "highpass=f=80,acompressor=threshold=-20dB:ratio=2.5,loudnorm=I=-16:TP=-1.5,aresample=48000", "-ac", "1", OUT + f"l{i:02d}.wav"], check=True)
asyncio.run(grabar())
dur = lambda f: float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]))
# Línea de tiempo: cada escena empieza donde terminó la anterior; las voces van en orden con su pausa
t, escenas, lineas = 0.0, {}, []
for esc in guion.ORDEN:
    ini = t
    for i, (e, quien, txt, pausa) in enumerate(guion.LINEAS):
        if e != esc: continue
        t += pausa; d = round(dur(OUT + f"l{i:02d}.wav"), 2)
        lineas.append({"i": i, "esc": esc, "quien": quien, "txt": txt, "ini": round(t, 2), "fin": round(t + d, 2)}); t += d
    t += guion.COLA[esc]; escenas[esc] = [round(ini, 2), round(t, 2)]
json.dump({"escenas": escenas, "lineas": lineas, "dur": round(t, 2)}, open(OUT + "linea.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps(escenas), "total", round(t, 1))
