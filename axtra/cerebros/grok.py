"""Cerebro Grok (xAI). La API de xAI es compatible con el cliente de OpenAI."""

from __future__ import annotations

from .base import Cerebro, ErrorCerebro, Mensaje

XAI_URL = "https://api.x.ai/v1"


class CerebroGrok(Cerebro):
    nombre = "grok"

    def __init__(self, api_key: str, modelo: str) -> None:
        self.api_key = api_key
        self.modelo = modelo
        self._cliente = None

    def disponible(self) -> bool:
        return bool(self.api_key)

    def _cliente_api(self):
        if self._cliente is None:
            from openai import OpenAI

            self._cliente = OpenAI(api_key=self.api_key, base_url=XAI_URL)
        return self._cliente

    def responder(self, historial: list[Mensaje], sistema: str) -> str:
        import openai

        mensajes = [{"role": "system", "content": sistema}]
        mensajes += [{"role": m.rol, "content": m.texto} for m in historial]
        try:
            respuesta = self._cliente_api().chat.completions.create(
                model=self.modelo, messages=mensajes
            )
        except openai.OpenAIError as e:
            raise ErrorCerebro(f"Grok falló: {e}") from e

        texto = (respuesta.choices[0].message.content or "").strip()
        if not texto:
            raise ErrorCerebro("Grok devolvió una respuesta vacía.")
        return texto
