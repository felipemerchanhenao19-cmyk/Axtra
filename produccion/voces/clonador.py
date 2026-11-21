"""Clonador de voces de Apex: gratis, local y con control de calidad automático.

Modelo: Chatterbox Multilingual (Resemble AI, licencia MIT, uso comercial permitido, español incluido).
Cada audio generado lleva la marca de agua inaudible Perth del modelo, que identifica la voz como sintética.
Control de calidad: cada frase se transcribe con Whisper (faster-whisper) para comprobar que dice exactamente
el texto, y se compara con la huella de la voz original. Si falla, se repite con otra semilla y se queda la mejor.

Uso (con el entorno de voces: /home/user/voz-env/bin/python, ver instalar.sh):
  python clonador.py registrar <nombre> grabacion1.m4a [grabacion2.wav ...] --autoriza "Nombre Apellido" --acepto
  python clonador.py decir <nombre> "Texto a decir" salida.wav [--emocion 0.5] [--ritmo 0.5]
  python clonador.py probar <nombre>            → tres frases de prueba con sus métricas
  python clonador.py voces                      → voces registradas
  python clonador.py lote trabajo.json          → lo usa el motor de videos (una carga del modelo para todas las líneas)

Solo se registra una voz con la autorización expresa de su dueño: queda guardada en banco/<nombre>/meta.json."""
import os, sys, json, re, hashlib, subprocess, time, unicodedata, argparse, warnings
import numpy as np
warnings.filterwarnings("ignore")
AQUI = os.path.dirname(os.path.abspath(__file__)) + "/"
BANCO = AQUI + "banco/"
SR_REF = 24000
UMBRAL_PARECIDO = 0.86   # medido: clones 0,90–0,94; otra voz masculina parecida 0,83
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

# ---------------------------------------------------------------- texto
def _num(n):
    from num2words import num2words
    return num2words(n, lang="es")

def texto_hablado(t):
    """Escribe en palabras lo que un modelo de voz suele leer mal: precios, 24/7, porcentajes, cifras con punto de miles."""
    t = t.replace("24/7", "veinticuatro siete").replace("%", " por ciento")
    t = re.sub(r"\$\s?(\d{1,3}(?:\.\d{3})+|\d+)", lambda m: _num(int(m.group(1).replace(".", ""))) + " pesos", t)
    t = re.sub(r"\b(\d{1,3}(?:\.\d{3})+)\b", lambda m: _num(int(m.group(1).replace(".", ""))), t)
    t = re.sub(r"\b\d+\b", lambda m: _num(int(m.group(0))), t)
    return re.sub(r"\s+", " ", t).strip()

def normal(t):
    t = unicodedata.normalize("NFD", texto_hablado(t).lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-zñ ]+", " ", t).split()

def error_caracteres(ref, hip):
    """Tasa de error por caracteres (0 = idéntico) entre lo que se pidió y lo que Whisper entendió."""
    a, b = " ".join(normal(ref)), " ".join(normal(hip))
    if not a: return 0.0
    d = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        p, d[0] = d[0], i
        for j, cb in enumerate(b, 1): p, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, p + (ca != cb))
    return d[len(b)] / len(a)

def frases(t, maximo=220):
    """Parte textos largos en frases (el modelo rinde mejor con frases cortas)."""
    if len(t) <= maximo: return [t]
    partes, actual = [], ""
    for f in re.split(r"(?<=[.!?…])\s+", t):
        if actual and len(actual) + len(f) > maximo: partes.append(actual); actual = f
        else: actual = (actual + " " + f).strip()
    return partes + ([actual] if actual else [])

