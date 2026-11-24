ARG BASE=python:3.12-slim
FROM ${BASE}
WORKDIR /app
# ffmpeg: el agente de contenido arma los videos de TikTok e Instagram
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*
COPY servidor/requirements.txt servidor/requirements.txt
RUN pip install --no-cache-dir -r servidor/requirements.txt
COPY servidor servidor
ENV AXTRA_DATOS=/datos
VOLUME /datos
EXPOSE 8080 8090
CMD ["python", "-m", "servidor.arranque"]
