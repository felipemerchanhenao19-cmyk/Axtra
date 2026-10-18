"""Diseño sonoro de «La factura»: python sonido.py <salida.wav> [carpeta_voces]"""
import sys, os, json, numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
SR = 48000; DUR = 25.5; N = int(DUR * SR); t = np.arange(N) / SR
rng = np.random.default_rng(3)
VOCES = sys.argv[2].rstrip("/") + "/" if len(sys.argv) > 2 and os.path.exists(sys.argv[2] + "/voz.json") else None
L = np.zeros(N); R = np.zeros(N)
def hz(n):
    d = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}
    return 440 * 2 ** ((d[n[:-1]] + (int(n[-1]) - 4) * 12) / 12)
def lp(x, f): return sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)
def hp(x, f): return sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)
def pon(x, a, g=1.0, pan=0.0):
    i = int(a * SR); n = min(len(x), N - i)
    if n <= 0: return
    L[i:i + n] += x[:n] * g * (1 - pan) ; R[i:i + n] += x[:n] * g * (1 + pan)
def ad(n, ataque=0.01, caida=3.0):
    tl = np.arange(n) / SR; return np.minimum(1, tl / ataque) * np.exp(-tl * caida)
def cuerdas(notas, dur, g=0.12, trem=0.0, corte=2500):   # sierra con vibrato: «cuerdas» de telenovela
    n = int(dur * SR); tl = np.arange(n) / SR; x = np.zeros(n)
    for nota in notas:
        for d in (0.996, 1.0, 1.004):
            f = hz(nota) * d * (1 + 0.004 * np.sin(2 * np.pi * 5.5 * tl))
            x += 2 * ((np.cumsum(np.full(n, f)) / SR + rng.random()) % 1) - 1
    x = lp(x, corte) * g / len(notas)
    e = np.minimum(1, tl / 0.06) * np.minimum(1, (dur - tl) / 0.4)
    if trem: e *= 0.75 + 0.25 * np.sin(2 * np.pi * trem * tl)
    return x * e
def golpe(f=55, dur=1.2, g=1.0):
    n = int(dur * SR); tl = np.arange(n) / SR
    return (np.sin(2 * np.pi * (f * 1.8 * np.exp(-tl * 10) + f) * tl) * np.exp(-tl * 3) + lp(rng.standard_normal(n), 1800) * np.exp(-tl * 18) * 0.4) * g
def campana(f, dur=1.5, g=0.3):
    n = int(dur * SR); tl = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * tl) + 0.5 * np.sin(2 * np.pi * f * 2.76 * tl) + 0.25 * np.sin(2 * np.pi * f * 5.4 * tl)) * np.exp(-tl * 4) * g
def silbido(a, b, dur=0.35, g=0.25):   # «whoosh»
    n = int(dur * SR); x = rng.standard_normal(n); out = np.zeros(n); paso = n // 12
    for k in range(12):
        f = a + (b - a) * k / 11; s = slice(k * paso, (k + 1) * paso); out[s] = lp(x, f)[s]
    return out * np.sin(np.linspace(0, np.pi, n)) * g
def blip(f, dur=0.07, g=0.18, cuadrada=False):
    n = int(dur * SR); tl = np.arange(n) / SR; o = np.sin(2 * np.pi * f * tl)
    if cuadrada: o = np.sign(o) * 0.6
    return lp(o, 3000) * np.sin(np.linspace(0, np.pi, n)) ** 0.6 * g
def hablar(a, b, base, g=0.16, cuadrada=False):
    if VOCES: return
    tt = a
    while tt < b - 0.05:
        d = rng.uniform(0.06, 0.11); pon(blip(base * rng.uniform(0.85, 1.35), d, g, cuadrada), tt, 1, rng.uniform(-0.2, 0.2)); tt += d + rng.uniform(0.01, 0.05)
# 0 · Título: platillo que crece y acorde dramático (la menor) con trémolo
n = int(1.0 * SR); pon(hp(rng.standard_normal(n), 4000) * np.linspace(0, 1, n) ** 3 * 0.18, 0.0)
pon(cuerdas(["A2", "E3", "A3", "C4", "E4"], 2.3, 0.5, trem=7), 0.55); pon(golpe(45, 1.6, 0.8), 0.55)
# 1 · Notificación y «dun dun DUN» en los zoom
pon(campana(hz("E6"), 0.4, 0.15), 2.3); pon(campana(hz("B6"), 0.5, 0.15), 2.45)
for i, (a, nota) in enumerate([(3.6, "D3"), (4.35, "D#3"), (5.1, "D3")]):
    pon(silbido(400, 6000, 0.25, 0.18), a - 0.22)
    pon(cuerdas([nota, "A3" if i < 2 else "A#3"], 0.75 if i < 2 else 1.3, 0.55), a); pon(golpe(50 + i * 4, 1.0, 0.7 + 0.15 * i), a)
