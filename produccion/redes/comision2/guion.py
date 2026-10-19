"""Guion de «La Comisión — Capítulo 2: La revancha». Comi es una app de domicilios FICTICIA (no es ninguna marca real)."""
REPARTO = {
    "orbi": ("es-CO-GonzaloNeural", "+8%", "+2Hz"),
    "comi": ("es-MX-DaliaNeural", "+12%", "+6Hz"),    # diva de telenovela
    "rosa": ("es-CO-SalomeNeural", "+6%", "-6Hz"),    # dueña, paciente pero cansada
}
LINEAS = [
    ("entrada", "comi", "Rosa, mi amor… volví. Y traigo una promo especial.", 0.6),
    ("entrada", "rosa", "¿Otra vez usted?", 0.25),
    ("cobro", "comi", "Solo veinticinco por ciento. ¡Rebajadito!", 0.2),
    ("cobro", "rosa", "¡Igual se lleva mi plata!", 0.3),
    ("cobro", "comi", "Pero con cariño.", 0.2),
    ("orbi", "orbi", "Doña Rosa ya tiene domicilios propios.", 0.7),
    ("orbi", "comi", "¿Todavía sigues aquí, bolita?", 0.2),
    ("orbi", "orbi", "Todos los días. Sin cobrarle un peso.", 0.3),
    ("drama", "comi", "¿¡Cero por ciento!? ¡Eso es ilegal!", 0.7),
    ("drama", "orbi", "No. Es Apex Domicilios.", 0.4),
    ("llanto", "comi", "¡Te doy envío gratis el primer mes!", 0.3),
    ("llanto", "rosa", "¿Y el segundo mes, qué?", 0.35),
    ("salida", "comi", "¡Esto no se queda así! ¡Capítulo tres!", 0.35),
    ("final", "orbi", "Doña Rosa… ¿le traigo un tintico?", 0.7),
    ("final", "rosa", "¡Ay, Orbi!", 0.25),
]
COLA = {"titulo": 2.6, "entrada": 0.3, "cobro": 0.4, "orbi": 0.3, "drama": 0.4, "llanto": 0.4, "salida": 0.9, "final": 0.4, "sello": 3.2}
ORDEN = ["titulo", "entrada", "cobro", "orbi", "drama", "llanto", "salida", "final", "sello"]
