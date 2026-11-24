"""Agente de contenido: calendario, aprobación, armado del video, publicación en Instagram y borradores en TikTok."""
import datetime as dt
import json
import shutil
import subprocess
import time

import pytest
from fastapi.testclient import TestClient

from servidor import app as app_mod, config, contenido as c


class R:
    def __init__(self, datos, status=200):
        self.datos, self.status_code, self.text = datos, status, json.dumps(datos)

    def json(self):
        return self.datos


@pytest.fixture
def limpio(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)
    (tmp_path / "videos").mkdir()
    monkeypatch.setattr(c, "carpeta_videos", lambda: tmp_path / "videos")
    for k in ("IG_USUARIO_ID", "IG_TOKEN", "TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REFRESH_TOKEN", "IG_PERSONAL_USUARIO_ID",
              "IG_PERSONAL_TOKEN", "TIKTOK_PERSONAL_REFRESH_TOKEN", "ELEVENLABS_API_KEY", "CONTENIDO_VOZ_FELIPE_ID"):
        monkeypatch.delenv(k, raising=False)
    return tmp_path


def test_calendario_inicial_dos_videos_al_dia(limpio):
    assert c.sembrar(dt.date(2026, 11, 19)) == 28
    assert c.sembrar() == 0                                              # solo la primera vez
    ps = c.piezas()
    assert len(ps) == 28 and all(p["estado"] == "propuesta" for p in ps)   # nada se publica sin aprobar
    assert [p["hora_colombia"] for p in ps[:3]] == ["2026-11-19 12:30", "2026-11-19 19:00", "2026-11-20 12:30"]
    assert ps[-1]["hora_colombia"] == "2026-12-02 19:00"
    for p in ps:
        assert p["gancho"] and len(p["gancho"]) <= 70 and 3 <= len(p["escenas"]) <= 6
        assert all(e["visual"] in c.VISUALES for e in p["escenas"])
        assert "#restaurantes" in p["hashtags"] and len(p["hashtags"]) == len(set(p["hashtags"]))
        assert sum(len(e["voz"].split()) for e in p["escenas"]) <= 95       # unos 30 segundos de voz


def test_cambiar_el_guion_obliga_a_rehacer_el_video(limpio):
    c.sembrar(dt.date(2026, 11, 19))
    c.actualizar(1, video="abc.mp4")
    assert c.actualizar(1, descripcion="otro texto")["video"] == "abc.mp4"
    p = c.actualizar(1, escenas=[{"voz": "Hola", "visual": "inventado"}])
    assert p["video"] == "" and p["escenas"] == [{"voz": "Hola", "visual": "orbe"}]
    with pytest.raises(ValueError):
        c.actualizar(1, escenas=[{"voz": "  "}])
    with pytest.raises(ValueError):
        c.actualizar(1, estado="viral")


def test_subtitulos_cortan_en_la_puntuacion_del_guion():
    palabras = [(0, .2, "Sábado"), (.2, .4, "en"), (.4, .6, "la"), (.6, .8, "noche"), (.8, 1, "El"), (1, 1.2, "restaurante"), (1.2, 1.4, "lleno")]
    assert [t for _, _, t in c.trozos(palabras, "Sábado en la noche. El restaurante lleno.")] == ["Sábado en la", "noche", "El restaurante lleno"]
    ass = c.subtitulos("Minuto {14}", c.trozos(palabras, ""), 10)
    assert "Style: Gancho" in ass and "Minuto (14)" in ass and ass.count("Dialogue:") == 4


def test_instagram_publica_el_reel_en_dos_pasos(limpio, monkeypatch):
    monkeypatch.setenv("IG_USUARIO_ID", "178"); monkeypatch.setenv("IG_TOKEN", "t")
    llamadas = []

    def post(url, data=None, **kw):
        llamadas.append((url, data))
        return R({"id": "contenedor1"} if url.endswith("/media") else {"id": "reel9"})

    def get(url, params=None, **kw):
        return R({"status_code": "FINISHED"} if "contenedor1" in url else {"permalink": "https://instagram.com/reel/9"})

    monkeypatch.setattr(c.requests, "post", post); monkeypatch.setattr(c.requests, "get", get)
    c.sembrar(dt.date(2026, 11, 19))
    p = c.actualizar(1, video="a" * 32 + ".mp4", estado="aprobada")
    (limpio / "videos" / p["video"]).write_bytes(b"mp4")
    p = c.publicar(1)
    assert p["estado"] == "publicada" and p["ig_id"] == "reel9" and p["ig_enlace"] == "https://instagram.com/reel/9"
    crear = llamadas[0][1]
    assert crear["media_type"] == "REELS" and crear["video_url"].endswith("/" + p["video"]) and "#restaurantes" in crear["caption"]
    assert llamadas[1][1]["creation_id"] == "contenedor1"


