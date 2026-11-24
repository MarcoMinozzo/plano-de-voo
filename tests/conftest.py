import os
from datetime import datetime, timedelta, timezone
from pathlib import Path


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
                    return valor
    raise RuntimeError("Defina DATABASE_URL_TESTE no ambiente. O valor não fica no repositório.")


os.environ["DATABASE_URL"] = _url_teste()
os.environ["SECRET_KEY"] = "teste-sessao"
os.environ["COOKIE_SECURE"] = "0"
os.environ["PLANO_CONSULTAR_SOL"] = "0"

import pytest

from app import criar_app
from servidor.modelos import Aerodromo, Base, EmendaRotaer, Sessao, agora, configurar
from servidor.semente import semear

JSON = {"Accept": "application/json"}


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
    Sessao.remove()
    with aplicacao.test_client() as c:
        yield c
    Sessao.remove()


def cadastrar(cliente, identificacao="ana", senha="segredo12"):
    resposta = cliente.post(
        "/cadastro",
        json={"identificacao": identificacao, "senha": senha},
        headers=JSON,
    )
    assert resposta.status_code == 200
    return resposta


def plano_valido(**extra):
    dados = {
        "aeronave_id": 1,
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
