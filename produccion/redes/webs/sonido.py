"""Música, efectos y voces de «Apex · Páginas web»: python sonido.py <carpeta_trabajo>  →  sonido.wav"""
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
def zas(a, d=0.6, g=0.12):
    n = int(d * SR); tl = np.arange(n) / SR; pon(FX, lp(hp(rng.standard_normal(n), 600), 6000) * np.sin(np.pi * tl / d) ** 2 * g, a - d * 0.6, 1, 0)
def pulso(ini, fin, bpm, g=0.5):
    neg = 60 / bpm; tt = ini; k = 0
    while tt < fin - 0.05:
        pon(M, golpe(48, 0.45, 0.45 * g), tt)
        if k % 2: golpecito(tt, 0.05 * g, 6500)
        tt += neg; k += 1
def arpegio(ini, fin, notas, paso=0.25, g=0.05):
    tt = ini; k = 0
    while tt < fin - 0.05: pon(M, tono(hz(notas[k % len(notas)]), 1.2, 3.5, (1, .4, .15), g), tt, 1, 0.3 * np.sin(k)); tt += paso; k += 1
# --- gancho: zumbido y clic de error
a, b = E["gancho"]
pon(M, cuerdas(["A2", "E3", "A3"], b - a + 0.3, 0.12, 900), a)
for d in (0.3, 0.42): golpecito(a + d, 0.25, 900)
# --- marca: golpe y acorde abierto
a, b = E["marca"]
zas(a); pon(FX, golpe(38, 2.0, 0.9), a); pon(M, cuerdas(["D3", "A3", "D4", "F#4"], b - a + 0.6, 0.18, 2600), a)
pon(FX, tono(hz("E6"), 1.8, 2.5, g=0.12), a + 0.2)
# --- software y webs: pulso y arpegio
a = E["software"][0]; b = E["funciones"][1]
zas(a); zas(E["webs"][0]); zas(E["funciones"][0])
pulso(a, b, 100, 0.8)
arpegio(a, b, ["D4", "F#4", "A4", "D5", "B3", "D4", "F#4", "B4", "G3", "B3", "D4", "G4", "A3", "C#4", "E4", "A4"], 0.3, 0.045)
pon(M, cuerdas(["D3", "A3", "F#4"], b - a, 0.07, 1800), a)
for i in range(3): pon(FX, tono(hz(["A5", "C#6", "E6"][i]), 0.6, 6, (1, .4), 0.1), E["funciones"][0] + 0.9 + i * 0.9)
# --- precio: subida y brillo en «$99.000»
a, b = E["precio"]
zas(a); pon(M, cuerdas(["B2", "F#3", "D4"], 3.2, 0.1, 1600), a)
n = int(1.6 * SR); tl = np.arange(n) / SR; pon(FX, hp(rng.standard_normal(n), 2000) * (tl / tl[-1]) ** 2 * 0.1, a + 1.7)
pon(FX, golpe(40, 2.0, 1.0), a + 3.2); pon(M, cuerdas(["D3", "A3", "D4", "F#4", "A4"], b - a - 3.0, 0.2, 3000), a + 3.2)
for k in range(10): pon(FX, tono(hz("A6") * (1 + 0.06 * k), 0.5, 6, (1,), 0.04), a + 4.8 + k * 0.05)
pulso(a + 3.2, b, 100, 0.9)
# --- cierre: acorde final
a, b = E["cierre"]
zas(a); pon(FX, golpe(36, 2.5, 0.8), a); pon(M, piano(("D3", "A3", "D4", "F#4", "A4"), 4.0, 0.1), a + 0.1)
pon(M, cuerdas(["D3", "A3", "F#4", "A4"], b - a + 0.3, 0.12, 2600), a)
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
