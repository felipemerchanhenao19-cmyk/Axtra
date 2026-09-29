"""Cerebro Gemini (Google)."""

from __future__ import annotations

from .base import Cerebro, ErrorCerebro, Mensaje


class CerebroGemini(Cerebro):
    nombre = "gemini"

    def __init__(self, api_key: str, modelo: str) -> None:
        self.api_key = api_key
        self.modelo = modelo
        self._cliente = None

    def disponible(self) -> bool:
        return bool(self.api_key)

    def _cliente_api(self):
        if self._cliente is None:
            from google import genai

            self._cliente = genai.Client(api_key=self.api_key)
        return self._cliente

    def responder(self, historial: list[Mensaje], sistema: str) -> str:
        from google.genai import types

        contenidos = [
            types.Content(
                role="model" if m.rol == "assistant" else "user",
                parts=[types.Part(text=m.texto)],
            )
            for m in historial
        ]
        try:
            respuesta = self._cliente_api().models.generate_content(
                model=self.modelo,
                contents=contenidos,
                config=types.GenerateContentConfig(
                    system_instruction=sistema,
                    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
                ),
            )
        except Exception as e:  # el SDK de Google lanza varios tipos de error
            raise ErrorCerebro(f"Gemini falló: {e}") from e

        texto = (respuesta.text or "").strip()
        if not texto:
            raise ErrorCerebro("Gemini devolvió una respuesta vacía.")
        return texto
