import os
import tempfile

# Datos de prueba en una carpeta temporal y sin llaves reales
os.environ["AXTRA_DATOS"] = tempfile.mkdtemp(prefix="axtra_pruebas_")
for k in ("GROQ_API_KEY", "CEREBRAS_API_KEY", "GEMINI_API_KEY", "OPENROUTER_API_KEY", "ANTHROPIC_API_KEY",
          "XAI_API_KEY", "TAVILY_API_KEY", "CF_ACCESS_EQUIPO", "CF_ACCESS_AUD", "AXTRA_MODO"):
    os.environ[k] = ""
os.environ["AXTRA_CORREO"] = "felipe@ejemplo.com"
