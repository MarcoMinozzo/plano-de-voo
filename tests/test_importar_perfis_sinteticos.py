import pytest
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    JSON,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    inspect,
    select,
)
from sqlalchemy.orm import sessionmaker

from servidor import importar_perfis_sinteticos as importador
from servidor.importar_perfis_sinteticos import transferir_perfis_sinteticos
from servidor.modelos import (
    Aerodromo,
    Aeronave,
    Base,
    EmendaRotaer,
    ExtratoRab,
    FonteTecnicaAeronave,
    Piloto,
    agora,
)
from servidor.perfis_sinteticos import PERFIS_SINTETICOS


CAMPOS = (
    ("peso_vazio", "peso_vazio_kg", "kg"),
    ("peso_maximo_decolagem", "peso_max_decolagem_kg", "kg"),
    ("bagagem_maxima", "bagagem_max_kg", "kg"),
    ("combustivel_utilizavel", "combustivel_valor", "gal"),
    ("velocidade_cruzeiro", "velocidade_valor", "kt"),
    ("consumo_cruzeiro", "consumo_valor", "gal/h"),
)


def _banco():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine, expire_on_commit=False)()


def _banco_origem_legada():
    engine = create_engine("sqlite://")
    metadata = MetaData()
    aeronave = Table(
        "aeronave",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("nome", String(200), nullable=False),
        Column("frota", Integer, nullable=False),
        Column("manual_estado", String(20), nullable=False),
        Column("extrato_id", Integer),
        Column("fonte_manual", Text),
        Column("peso_vazio_kg", Float),
        Column("peso_max_decolagem_kg", Float),
        Column("bagagem_max_kg", Float),
        Column("braco_bagagem_m", Float),
        Column("combustivel_valor", Float),
        Column("combustivel_unidade", String(20)),
        Column("velocidade_valor", Float),
        Column("velocidade_unidade", String(20)),
        Column("consumo_valor", Float),
        Column("consumo_unidade", String(20)),
        Column("itens_manutencao", JSON, nullable=False),
    )
    fonte = Table(
        "fonte_tecnica_aeronave",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("aeronave_id", Integer, nullable=False),
        Column("campo", String(80), nullable=False),
        Column("valor", Float, nullable=False),
        Column("unidade", String(20), nullable=False),
        Column("tipo_fonte", String(20), nullable=False),
        Column("publicador", String(200), nullable=False),
        Column("referencia", Text, nullable=False),
        Column("data_publicacao", DateTime(timezone=True)),
        Column("data_consulta", DateTime(timezone=True), nullable=False),
        Column("modelo_variante", String(200), nullable=False),
        Column("perfil", String(200)),
        Column("revisao_edicao", String(200)),
        Column("pagina_tabela", String(200)),
        Column("selecionada", Boolean, nullable=False),
        Column("divergencia", Text),
    )
    metadata.create_all(engine)
    return (
        engine,
        aeronave,
        fonte,
        sessionmaker(bind=engine, expire_on_commit=False)(),
    )


