import math
from types import SimpleNamespace

import requests

from servidor import tempo as tempo_mod
from servidor.modelos import PlanoDeVoo, Sessao
from servidor.tempo import campos_metar, campos_taf, carta, linhas_boletim, meteorologia, radar, vento_area
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


def test_taf_e_consultado_quando_metar_nao_tem_publicacao():
    chamadas = []

    def getter(url, params=None, timeout=None):
        chamadas.append(url.rsplit("/", 1)[-1])
        if url.endswith("/metar"):
            return Resposta(204, b"")
        return Resposta(
            200,
            b"[{}]",
            [{"rawTAF": "TAF SBJD 011100Z 18008KT", "issueTime": "2026-12-01T11:00:00Z"}],
        )

    resultado = meteorologia("SBJD", getter)

    assert chamadas == ["metar", "taf"]
    assert resultado["estado"] == "disponivel"
    assert resultado["metar"] is None
    assert resultado["taf"]["raw"] == "TAF SBJD 011100Z 18008KT"


def test_taf_permanece_disponivel_quando_consulta_metar_falha(caplog):
    def getter(url, params=None, timeout=None):
        if url.endswith("/metar"):
            raise requests.Timeout()
        return Resposta(200, b"[{}]", [{"rawTAF": "TAF SBJD 011100Z"}])

    resultado = meteorologia("SBJD", getter)

    assert resultado["estado"] == "disponivel"
    assert resultado["metar"] is None
    assert resultado["taf"]["raw"] == "TAF SBJD 011100Z"
    assert "Falha ao consultar METAR AWC para SBJD" in caplog.text


def test_falha_no_taf_nao_remove_metar_valido(caplog):
    def getter(url, params=None, timeout=None):
        if url.endswith("/metar"):
            return Resposta(
                200,
                b"[{}]",
                [{"icaoId": "SBJD", "rawOb": "METAR SBJD 011200Z"}],
            )
        raise requests.Timeout()

    resultado = meteorologia("SBJD", getter)

    assert resultado["estado"] == "disponivel"
    assert resultado["metar"]["raw"] == "METAR SBJD 011200Z"
    assert resultado["taf"]["estado"] == "indisponivel"
    assert "Falha ao consultar TAF AWC para SBJD" in caplog.text


def test_taf_redemet_prioriza_mensagem_valida_mais_recente(monkeypatch):
    monkeypatch.setenv("REDEMET_API_KEY", "chave-de-teste")
    monkeypatch.setattr(
        tempo_mod,
        "_agora_utc",
        lambda: tempo_mod._instante_redemet("2026-11-27 05:00:00"),
    )
    chamadas = []
    mensagens = [
        {
            "id_localidade": "SBMT",
            "mens": "TAF SBMT 270300Z 2706/2718 18008KT",
            "recebimento": "2026-11-27 03:10:00",
            "validade_inicial": "2026-11-27 06:00:00",
            "validade_final": "2026-11-27 18:00:00",
        },
        {
            "id_localidade": "SBMT",
            "mens": "TAF SBMT 270400Z 2706/2718 19010KT",
            "recebimento": "2026-11-27 04:20:00",
            "validade_inicial": "2026-11-27 06:00:00",
            "validade_final": "2026-11-27 18:00:00",
        },
        {
            "id_localidade": "SBSP",
            "mens": "TAF SBSP 270500Z 2706/2718 20012KT",
            "recebimento": "2026-11-27 05:20:00",
            "validade_inicial": "2026-11-27 06:00:00",
            "validade_final": "2026-11-27 18:00:00",
        },
        {
            "id_localidade": "SBMT",
            "mens": "TAF SBMT 270500Z 2706/2718 20012KT",
            "recebimento": "não informado",
            "validade_inicial": "2026-11-27 06:00:00",
            "validade_final": "2026-11-27 18:00:00",
        },
    ]

    def getter(url, params=None, timeout=None):
        chamadas.append(url)
        if url.endswith("/metar"):
            return Resposta(204, b"")
        if url.endswith("/mensagens/taf/SBMT"):
            assert params["api_key"] == "chave-de-teste"
            return Resposta(200, b"{}", {"status": True, "data": {"taf": mensagens}})
        raise AssertionError(f"TAF AWC não deve ser consultado: {url}")

    resultado = meteorologia("SBMT", getter)

    assert resultado["taf"] == {
        "raw": "TAF SBMT 270400Z 2706/2718 19010KT",
        "hora": "2026-11-27 04:20:00",
        "fonte": "REDEMET",
        "icao": "SBMT",
        "validade_inicial": "2026-11-27 06:00:00",
        "validade_final": "2026-11-27 18:00:00",
    }
    assert resultado["estado"] == "disponivel"
    assert len(chamadas) == 2


