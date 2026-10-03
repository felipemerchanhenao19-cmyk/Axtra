ARG BASE=python:3.12-slim
FROM ${BASE}
WORKDIR /app
COPY servidor/requirements.txt servidor/requirements.txt
RUN pip install --no-cache-dir -r servidor/requirements.txt
COPY servidor servidor
ENV AXTRA_DATOS=/datos
VOLUME /datos
EXPOSE 8080 8090
CMD ["python", "-m", "servidor.arranque"]
