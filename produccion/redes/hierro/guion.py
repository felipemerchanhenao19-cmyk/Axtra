"""Guion de «Orbi · Mark I» (homenaje al genio millonario de la armadura, Apex Play). Sin nombres ni logos de Marvel."""
REPARTO = {
    "orbi": ("es-CO-GonzaloNeural", "+4%", "-3Hz"),     # genio, seguro, con chispa
    "sofia": ("es-ES-ElviraNeural", "+12%", "-2Hz"),     # la inteligencia artificial del taller
    "julian": ("es-MX-JorgeNeural", "+4%", "+2Hz"),     # el mesero, desbordado
}
LINEAS = [
    ("gancho", "sofia", "Alerta: catorce mesas esperando.", 0.1),
    ("taller", "orbi", "Sofía… ¿cuánto llevan esperando?", 0.5),
    ("taller", "sofia", "Veinte minutos, señor. Y el mesero está solo.", 0.3),
    ("taller", "orbi", "Prepara el traje.", 0.4),
    ("traje", "sofia", "Traje Mark uno. Menú cargado. Pagos en línea.", 1.4),
    ("traje", "orbi", "Me encanta cuando hablas así.", 0.4),
    ("vuelo", "orbi", "Conéctame a todas las mesas.", 0.8),
    ("vuelo", "sofia", "Conectando catorce códigos QR.", 0.3),
    ("mesas", "sofia", "Mesa uno: pedido enviado. Mesa dos: pedido enviado.", 0.4),
    ("mesas", "orbi", "Y que no se enfríe el ajiaco.", 0.4),
    ("aterriza", "julian", "¿Y usted… quién es?", 1.6),
    ("aterriza", "orbi", "Yo soy… su mesero.", 0.6),
]
COLA = {"gancho": 0.3, "titulo": 2.8, "taller": 0.4, "traje": 0.8, "vuelo": 0.6, "mesas": 0.5, "aterriza": 1.0, "sello": 3.6}
ORDEN = ["gancho", "titulo", "taller", "traje", "vuelo", "mesas", "aterriza", "sello"]
