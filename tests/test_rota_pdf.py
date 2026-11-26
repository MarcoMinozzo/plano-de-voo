import re

from tests.conftest import JSON, cadastrar
from tests.conftest_rota import preparar_rota
from servidor.modelos import Aeronave, PlanoDeVoo, Sessao
from tests.conftest_rota import semear_perfis_sinteticos_teste
from servidor.pdf_layout import _estilos
from servidor.pdf_plano import _conteudo_relatorio


def _pedido(aeronave_id):
    return {
        "aeronave_id": aeronave_id,
        "origem": "S0A1",
        "destino": "S0C3",
        "hora_partida": "2026-12-01T12:00:00+00:00",
        "numero_passageiros": 1,
        "peso_pessoas_kg": 80,
        "peso_bagagem_kg": 5,
    }


def test_html_e_pdf_trazem_trecho_reabastecimento_e_aviso(cliente):
    cadastrar(cliente)
    ids = preparar_rota()
    criado = cliente.post("/planos", json=_pedido(ids["alfa"]), headers=JSON)
    assert criado.status_code == 201
    plano_id = criado.get_json()["id"]
    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)
    assert "S0B2" in html
    assert "reabastec" in html.lower()
    assert "Não é autorização de voo." in html
    assert "0.539" not in html
    pdf = cliente.get(f"/planos/{plano_id}/pdf").data
    assert b"S0B2" in pdf
    assert b"reabastec" in pdf or "reabastec".encode("utf-16-be") in pdf
    assert b"autoriza" in pdf or "autoriza".encode("utf-16-be") in pdf


def test_pdf_de_plano_de_outro_piloto_e_recusado(cliente):
    cadastrar(cliente)
    ids = preparar_rota()
    criado = cliente.post("/planos", json=_pedido(ids["alfa"]), headers=JSON)
    plano_id = criado.get_json()["id"]
    outro_piloto = cliente.application.test_client()
    cadastrar(outro_piloto, identificacao="bia")

    resposta = outro_piloto.get(f"/planos/{plano_id}/pdf", headers=JSON)

    assert resposta.status_code == 404
    assert resposta.get_json()["mensagem"] == "Acesso recusado."
    assert not resposta.data.startswith(b"%PDF")


def test_capa_pdf_identifica_piloto_rota_data_e_emblema(cliente):
    cadastrar(cliente, nome_exibicao="Marina Costa")
    alterado = cliente.post(
        "/perfil",
        json={"nome_exibicao": "Marina Atualizada"},
        headers=JSON,
    )
    assert alterado.status_code == 200
    ids = preparar_rota()
    criado = cliente.post("/planos", json=_pedido(ids["alfa"]), headers=JSON)
    plano_id = criado.get_json()["id"]

    resposta = cliente.get(f"/planos/{plano_id}/pdf")
    pdf = resposta.data

    assert resposta.status_code == 200
    assert resposta.mimetype == "application/pdf"
    assert b"Marina Atualizada" in pdf
    assert b"Marina Costa" not in pdf
    assert b"S0A1" in pdf
    assert b"S0B2" in pdf
    assert b"S0C3" in pdf
    assert b"01/12/2026" in pdf
    assert b"12:00 UTC" in pdf
    assert b"/Subtype /Image" in pdf
    assert b"[x]" not in pdf
    assert b"[ ]" not in pdf
    assert len(re.findall(rb"/Type\s*/Page\b", pdf)) >= 2


def test_perfil_sintetico_preserva_rotulo_no_resultado_e_no_pdf(cliente):
    cadastrar(cliente)
    preparar_rota()
    db = Sessao()
    try:
        ids = semear_perfis_sinteticos_teste(db)
    finally:
        Sessao.remove()

    aeronave_id = ids["CESSNA AIRCRAFT 152"]
    criado = cliente.post("/planos", json=_pedido(aeronave_id), headers=JSON)
    assert criado.status_code == 201
    plano_id = criado.get_json()["id"]

    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)
    pdf = cliente.get(f"/planos/{plano_id}/pdf").data
    db = Sessao()
    try:
        plano = db.query(PlanoDeVoo).filter_by(id=plano_id).one()
        procedencia = plano.resultado["procedencia"]["velocidade_cruzeiro"]
        assert plano.resultado["proxy_sintetico"] is True
        assert plano.resultado["modelo_alvo"] == "CESSNA AIRCRAFT 152"
        assert procedencia["dados_sinteticos"] is True
        assert procedencia["unidade"] == "kt"
        assert procedencia["valor"] == 100
        conteudo = _conteudo_relatorio(plano, _estilos())
    finally:
        Sessao.remove()

    assert "Estado: aceitável para planejamento" not in html
    assert "perfil sintético didático — valores não validados" not in html
    assert "Alvo do exercício:" not in html
    assert "Em cada escala, a hipótese é reabastecer" not in html
    assert "<h2>Fontes técnicas da aeronave</h2>" not in html
    assert "Aeronave: CESSNA AIRCRAFT 152." in html
    assert "Não é autorização de voo." in html
    assert "CESSNA AIRCRAFT 152" in html
    assert "faixa de teste" not in html
    assert "DEMO" not in html
    assert b"Dados sint" in pdf
    assert b"DEMO" not in pdf
    assert b"valores n" in pdf
    assert conteudo[-1].getPlainText() == (
        "Cálculos e dados dos perfis sintéticos são exclusivamente didáticos: "
        "valores não validados, que não representam dados do modelo associado. "
        "Não substituem o manual da aeronave, o treinamento de voo nem a norma "
        "vigente; não são adequados para planejamento de voo real e não autorizam "
        "o voo."
    )
