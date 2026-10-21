from pathlib import Path

from tests.conftest import cadastrar, plano_valido


def test_tela_e_pdf_usam_o_texto_do_piloto(cliente):
    texto = Path("documentacao/piloto.md").read_text(encoding="utf-8")
    cadastrar(cliente)
    criado = cliente.post(
        "/planos",
        json=plano_valido(),
        headers={"Accept": "application/json"},
    )
    plano_id = criado.get_json()["id"]
    pagina = cliente.get(f"/planos/{plano_id}")
    assert "Informe de onde sai" in pagina.get_data(as_text=True)
    assert "não autoriza o voo" in pagina.get_data(as_text=True).lower() or "Não é autorização de voo." in texto
    assert "Não é autorização de voo." in pagina.get_data(as_text=True)
    assert "Item indisponível" in pagina.get_data(as_text=True)
    pdf = cliente.get(f"/planos/{plano_id}/pdf").data
    assert "autoriza".encode("utf-16-be") in pdf or b"autoriza" in pdf
