"""Qué se ve en cada escena (texto en pantalla, poses del celular, de qué parte de la grabación sale la pantalla)."""
# pose = (x en px desde el centro, y, escala, rotX, rotY, rotZ)
IZQ_A = (-430, 30, 0.92, 6, 24, -2); IZQ_B = (-410, 20, 0.97, 2, 14, -1)
DER_A = (430, 30, 0.92, 6, -24, 2); DER_B = (410, 20, 0.97, 2, -14, 1)
CEN_A = (360, 170, 1.18, 12, -4, 0); CEN_B = (390, 130, 1.3, 6, 7, 0)   # primer plano, recortado por abajo

def play(m):
    return {
     "apertura": {"tipo": "texto", "lineas": [(0.0, "Cada noche.", "en miles de restaurantes")], "luz": "fria"},
     "problema": {"tipo": "texto", "lineas": [(0.0, "Mesas llenas.", ""), (0.33, "Clientes esperando.", ""), (0.66, "Pedidos que se pierden.", "")], "luz": "calida"},
     "revelacion": {"tipo": "revelacion", "antes": "Hasta hoy.", "marca": "Apex Play", "lema": ""},
     "qr": {"tipo": "cel", "fuente": "c", "desde": m["qr"] + 2.5, "pose": (DER_A, DER_B), "texto": "izq",
            "kicker": "Escanee", "titulo": "Sin descargar<br>nada.", "sub": "Un código QR en cada mesa."},
     "carta": {"tipo": "cel", "fuente": "c", "desde": m["pedir"] - 0.6, "pose": (IZQ_A, IZQ_B), "texto": "der",
               "kicker": "Su carta", "titulo": "Cobra vida.", "sub": "Un asistente que habla, escucha<br>y recomienda."},
     "tresd": {"tipo": "cel", "fuente": "c", "desde": m["tresd"], "pose": (CEN_A, CEN_B), "texto": "izq",
               "kicker": "Realidad aumentada", "titulo": "Platos en 3D.", "sub": ""},
     "oferta": {"tipo": "cel", "fuente": "c", "desde": m["oferta"] + 0.4, "pose": (DER_A, DER_B), "texto": "izq",
                "kicker": "Postre del día", "titulo": "Más venta.<br>En cada mesa.", "sub": ""},
     "caja": {"tipo": "tab", "fuente": "k", "desde": m["envio_caja"] - 0.2, "texto": "izq",
              "kicker": "Al instante", "titulo": "Directo<br>a la caja.", "sub": "Sin papel. Sin errores."},
     "idiomas": {"tipo": "cel", "fuente": "c", "desde": m["idiomas"] + 2.2, "pose": ((420, 60, 0.9, 8, -16, 0), (400, 40, 0.96, 3, -8, 0)), "texto": "idiomas",
                 "kicker": "", "titulo": "", "sub": "", "saludos": ["Hola", "Hello", "Olá", "Hallo", "Привет"]},
     "futuro": {"tipo": "futuro", "tarjetas": ["Meseros virtuales", "Domicilios", "Repartidores"], "titulo": "Todo, en un solo lugar."},
     "final": {"tipo": "logo", "marca": "Apex Play", "lema": "Un mesero virtual en cada mesa."},
     "contacto": {"tipo": "contacto", "marca": "Apex Play", "qr": "https://api.axtra.chat/demo"},
    }

def domicilios(m):
    return {
     "apertura": {"tipo": "numero", "desde": 0, "hasta": 27, "sufijo": "%", "pie": "de comisión por cada domicilio"},
     "problema": {"tipo": "texto", "lineas": [(0.0, "Su cliente.", ""), (0.2, "Su comida.", ""), (0.38, "Su trabajo.", ""), (0.62, "La comisión,", "para otro.")], "luz": "calida"},
     "revelacion": {"tipo": "revelacion", "antes": "Hasta hoy.", "marca": "Apex Domicilios", "lema": ""},
     "link": {"tipo": "cel", "fuente": "c", "desde": m["link"] + 1.5, "pose": (DER_A, DER_B), "texto": "izq",
              "kicker": "Su propio link", "titulo": "Donde ya están<br>sus clientes.", "sub": "", "chips": ["Instagram", "WhatsApp", "Google Maps"]},
     "carta": {"tipo": "cel", "fuente": "c", "desde": m["carta"], "pose": (IZQ_A, IZQ_B), "texto": "der",
               "kicker": "Pida como quiera", "titulo": "Hablando.<br>O con un toque.", "sub": "Y el postre del día, ofrecido a tiempo."},
     "datos": {"tipo": "cel", "fuente": "c", "desde": m["datos"], "pose": (DER_A, DER_B), "texto": "izq",
               "kicker": "Pago", "titulo": "Contra entrega<br>o Nequi.", "sub": "Dirección, barrio y zona en segundos."},
     "caja": {"tipo": "tab", "fuente": "k", "desde": m["caja_desde"] + 1.0, "texto": "izq",
              "kicker": "En su caja", "titulo": "Suena<br>el pedido.", "sub": "Con todos los datos.<br>Y WhatsApp a un toque."},
     "seguimiento": {"tipo": "cel", "fuente": "c", "desde": m["seguimiento"], "pose": (CEN_A, CEN_B), "texto": "izq",
                     "kicker": "En vivo", "titulo": "Hasta su puerta.", "sub": ""},
     "sincomision": {"tipo": "numero", "desde": 27, "hasta": 0, "sufijo": "%", "pie": "Los clientes son suyos."},
     "futuro": {"tipo": "futuro", "tarjetas": ["Meseros virtuales", "Domicilios", "Repartidores"], "titulo": "Todo, en un solo lugar."},
     "final": {"tipo": "logo", "marca": "Apex Domicilios", "lema": "Sus domicilios, sin comisiones."},
     "contacto": {"tipo": "contacto", "marca": "Apex Domicilios", "qr": "https://api.axtra.chat/domicilios"},
    }
