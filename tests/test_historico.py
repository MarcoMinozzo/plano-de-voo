from tests.conftest import JSON, cadastrar, plano_valido


def test_editar_recalcula_e_apagar_pede_confirmacao(cliente):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]
    lista = cliente.get("/painel", headers=JSON).get_json()
    assert lista[0]["origem"] == "SBJD"
    assert lista[0]["destino"] == "SBAU"
    editado = cliente.put(
        f"/planos/{plano_id}",
        json=plano_valido(destino="SBBU", hora_partida="2026-12-02T15:00:00+00:00"),
        headers=JSON,
    )
    assert editado.status_code == 200
    assert editado.get_json()["destino"] == "SBBU"
    assert editado.get_json()["atualizado_em"] >= criado.get_json()["atualizado_em"]
    sem = cliente.delete(f"/planos/{plano_id}", json={"confirmar": False}, headers=JSON)
    assert sem.status_code == 400
    ainda = cliente.get(f"/planos/{plano_id}", headers=JSON)
    assert ainda.status_code == 200
    com = cliente.delete(f"/planos/{plano_id}", json={"confirmar": True}, headers=JSON)
    assert com.status_code == 200
    sumiu = cliente.get(f"/planos/{plano_id}", headers=JSON)
    assert sumiu.status_code == 404
