"""Banda sonora cinematográfica sintetizada, ajustada a la línea de tiempo: python musica.py play|domicilios <carpeta_voz> <salida.wav>
Capas: colchón grave (drone), latido en el problema, subida antes de cada revelación, impacto con cola larga, destellos en las funciones y acorde final."""
import sys, os, numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.io import wavfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import linea
PROD, CV, SAL = sys.argv[1], sys.argv[2], sys.argv[3]
L = {e["id"]: e for e in linea.linea(PROD, CV)}
FIN = list(L.values())[-1]["fin"]
SR = 48000; N = int((FIN + 2) * SR); t = np.arange(N) / SR
rng = np.random.default_rng(7)
def hz(nota):  # 'D2' → Hz
    n = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}
    return 440 * 2 ** ((n[nota[:-1]] + (int(nota[-1]) - 4) * 12) / 12)
def lp(x, f, o=2): return sosfilt(butter(o, f, "low", fs=SR, output="sos"), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, "high", fs=SR, output="sos"), x)
def env(a, b, sube=1.5, baja=2.0):  # envolvente suave entre a y b (s)
    e = np.zeros(N); i0, i1 = int(a * SR), int(b * SR)
    e[i0:i1] = 1
    k = int(sube * SR); e[i0:i0 + k] *= np.linspace(0, 1, len(e[i0:i0 + k])) ** 2
    k2 = int(baja * SR); e[max(i1 - k2, i0):i1] *= np.linspace(1, 0, len(e[max(i1 - k2, i0):i1])) ** 2
    return e
def sierra(f, fase=0.0): return 2 * ((f * t + fase) % 1) - 1
def ir(seg=4.0, brillo=6000):  # reverberación sintética
    n = int(seg * SR); x = rng.standard_normal(n) * np.exp(-np.linspace(0, 7, n))
    return lp(x, brillo) * 0.02
REV = ir()
izq = np.zeros(N); der = np.zeros(N)
def suma(x, pan=0.0, g=1.0):
    global izq, der
    izq += x * g * (1 - pan) / 2 * 2 ** 0.5; der += x * g * (1 + pan) / 2 * 2 ** 0.5

rev_, fut, fin_, cont = L["revelacion"], L["futuro"], L["final"], L["contacto"]
hit1 = rev_["voz"] + rev_["dur_voz"] * 0.62          # «… Apex Play»
hit2 = fin_["voz"] - 0.15                            # logo final

# 1) Colchón grave: re menor antes de la revelación, re mayor/luminoso después
def acorde(notas, a, b, g, corte):
    x = sum(sierra(hz(n) * d, rng.random()) for n in notas for d in (0.997, 1.003))
    return lp(x, corte, 4) * env(a, b, 3.0, 3.0) * g
oscuro = acorde(["D2", "A2", "D3", "F3"], 0.0, hit1 + 0.4, 0.17, 700)
claro = acorde(["D2", "A2", "D3", "F#3", "A3"], hit1 - 0.2, cont["fin"] + 1.5, 0.14, 1100)
suma(oscuro, -0.1); suma(claro, 0.1)
# 2) Latido en el problema (cada 0,95 s, cada vez más fuerte)
p = L["problema"]
for i, tt in enumerate(np.arange(p["ini"], rev_["ini"] + 1.0, 0.95)):
    i0 = int(tt * SR); n = int(0.5 * SR); tl = np.arange(n) / SR
    golpe = np.sin(2 * np.pi * (55 * np.exp(-tl * 8) + 38) * tl) * np.exp(-tl * 9) * (0.25 + 0.06 * i)
    seg = np.zeros(N); seg[i0:i0 + n] = golpe[:len(seg[i0:i0 + n])]; suma(seg, 0, 1.0)