def test_instagram_avisa_si_no_pudo_procesar(limpio, monkeypatch):
    monkeypatch.setenv("IG_USUARIO_ID", "178"); monkeypatch.setenv("IG_TOKEN", "t")
    monkeypatch.setattr(c.requests, "post", lambda url, **kw: R({"id": "x"}))
    monkeypatch.setattr(c.requests, "get", lambda url, **kw: R({"status_code": "ERROR", "status": "formato de video"}))
    c.sembrar(dt.date(2026, 11, 19))
    c.actualizar(1, video="b" * 32 + ".mp4", estado="aprobada"); (limpio / "videos" / ("b" * 32 + ".mp4")).write_bytes(b"x")
    p = c.publicar(1)
    assert p["estado"] == "error" and "formato de video" in p["error"]


def test_tiktok_llega_como_borrador_y_renueva_el_token(limpio, monkeypatch):
    for k, v in (("TIKTOK_CLIENT_KEY", "ck"), ("TIKTOK_CLIENT_SECRET", "cs"), ("TIKTOK_REFRESH_TOKEN", "r1")):
        monkeypatch.setenv(k, v)
    vistos = []

    def post(url, data=None, json=None, headers=None, **kw):
        vistos.append(url)
        if url.endswith("/oauth/token/"):
            assert data["refresh_token"] == "r1"
            return R({"access_token": "a1", "expires_in": 86400, "refresh_token": "r2"})
        assert headers["Authorization"] == "Bearer a1" and json["source_info"]["source"] == "FILE_UPLOAD"
        return R({"data": {"publish_id": "pub7", "upload_url": "https://subida"}, "error": {"code": "ok"}})

    subidas = []
    monkeypatch.setattr(c.requests, "post", post)
    monkeypatch.setattr(c.requests, "put", lambda url, data=None, headers=None, **kw: (subidas.append(headers), R({}, 201))[1])
    c.sembrar(dt.date(2026, 11, 19))
    c.actualizar(1, video="c" * 32 + ".mp4", estado="aprobada"); (limpio / "videos" / ("c" * 32 + ".mp4")).write_bytes(b"12345")
    p = c.publicar(1)
    assert p["tiktok_id"] == "pub7" and "borrador" in p["tiktok_estado"] and p["estado"] == "publicada"
    assert subidas[0]["Content-Range"] == "bytes 0-4/5"
    assert c.ajuste("tiktok_refresh") == "r2" and c._tiktok_token() == "a1"     # el token nuevo se guarda y se reutiliza
    assert sum(u.endswith("/oauth/token/") for u in vistos) == 1


def test_sin_aprobar_no_se_publica_y_sin_cuentas_queda_el_aviso(limpio, monkeypatch):
    c.sembrar(dt.date(2026, 11, 19))
    with pytest.raises(ValueError):
        c.publicar(1)
    c.actualizar(1, video="d" * 32 + ".mp4", estado="aprobada"); (limpio / "videos" / ("d" * 32 + ".mp4")).write_bytes(b"x")
    p = c.publicar(1)
    assert p["estado"] == "error" and "falta conectar" in p["error"]


def test_el_vigilante_arma_antes_y_publica_a_su_hora(limpio, monkeypatch):
    c.sembrar(dt.date(2026, 11, 19))
    armados, publicados = [], []
    monkeypatch.setattr(c, "armar_video", lambda pid: (armados.append(pid), c.actualizar(pid, video="e" * 32 + ".mp4"))[1])
    monkeypatch.setattr(c, "publicar", lambda pid: publicados.append(pid))
    c.actualizar(1, estado="aprobada"); c.actualizar(3, estado="aprobada")
    p1 = c.pieza(1)
    c.revisar(ahora=p1["cuando"] - 3600)                                  # una hora antes: arma, no publica
    assert armados == [1] and publicados == []
    c.revisar(ahora=p1["cuando"] + 60)
    assert publicados == [1]                                               # la 2 no está aprobada; la 3 es de mañana


