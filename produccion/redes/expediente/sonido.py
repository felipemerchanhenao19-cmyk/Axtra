"""Música, efectos y voces de «Expediente 27»: python sonido.py <carpeta_trabajo>  →  sonido.wav"""
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
LI = {l["esc"] + l["quien"]: l for l in LIN["lineas"]}
RAYOS = [(0.35, 1), (1.9, 0.8), (E["callejon"][0] + 0.15, 0.7), (E["revela"][0], 1)]
# --- ambiente: lluvia afuera fuerte, adentro apagada; al amanecer ya no llueve
lluvia(0, E["titulo"][1] + 0.3, 0.05); lluvia(E["oficina"][0], E["cliente"][1], 0.035, 1100); lluvia(E["pistas"][0], E["pistas"][1], 0.02, 900)
lluvia(E["callejon"][0] - 0.2, E["revela"][1], 0.06); lluvia(E["sello"][0], DUR, 0.03)
for a, f in RAYOS: trueno(a + 0.25, 0.6 * f)
# --- título: máquina de escribir (13 letras) y timbre del carro
a, b = E["titulo"]
for i in range(13): golpecito(a + 0.5 + i * 1.1 / 13 + rng.uniform(0, 0.02), 0.35)
pon(FX, tono(hz("A6"), 1.2, 4, (1, .5), 0.18), a + 1.65)
pon(M, sax("D4", 0.5, 0.11), a + 0.6); pon(M, sax("F4", 0.5, 0.11), a + 1.1); pon(M, sax("A4", 1.3, 0.12), a + 1.6); pon(M, piano(("D3", "F3", "A3", "C4"), 2.5, 0.07), a + 1.6)
# --- oficina: ventilador, jazz lento y un saxo que cuenta la ciudad
a, b = E["oficina"]
n = int((E["cliente"][1] - a) * SR); tl = np.arange(n) / SR; pon(FX, lp(rng.standard_normal(n), 180) * (0.6 + 0.4 * np.sin(2 * np.pi * 3.5 * tl)) * 0.05, a)
jazz(a, E["cliente"][1], 78)
melodia(a + 0.2, [("A4", .6), ("C5", .4), ("A4", .4), ("G4", .6), ("F4", 1.2), (None, .4), ("E4", .5), ("F4", .5), ("D4", 1.5)], 0.06)
# --- cliente: toc-toc, rechinido de puerta, pasos mojados
a, b = E["cliente"]
for d in (0.0, 0.22): pon(FX, golpe(140, 0.25, 0.35), a + d)
n = int(0.9 * SR); tl = np.arange(n) / SR; pon(FX, lp(np.sin(2 * np.pi * np.cumsum(420 + 200 * np.sin(2 * np.pi * 1.4 * tl) + 80 * rng.standard_normal(n) * 0.1) / SR) * np.exp(-((tl - 0.45) / 0.3) ** 2), 2000) * 0.07, a + 0.6)
for k in range(3): pon(FX, ruido(0.12, 300, 3000, 0.08) * np.exp(-np.arange(int(0.12 * SR)) / SR * 25), a + 1.0 + k * 0.32)
# --- pistas: reloj que avanza, bajo de suspenso, golpe al ver la marca
a, b = E["pistas"]
for k in range(int((b - a) / 0.5)): golpecito(a + k * 0.5, 0.06, 3200 if k % 2 else 2400)
for k in range(int((b - a) / 0.7)): pon(M, bajo(["D2", "D2", "D#2", "D2"][k % 4], 0.6, 0.4), a + k * 0.7)
pon(M, cuerdas(["D3", "G#3", "C4"], b - a, 0.07, 1600), a)
n_ = LI.get("pistasnarra")
if n_:
    for i in range(6): pon(FX, ruido(0.18, 800, 4000, 0.05), n_["ini"] + 3.0 + i * 0.12)   # rotulador rojo
    pon(FX, golpe(48, 1.6, 0.9), n_["ini"] + 3.7); pon(M, cuerdas(["D3", "D#4", "A4"], 1.8, 0.25, 2600), n_["ini"] + 3.7)
