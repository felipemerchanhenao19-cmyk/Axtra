"""Guion de «Viernes, 8 p. m.»: escenas, diálogos y reparto de voces (Microsoft, gratis)."""
REPARTO = {   # personaje: (voz, velocidad, tono)
    "orbi":   ("es-CO-GonzaloNeural", "+4%", "+2Hz"),     # cálido, seguro, con carisma
    "julian": ("es-VE-SebastianNeural", "+10%", "+0Hz"),   # joven y acelerado
    "papel":  ("es-ES-AlvaroNeural", "+6%", "-12Hz"),      # señor de la vieja escuela
    "c1": ("es-AR-TomasNeural", "+8%", "+0Hz"), "c2": ("es-CO-SalomeNeural", "+6%", "+0Hz"),
    "c3": ("es-EC-LuisNeural", "+6%", "-4Hz"), "c4": ("es-PE-CamilaNeural", "+6%", "+2Hz"),
}
# (escena, quién, texto, pausa_antes)
LINEAS = [
    ("avalancha", "c1", "¡Mesero!", 0.8), ("avalancha", "c2", "¡La carta, por favor!", -0.1), ("avalancha", "c3", "¡Otra cerveza!", -0.45),
    ("avalancha", "c4", "¡Joven, aquí!", -0.35), ("avalancha", "julian", "¡Ya voy, ya voy!", 0.0),
    ("papel", "papel", "Tranquilo, muchacho. Anota todo en mí, como toda la vida.", 0.6),
    ("papel", "c3", "¡Yo pedí carne, no pescado!", 0.4),
    ("derrota", "julian", "Ya no puedo más…", 0.7),
    ("aparece", "orbi", "Buenas noches. ¿Me permite?", 1.3), ("aparece", "papel", "¿Y este quién es?", 0.3),
    ("atiende", "orbi", "Mesa dos, bandeja paisa. Mesa cinco, dos cervezas.", 0.4),
    ("atiende", "orbi", "Y para la mesa tres… ¿le traigo el postre?", 0.3), ("atiende", "c4", "¡Claro que sí!", 0.15),
    ("protesta", "papel", "¡Oiga! ¡Aquí se anota a mano!", 0.4), ("protesta", "orbi", "Shhh.", 0.35),
    ("final", "julian", "¿De dónde saliste?", 0.6), ("final", "orbi", "De la mesa siete.", 0.25),
]
COLA = {"calma": 2.8, "avalancha": 0.5, "papel": 0.6, "derrota": 0.8, "aparece": 0.4, "atiende": 0.4, "protesta": 0.5, "final": 0.4, "sello": 3.4}
ORDEN = ["calma", "avalancha", "papel", "derrota", "aparece", "atiende", "protesta", "final", "sello"]
