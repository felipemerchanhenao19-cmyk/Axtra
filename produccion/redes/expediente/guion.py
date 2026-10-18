"""Guion de «Expediente 27» (cine negro, Apex Domicilios). Comi es una app FICTICIA, la misma villana de «La Comisión»."""
REPARTO = {
    "narra": ("es-CO-GonzaloNeural", "+2%", "-9Hz"),   # Orbi detective, voz en off grave
    "orbi": ("es-CO-GonzaloNeural", "+4%", "-4Hz"),
    "aure": ("es-EC-LuisNeural", "+2%", "-8Hz"),       # Don Aurelio, dueño de un asadero
    "comi": ("es-MX-DaliaNeural", "-8%", "-7Hz"),      # villana en la sombra, susurra
}
LINEAS = [
    ("oficina", "narra", "Llovía sobre la ciudad. Y alguien se estaba llevando el dinero de los restaurantes.", 0.5),
    ("cliente", "aure", "Detective… vendo más que nunca. Y cada mes tengo menos.", 0.6),
    ("cliente", "orbi", "Siéntese, Don Aurelio.", 0.3),
    ("pistas", "narra", "Treinta pedidos. Treinta recibos. Y en todos, la misma marca.", 0.5),
    ("callejon", "narra", "Las huellas llevaban a un solo lugar.", 0.6),
    ("callejon", "comi", "Llegas tarde, bolita. Todos me pagan.", 0.7),
    ("revela", "orbi", "Ya no. Don Aurelio tiene su propio canal.", 0.5),
    ("revela", "comi", "¡Nooo!", 0.6),
    ("cierre", "narra", "Caso cerrado. Sus clientes. Su dinero.", 0.6),
]
COLA = {"titulo": 2.6, "oficina": 0.3, "cliente": 0.3, "pistas": 0.5, "callejon": 0.3, "revela": 0.6, "cierre": 0.4, "sello": 3.3}
ORDEN = ["titulo", "oficina", "cliente", "pistas", "callejon", "revela", "cierre", "sello"]
