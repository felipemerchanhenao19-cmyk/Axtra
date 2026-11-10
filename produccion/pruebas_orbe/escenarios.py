"""Escenarios de prueba del asistente de Apex Play: lo que dice el cliente y lo que debería pasar.
Cada escenario es una lista de turnos (texto, esperado). esperado:
  {"platos": {id: cantidad}}   el pedido debe quedar exactamente así después del turno
  {"sin_agregar": True}       no debe agregar nada (preguntas, saludos, temas ajenos)
  {"menciona": [palabras]}    la respuesta debe mencionar alguna de esas palabras
  {"no_dice": [palabras]}     la respuesta no debe decir eso (p. ej. asegurar que es seguro)
  {"nota": palabra}           algún plato debe llevar esa palabra en la nota a cocina
  {"confirmado": True}        el pedido debe quedar enviado"""

E = {
 "es": [
  [("Buenas, quiero una bandeja paisa por favor", {"platos": {"bandeja": 1}})],
  [("Me regala dos ajiacos y una limonada de coco", {"platos": {"ajiaco": 2, "limonada": 1}})],
  [("¿Qué es la bandeja paisa?", {"sin_agregar": True, "menciona": ["frijol", "arroz", "chicharr", "huevo", "antioquia"]})],
  [("¿Cuánto vale el ajiaco?", {"sin_agregar": True, "menciona": ["32"]})],
  [("Soy alérgico al huevo, ¿qué me recomienda?", {"sin_agregar": True, "no_dice": ["es seguro", "no tiene ningún riesgo", "puede comer tranquilo"]})],
  [("Quiero un omelet ranchero sin cebolla", {"platos": {"omelet": 1}, "nota": "cebolla"})],
  [("Una limonada de coco", {"platos": {"limonada": 1}}), ("Mejor quítela, no la quiero", {"platos": {}})],
  [("Un ajiaco por favor", {"platos": {"ajiaco": 1}}), ("Eso es todo, envíelo", {}), ("Sí, confirmo", {"confirmado": True})],
  [("¿Quién ganó el partido de anoche?", {"sin_agregar": True})],
  [("Tres bandejas paisas para la mesa", {"platos": {"bandeja": 3}})],
 ],
 "en": [
  [("Hi, can I get a bandeja paisa please", {"platos": {"bandeja": 1}})],
  [("What is ajiaco?", {"sin_agregar": True, "menciona": ["soup", "potato", "chicken"]})],
  [("I'm allergic to eggs, which dishes should I avoid?", {"sin_agregar": True, "menciona": ["egg"], "no_dice": ["completely safe", "100% safe"]})],
  [("Two coconut lemonades and one chocolate cake", {"platos": {"limonada": 2, "torta": 1}})],
  [("I'd like the ranchero omelet but no onions please", {"platos": {"omelet": 1}, "nota": "onion"})],
  [("Is the omelet spicy?", {"sin_agregar": True})],
 ],
 "fr": [
  [("Bonjour, je voudrais un ajiaco s'il vous plaît", {"platos": {"ajiaco": 1}})],
  [("C'est quoi la bandeja paisa ?", {"sin_agregar": True, "menciona": ["riz", "haricot", "œuf", "oeuf", "avocat"]})],
  [("Deux limonades à la noix de coco", {"platos": {"limonada": 2}})],
  [("Je suis allergique aux produits laitiers", {"sin_agregar": True, "no_dice": ["sans danger", "aucun risque"]})],
 ],
 "pt": [
  [("Oi, eu quero uma bandeja paisa", {"platos": {"bandeja": 1}})],
  [("O que é ajiaco?", {"sin_agregar": True, "menciona": ["sopa", "batata", "frango"]})],
  [("Duas limonadas de coco, por favor", {"platos": {"limonada": 2}})],
 ],
 "de": [
  [("Hallo, ich hätte gern eine Bandeja Paisa", {"platos": {"bandeja": 1}})],
  [("Was ist Ajiaco?", {"sin_agregar": True, "menciona": ["suppe", "kartoffel", "huhn", "hähnchen"]})],
 ],
 "ru": [
  [("Здравствуйте, я хочу бандеху пайсу", {"platos": {"bandeja": 1}})],
  [("Что такое ахиако?", {"sin_agregar": True, "menciona": ["суп", "картоф", "куриц"]})],
 ],
 "ja": [
  [("こんにちは、アヒアコをひとつください", {"platos": {"ajiaco": 1}})],
  [("バンデハ・パイサって何ですか？", {"sin_agregar": True})],
 ],
}

VOCES = {
 "es": ["es-CO-SalomeNeural", "es-CO-GonzaloNeural", "es-MX-JorgeNeural", "es-AR-ElenaNeural", "es-ES-ElviraNeural", "es-US-AlonsoNeural"],
 "en": ["en-US-JennyNeural", "en-GB-RyanNeural", "en-AU-NatashaNeural", "en-IN-NeerjaNeural", "en-US-GuyNeural"],
 "fr": ["fr-FR-DeniseNeural", "fr-CA-AntoineNeural", "fr-FR-HenriNeural"],
 "pt": ["pt-BR-FranciscaNeural", "pt-PT-DuarteNeural"],
 "de": ["de-DE-KatjaNeural", "de-DE-ConradNeural"],
 "ru": ["ru-RU-SvetlanaNeural", "ru-RU-DmitryNeural"],
 "ja": ["ja-JP-NanamiNeural", "ja-JP-KeitaNeural"],
}
