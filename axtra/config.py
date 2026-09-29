"""Carga la configuración de Axtra desde variables de entorno / archivo .env."""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

CEREBROS = ("claude", "gemini", "grok")

SISTEMA = (
    "Eres Axtra, un asistente personal de inteligencia artificial al estilo de JARVIS. "
    "Respondes en español, de forma clara, directa y con un toque de cortesía. "
    "Si no sabes algo, lo dices en lugar de inventarlo."
)


@dataclass
class Config:
    anthropic_key: str = ""
    gemini_key: str = ""
    xai_key: str = ""
    claude_model: str = "claude-opus-5-5"
    gemini_model: str = "gemini-2.5-flash"
    grok_model: str = "grok-4"
    cerebro: str = "auto"
    orden: list[str] = field(default_factory=lambda: ["gemini", "grok", "claude"])
    sistema: str = SISTEMA


def cargar_config() -> Config:
    load_dotenv()
    orden = [
        c.strip().lower()
        for c in os.getenv("AXTRA_ORDEN", "gemini,grok,claude").split(",")
        if c.strip().lower() in CEREBROS
    ]
    return Config(
        anthropic_key=os.getenv("ANTHROPIC_API_KEY", ""),
        gemini_key=os.getenv("GEMINI_API_KEY", ""),
        xai_key=os.getenv("XAI_API_KEY", ""),
        claude_model=os.getenv("CLAUDE_MODEL", "claude-opus-5-5"),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
        grok_model=os.getenv("GROK_MODEL", "grok-4"),
        cerebro=os.getenv("AXTRA_CEREBRO", "auto").strip().lower(),
        orden=orden or list(CEREBROS),
    )
