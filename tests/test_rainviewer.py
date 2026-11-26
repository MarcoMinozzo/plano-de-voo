import pytest
import requests

from servidor import rainviewer


PNG = b"\x89PNG\r\n\x1a\n tile"


class Resposta:
    def __init__(self, status_code=200, conteudo=PNG, dados=None, headers=None):
        self.status_code = status_code
        self.content = conteudo
        self.headers = headers or {"Content-Type": "image/png"}
        self._dados = dados or {}

    def json(self):
        return self._dados


def _manifesto(**alteracoes):
    dados = {
        "host": "https://tilecache.rainviewer.com",
        "generated": 300,
        "radar": {
            "past": [
                {"time": 100, "path": "/v2/radar/old-frame"},
                {"time": 200, "path": "/v2/radar/current-frame"},
            ]
        },
    }
    dados.update(alteracoes)
    return dados


def test_buscar_frame_seleciona_frame_mais_recente_sem_usar_geracao_do_manifesto():
    chamadas = []

    def get(url, timeout, allow_redirects):
        chamadas.append((url, timeout, allow_redirects))
        return Resposta(dados=_manifesto())

    resultado = rainviewer.buscar_frame(getter=get)

    assert resultado == {"frame": "current-frame", "hora": 200, "max_zoom": 7}
    assert chamadas == [
        (rainviewer.MANIFEST_URL, rainviewer.TIMEOUT, False)
    ]


@pytest.mark.parametrize(
    "dados",
    [
        _manifesto(radar={"past": []}),
        _manifesto(radar={"past": [{"time": 200, "path": "/v2/radar/../escape"}]}),
        _manifesto(host="https://attacker.example"),
    ],
)
def test_buscar_frame_recusa_manifesto_sem_frame_ou_nao_confiavel(dados):
    with pytest.raises(rainviewer.RainViewerIndisponivel):
        rainviewer.buscar_frame(getter=lambda *args, **kwargs: Resposta(dados=dados))


def test_buscar_tile_usa_host_fixo_e_valida_imagem():
    chamadas = []

    def get(url, timeout, allow_redirects):
        chamadas.append((url, timeout, allow_redirects))
        return Resposta(
            headers={
                "Content-Type": "image/png",
                "Cache-Control": "public, max-age=60",
            }
        )

    conteudo, cache = rainviewer.buscar_tile(
        "current-frame",
        7,
        127,
        127,
        getter=get,
    )

    assert conteudo == PNG
    assert cache == "public, max-age=60"
    assert chamadas == [
        (
            "https://tilecache.rainviewer.com/v2/radar/current-frame/256/7/127/127/2/1_1.png",
            rainviewer.TIMEOUT,
            False,
        )
    ]


def test_buscar_mascara_usa_endpoint_de_cobertura_fixo():
    chamadas = []

    def get(url, timeout, allow_redirects):
        chamadas.append(url)
        return Resposta()

    assert rainviewer.buscar_mascara(3, 2, 5, getter=get) == (PNG, None)
    assert chamadas == [
        "https://tilecache.rainviewer.com/v2/coverage/0/256/3/2/5/0/0_0.png"
    ]


@pytest.mark.parametrize(
    ("frame", "z", "x", "y"),
    [
        ("../escape", 3, 2, 5),
        ("frame", 8, 2, 5),
        ("frame", 3, 8, 5),
        ("frame", 3, 2, 8),
        ("frame", -1, 0, 0),
    ],
)
def test_buscar_tile_recusa_frame_ou_coordenadas_invalidas(frame, z, x, y):
    chamadas = []

    with pytest.raises((ValueError, rainviewer.RainViewerIndisponivel)):
        rainviewer.buscar_tile(
            frame,
            z,
            x,
            y,
            getter=lambda *args, **kwargs: chamadas.append(args),
        )

    assert chamadas == []


@pytest.mark.parametrize(
    "resposta",
    [
        Resposta(status_code=503),
        Resposta(headers={"Content-Type": "application/json"}),
        Resposta(conteudo=b"not an image"),
    ],
)
def test_buscar_tile_recusa_resposta_remota_invalida(resposta):
    with pytest.raises(rainviewer.RainViewerIndisponivel):
        rainviewer.buscar_tile(
            "current-frame",
            3,
            2,
            5,
            getter=lambda *args, **kwargs: resposta,
        )


def test_timeout_do_provedor_fica_indisponivel():
    def timeout(*args, **kwargs):
        raise requests.Timeout("timeout")

    with pytest.raises(rainviewer.RainViewerIndisponivel):
        rainviewer.buscar_frame(getter=timeout)
