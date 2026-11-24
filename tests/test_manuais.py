import json

import pytest

from servidor.catalogo import carregar_rab
from servidor.manuais import carregar_manuais
from servidor.modelos import Aeronave, Sessao


def grandeza(valor, unidade, pagina="1-1"):
    return {"valor": valor, "unidade": unidade, "pagina": pagina}


def manual_ficticio(**extra):
    dados = {
        "modelo_rab": "Fictício F1",
        "fabricante": "Fábrica de Teste",
        "experimental": False,
        "documento": {
            "titulo": "Manual de Teste",
            "numero": "MT-01",
            "revisao": "rev. 0",
            "copia_publica": "https://exemplo.invalido/manual.pdf",
        },
        "peso_vazio": grandeza(500, "kg", "6-2"),
        "peso_max_decolagem": grandeza(800, "kg", "2-3"),
        "bagagem_max": grandeza(40, "kg", "2-4"),
        "braco_bagagem": grandeza(2.0, "m", "6-5"),
        "combustivel_utilizavel": grandeza(30, "gal", "2-6"),
        "massa_por_galao": grandeza(2.72, "kg/gal", "6-1"),
        "cruzeiro": {
            "condicao": "75% de potência, 4.000 ft, atmosfera padrão",
            "velocidade": grandeza(100, "kt", "5-9"),
            "consumo": grandeza(6, "gal/h", "5-9"),
        },
        "itens_checklist": [{"texto": "Comandos livres", "pagina": "4-3"}],
    }
    dados.update(extra)
    return dados


def gravar_arquivos(pasta, *manuais):
    for indice, dados in enumerate(manuais):
        (pasta / f"m{indice}.json").write_text(json.dumps(dados), encoding="utf-8")
    return pasta


@pytest.fixture
def db(cliente):
    sessao = Sessao()
    yield sessao
    Sessao.remove()


def test_arquivo_valido_grava_manual_com_documento_e_pagina(db, tmp_path):
    gravados, recusados = carregar_manuais(db, gravar_arquivos(tmp_path, manual_ficticio()))
    assert recusados == []
    assert gravados == ["Fictício F1"]
    modelo = db.query(Aeronave).filter_by(nome="Fictício F1").one()
    assert modelo.manual_estado == "gravado"
    assert modelo.peso_vazio_kg == 500
    assert modelo.velocidade_unidade == "kt"
    assert modelo.consumo_unidade == "gal/h"
    assert modelo.combustivel_unidade == "gal"
    assert modelo.combustivel_kg_por_gal == pytest.approx(2.72)
    for trecho in ("Manual de Teste", "MT-01", "p. 6-2", "p. 5-9", "75% de potência", "https://exemplo.invalido"):
        assert trecho in modelo.fonte_manual
    assert modelo.itens_manutencao[0]["texto"] == "Comandos livres"
    assert "p. 4-3" in modelo.itens_manutencao[0]["fonte"]


def test_unidades_do_manual_viram_as_do_calculo(db, tmp_path):
    manual = manual_ficticio(
        peso_vazio=grandeza(1000, "lb"),
        peso_max_decolagem=grandeza(1600, "lb"),
        bagagem_max=grandeza(100, "lb"),
        braco_bagagem=grandeza(80, "in"),
        combustivel_utilizavel=grandeza(100, "L"),
        massa_por_galao=grandeza(6.7, "lb/gal"),
        cruzeiro={
            "condicao": "cruzeiro recomendado, 10.000 ft",
            "velocidade": grandeza(150, "mph"),
            "consumo": grandeza(67, "lb/h"),
        },
    )
    carregar_manuais(db, gravar_arquivos(tmp_path, manual))
    modelo = db.query(Aeronave).filter_by(nome="Fictício F1").one()
    assert modelo.peso_vazio_kg == pytest.approx(453.59, abs=0.01)
    assert modelo.peso_max_decolagem_kg == pytest.approx(725.75, abs=0.01)
    assert modelo.braco_bagagem_m == pytest.approx(2.032, abs=0.001)
    assert modelo.combustivel_valor == pytest.approx(26.42, abs=0.01)
    assert modelo.combustivel_kg_por_gal == pytest.approx(3.039, abs=0.001)
    assert modelo.velocidade_valor == pytest.approx(130.35, abs=0.01)
    assert modelo.consumo_valor == pytest.approx(10.0, abs=0.01)


@pytest.mark.parametrize(
    ("mudanca", "campo"),
    [
        ({"peso_vazio": {"valor": 500, "unidade": "kg"}}, "peso_vazio.pagina"),
        ({"bagagem_max": grandeza(40, "arroba")}, "bagagem_max.unidade"),
        ({"combustivel_utilizavel": grandeza(0, "gal")}, "combustivel_utilizavel.valor"),
        ({"experimental": True}, "experimental"),
        ({"peso_max_decolagem": grandeza(6000, "kg")}, "peso_max_decolagem"),
        ({"peso_vazio": grandeza(800, "kg")}, "peso_vazio"),
        ({"documento": {"titulo": "Manual de Teste"}}, "documento.numero"),
        ({"modelo_rab": "Cessna 140"}, "modelo_rab"),
    ],
)
def test_arquivo_invalido_e_recusado_pelo_campo(db, tmp_path, mudanca, campo):
    nome = mudanca.get("modelo_rab", "Fictício F1")
    gravados, recusados = carregar_manuais(db, gravar_arquivos(tmp_path, manual_ficticio(**mudanca)))
    assert gravados == []
    assert recusados == [("m0.json", campo)]
    if nome != "Cessna 140":
        assert db.query(Aeronave).filter_by(nome=nome).count() == 0


def test_recusa_nao_impede_os_outros_arquivos(db, tmp_path):
    ruim = manual_ficticio(modelo_rab="Fictício F2", experimental=True)
    gravados, recusados = carregar_manuais(db, gravar_arquivos(tmp_path, manual_ficticio(), ruim))
    assert gravados == ["Fictício F1"]
    assert recusados == [("m1.json", "experimental")]


def test_carga_repetida_da_o_mesmo_banco_e_preserva_o_cessna(db, tmp_path):
    cessna = db.query(Aeronave).filter_by(nome="Cessna 140").one()
    antes = (cessna.fonte_manual, cessna.consumo_valor, cessna.peso_vazio_kg)
    pasta = gravar_arquivos(tmp_path, manual_ficticio())
    carregar_manuais(db, pasta)
    carregar_manuais(db, pasta)
    assert db.query(Aeronave).filter_by(nome="Fictício F1").count() == 1
    db.refresh(cessna)
    assert (cessna.fonte_manual, cessna.consumo_valor, cessna.peso_vazio_kg) == antes
    assert cessna.combustivel_kg_por_gal is None


def test_carga_do_rab_depois_mantem_o_manual(db, tmp_path):
    carregar_manuais(db, gravar_arquivos(tmp_path, manual_ficticio()))
    registros = [
        {"nome": "FICTÍCIO F1", "pmd_kg": 790, "categoria": "aviao", "fabricante": "FABRICA DE TESTE", "frota": 12},
    ]
    assert carregar_rab(db, registros=registros, referencia="extrato-teste") == "disponivel"
    modelos = db.query(Aeronave).filter(Aeronave.nome.ilike("fictício f1")).all()
    assert len(modelos) == 1
    assert modelos[0].manual_estado == "gravado"
    assert modelos[0].frota == 12
    assert modelos[0].peso_max_decolagem_kg == 800
