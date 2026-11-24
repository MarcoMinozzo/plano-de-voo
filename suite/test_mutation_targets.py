from types import SimpleNamespace

from servidor.calculo import calcular, distancia_km, distancia_nm, proa_graus


def _aeronave():
    return SimpleNamespace(
        velocidade_valor=100.0, consumo_valor=8.0, peso_vazio_kg=400.0,
        peso_max_decolagem_kg=700.0, bagagem_max_kg=20.0, combustivel_valor=30.0,
        combustivel_unidade="gal", velocidade_unidade="kt", consumo_unidade="gal/h",
        fonte_manual="manual",
    )


def _pontos():
    return (
        SimpleNamespace(lat=0.0, lon=0.0, icao="AAAA", fonte="carta"),
        SimpleNamespace(lat=0.0, lon=1.0, icao="BBBB", fonte="carta"),
    )


def _carga():
    return {"numero_passageiros": 1, "peso_pessoas_kg": 70, "peso_bagagem_kg": 0}


def test_distance_and_heading_use_the_sphere():
    assert distancia_km(0, 0, 0, 1) == 111.19492664455873
    assert distancia_km(0, 0, 0, 0) == 0
    assert distancia_nm(0, 0, 0, 1) == 60.040479006216
    assert proa_graus(0, 0, 0, 1) == 90
    assert proa_graus(0, 0, 1, 0) == 0
    assert proa_graus(0, 0, 0, -1) == 270


def test_plan_names_a_missing_field_and_refuses_a_headwind_above_cruise():
    origem, destino = _pontos()
    incompleta = _aeronave()
    incompleta.consumo_valor = None
    assert calcular(incompleta, origem, destino, _carga())["erro"] == "consumo_valor"
    sem_velocidade = _aeronave()
    sem_velocidade.velocidade_valor = None
    assert calcular(sem_velocidade, origem, destino, _carga())["erro"] == "velocidade_valor"
    recusado = calcular(_aeronave(), origem, destino, _carga(), {"estado": "disponivel", "direcao_de_graus": 90, "velocidade_kt": 120, "fonte": "metar"})
    assert recusado["erro"] == "vento de proa maior que a velocidade de planejamento"
    plano = calcular(_aeronave(), origem, destino, _carga(), {"estado": "disponivel", "direcao_de_graus": 270, "velocidade_kt": 10, "fonte": "metar"})
    assert plano["grava"] is True
    assert plano["aceitavel"] is True
    assert plano["vento_estado"] == "disponivel"
    assert "cauda" in plano["efeito_vento"]
    sem_vento = calcular(_aeronave(), origem, destino, _carga())
    assert sem_vento["vento_estado"] == "indisponivel"
    assert sem_vento["efeito_vento"] == "vento não aplicado"
    pesada = _carga()
    pesada["peso_bagagem_kg"] = 40
    pesada["peso_pessoas_kg"] = 400
    alerta = calcular(_aeronave(), origem, destino, pesada)
    assert any(item.startswith("Bagagem") for item in alerta["alertas"])
    assert any(item.startswith("Peso") for item in alerta["alertas"])
    assert alerta["aceitavel"] is False
    curta = _aeronave()
    curta.combustivel_valor = 1
    sem_reserva = calcular(curta, origem, destino, _carga())
    assert any(item.startswith("Combustível") for item in sem_reserva["alertas"])
    assert sem_reserva["cabe_reserva"] is False
