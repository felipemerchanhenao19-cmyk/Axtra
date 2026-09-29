"""Interfaz de terminal de Axtra (funciona en PowerShell, CMD y terminales Linux/Mac)."""

from __future__ import annotations

import os

from .cerebros import ErrorCerebro
from .config import cargar_config
from .nucleo import Axtra

AZUL, VERDE, AMARILLO, ROJO, GRIS, FIN = (
    "\033[96m", "\033[92m", "\033[93m", "\033[91m", "\033[90m", "\033[0m"
)

AYUDA = f"""{AMARILLO}Comandos:{FIN}
  /cerebro <auto|claude|gemini|grok>  cambia el cerebro que responde
  /todos <pregunta>                   pregunta a todos los cerebros y compara
  /estado                             muestra cerebros disponibles y modo actual
  /limpiar                            borra la memoria de la conversación
  /ayuda                              muestra esta ayuda
  /salir                              cierra Axtra"""


def _activar_colores() -> None:
    # Activa los códigos de color ANSI en la consola de Windows.
    if os.name == "nt":
        os.system("")


def _estado(axtra: Axtra) -> str:
    disp = axtra.disponibles()
    return (f"{GRIS}Modo: {axtra.modo} | Cerebros disponibles: "
            f"{', '.join(disp) if disp else 'ninguno'}{FIN}")


def _comando(axtra: Axtra, linea: str) -> bool:
    """Ejecuta un comando. Devuelve False si hay que salir."""
    partes = linea.split(maxsplit=1)
    cmd, arg = partes[0].lower(), (partes[1] if len(partes) > 1 else "")

    if cmd in ("/salir", "/exit"):
        return False
    if cmd == "/ayuda":
        print(AYUDA)
    elif cmd == "/estado":
        print(_estado(axtra))
    elif cmd == "/limpiar":
        axtra.limpiar()
        print(f"{GRIS}Memoria borrada.{FIN}")
    elif cmd == "/cerebro":
        try:
            axtra.cambiar_modo(arg or "auto")
            print(f"{GRIS}Ahora responde: {axtra.modo}{FIN}")
        except ValueError as e:
            print(f"{ROJO}{e}{FIN}")
    elif cmd == "/todos":
        if not arg:
            print(f"{ROJO}Uso: /todos <pregunta>{FIN}")
        for nombre, respuesta in axtra.consultar_todos(arg).items():
            print(f"\n{VERDE}[{nombre}]{FIN} {respuesta}")
    else:
        print(f"{ROJO}Comando desconocido. Escribe /ayuda{FIN}")
    return True


def main() -> None:
    _activar_colores()
    axtra = Axtra.desde_config(cargar_config())

    print(f"{AZUL}=== AXTRA en línea ==={FIN}")
    print(_estado(axtra))
    print(f"{GRIS}Escribe /ayuda para ver los comandos.{FIN}")
    if not axtra.disponibles():
        print(f"{ROJO}No hay llaves configuradas. Copia .env.example como .env y agrégalas.{FIN}")

    while True:
        try:
            linea = input(f"\n{AZUL}Tú > {FIN}").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not linea:
            continue
        if linea.startswith("/"):
            if not _comando(axtra, linea):
                break
            continue
        try:
            nombre, respuesta = axtra.preguntar(linea)
            print(f"{VERDE}Axtra [{nombre}] >{FIN} {respuesta}")
        except ErrorCerebro as e:
            print(f"{ROJO}{e}{FIN}")

    print(f"{AZUL}Axtra desconectado. Hasta pronto.{FIN}")