def test_taf_redemet_rejeita_icao_divergente_e_faz_fallback_awc(monkeypatch):
    monkeypatch.setenv("REDEMET_API_KEY", "chave-de-teste")
    monkeypatch.setattr(
        tempo_mod,
        "_agora_utc",
        lambda: tempo_mod._instante_redemet("2026-11-27 05:00:00"),
    )
    chamadas = []

    def getter(url, params=None, timeout=None):
        chamadas.append(url)
        if url.endswith("/metar"):
            return Resposta(204, b"")
        if url.endswith("/mensagens/taf/SBMT"):
            return Resposta(
                200,
                b"{}",
                {
                    "status": True,
                    "data": {
                        "taf": [
                            {
                                "id_localidade": "SBSP",
                                "mens": "TAF SBSP 270400Z 2706/2718 19010KT",
                                "recebimento": "2026-11-27 04:20:00",
                                "validade_inicial": "2026-11-27 06:00:00",
                                "validade_final": "2026-11-27 18:00:00",
                            },
                            {
                                "id_localidade": "SBMT",
                                "mens": "TAF SBMT 270000Z 2700/2704 18008KT",
                                "recebimento": "2026-11-27 00:20:00",
                                "validade_inicial": "2026-11-27 00:00:00",
                                "validade_final": "2026-11-27 04:00:00",
                            },
                        ]
                    },
                },
            )
        return Resposta(
            200,
            b"[{}]",
            [
                {
                    "rawTAF": "TAF SBMT 270400Z 2706/2718 18008KT",
                    "issueTime": "2026-11-27T04:20:00Z",
                }
            ],
        )

    resultado = meteorologia("SBMT", getter)

    assert resultado["taf"]["raw"] == "TAF SBMT 270400Z 2706/2718 18008KT"
    assert resultado["taf"]["fonte"] == "Aviation Weather Center"
    assert any("/mensagens/taf/SBMT" in url for url in chamadas)
    assert chamadas[-1].endswith("/taf")


def test_falha_taf_redemet_e_awc_preserva_metar_valido(monkeypatch):
    monkeypatch.setenv("REDEMET_API_KEY", "chave-de-teste")
    chamadas = []

    def getter(url, params=None, timeout=None):
        chamadas.append(url)
        if url.endswith("/metar"):
            return Resposta(
                200,
                b"[{}]",
                [{"icaoId": "SBJD", "rawOb": "METAR SBJD 011200Z"}],
            )
        raise requests.Timeout()

    resultado = meteorologia("SBJD", getter)

    assert resultado["estado"] == "disponivel"
    assert resultado["metar"]["raw"] == "METAR SBJD 011200Z"
    assert resultado["taf"]["estado"] == "indisponivel"
    assert any("/mensagens/taf/SBJD" in url for url in chamadas)


def test_metar_direto_tem_prioridade_sobre_busca_regional():
    aerodromo = _lugar(-23.2, -46.9, "SBJD")
    chamadas = []

    def getter(url, params=None, timeout=None):
        chamadas.append((url.rsplit("/", 1)[-1], params))
        if url.endswith("/metar"):
            return Resposta(
                200,
                b"[{}]",
                [{"icaoId": "SBJD", "name": "Aeródromo", "rawOb": "METAR SBJD 011200Z"}],
            )
        return Resposta(204, b"")

    resultado = tempo_mod.meteorologia_rota(
        aerodromo,
        aerodromo,
        getter,
        aerodromos=[aerodromo],
    )["aerodromos"]["SBJD"]

    assert resultado["metar"]["icao"] == "SBJD"
    assert resultado["metar"]["regional"] is False
    assert not any("bbox" in params for _, params in chamadas)