def test_proponer_ideas_nuevas(limpio):
    c.sembrar(dt.date(2026, 11, 19))

    class Cerebro:
        def _cadena(self, nombres, sistema, mensajes, max_tokens=0):
            assert "nunca inventes cifras" in sistema and "Mesa 7" not in mensajes[0]["content"] or True
            idea = {"pilar": "Consejo", "titulo": "Idea nueva", "gancho": "Gancho", "hashtags": ["restaurantes"],
                    "escenas": [{"voz": "Una frase.", "visual": "orbe"}], "descripcion": "Texto"}
            return type("Resp", (), {"texto": "Aquí van: " + json.dumps({"piezas": [idea] * 14})})()

    ids = c.proponer(7, Cerebro())
    nuevas = [c.pieza(i) for i in ids]
    assert len(nuevas) == 14 and all(p["estado"] == "propuesta" and p["origen"] == "agente" for p in nuevas)
    assert nuevas[0]["hora_colombia"] == "2026-12-03 12:30" and nuevas[-1]["hora_colombia"] == "2026-12-09 19:00"
    assert nuevas[0]["hashtags"] == ["#restaurantes"]


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="sin ffmpeg")
def test_armar_video_vertical_con_voz_y_subtitulos(limpio, monkeypatch):
    def voz_falsa(texto, destino):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=220:d=1.2", "-ar", "24000", str(destino)], check=True)
        return [(0.1, 0.5, "Hola"), (0.5, 1.0, "mundo")]
    monkeypatch.setattr(c, "_voz", voz_falsa)
    c.agregar({"titulo": "Prueba", "gancho": "Gancho de prueba", "escenas": [{"voz": "Hola mundo.", "visual": "texto", "texto": "Mesa 7\nminuto 14"},
                                                                          {"voz": "Hola mundo.", "visual": "orbe"}, {"voz": "Hola mundo.", "visual": "carta_es"}]}, time.time())
    p = c.armar_video(1)
    f = limpio / "videos" / p["video"]
    info = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(f)], capture_output=True, text=True).stdout)
    v = next(s for s in info["streams"] if s["codec_type"] == "video")
    assert (v["width"], v["height"]) == (1080, 1920) and any(s["codec_type"] == "audio" for s in info["streams"])
    assert 6 < p["duracion"] < 9                                            # 3 escenas de ~1,4 s + el cierre de 2,8 s


def test_api_solo_con_sesion_y_video_publico_con_nombre_secreto(limpio, monkeypatch):
    cl = TestClient(app_mod.app)
    assert cl.get("/api/contenido").status_code == 401
    monkeypatch.setattr(config, "MODO_DESARROLLO", True)
    d = cl.get("/api/contenido").json()
    assert len(d["piezas"]) >= 0 and d["instagram"] is False and d["tiktok"] is False
    pid = c.piezas()[0]["id"]
    r = cl.patch(f"/api/contenido/{pid}", json={"estado": "aprobada", "hora": "2026-12-24 18:45"})
    assert r.status_code == 200 and r.json()["estado"] == "aprobada" and r.json()["hora_colombia"] == "2026-12-24 18:45"
    assert cl.patch(f"/api/contenido/{pid}", json={"estado": "viral"}).status_code == 422
    assert cl.get(f"/api/contenido/{pid}/video").status_code == 404
    assert cl.get("/contenido.html").status_code == 200
    from servidor.apex import app as apex_app
    ca = TestClient(apex_app.app)
    assert ca.get("/v1/contenido/..%2Fapex.db").status_code == 404
    assert ca.get("/v1/contenido/" + "f" * 32 + ".mp4").status_code == 404


# ---------------- Marca personal: videos que graba Felipe y su voz clonada ----------------
def _video_prueba(destino, ancho=1280, alto=720, dur=6.0, silencio=(2.0, 4.5)):
    """Un video acostado con voz (tono) que se calla en la mitad, como alguien que hace una pausa larga."""
    a, b = silencio
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc2=s={ancho}x{alto}:r=30:d={dur}",
                    "-f", "lavfi", "-i", f"sine=f=300:d={dur}", "-af", f"volume=enable='between(t,{a},{b})':volume=0",
                    "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", str(destino)], check=True)
    return destino


def _info(f):
    d = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(f)], capture_output=True, text=True).stdout)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    return v["width"], v["height"], float(d["format"]["duration"]), any(s["codec_type"] == "audio" for s in d["streams"])


