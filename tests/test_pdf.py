from tests.conftest import JSON, cadastrar, plano_valido


def test_checklist_e_pdf(cliente):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano = criado.get_json()
    assert plano["checklist"]
    assert all(item["fonte"] for item in plano["checklist"])
    item = plano["checklist"][0]
    marcado = cliente.post(
        f"/planos/{plano['id']}/checklist/{item['id']}",
        json={"marcado": True},
        headers=JSON,
    )
    assert marcado.get_json()["marcado"] is True
    pdf = cliente.get(f"/planos/{plano['id']}/pdf")
    assert pdf.mimetype == "application/pdf"
    assert pdf.data.startswith(b"%PDF")
    assert "autoriza".encode("utf-16-be") in pdf.data or b"autoriza" in pdf.data
