from datetime import datetime, timedelta, timezone
from math import sqrt
from types import SimpleNamespace

from servidor.calculo import distancia_nm, proa_graus
from servidor.modelos import Aerodromo, Sessao
from servidor.rota import escolher
from tests.conftest import JSON, cadastrar
from tests.conftest_rota import preparar_rota

PARTICULARES = {
    "numero_passageiros": 1,
    "peso_pessoas_kg": 80,
    "peso_bagagem_kg": 5,
}


def _aviao(**extra):
    dados = dict(
        fonte_manual="manual de teste de rota",
        velocidade_valor=100.0,
        velocidade_unidade="kt",
        consumo_valor=10.0,
        consumo_unidade="gal/h",
        combustivel_valor=12.0,
        combustivel_unidade="gal",
        peso_vazio_kg=510.0,
        peso_max_decolagem_kg=900.0,
        bagagem_max_kg=20.0,
    )
    dados.update(extra)
    return SimpleNamespace(**dados)


def _lugar(icao, norte_nm, leste_nm):
    return SimpleNamespace(
        icao=icao,
        nome=icao,
        tipo="aerodromo",
        fonte="teste",
        lat=norte_nm / 60.04,
        lon=leste_nm / 60.04,
        elev_m=1,
    )


def _pedido(aeronave_id, origem, destino):
    return {
        "aeronave_id": aeronave_id,
        "origem": origem,
        "destino": destino,
        "hora_partida": "2026-12-01T12:00:00+00:00",
        **PARTICULARES,
    }


def _caminho(rota):
    trechos = rota["trechos"]
    return [trechos[0]["origem"]] + [trecho["destino"] for trecho in trechos]


def test_direto_unico_sem_credito_de_cauda(cliente):
    cadastrar(cliente)
    ids = preparar_rota()
    resposta = cliente.post("/planos", json=_pedido(ids["alfa"], "S0A1", "S0B2"), headers=JSON)
    corpo = resposta.get_json()
    assert resposta.status_code == 201
    assert corpo["estado"] == "calculado"
    assert corpo["rota"]["criterio"] == "menor tempo de voo"
    assert len(corpo["rota"]["trechos"]) == 1
    trecho = corpo["rota"]["trechos"][0]
    assert trecho["origem"] == "S0A1"
    assert trecho["destino"] == "S0B2"
    assert trecho["vento_estado"] == "indisponivel"
    assert trecho["velocidade_solo_kt"] == 100
    nomes = [linha["nome"] for linha in corpo["resultado"]["linhas"]]
    assert "Velocidade em relação ao solo" not in nomes
    assert corpo["resultado"]["efeito_vento"] == "vento não aplicado"


def test_escala_quando_direto_nao_cabe(cliente):
    cadastrar(cliente)
    ids = preparar_rota()
    resposta = cliente.post("/planos", json=_pedido(ids["alfa"], "S0A1", "S0C3"), headers=JSON)
    corpo = resposta.get_json()
    assert resposta.status_code == 201
    assert corpo["estado"] == "calculado"
    assert corpo["rota"]["criterio"] == "menor tempo de voo"
    assert _caminho(corpo["rota"]) == ["S0A1", "S0B2", "S0C3"]
    for trecho in corpo["rota"]["trechos"]:
        for parte in ("distancia", "proa", "tempo", "combustivel"):
            assert trecho[parte]["unidade"]
            assert trecho[parte]["fonte"]
        assert trecho["combustivel"]["valor"] <= 12


def test_rota_impossivel_gravada(cliente):
    cadastrar(cliente)
    ids = preparar_rota()
    db = Sessao()
    try:
        meio = db.get(Aerodromo, "S0B2")
        meio.tipo = "heliponto"
        db.commit()
    finally:
        Sessao.remove()
    resposta = cliente.post("/planos", json=_pedido(ids["alfa"], "S0A1", "S0C3"), headers=JSON)
    corpo = resposta.get_json()
    assert resposta.status_code == 201
    assert corpo["estado"] == "inaceitavel"
    assert corpo["rota"]["estado"] == "inaceitavel"
    assert corpo["rota"]["trechos"] == []
    assert "reserva de 30 minutos" in corpo["motivo"]
    lista = cliente.get("/painel", headers=JSON).get_json()
    assert lista[0]["estado"] == "inaceitavel"


def test_empate_prefere_menos_escalas_e_depois_distancia():
    aviao = _aviao()
    ta, tb, tc = _lugar("TA", 0, 0), _lugar("TB", 24, 55), _lugar("TC", 0, 110)
    tx, ty = _lugar("TX", 19.6, 36), _lugar("TY", 19.6, 74)
    rota = escolher(aviao, [ta, tb, tc, tx, ty], ta, tc, PARTICULARES)
    assert rota["rota_estado"] == "aceitavel"
    assert _caminho(rota) == ["TA", "TB", "TC"]

    da, dc = _lugar("DA", 0, 0), _lugar("DC", 0, 90)
    altura_curta = sqrt(50**2 - 45**2)
    altura_longa = sqrt(60**2 - 45**2)
    dd = _lugar("DD", altura_curta, 45)
    db = _lugar("DB", -altura_longa, 45)

    def vento_de(saida, chegada):
        if "DD" not in (saida.icao, chegada.icao):
            return {"estado": "indisponivel"}
        milhas = distancia_nm(saida.lat, saida.lon, chegada.lat, chegada.lon)
        return {
            "estado": "disponivel",
            "direcao_de_graus": proa_graus(saida.lat, saida.lon, chegada.lat, chegada.lon),
            "velocidade_kt": 100 - (milhas / 0.6),
            "fonte": "vento de teste",
        }

    desempate = escolher(
        aviao, [da, db, dc, dd], da, dc, PARTICULARES, vento_de=vento_de
    )
    assert desempate["rota_estado"] == "aceitavel"
    assert _caminho(desempate) == ["DA", "DD", "DC"]


def test_vento_de_cauda_nao_estende_o_alcance_em_ar_calmo():
    aviao = _aviao()
    origem = _lugar("VA", 0, 0)
    perto = _lugar("VB", 0, 30)
    longe = _lugar("VC", 0, 80)

    def cauda(saida, chegada):
        rumo = proa_graus(saida.lat, saida.lon, chegada.lat, chegada.lon)
        return {
            "estado": "disponivel",
            "direcao_de_graus": (rumo + 180) % 360,
            "velocidade_kt": 40,
            "fonte": "vento de teste",
        }

    curto = escolher(aviao, [origem, perto], origem, perto, PARTICULARES)
    assert curto["rota_estado"] == "aceitavel"
    assert curto["trechos"][0]["velocidade_solo_kt"] == 100
    longo = escolher(aviao, [origem, longe], origem, longe, PARTICULARES, vento_de=cauda)
    assert longo["rota_estado"] == "inaceitavel"
    assert longo["trechos"] == []


def test_por_do_sol_conhecido_tira_o_trecho_da_rota():
    aviao = _aviao()
    origem = _lugar("SA", 0, 0)
    destino = _lugar("SB", 0, 30)
    hora = datetime(2026, 12, 1, 12, tzinfo=timezone.utc)

    def sol_de(_aero, _chegada):
        return {"estado": "disponivel", "por_do_sol": hora + timedelta(minutes=1)}

    rota = escolher(
        aviao,
        [origem, destino],
        origem,
        destino,
        PARTICULARES,
        sol_de=sol_de,
        hora_partida=hora,
    )
    assert rota["rota_estado"] == "inaceitavel"
    assert "pôr do sol" in rota["motivo"]
