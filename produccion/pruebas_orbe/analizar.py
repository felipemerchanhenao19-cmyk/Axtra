"""Resumen de las pruebas de voz: python analizar.py resultados.jsonl [más.jsonl ...]"""
import json, sys, statistics as st
from collections import Counter, defaultdict

filas = [json.loads(l) for f in sys.argv[1:] for l in open(f) if l.strip()]
if not filas: sys.exit("sin datos")


def p(v, q): v = sorted(v); return v[min(len(v) - 1, int(q * len(v)))] if v else 0


def bloque(nombre, fs):
    ok = sum(not f["fallas"] for f in fs); tot = [f["total_s"] for f in fs if f["http"] == 200]
    w = [f["wer"] for f in fs if f.get("wer") is not None]
    t = defaultdict(list)
    for f in fs:
        for k, v in (f.get("tiempos") or {}).items():
            if k != "audio_kb": t[k].append(v)
    pasos = " · ".join(f"{k} {st.median(v):.2f}/{p(v, .9):.2f}" for k, v in t.items())
    print(f"{nombre:16s} {len(fs):5d} turnos · aciertos {100 * ok / len(fs):5.1f}% · total mediana {st.median(tot) if tot else 0:.2f}s p90 {p(tot, .9):.2f}s"
          f" · error de oído {100 * st.mean(w) if w else 0:4.1f}% · {pasos}")


print(f"=== {len(filas)} turnos · {len({(f['t'] // 1) for f in filas})} ===")
bloque("TODO", filas)
print("\n-- por idioma")
for l in sorted({f["idioma"] for f in filas}): bloque(l, [f for f in filas if f["idioma"] == l])
print("\n-- por ruido (dB de señal sobre ruido; menos es más ruido)")
for r in sorted({str(f["snr"]) for f in filas}): bloque("limpio" if r == "None" else r + " dB", [f for f in filas if str(f["snr"]) == r])
print("\n-- fallas más comunes")
c = Counter(x.split(":")[0].split("{")[0].strip() for f in filas for x in f["fallas"])
for k, v in c.most_common(12): print(f"{v:5d}  {k}")
print("\n-- turnos más lentos")
for f in sorted(filas, key=lambda f: -f["total_s"])[:6]: print(f"{f['total_s']:6.2f}s {f['idioma']} {f.get('tiempos')} {f['texto'][:50]}")
print("\n-- ejemplos de fallas (texto → oído → respuesta)")
vistos = set()
for f in filas:
    if f["fallas"] and (f["texto"], f["fallas"][0][:20]) not in vistos and len(vistos) < 25:
        vistos.add((f["texto"], f["fallas"][0][:20]))
        print(f"[{f['idioma']} {('limpio' if f['snr'] is None else str(f['snr']) + 'dB')}] {f['texto']}\n   oído: {f.get('oido')}\n   resp: {(f.get('respuesta') or '')[:160]}\n   pedido {f['pedido']} · {f['fallas']}")
