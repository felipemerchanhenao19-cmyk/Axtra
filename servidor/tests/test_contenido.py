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
    for k in ("IG_USUARIO_ID", "IG_TOKEN", "TIKTOK_CLIENT_KEY", "TIKTOK_CLIENT_SECRET", "TIKTOK_REFRESH_TOKEN"):
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
