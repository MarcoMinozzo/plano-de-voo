from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
import os
import runpy

import pytest

import app
from servidor.ambiente import resolver_ambiente


URL_PRODUTO = "postgresql+psycopg://piloto:senha@localhost/plano"
URL_LEGADA = "postgresql+psycopg://piloto:senha@localhost/plano_demo"


def test_ambiente_ignora_variaveis_legadas_de_demo():
    ambiente = resolver_ambiente(
        {
            "DATABASE_URL": URL_PRODUTO,
            "APP_ENV": "development",
            "DEMO_MODE": "1",
            "DATABASE_URL_DEMO": URL_LEGADA,
        }
    )

    assert ambiente.database_url == URL_PRODUTO
    assert not hasattr(ambiente, "demo")


@pytest.mark.parametrize(
    "valor",
    [
        "",
        "url-invalida",
        "sqlite:///plano.db",
        "postgresql+psycopg://piloto:senha@localhost/",
    ],
)
def test_ambiente_recusa_url_de_produto_ausente_ou_invalida(valor):
    with pytest.raises(RuntimeError):
        resolver_ambiente({"DATABASE_URL": valor})


def test_criar_app_valida_url_antes_de_configurar_banco(monkeypatch):
    monkeypatch.setattr(app, "carregar_env", lambda: None)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setattr(
        app,
        "configurar",
        lambda _url: pytest.fail("A URL deve ser validada antes da configuração do banco."),
    )

    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        app.criar_app()


def test_criar_app_usa_database_url_com_variaveis_legadas_presentes(monkeypatch):
    monkeypatch.setattr(app, "carregar_env", lambda: None)
    monkeypatch.setenv("DATABASE_URL", URL_PRODUTO)
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DEMO_MODE", "1")
    monkeypatch.setenv("DATABASE_URL_DEMO", URL_LEGADA)
    urls = []
    monkeypatch.setattr(app, "configurar", urls.append)

    aplicacao = app.criar_app()

    assert urls == [URL_PRODUTO]
    assert "DEMO_MODE" not in aplicacao.config


def test_alembic_usa_database_url_com_variaveis_legadas_presentes(monkeypatch):
    from alembic import context

    monkeypatch.setenv("DATABASE_URL", URL_PRODUTO)
    monkeypatch.setenv("APP_ENV", "development")
    monkeypatch.setenv("DEMO_MODE", "1")
    monkeypatch.setenv("DATABASE_URL_DEMO", URL_LEGADA)
    configuracoes = []
    monkeypatch.setattr(
        context,
        "config",
        SimpleNamespace(config_file_name=None),
        raising=False,
    )
    monkeypatch.setattr(context, "is_offline_mode", lambda: True)
    monkeypatch.setattr(
        context,
        "configure",
        lambda **kwargs: configuracoes.append(kwargs),
    )
    monkeypatch.setattr(context, "begin_transaction", nullcontext)
    monkeypatch.setattr(context, "run_migrations", lambda: None)
    raiz = Path(__file__).resolve().parents[1]

    runpy.run_path(str(raiz / "alembic" / "env.py"))

    assert configuracoes[0]["url"] == URL_PRODUTO


def test_conftest_aponta_banco_de_sessao_para_database_url_teste():
    assert os.environ["DATABASE_URL"] == os.environ["DATABASE_URL_TESTE"]