# --- callejón: clic de linterna, pasos en charcos, la sombra
a, b = E["callejon"]
golpecito(a + 0.4, 0.4, 1800); golpecito(a + 0.45, 0.3, 1200)
for k in range(5): pon(FX, ruido(0.16, 400, 5000, 0.06) * np.exp(-np.arange(int(0.16 * SR)) / SR * 18), a + 0.7 + k * 0.42, 1, 0.2 * (-1) ** k)
pon(M, cuerdas(["D2", "A2", "D3"], b - a, 0.12, 900), a)
for k in range(int((b - a) / 0.9)): pon(M, bajo("D2", 0.8, 0.35), a + k * 0.9)
s_ = LI.get("callejoncomi")
if s_:
    pon(M, cuerdas(["D#4", "A4", "D5"], s_["fin"] - s_["ini"] + 1.4, 0.06, 3500), s_["ini"] - 0.9)
    pon(FX, golpe(42, 2.0, 0.7), s_["ini"] - 1.0); melodia(s_["ini"] - 0.9, [("D4", .5), ("C#4", .5), ("C4", .5), ("B3", 1.2)], 0.07)
# --- revela: golpe de orquesta con el rayo, música de Apex, el derretimiento
a, b = E["revela"]
pon(M, cuerdas(["D3", "F3", "G#3", "B3", "D4"], 1.6, 0.45, 3000), a); pon(FX, golpe(38, 2.0, 1.0), a)
o_ = LI.get("revelaorbi")
if o_:
    pon(FX, tono(hz("E6"), 1.6, 2.5, g=0.22), o_["ini"] + 1.0); pon(FX, tono(hz("B6"), 1.6, 2.5, g=0.14), o_["ini"] + 1.05)
    pon(M, piano(("D3", "F#3", "A3", "D4"), 2.2, 0.08), o_["ini"] + 1.0)
c_ = LI.get("revelacomi")
if c_:
    n = int(1.4 * SR); tl = np.arange(n) / SR
    pon(FX, np.sin(2 * np.pi * np.cumsum(600 * np.exp(-tl * 2.2) + 60) / SR) * np.exp(-tl * 1.6) * 0.18, c_["ini"] + 0.1)   # se derrite
    for i in range(8): pon(FX, ruido(0.1, 2500, 9000, 0.05), c_["ini"] + 0.2 + i * 0.1)                                    # billetes
    pon(FX, golpe(70, 0.7, 0.6), c_["ini"] + 0.05)
# --- cierre: amanecer, ya no llueve; sello «CERRADO» y jazz en mayor
a, b = E["cierre"]
for k in range(4): pon(FX, tono(hz("E7") * (1 + 0.1 * (k % 2)), 0.12, 20, (1,), 0.04), a + 0.5 + k * 0.9)       # pajaritos
jazz(a, b + 0.2, 92, ("D2", "F#2", "A2", "B2", "G1", "B1", "D2", "E2", "A1", "C#2", "E2", "G2"), (("D3", "F#3", "A3", "C#4"), ("G2", "B2", "D3", "F#3"), ("A2", "C#3", "E3", "G3")), 0.9)
cn = LI.get("cierrenarra")
if cn: pon(FX, golpe(90, 0.5, 1.0), cn["ini"] + 0.25); pon(FX, ruido(0.08, 200, 3000, 0.2), cn["ini"] + 0.25)
# --- sello: máquina de escribir y frase final del saxo
a, b = E["sello"]
for i in range(13): golpecito(a + 0.3 + i * 0.6 / 13, 0.3)
pon(FX, tono(hz("A6"), 1.2, 4, (1, .5), 0.15), a + 0.95)
melodia(a + 0.2, [("A4", .35), ("B4", .35), ("D5", .35), ("F#5", .5), ("E5", 1.6)], 0.09); pon(M, piano(("D3", "F#3", "A3", "C#4", "E4"), 3.2, 0.09), a + 1.6)
# --- voces
for l in LIN["lineas"]:
    sr, v = wavfile.read(W_ + f"voces/l{l['i']:02d}.wav"); v = v.astype(float) / 32767
    pon(VZ, v if v.ndim == 1 else v.mean(1), l["ini"], 1.0, {"comi": .2, "aure": .25}.get(l["quien"], 0))
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
