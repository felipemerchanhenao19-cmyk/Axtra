# Pruebas nocturnas del asistente de voz (Apex Play) — 9 y 10 de noviembre de 2026

## Qué se hizo
- **Banco de pruebas contra el servidor publicado** (`ejecutar.py`): voz de clientes en 7 idiomas (es, en, pt, fr, de, ja, ru),
  varios acentos y velocidades, mezclada con ruido de restaurante (conversaciones de otras mesas, cubiertos y platos) a
  tres niveles: limpio, 15 dB y 8 dB (mucho ruido). Se envía igual que el celular a `/v1/turno` y se revisa qué entendió,
  qué hizo con el pedido, si explicó el plato, si la nota a cocina («sin cebolla») llegó y cuánto tardó cada paso.
- **131 turnos reales** en dos tandas. La prueba se detuvo sola cada vez que el servidor empezó a rechazar.
- **Simulador de carga** (`carga.py`): el servidor de Apex de verdad con una ranura falsa que tarda lo que la real.
  200 personas en 50 mesas, 4 turnos cada una.
- **Prueba del celular de punta a punta** (`celular.py`): Chromium con un micrófono falso, la página real del menú.

## Resultados
| | |
|---|---|
| Oído (Whisper) | Error de palabras 1-6 % incluso con 8 dB de ruido. Casi todo es «2» por «two» o kanji por hiragana. Solo en un caso entró una frase del fondo. |
| Aciertos cuando el cerebro respondió todo el turno | **98 %** (48 turnos) |
| Turnos que fallaron por el cupo de Groq | 41 «sin voz» y unos 40 cortados a mitad del turno |
| Tiempo por paso (mediana / p90) | oír 0,26 / 0,66 s · pensar 0,58 / 1,8 s · voz 1,2 / 9,7 s |

## Fallas encontradas y arreglo (todo en la rama `claude/axtra-continuacion-p5n98r`, falta pasarlo a main)
1. **El cupo gratuito de Groq** (gpt-oss-20b: 8.000 tokens/min y 200.000 tokens/día; un turno usa unos 5.000) alcanza
   para ~1 mesa conversando a la vez y ~40 turnos al día en total. Arreglo: varios modelos de respaldo, cada uno con
   su propio cupo (gpt-oss-120b, llama-4-scout, Gemini, Gemini lite), y el modelo agotado «descansa» lo que pide Groq,
   así no se pierde tiempo preguntándole. **Lo de fondo es pasar Groq al plan de pago** (≈ 1,6 COP por turno).
2. **Voz en inglés lenta**: Andrew tardaba 4-6 s (hasta 22 s) y a veces no respondía. Ahora Guy (~1 s) con respaldos y
   límite de tiempo por intento. La voz del sitio en inglés también pasa a Guy.
3. **Oído sin respaldo**: si Whisper se quedaba sin cupo, el orbe quedaba sordo. Ahora usa Whisper turbo de respaldo.
4. **«¡Excelente elección!» falso**: decía eso aunque solo hubiera agregado uno de dos platos o ninguno. Ahora dice
   exactamente lo que anotó («Anotado: 2 limonadas de coco y torta de chocolate. ¿Desea algo más?») en 8 idiomas.
5. **Ruso**: «бандеху» (declinado) no se reconocía como «бандеха» y se bloqueaba el pedido. Arreglado.
6. **Mezcla de idiomas** («Your omelet, sin cebolla, is ready»): regla nueva en las instrucciones.
7. **Fila en el servidor**: Python daba 5-6 hilos para los turnos; con 200 personas la respuesta tardaba 21 s de mediana.
   Con 64 hilos: 1,3 s de mediana y 2,1 s p99, sin fallas.
8. **Silencio al final del audio**: el celular mandaba ~0,7 s de ruido al final; ahora 0,15 s (sube más rápido y
   Whisper no inventa palabras).
9. **Tokens**: el historial guarda las herramientas resumidas y el número de mesa va al final de las instrucciones
   (el resto queda en el caché de Groq, que no cuenta contra el límite).
10. **Modo rápido** (experimento, restaurante `pruebas_rapido`): después de agregar platos responde sin volver a pensar
    (la mitad de tokens, ~0,6 s menos). No se salta el cerebro si hay cambios para la cocina o alergias.

## Capacidad con el simulador (200 personas)
| Cupo del cerebro (tokens/min) | Turnos bien |
|---|---|
| 8.000 (Groq gratis, un modelo) | 5 de 800 |
| 32.000 | 16 de 800 |
| 250.000 | 125 de 800 |
| sin límite | 800 de 800 |

El simulador es exigente: 200 personas hablando cada 8 a 20 s, unos 6 turnos por segundo. Un restaurante real pide
mucho menos. Aun así muestra que el límite es el cupo del cerebro, no el servidor.
