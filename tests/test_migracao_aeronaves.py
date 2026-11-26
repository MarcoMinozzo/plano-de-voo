import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, text


def test_migracao_invalida_fontes_nao_oficiais_sem_apagar_valores():
    caminho = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "715f2c8a9e31_invalidar_fonte_nao_oficial_aeronave.py"
    )
    spec = importlib.util.spec_from_file_location("migracao_aeronave", caminho)
    assert spec is not None
    assert spec.loader is not None
    migracao = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migracao)

    engine = create_engine("sqlite://")
    with engine.begin() as conexao:
        conexao.execute(
            text(
                """
                CREATE TABLE aeronave (
                    nome TEXT PRIMARY KEY,
                    manual_estado TEXT NOT NULL,
                    fonte_manual TEXT,
                    combustivel_valor FLOAT
                )
                """
            )
        )
        conexao.execute(
            text(
                """
                INSERT INTO aeronave (nome, manual_estado, fonte_manual, combustivel_valor)
                VALUES
                    ('Modelo Alpha', 'gravado', 'Números de estudo', 22),
                    ('Modelo Beta', 'gravado', NULL, 18),
                    ('Modelo Gamma', 'gravado', 'POH oficial, variante e edição', 30)
                """
            )
        )
        contexto = MigrationContext.configure(conexao)
        with Operations.context(contexto):
            migracao.upgrade()
        registros = conexao.execute(
            text(
                "SELECT nome, manual_estado, fonte_manual, combustivel_valor "
                "FROM aeronave ORDER BY nome"
            )
        ).all()

    assert registros == [
        ("Modelo Alpha", "ausente", "Números de estudo", 22.0),
        ("Modelo Beta", "ausente", None, 18.0),
        ("Modelo Gamma", "gravado", "POH oficial, variante e edição", 30.0),
    ]


def test_migracao_adiciona_metadados_sinteticos_sem_alterar_fontes_existentes():
    caminho = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "d1e2f3a4b5c6_procedencia_intervalos_sinteticos.py"
    )
    spec = importlib.util.spec_from_file_location("migracao_intervalos", caminho)
    assert spec is not None
    assert spec.loader is not None
    migracao = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migracao)

    engine = create_engine("sqlite://")
    with engine.begin() as conexao:
        conexao.execute(
            text(
                """
                CREATE TABLE fonte_tecnica_aeronave (
                    id INTEGER PRIMARY KEY,
                    tipo_fonte TEXT NOT NULL,
                    valor FLOAT NOT NULL,
                    referencia TEXT NOT NULL
                )
                """
            )
        )
        conexao.execute(
            text(
                """
                INSERT INTO fonte_tecnica_aeronave (id, tipo_fonte, valor, referencia)
                VALUES (1, 'oficial', 900, 'POH oficial')
                """
            )
        )
        contexto = MigrationContext.configure(conexao)
        with Operations.context(contexto):
            migracao.upgrade()
        registro = conexao.execute(
            text(
                "SELECT valor, referencia, limite_inferior, limite_superior, "
                "metodo_geracao, versao_semente, incerteza, "
                "justificativa_comparabilidade "
                "FROM fonte_tecnica_aeronave WHERE id = 1"
            )
        ).one()
        colunas = {
            linha[1]
            for linha in conexao.execute(text("PRAGMA table_info(fonte_tecnica_aeronave)"))
        }

    assert registro[:2] == (900.0, "POH oficial")
    assert registro[2:] == (None, None, None, None, None, None)
    assert {
        "limite_inferior",
        "limite_superior",
        "metodo_geracao",
        "versao_semente",
        "incerteza",
        "justificativa_comparabilidade",
    } <= colunas
