from types import SimpleNamespace

from servidor.calculo import calcular
from tests.conftest import JSON, cadastrar, plano_valido


def aeronave_minima(**extra):
    dados = dict(
        fonte_manual="manual de teste",
        velocidade_valor=91.0,
        velocidade_unidade="kt",
        consumo_valor=5.0,
        consumo_unidade="gal/h",
        combustivel_valor=22.0,
        combustivel_unidade="gal",
        peso_vazio_kg=404.0,
        peso_max_decolagem_kg=658.0,
        bagagem_max_kg=36.0,
    )
    dados.update(extra)
    return SimpleNamespace(**dados)


def aerodromo(icao, lat, lon):
    return SimpleNamespace(icao=icao, lat=lat, lon=lon, fonte="fonte de teste")


def test_grandeza_tem_unidade_e_fonte():
    conta = calcular(
        aeronave_minima(),
        aerodromo("SBJD", -23.18, -46.94),
        aerodromo("SBAU", -21.14, -50.42),
        {
            "peso_pessoas_kg": 80,
            "peso_bagagem_kg": 5,
        },
    )
    assert conta["grava"] is True
    for linha in conta["linhas"]:
        assert linha["unidade"]
        assert linha["fonte"]


def test_peso_acima_de_658_inaceitavel(cliente):
    cadastrar(cliente)
    resposta = cliente.post(
        "/planos",
        json=plano_valido(peso_pessoas_kg=500),
        headers=JSON,
    )
    corpo = resposta.get_json()
    assert resposta.status_code == 201
    assert corpo["estado"] == "inaceitavel"
    assert any("658" in alerta for alerta in corpo["resultado"]["alertas"])


def test_origem_igual_destino_nao_grava(cliente):
    cadastrar(cliente)
    resposta = cliente.post("/planos", json=plano_valido(destino="SBJD"), headers=JSON)
    assert resposta.status_code == 400
    lista = cliente.get("/painel", headers=JSON)
    assert lista.get_json() == []


def test_manual_incompleto_nao_grava():
    conta = calcular(
        aeronave_minima(velocidade_valor=None),
        aerodromo("SBJD", -23.18, -46.94),
        aerodromo("SBAU", -21.14, -50.42),
        {
            "peso_pessoas_kg": 80,
            "peso_bagagem_kg": 5,
        },
    )
    assert conta["grava"] is False
    assert conta["erro"] == "velocidade_valor"


def test_sem_vento_nao_publica_velocidade_de_solo():
    conta = calcular(
        aeronave_minima(),
        aerodromo("SBJD", -23.18, -46.94),
        aerodromo("SBAU", -21.14, -50.42),
        {
            "peso_pessoas_kg": 80,
            "peso_bagagem_kg": 5,
        },
    )
    assert all(linha["nome"] != "Velocidade em relação ao solo" for linha in conta["linhas"])


def test_vento_disponivel_publica_a_fonte_do_produto():
    conta = calcular(
        aeronave_minima(),
        aerodromo("SBJD", -23.18, -46.94),
        aerodromo("SBAU", -21.14, -50.42),
        {
            "peso_pessoas_kg": 80,
            "peso_bagagem_kg": 5,
        },
        {"estado": "disponivel", "direcao_de_graus": 90, "velocidade_kt": 20, "fonte": "REDEMET área SBCW"},
    )
    solo = next(linha for linha in conta["linhas"] if linha["nome"] == "Velocidade em relação ao solo")
    assert solo["fonte"] == "REDEMET área SBCW"
    assert solo["unidade"] == "kt"


def _peso_combustivel(conta):
    return next(linha for linha in conta["linhas"] if linha["nome"] == "Peso de combustível")


def test_peso_do_combustivel_usa_a_massa_por_galao_do_manual():
    origem, destino = aerodromo("SBJD", -23.18, -46.94), aerodromo("SBAU", -21.14, -50.42)
    particulares = {"peso_pessoas_kg": 80, "peso_bagagem_kg": 5}
    querosene = _peso_combustivel(calcular(aeronave_minima(combustivel_kg_por_gal=3.0), origem, destino, particulares))
    assert querosene["valor"] == 66.0
    assert querosene["fonte"] == "manual de teste"
    avgas = _peso_combustivel(calcular(aeronave_minima(), origem, destino, particulares))
    assert avgas["valor"] == round(22.0 * 2.72, 1)
    assert "2,72 kg/gal" in avgas["fonte"]
