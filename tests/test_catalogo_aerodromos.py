from servidor.catalogo import carregar_rotaer
from servidor.modelos import Aerodromo, Sessao
from tests.conftest import JSON, cadastrar
from tests.conftest_rota import preparar_rota, xml_emenda


def _db():
    return Sessao()


def test_lista_so_aerodromo_e_rejeita_heliponto(cliente):
    cadastrar(cliente)
    db = _db()
    try:
        assert carregar_rotaer(db, corpo=xml_emenda()) == "disponivel"
    finally:
        Sessao.remove()
    corpo = cliente.get("/aerodromos", headers=JSON).get_json()
    identificadores = [item["identificador"] for item in corpo["aerodromos"]]
    assert corpo["estado"] == "disponivel"
    assert "S0A1" in identificadores
    assert "S0B2" in identificadores
    assert "S0C3" in identificadores
    assert "H0H1" not in identificadores
    for item in corpo["aerodromos"]:
        assert "lat" not in item
        assert item["fonte"]
    ids = preparar_rota()
    recusa = cliente.post(
        "/planos",
        json={
            "aeronave_id": ids["alfa"],
            "origem": "H0H1",
            "destino": "S0A1",
            "hora_partida": "2026-12-01T12:00:00+00:00",
            "numero_passageiros": 1,
            "peso_pessoas_kg": 80,
            "peso_bagagem_kg": 5,
        },
        headers=JSON,
    )
    assert recusa.status_code == 400
    assert "aeródromo de avião" in recusa.get_json()["mensagem"]
    assert cliente.get("/painel", headers=JSON).get_json() == []


def test_emenda_ausente_nao_cria_coordenada(cliente, monkeypatch):
    cadastrar(cliente)
    db = _db()
    try:
        antes = {aero.icao for aero in db.query(Aerodromo).all()}
        corpo = """
        <aisweb>
          <rotaer>
            <AeroCode>S9Z9</AeroCode><name>Novo</name><type>AD</type>
            <lat>2</lat><lng>3</lng><altM>8</altM>
          </rotaer>
        </aisweb>
        """
        assert carregar_rotaer(db, corpo=corpo) == "indisponivel"
        assert db.get(Aerodromo, "S9Z9") is None
        monkeypatch.setenv("AISWEB_API_KEY", "")
        monkeypatch.setenv("AISWEB_API_PASS", "")
        assert carregar_rotaer(db, corpo="") == "indisponivel"
        assert {aero.icao for aero in db.query(Aerodromo).all()} == antes
    finally:
        Sessao.remove()
    resposta = cliente.get("/aerodromos", headers=JSON).get_json()
    assert resposta["estado"] == "indisponivel"
    assert resposta["aerodromos"] == []
