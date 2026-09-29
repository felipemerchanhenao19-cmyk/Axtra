"""Control del mouse y el teclado por voz, SIN IA (gratis).

1. Órdenes de mouse: "mueve el mouse a la derecha", "más arriba", "un poco a la izquierda",
   "clic", "doble clic", "clic derecho", "baja la página", "arrastra" / "suelta".
2. Cuadrícula: "cuadrícula" divide la pantalla en 9 cuadros numerados; dices un número y ese cuadro
   se divide otra vez; "clic" hace clic en el centro del cuadro elegido.
3. Clic por nombre: "haz clic en Enviar". Busca botones y menús con UI Automation de Windows y,
   si no los encuentra, lee el texto de la pantalla con el OCR de Windows.
4. Teclado: "escribe aquí hola", "presiona enter", "copia", "pega", "deshacer", "cambia de ventana"...
"""
import queue
import re
import threading
import time
import unicodedata

last_action = 0.0          # para escuchar más tiempo mientras usas el mouse por voz
_drag = False


def recent(seconds: float = 45) -> bool:
    return time.time() - last_action < seconds or grid.active


def _mark():
    global last_action
    last_action = time.time()


def _pg():
    import pyautogui

    pyautogui.FAILSAFE = False   # no se detiene si el mouse llega a una esquina
    pyautogui.PAUSE = 0.02
    return pyautogui


def _norm(t: str) -> str:
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn").strip()


# ---------------- Mouse básico ----------------
def mover(direccion: str, cantidad: str = "normal") -> None:
    pg = _pg()
    step = {"poco": 40, "normal": 150, "mucho": 450}[cantidad]
    dx, dy = {"arriba": (0, -step), "abajo": (0, step), "izquierda": (-step, 0), "derecha": (step, 0)}[direccion]
    if _drag:
        pg.moveRel(dx, dy, duration=0.25)
    else:
        pg.moveRel(dx, dy, duration=0.12)
    _mark()


