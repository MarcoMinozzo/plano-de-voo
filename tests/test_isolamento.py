from servidor.auth import MENSAGEM_RECUSA
from tests.conftest import JSON, cadastrar, plano_valido


def test_piloto_nao_ve_plano_alheio(cliente):
    cadastrar(cliente, "ana")
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    assert criado.status_code == 201
    plano_id = criado.get_json()["id"]
    outro = cliente.application.test_client()
    cadastrar(outro, "bia")
    for metodo, url, kwargs in (
        ("get", f"/planos/{plano_id}", {}),
        ("put", f"/planos/{plano_id}", {"json": plano_valido(destino="SBBU")}),
        ("delete", f"/planos/{plano_id}", {"json": {"confirmar": True}}),
    ):
        resposta = getattr(outro, metodo)(url, headers=JSON, **kwargs)
        assert resposta.status_code == 404
        assert resposta.get_json()["mensagem"] == MENSAGEM_RECUSA
    lista = outro.get("/painel", headers=JSON)
    assert lista.get_json() == []
    ainda = cliente.get(f"/planos/{plano_id}", headers=JSON)
    assert ainda.status_code == 200