# 3) Subidas (ruido que se abre + tono que sube) antes de cada impacto
def subida(fin, largo=3.2, g=0.22):
    a = fin - largo; i0, i1 = int(a * SR), int(fin * SR); n = i1 - i0; tl = np.arange(n) / SR
    ruido = hp(rng.standard_normal(n), 300) * np.linspace(0, 1, n) ** 3
    ruido = sosfilt(butter(2, 9000, "low", fs=SR, output="sos"), ruido)
    tono = np.sin(2 * np.pi * np.cumsum(np.linspace(110, 880, n)) / SR) * np.linspace(0, 1, n) ** 2 * 0.3
    seg = np.zeros(N); seg[i0:i1] = (ruido * 0.5 + tono) * g; suma(seg, 0)
# 4) Impacto: bombo sub + golpe de ruido + cola larga
def impacto(tt, g=1.0):
    i0 = int(tt * SR); n = int(5 * SR); tl = np.arange(n) / SR
    sub = np.sin(2 * np.pi * (48 * np.exp(-tl * 3) + 28) * tl) * np.exp(-tl * 1.6)
    golpe = lp(rng.standard_normal(n), 2500) * np.exp(-tl * 14)
    x = (sub * 0.9 + golpe * 0.35) * g
    seg = np.zeros(N); seg[i0:i0 + n] = x[:len(seg[i0:i0 + n])]; suma(seg, 0)
    cola = fftconvolve(seg, REV)[:N] * 1.4; suma(cola, -0.3, 0.6); suma(cola, 0.3, 0.6)
subida(hit1); impacto(hit1); subida(hit2, 2.6, 0.18); impacto(hit2, 0.85)
# 5) Destellos: notas de campana suaves durante las funciones (entre la revelación y el futuro)
notas = ["D5", "A4", "F#5", "E5", "A5", "D5", "F#5", "C#6"]
destellos = np.zeros(N); paso = 60 / 96 * 2
for i, tt in enumerate(np.arange(hit1 + 2.0, fut["ini"], paso)):
    f = hz(notas[i % len(notas)]); i0 = int(tt * SR); n = int(2.5 * SR); tl = np.arange(n) / SR
    x = (np.sin(2 * np.pi * f * tl) + 0.3 * np.sin(2 * np.pi * f * 2.01 * tl)) * np.exp(-tl * 2.2) * 0.13
    destellos[i0:i0 + n] += x[:len(destellos[i0:i0 + n])]
destellos = destellos + fftconvolve(destellos, REV)[:N] * 0.9
suma(destellos, 0.35)
# 6) Futuro: pulso que crece (corcheas graves) hasta el final
for i, tt in enumerate(np.arange(fut["ini"], hit2 - 0.3, 60 / 96 / 2)):
    i0 = int(tt * SR); n = int(0.22 * SR); tl = np.arange(n) / SR
    x = sierra(hz("D2"))[:n] * 0 + np.sign(np.sin(2 * np.pi * hz("D2") * tl)) * np.exp(-tl * 18)
    x = lp(x, 900) * (0.03 + 0.07 * (tt - fut["ini"]) / max(1, hit2 - fut["ini"]))
    seg = np.zeros(N); seg[i0:i0 + n] = x[:len(seg[i0:i0 + n])]; suma(seg, 0)
subida(hit2 - 0.05, 4.5, 0.12)
# 7) Acorde final brillante con cola
fin_acorde = acorde(["D3", "A3", "D4", "F#4", "A4"], hit2, cont["fin"] + 1.8, 0.1, 3000)
suma(fin_acorde + fftconvolve(fin_acorde, REV)[:N] * 0.5, 0.0)

mezcla = np.stack([izq, der], 1)
mezcla *= env(0, FIN + 1.8, 0.8, 2.5)[:, None]
mezcla /= np.max(np.abs(mezcla)) / 0.89
wavfile.write(SAL, SR, (mezcla * 32767).astype(np.int16))
print("música", round(N / SR, 1), "s · impactos en", round(hit1, 2), round(hit2, 2))