def test_meteorologia_rota_escolhe_estacao_regional_mais_proxima_e_desempata():
    aerodromo = _lugar(0, 0, "SBJD")
    chamadas = []
    bbox_consultado = []
    observacoes = [
        {
            "icaoId": "KZZZ",
            "name": "Estação B",
            "lat": 0,
            "lon": 0.2,
            "reportTime": "2026-12-01T12:00:00Z",
            "rawOb": "METAR KZZZ 011200Z",
        },
        {
            "icaoId": "KBBB",
            "name": "Estação distante",
            "lat": 0,
            "lon": 0.4,
            "reportTime": "2026-12-01T12:00:00Z",
            "rawOb": "METAR KBBB 011200Z",
        },
        {
            "icaoId": "KAAA",
            "name": "Estação A",
            "lat": 0,
            "lon": 0.2,
            "reportTime": "2026-12-01T12:00:00Z",
            "rawOb": "METAR KAAA 011200Z",
        },
    ]

    def getter(url, params=None, timeout=None):
        if url.endswith("/metar") and "bbox" in params:
            chamadas.append("bbox")
            bbox_consultado.append(params["bbox"])
            return Resposta(200, b"[{}]", observacoes)
        if url.endswith("/metar"):
            chamadas.append("metar")
            return Resposta(204, b"")
        chamadas.append("taf")
        return Resposta(204, b"")

    resultado = tempo_mod.meteorologia_rota(
        aerodromo,
        aerodromo,
        getter,
        aerodromos=[aerodromo],
    )["aerodromos"]["SBJD"]

    assert chamadas == ["metar", "taf", "bbox"]
    partes_bbox = bbox_consultado[0].split(",")
    assert len(partes_bbox) == 4
    assert all(len(parte.partition(".")[2]) <= 3 for parte in partes_bbox)
    assert resultado["estado"] == "disponivel"
    assert resultado["metar"]["icao"] == "KAAA"
    assert resultado["metar"]["nome_estacao"] == "Estação A"
    assert resultado["metar"]["aerodromo_referencia"] == "SBJD"
    assert resultado["metar"]["regional"] is True
    assert resultado["metar"]["distancia_nm"] < 50
    assert resultado["metar"]["hora"] == "2026-12-01T12:00:00Z"


def test_meteorologia_rota_aceita_50_nm_e_rejeita_estacao_mais_distante():
    aerodromo = _lugar(0, 0, "SBJD")
    raio_esferico_nm = 3440.065
    limite_lon = math.degrees(50 / raio_esferico_nm)
    observacoes = [
        {
            "icaoId": "K050",
            "name": "No limite",
            "lat": 0,
            "lon": limite_lon,
            "reportTime": "2026-12-01T12:00:00Z",
            "rawOb": "METAR K050 011200Z",
        },
        {
            "icaoId": "K051",
            "name": "Além do limite",
            "lat": 0,
            "lon": math.degrees(50.5 / raio_esferico_nm),
            "reportTime": "2026-12-01T12:00:00Z",
            "rawOb": "METAR K051 011200Z",
        },
    ]

    def getter(url, params=None, timeout=None):
        if url.endswith("/metar") and "bbox" in params:
            return Resposta(200, b"[{}]", observacoes)
        if url.endswith("/metar"):
            return Resposta(204, b"")
        return Resposta(204, b"")

    resultado = tempo_mod.meteorologia_rota(
        aerodromo,
        aerodromo,
        getter,
        aerodromos=[aerodromo],
    )["aerodromos"]["SBJD"]

    assert resultado["metar"]["icao"] == "K050"
    assert resultado["metar"]["distancia_nm"] <= 50


