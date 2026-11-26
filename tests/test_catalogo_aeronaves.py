from servidor.catalogo import carregar_rab, selecionar_fonte_aplicavel
from servidor.modelos import Aeronave, FonteTecnicaAeronave, Sessao
from servidor.catalogo import selecionar_fonte_aplicavel
from datetime import datetime, timezone
from tests.conftest import JSON, cadastrar, plano_valido
from tests.conftest_rota import (
    REGISTROS,
    _preencher_manual as preencher_manual_rota,
    preparar_rota,
)


def _preencher_manual(aeronave):
    preencher_manual_rota(
        aeronave,
        "POH fictício, variante X, edição 1, páginas 1–2",
        (500, 900, 20, 1.2, 12, 100, 10),
    )


def test_ordem_pela_frota_e_exclui_aviao_grande(cliente):
    cadastrar(cliente)
    db = Sessao()
    try:
        cessna = db.query(Aeronave).filter_by(nome="Cessna 140").one()
        consumo_cessna = cessna.consumo_valor
        assert cessna.manual_estado == "ausente"
        assert carregar_rab(db, registros=list(REGISTROS), referencia="extrato-teste") == "disponivel"
        assert db.query(Aeronave).filter_by(nome="Grande Jato").count() == 0
        for nome in ("Avião Alfa", "Avião Beta"):
            _preencher_manual(db.query(Aeronave).filter_by(nome=nome).one())
        db.commit()
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
    assert nomes == ["Avião Alfa", "Avião Beta"]
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


def test_oferece_apenas_trinta_modelos_completos_e_desempata_por_nome(cliente):
    cadastrar(cliente)
    registros = [
        {
            "nome": f"Modelo {indice:02d}",
            "pmd_kg": 900,
            "categoria": "aviao",
            "frota": 100,
        }
        for indice in range(34)
    ]
    registros.append(
        {
            "nome": "Incompleto Primeira",
            "pmd_kg": 900,
            "categoria": "aviao",
            "frota": 1000,
        }
    )
    db = Sessao()
    try:
        assert carregar_rab(db, registros=registros, referencia="extrato-teste") == "disponivel"
        modelos = db.query(Aeronave).filter(Aeronave.extrato_id.isnot(None)).all()
        for aeronave in modelos:
            if aeronave.nome.startswith("Modelo "):
                _preencher_manual(aeronave)
            if aeronave.nome == "Modelo 31":
                aeronave.fonte_manual = None
            elif aeronave.nome == "Modelo 32":
                aeronave.bagagem_max_kg = None
            elif aeronave.nome == "Modelo 33":
                aeronave.velocidade_unidade = None
        db.commit()
    finally:
        Sessao.remove()

    resposta = cliente.get("/aeronaves", headers=JSON).get_json()

    assert resposta["estado"] == "disponivel"
    assert [item["nome"] for item in resposta["modelos"]] == [
        f"Modelo {indice:02d}" for indice in range(30)
    ]


