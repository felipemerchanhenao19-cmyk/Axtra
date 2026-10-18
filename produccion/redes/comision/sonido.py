"""Música, efectos y voces de «La Comisión»: python sonido.py <carpeta_trabajo>  →  sonido.wav"""
import sys, os, json, numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
W_ = os.path.abspath(sys.argv[1]) + "/"
LIN = json.load(open(W_ + "voces/linea.json")); E = LIN["escenas"]
SR = 48000; DUR = LIN["dur"] + 0.3; N = int(DUR * SR); t = np.arange(N) / SR
rng = np.random.default_rng(5)
M = np.zeros((N, 2)); FX = np.zeros((N, 2)); VZ = np.zeros((N, 2))
def hz(n):
    d = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}
    return 440 * 2 ** ((d[n[:-1]] + (int(n[-1]) - 4) * 12) / 12)
def lp(x, f): return sosfilt(butter(2, f, "low", fs=SR, output="sos"), x)
def hp(x, f): return sosfilt(butter(2, f, "high", fs=SR, output="sos"), x)
def pon(buf, x, a, g=1.0, pan=0.0):
    i = int(a * SR); n = min(len(x), N - i)
    if n > 0 and i >= 0: buf[i:i + n, 0] += x[:n] * g * (1 - pan); buf[i:i + n, 1] += x[:n] * g * (1 + pan)
def tono(f, d, caida=6, armo=(1, .3, .1), g=1.0):
    n = int(d * SR); tl = np.arange(n) / SR
    return sum(a * np.sin(2 * np.pi * f * (k + 1) * tl) for k, a in enumerate(armo)) * np.exp(-tl * caida) * np.minimum(1, tl / 0.004) * g
def cuerdas(notas, d, g=0.1, corte=2200):
    n = int(d * SR); tl = np.arange(n) / SR; x = np.zeros(n)
    for nota in notas:
        for dd in (0.996, 1.004):
            f = hz(nota) * dd * (1 + 0.004 * np.sin(2 * np.pi * 5.3 * tl)); x += 2 * ((np.cumsum(np.full(n, f)) / SR + rng.random()) % 1) - 1
    return lp(x, corte) * g / len(notas) * np.minimum(1, tl / 0.25) * np.minimum(1, (d - tl) / 0.5)
def golpe(f=55, d=0.8, g=1.0):
    n = int(d * SR); tl = np.arange(n) / SR
    return (np.sin(2 * np.pi * (f * 1.6 * np.exp(-tl * 12) + f) * tl) * np.exp(-tl * 5) + lp(rng.standard_normal(n), 1500) * np.exp(-tl * 25) * 0.3) * g
def ruido(d, a, b, g): n = int(d * SR); return lp(hp(rng.standard_normal(n), a), b) * g
def patron(buf, ini, fin, bpm, notas, g, caida=9, armo=(1, .25, .1), pan=0.2, cada=1):
    paso = 60 / bpm / 2; k = 0; tt = ini
    while tt < fin - 0.05:
        if k % cada == 0: pon(buf, tono(hz(notas[k % len(notas)]), 0.6, caida, armo, g), tt, 1, pan * np.sin(k))
        tt += paso; k += 1
# --- título: acorde dramático de telenovela con trémolo
a, b = E["titulo"]
n = int(0.9 * SR); pon(FX, hp(rng.standard_normal(n), 4000) * np.linspace(0, 1, n) ** 3 * 0.15, a)
pon(M, cuerdas(["A2", "E3", "A3", "C4", "E4"], b - a + 0.3, 0.45), a + 0.5); pon(FX, golpe(45, 1.6, 0.8), a + 0.5)
# --- entrada: campanita de la puerta, brillo de diva y bolero suave
a, b = E["entrada"]
pon(FX, tono(hz("E6"), 1.2, 3, g=0.25), a + 0.1); pon(FX, tono(hz("C6"), 1.4, 3, g=0.25), a + 0.35)
for k in range(12): pon(FX, tono(hz("C7") * (1 + 0.05 * k), 0.4, 6, g=0.04), a + 0.3 + k * 0.05)
patron(M, a + 0.5, b, 96, ["A3", "C4", "E4", "C4", "D3", "F3", "A3", "F3", "E3", "G#3", "B3", "G#3"], 0.11, 6, (1, .35, .15))
# --- cobro: caja registradora y billetes
a, b = E["cobro"]
patron(M, a, b, 96, ["A3", "C4", "E4", "C4", "D3", "F3", "A3", "F3"], 0.09, 6, (1, .35, .15))
lc = [l for l in LIN["lineas"] if l["esc"] == "cobro" and l["quien"] == "comi"]
if lc:
    for i in range(6): pon(FX, ruido(0.12, 2000, 8000, 0.06), lc[0]["ini"] + i * 0.35)
    pon(FX, tono(hz("C7"), 0.5, 6, g=0.2) + 0, lc[0]["ini"] + 0.9); pon(FX, tono(hz("G6"), 0.6, 6, g=0.15), lc[0]["ini"] + 0.95)