# ---------------------------------------------------------------- audio
def leer(ruta, sr=SR_REF):
    x = subprocess.run(["ffmpeg", "-v", "error", "-i", ruta, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(x, np.float32).copy()

def escribir(ruta, x, sr):
    from scipy.io import wavfile
    wavfile.write(ruta, sr, (np.clip(x, -1, 1) * 32767).astype(np.int16))

def niveles(x, sr, ventana=0.03):
    n = int(sr * ventana); k = len(x) // n
    return 20 * np.log10(np.sqrt((x[:k * n].reshape(k, n) ** 2).mean(1)) + 1e-9)

def analizar(x, sr):
    db = niveles(x, sr); piso, voz = np.percentile(db, 10), np.percentile(db, 90)
    return {"duracion": round(len(x) / sr, 1), "ruido_db": round(float(piso), 1), "relacion_senal_ruido_db": round(float(voz - piso), 1),
            "recorte_pct": round(float((np.abs(x) > 0.985).mean() * 100), 3), "habla_pct": round(float((db > piso + 12).mean() * 100), 1)}

def limpiar(entradas, salida):
    """Une las grabaciones, quita zumbidos y ruido de fondo, acorta pausas largas y nivela el volumen."""
    lista, partes = salida + ".txt", []
    for i, e in enumerate(entradas):
        p = salida + f".p{i}.wav"; subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", e, "-ac", "1", "-ar", "48000", p], check=True); partes.append(p)
    with open(lista, "w") as f: f.write("".join(f"file '{p}'\n" for p in partes))
    filtro = ("highpass=f=75,lowpass=f=11000,afftdn=nr=10:nf=-45:tn=1,"
              "silenceremove=start_periods=1:start_threshold=-45dB:stop_periods=-1:stop_duration=0.5:stop_threshold=-45dB:stop_silence=0.3,"
              "loudnorm=I=-20:TP=-2:LRA=11")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", lista, "-af", filtro, "-ac", "1", "-ar", str(SR_REF), salida], check=True)
    for p in partes + [lista]: os.remove(p)

def mejor_ventana(x, sr, seg=10.0):
    """El trozo de ~10 s con más habla continua y sin recortes: es lo que el modelo usa como muestra."""
    if len(x) <= seg * sr: return x
    db = niveles(x, sr, 0.03); umbral = np.percentile(db, 10) + 12; act = (db > umbral).astype(float)
    clip = np.abs(x[: len(db) * int(sr * 0.03)]).reshape(len(db), -1).max(1) > 0.985
    n = int(seg / 0.03); mejor, ini = -1, 0
    for i in range(0, len(db) - n, 8):
        s = act[i:i + n].mean() - clip[i:i + n].mean() * 5
        if s > mejor: mejor, ini = s, i
    a = int(ini * 0.03 * sr); return x[a:a + int(seg * sr)]

def huella_archivo(ruta): return hashlib.sha256(open(ruta, "rb").read()).hexdigest()

# ---------------------------------------------------------------- modelos
class Motor:
    def __init__(self):
        import torch
        torch.set_num_threads(os.cpu_count() or 4)
        from chatterbox.mtl_tts import ChatterboxMultilingualTTS
        self.torch = torch; self.tts = ChatterboxMultilingualTTS.from_pretrained(device="cpu"); self.sr = self.tts.sr
        self._asr = None; self._voz = None; self._emb = {}

    @property
    def asr(self):
        if self._asr is None:
            from faster_whisper import WhisperModel
            self._asr = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=os.cpu_count() or 4)
        return self._asr

    def transcribir(self, x, sr):
        import scipy.signal as ss
        y = ss.resample_poly(x, 16000, sr).astype(np.float32)
        segs, _ = self.asr.transcribe(y, language="es", beam_size=3, vad_filter=False)
        return " ".join(s.text.strip() for s in segs)

    def embedding(self, x, sr):
        import scipy.signal as ss
        y = ss.resample_poly(x, 16000, sr).astype(np.float32)
        e = self.tts.ve.embeds_from_wavs([y], sample_rate=16000); e = np.asarray(e).reshape(-1)
        return e / (np.linalg.norm(e) + 1e-9)

    def usar(self, nombre, emocion):
        ref = BANCO + nombre + "/ref.wav"
        if not os.path.exists(ref): sys.exit(f"No existe la voz «{nombre}». Regístrela primero (python clonador.py registrar ...).")
        if self._voz != nombre:
            self.tts.prepare_conditionals(ref, exaggeration=emocion); self._voz = nombre
            self._emb[nombre] = np.load(BANCO + nombre + "/huella.npy")
        return self._emb[nombre]

    def decir(self, nombre, texto, emocion=0.5, ritmo=0.5, intentos=3, semilla=7, mostrar=True):
        """Genera la frase; la acepta si Whisper entiende el texto (error ≤ 8 %) y la voz se parece a la original (≥ UMBRAL_PARECIDO). Si no, reintenta."""
        huella = self.usar(nombre, emocion); hablado = texto_hablado(texto); trozos = frases(hablado)
        mejor = None
        for k in range(intentos):
            self.torch.manual_seed(semilla + k * 101)
            audio = []
            for f in trozos:
                w = self.tts.generate(f, language_id="es", exaggeration=emocion, cfg_weight=ritmo).squeeze(0).numpy()
                audio += [w, np.zeros(int(self.sr * 0.28), np.float32)]
            x = np.concatenate(audio[:-1]) if audio else np.zeros(1, np.float32)
            oido = self.transcribir(x, self.sr); err = error_caracteres(hablado, oido)
            sim = float(np.dot(self.embedding(x, self.sr), huella))
            vel = len(" ".join(normal(hablado))) / max(0.1, len(x) / self.sr)   # caracteres por segundo (habla normal: 9–20)
            umbral = UMBRAL_PARECIDO if len(x) / self.sr >= 2.5 else UMBRAL_PARECIDO - 0.05   # en frases muy cortas la huella es menos precisa
            ok = err <= 0.08 and sim >= umbral and 7 <= vel <= 24
            nota = {"intento": k + 1, "error_texto": round(err, 3), "parecido_voz": round(sim, 3), "car_por_seg": round(vel, 1), "oido": oido, "ok": ok}
            if mostrar: print("   ", json.dumps(nota, ensure_ascii=False), flush=True)
            puntaje = sim - 3 * err - (0 if 7 <= vel <= 24 else 0.5)
            if mejor is None or puntaje > mejor[0]: mejor = (puntaje, x, nota)
            if ok: break
        return mejor[1], self.sr, mejor[2]

# ---------------------------------------------------------------- órdenes
def registrar(a):
    if not a.acepto or not a.autoriza.strip():
        sys.exit("Para clonar una voz hace falta la autorización de su dueño: use --autoriza \"Nombre completo\" --acepto")
    nombre = re.sub(r"[^a-z0-9_-]", "", a.nombre.lower())
    d = BANCO + nombre + "/"; os.makedirs(d, exist_ok=True)
    for e in a.archivos:
        if not os.path.exists(e): sys.exit(f"No encuentro {e}")
    limpiar(a.archivos, d + "limpio.wav"); x = leer(d + "limpio.wav")
    crudo = np.concatenate([leer(e) for e in a.archivos]); info_crudo = analizar(crudo, SR_REF); info = analizar(x, SR_REF)
    avisos = []
    if info["duracion"] < 8: sys.exit(f"La grabación útil dura {info['duracion']} s: hacen falta al menos 10 s de habla (ideal 30–60 s).")
    if info["duracion"] < 25: avisos.append("Grabación corta: con 30–60 s de lectura la voz sale más parecida.")
    if info_crudo["relacion_senal_ruido_db"] < 25: avisos.append("Hay bastante ruido de fondo: grabe en un cuarto más silencioso (sin ventilador ni tráfico).")
    if info_crudo["recorte_pct"] > 0.1: avisos.append("La grabación satura (volumen muy alto o micrófono muy cerca): aleje el celular un poco.")
    ref = mejor_ventana(x, SR_REF, 10.0); escribir(d + "ref.wav", ref, SR_REF)
    m = Motor(); np.save(d + "huella.npy", m.embedding(x, SR_REF))
    meta = {"nombre": nombre, "autoriza": a.autoriza.strip(), "fecha": time.strftime("%Y-%m-%d %H:%M"), "uso": a.uso,
            "consentimiento": f"{a.autoriza.strip()} autorizó clonar su voz para el contenido de Apex Corporation ({a.uso}).",
            "originales_sha256": [huella_archivo(e) for e in a.archivos], "grabacion": info_crudo, "limpia": info, "avisos": avisos}
    json.dump(meta, open(d + "meta.json", "w"), ensure_ascii=False, indent=1)
    print(f"Voz «{nombre}» registrada: {info['duracion']} s útiles, relación señal/ruido {info_crudo['relacion_senal_ruido_db']} dB.")
    for v in avisos: print("  ⚠", v)
    print("Probando la voz…"); probar(argparse.Namespace(nombre=nombre, emocion=0.5), m)

PRUEBAS = ["Hola, ¿cómo están? Hoy les traigo algo que les va a cambiar el día.",
           "¿En serio? ¡No lo puedo creer! Llegó el pedido antes de tiempo.",
           "Con Apex Domicilios no pagas comisión: el pedido llega directo a tu restaurante."]

def probar(a, m=None):
    m = m or Motor(); d = BANCO + a.nombre + "/prueba/"; os.makedirs(d, exist_ok=True); notas = []
    for i, t in enumerate(PRUEBAS):
        print(f"  {i + 1}. {t}"); t0 = time.time(); x, sr, nota = m.decir(a.nombre, t, a.emocion)
        escribir(d + f"prueba{i + 1}.wav", x, sr); nota["segundos_de_proceso"] = round(time.time() - t0); notas.append(nota)
    json.dump(notas, open(d + "notas.json", "w"), ensure_ascii=False, indent=1)
    print(f"Pruebas en {d}  ·  parecido medio {np.mean([n['parecido_voz'] for n in notas]):.2f}  ·  error medio de texto {np.mean([n['error_texto'] for n in notas]):.3f}")

def decir(a):
    m = Motor(); x, sr, nota = m.decir(a.nombre, a.texto, a.emocion, a.ritmo); escribir(a.salida, x, sr)
    print("listo", a.salida, json.dumps(nota, ensure_ascii=False))

def lote(a):
    """trabajo.json: [{"voz": "felipe", "texto": "...", "salida": "/ruta.wav", "emocion": 0.5, "ritmo": 0.5}, ...]"""
    tareas = json.load(open(a.trabajo)); m = Motor(); informe = []
    for i, t in enumerate(sorted(tareas, key=lambda t: t["voz"])):
        print(f"[{i + 1}/{len(tareas)}] {t['voz']}: {t['texto']}", flush=True)
        x, sr, nota = m.decir(t["voz"], t["texto"], t.get("emocion", 0.5), t.get("ritmo", 0.5))
        escribir(t["salida"], x, sr); informe.append(dict(t, **nota))
    json.dump(informe, open(a.trabajo.replace(".json", "") + "-informe.json", "w"), ensure_ascii=False, indent=1)
    malas = [r for r in informe if not r["ok"]]
    print(f"{len(informe) - len(malas)}/{len(informe)} líneas pasaron el control de calidad.")
    for r in malas: print("  ⚠ revisar:", r["voz"], "·", r["texto"], "→ se oyó:", r["oido"])

def voces(a):
    if not os.path.isdir(BANCO): print("Aún no hay voces registradas."); return
    for n in sorted(os.listdir(BANCO)):
        if os.path.exists(BANCO + n + "/meta.json"):
            m = json.load(open(BANCO + n + "/meta.json")); print(f"{n:14s} autoriza: {m['autoriza']:24s} {m['limpia']['duracion']:5.1f} s  {m['fecha']}")

if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter); s = p.add_subparsers(dest="orden", required=True)
    r = s.add_parser("registrar"); r.add_argument("nombre"); r.add_argument("archivos", nargs="+"); r.add_argument("--autoriza", default="")
    r.add_argument("--acepto", action="store_true"); r.add_argument("--uso", default="videos de redes sociales y piezas comerciales"); r.set_defaults(f=registrar)
    r = s.add_parser("decir"); r.add_argument("nombre"); r.add_argument("texto"); r.add_argument("salida")
    r.add_argument("--emocion", type=float, default=0.5); r.add_argument("--ritmo", type=float, default=0.5); r.set_defaults(f=decir)
    r = s.add_parser("probar"); r.add_argument("nombre"); r.add_argument("--emocion", type=float, default=0.5); r.set_defaults(f=probar)
    r = s.add_parser("lote"); r.add_argument("trabajo"); r.set_defaults(f=lote)
    r = s.add_parser("voces"); r.set_defaults(f=voces)
    a = p.parse_args(); a.f(a)
