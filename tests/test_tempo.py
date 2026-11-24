from types import SimpleNamespace

import requests

from servidor.modelos import PlanoDeVoo, Sessao
from servidor.tempo import carta, linhas_boletim, meteorologia, vento_area
from tests.conftest import JSON, cadastrar, plano_valido


class Resposta:
    def __init__(self, status=200, conteudo=b"[]", json_dados=None):
        self.status_code = status
        self.content = conteudo
        self._json = json_dados if json_dados is not None else []
        self.text = conteudo.decode() if isinstance(conteudo, bytes) else conteudo

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(self.status_code)

    def json(self):
        return self._json


def test_corpo_vazio_fica_indisponivel():
    def getter(url, params=None, timeout=None):
        assert timeout == 8
        return Resposta(204, b"")

    assert meteorologia("SBJD", getter).get("estado") == "indisponivel"


def test_falha_de_rede_fica_indisponivel():
    def getter(url, params=None, timeout=None):
        assert timeout == 8
        raise requests.Timeout()

    assert meteorologia("SBJD", getter).get("estado") == "indisponivel"


def test_sem_dado_nao_inventa_valor():
    def getter(url, params=None, timeout=None):
        return Resposta(200, b"[]", [])

    resultado = meteorologia("SBJD", getter)
    assert resultado.get("estado") == "indisponivel"
    assert "raw" not in resultado


def _lugar(lat, lon, icao="SBJD"):
    return SimpleNamespace(icao=icao, lat=lat, lon=lon, fonte="teste")


def test_vento_so_quando_a_mensagem_cobre_a_rota(monkeypatch):
    monkeypatch.setenv("REDEMET_API_KEY", "teste")
    origem = _lugar(-23.2, -46.9)
    destino = _lugar(-21.1, -50.4, "SBAU")
    mensagem = {
        "id_localidade": "SBCW",
        "mens": "SBCW GAMET WND 270/20KT",
        "lat_min": -34,
        "lat_max": -20,
        "lon_min": -55,
        "lon_max": -40,
    }

    def cobre(url, params=None, timeout=None):
        assert timeout == 8
        return Resposta(200, b"{}", {"data": [mensagem]})

    vento = vento_area(origem, destino, cobre)
    assert vento["estado"] == "disponivel"
    assert vento["direcao_de_graus"] == 270
    assert vento["velocidade_kt"] == 20
    assert vento["unidade"] == "kt"
    assert vento["fonte"] == "REDEMET área SBCW"

    def fora(url, params=None, timeout=None):
        return Resposta(200, b"{}", {"data": [dict(mensagem, lat_min=10, lat_max=20, lon_min=10, lon_max=20)]})

    sem_cobertura = vento_area(origem, destino, fora)
    assert sem_cobertura == {"estado": "indisponivel"}


def test_carta_wac_da_area_da_rota(monkeypatch):
    monkeypatch.setenv("AISWEB_API_KEY", "teste")
    monkeypatch.setenv("AISWEB_API_PASS", "teste")
    origem = _lugar(-23.2, -46.9)
    destino = _lugar(-21.1, -50.4, "SBAU")
    xml = """<aisweb>
      <item>
        <nome>WAC 3182</nome>
        <link>https://exemplo.invalid/wac3182</link>
        <lat_min>-34</lat_min><lat_max>-20</lat_max>
        <lon_min>-55</lon_min><lon_max>-40</lon_max>
      </item>
      <item>
        <nome>WAC longe</nome>
        <link>https://exemplo.invalid/longe</link>
        <lat_min>10</lat_min><lat_max>20</lat_max>
        <lon_min>10</lon_min><lon_max>20</lon_max>
      </item>
    </aisweb>"""

    def cobre(url, params=None, timeout=None):
        assert timeout == 8
        return Resposta(200, xml.encode())

    carta_rota = carta(origem, destino, cobre)
    assert carta_rota["estado"] == "disponivel"
    assert carta_rota["url"] == "https://exemplo.invalid/wac3182"
    assert carta_rota["fonte"] == "AISWEB WAC 3182"

    def longe(url, params=None, timeout=None):
        return Resposta(200, b"<aisweb><item><nome>WAC longe</nome><link>https://exemplo.invalid/longe</link><lat_min>10</lat_min><lat_max>20</lat_max><lon_min>10</lon_min><lon_max>20</lon_max></item></aisweb>")

    assert carta(origem, destino, longe) == {"estado": "indisponivel"}


def test_tela_e_pdf_mostram_o_texto_do_boletim(cliente):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]
    db = Sessao()
    try:
        plano = db.get(PlanoDeVoo, plano_id)
        plano.meteorologia = {
            "estado": "disponivel",
            "origem": {
                "estado": "disponivel",
                "metar": {"raw": "METAR SBJD 121200Z 18010KT"},
                "taf": {"raw": "TAF SBJD 121100Z 18008KT"},
            },
            "destino": {
                "estado": "disponivel",
                "metar": {"raw": "METAR SBAU 121200Z 09005KT"},
                "taf": {"estado": "indisponivel"},
            },
        }
        db.commit()
    finally:
        Sessao.remove()
    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)
    assert "METAR SBJD 121200Z 18010KT" in html
    assert "TAF SBJD 121100Z 18008KT" in html
    assert "METAR SBAU 121200Z 09005KT" in html
    assert "TAF destino: indisponível" in html
    pdf = cliente.get(f"/planos/{plano_id}/pdf").data
    assert b"METAR SBJD 121200Z 18010KT" in pdf
    assert b"TAF SBJD 121100Z 18008KT" in pdf
    assert b"TAF destino: indispon\\355vel" in pdf
    db = Sessao()
    try:
        plano = db.get(PlanoDeVoo, plano_id)
        plano.meteorologia = {"estado": "indisponivel"}
        db.commit()
    finally:
        Sessao.remove()
    sem_boletim = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)
    assert (
        "Meteorologia: indisponível." in sem_boletim
        or "Tempo, vento, carta de voo visual e radar: indisponível." in sem_boletim
        or "Indisponível:" in sem_boletim
    )
    assert "METAR SBJD" not in sem_boletim
    assert linhas_boletim({"estado": "indisponivel"}) == []