def test_meteorologia_rota_rejeita_metar_acima_de_50_nm():
    aerodromo = _lugar(0, 0, "SBJD")
    longitude = math.degrees(50.5 / 3440.065)

    def getter(url, params=None, timeout=None):
        if url.endswith("/metar") and "bbox" in params:
            return Resposta(
                200,
                b"[{}]",
                [
                    {
                        "icaoId": "K051",
                        "name": "Além do limite",
                        "lat": 0,
                        "lon": longitude,
                        "rawOb": "METAR K051 011200Z",
                    }
                ],
            )
        return Resposta(204, b"")

    resultado = tempo_mod.meteorologia_rota(
        aerodromo,
        aerodromo,
        getter,
        aerodromos=[aerodromo],
    )["aerodromos"]["SBJD"]

    assert resultado["metar"] is None
    assert resultado["estado"] == "indisponivel"


def test_meteorologia_rota_nao_busca_regional_sem_coordenadas_validas():
    aerodromo = _lugar(None, None, "SBJD")
    chamadas = []

    def getter(url, params=None, timeout=None):
        chamadas.append((url.rsplit("/", 1)[-1], params))
        return Resposta(204, b"")

    resultado = tempo_mod.meteorologia_rota(
        aerodromo,
        aerodromo,
        getter,
        aerodromos=[aerodromo],
    )["aerodromos"]["SBJD"]

    assert resultado["metar"] is None
    assert all("bbox" not in params for _, params in chamadas)


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
    monkeypatch.setattr(tempo_mod, "_metar_regional", lambda *args: None)
    monkeypatch.setattr(tempo_mod, "vento_area", lambda *args: {"estado": "indisponivel"})
    monkeypatch.setattr(tempo_mod, "carta", lambda *args: {"estado": "indisponivel"})
    monkeypatch.setattr(tempo_mod, "radar", lambda *args: {"estado": "indisponivel"})

    resultado = tempo_mod.buscar(origem, destino, aerodromos=[origem, escala, destino, escala])

    assert chamadas == ["SBJD", "SBAU"]
    assert set(resultado["meteorologia"]["aerodromos"]) == {"SBJD", "SBAU"}
    assert resultado["meteorologia"]["origem"] == resultado["meteorologia"]["aerodromos"]["SBJD"]
    assert resultado["meteorologia"]["destino"] == resultado["meteorologia"]["aerodromos"]["SBJD"]


def test_meteorologia_rota_consulta_cada_aerodromo_distinto_uma_vez(monkeypatch):
    origem = _lugar(-23.2, -46.9, "SBJD")
    destino = _lugar(-21.1, -50.4, "SBJD")
    escala = _lugar(-22.0, -47.0, "SBAU")
    chamadas = []

    def meteorologia_falsa(icao, getter=None):
        chamadas.append(icao)
        return {
            "estado": "disponivel",
            "metar": {"raw": f"METAR {icao} 011200Z"},
            "taf": None,
            "fonte": "Aviation Weather Center",
        }

    monkeypatch.setattr(tempo_mod, "meteorologia", meteorologia_falsa)
    monkeypatch.setattr(tempo_mod, "_metar_regional", lambda *args: None)

    resultado = tempo_mod.meteorologia_rota(
        origem,
        destino,
        aerodromos=[origem, escala, destino, escala],
    )

    assert chamadas == ["SBJD", "SBAU"]
    assert set(resultado["aerodromos"]) == {"SBJD", "SBAU"}
    assert resultado["origem"] == resultado["aerodromos"]["SBJD"]
    assert resultado["destino"] == resultado["aerodromos"]["SBJD"]


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


def test_campos_taf_separa_grupos_e_preserva_periodos():
    raw = (
        "TAF SBMT 270400Z 2706/2718 18008KT 9999 -RA BKN030 "
        "FM271000 22010G20KT 8000 SHRA SCT020CB "
        "BECMG 2712/2714 24015KT "
        "TEMPO 2714/2718 4000 +TSRA OVC012CB "
        "PROB30 2716/2718 3000 TSRA BKN008CB"
    )
    taf = {"raw": raw}

    grupos = campos_taf(taf)

    assert taf["raw"] == raw
    assert [grupo["tipo"] for grupo in grupos] == [
        "Previsão base",
        "FM",
        "BECMG",
        "TEMPO",
        "PROB30",
    ]
    assert [grupo["periodo"] for grupo in grupos] == [
        "2706/2718",
        "271000Z",
        "2712/2714",
        "2714/2718",
        "2716/2718",
    ]
    campos_base = {campo["nome"]: campo for campo in grupos[0]["campos"]}
    assert campos_base["Direção do vento"]["valor"] == "180"
    assert campos_base["Direção do vento"]["unidade"] == "graus"
    assert campos_base["Velocidade do vento"]["valor"] == "8"
    assert campos_base["Velocidade do vento"]["unidade"] == "kt"
    assert campos_base["Visibilidade"]["valor"] == "10 km ou mais"
    assert campos_base["Nuvens"]["valor"].startswith("BKN030")
    assert "3.000 ft" in campos_base["Nuvens"]["valor"]
    assert any(campo["valor"] == "SHRA" for campo in grupos[1]["campos"])
    assert any(campo["valor"] == "4000" for campo in grupos[3]["campos"])


