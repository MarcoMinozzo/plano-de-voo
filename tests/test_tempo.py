from types import SimpleNamespace

import requests

from servidor import tempo as tempo_mod
from servidor.modelos import PlanoDeVoo, Sessao
from servidor.tempo import campos_metar, carta, linhas_boletim, meteorologia, radar, vento_area
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


def test_metar_preserva_campos_estruturados_opcionais_sem_alterar_o_original():
    observacao = {
        "rawOb": "METAR SBJD 121200Z VRB12G20KT 6SM -RA BKN020",
        "reportTime": "2026-12-01T12:00:00Z",
        "temp": 18,
        "dewp": 12,
        "wdir": "VRB",
        "wspd": 12,
        "wgst": 20,
        "visib": 6,
        "altim": 1013.2,
        "wxString": "-RA",
        "vertVis": 2500,
        "clouds": [{"cover": "BKN", "base": 2000, "type": "CB"}],
    }

    def getter(url, params=None, timeout=None):
        if url.endswith("/metar"):
            return Resposta(200, b"[{}]", [observacao])
        return Resposta(200, b"[]", [])

    resultado = meteorologia("SBJD", getter)
    metar = resultado["metar"]
    assert metar["icao"] == "SBJD"
    assert metar["raw"] == observacao["rawOb"]
    assert metar["hora"] == observacao["reportTime"]
    assert metar["temp_c"] == 18
    assert metar["vento_kt"] == 12
    assert metar["unidade_vento"] == "kt"
    assert metar["ponto_orvalho_c"] == 12
    assert metar["direcao_vento"] == "VRB"
    assert metar["rajada_kt"] == 20
    assert metar["visibilidade_sm"] == 6
    assert metar["altimetro_hpa"] == 1013.2
    assert metar["fenomenos"] == "-RA"
    assert metar["visibilidade_vertical_ft"] == 2500
    assert metar["nuvens"] == observacao["clouds"]
    assert metar["fonte"] == "Aviation Weather Center"


def test_metar_nao_cria_campos_estruturados_ausentes_ou_nulos():
    observacao = {"rawOb": "METAR SBJD 121200Z VRB12KT", "wdir": None, "clouds": []}

    def getter(url, params=None, timeout=None):
        if url.endswith("/metar"):
            return Resposta(200, b"[{}]", [observacao])
        return Resposta(200, b"[]", [])

    metar = meteorologia("SBJD", getter)["metar"]
    assert metar["raw"] == observacao["rawOb"]
    assert "direcao_vento" not in metar
    assert "ponto_orvalho_c" not in metar
    assert metar["nuvens"] == []


def test_buscar_consulta_uma_vez_por_aerodromo_distinto(monkeypatch):
    origem = _lugar(-23.2, -46.9, "SBJD")
    destino = _lugar(-21.1, -50.4, "SBJD")
    escala = _lugar(-22.0, -47.0, "SBAU")
    chamadas = []

    def meteorologia_falsa(icao, getter=None):
        chamadas.append(icao)
        return {"estado": "indisponivel", "fonte": "Aviation Weather Center"}

    monkeypatch.setattr(tempo_mod, "meteorologia", meteorologia_falsa)
    monkeypatch.setattr(tempo_mod, "vento_area", lambda *args: {"estado": "indisponivel"})
    monkeypatch.setattr(tempo_mod, "carta", lambda *args: {"estado": "indisponivel"})
    monkeypatch.setattr(tempo_mod, "radar", lambda *args: {"estado": "indisponivel"})

    resultado = tempo_mod.buscar(origem, destino, aerodromos=[origem, escala, destino, escala])

    assert chamadas == ["SBJD", "SBAU"]
    assert set(resultado["meteorologia"]["aerodromos"]) == {"SBJD", "SBAU"}
    assert resultado["meteorologia"]["origem"] == resultado["meteorologia"]["aerodromos"]["SBJD"]
    assert resultado["meteorologia"]["destino"] == resultado["meteorologia"]["aerodromos"]["SBJD"]


