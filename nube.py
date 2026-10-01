"""Conecta este Axtra (el del PC) con Axtra en la nube, para que la app del celular tenga tus datos.

Cada 10 minutos sube: tus recuerdos, el perfil de tus empresas, el CRM, tareas y recordatorios, la
Sincronización y el avance del Protocolo de inteligencia avanzada. En la nube solo los usan los cerebros
de pago (Claude o Grok); los gratis nunca los reciben.

En el .env del PC:
    AXTRA_NUBE_URL=https://tu-dominio            (la dirección de Axtra en la nube)
    CF_ACCESS_CLIENT_ID=...                      (el "token de servicio" de Cloudflare Access)
    CF_ACCESS_CLIENT_SECRET=...
Probar:  python axtra.py nube
"""
import json
import os
import threading
import time

import requests

from config import DATA_DIR

URL = os.getenv("AXTRA_NUBE_URL", "").rstrip("/")
CLIENT_ID = os.getenv("CF_ACCESS_CLIENT_ID", "")
CLIENT_SECRET = os.getenv("CF_ACCESS_CLIENT_SECRET", "")
MINUTOS = float(os.getenv("AXTRA_NUBE_MINUTOS", "10"))
_estado = {"ultimo": None, "error": ""}


def configurada() -> bool:
    return bool(URL and CLIENT_ID and CLIENT_SECRET)


def _json(nombre: str, defecto):
    try:
        return json.loads((DATA_DIR / nombre).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return defecto


def _protocolo() -> list:
    import aprendizaje

    temas = []
    for f in sorted(aprendizaje.DIR.glob("*.json")):
        try:
            plan = json.loads(f.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        modulos = []
        for m in plan.get("modulos", []):
            lecciones = m.get("lecciones", [])
            modulos.append({"titulo": m.get("titulo", ""), "hechas": sum(1 for l in lecciones if l.get("hecha")),
                            "total": len(lecciones)})
        actual = next((m["titulo"] for m in modulos if m["hechas"] < m["total"]), "")
        temas.append({"tema": plan.get("tema", f.stem), "porcentaje": aprendizaje.progress(plan),
                      "modulo_actual": actual, "modulos": modulos, "tarjetas": len(plan.get("tarjetas", []))})
    return temas


def paquete() -> dict:
    """Todo lo que la nube necesita saber, en un solo JSON."""
    import knowledge
    import sync

    datos = {"version": 1, "enviado": time.time(),
             "recuerdos": _json("recuerdos.json", []),
             "crm": _json("crm.json", []),
             "tareas": _json("tareas.json", []),
             "recordatorios": _json("recordatorios.json", []),
             "idiomas_pc": _json("idiomas.json", {})}
    try:
        datos["perfil"] = knowledge.profile_full()
    except Exception:
        datos["perfil"] = ""
    try:
        s = sync.score()
        datos["sincronizacion"] = {"total": s["total"], "partes": s["partes"], "nivel": s["nivel"][1],
                                   "nivel_umbral": s["nivel"][0], "que_desbloquea": s["nivel"][2],
                                   "area_debil": s["area_debil"]}
    except Exception as e:
        datos["sincronizacion"] = {"error": str(e)}
    try:
        datos["protocolo"] = _protocolo()
    except Exception:
        datos["protocolo"] = []
    return datos


def subir() -> dict:
    if not configurada():
        raise RuntimeError("falta AXTRA_NUBE_URL, CF_ACCESS_CLIENT_ID o CF_ACCESS_CLIENT_SECRET en el .env")
    r = requests.post(f"{URL}/api/pc/sincronizar", json=paquete(), timeout=30,
                      headers={"CF-Access-Client-Id": CLIENT_ID, "CF-Access-Client-Secret": CLIENT_SECRET})
    if r.status_code in (401, 403):
        raise RuntimeError("la nube rechazó el acceso: revisa el token de servicio de Cloudflare")
    r.raise_for_status()
    _estado.update(ultimo=time.time(), error="")
    return r.json()


def _bucle() -> None:
    while True:
        try:
            subir()
        except Exception as e:
            if str(e) != _estado["error"]:
                print(f"  (nube: {e})")
            _estado["error"] = str(e)
        time.sleep(MINUTOS * 60)


def iniciar() -> None:
    """main.py lo llama al arrancar: sube los datos en segundo plano (no hace nada si no está configurada)."""
    if configurada():
        threading.Thread(target=_bucle, daemon=True, name="nube").start()
        print(f"  - Conectado a Axtra en la nube ({URL}): sincroniza cada {MINUTOS:.0f} min")


if __name__ == "__main__":
    print("=== Conexión con Axtra en la nube ===")
    if not configurada():
        raise SystemExit(__doc__)
    p = paquete()
    print(f"Subiendo: {len(p['recuerdos'])} recuerdos, {len(p['crm'])} clientes, {len(p['protocolo'])} temas del "
          f"Protocolo, sincronización {p['sincronizacion'].get('total', '?')} %...")
    print("Respuesta de la nube:", subir())
    print("LISTO: la app del celular ya tiene sus datos.")
