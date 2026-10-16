"""Narración: python voz_cine.py play|domicilios <carpeta_salida>
Con GOOGLE_TTS_API_KEY usa una voz de Google (grave, con énfasis por SSML). Sin ella, piper (provisional)."""
import sys, os, re, json, base64, subprocess, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import guion_cine
PROD, OUT = sys.argv[1], sys.argv[2].rstrip("/") + "/"
os.makedirs(OUT, exist_ok=True)
ESC = {"play": guion_cine.PLAY, "domicilios": guion_cine.DOMICILIOS}[PROD]
CLAVE = os.getenv("GOOGLE_TTS_API_KEY", "")
VOZ = os.getenv("VOZ_GOOGLE", "es-US-Studio-B")          # voz masculina grave; admite SSML con énfasis
PIPER = os.getenv("PIPER_DIR", "")                       # carpeta con piper/ y el modelo (respaldo)

def ssml(txt):
    t = txt.replace("...", '<break time="650ms"/>')
    t = re.sub(r"\*([^*]+)\*", r'<emphasis level="strong">\1</emphasis>', t)
    t = re.sub(r"\.\s", '.<break time="350ms"/> ', t)
    return f'<speak><prosody rate="92%" pitch="-2st">{t}</prosody></speak>'

def google(txt, ruta):
    cuerpo = {"input": {"ssml": ssml(txt)}, "voice": {"languageCode": VOZ[:5], "name": VOZ},
              "audioConfig": {"audioEncoding": "LINEAR16", "sampleRateHertz": 48000}}
    req = urllib.request.Request(f"https://texttospeech.googleapis.com/v1/text:synthesize?key={CLAVE}", json.dumps(cuerpo).encode(),
                                 {"Content-Type": "application/json"})
    open(ruta, "wb").write(base64.b64decode(json.load(urllib.request.urlopen(req, timeout=60))["audioContent"]))

def piper(txt, ruta):
    limpio = txt.replace("*", "").replace("...", ",")
    subprocess.run([PIPER + "/piper/piper", "--model", PIPER + "/voice-es-carlfm-x-low/es-carlfm-x-low.onnx", "--length_scale", "1.15",
                    "--sentence_silence", "0.45", "--output_file", ruta], input=limpio.encode(), check=True, capture_output=True)

dur = {}
for k, txt in ESC:
    crudo = OUT + k + "_crudo.wav"
    (google if CLAVE else piper)(txt, crudo)
    # Voz de narrador: cuerpo en graves, presencia, compresión suave y volumen parejo
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", crudo, "-af",
                    "highpass=f=70,equalizer=f=140:t=q:w=1:g=3,equalizer=f=3500:t=q:w=1.5:g=2,acompressor=threshold=-20dB:ratio=3:attack=10:release=150,loudnorm=I=-16:TP=-1.5,aresample=48000",
                    "-ac", "2", OUT + k + ".wav"], check=True)
    dur[k] = round(float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", OUT + k + ".wav"])), 2)
json.dump({"motor": "google " + VOZ if CLAVE else "piper (provisional)", "dur": dur}, open(OUT + "voz.json", "w"), indent=1)
print(dur, round(sum(dur.values()), 1))
