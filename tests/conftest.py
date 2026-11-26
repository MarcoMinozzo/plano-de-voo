import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


def _identidade_banco(valor):
    try:
        url = make_url(valor)
    except ArgumentError:
        raise RuntimeError("Uma URL de banco usada nos testes é inválida.") from None
    if url.get_backend_name() != "postgresql" or not url.database:
        raise RuntimeError("Os bancos de teste e produto precisam ser PostgreSQL.")
    return (
        url.get_backend_name(),
        (url.host or "").casefold(),
        url.port or 5432,
        url.database,
    )


def _url_teste():
    valor = os.environ.get("DATABASE_URL_TESTE", "").strip()
    if valor:
        return valor
    env = Path(__file__).resolve().parents[1] / ".env"
    if env.exists():
        for linha in env.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if linha.startswith("DATABASE_URL_TESTE="):
                valor = linha.split("=", 1)[1].strip().strip('"').strip("'")
                if valor:
                    break
        if valor:
            return valor
    raise RuntimeError("Defina DATABASE_URL_TESTE no ambiente. O valor não fica no repositório.")


URL_PRODUTO_ORIGINAL = os.environ.get("DATABASE_URL", "").strip()
URL_TESTE = _url_teste()
IDENTIDADE_BANCO_TESTE = _identidade_banco(URL_TESTE)
if URL_PRODUTO_ORIGINAL and _identidade_banco(URL_PRODUTO_ORIGINAL) == IDENTIDADE_BANCO_TESTE:
    raise RuntimeError("DATABASE_URL_TESTE não pode apontar para o banco de produto.")
os.environ["DATABASE_URL_TESTE"] = URL_TESTE
os.environ["DATABASE_URL"] = URL_TESTE
os.environ["SECRET_KEY"] = "teste-sessao"
os.environ["COOKIE_SECURE"] = "0"
os.environ["PLANO_CONSULTAR_SOL"] = "0"

import pytest

from app import criar_app
from servidor.catalogo import carregar_rab
from servidor.modelos import Aerodromo, Aeronave, Base, EmendaRotaer, Sessao, agora, configurar
from servidor.semente import semear
from tests.conftest_rota import _preencher_manual

JSON = {"Accept": "application/json"}
if __name__ == "conftest":
    sys.modules.setdefault("tests.conftest", sys.modules[__name__])


@pytest.fixture
def cliente():
    aplicacao = criar_app()
    engine = configurar(os.environ["DATABASE_URL"])
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    db = Sessao()
    semear(db)
    emenda = EmendaRotaer(
        codigo_emenda="semente-teste",
        vigente=True,
        carregada_em=agora(),
        estado="disponivel",
    )
    db.add(emenda)
    db.flush()
    for aero in db.query(Aerodromo).all():
        aero.tipo = "aerodromo"
        aero.emenda_id = emenda.id
    db.commit()
    carregar_rab(
        db,
        registros=[
            {
                "nome": "Modelo Base",
                "pmd_kg": 900,
                "categoria": "aviao",
                "frota": 1,
            }
        ],
        referencia="extrato-ficticio-teste",
    )
    modelo_base = db.query(Aeronave).filter_by(nome="Modelo Base").one()
    _preencher_manual(
        modelo_base,
        "POH fictício de teste, variante X, edição 1",
        (500, 900, 20, 1.2, 100, 100, 10),
    )
    modelo_base.itens_manutencao = [
        {"texto": "Item de teste 1", "fonte": modelo_base.fonte_manual},
        {"texto": "Item de teste 2", "fonte": modelo_base.fonte_manual},
    ]
    db.commit()
    Sessao.remove()
    with aplicacao.test_client() as c:
        yield c
    Sessao.remove()


def cadastrar(
    cliente,
    identificacao="ana",
    senha="segredo12",
    nome_exibicao="Ana Pilota",
):
    resposta = cliente.post(
        "/cadastro",
        json={
            "identificacao": identificacao,
            "senha": senha,
            "nome_exibicao": nome_exibicao,
        },
        headers=JSON,
    )
    assert resposta.status_code == 200
    return resposta


def plano_valido(**extra):
    dados = {
        "aeronave_id": 2,
        "origem": "SBJD",
        "destino": "SBAU",
        "hora_partida": "2026-12-01T12:00:00+00:00",
        "numero_passageiros": 1,
        "peso_pessoas_kg": 80,
        "peso_bagagem_kg": 5,
    }
    dados.update(extra)
    return dados


def futuro():
    return (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
