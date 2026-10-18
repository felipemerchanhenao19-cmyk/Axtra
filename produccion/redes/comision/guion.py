"""Guion de «La Comisión — Capítulo 1: El reencuentro». Comi es una app de domicilios FICTICIA (no es ninguna marca real)."""
REPARTO = {
    "orbi": ("es-CO-GonzaloNeural", "+8%", "+2Hz"),
    "comi": ("es-MX-DaliaNeural", "+12%", "+6Hz"),    # diva de telenovela
    "rosa": ("es-CO-SalomeNeural", "+6%", "-6Hz"),    # dueña, paciente pero cansada
}
LINEAS = [
    ("entrada", "comi", "Rosa… ¿no me saludas? Soy yo, Comi. Tu app de siempre.", 0.6),
    ("entrada", "rosa", "Hola, Comi.", 0.25),
    ("cobro", "comi", "Vengo por lo mío: mi veintisiete por ciento.", 0.2),
    ("cobro", "rosa", "¡Pero si la comida la hice yo!", 0.3),
    ("cobro", "comi", "Detalles, mi amor.", 0.2),
    ("orbi", "orbi", "Disculpe… ¿y usted quién es?", 0.7),
    ("orbi", "comi", "¿Y tú quién eres, bolita?", 0.2),
    ("orbi", "orbi", "El canal de domicilios de Rosa. Sin comisiones.", 0.3),
    ("drama", "comi", "¿¡Sin comisiones!? ¡Eso no existe!", 0.7),
    ("drama", "orbi", "Sus clientes. Su dinero.", 0.4),
    ("llanto", "comi", "¡Después de todo lo que te cobré!", 0.3),
    ("llanto", "rosa", "Por eso mismo, Comi.", 0.35),
    ("salida", "comi", "¡Volverás! ¡Todas vuelven!", 0.35),
    ("final", "orbi", "Doña Rosa… ¿le traigo el postre?", 0.7),
    ("final", "rosa", "¡Ay, Orbi!", 0.25),
]
COLA = {"titulo": 2.6, "entrada": 0.3, "cobro": 0.4, "orbi": 0.3, "drama": 0.4, "llanto": 0.4, "salida": 0.9, "final": 0.4, "sello": 3.2}
ORDEN = ["titulo", "entrada", "cobro", "orbi", "drama", "llanto", "salida", "final", "sello"]
