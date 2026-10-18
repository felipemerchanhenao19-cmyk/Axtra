"""Guion de «Mesero nocturno» (homenaje a Taxi Driver, Apex Play). Gancho: «¿Me hablas a mí?» en el primer segundo."""
REPARTO = {
    "narra": ("es-CO-GonzaloNeural", "-10%", "-10Hz"),
    "lento": ("es-CO-GonzaloNeural", "-22%", "-7Hz"),        # el gancho y el espejo, con calma amenazante   # Orbi escribe su diario, voz en off cansada
    "orbi": ("es-CO-GonzaloNeural", "+2%", "-5Hz"),
}
LINEAS = [
    ("gancho", "lento", "¿Me hablas… a mí?", 0.05),
    ("taxi", "narra", "Diario. Noche treinta. La ciudad tiene hambre… y nadie la atiende.", 0.7),
    ("mesas", "narra", "Mesas que esperan. Meseros que no dan abasto. Clientes que se van.", 0.4),
    ("espejo", "lento", "¿Me hablas a mí?", 0.6),
    ("espejo", "lento", "¿Me estás pidiendo… a mí?", 0.7),
    ("espejo", "orbi", "Pues ya está en cocina.", 0.7),
    ("accion", "narra", "Ahora cada mesa tiene su mesero. Escanean. Piden. Listo.", 0.4),
    ("final", "orbi", "¿Algo más, señor?", 0.8),
]
COLA = {"gancho": 0.35, "titulo": 2.2, "taxi": 0.3, "mesas": 0.3, "espejo": 0.6, "accion": 0.4, "final": 0.9, "sello": 3.2}
ORDEN = ["gancho", "titulo", "taxi", "mesas", "espejo", "accion", "final", "sello"]
