from datetime import datetime, timedelta, timezone

from servidor.auth import MENSAGEM_NOME_EXIBICAO, MENSAGEM_RECUSA
from tests.conftest import JSON, cadastrar
from servidor.modelos import Piloto, Sessao


def test_senha_curta_nao_cria(cliente):
    resposta = cliente.post(
        "/cadastro",
        json={"identificacao": "ana", "senha": "curta"},
        headers=JSON,
    )
    assert resposta.status_code == 400
    assert "8" in resposta.get_json()["mensagem"]


def test_cadastro_exige_nome_de_exibicao(cliente):
    resposta = cliente.post(
        "/cadastro",
        json={"identificacao": "ana", "senha": "segredo12"},
        headers=JSON,
    )

    assert resposta.status_code == 400
    assert "nome" in resposta.get_json()["mensagem"].lower()


def test_cadastro_apara_nome_de_exibicao(cliente):
    resposta = cliente.post(
        "/cadastro",
        json={
            "identificacao": "ana",
            "senha": "segredo12",
            "nome_exibicao": "  Ana Silva  ",
        },
        headers=JSON,
    )

    assert resposta.status_code == 200
    perfil = cliente.get("/perfil")
    assert "Ana Silva" in perfil.get_data(as_text=True)
    assert "  Ana Silva  " not in perfil.get_data(as_text=True)


def test_cadastro_html_cria_sessao_e_abre_painel(cliente):
    resposta = cliente.post(
        "/cadastro",
        data={
            "identificacao": "ana",
            "senha": "segredo12",
            "nome_exibicao": "Ana Silva",
        },
        follow_redirects=True,
    )

    assert resposta.status_code == 200
    assert "Seus planos" in resposta.get_data(as_text=True)


def test_cadastro_recusa_nome_vazio_ou_acima_do_limite(cliente):
    for nome in ("   ", "A" * 161):
        resposta = cliente.post(
            "/cadastro",
            json={
                "identificacao": "ana",
                "senha": "segredo12",
                "nome_exibicao": nome,
            },
            headers=JSON,
        )
        assert resposta.status_code == 400


def test_edicao_de_perfil_altera_somente_o_piloto_autenticado(cliente):
    cadastrar(cliente, nome_exibicao="Ana Silva")
    with Sessao() as db:
        ana_id = db.query(Piloto).filter_by(identificacao="ana").one().id
    outro = cliente.application.test_client()
    cadastrar(outro, identificacao="bia", nome_exibicao="Bia Santos")

    resposta = outro.post(
        "/perfil",
        json={"nome_exibicao": "Bia Nova", "piloto_id": ana_id},
        headers=JSON,
    )

    assert resposta.status_code == 200
    assert resposta.get_json() == {"ok": True, "nome_exibicao": "Bia Nova"}
    with Sessao() as db:
        assert db.get(Piloto, ana_id).nome_exibicao == "Ana Silva"


def test_edicao_de_perfil_recusa_nome_invalido_sem_alterar_valor(cliente):
    cadastrar(cliente, nome_exibicao="Ana Silva")

    resposta = cliente.post(
        "/perfil",
        json={"nome_exibicao": " " * 161},
        headers=JSON,
    )

    assert resposta.status_code == 400
    assert "160" in resposta.get_json()["mensagem"]
    perfil = cliente.get("/perfil").get_data(as_text=True)
    assert "Ana Silva" in perfil


def test_edicao_html_de_perfil_salva_nome_e_redireciona(cliente):
    cadastrar(cliente, nome_exibicao="Ana Silva")

    resposta = cliente.post(
        "/perfil",
        data={"nome_exibicao": "Ana Pilota"},
        follow_redirects=True,
    )

    html = resposta.get_data(as_text=True)
    assert resposta.status_code == 200
    assert "Seus planos" in html
    assert "Ana Pilota" in html
    assert "Ana Silva" not in html
    assert "Nome de exibição salvo." in html


