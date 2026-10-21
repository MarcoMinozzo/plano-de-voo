from datetime import datetime, timedelta, timezone

from servidor.auth import MENSAGEM_RECUSA
from tests.conftest import JSON, cadastrar


def test_senha_curta_nao_cria(cliente):
    resposta = cliente.post(
        "/cadastro",
        json={"identificacao": "ana", "senha": "curta"},
        headers=JSON,
    )
    assert resposta.status_code == 400
    assert "8" in resposta.get_json()["mensagem"]


def test_mensagem_unica_e_bloqueio(cliente):
    cadastrar(cliente)
    cliente.post("/sair", headers=JSON)
    desconhecida = cliente.post(
        "/entrar",
        json={"identificacao": "ninguem", "senha": "segredo12"},
        headers=JSON,
    )
    assert desconhecida.status_code == 401
    mensagem = desconhecida.get_json()["mensagem"]
    assert mensagem == MENSAGEM_RECUSA
    for _ in range(5):
        errada = cliente.post(
            "/entrar",
            json={"identificacao": "ana", "senha": "erradaaa"},
            headers=JSON,
        )
        assert errada.get_json()["mensagem"] == mensagem
    certa = cliente.post(
        "/entrar",
        json={"identificacao": "ana", "senha": "segredo12"},
        headers=JSON,
    )
    assert certa.status_code == 401
    assert certa.get_json()["mensagem"] == mensagem


def test_sair_encerra_sessao(cliente):
    cadastrar(cliente)
    cliente.post("/sair", headers=JSON)
    resposta = cliente.get("/painel", headers=JSON)
    assert resposta.status_code == 401


def test_oito_horas_sem_uso(cliente):
    cadastrar(cliente)
    with cliente.session_transaction() as sessao:
        sessao["visto_em"] = (datetime.now(timezone.utc) - timedelta(hours=9)).isoformat()
    resposta = cliente.get("/painel", headers=JSON)
    assert resposta.status_code == 401
