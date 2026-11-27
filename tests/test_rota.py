from math import sqrt
from types import SimpleNamespace

import servidor.rota as rota_mod
import servidor.planos as planos_mod
from servidor import tempo as tempo_mod
from servidor.calculo import distancia_nm, proa_graus
from servidor.modelos import (
    Aerodromo,
    Aeronave,
    EmendaRotaer,
    ExtratoRab,
    PlanoDeVoo,
    Sessao,
)
from servidor.rota import escolher
from tests.conftest import JSON, cadastrar
from tests.conftest_rota import preparar_rota, semear_perfis_sinteticos_teste

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


def test_busca_com_muitos_aerodromos_poda_rotas_fora_do_otimo(monkeypatch):
    aviao = _aviao()
    origem = _lugar("ORIGEM", 0, 0)
    destino = _lugar("DESTINO", 0, 40)
    distracoes = [
        _lugar(
            f"N{i:04d}",
            0.5 + (i % 17) * 0.05,
            0.5 + (i // 17) * 0.1,
        )
        for i in range(400)
    ]
    chamadas_distancia = 0
    chamadas_calculo = 0
    distancia_original = rota_mod.distancia_nm
    calcular_original = rota_mod.calcular

    def contar_distancia(*args):
        nonlocal chamadas_distancia
        chamadas_distancia += 1
        return distancia_original(*args)

    def contar_calculo(*args, **kwargs):
        nonlocal chamadas_calculo
        chamadas_calculo += 1
        return calcular_original(*args, **kwargs)

    monkeypatch.setattr(rota_mod, "distancia_nm", contar_distancia)
    monkeypatch.setattr(rota_mod, "calcular", contar_calculo)
    lugares = [origem, destino, *distracoes]

    rota = escolher(aviao, lugares, origem, destino, PARTICULARES)

    assert rota["rota_estado"] == "aceitavel"
    assert _caminho(rota) == ["ORIGEM", "DESTINO"]
    assert chamadas_distancia < len(lugares) * 8
    assert chamadas_calculo <= len(lugares)


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


def test_busca_meteorologia_uma_vez_por_aerodromo_da_rota(cliente, monkeypatch):
    cadastrar(cliente)
    ids = preparar_rota()
    chamadas = []

    def meteorologia_falsa(icao, getter=None):
        chamadas.append(icao)
        if icao == "S0B2":
            return {
                "estado": "disponivel",
                "metar": {"raw": "METAR S0B2"},
                "taf": None,
                "fonte": "Aviation Weather Center",
            }
        return {"estado": "indisponivel", "fonte": "Aviation Weather Center"}

    monkeypatch.setattr(tempo_mod, "meteorologia", meteorologia_falsa)
    monkeypatch.setattr(tempo_mod, "vento_area", lambda *args: {"estado": "indisponivel"})
    monkeypatch.setattr(tempo_mod, "carta", lambda *args: {"estado": "indisponivel"})
    monkeypatch.setattr(tempo_mod, "radar", lambda *args: {"estado": "indisponivel"})

    resposta = cliente.post(
        "/planos",
        json=_pedido(ids["alfa"], "S0A1", "S0C3"),
        headers=JSON,
    )

    assert resposta.status_code == 201
    corpo = resposta.get_json()
    assert _caminho(corpo["rota"]) == ["S0A1", "S0B2", "S0C3"]
    assert chamadas == ["S0A1", "S0B2", "S0C3"]
    meteo = corpo["meteorologia"]
    assert meteo["estado"] == "disponivel"
    assert set(meteo["aerodromos"]) == {"S0A1", "S0B2", "S0C3"}
    assert meteo["aerodromos"]["S0B2"]["metar"]["raw"] == "METAR S0B2"
    assert meteo["aerodromos"]["S0A1"]["estado"] == "indisponivel"
    assert meteo["origem"] == meteo["aerodromos"]["S0A1"]
    assert meteo["destino"] == meteo["aerodromos"]["S0C3"]


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


def test_lista_local_nao_permite_plano_sem_emenda_rotaer_vigente(cliente):
    cadastrar(cliente)
    ids = preparar_rota()
    criado = cliente.post(
        "/planos",
        json=_pedido(ids["alfa"], "S0A1", "S0B2"),
        headers=JSON,
    )
    assert criado.status_code == 201
    plano_id = criado.get_json()["id"]
    db = Sessao()
    try:
        emenda = db.query(EmendaRotaer).filter_by(vigente=True, estado="disponivel").one()
        emenda.vigente = False
        emenda.estado = "indisponivel"
        db.commit()
    finally:
        Sessao.remove()

    tela = cliente.get("/planos/novo").get_data(as_text=True)
    assert "Lista local. Não é o catálogo do país inteiro." in tela
    assert 'value="S0A1"' in tela

    resposta = cliente.post(
        "/planos",
        json=_pedido(ids["alfa"], "S0A1", "S0B2"),
        headers=JSON,
    )
    assert resposta.status_code == 400
    assert resposta.get_json()["mensagem"] == "Catálogo nacional indisponível."

    alteracao = cliente.post(
        f"/planos/{plano_id}/alterar",
        data=_pedido(ids["alfa"], "S0A1", "S0B2"),
    )
    assert alteracao.status_code == 400


def test_post_e_put_recusam_aeronave_fora_da_selecao_vigente(cliente):
    cadastrar(cliente)
    ids = preparar_rota()
    db = Sessao()
    try:
        fora_da_selecao = Aeronave(
            nome="Modelo Fora da Seleção",
            frota=1,
            manual_estado="gravado",
            fonte_manual="POH fictício, variante X, edição 1",
            peso_vazio_kg=500,
            peso_max_decolagem_kg=900,
            bagagem_max_kg=20,
            braco_bagagem_m=1.2,
            combustivel_valor=12,
            combustivel_unidade="gal",
            velocidade_valor=100,
            velocidade_unidade="kt",
            consumo_valor=10,
            consumo_unidade="gal/h",
            itens_manutencao=[],
        )
        db.add(fora_da_selecao)
        db.commit()
        fora_da_selecao_id = fora_da_selecao.id
    finally:
        Sessao.remove()

    dados_fora = _pedido(fora_da_selecao_id, "S0A1", "S0B2")
    recusado = cliente.post("/planos", json=dados_fora, headers=JSON)
    assert recusado.status_code == 400
    assert "seleção" in recusado.get_json()["mensagem"].casefold()

    criado = cliente.post(
        "/planos",
        json=_pedido(ids["alfa"], "S0A1", "S0B2"),
        headers=JSON,
    )
    assert criado.status_code == 201
    plano_id = criado.get_json()["id"]

    recusado = cliente.put(f"/planos/{plano_id}", json=dados_fora, headers=JSON)
    assert recusado.status_code == 400
    assert "seleção" in recusado.get_json()["mensagem"].casefold()
    assert cliente.get(f"/planos/{plano_id}", headers=JSON).get_json()["aeronave_id"] == ids["alfa"]


def test_perfil_sintetico_exige_emenda_rotaer_vigente(cliente):
    cadastrar(cliente)
    preparar_rota()
    db = Sessao()
    try:
        ids = semear_perfis_sinteticos_teste(db)
        for emenda in db.query(EmendaRotaer).all():
            emenda.vigente = False
        db.commit()
    finally:
        Sessao.remove()

    resposta = cliente.post(
        "/planos",
        json=_pedido(ids["CESSNA AIRCRAFT 152"], "S0A1", "S0B2"),
        headers=JSON,
    )

    assert resposta.status_code == 400
    assert "ROTAER" in resposta.get_json()["mensagem"]


def test_perfil_sintetico_pode_ser_calculado_sem_rab(cliente):
    cadastrar(cliente)
    preparar_rota()
    db = Sessao()
    try:
        ids = semear_perfis_sinteticos_teste(db)
        for aeronave in db.query(Aeronave).all():
            aeronave.extrato_id = None
        db.query(ExtratoRab).delete(synchronize_session=False)
        db.commit()
    finally:
        Sessao.remove()

    resposta = cliente.post(
        "/planos",
        json=_pedido(ids["CESSNA AIRCRAFT 152"], "S0A1", "S0B2"),
        headers=JSON,
    )

    assert resposta.status_code == 201
    resultado = resposta.get_json()["resultado"]
    assert resultado["proxy_sintetico"] is True
    assert resultado["modelo_alvo"] == "CESSNA AIRCRAFT 152"


def test_empate_prefere_menos_escalas_e_depois_distancia():
    aviao = _aviao()
    ta, tb, tc = _lugar("TA", 0, 0), _lugar("TB", 24, 55), _lugar("TC", 0, 110)
    tx, ty = _lugar("TX", 19.6389737287963, 36), _lugar(
        "TY", 19.6389737287963, 74
    )
    rota = escolher(aviao, [ta, tb, tc, tx, ty], ta, tc, PARTICULARES)
    assert rota["rota_estado"] == "aceitavel"
    assert _caminho(rota) == ["TA", "TB", "TC"]

    da, dc = _lugar("DA", 0, 0), _lugar("DC", 0, 90)
    altura_curta = sqrt(50**2 - 45**2)
    altura_longa = 39.68667785813085
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


def test_rota_fuel_based_remains_available_for_daylight_scheduler():
    aviao = _aviao()
    origem = _lugar("SA", 0, 0)
    destino = _lugar("SB", 0, 30)

    rota = escolher(
        aviao,
        [origem, destino],
        origem,
        destino,
        PARTICULARES,
    )
    assert rota["rota_estado"] == "aceitavel"
    assert _caminho(rota) == ["SA", "SB"]


def test_plano_persiste_programacao_calculada_pelo_servidor(cliente, monkeypatch):
    cadastrar(cliente)
    ids = preparar_rota()
    chamadas_sol = []

    def sol_aerodromo_falso(icao, instante):
        chamadas_sol.append((icao, instante.date()))
        nascer = instante.replace(hour=6, minute=0, second=0, microsecond=0)
        por = instante.replace(hour=20, minute=0, second=0, microsecond=0)
        return {
            "estado": "disponivel",
            "nascer_do_sol": nascer,
            "por_do_sol": por,
            "fonte": "AISWEB sol",
        }

    monkeypatch.setattr(planos_mod, "sol_aerodromo", sol_aerodromo_falso)
    monkeypatch.setattr(
        tempo_mod,
        "vento_area",
        lambda *args, **kwargs: {"estado": "indisponivel"},
    )
    monkeypatch.setattr(
        tempo_mod,
        "buscar",
        lambda *args, **kwargs: {
            "meteorologia": {"estado": "indisponivel"},
            "vento": {"estado": "indisponivel"},
            "carta": {"estado": "indisponivel"},
            "radar": {"estado": "indisponivel"},
        },
    )

    resposta = cliente.post(
        "/planos",
        json=_pedido(ids["alfa"], "S0A1", "S0C3"),
        headers=JSON,
    )

    assert resposta.status_code == 201
    corpo = resposta.get_json()
    programacao = corpo["resultado"]["programacao"]
    assert corpo["programacao"] == programacao
    assert programacao["estado"] == "disponivel"
    assert len(programacao["trechos"]) == 2
    assert programacao["trechos"][0]["etd"].endswith("+00:00")
    assert programacao["trechos"][0]["eta"].endswith("+00:00")
    assert chamadas_sol

    db = Sessao()
    try:
        plano = db.get(PlanoDeVoo, corpo["id"])
        assert plano.resultado["programacao"] == programacao
    finally:
        Sessao.remove()
