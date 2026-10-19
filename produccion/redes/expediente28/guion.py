"""Guion de «Expediente 28» (cine negro, Apex Domicilios). Comi es una app FICTICIA, la misma villana de «La Comisión»."""
REPARTO = {
    "narra": ("es-CO-GonzaloNeural", "+2%", "-9Hz"),   # Orbi detective, voz en off grave
    "orbi": ("es-CO-GonzaloNeural", "+4%", "-4Hz"),
    "aure": ("es-EC-LuisNeural", "+2%", "-8Hz"),       # Don Aurelio, dueño de un asadero
    "comi": ("es-MX-DaliaNeural", "-8%", "-7Hz"),      # villana en la sombra, susurra
}
LINEAS = [
    ("oficina", "narra", "Otra noche de lluvia. Y un viejo conocido volvía a tocar mi puerta.", 0.5),
    ("cliente", "aure", "Detective… ya no me cobran comisión. Ahora me cobran «tarifa de servicio».", 0.6),
    ("cliente", "orbi", "Mismo perro… con otro collar.", 0.3),
    ("pistas", "narra", "Tarifa de servicio. Tarifa de empaque. Y al final, la misma marca.", 0.5),
    ("callejon", "narra", "La pista me llevó al mismo callejón.", 0.6),
    ("callejon", "comi", "Cambié de nombre, bolita. No de costumbres.", 0.7),
    ("revela", "orbi", "Y Don Aurelio cambió de canal. Para siempre.", 0.5),
    ("revela", "comi", "¡Otra vez nooo!", 0.6),
    ("cierre", "narra", "Expediente veintiocho. Cerrado.", 0.6),
]
COLA = {"titulo": 2.6, "oficina": 0.3, "cliente": 0.3, "pistas": 0.5, "callejon": 0.3, "revela": 0.6, "cierre": 0.4, "sello": 3.3}
ORDEN = ["titulo", "oficina", "cliente", "pistas", "callejon", "revela", "cierre", "sello"]
