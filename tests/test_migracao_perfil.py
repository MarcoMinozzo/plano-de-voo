import importlib.util
from pathlib import Path

from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, text


def test_migracao_preenche_nome_de_exibicao_sem_alterar_credenciais():
    caminho = (
        Path(__file__).resolve().parents[1]
        / "alembic"
        / "versions"
        / "a4f3c8d1926e_nome_exibicao_piloto.py"
    )
    spec = importlib.util.spec_from_file_location("migracao_nome_piloto", caminho)
    assert spec is not None
    assert spec.loader is not None
    migracao = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(migracao)

    engine = create_engine("sqlite://")
    with engine.begin() as conexao:
        conexao.execute(
            text(
                """
                CREATE TABLE piloto (
                    id INTEGER PRIMARY KEY,
                    identificacao VARCHAR(80) NOT NULL,
                    senha_hash VARCHAR(255) NOT NULL,
                    criado_em DATETIME NOT NULL
                )
                """
            )
        )
        conexao.execute(
            text(
                """
                INSERT INTO piloto (id, identificacao, senha_hash, criado_em)
                VALUES (1, 'ana@example.test', 'hash-ana', '2026-01-01'),
                       (2, 'bia', 'hash-bia', '2026-01-02')
                """
            )
        )
        contexto = MigrationContext.configure(conexao)
        with Operations.context(contexto):
            migracao.upgrade()
        registros = conexao.execute(
            text(
                "SELECT identificacao, senha_hash, nome_exibicao "
                "FROM piloto ORDER BY id"
            )
        ).all()
        coluna_nome = next(
            coluna
            for coluna in conexao.execute(text("PRAGMA table_info(piloto)"))
            if coluna[1] == "nome_exibicao"
        )

    assert registros == [
        ("ana@example.test", "hash-ana", "ana@example.test"),
        ("bia", "hash-bia", "bia"),
    ]
    assert coluna_nome[3] == 1
