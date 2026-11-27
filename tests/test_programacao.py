from datetime import datetime, timezone

from servidor.programacao import programar


UTC = timezone.utc


def _instante(dia, hora, minuto=0):
    return datetime(2026, 12, dia, hora, minuto, tzinfo=UTC)


def _trecho(ordem, origem, destino, duracao_h):
    return {
        "ordem": ordem,
        "origem": origem,
        "destino": destino,
        "tempo_valor": duracao_h,
        "tempo_unidade": "h",
    }


def _sol(nascer, por):
    return {
        "estado": "disponivel",
        "nascer_do_sol": nascer,
        "por_do_sol": por,
        "fonte": "AISWEB sol",
    }


def _consultor(dados):
    chamadas = []

    def consultar(icao, instante):
        chave = (icao, instante.date())
        chamadas.append(chave)
        return dados.get(chave, {"estado": "indisponivel"})

    return consultar, chamadas


def test_partida_antes_do_nascer_e_adiada_sem_pernoite():
    dia = _instante(1, 0).date()
    dados = {
        ("A", dia): _sol(_instante(1, 6), _instante(1, 18)),
        ("B", dia): _sol(_instante(1, 7), _instante(1, 19)),
    }
    consultar, _chamadas = _consultor(dados)

    agenda = programar(
        [_trecho(1, "A", "B", 1)],
        _instante(1, 5, 30),
        consultar,
    )

    assert agenda["estado"] == "disponivel"
    trecho = agenda["trechos"][0]
    assert trecho["etd"] == "2026-12-01T06:00:00+00:00"
    assert trecho["eta"] == "2026-12-01T07:00:00+00:00"
    assert trecho["pernoite"] is None


def test_chegada_exatamente_no_por_do_sol_e_aceita():
    dia = _instante(1, 0).date()
    dados = {
        ("A", dia): _sol(_instante(1, 6), _instante(1, 18)),
        ("B", dia): _sol(_instante(1, 5), _instante(1, 13)),
    }
    consultar, _chamadas = _consultor(dados)

    agenda = programar(
        [_trecho(1, "A", "B", 1)],
        _instante(1, 12),
        consultar,
    )

    assert agenda["estado"] == "disponivel"
    assert agenda["trechos"][0]["eta"] == "2026-12-01T13:00:00+00:00"


def test_excesso_do_por_do_sol_tenta_so_o_proximo_nascer_e_registra_pernoite():
    dia_um = _instante(1, 0).date()
    dia_dois = _instante(2, 0).date()
    dados = {
        ("A", dia_um): _sol(_instante(1, 6), _instante(1, 12)),
        ("B", dia_um): _sol(_instante(1, 6), _instante(1, 12)),
        ("A", dia_dois): _sol(_instante(2, 6), _instante(2, 18)),
        ("B", dia_dois): _sol(_instante(2, 5), _instante(2, 18)),
    }
    consultar, chamadas = _consultor(dados)

    agenda = programar(
        [_trecho(1, "A", "B", 1)],
        _instante(1, 11, 30),
        consultar,
    )

    assert agenda["estado"] == "disponivel"
    trecho = agenda["trechos"][0]
    assert trecho["etd"] == "2026-12-02T06:00:00+00:00"
    assert trecho["eta"] == "2026-12-02T07:00:00+00:00"
    assert trecho["pernoite"] == {"icao": "A", "data": "2026-12-01"}
    assert chamadas.count(("A", dia_um)) == 1
    assert chamadas.count(("A", dia_dois)) == 1


