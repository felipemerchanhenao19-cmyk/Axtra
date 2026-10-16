"""Mezcla final: voz en su lugar + música que se baja cuando habla el narrador, y une con la imagen.
python mezcla.py play|domicilios <carpeta_trabajo> <salida.mp4>"""
import sys, os, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import linea
PROD, W_, SAL = sys.argv[1], os.path.abspath(sys.argv[2]) + "/", sys.argv[3]
TL = linea.linea(PROD, W_ + "voz"); FIN = TL[-1]["fin"]
ins, ramas = [], []
for i, e in enumerate(TL):
    ins += ["-i", W_ + f"voz/{e['id']}.wav"]
    ms = int(e["voz"] * 1000)
    ramas.append(f"[{i}:a]adelay={ms}|{ms},apad=whole_dur={FIN}[v{i}]")
n = len(TL)
ins += ["-i", W_ + "musica.wav", "-i", W_ + "imagen.mp4"]
filtro = ";".join(ramas) + f";{''.join(f'[v{i}]' for i in range(n))}amix=inputs={n}:normalize=0,atrim=0:{FIN}[voz];" \
    "[voz]asplit=2[voz1][voz2];" \
    f"[{n}:a]atrim=0:{FIN},volume=0.85[mus];" \
    "[mus][voz2]sidechaincompress=threshold=0.02:ratio=8:attack=30:release=450:makeup=1[musb];" \
    "[voz1]volume=1.0[vf];[vf][musb]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.0:LRA=11,aresample=48000[a]"
subprocess.run(["ffmpeg", "-y", "-v", "error", *ins, "-filter_complex", filtro, "-map", f"{n+1}:v", "-map", "[a]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", "-movflags", "+faststart", SAL], check=True)
print(SAL, subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "csv=p=0", SAL]).decode().strip())
