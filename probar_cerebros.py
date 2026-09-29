"""Prueba todos los cerebros gratis y la búsqueda. Uso: python axtra.py cerebros"""
import time

import config
import llm
import search

SYS = "Eres AXTRA, mayordomo británico. Responde en español en una sola frase."
MSG = [{"role": "user", "content": "Preséntate brevemente."}]

print("=== Cerebros gratis de Axtra ===\n")
for name, key in (("gemini", config.GEMINI_API_KEY), ("groq", config.GROQ_API_KEY),
                  ("openrouter", config.OPENROUTER_API_KEY)):
    if not key:
        print(f"{llm.NAMES[name]:11}: sin clave (opcional)")
        continue
    t = time.time()
    try:
        txt = llm.gemini_chat(SYS, MSG, 80) if name == "gemini" else llm.compat_chat(name, SYS, MSG, 80)
        print(f"{llm.NAMES[name]:11}: OK ({time.time() - t:.1f} s) -> {txt[:90]}")
    except Exception as e:
        print(f"{llm.NAMES[name]:11}: FALLA -> {str(e)[:120]}")

print("\nBúsqueda gratis en internet:")
res = search.web("noticias de inteligencia artificial hoy", 3)
print("  OK:" if res else "  FALLA: no se obtuvieron resultados")
for r in res:
    print(f"   - {r['titulo'][:80]}")
print(f"\nOrden de uso: {' -> '.join(llm.NAMES.get(n, n) for n in config.FREE_BRAINS)}")
