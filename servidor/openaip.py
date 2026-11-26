import os

import requests

URL_TILE = "https://api.tiles.openaip.net/api/data/openaip/{z}/{x}/{y}.png"
TIMEOUT = 8
ZOOM_MIN = 2
ZOOM_MAX = 18
ASSINATURA_PNG = b"\x89PNG\r\n\x1a\n"


class TileIndisponivel(Exception):
    pass


def validar_coordenadas(z, x, y):
    if not ZOOM_MIN <= z <= ZOOM_MAX:
        raise ValueError("Zoom de tile fora do intervalo permitido.")
    limite = 1 << z
    if not 0 <= x < limite or not 0 <= y < limite:
        raise ValueError("Coordenadas de tile fora do intervalo permitido.")


def buscar_tile(z, x, y, getter=None):
    validar_coordenadas(z, x, y)
    chave = os.environ.get("OPENAIP_API_KEY", "").strip()
    if not chave:
        raise TileIndisponivel("A chave OpenAIP não está configurada.")

    obter = getter or requests.get
    try:
        resposta = obter(
            URL_TILE.format(z=z, x=x, y=y),
            headers={"x-openaip-api-key": chave},
            timeout=TIMEOUT,
            allow_redirects=False,
        )
    except requests.RequestException as exc:
        raise TileIndisponivel("O serviço OpenAIP está indisponível.") from exc

    tipo = resposta.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
    conteudo = resposta.content
    if (
        resposta.status_code != 200
        or tipo != "image/png"
        or not conteudo.startswith(ASSINATURA_PNG)
    ):
        raise TileIndisponivel("O serviço OpenAIP não retornou um tile válido.")

    return conteudo, resposta.headers.get("Cache-Control")
