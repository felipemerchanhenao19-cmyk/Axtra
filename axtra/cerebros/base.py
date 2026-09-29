"""Interfaz común para todos los cerebros de Axtra."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Mensaje:
    rol: str  # "user" o "assistant"
    texto: str


class ErrorCerebro(Exception):
    """Un cerebro no pudo responder (sin llave, error de red, límite, etc.)."""


class Cerebro(ABC):
    nombre: str = "cerebro"

    @abstractmethod
    def disponible(self) -> bool:
        """True si el cerebro tiene lo necesario (llave API) para funcionar."""

    @abstractmethod
    def responder(self, historial: list[Mensaje], sistema: str) -> str:
        """Devuelve la respuesta al último mensaje del historial."""