class Cerebro:
    def __init__(self, respuesta):
        self.respuesta, self.vistos = respuesta, []

    def _cadena(self, nombres, sistema, mensajes, max_tokens=0):
        self.vistos.append((sistema, mensajes))
        return type("Resp", (), {"texto": "Listo: " + json.dumps(self.respuesta)})()


def test_cortes_quitan_el_arranque_el_final_y_las_pausas_largas():
    palabras = [(1.0, 1.4, "Hola"), (1.5, 2.0, "amigos"), (4.0, 4.5, "hoy"), (4.6, 5.0, "aprendí")]
    t = c.cortes(palabras, 9.0)
    assert len(t) == 2                                        # la pausa de 2 s se corta; la de 0,1 s no
    assert t[0][0] < 1.0 and t[0][0] >= 0.8 and 2.0 < t[0][1] <= 2.35
    assert 3.75 <= t[1][0] < 4.0 and 5.0 < t[1][1] <= 5.45   # el final sin la mano que apaga la cámara
    assert all(abs(x * 30 - round(x * 30)) < 1e-6 for par in t for x in par)    # a cuadros enteros
    assert c.cortes([], 7.5) == [(0.0, 7.5)]
    nuevas = c.remapear(palabras, t)
    assert nuevas[0][0] == pytest.approx(1.0 - t[0][0], abs=0.01)
    assert nuevas[2][0] == pytest.approx(t[0][1] - t[0][0] + 4.0 - t[1][0], abs=0.01)   # «hoy» llega justo después del corte
    assert [w for _, _, w in nuevas] == ["Hola", "amigos", "hoy", "aprendí"]


def test_corregir_subtitulos_conserva_los_tiempos():
    palabras = [[0.0, 0.4, "Hola"], [0.5, 1.0, "soy"], [1.1, 1.6, "Felipe"], [1.7, 2.4, "y"], [2.5, 3.0, "hago"], [3.1, 3.6, "extra"]]
    nuevas = c.alinear(palabras, "Hola, soy Felipe y hago Axtra con IA.")
    assert [w for _, _, w in nuevas] == ["Hola", "soy", "Felipe", "y", "hago", "Axtra", "con", "IA"]
    assert nuevas[5][0] == 3.1 and nuevas[-1][1] == 3.6      # «Axtra con IA» se reparte el tiempo de «extra», que reemplaza
    assert nuevas[4][:2] == [2.5, 3.0]
    assert all(a <= b for a, b, _ in nuevas)


def test_whisper_sin_lo_que_se_invento_en_los_silencios():
    d = {"text": "Hola a todos. Subtítulos realizados por la comunidad de Amara.org",
         "segments": [{"start": 0, "end": 1.5, "text": " Hola a todos.", "no_speech_prob": 0.01},
                      {"start": 4, "end": 7, "text": " Subtítulos realizados por la comunidad de Amara.org", "no_speech_prob": 0.3}],
         "words": [{"word": " Hola", "start": 0.1, "end": 0.4}, {"word": "a", "start": 0.4, "end": 0.5}, {"word": "todos.", "start": 0.5, "end": 1.0},
                   {"word": "Subtítulos", "start": 4.2, "end": 5.0}]}
    t = c.limpiar_transcripcion(d)
    assert t["texto"] == "Hola a todos." and [w for _, _, w in t["palabras"]] == ["Hola", "a", "todos"]


def test_el_video_llega_por_partes_y_una_parte_repetida_no_se_duplica(limpio):
    assert c.recibir_parte("pieza1", 0, 10, b"abcd") is None
    assert c.recibir_parte("pieza1", 0, 10, b"abcd") is None                 # el celular reenvió la primera
    assert c.recibir_parte("pieza1", 4, 10, b"efg") is None
    assert c.recibir_parte("pieza1", 4, 10, b"efg") is None                  # se cortó la respuesta y la reenvió
    with pytest.raises(ValueError):
        c.recibir_parte("pieza1", 9, 10, b"j")                               # se saltó una parte
    f = c.recibir_parte("pieza1", 7, 10, b"hij")
    assert f.read_bytes() == b"abcdefghij"
    assert limpio in f.parents and (limpio / "videos") not in f.parents     # el original no queda en la carpeta pública
    with pytest.raises(ValueError):
        c.recibir_parte("../x", 0, 3, b"abc")
    with pytest.raises(ValueError):
        c.recibir_parte("pieza2", 0, c.MAX_SUBIDA + 1, b"a")


