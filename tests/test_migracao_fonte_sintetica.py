import importlib.util
from pathlib import Path

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text


def _migracao():
    caminho = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "c8d3f41a2b67_adicionar_fonte_sintetica.py"
    )
    spec = importlib.util.spec_from_file_location("fonte_sintetica", caminho)
    assert spec is not None
    assert spec.loader is not None
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def test_migracao_permita_sintetica_sem_data_editorial():
    engine = create_engine("sqlite://")
    with engine.begin() as conexao:
        conexao.execute(
            text(
                """
                CREATE TABLE fonte_tecnica_aeronave (
                    id INTEGER PRIMARY KEY,
                    tipo_fonte VARCHAR(20) NOT NULL,
                    data_publicacao DATETIME NOT NULL,
                    CONSTRAINT ck_fonte_tecnica_tipo
                    CHECK (tipo_fonte in ('oficial', 'secundaria'))
                )
                """
            )
        )
        conexao.execute(
            text(
                "INSERT INTO fonte_tecnica_aeronave "
                "(id, tipo_fonte, data_publicacao) VALUES (1, 'oficial', '2024-01-01')"
            )
        )
        contexto = MigrationContext.configure(conexao)
        with Operations.context(contexto):
            _migracao().upgrade()

        conexao.execute(
            text(
                "INSERT INTO fonte_tecnica_aeronave "
                "(id, tipo_fonte, data_publicacao) VALUES (2, 'sintetica', NULL)"
            )
        )
        colunas = inspect(conexao).get_columns("fonte_tecnica_aeronave")

    assert next(c for c in colunas if c["name"] == "data_publicacao")["nullable"] is True


def test_migracao_nao_permite_reverter_com_dados_sinteticos():
    engine = create_engine("sqlite://")
    with engine.begin() as conexao:
        conexao.execute(
            text(
                """
                CREATE TABLE fonte_tecnica_aeronave (
                    id INTEGER PRIMARY KEY,
                    tipo_fonte VARCHAR(20) NOT NULL,
                    data_publicacao DATETIME NULL,
                    CONSTRAINT ck_fonte_tecnica_tipo
                    CHECK (tipo_fonte in ('oficial', 'secundaria', 'sintetica'))
                )
                """
            )
        )
        conexao.execute(
            text(
                "INSERT INTO fonte_tecnica_aeronave "
                "(id, tipo_fonte, data_publicacao) VALUES (1, 'sintetica', NULL)"
            )
        )
        contexto = MigrationContext.configure(conexao)
        with Operations.context(contexto), pytest.raises(RuntimeError, match="sintéticas"):
            _migracao().downgrade()
