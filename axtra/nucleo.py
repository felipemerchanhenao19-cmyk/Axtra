"""Núcleo de Axtra: decide qué cerebro responde y guarda la conversación."""

from __future__ import annotations

from .cerebros import (
    Cerebro,
    CerebroClaude,
    CerebroGemini,
    CerebroGrok,
    ErrorCerebro,
    Mensaje,
)
from .config import CEREBROS, Config

MAX_MENSAJES = 40  # historial máximo que se envía a los cerebros


class Axtra:
    def __init__(self, cerebros: dict[str, Cerebro], orden: list[str], sistema: str,
                 modo: str = "auto") -> None:
        self.cerebros = cerebros
        self.orden = [n for n in orden if n in cerebros]
        self.sistema = sistema
        self.historial: list[Mensaje] = []
        self.modo = "auto"
        self.cambiar_modo(modo)

    @classmethod
    def desde_config(cls, config: Config) -> "Axtra":
        cerebros: dict[str, Cerebro] = {
            "claude": CerebroClaude(config.anthropic_key, config.claude_model),
            "gemini": CerebroGemini(config.gemini_key, config.gemini_model),
            "grok": CerebroGrok(config.xai_key, config.grok_model),
        }
        return cls(cerebros, config.orden, config.sistema, config.cerebro)

    def disponibles(self) -> list[str]:
        return [n for n in CEREBROS if n in self.cerebros and self.cerebros[n].disponible()]

    def cambiar_modo(self, modo: str) -> None:
        modo = modo.strip().lower()
        if modo != "auto" and modo not in self.cerebros:
            raise ValueError(f"Cerebro desconocido: {modo}. Opciones: auto, {', '.join(CEREBROS)}")
        self.modo = modo

    def _candidatos(self) -> list[str]:
        """Orden en que se intentan los cerebros: el elegido primero, luego el resto."""
        orden = list(self.orden) + [n for n in CEREBROS if n not in self.orden]
        if self.modo != "auto":
            orden = [self.modo] + [n for n in orden if n != self.modo]
        return [n for n in orden if n in self.cerebros and self.cerebros[n].disponible()]

    def preguntar(self, texto: str) -> tuple[str, str]:
        """Envía la pregunta. Devuelve (cerebro que respondió, respuesta).

        Si un cerebro falla, se intenta con el siguiente disponible.
        """
        candidatos = self._candidatos()
        if not candidatos:
            raise ErrorCerebro("No hay cerebros disponibles. Revisa las llaves en tu archivo .env.")

        mensajes = self.historial[-MAX_MENSAJES:] + [Mensaje("user", texto)]
        errores = []
        for nombre in candidatos:
            try:
                respuesta = self.cerebros[nombre].responder(mensajes, self.sistema)
            except ErrorCerebro as e:
                errores.append(str(e))
                continue
            self.historial += [Mensaje("user", texto), Mensaje("assistant", respuesta)]
            return nombre, respuesta
        raise ErrorCerebro("Ningún cerebro pudo responder:\n  - " + "\n  - ".join(errores))

    def consultar_todos(self, texto: str) -> dict[str, str]:
        """Hace la misma pregunta a todos los cerebros disponibles (no toca el historial)."""
        mensajes = self.historial[-MAX_MENSAJES:] + [Mensaje("user", texto)]
        resultados = {}
        for nombre in self.disponibles():
            try:
                resultados[nombre] = self.cerebros[nombre].responder(mensajes, self.sistema)
            except ErrorCerebro as e:
                resultados[nombre] = f"[error] {e}"
        return resultados

    def limpiar(self) -> None:
        self.historial.clear()