def _popular_origem_legada(db, aeronave, fonte):
    momento = agora()
    with db.begin():
        conexao = db.connection()
        for indice, perfil in enumerate(PERFIS_SINTETICOS, 1):
            valores = {
                "peso_vazio": 500 + indice,
                "peso_maximo_decolagem": 1000 + indice,
                "bagagem_maxima": 100 + indice,
                "combustivel_utilizavel": 20 + indice,
                "velocidade_cruzeiro": 100 + indice,
                "consumo_cruzeiro": 10 + indice,
            }
            aeronave_id = indice
            aeronave_values = {
                "id": aeronave_id,
                "nome": f"Aeronave DEMO {indice:02}",
                "frota": 0,
                "manual_estado": "ausente",
                "extrato_id": 77,
                "fonte_manual": "Registro genérico legado",
                "peso_vazio_kg": valores["peso_vazio"],
                "peso_max_decolagem_kg": valores["peso_maximo_decolagem"],
                "bagagem_max_kg": valores["bagagem_maxima"],
                "braco_bagagem_m": None,
                "combustivel_valor": valores["combustivel_utilizavel"],
                "combustivel_unidade": "gal",
                "velocidade_valor": valores["velocidade_cruzeiro"],
                "velocidade_unidade": "kt",
                "consumo_valor": valores["consumo_cruzeiro"],
                "consumo_unidade": "gal/h",
                "itens_manutencao": [],
            }
            conexao.execute(aeronave.insert(), aeronave_values)
            fontes = []
            for deslocamento, (campo, _atributo, unidade) in enumerate(CAMPOS):
                fontes.append(
                    {
                        "id": (indice - 1) * len(CAMPOS) + deslocamento + 1,
                        "aeronave_id": aeronave_id,
                        "campo": campo,
                        "valor": valores[campo],
                        "unidade": unidade,
                        "tipo_fonte": "sintetica",
                        "publicador": "Dados sintéticos legados",
                        "referencia": "Valor genérico de teste",
                        "data_publicacao": None,
                        "data_consulta": momento,
                        "modelo_variante": f"Aeronave DEMO {indice:02}",
                        "perfil": "Cruzeiro legado"
                        if campo in {"velocidade_cruzeiro", "consumo_cruzeiro"}
                        else None,
                        "revisao_edicao": "legado",
                        "pagina_tabela": None,
                        "selecionada": True,
                        "divergencia": None,
                    }
                )
            conexao.execute(fonte.insert(), fontes)


def _snapshot_tabelas(db, *tabelas):
    conexao = db.connection()
    return tuple(
        tuple(
            tuple(linha)
            for linha in conexao.execute(
                select(tabela).order_by(tabela.c.id)
            ).all()
        )
        for tabela in tabelas
    )


def _popular_origem(db, quantidade=20):
    momento = agora()
    extrato = ExtratoRab(
        referencia="Extrato sintético legado",
        carregado_em=momento,
        estado="disponivel",
    )
    db.add(extrato)
    db.flush()

    for indice, perfil in enumerate(PERFIS_SINTETICOS[:quantidade], 1):
        alvo = perfil.alvo_modelo
        valores = {
            "peso_vazio": 500 + indice,
            "peso_maximo_decolagem": 1000 + indice,
            "bagagem_maxima": 100 + indice,
            "combustivel_utilizavel": 20 + indice,
            "velocidade_cruzeiro": 100 + indice,
            "consumo_cruzeiro": 10 + indice,
        }
        aeronave = Aeronave(
            nome=perfil.nome_origem,
            frota=0,
            manual_estado="proxy_sintetico",
            extrato_id=extrato.id,
            fonte_manual=f"Alvo de teste: {alvo}",
            peso_vazio_kg=valores["peso_vazio"],
            peso_max_decolagem_kg=valores["peso_maximo_decolagem"],
            bagagem_max_kg=valores["bagagem_maxima"],
            combustivel_valor=valores["combustivel_utilizavel"],
            combustivel_unidade="gal",
            velocidade_valor=valores["velocidade_cruzeiro"],
            velocidade_unidade="kt",
            consumo_valor=valores["consumo_cruzeiro"],
            consumo_unidade="gal/h",
            itens_manutencao=[],
        )
        db.add(aeronave)
        db.flush()
        for campo, atributo, unidade in CAMPOS:
            db.add(
                FonteTecnicaAeronave(
                    aeronave_id=aeronave.id,
                    campo=campo,
                    valor=valores[campo],
                    unidade=unidade,
                    tipo_fonte="sintetica",
                    publicador="Dado sintético de teste",
                    referencia="Referência de teste",
                    data_publicacao=None,
                    data_consulta=momento,
                    modelo_variante=alvo,
                    perfil="Perfil sintético de teste"
                    if campo in {"velocidade_cruzeiro", "consumo_cruzeiro"}
                    else None,
                    selecionada=True,
                )
            )

    db.add(
        Aeronave(
            nome="Aeronave DEMO 99",
            manual_estado="sintetico_demo",
            extrato_id=extrato.id,
        )
    )
    db.add(
        Piloto(
            identificacao="legado",
            senha_hash="hash-de-teste",
            nome_exibicao="Piloto legado",
            criado_em=momento,
        )
    )
    db.commit()


