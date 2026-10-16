"""Línea de tiempo común a la música y a la imagen: dónde empieza cada escena y dónde entra la voz."""
import json
# (escena, silencio antes de la voz, cola después de la voz)
RITMO = {"apertura": (1.8, 0.5), "problema": (0.3, 0.9), "revelacion": (0.5, 2.2), "futuro": (0.6, 1.0),
         "final": (1.0, 0.8), "contacto": (0.3, 3.4), "sincomision": (0.4, 0.9)}
def linea(prod, carpeta_voz):
    import guion_cine
    esc = {"play": guion_cine.PLAY, "domicilios": guion_cine.DOMICILIOS}[prod]
    dur = json.load(open(carpeta_voz.rstrip("/") + "/voz.json"))["dur"]
    t, out = 0.0, []
    for k, _ in esc:
        antes, cola = RITMO.get(k, (0.45, 0.65))
        out.append({"id": k, "ini": round(t, 3), "voz": round(t + antes, 3), "dur_voz": dur[k], "fin": round(t + antes + dur[k] + cola, 3)})
        t = out[-1]["fin"]
    return out
