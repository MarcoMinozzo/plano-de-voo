import pytest
import requests

from servidor import openaip


PNG = b"\x89PNG\r\n\x1a\n tile"


class Resposta:
    def __init__(self, status_code=200, content=PNG, headers=None):
        self.status_code = status_code
        self.content = content
        self.headers = headers or {"Content-Type": "image/png"}


def test_buscar_tile_usa_host_fixo_header_secreto_e_cache_do_provedor(monkeypatch):
    monkeypatch.setenv("OPENAIP_API_KEY", "fake-private-key")
    chamadas = []

    def get(url, headers, timeout, allow_redirects):
        chamadas.append((url, headers, timeout, allow_redirects))
        return Resposta(headers={
            "Content-Type": "image/png",
            "Cache-Control": "public, max-age=60",
        })

    conteudo, cache_control = openaip.buscar_tile(3, 2, 5, getter=get)

    assert conteudo == PNG
    assert cache_control == "public, max-age=60"
    assert chamadas == [
        (
            "https://api.tiles.openaip.net/api/data/openaip/3/2/5.png",
            {"x-openaip-api-key": "fake-private-key"},
            openaip.TIMEOUT,
            False,
        )
    ]


def test_buscar_tile_falha_sem_chave_sem_chamar_provedor(monkeypatch):
    monkeypatch.delenv("OPENAIP_API_KEY", raising=False)
    chamadas = []

    with pytest.raises(openaip.TileIndisponivel):
        openaip.buscar_tile(3, 2, 5, getter=lambda *args, **kwargs: chamadas.append(args))

    assert chamadas == []


@pytest.mark.parametrize(
    ("z", "x", "y"),
    [(1, 0, 0), (3, 8, 0), (3, 0, 8), (19, 0, 0), (-1, 0, 0)],
)
def test_buscar_tile_recusa_coordenadas_invalidas(monkeypatch, z, x, y):
    monkeypatch.setenv("OPENAIP_API_KEY", "fake-private-key")
    chamadas = []

    with pytest.raises(ValueError):
        openaip.buscar_tile(
            z,
            x,
            y,
            getter=lambda *args, **kwargs: chamadas.append(args),
        )

    assert chamadas == []


@pytest.mark.parametrize(
    "resposta",
    [
        Resposta(status_code=401, content=b"unauthorized"),
        Resposta(status_code=429, content=b"rate limit"),
        Resposta(headers={"Content-Type": "application/json"}),
        Resposta(content=b"not a PNG"),
    ],
)
def test_buscar_tile_rejeita_resposta_remota_invalida(monkeypatch, resposta):
    monkeypatch.setenv("OPENAIP_API_KEY", "fake-private-key")

    with pytest.raises(openaip.TileIndisponivel):
        openaip.buscar_tile(
            3,
            2,
            5,
            getter=lambda *args, **kwargs: resposta,
        )


def test_buscar_tile_converte_timeout_em_indisponibilidade(monkeypatch):
    monkeypatch.setenv("OPENAIP_API_KEY", "fake-private-key")

    def timeout(*args, **kwargs):
        raise requests.Timeout("timeout")

    with pytest.raises(openaip.TileIndisponivel):
        openaip.buscar_tile(3, 2, 5, getter=timeout)