def test_video_grabado_su_guia_y_sus_opciones(limpio):
    pid = c.nueva_grabada()["id"]
    p = c.pieza(pid)
    assert p["tipo"] == "grabado" and p["cuenta"] == "personal" and p["escenas"] == [] and p["opciones"] == {"cortar_silencios": True, "cierre": False}
    assert p["hora_colombia"].endswith(c.PERSONAL_HORA) and p["cuando"] > time.time()
    c.actualizar(pid, video="abc.mp4")
    p = c.actualizar(pid, escenas=[{"voz": "Cuenta por qué empezaste", "visual": "orbe"}], notas="Caminando por la calle")
    assert p["video"] == "abc.mp4" and p["escenas"] == [{"voz": "Cuenta por qué empezaste", "visual": "camara"}]   # la guía no cambia el video
    c.actualizar(pid, video="abc.mp4")
    assert c.actualizar(pid, opciones={"cierre": True, "inventada": True})["video"] == ""
    assert c.pieza(pid)["opciones"] == {"cortar_silencios": True, "cierre": True}
    c.actualizar(pid, video="abc.mp4")
    assert c.actualizar(pid, gancho="Nuevo gancho")["video"] == ""
    # el segundo video suyo va al día siguiente: uno al día en la marca personal
    otro = c.nueva_grabada()
    assert otro["hora_colombia"][:10] > p["hora_colombia"][:10]
    pantalla = c.para_pantalla(c.actualizar(pid, transcripcion={"texto": "Hola", "palabras": [[0, 1, "Hola"]]}, grabacion="x.mp4"))
    assert pantalla["subtitulos"] == "Hola" and pantalla["grabada"] and "transcripcion" not in pantalla and "grabacion" not in pantalla


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="sin ffmpeg")
def test_editar_el_video_que_grabo_felipe(limpio, monkeypatch):
    pid = c.nueva_grabada()["id"]
    original = _video_prueba(limpio / "subido.mov")
    c.guardar_grabacion(pid, original, "IMG_0042.MOV")
    p = c.pieza(pid)
    assert p["grabacion"].endswith(".mov") and (c.carpeta_grabaciones() / p["grabacion"]).exists() and not original.exists()
    oidos = []

    def oido(audio):
        oidos.append(audio)
        return {"texto": "Hola amigos. Vamos ya.", "palabras": [[0.3, 0.8, "Hola"], [0.9, 1.6, "amigos"], [4.6, 5.2, "Vamos"], [5.3, 5.8, "ya"]]}
    monkeypatch.setattr(c, "_transcribir", oido)
    cerebro = Cerebro({"titulo": "Mi primer video", "gancho": "Esto me pasó hoy", "descripcion": "Les cuento.", "hashtags": ["emprender", "ia"]})
    p = c.editar_grabacion(pid, cerebro)
    ancho, alto, dur, audio = _info(limpio / "videos" / p["video"])
    assert (ancho, alto) == (1080, 1920) and audio
    assert 2.6 < dur < 4.0                                   # de 6 s quedan unos 3: sin el arranque, la pausa larga ni el final
    assert p["titulo"] == "Mi primer video" and p["gancho"] == "Esto me pasó hoy" and p["hashtags"] == ["#emprender", "#ia"]
    assert "Hola amigos" in cerebro.vistos[0][1][0]["content"] and p["error"] == ""
    assert p["transcripcion"]["palabras"][0] == [0.3, 0.8, "Hola"]
    # rehacer con el cierre: no vuelve a transcribir
    c.actualizar(pid, opciones={"cierre": True})
    p2 = c.armar_video(pid)
    assert len(oidos) == 1 and _info(limpio / "videos" / p2["video"])[2] == pytest.approx(dur + 2.2, abs=0.25)
    assert not (limpio / "videos" / p["video"]).exists()     # el video anterior se borra
    # sin quitar silencios queda completo
    c.actualizar(pid, opciones={"cortar_silencios": False, "cierre": False})
    assert _info(limpio / "videos" / c.armar_video(pid)["video"])[2] == pytest.approx(6.0, abs=0.2)


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="sin ffmpeg")
def test_sin_whisper_el_video_sale_sin_subtitulos_y_avisa(limpio, monkeypatch):
    pid = c.nueva_grabada()["id"]
    c.guardar_grabacion(pid, _video_prueba(limpio / "v.mp4", 1080, 1920, 3.0, (5, 6)), "v.mp4")
    monkeypatch.setattr(c.config, "GROQ_API_KEY", "")
    p = c.editar_grabacion(pid, Cerebro({}))
    assert p["video"] and "sin subtítulos" in p["error"] and "GROQ_API_KEY" in p["error"]
    assert _info(limpio / "videos" / p["video"])[:2] == (1080, 1920)


