import re

import requests


MANIFEST_URL = "https://api.rainviewer.com/public/weather-maps.json"
TILE_HOST = "https://tilecache.rainviewer.com"
TIMEOUT = 8
ZOOM_MAX = 7
TILE_SIZE = 256
ASSINATURA_PNG = b"\x89PNG\r\n\x1a\n"
_FRAME_PATH = re.compile(r"/v2/radar/([A-Za-z0-9_-]+)")
_FRAME_ID = re.compile(r"[A-Za-z0-9_-]+")


class RainViewerIndisponivel(Exception):
    pass


def _validar_coordenadas(z, x, y):
    if any(not isinstance(valor, int) or isinstance(valor, bool) for valor in (z, x, y)):
        raise ValueError("Coordenadas de tile inválidas.")
    if not 0 <= z <= ZOOM_MAX:
        raise ValueError("Zoom de tile fora do intervalo permitido.")
    limite = 1 << z
    if not 0 <= x < limite or not 0 <= y < limite:
        raise ValueError("Coordenadas de tile fora do intervalo permitido.")


def _png_valido(resposta):
    tipo = resposta.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
    conteudo = resposta.content
    if (
        resposta.status_code != 200
        or tipo != "image/png"
        or not conteudo.startswith(ASSINATURA_PNG)
    ):
        raise RainViewerIndisponivel("RainViewer não retornou um tile PNG válido.")
    return conteudo, resposta.headers.get("Cache-Control")


def buscar_frame(getter=None):
    obter = getter or requests.get
    try:
        resposta = obter(
            MANIFEST_URL,
            timeout=TIMEOUT,
            allow_redirects=False,
        )
    except requests.RequestException as exc:
        raise RainViewerIndisponivel("Serviço RainViewer indisponível.") from exc

    if resposta.status_code != 200:
        raise RainViewerIndisponivel("Serviço RainViewer indisponível.")
    try:
        manifesto = resposta.json()
    except (TypeError, ValueError) as exc:
        raise RainViewerIndisponivel("Manifesto RainViewer inválido.") from exc

    if not isinstance(manifesto, dict) or manifesto.get("host") != TILE_HOST:
        raise RainViewerIndisponivel("Manifesto RainViewer inválido.")

    radar = manifesto.get("radar")
    frames = radar.get("past") if isinstance(radar, dict) else None
    candidatos = []
    for frame in frames if isinstance(frames, list) else ():
        if not isinstance(frame, dict):
            continue
        caminho = frame.get("path")
        correspondencia = _FRAME_PATH.fullmatch(caminho) if isinstance(caminho, str) else None
        hora = frame.get("time")
        if (
            correspondencia
            and isinstance(hora, int)
            and not isinstance(hora, bool)
            and hora > 0
        ):
            candidatos.append({"frame": correspondencia.group(1), "hora": hora})

    if not candidatos:
        raise RainViewerIndisponivel("RainViewer não forneceu frames de radar válidos.")
    return {**max(candidatos, key=lambda item: item["hora"]), "max_zoom": ZOOM_MAX}


def buscar_tile(frame, z, x, y, getter=None):
    _validar_coordenadas(z, x, y)
    if not isinstance(frame, str) or not _FRAME_ID.fullmatch(frame):
        raise ValueError("Identificador de frame RainViewer inválido.")

    obter = getter or requests.get
    url = f"{TILE_HOST}/v2/radar/{frame}/{TILE_SIZE}/{z}/{x}/{y}/2/1_1.png"
    try:
        resposta = obter(
            url,
            timeout=TIMEOUT,
            allow_redirects=False,
        )
    except requests.RequestException as exc:
        raise RainViewerIndisponivel("Tile RainViewer indisponível.") from exc
    return _png_valido(resposta)


def buscar_mascara(z, x, y, getter=None):
    _validar_coordenadas(z, x, y)
    obter = getter or requests.get
    url = f"{TILE_HOST}/v2/coverage/0/{TILE_SIZE}/{z}/{x}/{y}/0/0_0.png"
    try:
        resposta = obter(
            url,
            timeout=TIMEOUT,
            allow_redirects=False,
        )
    except requests.RequestException as exc:
        raise RainViewerIndisponivel("Máscara de cobertura RainViewer indisponível.") from exc
    return _png_valido(resposta)
