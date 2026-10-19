"""Música, efectos y voces de «Orbi · Mark I»: python sonido.py <carpeta_trabajo>  →  sonido.wav"""
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
def servo(a, d=0.6, f0=300, f1=900, g=0.06):
    n = int(d * SR); tl = np.arange(n) / SR; f = f0 + (f1 - f0) * np.sin(np.pi * tl / d / 2)
    pon(FX, lp(2 * ((np.cumsum(f) / SR) % 1) - 1, 2500) * np.sin(np.pi * tl / d) * g, a, 1, rng.uniform(-.4, .4))
def clank(a, g=0.4): pon(FX, golpe(220, 0.4, g), a); pon(FX, tono(1800, 0.5, 9, (1, .7, .5, .4), g * 0.25) + tono(2730, 0.5, 11, (1, .5), g * 0.15), a)
def bombo(a, g=0.6): pon(M, golpe(52, 0.5, g), a)
def caja(a, g=0.25): n = int(0.22 * SR); tl = np.arange(n) / SR; pon(M, (hp(rng.standard_normal(n), 1200) * np.exp(-tl * 18) + np.sin(2 * np.pi * 190 * tl) * np.exp(-tl * 25) * 0.5) * g, a)
def sierra(notas, d, g=0.08, corte=1400):
    n = int(d * SR); tl = np.arange(n) / SR; x = np.zeros(n)
    for nota in notas:
        for dd in (0.995, 1.005): x += 2 * ((hz(nota) * dd * tl + rng.random()) % 1) - 1
    return lp(np.tanh(x * 1.6), corte) * g * np.minimum(1, tl / 0.02) * np.minimum(1, (d - tl) / 0.15)
def ritmo(ini, fin, bpm, acordes, g=1.0):
    neg = 60 / bpm; k = 0; tt = ini
    while tt < fin - 0.05:
        if k % 2 == 0: bombo(tt, 0.55 * g)
        if k % 4 == 2: caja(tt, 0.22 * g)
        golpecito(tt + neg / 2, 0.03 * g, 7000)
        if k % 4 == 0: pon(M, sierra(acordes[(k // 4) % len(acordes)], neg * 3.9, 0.07 * g), tt)
        pon(M, bajo(acordes[(k // 4) % len(acordes)][0][:-1] + "2", neg * 0.9, 0.35 * g), tt)
        tt += neg; k += 1
# --- gancho: alarma
a, b = E["gancho"]
for k in range(5): pon(FX, tono(880 if k % 2 == 0 else 660, 0.22, 4, (1, .5, .3), 0.12), a + k * 0.45)
pon(M, cuerdas(["D2", "A2", "D#3"], b - a, 0.2, 900), a)
# --- título: golpe grande y barrido metálico
a, b = E["titulo"]
pon(FX, golpe(34, 2.5, 1.0), a); clank(a, 0.5); n = int(1.6 * SR); tl = np.arange(n) / SR
pon(FX, hp(rng.standard_normal(n), 3000) * (tl / tl[-1]) ** 2 * 0.08, a + 0.4); pon(M, sierra(["D3", "A3", "D4"], b - a, 0.09, 1800), a + 0.2)
# --- taller: ambiente elegante, piano y pads
a, b = E["taller"]
n = int((E["traje"][1] - a) * SR); pon(FX, lp(rng.standard_normal(n), 120) * 0.04, a)
for i, ac in enumerate([("D3", "F3", "A3", "E4"), ("A#2", "D3", "F3", "A3"), ("C3", "E3", "G3", "D4"), ("A2", "C#3", "E3", "G3")]): pon(M, piano(ac, 2.2, 0.07), a + 0.2 + i * 1.75)
pon(M, cuerdas(["D3", "A3", "F4"], b - a, 0.06, 1500), a)
for k in range(8): pon(FX, tono(hz("A6") * (1 + 0.12 * (k % 3)), 0.12, 20, (1,), 0.03), a + 0.6 + k * 0.8)
# --- traje: servos, piezas, reactor y visor
a, b = E["traje"]
ritmo(a + 0.9, b, 100, [["D3", "A3", "D4"], ["A#2", "F3", "A#3"], ["C3", "G3", "C4"], ["A2", "E3", "A3"]], 0.8)
for x in (0.4, 1.0, 1.6, 2.2, 2.8, 3.4): servo(a + x, 0.5, 250 + 50 * x, 900)
for x in (1.6, 2.8, 4.0): clank(a + x, 0.55)
n = int(1.2 * SR); tl = np.arange(n) / SR; pon(FX, np.sin(2 * np.pi * np.cumsum(120 + 900 * tl / tl[-1]) / SR) * np.minimum(1, tl / 0.1) * np.exp(-np.maximum(0, tl - 0.9) * 8) * 0.12, a + 4.4)
pon(FX, tono(hz("E6"), 1.5, 2.5, g=0.18), a + 5.4)
servo(a + 6.4, 0.35, 600, 1400, 0.08); clank(a + 6.75, 0.7); pon(FX, golpe(40, 1.6, 0.9), a + 6.75)
for k in range(3): pon(FX, tono(hz("E6") * (1 + k * 0.25), 0.2, 10, (1,), 0.06), a + 6.9 + k * 0.1)
# --- vuelo: propulsores y música épica
a, b = E["vuelo"]
n = int((b - a + 0.2) * SR); tl = np.arange(n) / SR; pon(FX, lp(hp(rng.standard_normal(n), 300), 3000) * (0.12 + 0.05 * np.sin(2 * np.pi * 0.7 * tl)) * np.minimum(1, tl / 0.4), a)
ritmo(a, b, 120, [["D3", "A3", "D4"], ["F3", "C4", "F4"], ["C3", "G3", "C4"], ["A#2", "F3", "A#3"]], 1.0)
s_ = li("vuelo", "sofia")
for k in range(14): pon(FX, tono(hz("C7"), 0.08, 30, (1,), 0.05), s_["ini"] + k * (s_["fin"] - s_["ini"]) / 14)
# --- mesas: cada mesa conectada suena
a, b = E["mesas"]
ritmo(a, b, 120, [["D3", "A3", "D4"], ["F3", "C4", "F4"], ["G3", "D4", "G4"], ["A3", "E4", "A4"]], 0.85)
for i in range(4): pon(FX, tono(hz(["C6", "E6", "G6", "C7"][i]), 0.8, 4, (1, .4), 0.14), a + 0.4 + (i + 1) * 4.4 / 5)
# --- aterriza: caída, impacto, silencio y la frase
a, b = E["aterriza"]
n = int(0.6 * SR); tl = np.arange(n) / SR; pon(FX, hp(rng.standard_normal(n), 800) * (tl / tl[-1]) ** 2 * 0.2, a)
pon(FX, golpe(32, 2.5, 1.0), a + 0.6); clank(a + 0.6, 0.6); pon(FX, ruido(0.8, 80, 1200, 0.25), a + 0.62)
ol = li("aterriza", "orbi"); servo(ol["ini"] - 0.7, 0.4, 900, 400, 0.07)
pon(M, sierra(["D3", "A3", "D4", "F#4"], 2.2, 0.08, 2200), ol["fin"] + 0.05); pon(FX, golpe(45, 1.4, 0.7), ol["fin"] + 0.05)
# --- sello
a, b = E["sello"]
pon(M, piano(("D3", "A3", "D4", "F#4", "A4"), 3.2, 0.1), a + 0.3); pon(FX, tono(hz("E6"), 2.0, 2, g=0.2), a + 1.3)
servo(a + 0.4, 0.4, 900, 400, 0.05)
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