def test_sequencia_de_trechos_registra_pernoite_no_aerodromo_da_segunda_perna():
    dia_um = _instante(1, 0).date()
    dia_dois = _instante(2, 0).date()
    dados = {
        ("A", dia_um): _sol(_instante(1, 6), _instante(1, 18)),
        ("B", dia_um): _sol(_instante(1, 6), _instante(1, 18)),
        ("C", dia_um): _sol(_instante(1, 6), _instante(1, 11)),
        ("B", dia_dois): _sol(_instante(2, 6), _instante(2, 18)),
        ("C", dia_dois): _sol(_instante(2, 6), _instante(2, 18)),
    }
    consultar, _chamadas = _consultor(dados)

    agenda = programar(
        [_trecho(1, "A", "B", 1), _trecho(2, "B", "C", 2)],
        _instante(1, 9),
        consultar,
    )

    assert agenda["estado"] == "disponivel"
    assert agenda["trechos"][0]["eta"] == "2026-12-01T10:00:00+00:00"
    assert agenda["trechos"][1]["etd"] == "2026-12-02T06:00:00+00:00"
    assert agenda["trechos"][1]["eta"] == "2026-12-02T08:00:00+00:00"
    assert agenda["trechos"][1]["pernoite"] == {
        "icao": "B",
        "data": "2026-12-01",
    }


def test_uma_hora_de_abastecimento_separa_a_chegada_da_partida_seguinte():
    dia = _instante(1, 0).date()
    sol = _sol(_instante(1, 6), _instante(1, 20))
    consultar, _chamadas = _consultor(
        {("A", dia): sol, ("B", dia): sol, ("C", dia): sol}
    )

    agenda = programar(
        [_trecho(1, "A", "B", 1), _trecho(2, "B", "C", 1)],
        _instante(1, 9),
        consultar,
    )

    assert agenda["estado"] == "disponivel"
    assert agenda["intervalo_abastecimento_h"] == 1
    assert agenda["trechos"][0]["eta"] == "2026-12-01T10:00:00+00:00"
    assert agenda["trechos"][1]["etd"] == "2026-12-01T11:00:00+00:00"
    assert agenda["trechos"][1]["eta"] == "2026-12-01T12:00:00+00:00"
    assert agenda["trechos"][1]["pernoite"] is None


def test_falta_de_dados_solares_invalida_agenda_sem_inventar_horarios():
    consultar, _chamadas = _consultor({})

    agenda = programar(
        [_trecho(1, "A", "B", 1)],
        _instante(1, 9),
        consultar,
    )

    assert agenda["estado"] == "indisponivel"
    assert agenda["trechos"][0]["estado"] == "indisponivel"
    assert agenda["trechos"][0]["etd"] is None
    assert agenda["trechos"][0]["eta"] is None


def test_trecho_que_nao_cabe_apos_uma_tentativa_fica_indisponivel():
    dia_um = _instante(1, 0).date()
    dia_dois = _instante(2, 0).date()
    dados = {
        ("A", dia_um): _sol(_instante(1, 6), _instante(1, 8)),
        ("A", dia_dois): _sol(_instante(2, 6), _instante(2, 8)),
        ("B", dia_um): _sol(_instante(1, 6), _instante(1, 8)),
        ("B", dia_dois): _sol(_instante(2, 6), _instante(2, 8)),
    }
    consultar, chamadas = _consultor(dados)

    agenda = programar(
        [_trecho(1, "A", "B", 4)],
        _instante(1, 6),
        consultar,
    )

    assert agenda["estado"] == "indisponivel"
    assert agenda["trechos"][0]["motivo"] == "nao_cabe_no_periodo_diurno"
    assert agenda["trechos"][0]["etd"] is None
    assert agenda["trechos"][0]["eta"] is None
    assert chamadas.count(("A", dia_um)) == 1
    assert chamadas.count(("A", dia_dois)) == 1
    assert sum(1 for icao, _dia in chamadas if icao == "A") == 2


def test_cache_solar_e_limitado_a_mesmo_aerodromo_e_data():
    dia = _instante(1, 0).date()
    consulta = _sol(_instante(1, 6), _instante(1, 18))
    consultar, chamadas = _consultor(
        {
            ("A", dia): consulta,
            ("B", dia): consulta,
            ("C", dia): consulta,
        }
    )

    programar(
        [_trecho(1, "A", "B", 1), _trecho(2, "B", "C", 1)],
        _instante(1, 9),
        consultar,
    )

    assert len(chamadas) == len(set(chamadas))