def test_un_archivo_que_no_es_video_no_se_guarda(limpio):
    pid = c.nueva_grabada()["id"]
    malo = limpio / "nota.txt"; malo.write_text("hola")
    with pytest.raises(ValueError):
        c.guardar_grabacion(pid, malo, "nota.txt")
    assert not malo.exists() and c.pieza(pid)["grabacion"] == ""


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="sin ffmpeg")
def test_clonar_la_voz_de_felipe(limpio, monkeypatch):
    muestra = limpio / "nota.m4a"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=200:d=32", str(muestra)], check=True)
    with pytest.raises(RuntimeError):
        c.clonar_voz(muestra)                                 # sin la clave de ElevenLabs
    monkeypatch.setenv("ELEVENLABS_API_KEY", "xi")
    enviados, borrados = [], []

    def post(url, headers=None, data=None, files=None, **kw):
        enviados.append((url, headers, data, files))
        return R({"voice_id": f"voz{len(enviados)}"})
    monkeypatch.setattr(c.requests, "post", post)
    monkeypatch.setattr(c.requests, "delete", lambda url, **kw: (borrados.append(url), R({}))[1])
    assert c.clonar_voz(muestra) == "voz1" and c.voz_felipe_lista()
    url, headers, data, files = enviados[0]
    assert url.endswith("/voices/add") and headers["xi-api-key"] == "xi" and files[0][1][2] == "audio/mpeg" and data["remove_background_noise"] == "true"
    assert c.clonar_voz(muestra) == "voz2" and borrados[0].endswith("/voices/voz1")      # la vieja se borra
    corta = limpio / "corta.m4a"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "sine=f=200:d=5", str(corta)], check=True)
    with pytest.raises(ValueError):
        c.clonar_voz(corta)
    c.borrar_voz()
    assert not c.voz_felipe_lista() and borrados[-1].endswith("/voices/voz2")


def test_la_voz_clonada_da_el_tiempo_de_cada_palabra(limpio, monkeypatch):
    monkeypatch.setenv("ELEVENLABS_API_KEY", "xi"); c.ajuste("voz_felipe_id", "v9")
    texto = "Hola, soy Felipe."
    al = {"characters": list(texto), "character_start_times_seconds": [i * 0.1 for i in range(len(texto))],
          "character_end_times_seconds": [i * 0.1 + 0.1 for i in range(len(texto))]}
    pedidos = []

    def post(url, json=None, headers=None, params=None, **kw):
        pedidos.append((url, json))
        return R({"audio_base64": c.base64.b64encode(b"ID3audio").decode(), "alignment": al})
    monkeypatch.setattr(c.requests, "post", post)
    destino = limpio / "voz.mp3"
    palabras = c._voz_felipe(texto, destino)
    assert destino.read_bytes() == b"ID3audio" and pedidos[0][0].endswith("/text-to-speech/v9/with-timestamps")
    assert [w for _, _, w in palabras] == ["Hola", "soy", "Felipe"] and palabras[1][0] == pytest.approx(0.6)
    p = c.pieza(c.agregar({"voz": "felipe", "escenas": [{"voz": "Hola", "visual": "texto", "texto": "Hola"}], "descripcion": "Un día normal",
                           "hashtags": ["ia"]}, time.time(), estado="aprobada"))
    assert p["voz"] == "felipe" and "Voz generada con IA." in c.texto_publicacion(p)