def test_taf_becmg_periodo_e_temperatura_nao_quebram_o_grupo():
    from servidor.tempo import legenda_periodo_taf

    taf = {
        "raw": (
            "TAF SBAE 270800Z 2712/2724 13012KT 9999 SCT016 "
            "TX27/2717Z TN22/2723Z BECMG 2712/2715 SCT035 BEC-MG 2720/2723 CAVOK"
        )
    }
    grupos = campos_taf(taf)
    assert [grupo["tipo"] for grupo in grupos] == [
        "Previsão base",
        "BECMG",
        "BECMG",
    ]
    assert grupos[0]["periodo"] == "2712/2724"
    assert grupos[1]["periodo"] == "2712/2715"
    assert grupos[2]["periodo"] == "2720/2723"
    nomes = [campo["nome"] for campo in grupos[0]["campos"]]
    assert "Temperatura máxima" in nomes
    assert "Temperatura mínima" in nomes
    assert legenda_periodo_taf("2712/2724") == (
        "2712/2724 (dia 27, 12 UTC até fim do dia 27)"
    )
    assert legenda_periodo_taf("2712/2715") == (
        "2712/2715 (dia 27, 12 UTC até dia 27, 15 UTC)"
    )


def test_campos_taf_sem_mensagem_nao_inventa_grupos():
    assert campos_taf({"estado": "indisponivel"}) == []


def test_fenomenos_metar_e_taf_incluem_explicacao_sem_inventar_desconhecidos():
    codigos = "-SHRA +TSRASN XYZ"
    campos_metar_resultado = campos_metar({"fenomenos": codigos})
    fenomenos_metar = next(
        campo
        for campo in campos_metar_resultado
        if campo["nome"] == "Fenômenos meteorológicos (código AWC)"
    )

    assert fenomenos_metar["valor"] == codigos
    assert "pancadas fracas de chuva" in fenomenos_metar["explicacao"].lower()
    assert "trovoada com chuva forte e neve" in fenomenos_metar["explicacao"].lower()
    assert "Código não interpretado: XYZ" in fenomenos_metar["explicacao"]

    taf = campos_taf(
        {
            "raw": (
                "TAF SBMT 270400Z 2706/2718 18008KT 9999 VCTS "
                "-FZRA BKN030 XYZ"
            )
        }
    )
    fenomenos_taf = [
        campo
        for campo in taf[0]["campos"]
        if campo["nome"] == "Fenômenos meteorológicos"
    ]

    assert [campo["valor"] for campo in fenomenos_taf] == ["VCTS", "-FZRA"]
    assert "trovoada nas proximidades" in fenomenos_taf[0]["explicacao"].lower()
    assert "chuva congelante fraca" in fenomenos_taf[1]["explicacao"].lower()
    codigo_taf_desconhecido = next(
        campo for campo in taf[0]["campos"] if campo["nome"] == "Código não interpretado"
    )
    assert codigo_taf_desconhecido["valor"] == "XYZ"
    assert "não foi atribuída uma descrição" in codigo_taf_desconhecido["explicacao"]


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