def test_carregar_rab_nao_associa_manual_sem_nome_exato(cliente):
    cadastrar(cliente)
    db = Sessao()
    try:
        manual_existente = Aeronave(
            nome="Fabricante Modelo X",
            frota=0,
            manual_estado="gravado",
            fonte_manual="POH fictício da variante Fabricante Modelo X",
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
        db.add(manual_existente)
        db.commit()

        assert carregar_rab(
            db,
            registros=[
                {
                    "nome": "Modelo X",
                    "fabricante": "Fabricante",
                    "pmd_kg": 900,
                    "categoria": "aviao",
                    "frota": 1,
                }
            ],
            referencia="extrato-teste",
        ) == "disponivel"

        modelo_rab = db.query(Aeronave).filter_by(nome="Modelo X").one()
        db.refresh(manual_existente)
        assert modelo_rab.manual_estado == "ausente"
        assert modelo_rab.fonte_manual is None
        assert modelo_rab.consumo_valor is None
        assert manual_existente.extrato_id is None
        assert manual_existente.manual_estado == "gravado"
    finally:
        Sessao.remove()


def test_carregar_rab_preserva_valores_de_registro_inelegivel(cliente):
    cadastrar(cliente)
    db = Sessao()
    try:
        legado = Aeronave(
            nome="Modelo Legado",
            frota=0,
            manual_estado="ausente",
            fonte_manual="Fonte antiga não verificada",
            peso_vazio_kg=410,
            peso_max_decolagem_kg=700,
            bagagem_max_kg=25,
            braco_bagagem_m=1.5,
            combustivel_valor=22,
            combustivel_unidade="gal",
            velocidade_valor=91,
            velocidade_unidade="kt",
            consumo_valor=5,
            consumo_unidade="gal/h",
            itens_manutencao=[],
        )
        db.add(legado)
        db.commit()
        valores_anteriores = (
            legado.fonte_manual,
            legado.peso_vazio_kg,
            legado.peso_max_decolagem_kg,
            legado.bagagem_max_kg,
            legado.combustivel_valor,
            legado.velocidade_valor,
            legado.consumo_valor,
        )

        assert carregar_rab(
            db,
            registros=[
                {
                    "nome": "Modelo Legado",
                    "pmd_kg": 910,
                    "categoria": "aviao",
                    "frota": 3,
                }
            ],
            referencia="extrato-teste",
        ) == "disponivel"
        db.refresh(legado)

        assert legado.manual_estado == "ausente"
        assert legado.extrato_id is not None
        assert (
            legado.fonte_manual,
            legado.peso_vazio_kg,
            legado.peso_max_decolagem_kg,
            legado.bagagem_max_kg,
            legado.combustivel_valor,
            legado.velocidade_valor,
            legado.consumo_valor,
        ) == valores_anteriores
    finally:
        Sessao.remove()


def test_rab_indisponivel_nao_oferece_modelos_locais(cliente, monkeypatch, tmp_path):
    cadastrar(cliente)
    monkeypatch.setenv("RAB_EXTRATO", str(tmp_path / "extrato-inexistente.csv"))
    db = Sessao()
    try:
        assert carregar_rab(db) == "indisponivel"
        modelo_local = Aeronave(
            nome="Modelo Local",
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
        db.add(modelo_local)
        db.commit()
    finally:
        Sessao.remove()

    resposta = cliente.get("/aeronaves", headers=JSON).get_json()

    assert resposta["estado"] == "indisponivel"
    assert resposta["modelos"] == []
    assert "lista local" in resposta["observacao"]


def test_fonte_mais_recente_e_empate_sem_selecao(cliente):
    cadastrar(cliente)
    db = Sessao()
    try:
        antiga = datetime(2024, 1, 1, tzinfo=timezone.utc)
        recente = datetime(2025, 1, 1, tzinfo=timezone.utc)
        consulta = datetime(2026, 1, 1, tzinfo=timezone.utc)
        aeronave = Aeronave(
            nome="Modelo Procedência",
            frota=1,
            manual_estado="gravado",
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
        db.add(aeronave)
        db.flush()
        db.add_all(
            [
                FonteTecnicaAeronave(
                    aeronave_id=aeronave.id,
                    campo="combustivel_utilizavel",
                    valor=10,
                    unidade="gal",
                    tipo_fonte="secundaria",
                    publicador="Publicador antigo",
                    referencia="Ref antiga",
                    data_publicacao=antiga,
                    data_consulta=consulta,
                    modelo_variante=aeronave.nome,
                ),
                FonteTecnicaAeronave(
                    aeronave_id=aeronave.id,
                    campo="combustivel_utilizavel",
                    valor=12,
                    unidade="gal",
                    tipo_fonte="secundaria",
                    publicador="Publicador novo",
                    referencia="Ref nova",
                    data_publicacao=recente,
                    data_consulta=consulta,
                    modelo_variante=aeronave.nome,
                ),
            ]
        )
        db.commit()

        escolhida = selecionar_fonte_aplicavel(
            db, aeronave, "combustivel_utilizavel"
        )
        assert escolhida.publicador == "Publicador novo"
        assert escolhida.divergencia is not None

        db.query(FonteTecnicaAeronave).filter_by(
            aeronave_id=aeronave.id,
            campo="combustivel_utilizavel",
        ).delete(synchronize_session=False)
        db.add_all(
            [
                FonteTecnicaAeronave(
                    aeronave_id=aeronave.id,
                    campo="combustivel_utilizavel",
                    valor=10,
                    unidade="gal",
                    tipo_fonte="secundaria",
                    publicador="A",
                    referencia="A",
                    data_publicacao=recente,
                    data_consulta=consulta,
                    modelo_variante=aeronave.nome,
                ),
                FonteTecnicaAeronave(
                    aeronave_id=aeronave.id,
                    campo="combustivel_utilizavel",
                    valor=11,
                    unidade="gal",
                    tipo_fonte="secundaria",
                    publicador="B",
                    referencia="B",
                    data_publicacao=recente,
                    data_consulta=consulta,
                    modelo_variante=aeronave.nome,
                ),
            ]
        )
        db.commit()
        assert selecionar_fonte_aplicavel(
            db, aeronave, "combustivel_utilizavel"
        ) is None
    finally:
        Sessao.remove()