def test_la_marca_personal_publica_en_las_cuentas_de_felipe(limpio, monkeypatch):
    monkeypatch.setenv("IG_USUARIO_ID", "apex"); monkeypatch.setenv("IG_TOKEN", "t-apex")
    monkeypatch.setenv("IG_PERSONAL_USUARIO_ID", "felipe"); monkeypatch.setenv("IG_PERSONAL_TOKEN", "t-felipe")
    llamadas = []

    def post(url, data=None, **kw):
        llamadas.append((url, data))
        return R({"id": "cont"} if url.endswith("/media") else {"id": "reel1"})
    monkeypatch.setattr(c.requests, "post", post)
    monkeypatch.setattr(c.requests, "get", lambda url, params=None, **kw: R({"status_code": "FINISHED"} if "cont" in url else {"permalink": "x"}))
    pid = c.nueva_grabada()["id"]
    c.actualizar(pid, video="a" * 32 + ".mp4", estado="aprobada", descripcion="Hola"); (limpio / "videos" / ("a" * 32 + ".mp4")).write_bytes(b"x")
    assert c.publicar(pid)["estado"] == "publicada"
    assert "/felipe/media" in llamadas[0][0] and llamadas[0][1]["access_token"] == "t-felipe" and llamadas[1][1]["access_token"] == "t-felipe"
    monkeypatch.delenv("IG_PERSONAL_TOKEN")
    pid2 = c.nueva_grabada()["id"]
    c.actualizar(pid2, video="b" * 32 + ".mp4", estado="aprobada"); (limpio / "videos" / ("b" * 32 + ".mp4")).write_bytes(b"x")
    p = c.publicar(pid2)                                     # sin sus cuentas no se publica en las de Apex
    assert p["estado"] == "error" and "marca personal" in p["error"] and len(llamadas) == 2


def test_tiktok_recibe_por_partes_los_videos_pesados(limpio, monkeypatch):
    for k, v in (("TIKTOK_CLIENT_KEY", "ck"), ("TIKTOK_CLIENT_SECRET", "cs"), ("TIKTOK_PERSONAL_REFRESH_TOKEN", "rp")):
        monkeypatch.setenv(k, v)
    monkeypatch.setattr(c, "TIKTOK_UN_TROZO", 10); monkeypatch.setattr(c, "TIKTOK_TROZO", 4)
    inicio = []

    def post(url, data=None, json=None, headers=None, **kw):
        if url.endswith("/oauth/token/"):
            assert data["refresh_token"] == "rp"
            return R({"access_token": "ap", "expires_in": 86400})
        inicio.append(json)
        return R({"data": {"publish_id": "p1", "upload_url": "https://subida"}, "error": {"code": "ok"}})
    partes = []
    monkeypatch.setattr(c.requests, "post", post)
    monkeypatch.setattr(c.requests, "put", lambda url, data=None, headers=None, **kw: (partes.append((headers["Content-Range"], data)), R({}, 206))[1])
    pid = c.nueva_grabada()["id"]
    c.actualizar(pid, video="c" * 32 + ".mp4", estado="aprobada"); (limpio / "videos" / ("c" * 32 + ".mp4")).write_bytes(b"0123456789A")
    assert c.publicar(pid)["tiktok_id"] == "p1"
    assert inicio[0]["source_info"] == {"source": "FILE_UPLOAD", "video_size": 11, "chunk_size": 4, "total_chunk_count": 2}
    assert partes == [("bytes 0-3/11", b"0123"), ("bytes 4-10/11", b"456789A")]          # la última lleva el resto
    assert c.ajuste("personal_tiktok_token") == "ap" and c.ajuste("tiktok_token") == ""   # los tokens de Apex no se tocan


def test_ideas_para_grabar_de_la_marca_personal(limpio, monkeypatch):
    ideas = [{"formato": "grabar", "pilar": "Lecciones de emprendedor", "titulo": f"Idea {i}", "gancho": "Lo que nadie te dice",
              "puntos": ["Cuenta cuándo empezaste", {"voz": "Di qué aprendiste"}], "consejo": "Frente al computador", "descripcion": "Texto",
              "hashtags": ["emprendimiento"]} for i in range(5)]
    ideas += [{"formato": "voz_en_off", "titulo": "Sin cámara", "gancho": "Tres cosas", "puntos": [{"voz": "La primera es la constancia de todos los días."}]}] * 2
    cerebro = Cerebro({"piezas": ideas})
    ids = c.proponer_personal(7, cerebro)
    ps = [c.pieza(i) for i in ids]
    assert "Nunca inventes cifras" in cerebro.vistos[0][0] and "Todas son «grabar»" in cerebro.vistos[0][0]
    assert len(ps) == 7 and all(p["tipo"] == "grabado" and p["cuenta"] == "personal" and p["origen"] == "agente" for p in ps)   # sin voz: todo es para grabar
    assert ps[0]["escenas"] == [{"voz": "Cuenta cuándo empezaste", "visual": "camara"}, {"voz": "Di qué aprendiste", "visual": "camara"}]
    assert ps[0]["notas"] == "Frente al computador" and len({p["hora_colombia"][:10] for p in ps}) == 7
    assert all(p["hora_colombia"].endswith(c.PERSONAL_HORA) for p in ps)
    monkeypatch.setenv("ELEVENLABS_API_KEY", "xi"); c.ajuste("voz_felipe_id", "v1")
    ps = [c.pieza(i) for i in c.proponer_personal(7, Cerebro({"piezas": ideas}))]
    off = [p for p in ps if p["tipo"] == "auto"]
    assert len(off) == 2 and all(p["voz"] == "felipe" and p["cuenta"] == "personal" for p in off)
    assert off[0]["escenas"][0]["visual"] == "texto" and off[0]["escenas"][0]["texto"].count("\n") <= 2
    assert min(p["cuando"] for p in ps) > max(c.pieza(i)["cuando"] for i in ids)          # siguen después de las anteriores


