"""Cerebro Claude (Anthropic)."""

from __future__ import annotations

from .base import Cerebro, ErrorCerebro, Mensaje


class CerebroClaude(Cerebro):
    nombre = "claude"

    def __init__(self, api_key: str, modelo: str) -> None:
        self.api_key = api_key
        self.modelo = modelo
        self._cliente = None

    def disponible(self) -> bool:
        return bool(self.api_key)

    def _cliente_api(self):
        if self._cliente is None:
            import anthropic

            self._cliente = anthropic.Anthropic(api_key=self.api_key)
        return self._cliente

    def responder(self, historial: list[Mensaje], sistema: str) -> str:
        import anthropic

        try:
            respuesta = self._cliente_api().beta.messages.create(
                model=self.modelo,
                max_tokens=16000,
                system=sistema,
                messages=[{"role": m.rol, "content": m.texto} for m in historial],
                output_config={"effort": "medium"},
                # Si Claude rechaza la petición por seguridad, la API la reintenta
                # automáticamente con otro modelo de Claude.
                betas=["server-side-fallback-2026-07-01"],
                fallbacks="default",
            )
        except anthropic.APIError as e:
            raise ErrorCerebro(f"Claude falló: {e}") from e

        if respuesta.stop_reason == "refusal":
            raise ErrorCerebro("Claude se negó a responder esta petición.")
        texto = "".join(b.text for b in respuesta.content if b.type == "text").strip()
        if not texto:
            raise ErrorCerebro("Claude devolvió una respuesta vacía.")
        return texto