hablar(5.2, 6.4, 210, 0.15, True)   # el dueño se queja
# 2 · 27 %: golpe y violín triste (re menor, descendente) + gotas
pon(golpe(40, 1.8, 1.0), 6.45)
mel = [("A4", 0.55), ("G4", 0.35), ("F4", 0.55), ("E4", 0.4), ("D4", 0.9)]
tt = 6.75
for nota, d in mel: pon(cuerdas([nota], d + 0.15, 0.32, corte=3200), tt, 1, 0.1); tt += d
pon(cuerdas(["D3", "F3", "A3"], 2.9, 0.18), 6.6)
for i in range(6):
    for k in range(3): pon(campana(hz("C7") * (1 + 0.1 * i), 0.25, 0.05), 6.9 + i * 0.35 + k * 1.1 + 0.6)
# 3 · Orbi: «ding», brillo y colchón cálido (do mayor)
pon(campana(hz("E6"), 1.6, 0.35), 9.0); pon(campana(hz("B6"), 1.6, 0.2), 9.05)
for k in range(10): pon(campana(hz("C7") * (1 + 0.06 * k), 0.4, 0.04), 9.0 + k * 0.04)
pon(cuerdas(["C3", "G3", "C4", "E4"], 5.2, 0.08, corte=1500), 9.1)
hablar(10.1, 11.4, 720); hablar(11.5, 13.9, 760)
# 4 · Caja: silbido de entrada, sello 0 % y ritmo alegre (marimba en do mayor, 112 bpm)
pon(silbido(300, 5000, 0.4, 0.2), 13.8); pon(golpe(70, 0.8, 0.9), 15.4)
for j, nota in enumerate(["C5", "E5", "G5", "C6"]): pon(campana(hz(nota), 1.2, 0.18), 15.45 + j * 0.06)
paso = 60 / 112 / 2; patron = ["C5", "E5", "G5", "E5", "A4", "C5", "E5", "C5", "F4", "A4", "C5", "A4", "G4", "B4", "D5", "B4"]
k = 0; tt = 14.2
while tt < 19.0:
    nn = int(0.3 * SR); tl = np.arange(nn) / SR; f = hz(patron[k % len(patron)])
    pon((np.sin(2 * np.pi * f * tl) + 0.3 * np.sin(2 * np.pi * f * 4 * tl)) * np.exp(-tl * 14) * 0.13, tt, 1, 0.25 * np.sin(k))
    if k % 4 == 0: pon(golpe(60, 0.3, 0.25), tt)
    tt += paso; k += 1
hablar(15.9, 18.9, 800)
# 5 · Ruptura por chat: silencio, «pop» de mensajes, rayón de disco y golpe final
pon(cuerdas(["A2", "E3", "A3"], 3.4, 0.12, trem=6), 19.1)
for a in (19.25, 20.75, 21.35): pon(blip(1300, 0.06, 0.35) + 0, a); pon(blip(900, 0.05, 0.2), a + 0.05)
n = int(0.45 * SR); tl = np.arange(n) / SR
pon(lp(rng.standard_normal(n), 3000) * np.sin(2 * np.pi * 9 * tl) * np.exp(-tl * 4) * 0.35 + np.sin(2 * np.pi * (900 - 1500 * tl) * tl) * 0.15 * np.exp(-tl * 5), 20.55)
pon(cuerdas(["D3", "A3", "D4", "F4"], 1.2, 0.5), 21.35); pon(golpe(45, 1.2, 0.9), 21.35)
# 6 · Sello: «ding», acorde final y Orbi preguntando por el postre
pon(campana(hz("E6"), 2.0, 0.35), 22.6); pon(campana(hz("B6"), 2.0, 0.2), 22.65)
pon(cuerdas(["C3", "G3", "C4", "E4", "G4"], 2.9, 0.2, corte=2600), 22.6)
hablar(23.3, 24.6, 780)
# Voces de los personajes (si existen): reemplazan las burbujas
if VOCES:
    from scipy.io import wavfile as wf
    for k, a in {"d1": 5.2, "o1": 10.15, "o2": 11.55, "o3": 15.95, "o4": 23.35}.items():
        sr, v = wf.read(VOCES + k + ".wav"); v = v.astype(float) / 32767
        if v.ndim > 1: v = v.mean(1)
        pon(v, a, 2.4)
# Sala: reverberación corta y volumen
ir = rng.standard_normal(int(1.2 * SR)) * np.exp(-np.linspace(0, 8, int(1.2 * SR))) * 0.03
L = L + fftconvolve(L, ir)[:N] * 0.6; R = R + fftconvolve(R, ir[::-1])[:N] * 0.6
x = np.stack([L, R], 1); x *= np.minimum(1, (DUR - t) / 0.6)[:, None]
x /= np.max(np.abs(x)) / 0.9
wavfile.write(sys.argv[1], SR, (x * 32767).astype(np.int16)); print("sonido listo")
