"""Música, efectos y voces de «Mesero nocturno»: python sonido.py <carpeta_trabajo>  →  sonido.wav"""
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
def sax(nota, d, g=0.12, corte=1900):
    n = int(d * SR); tl = np.arange(n) / SR; f = hz(nota) * (1 + 0.006 * np.sin(2 * np.pi * 5.2 * tl) * np.minimum(1, tl / 0.3))
    x = 2 * ((np.cumsum(f) / SR) % 1) - 1 + 0.04 * rng.standard_normal(n)
    return lp(lp(x, corte), corte * 1.4) * g * np.minimum(1, tl / 0.06) * np.minimum(1, (d - tl) / 0.12)
def bajo(nota, d=0.5, g=0.5): return lp(tono(hz(nota), d, 5, (1, .5, .2), g), 600)
def escobilla(g=0.05): n = int(0.25 * SR); tl = np.arange(n) / SR; return hp(rng.standard_normal(n), 3000) * np.exp(-tl * 14) * np.minimum(1, tl / 0.03) * g
def piano(notas, d=1.6, g=0.06): return sum(tono(hz(x), d, 2.5, (1, .4, .15, .05), g) for x in notas)
def jazz(ini, fin, bpm=84, notas=("D2", "F2", "A2", "C3", "B1", "D2", "F2", "G#2", "A1", "C#2", "E2", "G2"), acordes=(("D3", "F3", "A3", "C4"), ("B2", "D3", "F3", "G#3"), ("A2", "C#3", "G3", "E4")), g=1.0):
    neg = 60 / bpm; k = 0; tt = ini
    while tt < fin - 0.1:
        pon(M, bajo(notas[k % len(notas)], neg * 0.95, 0.42 * g), tt)
        if k % 2: pon(M, escobilla(0.05 * g), tt, 1, 0.3)
        pon(M, escobilla(0.02 * g), tt + neg * 0.66, 1, -0.3)
        if k % 4 == 0: pon(M, piano(acordes[(k // 4) % len(acordes)], neg * 3.5, 0.05 * g), tt + neg * 0.5, 1, -0.2)
        tt += neg; k += 1
def melodia(ini, frase, g=0.12):
    tt = ini
    for nota, d in frase:
        if nota: pon(M, sax(nota, d * 1.05, g), tt, 1, 0.15)
        tt += d
def trueno(a, g=0.7):
    n = int(3.5 * SR); tl = np.arange(n) / SR
    x = lp(rng.standard_normal(n), 220) * (np.exp(-tl * 1.3) * (1 + 0.6 * np.sin(2 * np.pi * 2.3 * tl) ** 2)) * np.minimum(1, tl / 0.05) * g * 4
    pon(FX, x, a); pon(FX, hp(rng.standard_normal(int(0.25 * SR)), 1500) * np.exp(-np.arange(int(0.25 * SR)) / SR * 12) * 0.25 * g, a)
def lluvia(ini, fin, g, corte=6000):
    n = int((fin - ini) * SR); x = lp(hp(rng.standard_normal(n), 400), corte) * g
    gotas = (rng.random(n) < 0.0016) * rng.standard_normal(n) * 3 * g; x += hp(gotas, 2500)
    x *= np.minimum(1, np.arange(n) / SR / 0.4) * np.minimum(1, (n - np.arange(n)) / SR / 0.4); pon(FX, x, ini, 1, 0); pon(FX, np.roll(x, 900) * 0.6, ini, 1, 0.4)
def golpecito(a, g=0.2, f=2600): n = int(0.05 * SR); tl = np.arange(n) / SR; pon(FX, (hp(rng.standard_normal(n), 1500) * 0.6 + np.sin(2 * np.pi * f * tl)) * np.exp(-tl * 90) * g, a, 1, rng.uniform(-.3, .3))
def li(esc, quien, n=0): return [l for l in LIN["lineas"] if l["esc"] == esc and l["quien"] == quien][n]
def redoble(a, d, g=0.05):
    tt = a
    while tt < a + d: golpecito(tt, g * (0.6 + 0.4 * (tt - a) / d), 220); pon(FX, escobilla(g * 0.6), tt); tt += 0.07
def trafico(ini, fin, g):
    n = int((fin - ini) * SR); tl = np.arange(n) / SR; x = lp(rng.standard_normal(n), 140) * (1 + 0.3 * np.sin(2 * np.pi * 0.2 * tl)) * g * 3
    x *= np.minimum(1, tl / 0.3) * np.minimum(1, (tl[-1] - tl) / 0.3); pon(FX, x, ini)
# --- gancho: zumbido grave y latido; corte seco con golpe en el título
a, b = E["gancho"]
pon(M, cuerdas(["C2", "G2", "C#3"], b - a + 0.1, 0.25, 700), a)
for d in (0.15, 0.45, 1.05, 1.35): pon(FX, golpe(48, 0.35, 0.5), a + d)
# --- título: golpe, lluvia, primera frase del saxo (original, no es la melodía de la película)
a, b = E["titulo"]
pon(FX, golpe(36, 2.2, 1.0), a); pon(FX, ruido(0.4, 60, 400, 0.4), a)
lluvia(a, E["taxi"][1], 0.04); trafico(a, E["mesas"][1], 0.03)
redoble(a + 0.2, 1.3, 0.05)
melodia(a + 0.3, [("G4", .45), ("C5", .35), ("D#5", 1.1), (None, .15), ("D5", .3), ("C5", .7)], 0.12)
pon(M, piano(("C3", "G3", "D#4", "A#4"), 2.6, 0.08), a + 0.3)
# --- taxi: jazz lento de madrugada, bocinas lejanas
a, b = E["taxi"]
jazz(a, b, 70, ("C2", "D#2", "G2", "A#2", "G#1", "C2", "D#2", "G2", "G1", "B1", "D2", "F2"), (("C3", "D#3", "G3", "A#3"), ("G#2", "C3", "D#3", "G3"), ("G2", "B2", "D3", "F3")), 0.9)
melodia(a + 0.4, [("D#5", 1.2), ("D5", .4), ("C5", .4), ("A#4", 1.4), (None, .6), ("G4", .5), ("A#4", .5), ("C5", 1.6)], 0.07)
for d in (1.6, 4.2): pon(FX, lp(tono(311, 0.5, 3, (1, .6, .4, .3), 0.06) + tono(370, 0.5, 3, (1, .6, .4, .3), 0.05), 2500), a + d, 1, 0.5)
# --- mesas: reloj acelerado, timbre que nadie atiende, platos, puerta
a, b = E["mesas"]
for k in range(int((b - a) / 0.25)): golpecito(a + k * 0.25, 0.05, 3200 if k % 2 else 2400)
for k in range(int((b - a) / 0.5)): pon(M, bajo(["C2", "C2", "C#2", "C2"][k % 4], 0.45, 0.4), a + k * 0.5)
pon(M, cuerdas(["C3", "F#3", "C4"], b - a, 0.06, 1500), a)
ln = li("mesas", "narra")
for d in (0.3, 0.9, 1.5): pon(FX, tono(hz("A6"), 0.8, 5, (1, .5), 0.08), ln["ini"] + d, 1, 0.3)
pon(FX, golpe(300, 0.2, 0.25), ln["ini"] + 2.6); pon(FX, ruido(0.15, 1500, 8000, 0.08), ln["ini"] + 2.62)
pon(FX, golpe(90, 0.5, 0.5), ln["ini"] + 5.0)
# --- espejo: casi silencio; la tarjeta sale de la manga y suena la campana de la cocina
a, b = E["espejo"]
pon(M, cuerdas(["C2", "G2"], b - a, 0.14, 600), a)
o3 = li("espejo", "orbi")
n = int(0.25 * SR); tl = np.arange(n) / SR; pon(FX, hp(rng.standard_normal(n), 1200) * np.sin(np.pi * tl / tl[-1]) * 0.18, o3["ini"] - 0.6)
pon(FX, golpe(160, 0.18, 0.6), o3["ini"] - 0.35); golpecito(o3["ini"] - 0.33, 0.4, 1600)
pon(FX, tono(hz("E6"), 1.6, 2.5, g=0.25), o3["fin"] - 0.1); pon(FX, tono(hz("B6"), 1.6, 2.5, g=0.15), o3["fin"] - 0.05)
# --- acción: el restaurante cobra vida, jazz en mayor y tres «ding» de pedidos
a, b = E["accion"]
jazz(a, b, 96, ("C2", "E2", "G2", "A2", "F1", "A1", "C2", "D2", "G1", "B1", "D2", "F2"), (("C3", "E3", "G3", "B3"), ("F2", "A2", "C3", "E3"), ("G2", "B2", "D3", "F3")), 1.0)
melodia(a + 0.3, [("E5", .4), ("G5", .4), ("A5", .8), ("G5", .4), ("E5", .4), ("D5", .8), ("C5", 1.2)], 0.06)
ac = li("accion", "narra")
for i in range(3): pon(FX, tono(hz(["C6", "E6", "G6"][i]), 0.9, 4, (1, .4), 0.14), ac["ini"] + 4.1 + i * 0.45)
for i in range(3): golpecito(ac["ini"] + 2.9 + i * 0.5, 0.12, 4200)
# --- final: retrovisor, luces que pasan, el saxo cierra
a, b = E["final"]
trafico(a, b, 0.035)
melodia(a + 0.2, [("G4", .5), ("A#4", .5), ("C5", 1.6)], 0.08); pon(M, piano(("C3", "G3", "D#4"), 2.6, 0.06), a + 0.2)
for d in (0.5, 1.6, 2.4): pon(FX, ruido(0.8, 200, 2000, 0.05) * np.sin(np.linspace(0, np.pi, int(0.8 * SR))), a + d)
# --- sello
a, b = E["sello"]
pon(FX, tono(hz("E6"), 2.0, 2, g=0.25), a + 1.0); pon(FX, tono(hz("B6"), 2.0, 2, g=0.15), a + 1.05)
pon(M, piano(("C3", "G3", "B3", "E4", "A4"), 3.0, 0.1), a + 0.1); melodia(a + 0.1, [("G4", .4), ("E5", .4), ("D5", 2.0)], 0.08)
if os.getenv("SIN_MUSICA"): M[:] = 0
# --- voces
for l in LIN["lineas"]:
    sr, v = wavfile.read(W_ + f"voces/l{l['i']:02d}.wav"); v = v.astype(float) / 32767
    pon(VZ, v if v.ndim == 1 else v.mean(1), l["ini"], 1.0, {}.get(l["quien"], 0))
# Mezcla: la música baja cuando alguien habla
activo = np.convolve((np.abs(VZ[:, 0]) > 0.02).astype(float), np.ones(int(0.25 * SR)) / int(0.25 * SR), "same")
ducking = 1 - 0.55 * np.clip(activo * 4, 0, 1)
ir = rng.standard_normal(int(1.0 * SR)) * np.exp(-np.linspace(0, 8, int(1.0 * SR))) * 0.03
for buf in (M, FX):
    for c in range(2): buf[:, c] += fftconvolve(buf[:, c], ir)[:N] * 0.5
mez = M * ducking[:, None] * 1.0 + FX * 0.9 + VZ * 1.6
mez *= np.minimum(1, (DUR - t) / 0.8)[:, None]
mez /= np.max(np.abs(mez)) / 0.92
wavfile.write(W_ + ("sonido_sin_musica.wav" if os.getenv("SIN_MUSICA") else "sonido.wav"), SR, (mez * 32767).astype(np.int16)); print("sonido listo")
