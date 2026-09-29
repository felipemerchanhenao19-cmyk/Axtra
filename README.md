# Axtra

Asistente personal de IA al estilo JARVIS, con **tres cerebros**:

| Cerebro | Proveedor | Variable de la llave |
|---------|-----------|----------------------|
| Claude  | Anthropic | `ANTHROPIC_API_KEY`  |
| Gemini  | Google    | `GEMINI_API_KEY`     |
| Grok    | xAI       | `XAI_API_KEY`        |

En modo `auto`, Axtra usa los cerebros en el orden de `AXTRA_ORDEN` y, si uno
falla (sin crédito, sin internet, límite de uso…), pasa automáticamente al siguiente.
Los cerebros sin llave simplemente se saltan.

## Instalación (Windows PowerShell, Python 3.10+)

```powershell
cd Axtra
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env    # luego abre .env y pon tus llaves
python main.py
```

## Comandos dentro de Axtra

| Comando | Qué hace |
|---------|----------|
| `/cerebro claude` (o `gemini`, `grok`, `auto`) | Cambia el cerebro que responde |
| `/todos <pregunta>` | Hace la misma pregunta a todos los cerebros para comparar |
| `/estado` | Muestra el modo actual y los cerebros disponibles |
| `/limpiar` | Borra la memoria de la conversación |
| `/ayuda` | Lista los comandos |
| `/salir` | Cierra Axtra |

Todos los cerebros comparten la misma memoria de la conversación, así que puedes
cambiar de cerebro a mitad de una charla y el nuevo sabe de qué venían hablando.

## Estructura

```
main.py                  # punto de entrada
axtra/config.py          # lee el .env
axtra/nucleo.py          # elige cerebro, respaldo automático y memoria
axtra/terminal.py        # interfaz de consola
axtra/cerebros/          # un archivo por cerebro (claude, gemini, grok)
tests/                   # pruebas (python -m pytest)
```

Para agregar un cerebro nuevo: crea una clase en `axtra/cerebros/` que herede de
`Cerebro` (métodos `disponible` y `responder`) y regístrala en `Axtra.desde_config`.
