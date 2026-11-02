"""Guion de «Apex · Páginas web» (presentación de la empresa para Instagram). Los sitios que aparecen son diseños de ejemplo."""
REPARTO = {"narra": ("es-CO-GonzaloNeural", "+2%", "-4Hz")}
LINEAS = [
    ("gancho", "narra", "¿Tu negocio todavía no tiene página web?", 0.15),
    ("marca", "narra", "Somos Apex Corporation.", 0.5),
    ("software", "narra", "Creamos software e inteligencia artificial para la industria gastronómica.", 0.3),
    ("webs", "narra", "Y también diseñamos páginas web para tu negocio.", 0.4),
    ("funciones", "narra", "Totalmente funcionales: catálogo, WhatsApp y diseño para celular.", 0.4),
    ("precio", "narra", "Somos una empresa joven que apenas está comenzando. Por eso nuestros precios son accesibles: menos de la mitad de lo normal.", 0.4),
    ("cierre", "narra", "Apex Corporation. Tecnología para tu negocio.", 0.6),
]
COLA = {"gancho": 0.5, "marca": 0.6, "software": 0.6, "webs": 1.6, "funciones": 0.8, "precio": 1.0, "cierre": 2.6}
ORDEN = ["gancho", "marca", "software", "webs", "funciones", "precio", "cierre"]