def test_satelite_seleciona_frame_mais_recente_e_limites_da_fonte(monkeypatch):
    monkeypatch.setenv("REDEMET_API_KEY", "chave-de-teste")
    corpo = {
        "status": True,
        "data": {
            "tipo": "realcada",
            "lat_lon": {
                "lat_min": "-56",
                "lat_max": "12.52",
                "lon_min": "-100",
                "lon_max": "-25.24",
            },
            "satelite": [
                {
                    "data": "2026-11-27 20:20:00",
                    "path": "https://estatico-redemet.decea.mil.br/satelite/frame-antigo.png",
                },
                {
                    "data": "2026-11-27 22:40:00",
                    "path": "https://estatico-redemet.decea.mil.br/satelite/frame-recente.png",
                },
            ],
        },
    }

    def getter(url, params=None, timeout=None):
        assert url == "https://api-redemet.decea.mil.br/produtos/satelite/realcada"
        assert params == {"api_key": "chave-de-teste", "anima": 10}
        assert timeout == 8
        return Resposta(200, b"", corpo)

    resultado = tempo_mod.satelite(getter)

    assert resultado == {
        "estado": "disponivel",
        "url": "https://estatico-redemet.decea.mil.br/satelite/frame-recente.png",
        "hora": "2026-11-27 22:40:00",
        "lat_min": -56.0,
        "lat_max": 12.52,
        "lon_min": -100.0,
        "lon_max": -25.24,
        "fonte": "REDEMET Satélite realçada",
    }


def test_satelite_sem_chave_ou_metadados_validos_fica_indisponivel(monkeypatch):
    monkeypatch.delenv("REDEMET_API_KEY", raising=False)
    assert tempo_mod.satelite() == {"estado": "indisponivel"}

    monkeypatch.setenv("REDEMET_API_KEY", "chave-de-teste")
    corpo_invalido = {
        "status": True,
        "data": {
            "tipo": "realcada",
            "lat_lon": {
                "lat_min": -91,
                "lat_max": 12.52,
                "lon_min": -100,
                "lon_max": -25.24,
            },
            "satelite": [
                {
                    "data": "",
                    "path": "https://imagem.example/frame.png",
                }
            ],
        },
    }

    def getter(url, params=None, timeout=None):
        return Resposta(200, b"", corpo_invalido)

    assert tempo_mod.satelite(getter) == {"estado": "indisponivel"}


def test_satelite_com_falha_de_rede_fica_indisponivel(monkeypatch):
    monkeypatch.setenv("REDEMET_API_KEY", "chave-de-teste")

    def indisponivel(url, params=None, timeout=None):
        raise requests.Timeout()

    assert tempo_mod.satelite(indisponivel) == {"estado": "indisponivel"}


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


def test_cartas_wac_sao_consultadas_por_aerodromo_e_ordenadas_na_rota(monkeypatch):
    monkeypatch.setenv("AISWEB_API_KEY", "teste")
    monkeypatch.setenv("AISWEB_API_PASS", "teste")
    origem = _lugar(-23.2, -46.9, "SBJD")
    escala = _lugar(-22.0, -47.0, "SBAU")
    destino = _lugar(-21.1, -50.4, "SBBU")
    chamadas = []
    cartas_por_icao = {
        "SBJD": (
            '<item><id>3182</id><tipo>WAC</tipo><nome>WAC 3182</nome>'
            '<IcaoCode>SBJD</IcaoCode><link>https://exemplo.invalid/3182.pdf</link></item>'
        ),
        "SBAU": (
            '<item><id>3182</id><tipo>WAC</tipo><nome>WAC 3182</nome>'
            '<IcaoCode>SBAU</IcaoCode><link>https://exemplo.invalid/3182.pdf</link></item>'
        ),
        "SBBU": (
            '<item><id>3183</id><tipo>WAC</tipo><nome>WAC 3183</nome>'
            '<IcaoCode>SBBU</IcaoCode><link>https://exemplo.invalid/3183.pdf</link></item>'
        ),
    }

    def cobre(url, params=None, timeout=None):
        assert url == "https://api.decea.mil.br/aisweb/"
        assert timeout == 8
        chamadas.append(dict(params))
        assert params["area"] == "cartas"
        assert params["especie"] == "VFR"
        assert params["tipo"] == "WAC"
        return Resposta(200, f"<aisweb>{cartas_por_icao[params['icaoCode']]}</aisweb>".encode())

    carta_rota = carta(origem, destino, cobre, [origem, escala, destino])
    assert carta_rota["estado"] == "disponivel"
    assert carta_rota["tipo"] == "pdf"
    assert [item["indice"] for item in carta_rota["documentos"]] == ["3182", "3183"]
    assert [item["icao"] for item in carta_rota["documentos"]] == ["SBJD", "SBBU"]
    assert [item["url"] for item in carta_rota["documentos"]] == [
        "https://exemplo.invalid/3182.pdf",
        "https://exemplo.invalid/3183.pdf",
    ]
    assert [chamada["icaoCode"] for chamada in chamadas] == ["SBJD", "SBAU", "SBBU"]


