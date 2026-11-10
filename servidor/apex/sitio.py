"""Guion del video «Mire Apex en su restaurante» del sitio de Apex Corporation.
Lo usan el servidor (voz con el nombre de cada restaurante) y produccion/sitio/voces_sitio.py (versión genérica de respaldo)."""
import re

# voz de Microsoft (gratis) y velocidad por idioma: la misma del recorrido guiado
VOCES = {"es": ("es-CO-GonzaloNeural", 1.04), "en": ("en-US-GuyNeural", 1.02), "pt": ("pt-BR-AntonioNeural", 1.04)}

_GUION = {
    "es": {"apertura": "Una noche cualquiera en {nombre}{lugar}.", "apertura_g": "Una noche cualquiera en su restaurante.", "lugar": ", en {ciudad}",
           "mesa": "Su cliente se sienta, escanea el código de la mesa... y aparezco yo.",
           "saludo": "¡Bienvenido a {nombre}! ¿Qué le provoca hoy?", "saludo_g": "¡Bienvenido! ¿Qué le provoca hoy?",
           "carta": "Hoy le recomiendo {plato}. ¡Es lo más pedido de la casa!", "carta_g": "Hoy le recomiendo el plato de la casa. ¡Es lo más pedido!",
           "cocina": "El pedido llega directo a la cocina. Sin errores, sin esperas y sin comisiones.",
           "cierre": "Así se vería Apex en {nombre}.", "cierre_g": "Así se vería Apex en su restaurante."},
    "en": {"apertura": "One night at {nombre}{lugar}.", "apertura_g": "One night at your restaurant.", "lugar": ", in {ciudad}",
           "mesa": "Your guest sits down, scans the code on the table... and here I am.",
           "saludo": "Welcome to {nombre}! What would you like today?", "saludo_g": "Welcome! What would you like today?",
           "carta": "Today I recommend the {plato}. It's the house favorite!", "carta_g": "Today I recommend the house special. It's the favorite!",
           "cocina": "The order goes straight to the kitchen. No mistakes, no waiting, and no commissions.",
           "cierre": "This is how Apex would look at {nombre}.", "cierre_g": "This is how Apex would look at your restaurant."},
    "pt": {"apertura": "Uma noite qualquer em {nombre}{lugar}.", "apertura_g": "Uma noite qualquer no seu restaurante.", "lugar": ", em {ciudad}",
           "mesa": "Seu cliente se senta, escaneia o código da mesa... e aí apareço eu.",
           "saludo": "Bem-vindo ao {nombre}! O que vai querer hoje?", "saludo_g": "Bem-vindo! O que vai querer hoje?",
           "carta": "Hoje eu recomendo {plato}. É o mais pedido da casa!", "carta_g": "Hoje eu recomendo o prato da casa. É o mais pedido!",
           "cocina": "O pedido chega direto na cozinha. Sem erros, sem espera e sem comissões.",
           "cierre": "Assim ficaria a Apex em {nombre}.", "cierre_g": "Assim ficaria a Apex no seu restaurante."},
}
ESCENAS = ["apertura", "mesa", "saludo", "carta", "cocina", "cierre"]


def limpio(s: str, maximo: int) -> str:
    """Solo letras, números y puntuación sencilla: lo que se le pasa a la voz no puede traer marcas ni símbolos."""
    s = re.sub(r"[^\w\s.,'’\-]", " ", s or "", flags=re.UNICODE)
    return re.sub(r"\s+", " ", s).strip(" .,-")[:maximo]


def guion(idioma: str, nombre: str = "", ciudad: str = "", plato: str = "") -> list[dict]:
    """Las seis frases del video. Sin nombre (o sin plato) usa la versión genérica de esa frase."""
    g = _GUION.get(idioma, _GUION["es"])
    nombre, ciudad, plato = limpio(nombre, 40), limpio(ciudad, 30), limpio(plato, 34)
    datos = {"nombre": nombre, "plato": plato, "lugar": g["lugar"].format(ciudad=ciudad) if ciudad else ""}
    out = []
    for e in ESCENAS:
        usa = "plato" if e == "carta" else "nombre"
        txt = g[e + "_g"] if (e + "_g") in g and not datos[usa] else g[e].format(**datos)
        out.append({"escena": e, "txt": txt})
    return out
