"""Voces de personajes: python voces.py <salida_dir> <id>=<personaje>:<texto> ...
Personajes: orbi (voz de orbe: aguda, ágil, con brillo metálico suave) · dueno (grave y dramático, de telenovela).
Base: Google si hay GOOGLE_TTS_API_KEY (VOZ_ORBI / VOZ_DUENO), si no piper (PIPER_DIR)."""
import sys, os, json, base64, subprocess, urllib.request
OUT = sys.argv[1].rstrip("/") + "/"; os.makedirs(OUT, exist_ok=True)
CLAVE = os.getenv("GOOGLE_TTS_API_KEY", ""); PIPER = os.getenv("PIPER_DIR", "")
PERSONAJES = {
  # base (google, piper), procesado de ffmpeg
  "orbi": (os.getenv("VOZ_ORBI", "es-US-Neural2-B"), "voice-es-carlfm-x-low/es-carlfm-x-low.onnx", 0.95,
           "highpass=f=140,rubberband=pitch=1.32:tempo=1.06:formant=shifted,"
           "chorus=0.6:0.85:28|36:0.25|0.2:0.35|0.4:1.8|2.2,equalizer=f=2800:t=q:w=1.2:g=4,equalizer=f=250:t=q:w=1:g=-3,"
           "aecho=0.7:0.5:18:0.18,acompressor=threshold=-18dB:ratio=3,loudnorm=I=-15:TP=-1.5"),
  "dueno": (os.getenv("VOZ_DUENO", "es-US-Neural2-C"), "voice-es-carlfm-x-low/es-carlfm-x-low.onnx", 1.0,
            "highpass=f=70,rubberband=pitch=0.84:tempo=1.0:formant=shifted,equalizer=f=150:t=q:w=1:g=3,aecho=0.8:0.6:60:0.2,loudnorm=I=-15:TP=-1.5"),
}
def base(txt, quien, ruta):
    voz, modelo, escala, _ = PERSONAJES[quien]
    if CLAVE:
        cuerpo = {"input": {"text": txt}, "voice": {"languageCode": voz[:5], "name": voz}, "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": 48000}}
        req = urllib.request.Request(f"https://texttospeech.googleapis.com/v1/text:synthesize?key={CLAVE}", json.dumps(cuerpo).encode(), {"Content-Type": "application/json"})
        open(ruta, "wb").write(base64.b64decode(json.load(urllib.request.urlopen(req, timeout=60))["audioContent"]))
    else:
        subprocess.run([PIPER + "/piper/piper", "--model", PIPER + "/" + modelo, "--length_scale", str(escala), "--sentence_silence", "0.2", "--output_file", ruta],
                       input=txt.encode(), check=True, capture_output=True)
dur = {}
for arg in sys.argv[2:]:
    k, resto = arg.split("=", 1); quien, txt = resto.split(":", 1)
    base(txt, quien, OUT + k + "_base.wav")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", OUT + k + "_base.wav", "-af", PERSONAJES[quien][3] + ",silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse,aresample=48000",
                    "-ac", "2", OUT + k + ".wav"], check=True)
    dur[k] = round(float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", OUT + k + ".wav"])), 2)
print(json.dumps(dur))