def test_edicao_html_invalida_nao_confirma_sucesso(cliente):
    cadastrar(cliente, nome_exibicao="Ana Silva")

    resposta = cliente.post(
        "/perfil",
        data={"nome_exibicao": " "},
    )

    html = resposta.get_data(as_text=True)
    assert resposta.status_code == 400
    assert MENSAGEM_NOME_EXIBICAO in html
    assert "Nome de exibição salvo." not in html
    assert "Ana Silva" in html


def test_alterar_senha_exige_senha_atual_e_confirmacao_igual(cliente):
    cadastrar(cliente)

    curta = cliente.post(
        "/perfil",
        data={
            "acao": "senha",
            "senha_atual": "segredo12",
            "senha_nova": "curta",
            "senha_confirmacao": "curta",
        },
    )
    assert curta.status_code == 400
    assert "8 caracteres" in curta.get_data(as_text=True)

    diferente = cliente.post(
        "/perfil",
        data={
            "acao": "senha",
            "senha_atual": "segredo12",
            "senha_nova": "segredo99",
            "senha_confirmacao": "segredo98",
        },
    )
    assert diferente.status_code == 400
    assert "mesma senha" in diferente.get_data(as_text=True)

    atual = cliente.post(
        "/perfil",
        json={
            "acao": "senha",
            "senha_atual": "errada12",
            "senha_nova": "segredo99",
            "senha_confirmacao": "segredo99",
        },
        headers=JSON,
    )
    assert atual.status_code == 400
    assert "senha atual" in atual.get_json()["mensagem"]

    igual = cliente.post(
        "/perfil",
        json={
            "senha_nova": "segredo12",
            "senha_confirmacao": "segredo12",
            "senha_atual": "segredo12",
        },
        headers=JSON,
    )
    assert igual.status_code == 400

    salva = cliente.post(
        "/perfil",
        data={
            "acao": "senha",
            "senha_atual": "segredo12",
            "senha_nova": "segredo99",
            "senha_confirmacao": "segredo99",
        },
        follow_redirects=True,
    )
    html = salva.get_data(as_text=True)
    assert salva.status_code == 200
    assert "Seus planos" in html
    assert "Senha alterada." in html
    assert "segredo99" not in html

    cliente.post("/sair")
    recusa = cliente.post(
        "/entrar",
        data={"identificacao": "ana", "senha": "segredo12"},
    )
    assert recusa.status_code == 401
    entra = cliente.post(
        "/entrar",
        data={"identificacao": "ana", "senha": "segredo99"},
    )
    assert entra.status_code == 302


def test_entrar_html_autentica_e_abre_painel(cliente):
    cadastrar(cliente)
    cliente.post("/sair", headers=JSON)

    resposta = cliente.post(
        "/entrar",
        data={"identificacao": "ana", "senha": "segredo12"},
        follow_redirects=True,
    )

    assert resposta.status_code == 200
    assert "Seus planos" in resposta.get_data(as_text=True)


def test_perfil_exige_sessao(cliente):
    assert cliente.get("/perfil", headers=JSON).status_code == 401
    assert cliente.post(
        "/perfil",
        json={"nome_exibicao": "Ana"},
        headers=JSON,
    ).status_code == 401


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


def test_sair_html_encerra_sessao_e_redireciona(cliente):
    cadastrar(cliente)

    resposta = cliente.post("/sair", data={}, follow_redirects=True)

    assert resposta.status_code == 200
    assert "<title>Entrar</title>" in resposta.get_data(as_text=True)
    assert cliente.get("/painel", headers=JSON).status_code == 401


def test_oito_horas_sem_uso(cliente):
    cadastrar(cliente)
    with cliente.session_transaction() as sessao:
        sessao["visto_em"] = (datetime.now(timezone.utc) - timedelta(hours=9)).isoformat()
    resposta = cliente.get("/painel", headers=JSON)
    assert resposta.status_code == 401
