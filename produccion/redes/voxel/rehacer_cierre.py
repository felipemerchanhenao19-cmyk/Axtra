"""Rehace solo la tarjeta final de capítulos ya renderizados (por ejemplo, para corregir un texto del cierre) sin volver a dibujar todo.
  python rehacer_cierre.py <id> [<id> ...]
Usa lo que dejó hacer.py en la carpeta de trabajo (imagen.mp4, sonidos y linea.json): dibuja de nuevo desde el último plano
hasta el final, lo pega a la imagen original y vuelve a exportar las tres versiones."""
import sys, os, json, asyncio, subprocess
import hacer
from episodios import EPISODIOS

async def tramo(W, a, b, salida):
    from playwright.async_api import async_playwright
    ff = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "image2pipe", "-framerate", str(hacer.FPS), "-c:v", "mjpeg", "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-pix_fmt", "yuv420p", salida], stdin=subprocess.PIPE)
    async with async_playwright() as p:
        br, pg = await hacer.abrir(p, W)
        for f in range(a, b): await pg.evaluate("t => render(t)", f / hacer.FPS); ff.stdin.write(await pg.screenshot(type="jpeg", quality=94))
        await br.close()
    ff.stdin.close(); ff.wait()

def rehacer(eid):
    W = hacer.motor.TRABAJO + "voxel_" + eid + "/"; lin = json.load(open(W + "linea.json"))
    hacer.three(); hacer.pagina(EPISODIOS[eid], lin, W)
    a, b = int(lin["planos"][-1]["ini"] * hacer.FPS), int(lin["dur"] * hacer.FPS)
    asyncio.run(tramo(W, a, b, W + "cierre.mp4"))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", W + "imagen.mp4", "-frames:v", str(a), "-c:v", "libx264", "-preset", "medium", "-crf", "15",
                    "-pix_fmt", "yuv420p", W + "cabeza.mp4"], check=True)
    open(W + "partes.txt", "w").write(f"file '{W}cabeza.mp4'\nfile '{W}cierre.mp4'\n")
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", W + "partes.txt", "-c", "copy", W + "imagen.mp4"], check=True)
    for son, nombre, extra in (("sonido.wav", f"{eid}.mp4", ["-crf", "19"]), ("sonido_sin_musica.wav", f"{eid}-sin-musica.mp4", ["-crf", "19"]),
                               ("sonido.wav", f"{eid}-liviano.mp4", ["-crf", "27", "-vf", "scale=720:-2"])):
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", W + "imagen.mp4", "-i", W + son, "-c:v", "libx264", "-preset", "slow", *extra, "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", hacer.SALIDA + nombre], check=True)
    print("cierre rehecho", eid, b - a, "cuadros", flush=True)

if __name__ == "__main__":
    for eid in sys.argv[1:]: rehacer(eid)