def test_carta_nao_infere_cobertura_por_bounds_nao_documentados(monkeypatch):
    monkeypatch.setenv("AISWEB_API_KEY", "teste")
    monkeypatch.setenv("AISWEB_API_PASS", "teste")

    def resposta_com_bounds(url, params=None, timeout=None):
        return Resposta(
            200,
            b"<aisweb><item><nome>WAC 3182</nome><link>https://exemplo.invalid/wac3182</link>"
            b"<lat_min>-34</lat_min><lat_max>-20</lat_max>"
            b"<lon_min>-55</lon_min><lon_max>-40</lon_max></item></aisweb>",
        )

    resultado = carta(
        _lugar(-23.2, -46.9, "SBJD"),
        _lugar(-21.1, -50.4, "SBAU"),
        resposta_com_bounds,
    )

    assert resultado == {"estado": "indisponivel"}


def test_cartas_wac_ficam_indisponiveis_se_um_aerodromo_nao_tiver_indice(
    monkeypatch,
):
    monkeypatch.setenv("AISWEB_API_KEY", "teste")
    monkeypatch.setenv("AISWEB_API_PASS", "teste")

    def resposta_parcial(url, params=None, timeout=None):
        if params["icaoCode"] == "SBJD":
            xml = (
                "<aisweb><item><id>3182</id><tipo>WAC</tipo>"
                "<IcaoCode>SBJD</IcaoCode><link>https://exemplo.invalid/3182.pdf</link>"
                "</item></aisweb>"
            )
        else:
            xml = "<aisweb><item><tipo>WAC</tipo><nome>WAC sem referência</nome></item></aisweb>"
        return Resposta(200, xml.encode())

    resultado = carta(
        _lugar(-23.2, -46.9, "SBJD"),
        _lugar(-21.1, -50.4, "SBAU"),
        resposta_parcial,
    )

    assert resultado == {"estado": "indisponivel"}


def test_tela_mostra_boletim_atual_e_pdf_preserva_o_snapshot(cliente, monkeypatch):
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

    boletim_atual = {
        "estado": "disponivel",
        "origem": {
            "estado": "disponivel",
            "metar": {"raw": "METAR SBJD 121300Z 19012KT"},
            "taf": {"raw": "TAF SBJD 121200Z 19010KT"},
        },
        "destino": {
            "estado": "disponivel",
            "metar": {"raw": "METAR SBAU 121300Z 10006KT"},
            "taf": {"estado": "indisponivel"},
        },
        "aerodromos": {},
    }
    monkeypatch.setattr(
        tempo_mod,
        "meteorologia_rota",
        lambda *args, **kwargs: boletim_atual,
    )
    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)
    assert "METAR SBJD 121300Z 19012KT" in html
    assert "TAF SBJD 121200Z 19010KT" in html
    assert "METAR SBAU 121300Z 10006KT" in html
    assert "METAR SBJD 121200Z 18010KT" not in html
    assert "TAF da chegada indisponível" in html

    pdf = cliente.get(f"/planos/{plano_id}/pdf").data
    assert b"METAR SBJD 121200Z 18010KT" in pdf
    assert b"TAF SBJD 121100Z 18008KT" in pdf
    assert b"TAF destino: indispon\\355vel" in pdf

    monkeypatch.setattr(
        tempo_mod,
        "meteorologia_rota",
        lambda *args, **kwargs: {
            "estado": "indisponivel",
            "origem": {"estado": "indisponivel"},
            "destino": {"estado": "indisponivel"},
            "aerodromos": {},
        },
    )
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
