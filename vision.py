"""Visión de Axtra con la cámara del computador.

- "¿Qué ves?": toma una foto y Axtra (Claude) la analiza.
- "Lee este documento": cuenta regresiva, foto en alta calidad, y lo lee / resume / explica.
- Te reconoce la cara y te saluda cuando llegas (después de un rato sin verte).

Privacidad: las imágenes se procesan en memoria. Solo se guardan las fotos de documentos que
pidas leer (en mis_documentos/capturas). Tu cara registrada queda en data/ y nunca sale del PC.
El saludo por cámara solo reconoce TU cara; no guarda ni identifica a otras personas.
"""
import base64
import threading
import time
from datetime import datetime

import numpy as np

from config import CAMERA_GREETING, CAMERA_INDEX, DATA_DIR, DOCS_DIR, USER_NAME

FACE_MODEL = DATA_DIR / "cara_modelo.yml"
ABSENCE_MIN = 10          # minutos sin verte para volver a saludarte
LBPH_THRESHOLD = 65       # menor = más estricto


def _cv2():
    import cv2

    return cv2


# ---------- Cámara ----------
class Camera:
    """Mantiene la cámara abierta en segundo plano y guarda el último cuadro."""

    def __init__(self, index: int = CAMERA_INDEX):
        self.index = index
        self.frame = None
        self.lock = threading.Lock()
        self.running = False

    def _open(self):
        cv2 = _cv2()
        import os

        cap = cv2.VideoCapture(self.index, cv2.CAP_DSHOW) if os.name == "nt" else cv2.VideoCapture(self.index)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        if not cap.isOpened():
            raise RuntimeError("No pude abrir la cámara (¿está tapada, en uso por otra app o sin permiso?)")
        return cap

    def start(self):
        self.running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        while self.running:
            try:
                cap = self._open()
                while self.running:
                    ok, f = cap.read()
                    if ok:
                        with self.lock:
                            self.frame = f
                    time.sleep(0.08)
                cap.release()
            except Exception as e:
                print(f"  (cámara: {e}; reintento en 30 s)")
                time.sleep(30)

    def snapshot(self):
        if self.running:
            for _ in range(30):
                with self.lock:
                    if self.frame is not None:
                        return self.frame.copy()
                time.sleep(0.1)
        cap = self._open()  # cámara bajo demanda
        try:
            frame = None
            for _ in range(12):  # los primeros cuadros salen oscuros mientras ajusta la exposición
                ok, f = cap.read()
                if ok:
                    frame = f
            if frame is None:
                raise RuntimeError("La cámara no entregó imagen")
            return frame
        finally:
            cap.release()


camera = Camera()


def _jpeg_b64(frame, max_w: int = 1280, quality: int = 85) -> str:
    cv2 = _cv2()
    h, w = frame.shape[:2]
    if w > max_w:
        frame = cv2.resize(frame, (max_w, int(h * max_w / w)))
    ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return base64.b64encode(buf.tobytes()).decode()


def _image_result(frame, note: str, max_w: int = 1280):
    return {"__imagen_b64__": _jpeg_b64(frame, max_w), "nota": note}


# ---------- Herramientas para el cerebro ----------
def ver_camara(pregunta: str = "") -> dict:
    frame = camera.snapshot()
    return _image_result(frame, f"Foto de la cámara del PC de {USER_NAME} tomada ahora. "
                                f"Pregunta: {pregunta or '¿qué ves?'} Describe con naturalidad y brevedad.")


def leer_documento(instruccion: str = "léelo y resúmelo") -> dict:
    import autonomy
    from audio import beep

    if autonomy.speaker:
        autonomy.speaker("Ponga el documento frente a la cámara, bien iluminado. Tomo la foto en tres segundos.")
    time.sleep(3)
    try:
        beep(freq=1200, duration=0.1)
    except Exception:
        pass
    frame = camera.snapshot()
    DOCS_DIR.joinpath("capturas").mkdir(exist_ok=True)
    path = DOCS_DIR / "capturas" / f"documento_{datetime.now():%Y%m%d_%H%M%S}.jpg"
    _cv2().imwrite(str(path), frame)
    return _image_result(frame, f"Foto de un documento que {USER_NAME} puso frente a la cámara "
                                f"(guardada en {path.name}). Instrucción: {instruccion}. Si no se lee bien, "
                                "pídele que lo acerque o mejore la luz.", max_w=1600)


def quien_esta() -> dict:
    if not watcher.enabled:
        return {"nota": "El reconocimiento de cara no está activo. Registra tu cara con: python axtra.py cara"}
    mins = (time.time() - watcher.last_owner) / 60 if watcher.last_owner else None
    return {"felipe_visto_hace_minutos": round(mins, 1) if mins is not None else "no te he visto aún",
            "personas_en_camara_ahora": watcher.faces_now}