# --- orbi: «ding» y brillo
a, b = E["orbi"]
pon(FX, tono(hz("E6"), 1.8, 2.5, g=0.3), a + 0.05); pon(FX, tono(hz("B6"), 1.8, 2.5, g=0.18), a + 0.1)
pon(M, cuerdas(["C3", "G3", "C4", "E4"], b - a, 0.08, 1800), a + 0.2)
# --- drama: «dun dun DUN» con zoom, luego música alegre de Apex
a, b = E["drama"]
ld = [l for l in LIN["lineas"] if l["esc"] == "drama" and l["quien"] == "comi"]
if ld:
    for i, (d, nota) in enumerate([(0, "D3"), (0.35, "D#3"), (0.7, "D3")]):
        pon(M, cuerdas([nota, "A3" if i < 2 else "A#3"], 0.7 if i < 2 else 1.2, 0.5), ld[0]["ini"] + d); pon(FX, golpe(50 + 4 * i, 1.0, 0.7 + 0.1 * i), ld[0]["ini"] + d)
    patron(M, ld[0]["fin"] + 0.3, b, 132, ["C4", "E4", "G4", "A4", "F4", "A4", "C5", "A4"], 0.10, 10)
    pon(FX, golpe(80, 0.6, 0.6), ld[0]["fin"] + 1.4)
# --- llanto: violín exagerado
a, b = E["llanto"]
for i, (nota, d) in enumerate([("E5", .4), ("D5", .4), ("C5", .4), ("B4", .5), ("A4", 1.0)]): pon(M, cuerdas([nota], d + 0.15, 0.3, 3200), a + 0.1 + sum([.4, .4, .4, .5, 1.0][:i]))
pon(M, cuerdas(["A2", "C3", "E3"], b - a, 0.1), a)
# --- salida: tacones, grito y portazo
a, b = E["salida"]
for k in range(6): pon(FX, tono(1800, 0.06, 40, (1,), 0.15) + 0, a + 1.6 + k * 0.15)
pon(FX, golpe(60, 1.0, 1.0), b - 0.9); pon(FX, ruido(0.3, 100, 1500, 0.2), b - 0.9)
# --- final y sello
a, b = E["final"]; patron(M, a, b, 132, ["C4", "E4", "G4", "A4"], 0.08, 10)
a, b = E["sello"]; pon(FX, tono(hz("E6"), 2.0, 2, g=0.3), a); pon(FX, tono(hz("B6"), 2.0, 2, g=0.2), a + 0.05)
pon(M, cuerdas(["C3", "G3", "C4", "E4", "G4"], b - a + 0.3, 0.16, 2800), a)
# --- voces
for l in LIN["lineas"]:
    sr, v = wavfile.read(W_ + f"voces/l{l['i']:02d}.wav"); v = v.astype(float) / 32767
    pon(VZ, v if v.ndim == 1 else v.mean(1), l["ini"], 1.0, {"comi": .2, "rosa": -.25}.get(l["quien"], 0))
# Mezcla: la música baja cuando alguien habla
activo = np.convolve((np.abs(VZ[:, 0]) > 0.02).astype(float), np.ones(int(0.25 * SR)) / int(0.25 * SR), "same")
ducking = 1 - 0.55 * np.clip(activo * 4, 0, 1)
ir = rng.standard_normal(int(1.0 * SR)) * np.exp(-np.linspace(0, 8, int(1.0 * SR))) * 0.03
for buf in (M, FX):
    for c in range(2): buf[:, c] += fftconvolve(buf[:, c], ir)[:N] * 0.5
mez = M * ducking[:, None] * 1.0 + FX * 0.9 + VZ * 1.6
mez *= np.minimum(1, (DUR - t) / 0.8)[:, None]
mez /= np.max(np.abs(mez)) / 0.92
wavfile.write(W_ + "sonido.wav", SR, (mez * 32767).astype(np.int16)); print("sonido listo")
