# Voces clonadas de Apex

Clonador propio, gratuito y local. Corre en el mismo servidor que hace los videos y no paga por uso.

| Pieza | Qué hace |
|---|---|
| **Chatterbox Multilingual** (Resemble AI, licencia MIT) | Clona una voz con 10 s de muestra y habla en español. Su intensidad emocional se regula. |
| **Whisper** (faster-whisper, licencia MIT) | Escucha cada frase generada y comprueba que diga exactamente el texto. |
| **Huella de voz** | Compara cada frase con la voz original. Si no se parece, la repite. |
| **Marca de agua Perth** | Va inaudible en cada audio y lo identifica como voz sintética. |

## Flujo
1. **Grabar:** cada persona lee `LEER-PARA-GRABAR.md`, de 30 a 60 s, con su autorización al inicio.
2. **Registrar:**
   ```
   /home/user/voz-env/bin/python clonador.py registrar felipe felipe.m4a --autoriza "Felipe ..." --acepto
   ```
   Limpia el audio (ruido, zumbido, pausas, volumen), elige los 10 s con más habla y prueba tres frases.
3. **Usar en un video:** en el reparto del episodio va `("clon:felipe", "+0%", "+0Hz")`.
   - El segundo valor ajusta la velocidad sin cambiar el tono.
   - Cada línea acepta `emo=` (de 0,3, tranquila, a 0,9, muy expresiva) y `ritmo=` (por debajo de 0,5 habla más pausado).

   ```python
   L("p01", "¡Cuarenta y dos pedidos!", emo=0.8)
   ```

## Control de calidad (por frase)
- **Texto:** error de texto de 8 % o menos según Whisper. Detecta palabras inventadas, cortes y repeticiones.
- **Parecido de voz:** 0,86 o más (0,81 en frases de menos de 2,5 s). Medido en ensayo, los clones sacaron entre 0,90 y 0,94, y otra voz masculina parecida, 0,83.
- **Ritmo:** entre 7 y 24 caracteres por segundo.
- **Reintentos:** hasta 3, con semillas distintas. Gana la mejor toma, y las líneas que no pasan quedan anotadas en `*-informe.json`.

## Tiempos (CPU de 4 núcleos)
- Unos **6 s de proceso por cada segundo de voz**. Un video de 25 s con 8 líneas tarda de 5 a 10 minutos en voces.
- **Las frases quedan en caché:** al volver a renderizar no se generan de nuevo.

## Reglas
- **Solo con autorización:** cada voz se registra con la autorización de su dueño. Queda guardada en `banco/<nombre>/meta.json`, con fecha y huella de los archivos originales.
- **Grabaciones originales fuera del repositorio:** no se guardan. Solo quedan la muestra limpia de 10 s (`ref.wav`), la grabación limpia y la huella.
- **Instalación en un servidor nuevo:** `bash instalar.sh`.