# ---------- Reconocimiento de cara (OpenCV, sin internet) ----------
class Faces:
    def __init__(self):
        cv2 = _cv2()
        self.cv2 = cv2
        self.det = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.rec = None
        if FACE_MODEL.exists():
            self.rec = cv2.face.LBPHFaceRecognizer_create()
            self.rec.read(str(FACE_MODEL))

    def crops(self, frame):
        cv2 = self.cv2
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        scale = 640 / gray.shape[1] if gray.shape[1] > 640 else 1.0
        small = cv2.resize(gray, None, fx=scale, fy=scale) if scale != 1.0 else gray
        faces = self.det.detectMultiScale(small, scaleFactor=1.15, minNeighbors=6, minSize=(60, 60))
        out = []
        for (x, y, w, h) in faces:
            x, y, w, h = [int(v / scale) for v in (x, y, w, h)]
            face = cv2.equalizeHist(cv2.resize(gray[y:y + h, x:x + w], (200, 200)))
            out.append(face)
        return out

    def is_owner(self, crop) -> bool:
        if self.rec is None:
            return False
        label, dist = self.rec.predict(crop)
        return label == 1 and dist < LBPH_THRESHOLD


def enroll_face() -> None:
    """python axtra.py cara → registra tu cara (unos 20 segundos)."""
    print("Mira a la cámara. Mueve un poco la cabeza (izquierda, derecha, arriba) durante 20 segundos.")
    print("Hazlo con la luz que normalmente tienes en tu cuarto.")
    input("Presiona Enter para empezar...")
    f = Faces()
    samples, t0 = [], time.time()
    cam = Camera()
    cap = cam._open()
    try:
        while time.time() - t0 < 20 and len(samples) < 60:
            ok, frame = cap.read()
            if not ok:
                continue
            crops = f.crops(frame)
            if len(crops) == 1:
                samples.append(crops[0])
                print(f"  muestras: {len(samples)}", end="\r")
            time.sleep(0.25)
    finally:
        cap.release()
    if len(samples) < 15:
        raise SystemExit(f"\nSolo capté {len(samples)} muestras. Mejora la luz y vuelve a intentarlo.")
    rec = f.cv2.face.LBPHFaceRecognizer_create()
    rec.train(samples, np.ones(len(samples), dtype=np.int32))
    rec.write(str(FACE_MODEL))
    print(f"\nCara registrada con {len(samples)} muestras. Reinicia Axtra para que te salude.")


class Watcher:
    """Revisa la cámara cada segundo y te saluda cuando llegas."""

    def __init__(self):
        self.enabled = False
        self.last_owner = 0.0
        self.faces_now = 0
        self.started = time.time()

    def start(self):
        if not (CAMERA_GREETING and FACE_MODEL.exists()):
            return
        self.faces = Faces()
        self.enabled = True
        camera.start()
        threading.Thread(target=self._loop, daemon=True).start()
        print("  - Cámara activa: te saludaré cuando llegues")

    def _greet(self):
        import autonomy

        h = datetime.now().hour
        saludo = "Buenos días" if h < 12 else "Buenas tardes" if h < 19 else "Buenas noches"
        pend = autonomy.notices.qsize()
        extra = f" Tengo {pend} aviso{'s' if pend != 1 else ''} para usted." if pend else ""
        if autonomy.speaker:
            autonomy.speaker(f"{saludo}, señor. Bienvenido de vuelta.{extra}")

    def _loop(self):
        import power
        from config import BATTERY_SAVER

        while True:
            try:
                # Con batería: apaga la cámara de fondo (gasta procesador y energía) hasta que conectes el cargador
                if BATTERY_SAVER and power.on_battery():
                    if camera.running:
                        camera.running = False
                        print("  (batería: cámara de fondo en pausa)")
                    time.sleep(15)
                    continue
                if not camera.running:
                    camera.start()
                    time.sleep(2)
                with camera.lock:
                    frame = None if camera.frame is None else camera.frame.copy()
                if frame is not None:
                    crops = self.faces.crops(frame)
                    self.faces_now = len(crops)
                    if any(self.faces.is_owner(c) for c in crops):
                        now = time.time()
                        away = now - self.last_owner if self.last_owner else now - self.started
                        if away > ABSENCE_MIN * 60 and now - self.started > 60:
                            self._greet()
                        self.last_owner = now
            except Exception as e:
                print(f"  (visión: {e})")
            time.sleep(1)


watcher = Watcher()

TOOL_SCHEMAS = [
    {"name": "ver_camara", "description": "Toma una foto con la cámara del PC para ver lo que hay frente a Felipe (objetos, ropa, lugar, lo que te muestra). Úsala cuando pregunte '¿qué ves?' o te muestre algo.",
     "input_schema": {"type": "object", "properties": {"pregunta": {"type": "string"}}}},
    {"name": "leer_documento", "description": "Felipe pone un documento, libro, recibo o tarea frente a la cámara: cuenta 3 segundos, toma la foto y lo lees, resumes, explicas o transcribes según la instrucción.",
     "input_schema": {"type": "object", "properties": {"instruccion": {"type": "string"}}}},
    {"name": "quien_esta", "description": "Si Felipe está frente a la cámara y cuántas personas se ven ahora.",
     "input_schema": {"type": "object", "properties": {}}},
]
FUNCS = {"ver_camara": ver_camara, "leer_documento": leer_documento, "quien_esta": quien_esta}
