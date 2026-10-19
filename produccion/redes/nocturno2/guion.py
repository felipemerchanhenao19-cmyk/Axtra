"""Guion de «Mesero nocturno» (homenaje a Taxi Driver, Apex Play). Gancho: «¿Me hablas a mí?» en el primer segundo."""
REPARTO = {
    "narra": ("es-CO-GonzaloNeural", "-10%", "-10Hz"),
    "lento": ("es-CO-GonzaloNeural", "-22%", "-7Hz"),        # el gancho y el espejo, con calma amenazante   # Orbi escribe su diario, voz en off cansada
    "orbi": ("es-CO-GonzaloNeural", "+2%", "-5Hz"),
}
LINEAS = [
    ("gancho", "orbi", "¿Cuarenta minutos esperando?", 0.05),
    ("taxi", "narra", "Noche treinta y uno. Un cliente que espera… es un cliente que no vuelve.", 0.7),
    ("mesas", "narra", "La cuenta que no llega. El pedido equivocado. La reseña de una estrella.", 0.4),
    ("espejo", "lento", "¿Me hablas a mí?", 0.6),
    ("espejo", "lento", "¿Me pides la cuenta… a mí?", 0.7),
    ("espejo", "orbi", "Ya te llegó al celular.", 0.7),
    ("accion", "narra", "Piden desde la mesa. Pagan desde la mesa. Nadie espera.", 0.4),
    ("final", "orbi", "¿Cinco estrellas, señor?", 0.8),
]
COLA = {"gancho": 0.5, "titulo": 2.2, "taxi": 0.3, "mesas": 0.3, "espejo": 0.6, "accion": 0.4, "final": 0.9, "sello": 3.2}
ORDEN = ["gancho", "titulo", "taxi", "mesas", "espejo", "accion", "final", "sello"]