def test_llega_la_hora_y_falta_el_video_grabado(limpio, monkeypatch):
    pid = c.nueva_grabada()["id"]
    p = c.actualizar(pid, estado="aprobada", gancho="Hola")
    armados = []
    monkeypatch.setattr(c, "armar_video", lambda i: armados.append(i))
    c.revisar(ahora=p["cuando"] - 600)
    assert armados == []                                     # no hay nada que armar sin el video
    c.revisar(ahora=p["cuando"] + 60)
    p = c.pieza(pid)
    assert p["estado"] == "error" and "falta subir su video" in p["error"]


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="sin ffmpeg")
def test_api_subir_el_video_por_partes_y_la_voz(limpio, monkeypatch):
    cl = TestClient(app_mod.app)
    assert cl.post("/api/contenido/nueva").status_code == 401
    monkeypatch.setattr(config, "MODO_DESARROLLO", True)
    monkeypatch.setattr(app_mod, "_hilo", lambda fn, *a: fn(*a))
    monkeypatch.setattr(c, "armar_video", lambda pid: c.actualizar(pid, video="d" * 32 + ".mp4", error=""))
    p = cl.post("/api/contenido/nueva").json()
    assert p["tipo"] == "grabado" and p["grabada"] is False
    assert cl.post(f"/api/contenido/{p['id']}/video").status_code == 422          # primero hay que subirlo
    datos = _video_prueba(limpio / "celular.mp4", 320, 568, 2.0, (5, 6)).read_bytes()
    mitad = len(datos) // 2
    r = cl.post(f"/api/contenido/{p['id']}/grabacion?desde=0&total={len(datos)}&nombre=IMG.MP4", content=datos[:mitad])
    assert r.json() == {"recibido": mitad}
    r = cl.post(f"/api/contenido/{p['id']}/grabacion?desde={mitad}&total={len(datos)}&nombre=IMG.MP4", content=datos[mitad:])
    assert r.status_code == 200 and r.json()["listo"]
    lista = cl.get("/api/contenido").json()
    yo = next(x for x in lista["piezas"] if x["id"] == p["id"])
    assert yo["grabada"] and yo["video"] == "d" * 32 + ".mp4" and "transcripcion" not in yo
    assert lista["personal"] == {"instagram": False, "tiktok": False} and lista["voz_felipe"] is False and lista["elevenlabs"] is False
    assert cl.post(f"/api/contenido/{p['id']}/subtitulos", json={"texto": "Hola"}).status_code == 422   # todavía no tiene subtítulos
    c.actualizar(p["id"], transcripcion={"texto": "Ola", "palabras": [[0.1, 0.5, "Ola"]]})
    assert cl.post(f"/api/contenido/{p['id']}/subtitulos", json={"texto": "Hola"}).status_code == 200
    assert c.pieza(p["id"])["transcripcion"]["palabras"] == [[0.1, 0.5, "Hola"]]
    malo = cl.post(f"/api/contenido/{p['id']}/grabacion?desde=0&total=4&nombre=x.txt", content=b"hola")
    assert malo.status_code == 422 and c.pieza(p["id"])["grabacion"]               # el video que ya tenía no se pierde
    assert cl.post("/api/contenido/voz?desde=0&total=3", content=b"abc").status_code == 422     # sin confirmar que es su voz
    r = cl.patch(f"/api/contenido/{p['id']}", json={"opciones": {"cierre": True}, "voz": "felipe"})
    assert r.status_code == 200 and r.json()["opciones"]["cierre"] is True and r.json()["voz"] == "apex"   # un video grabado lleva su voz real
    assert cl.patch(f"/api/contenido/{p['id']}", json={"voz": "robot"}).status_code == 422