def _snapshot(db):
    return [
        (
            aeronave.nome,
            aeronave.manual_estado,
            aeronave.peso_vazio_kg,
            aeronave.peso_max_decolagem_kg,
            aeronave.bagagem_max_kg,
            aeronave.combustivel_valor,
            aeronave.combustivel_unidade,
            aeronave.velocidade_valor,
            aeronave.velocidade_unidade,
            aeronave.consumo_valor,
            aeronave.consumo_unidade,
            tuple(
                (fonte.campo, fonte.valor, fonte.unidade)
                for fonte in sorted(aeronave.fontes_tecnicas, key=lambda item: item.campo)
            ),
        )
        for aeronave in db.query(Aeronave).order_by(Aeronave.nome).all()
    ]


def test_importa_vinte_perfis_sem_alterar_origem_ou_catalogos_do_destino():
    engine_origem, origem = _banco()
    engine_destino, destino = _banco()
    try:
        _popular_origem(origem)
        snapshot_origem = _snapshot(origem)
        destino.add(
            ExtratoRab(
                referencia="RAB canônico",
                carregado_em=agora(),
                estado="disponivel",
            )
        )
        destino.add(
            EmendaRotaer(
                codigo_emenda="ROTAER canônico",
                vigente=True,
                carregada_em=agora(),
                estado="disponivel",
            )
        )
        destino.add(
            Aerodromo(
                icao="SBXX",
                nome="Aeródromo canônico",
                tipo="aerodromo",
                lat=-23.0,
                lon=-46.0,
                elev_m=700,
                fonte="ROTAER oficial de teste",
            )
        )
        aeronave_factual = Aeronave(
            nome=PERFIS_SINTETICOS[0].alvo_modelo,
            frota=0,
            manual_estado="ausente",
        )
        destino.add(aeronave_factual)
        destino.commit()

        assert transferir_perfis_sinteticos(origem, destino) == (20, 0)
        assert destino.query(Aeronave).count() == 21
        assert destino.query(FonteTecnicaAeronave).count() == 120
        assert aeronave_factual.manual_estado == "ausente"
        assert (
            destino.query(Aeronave)
            .filter_by(
                nome=PERFIS_SINTETICOS[0].alvo_modelo,
                manual_estado="proxy_sintetico",
            )
            .count()
            == 1
        )
        assert destino.query(ExtratoRab).one().referencia == "RAB canônico"
        assert destino.query(EmendaRotaer).one().codigo_emenda == "ROTAER canônico"
        assert destino.query(Aerodromo).one().icao == "SBXX"
        assert destino.query(Piloto).count() == 0

        for indice, perfil in enumerate(PERFIS_SINTETICOS, 1):
            aeronave = destino.query(Aeronave).filter_by(
                nome=perfil.nome_exibicao,
                manual_estado="proxy_sintetico",
            ).one()
            esperado = {
                "peso_vazio": 500 + indice,
                "peso_maximo_decolagem": 1000 + indice,
                "bagagem_maxima": 100 + indice,
                "combustivel_utilizavel": 20 + indice,
                "velocidade_cruzeiro": 100 + indice,
                "consumo_cruzeiro": 10 + indice,
            }
            for campo, atributo, unidade in CAMPOS:
                assert getattr(aeronave, atributo) == esperado[campo]
                fontes = [
                    fonte
                    for fonte in aeronave.fontes_tecnicas
                    if fonte.campo == campo
                ]
                assert len(fontes) == 1
                assert fontes[0].valor == esperado[campo]
                assert fontes[0].unidade == unidade
                assert fontes[0].aeronave_id == aeronave.id
            assert aeronave.extrato_id is None

        assert _snapshot(origem) == snapshot_origem
    finally:
        origem.close()
        destino.close()
        engine_origem.dispose()
        engine_destino.dispose()