def test_campos_metar_em_portugues_mantem_unidades_e_codigos_da_fonte():
    campos = campos_metar(
        {
            "temp_c": 18,
            "ponto_orvalho_c": 12,
            "direcao_vento": "VRB",
            "vento_kt": 10,
            "rajada_kt": 20,
            "visibilidade_sm": 6,
            "altimetro_hpa": 1013.2,
            "fenomenos": "-RA",
            "visibilidade_vertical_ft": 2500,
            "nuvens": [{"cover": "BKN", "base": 2000, "type": "CB"}],
        }
    )
    por_nome = {campo["nome"]: campo for campo in campos}

    assert por_nome["Temperatura"] == {"nome": "Temperatura", "valor": 18, "unidade": "°C"}
    assert por_nome["Ponto de orvalho"]["unidade"] == "°C"
    assert por_nome["Direção do vento"]["valor"] == "VRB"
    assert por_nome["Direção do vento"]["unidade"] == "código AWC"
    assert por_nome["Velocidade do vento"]["unidade"] == "kt"
    assert por_nome["Rajada"]["unidade"] == "kt"
    assert por_nome["Visibilidade"]["unidade"] == "SM"
    assert por_nome["Altímetro"]["unidade"] == "hPa"
    assert por_nome["Fenômenos meteorológicos (código AWC)"]["valor"] == "-RA"
    assert "Chuva" not in por_nome["Fenômenos meteorológicos (código AWC)"]["valor"]
    assert por_nome["Visibilidade vertical"]["unidade"] == "ft"
    assert '"cover": "BKN"' in por_nome["Camadas de nuvens (dados AWC)"]["valor"]


def test_campos_metar_ausentes_sao_marcados_sem_inferencia():
    campos = campos_metar({"temp_c": None, "direcao_vento": None})

    assert all(campo["valor"] == "Indisponível" for campo in campos)


def _lugar(lat, lon, icao="SBJD"):
    return SimpleNamespace(icao=icao, lat=lat, lon=lon, fonte="teste")


def test_radar_sem_chave_informa_motivo(monkeypatch):
    monkeypatch.delenv("REDEMET_API_KEY", raising=False)

    resultado = radar(_lugar(-23.2, -46.9), _lugar(-21.1, -50.4, "SBAU"))

    assert resultado == {
        "estado": "indisponivel",
        "motivo": "Chave REDEMET não configurada.",
    }


def test_radar_sem_cobertura_geografica_informa_motivo(monkeypatch):
    monkeypatch.setenv("REDEMET_API_KEY", "teste")

    def sem_dados(url, params=None, timeout=None):
        return Resposta(200, b"{}", {"data": {"radar": []}})

    resultado = radar(_lugar(-23.2, -46.9), _lugar(-21.1, -50.4, "SBAU"), sem_dados)

    assert resultado == {
        "estado": "indisponivel",
        "motivo": "Radar sem dados geográficos válidos para o trecho.",
    }


def test_radar_com_falha_da_fonte_informa_motivo(monkeypatch):
    monkeypatch.setenv("REDEMET_API_KEY", "teste")

    def indisponivel(url, params=None, timeout=None):
        raise requests.Timeout()

    resultado = radar(_lugar(-23.2, -46.9), _lugar(-21.1, -50.4, "SBAU"), indisponivel)

    assert resultado == {
        "estado": "indisponivel",
        "motivo": "Fonte REDEMET indisponível.",
    }


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
        assert url == "https://api.decea.mil.br/aisweb/"
        assert params["area"] == "cartas"
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
    assert "TAF da chegada indisponível" in html
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
    assert "METAR da saída indisponível." in sem_boletim
    assert "METAR SBJD" not in sem_boletim
    assert linhas_boletim({"estado": "indisponivel"}) == []
