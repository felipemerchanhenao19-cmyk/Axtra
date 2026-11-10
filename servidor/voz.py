"""Voz de Axtra (edge-tts, gratis): su voz de mayordomo y voces nativas para los idiomas."""
import asyncio
import re

from . import config

# idioma -> (código, voz nativa, código para reconocer la voz)
IDIOMAS = {
    "ruso": ("ru", "ru-RU-DmitryNeural", "ru-RU"),
    "ingles": ("en", "en-US-AndrewNeural", "en-US"),
    "frances": ("fr", "fr-FR-HenriNeural", "fr-FR"),
    "portugues": ("pt", "pt-BR-AntonioNeural", "pt-BR"),
    "aleman": ("de", "de-DE-ConradNeural", "de-DE"),
    "italiano": ("it", "it-IT-DiegoNeural", "it-IT"),
    "japones": ("ja", "ja-JP-KeitaNeural", "ja-JP"),
    "chino": ("zh", "zh-CN-YunxiNeural", "zh-CN"),
    "coreano": ("ko", "ko-KR-InJoonNeural", "ko-KR"),
    "arabe": ("ar", "ar-SA-HamedNeural", "ar-SA"),
}
# Si una voz se demora o falla, se prueba otra del mismo idioma (medido: en-US-AndrewNeural a veces tarda 16 s
# y en-US-AndrewMultilingualNeural deja de responder; GuyNeural y ChristopherNeural responden en medio segundo).
RESPALDOS = {"en-US-AndrewNeural": ["en-US-GuyNeural", "en-US-ChristopherNeural"],
             "en-US-AndrewMultilingualNeural": ["en-US-GuyNeural", "en-US-ChristopherNeural"],
             "es-CO-GonzaloNeural": ["es-CO-SalomeNeural", "es-MX-JorgeNeural"], "es-ES-AlvaroNeural": ["es-ES-ElviraNeural", "es-MX-JorgeNeural"],
             "fr-FR-HenriNeural": ["fr-FR-DeniseNeural"], "pt-BR-AntonioNeural": ["pt-BR-FranciscaNeural"],
             "de-DE-ConradNeural": ["de-DE-KatjaNeural"], "ru-RU-DmitryNeural": ["ru-RU-SvetlanaNeural"], "ja-JP-KeitaNeural": ["ja-JP-NanamiNeural"]}
NOMBRES = {"ruso": "ruso", "ingles": "inglés", "frances": "francés", "portugues": "portugués", "aleman": "alemán",
           "italiano": "italiano", "japones": "japonés", "chino": "chino mandarín", "coreano": "coreano",
           "arabe": "árabe"}


def limpiar(texto: str) -> str:
    """Quita el formato que sonaría raro en voz alta."""
    texto = re.sub(r"https?://\S+", "", texto)
    texto = re.sub(r"(\d)\s*%", r"\1 por ciento", texto)
    texto = re.sub(r"[*#_`>|]", "", texto)
    return re.sub(r"\s+", " ", texto).strip()


def sintetizar(texto: str, idioma: str = None, lento: bool = False, voz: str = None, ritmo: str = "+0%",
               tono: str = "+0Hz") -> bytes:
    """Audio MP3. Sin idioma: voz de Axtra en español. Con idioma: voz nativa (más despacio si lento).
    voz: otra voz de edge-tts (la usan los orbes de los negocios como respaldo); ritmo: su velocidad, p. ej. «+15%»."""
    import edge_tts

    texto = limpiar(texto)[:2500]
    if not texto:
        raise ValueError("texto vacío")
    if voz:
        velocidad = ritmo                      # tono: más agudo suena más alegre (p. ej. «+10Hz»)
    elif idioma in IDIOMAS:
        voz, velocidad, tono = IDIOMAS[idioma][1], ("-35%" if lento else "-10%"), "+0Hz"
    else:
        voz, velocidad, tono = config.VOZ_AXTRA, ("-25%" if lento else config.VOZ_VELOCIDAD), config.VOZ_TONO

    async def _una(nombre: str) -> bytes:
        audio = bytearray()
        async for trozo in edge_tts.Communicate(texto, nombre, rate=velocidad, pitch=tono).stream():
            if trozo["type"] == "audio":
                audio.extend(trozo["data"])
        if not audio:
            raise RuntimeError("sin audio")
        return bytes(audio)

    async def _run():
        # El servicio de voz a veces se demora (hasta 16 s medidos en inglés) o no responde: cada intento tiene un límite
        # y, si falla, se prueba otra voz del mismo idioma.
        error = None
        for nombre, limite in [(voz, 5), *[(v, 6) for v in RESPALDOS.get(voz, [])], (voz, 8)]:
            try:
                return await asyncio.wait_for(_una(nombre), limite)
            except Exception as e:
                error = e
        raise RuntimeError(f"voz no disponible: {error}")

    return asyncio.run(_run())