def test_importa_esquema_legado_por_ordem_sem_alterar_origem():
    engine_origem, origem_aeronave, origem_fonte, origem = _banco_origem_legada()
    engine_destino, destino = _banco()
    try:
        _popular_origem_legada(origem, origem_aeronave, origem_fonte)
        snapshot_origem = _snapshot_tabelas(origem, origem_aeronave, origem_fonte)
        colunas_legadas = {
            coluna["name"]
            for coluna in inspect(engine_origem).get_columns(
                "fonte_tecnica_aeronave"
            )
        }
        assert not {
            "limite_inferior",
            "limite_superior",
            "metodo_geracao",
            "versao_semente",
            "incerteza",
            "justificativa_comparabilidade",
        } & colunas_legadas

        assert transferir_perfis_sinteticos(origem, destino) == (20, 0)
        assert destino.query(Aeronave).count() == 20
        assert destino.query(FonteTecnicaAeronave).count() == 120

        for indice, perfil in enumerate(PERFIS_SINTETICOS, 1):
            aeronave = destino.query(Aeronave).filter_by(
                nome=perfil.alvo_modelo
            ).one()
            esperado = {
                "peso_vazio": 500 + indice,
                "peso_maximo_decolagem": 1000 + indice,
                "bagagem_maxima": 100 + indice,
                "combustivel_utilizavel": 20 + indice,
                "velocidade_cruzeiro": 100 + indice,
                "consumo_cruzeiro": 10 + indice,
            }
            assert aeronave.manual_estado == "proxy_sintetico"
            assert aeronave.extrato_id is None
            for campo, atributo, unidade in CAMPOS:
                assert getattr(aeronave, atributo) == esperado[campo]
                fonte = destino.query(FonteTecnicaAeronave).filter_by(
                    aeronave_id=aeronave.id,
                    campo=campo,
                    selecionada=True,
                ).one()
                assert fonte.valor == esperado[campo]
                assert fonte.unidade == unidade

        snapshot_destino = _snapshot(destino)
        destino.rollback()
        assert transferir_perfis_sinteticos(origem, destino) == (0, 20)
        assert _snapshot(destino) == snapshot_destino
        assert _snapshot_tabelas(origem, origem_aeronave, origem_fonte) == snapshot_origem
    finally:
        origem.close()
        destino.close()
        engine_origem.dispose()
        engine_destino.dispose()


def test_fonte_duplicada_no_esquema_legado_aborta_sem_escrever():
    engine_origem, origem_aeronave, origem_fonte, origem = _banco_origem_legada()
    engine_destino, destino = _banco()
    try:
        _popular_origem_legada(origem, origem_aeronave, origem_fonte)
        with origem.begin():
            origem.connection().execute(
                origem_fonte.insert(),
                {
                    "id": 121,
                    "aeronave_id": 1,
                    "campo": "peso_vazio",
                    "valor": 501,
                    "unidade": "kg",
                    "tipo_fonte": "sintetica",
                    "publicador": "Dados sintéticos legados",
                    "referencia": "Valor genérico de teste",
                    "data_publicacao": None,
                    "data_consulta": agora(),
                    "modelo_variante": "Aeronave DEMO 01",
                    "perfil": None,
                    "revisao_edicao": "legado",
                    "pagina_tabela": None,
                    "selecionada": True,
                    "divergencia": None,
                },
            )
        snapshot_origem = _snapshot_tabelas(origem, origem_aeronave, origem_fonte)

        with pytest.raises(RuntimeError, match="Fonte sintética duplicada"):
            transferir_perfis_sinteticos(origem, destino)

        assert destino.query(Aeronave).count() == 0
        assert destino.query(FonteTecnicaAeronave).count() == 0
        assert _snapshot_tabelas(origem, origem_aeronave, origem_fonte) == snapshot_origem
    finally:
        origem.close()
        destino.close()
        engine_origem.dispose()
        engine_destino.dispose()