def centro() -> None:
    pg = _pg()
    w, h = pg.size()
    pg.moveTo(w // 2, h // 2, duration=0.12)
    _mark()


def clic(tipo: str = "izquierdo") -> None:
    pg = _pg()
    if grid.active:
        x, y = grid.center()
        grid.hide()
        time.sleep(0.15)
        pg.moveTo(x, y)
    if tipo == "doble":
        pg.doubleClick()
    elif tipo == "derecho":
        pg.rightClick()
    else:
        pg.click()
    _mark()


def rueda(direccion: str, cantidad: str = "normal") -> None:
    n = {"poco": 3, "normal": 8, "mucho": 25}[cantidad]
    _pg().scroll(n * 100 if direccion == "arriba" else -n * 100)
    _mark()


def arrastrar(empezar: bool) -> None:
    global _drag
    pg = _pg()
    if grid.active:
        x, y = grid.center()
        grid.hide()
        pg.moveTo(x, y)
    (pg.mouseDown if empezar else pg.mouseUp)()
    _drag = empezar
    _mark()


# ---------------- Teclado ----------------
KEYS = {
    "enter": ["enter"], "intro": ["enter"], "escape": ["esc"], "tab": ["tab"], "borrar": ["backspace"],
    "suprimir": ["delete"], "espacio": ["space"], "inicio": ["home"], "fin": ["end"],
    "copia": ["ctrl", "c"], "copiar": ["ctrl", "c"], "pega": ["ctrl", "v"], "pegar": ["ctrl", "v"],
    "corta": ["ctrl", "x"], "cortar": ["ctrl", "x"], "deshacer": ["ctrl", "z"], "deshaz": ["ctrl", "z"],
    "rehacer": ["ctrl", "y"], "selecciona todo": ["ctrl", "a"], "seleccionar todo": ["ctrl", "a"],
    "guarda": ["ctrl", "s"], "guardar": ["ctrl", "s"], "nueva pestana": ["ctrl", "t"],
    "cierra la pestana": ["ctrl", "w"], "cerrar pestana": ["ctrl", "w"], "recarga": ["f5"], "recargar": ["f5"],
    "atras": ["alt", "left"], "adelante": ["alt", "right"], "cambia de ventana": ["alt", "tab"],
    "cambiar de ventana": ["alt", "tab"], "minimiza": ["win", "down"], "minimizar": ["win", "down"],
    "maximiza": ["win", "up"], "maximizar": ["win", "up"], "escritorio": ["win", "d"],
    "muestra el escritorio": ["win", "d"], "cierra la ventana": ["alt", "f4"], "cerrar ventana": ["alt", "f4"],
    "captura de pantalla": ["win", "shift", "s"], "recorte": ["win", "shift", "s"],
    "busca en la pagina": ["ctrl", "f"], "zoom": ["ctrl", "+"], "aleja": ["ctrl", "-"],
}


def teclas(nombre: str) -> None:
    _pg().hotkey(*KEYS[nombre])
    _mark()


def escribir(texto: str) -> None:
    """Escribe con tildes y ñ usando el portapapeles (más confiable que teclear letra por letra)."""
    try:
        import pyperclip

        old = pyperclip.paste()
        pyperclip.copy(texto)
        _pg().hotkey("ctrl", "v")
        time.sleep(0.2)
        pyperclip.copy(old)
    except Exception:
        _pg().write(texto, interval=0.01)
    _mark()


# ---------------- Clic por nombre ----------------
def _uia_find(target: str):
    """Busca un botón, enlace o menú por su nombre en la ventana activa (UI Automation)."""
    import uiautomation as auto

    with auto.UIAutomationInitializerInThread():
        root = auto.GetForegroundControl()
        if root is None:
            return None
        root = root.GetTopLevelControl() or root
        best, t0 = None, time.time()
        for c, _depth in auto.WalkControl(root, includeTop=True, maxDepth=40):
            if time.time() - t0 > 3:
                break
            try:
                name = _norm(c.Name or "")
                if not name or target not in name or c.IsOffscreen:
                    continue
                r = c.BoundingRectangle
                if r.width() <= 0 or r.height() <= 0:
                    continue
                score = (name == target) * 3 + name.startswith(target) + ("Button" in c.ControlTypeName) \
                    + ("Hyperlink" in c.ControlTypeName) + ("MenuItem" in c.ControlTypeName)
                if best is None or score > best[0] or (score == best[0] and len(name) < best[2]):
                    best = (score, (r.xcenter(), r.ycenter()), len(name))
                    if name == target and score >= 4:
                        break
            except Exception:
                continue
        return best[1] if best else None


def _ocr_find(target: str):
    """Lee el texto de la pantalla con el OCR de Windows (gratis, sin internet) y busca la frase."""
    import asyncio

    from PIL import ImageGrab
    from winsdk.windows.globalization import Language
    from winsdk.windows.graphics.imaging import BitmapAlphaMode, BitmapPixelFormat, SoftwareBitmap
    from winsdk.windows.media.ocr import OcrEngine
    from winsdk.windows.storage.streams import DataWriter

    img = ImageGrab.grab().convert("RGBA")
    w, h = img.size
    dw = DataWriter()
    dw.write_bytes(img.tobytes())
    bmp = SoftwareBitmap.create_copy_from_buffer(dw.detach_buffer(), BitmapPixelFormat.RGBA8, w, h,
                                                 BitmapAlphaMode.PREMULTIPLIED)
    engine = OcrEngine.try_create_from_language(Language("es")) or OcrEngine.try_create_from_user_profile_languages()

    async def run():
        return await engine.recognize_async(bmp)

    result = asyncio.run(run())
    want = target.split()
    for line in result.lines:
        words = list(line.words)
        texts = [_norm(x.text).strip(".,:;!?¿¡()[]\"'") for x in words]
        for i in range(len(texts) - len(want) + 1):
            if all(want[j] in texts[i + j] for j in range(len(want))):
                rs = [words[i + j].bounding_rect for j in range(len(want))]
                x1 = min(r.x for r in rs)
                y1 = min(r.y for r in rs)
                x2 = max(r.x + r.width for r in rs)
                y2 = max(r.y + r.height for r in rs)
                return int((x1 + x2) / 2), int((y1 + y2) / 2)
    return None


# Frases del botón real "Saltar anuncio" (varía según el idioma/versión de YouTube)
_SALTAR_FRASES = ("saltar anuncio", "saltar anuncios", "omitir anuncio", "omitir anuncios", "skip ad", "skip ads", "skip")
# La cuenta regresiva ("puedes saltar el anuncio en 5") contiene las mismas palabras pero AÚN NO es
# clicable; si Axtra le hace clic ahí, en realidad le da al video y lo pausa. Esto la distingue.
_CUENTA_REGRESIVA = re.compile(r"\b(puedes?|podr[aá]s?)\b|\ben\s*\d|\d\s*s(eg)?\b|:\d\d\b|\d$")


def _uia_find_saltar():
    """Una sola pasada por la pantalla buscando el botón REAL de saltar anuncio (no la cuenta regresiva)."""
    import uiautomation as auto

    with auto.UIAutomationInitializerInThread():
        root = auto.GetForegroundControl()
        if root is None:
            return None
        root = root.GetTopLevelControl() or root
        best, t0 = None, time.time()
        for c, _depth in auto.WalkControl(root, includeTop=True, maxDepth=40):
            if time.time() - t0 > 1.5:
                break
            try:
                name = _norm(c.Name or "")
                if not name or c.IsOffscreen or not any(p in name for p in _SALTAR_FRASES):
                    continue
                if _CUENTA_REGRESIVA.search(name):
                    continue
                r = c.BoundingRectangle
                if r.width() <= 0 or r.height() <= 0:
                    continue
                es_boton = ("Button" in c.ControlTypeName) or ("Hyperlink" in c.ControlTypeName)
                score = es_boton * 2 + (name in _SALTAR_FRASES)
                if best is None or score > best[0]:
                    best = (score, (r.xcenter(), r.ycenter()))
            except Exception:
                continue
        return best[1] if best else None


def _ocr_find_saltar():
    """Una sola captura + OCR buscando el texto real del botón, descartando la cuenta regresiva."""
    import asyncio

    from PIL import ImageGrab
    from winsdk.windows.globalization import Language
    from winsdk.windows.graphics.imaging import BitmapAlphaMode, BitmapPixelFormat, SoftwareBitmap
    from winsdk.windows.media.ocr import OcrEngine
    from winsdk.windows.storage.streams import DataWriter

    img = ImageGrab.grab().convert("RGBA")
    w, h = img.size
    dw = DataWriter()
    dw.write_bytes(img.tobytes())
    bmp = SoftwareBitmap.create_copy_from_buffer(dw.detach_buffer(), BitmapPixelFormat.RGBA8, w, h,
                                                 BitmapAlphaMode.PREMULTIPLIED)
    engine = OcrEngine.try_create_from_language(Language("es")) or OcrEngine.try_create_from_user_profile_languages()

    async def run():
        return await engine.recognize_async(bmp)

    result = asyncio.run(run())
    for line in result.lines:
        texto = _norm(line.text)
        if any(p in texto for p in ("saltar anuncio", "omitir anuncio", "skip ad")) and not _CUENTA_REGRESIVA.search(texto):
            words = list(line.words)
            rs = [x.bounding_rect for x in words]
            x1, y1 = min(r.x for r in rs), min(r.y for r in rs)
            x2, y2 = max(r.x + r.width for r in rs), max(r.y + r.height for r in rs)
            return int((x1 + x2) / 2), int((y1 + y2) / 2)
    return None


def buscar_y_saltar_anuncio() -> bool:
    """Un solo intento: busca el botón real (UIA, luego OCR si hace falta) y le hace clic. True si lo logró."""
    for finder in (_uia_find_saltar, _ocr_find_saltar):
        try:
            pos = finder()
        except ImportError as e:
            print(f"  (saltar anuncio: falta instalar {e.name}; ejecuta python instalar.py)")
            continue
        except Exception as e:
            print(f"  (saltar anuncio, {finder.__name__}: {e})")
            continue
        if pos:
            if grid.active:
                grid.hide()
            pg = _pg()
            pg.moveTo(*pos, duration=0.1)
            pg.click()
            _mark()
            return True
    return False


def clic_en(nombre: str, tipo: str = "izquierdo") -> str:
    target = _norm(nombre).strip(" .")
    target = re.sub(r"^(el|la|los|las|boton|botón|enlace|opcion|menu|pestana|icono)\s+", "", target)
    if grid.active:
        grid.hide()
    pos = None
    for finder in (_uia_find, _ocr_find):
        try:
            pos = finder(target)
        except ImportError as e:
            print(f"  (clic por nombre: falta instalar {e.name}; ejecuta python instalar.py)")
        except Exception as e:
            print(f"  (clic por nombre, {finder.__name__}: {e})")
        if pos:
            break
    if not pos:
        return f"No encuentro '{nombre}' en la pantalla, señor. Pruebe con la cuadrícula."
    pg = _pg()
    pg.moveTo(*pos, duration=0.15)
    {"doble": pg.doubleClick, "derecho": pg.rightClick}.get(tipo, pg.click)()
    _mark()
    return " "


# ---------------- Cuadrícula ----------------
class Grid:
    """Ventana transparente encima de todo con 9 cuadros numerados."""

    def __init__(self):
        self.active = False
        self.region = None       # (x, y, ancho, alto)
        self._q = queue.Queue()
        self._thread = None

    def _ensure(self):
        if self._thread is None:
            import ui

            self._thread = True
            ui.call(self._ui)
            time.sleep(0.3)

    def _ui(self, master):
        import tkinter as tk

        root = tk.Toplevel(master)
        root.withdraw()
        root.overrideredirect(True)
        root.attributes("-topmost", True)
        key = "#010101"
        root.configure(bg=key)
        try:
            root.attributes("-transparentcolor", key)   # el fondo no se ve y deja pasar los clics
        except tk.TclError:
            root.attributes("-alpha", 0.4)
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{sw}x{sh}+0+0")
        cv = tk.Canvas(root, bg=key, highlightthickness=0, width=sw, height=sh)
        cv.pack(fill="both", expand=True)
        self._scale = (sw, sh)

        def draw():
            cv.delete("all")
            x, y, w, h = self._to_tk(self.region)
            for i in range(4):
                cv.create_line(x + w * i / 3, y, x + w * i / 3, y + h, fill="#00e5ff", width=2)
                cv.create_line(x, y + h * i / 3, x + w, y + h * i / 3, fill="#00e5ff", width=2)
            size = max(10, int(min(w, h) / 9))
            for n in range(9):
                cx, cy = x + w * (n % 3 + 0.5) / 3, y + h * (n // 3 + 0.5) / 3
                cv.create_text(cx + 2, cy + 2, text=str(n + 1), fill="#000000", font=("Segoe UI", size, "bold"))
                cv.create_text(cx, cy, text=str(n + 1), fill="#ffd400", font=("Segoe UI", size, "bold"))

        def poll():
            try:
                while True:
                    cmd = self._q.get_nowait()
                    if cmd == "show":
                        draw()
                        root.deiconify()
                        root.attributes("-topmost", True)
                    elif cmd == "hide":
                        root.withdraw()
            except queue.Empty:
                pass
            root.after(50, poll)

        poll()

    def _to_tk(self, region):
        """Coordenadas reales de la pantalla -> coordenadas de la ventana (por si Windows usa escala 125-150 %)."""
        pw, ph = _pg().size()
        sw, sh = getattr(self, "_scale", (pw, ph))
        fx, fy = sw / pw, sh / ph
        x, y, w, h = region
        return x * fx, y * fy, w * fx, h * fy

    def show(self):
        pg = _pg()
        w, h = pg.size()
        self.region = (0, 0, w, h)
        self.active = True
        self._ensure()
        self._q.put("show")
        _mark()

    def pick(self, n: int):
        x, y, w, h = self.region
        c, r = (n - 1) % 3, (n - 1) // 3
        self.region = (x + w * c / 3, y + h * r / 3, w / 3, h / 3)
        _pg().moveTo(*self.center(), duration=0.1)
        self._q.put("show")
        _mark()

    def center(self):
        x, y, w, h = self.region
        return int(x + w / 2), int(y + h / 2)

    def hide(self):
        self.active = False
        self._q.put("hide")


grid = Grid()


# ---------------- Frases ----------------
NUMS = {"uno": 1, "un": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6,
        "siete": 7, "ocho": 8, "nueve": 9}
CLICK = r"(clic|click|clik|klik|clip|cliq)"
DIRS = {"arriba": "arriba", "abajo": "abajo", "izquierda": "izquierda", "derecha": "derecha",
        "subir": "arriba", "bajar": "abajo"}


MOVE_WORDS = set("""mueve mover muevelo lleva llevalo pon el mouse raton cursor puntero flecha un poco poquito
mucho bastante mas hacia a la al arriba abajo izquierda derecha""".split())


# Órdenes de una sola palabra que se pueden decir pegadas a "Axtra" ("Axtra, clic")
ONE_WORD = {"cuadricula", "grilla", "clic", "click", "arriba", "abajo", "izquierda", "derecha", "copia",
            "pega", "enter", "suelta", "arrastra", "baja", "sube", "deshacer", "deshaz", "escritorio",
            "minimiza", "maximiza", "recarga", "atras", "adelante", "guarda", "escape",
            "sincronicemos", "sincronizamos", "sincronizacion", "sincronizate", "apagate", "escritorio"}


def _amount(t):
    return "poco" if re.search(r"\b(un poco|poquito|poco|un pelin)\b", t) else \
        "mucho" if re.search(r"\b(mucho|bastante|harto)\b", t) else "normal"


def handle(t: str):
    """t ya viene normalizado (sin tildes). Devuelve ' ' (hecho, sin hablar), un texto, o None."""
    # Cuadrícula
    if re.fullmatch(r"(muestra |abre |activa |pon )?(la )?(cuadricula|grilla|rejilla|numeros)", t):
        grid.show()
        return " "
    if grid.active:
        if re.fullmatch(r"(cancela|cancelar|cierra|cerrar|quita|oculta|salir)( la)?( cuadricula| grilla)?|nada", t):
            grid.hide()
            return " "
        nums = [NUMS.get(w, int(w) if w.isdigit() and 1 <= int(w) <= 9 else 0) for w in t.split()]
        if nums and all(nums) and len(nums) <= 4:
            for n in nums:
                grid.pick(n)
            return " "
    # Clic por nombre: "haz clic en enviar", "doble clic en la carpeta fotos"
    m = re.fullmatch(r"(?:haz |dale |da |pulsa |presiona |oprime )?(doble |)" + CLICK + r"( derecho)? (?:en|sobre|a) (.+)", t)
    if m:
        tipo = "doble" if m.group(1) else "derecho" if m.group(3) else "izquierdo"
        return clic_en(m.group(4), tipo)
    m = re.fullmatch(r"(?:abre|pulsa|presiona|oprime|selecciona|toca) (?:el boton|la opcion|el enlace|el menu|la pestana) (.+)", t)
    if m:
        return clic_en(m.group(1))
    # Saltar anuncios de YouTube: busca el botón "Saltar anuncio" en pantalla y le hace clic
    if re.search(r"(salta|saltate|saltalo|omite|quita|quitale)(te)?( el| los)? (anuncio|anuncios|publicidad|comercial)(s)?", t):
        for intento in range(5):          # el botón de YouTube tarda unos segundos en aparecer
            if buscar_y_saltar_anuncio():
                return " "
            if intento < 4:
                time.sleep(0.8)
        return "Todavía no veo el botón de saltar anuncio, señor; dígamelo otra vez apenas aparezca."
    # Clic simple
    if re.fullmatch(r"(haz |dale |da |un )?(doble )" + CLICK + r"( ahi| aqui)?", t):
        clic("doble")
        return " "
    if re.fullmatch(r"(haz |dale |da |un )?" + CLICK + r" derecho( ahi| aqui)?", t):
        clic("derecho")
        return " "
    if re.fullmatch(r"(haz |dale |da |un )?" + CLICK + r"( ahi| aqui| izquierdo)?", t):
        clic()
        return " "
    # Arrastrar
    if re.fullmatch(r"(arrastra|arrastrar|agarra|sostén|sosten|manten presionado)( esto| aqui)?", t):
        arrastrar(True)
        return " "
    if re.fullmatch(r"(suelta|soltar|sueltalo|deja ahi|deja)", t):
        arrastrar(False)
        return " "
    # Rueda: "baja la página", "sube un poco", "desplaza abajo"
    m = re.fullmatch(r"(baja|bajale|sube|subele|desplaza(?:te)?(?: hacia)? (?:arriba|abajo)|scroll(?: hacia)? (?:arriba|abajo))"
                     r"( la pagina| la pantalla)?( un poco| mucho| bastante| mas)?", t)
    if m:
        up = m.group(1).startswith("sub") or m.group(1).endswith("arriba")
        rueda("arriba" if up else "abajo", _amount(t))
        return " "
    # Mover: "mueve el mouse a la derecha", "más arriba", "un poco a la izquierda"
    words = t.split()
    dirs = [w for w in words if w in ("arriba", "abajo", "izquierda", "derecha")]
    if len(dirs) == 1 and all(w in MOVE_WORDS for w in words):
        mover(dirs[0], _amount(t))
        return " "
    if re.fullmatch(r"(mueve |pon |lleva )?(el )?(mouse|raton|cursor|flecha) (al|en el) centro|al centro", t):
        centro()
        return " "
    # Teclado
    m = re.fullmatch(r"(?:presiona|oprime|pulsa|tecla|dale)(?: la tecla)? (.+)", t)
    if m and m.group(1) in KEYS:
        teclas(m.group(1))
        return " "
    if t in KEYS:
        teclas(t)
        return " "
    m = re.match(r"(?:escribe aqui|escribe|teclea|digita)[: ]+(.+)$", t)
    if m and not re.search(r"\b(ensayo|correo|propuesta|documento|trabajo|carta|informe)\b", t):
        return "ESCRIBIR"   # quick.py escribe el texto original (con mayúsculas y tildes)
    return None
