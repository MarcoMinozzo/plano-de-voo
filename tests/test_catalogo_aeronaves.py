from servidor.catalogo import carregar_rab
from servidor.modelos import Aeronave, Sessao
from tests.conftest import JSON, cadastrar, plano_valido
from tests.conftest_rota import REGISTROS, preparar_rota


def test_ordem_pela_frota_e_exclui_aviao_grande(cliente):
    cadastrar(cliente)
    db = Sessao()
    try:
        cessna = db.query(Aeronave).filter_by(nome="Cessna 140").one()
        consumo_cessna = cessna.consumo_valor
        assert carregar_rab(db, registros=list(REGISTROS), referencia="extrato-teste") == "disponivel"
        assert db.query(Aeronave).filter_by(nome="Grande Jato").count() == 0
        sem = db.query(Aeronave).filter_by(nome="Modelo Sem Manual").one()
        assert sem.consumo_valor is None
        assert sem.velocidade_valor is None
        assert sem.manual_estado == "ausente"
        db.refresh(cessna)
        assert cessna.consumo_valor == consumo_cessna
    finally:
        Sessao.remove()
    corpo = cliente.get("/aeronaves", headers=JSON).get_json()
    assert corpo["estado"] == "disponivel"
    nomes = [item["nome"] for item in corpo["modelos"]]
    assert nomes == ["Avião Alfa", "Avião Beta", "Modelo Sem Manual"]
    frotas = [item["frota"] for item in corpo["modelos"]]
    assert frotas == sorted(frotas, reverse=True)
    for item in corpo["modelos"]:
        assert "peso_max_decolagem_kg" not in item
        assert "velocidade_valor" not in item
        assert "consumo_valor" not in item
    assert "registro inteiro" not in corpo


def test_recusa_modelo_sem_manual(cliente):
    cadastrar(cliente)
    ids = preparar_rota()
    resposta = cliente.post(
        "/planos",
        json=plano_valido(
            aeronave_id=ids["sem_manual"],
            origem="S0A1",
            destino="S0B2",
        ),
        headers=JSON,
    )
    assert resposta.status_code == 400
    assert "Modelo Sem Manual" in resposta.get_json()["mensagem"]
    assert cliente.get("/painel", headers=JSON).get_json() == []