def test_importacao_repetida_nao_duplica_ou_altera_perfis():
    engine_origem, origem = _banco()
    engine_destino, destino = _banco()
    try:
        _popular_origem(origem)
        assert transferir_perfis_sinteticos(origem, destino) == (20, 0)
        snapshot_destino = _snapshot(destino)
        destino.rollback()

        assert transferir_perfis_sinteticos(origem, destino) == (0, 20)
        assert destino.query(Aeronave).count() == 20
        assert destino.query(FonteTecnicaAeronave).count() == 120
        assert _snapshot(destino) == snapshot_destino
    finally:
        origem.close()
        destino.close()
        engine_origem.dispose()
        engine_destino.dispose()


def test_origem_incompleta_aborta_sem_escrever_no_destino():
    engine_origem, origem = _banco()
    engine_destino, destino = _banco()
    try:
        _popular_origem(origem, quantidade=19)
        snapshot_origem = _snapshot(origem)

        with pytest.raises(RuntimeError, match="20"):
            transferir_perfis_sinteticos(origem, destino)

        assert destino.query(Aeronave).count() == 0
        assert destino.query(FonteTecnicaAeronave).count() == 0
        assert _snapshot(origem) == snapshot_origem
    finally:
        origem.close()
        destino.close()
        engine_origem.dispose()
        engine_destino.dispose()


def test_fonte_tecnica_ausente_aborta_sem_escrever_no_destino():
    engine_origem, origem = _banco()
    engine_destino, destino = _banco()
    try:
        _popular_origem(origem)
        perfil = PERFIS_SINTETICOS[0]
        aeronave = origem.query(Aeronave).filter_by(nome=perfil.nome_origem).one()
        fonte = (
            origem.query(FonteTecnicaAeronave)
            .filter_by(aeronave_id=aeronave.id, campo="consumo_cruzeiro")
            .one()
        )
        origem.delete(fonte)
        origem.commit()

        with pytest.raises(RuntimeError, match="Fontes técnicas ausentes"):
            transferir_perfis_sinteticos(origem, destino)

        assert destino.query(Aeronave).count() == 0
        assert destino.query(FonteTecnicaAeronave).count() == 0
    finally:
        origem.close()
        destino.close()
        engine_origem.dispose()
        engine_destino.dispose()


def test_conflito_divergente_aborta_sem_insercoes_parciais():
    engine_origem, origem = _banco()
    engine_destino, destino = _banco()
    try:
        _popular_origem(origem)
        perfil = PERFIS_SINTETICOS[0]
        conflito = Aeronave(
            nome=perfil.nome_exibicao,
            manual_estado="proxy_sintetico",
            peso_vazio_kg=999,
            peso_max_decolagem_kg=1200,
        )
        destino.add(conflito)
        destino.commit()

        with pytest.raises(RuntimeError, match="Conflito"):
            transferir_perfis_sinteticos(origem, destino)

        assert destino.query(Aeronave).count() == 1
        assert destino.query(FonteTecnicaAeronave).count() == 0
        conflito_atual = destino.query(Aeronave).filter_by(id=conflito.id).one()
        assert conflito_atual.peso_vazio_kg == 999
        assert conflito_atual.peso_max_decolagem_kg == 1200
    finally:
        origem.close()
        destino.close()
        engine_origem.dispose()
        engine_destino.dispose()


def test_comando_recusa_a_mesma_base_antes_de_conectar(monkeypatch):
    url = "postgresql+psycopg://user:password@localhost/plano"
    monkeypatch.setattr(importador, "carregar_env", lambda: None)
    monkeypatch.setattr(importador, "create_engine", lambda _url: pytest.fail("Conexão inesperada"))
    monkeypatch.setenv("DATABASE_URL_DEMO_ORIGEM", url)
    monkeypatch.setenv("DATABASE_URL", url)

    with pytest.raises(RuntimeError, match="bases PostgreSQL distintas"):
        importador.main()
