"""Animación cuadro a cuadro (stop-motion, 12 imágenes por segundo) con las imágenes que crea el cliente.
  python cuadro_a_cuadro.py <id>                 →  entregables/redes/minifiguras/<id>/<id>.mp4 (+ sin música y liviano)
  PRUEBA=planos python cuadro_a_cuadro.py <id>   →  un cuadro por toma
Para que la imagen no «tiemble», de cada variante (boca, ojos) solo se toma lo que cambia dentro de una zona y se pega sobre la base.
La boca se elige cuadro a cuadro con el volumen real de la voz: cerrada, media o abierta."""
import sys, os, re, json, asyncio, subprocess
import numpy as np
from PIL import Image, ImageFilter
from scipy.io import wavfile
import animatica
from guiones import GUIONES
motor, AQUI = animatica.motor, animatica.AQUI
FPS_CC = 12

def t_clave(k, L):
    """Segundos desde el inicio de la toma: número, "l0" (inicio de la línea 0), "f0" (fin), "l0+0.5"."""
    if isinstance(k, (int, float)): return float(k)
    m = re.match(r"^([lf])(\d+)([+-][\d.]+)?$", k); l = L["lineas"][int(m.group(2))]
    return (l["ini"] if m.group(1) == "l" else l["fin"]) - L["ini"] + (float(m.group(3)) if m.group(3) else 0)

def discreto(spec, t, L):
    if not isinstance(spec, list): return spec
    v = spec[0][1]
    for k, x in spec:
        if t_clave(k, L) <= t: v = x
    return v

def abrir(W, clave): return Image.open(W + clave).convert("RGB")

def componer(W, base, var, zona, nombre):
    """Pega sobre la base solo lo que cambia entre base y variante, dentro de la zona [x0, y0, x1, y1], con borde suave."""
    a, b = np.asarray(abrir(W, base), float), np.asarray(abrir(W, var), float)
    d = np.abs(a - b).sum(2); m = np.zeros_like(d); x0, y0, x1, y1 = zona; m[y0:y1, x0:x1] = (d[y0:y1, x0:x1] > 45).astype(float)
    mi = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(17)).filter(ImageFilter.GaussianBlur(5))
    m = np.asarray(mi, float)[..., None] / 255
    caja = np.zeros_like(m); caja[y0:y1, x0:x1] = 1; caja = np.asarray(Image.fromarray((caja[..., 0] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(8)), float)[..., None] / 255
    m = m * caja; os.makedirs(W + "cc", exist_ok=True)
    Image.fromarray((a * (1 - m) + b * m).astype(np.uint8)).save(W + "cc/" + nombre + ".jpg", quality=93)
    return "cc/" + nombre + ".jpg"

def paneles(W, g):
    """Recortes de imágenes con varios paneles: {clave: [archivo, [x0, y0, x1, y1]]}."""
    os.makedirs(W + "cc", exist_ok=True)
    for k, (f, caja) in g.get("paneles", {}).items():
        Image.open(W + f).convert("RGB").crop(caja).save(W + "cc/" + k + ".jpg", quality=95)

def envolventes(lin, W):
    for L in lin["planos"]:
        for l in L["lineas"]:
            sr, x = wavfile.read(W + f"voces/l{l['k']:02d}.wav"); x = x.astype(float); x = x if x.ndim == 1 else x.mean(1)
            n = sr // 30; rms = np.array([np.sqrt(np.mean(x[i:i + n] ** 2)) for i in range(0, len(x), n)]); rms = rms / (np.percentile(rms, 92) + 1e-9)
            l["env"] = [round(float(min(1, max(0, (v - 0.12) * 1.25))), 2) for v in np.convolve(rms, [0.25, 0.5, 0.25], "same")]

def plan(W, g, lin):
    planes = []
    for j, (tm, L) in enumerate(zip(g["tomas"], lin["planos"])):
        dur = L["fin"] - L["ini"]; pasos = int(np.ceil(dur * FPS_CC)) + 1; out = []
        bo, oj = tm.get("bocas"), tm.get("ojos")
        poses = tm.get("poses", tm.get("imagen"))
        cache = {}
        def comp(base, var, zona, etiqueta):
            k = (base, var, etiqueta)
            if k not in cache: cache[k] = componer(W, base, var, zona, f"t{j}_{len(cache)}_{etiqueta}")
            return cache[k]
        for s in range(pasos):
            t = s / FPS_CC; ab = L["ini"] + t; img = discreto(poses, t, L)
            if bo and img == bo.get("sobre", img) and (bo.get("solo") is None or img in bo["solo"]):
                v = 0
                for l in L["lineas"]:
                    if (l["quien"] == bo["quien"] or l["quien"].startswith(bo["quien"] + "_")) and l["ini"] <= ab < l["fin"]:
                        e = l["env"]; v = e[min(len(e) - 1, int((ab - l["ini"]) * 30))]
                if v > 0.45 and bo.get("abierta"): img = comp(img, bo["abierta"], bo["zona"], "abierta")
                elif v > 0.12 and bo.get("media"): img = comp(img, bo["media"], bo["zona"], "media")
                elif oj and (ab + j * 0.7) % 3.4 < 0.17: img = comp(img, oj["img"], oj["zona"], "ojos")
            elif oj and img == oj.get("sobre", img) and (ab + j * 0.7) % 3.4 < 0.17: img = comp(img, oj["img"], oj["zona"], "ojos")
            out.append([round(t, 3), img])
        planes.append(out)
    return planes

def hacer(gid):
    g = GUIONES[gid]; ep = dict(g, planos=g["tomas"], marcaAgua=False); W = motor.TRABAJO + "cc_" + gid + "/"; os.makedirs(W, exist_ok=True)
    lin = asyncio.run(motor.voces(ep, W)); envolventes(lin, W); json.dump(lin, open(W + "linea.json", "w"), ensure_ascii=False)
    animatica.pagina(ep, lin, W, [])          # copia modelos/ y cuadros/ a la carpeta de trabajo
    paneles(W, g); pl = plan(W, g, lin); animatica.pagina(ep, lin, W, pl)
    if os.getenv("PRUEBA"):
        ts = [round(p["ini"] + (p["fin"] - p["ini"]) * 0.5, 2) for p in lin["planos"]]
        asyncio.run(motor.prueba(W, ts)); print("pruebas en", W, ts); return
    motor.sonido(ep, lin, W); asyncio.run(motor.imagen(W, lin["dur"]))
    d = animatica.SALIDA + gid + "/"; os.makedirs(d, exist_ok=True)
    for son, nombre, extra in (("sonido.wav", f"{gid}.mp4", ["-crf", "19"]), ("sonido_sin_musica.wav", f"{gid}-sin-musica.mp4", ["-crf", "19"]),
                               ("sonido.wav", f"{gid}-liviano.mp4", ["-crf", "27", "-vf", "scale=720:-2"])):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", W + "imagen.mp4", "-i", W + son, "-c:v", "libx264", "-preset", "slow", *extra, "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", d + nombre], check=True)
    print("listo", d, lin["dur"], "s")

if __name__ == "__main__":
    hacer(sys.argv[1])
