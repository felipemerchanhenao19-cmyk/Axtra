"""Música, efectos y voces de «Viernes, 8 p. m.»: python sonido.py <carpeta_trabajo>  →  sonido.wav"""
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
# --- calma: bossa suave + silbido de Julián
a, b = E["calma"]
patron(M, a, b + 0.2, 128, ["E3", "B3", "G#3", "B3", "A2", "C#4", "E3", "C#4"], 0.10, 7)
for i, (nota, d) in enumerate([("B5", .3), ("G#5", .3), ("E5", .5), ("F#5", .3), ("G#5", .6)]):
    n = int(d * SR); tl = np.arange(n) / SR
    pon(FX, np.sin(2 * np.pi * hz(nota) * (1 + 0.012 * np.sin(2 * np.pi * 6 * tl)) * tl) * np.sin(np.linspace(0, np.pi, n)) * 0.12, a + 0.4 + sum(x[1] for x in [("B5", .3), ("G#5", .3), ("E5", .5), ("F#5", .3), ("G#5", .6)][:i]))
# --- avalancha: campana de la puerta, golpes por cliente, música frenética y murmullo
a, b = E["avalancha"]
pon(FX, tono(hz("E6"), 1.2, 3, g=0.3), a + 0.05); pon(FX, tono(hz("C6"), 1.4, 3, g=0.3), a + 0.3)
for l in LIN["lineas"]:
    if l["esc"] == "avalancha" and l["quien"].startswith("c"): pon(FX, tono(hz("A5"), 0.4, 9, g=0.12), l["ini"] - 0.45)
patron(M, a + 0.4, b, 172, ["D4", "F4", "A4", "D5", "C#5", "A4", "F4", "E4"], 0.11, 14, (1, .5, .2))
pon(M, ruido(b - a, 300, 2500, 0.03) * np.minimum(1, np.arange(int((b - a) * SR)) / SR / 1.0), a)
# --- papel: aparición cómica, hojas, zumbido de error
a, b = E["papel"]
n = int(0.5 * SR); tl = np.arange(n) / SR; pon(FX, np.sin(2 * np.pi * np.cumsum(220 + 500 * tl) / SR) * np.exp(-tl * 5) * 0.25, a + 0.05)
patron(M, a + 0.6, b, 110, ["G2", "D3", "G2", "A#2", "C3", "D3", "F2", "C3"], 0.13, 7, (1, .6, .4, .2))
for k in range(8): pon(FX, ruido(0.18, 1500, 7000, 0.04), a + 1.0 + k * 0.6)
err = [l for l in LIN["lineas"] if l["esc"] == "papel" and l["quien"] == "c3"]
if err: n = int(0.5 * SR); tl = np.arange(n) / SR; pon(FX, lp(np.sign(np.sin(2 * np.pi * 110 * tl)), 1200) * 0.12, err[0]["ini"] - 0.55)
# --- derrota: todo se apaga, violín triste
a, b = E["derrota"]
pon(FX, ruido(0.6, 200, 3000, 0.08) * np.linspace(1, 0, int(0.6 * SR)), a)
for i, (nota, d) in enumerate([("A4", .6), ("G4", .5), ("F4", .6), ("E4", .9)]): pon(M, cuerdas([nota], d + 0.2, 0.22, 3000), a + 0.3 + sum([.6, .5, .6, .9][:i]))
pon(M, cuerdas(["D3", "F3", "A3"], b - a, 0.08), a)
# --- aparece: brillo mágico, coro y campanita
a, b = E["aparece"]
for k in range(16): pon(FX, tono(hz("C6") * 2 ** (k / 12), 0.6, 6, g=0.05), a + 0.6 + k * 0.05)
pon(FX, tono(hz("E6"), 2.0, 2, g=0.3), a + 0.8); pon(FX, golpe(70, 1.0, 0.4), a + 0.8)
pon(M, cuerdas(["C4", "E4", "G4", "B4"], b - a, 0.10, 3500), a + 0.6)
# --- atiende: ritmo alegre (swing) y un «ding» por cada pedido en cocina
a, b = E["atiende"]
patron(M, a, b, 132, ["C4", "E4", "G4", "A4", "F4", "A4", "C5", "A4", "G4", "B4", "D5", "B4"], 0.10, 10)
patron(M, a, b, 132, ["C2", "C2", "F2", "G2"], 0.16, 6, (1, .4), 0, 4)
for tt in (0.12, 0.32, 0.5, 0.72): pon(FX, tono(hz("E6"), 0.7, 6, g=0.18), a + (b - a) * tt)
# --- protesta: rayón de disco y la libreta que se cierra
a, b = E["protesta"]
patron(M, a, b - 1.2, 132, ["C4", "E4", "G4", "A4"], 0.07, 10)
sh = [l for l in LIN["lineas"] if l["esc"] == "protesta" and l["quien"] == "orbi"]
if sh:
    s0 = sh[0]["ini"]; n = int(0.4 * SR); tl = np.arange(n) / SR
    pon(FX, lp(rng.standard_normal(n), 3000) * np.sin(2 * np.pi * 8 * tl) * np.exp(-tl * 5) * 0.3, s0 - 0.45)
    pon(FX, golpe(90, 0.5, 0.7), s0 + 0.35)
# --- final y sello
a, b = E["final"]; pon(M, cuerdas(["C3", "G3", "C4", "E4"], b - a + 0.3, 0.1), a)
a, b = E["sello"]; pon(FX, tono(hz("E6"), 2.0, 2, g=0.3), a); pon(FX, tono(hz("B6"), 2.0, 2, g=0.2), a + 0.05)
pon(M, cuerdas(["C3", "G3", "C4", "E4", "G4"], b - a + 0.3, 0.16, 2800), a)
# --- voces
for l in LIN["lineas"]:
    sr, v = wavfile.read(W_ + f"voces/l{l['i']:02d}.wav"); v = v.astype(float) / 32767
    pon(VZ, v if v.ndim == 1 else v.mean(1), l["ini"], 1.0, {"c1": .3, "c2": -.3, "c3": -.3, "c4": .3, "papel": -.15}.get(l["quien"], 0))
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
