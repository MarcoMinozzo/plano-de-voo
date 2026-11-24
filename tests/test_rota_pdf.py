from tests.conftest import JSON, cadastrar
from tests.conftest_rota import preparar_rota


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
