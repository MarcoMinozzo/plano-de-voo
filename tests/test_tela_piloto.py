import json
import re
import subprocess

from servidor.modelos import Aerodromo, EmendaRotaer, PlanoDeVoo, Sessao
from tests.conftest import JSON, cadastrar, plano_valido


def test_recusa_devolve_os_valores_e_nao_pede_hora_futura(cliente):
    cadastrar(cliente)
    dados = plano_valido(destino="SBJD", peso_pessoas_kg=80)
    resposta = cliente.post("/planos", data=dados)
    assert resposta.status_code == 400
    html = resposta.get_data(as_text=True)
    assert "Origem e destino precisam ser diferentes." in html
    assert 'value="SBJD"' in html
    assert 'value="80"' in html or 'value="80.0"' in html
    assert 'id="confirma-hora" hidden' in html
    assert '<select name="origem"' in html
    assert '<select name="aeronave_id"' in html
    assert "Não é autorização de voo." in html


def test_hora_passada_mostra_o_pedido(cliente):
    cadastrar(cliente)
    dados = plano_valido(hora_partida="2020-01-01T12:00")
    resposta = cliente.post("/planos", data=dados)
    assert resposta.status_code == 400
    html = resposta.get_data(as_text=True)
    assert "Hora de partida no passado" in html
    assert 'name="confirmar_hora"' in html
    assert 'id="confirma-hora" hidden' not in html
    assert 'value="2020-01-01T12:00"' in html


def test_busca_de_aerodromo_nao_devolve_a_lista_inteira(cliente):
    cadastrar(cliente)
    curto = cliente.get("/aerodromos?q=j", headers=JSON).get_json()
    assert curto["aerodromos"] == []
    achados = cliente.get("/aerodromos?q=JD", headers=JSON).get_json()
    identificadores = [item["identificador"] for item in achados["aerodromos"]]
    assert "SBJD" in identificadores
    assert "SBAU" not in identificadores
    pagina = cliente.get("/planos/novo").get_data(as_text=True)
    assert '<select name="origem"' in pagina
    assert '<select name="destino"' in pagina
    assert "SBJD —" in pagina
    assert "Cessna 140" in pagina
    assert 'size="' not in pagina
    assert "data-filtra" not in pagina
    assert "Não é autorização de voo." in pagina
    assert "Número de passageiros" in pagina
    assert "Peso das pessoas" in pagina
    assert "combustivel_a_bordo" not in pagina
    assert "peso_piloto" not in pagina


def test_filtro_casa_codigo_ou_nome_sem_acento(cliente):
    cadastrar(cliente)
    db = Sessao()
    try:
        emenda = db.query(EmendaRotaer).filter_by(vigente=True).one()
        for indice in range(8):
            db.add(
                Aerodromo(
                    icao=f"ZZ0{indice}",
                    nome=f"Pista {indice}",
                    tipo="aerodromo",
                    lat=0,
                    lon=0,
                    elev_m=1,
                    emenda_id=emenda.id,
                    fonte="teste",
                )
            )
        db.add(
            Aerodromo(
                icao="ZZSJ",
                nome="São José Teste",
                tipo="aerodromo",
                lat=0,
                lon=0,
                elev_m=1,
                emenda_id=emenda.id,
                fonte="teste",
            )
        )
        db.commit()
    finally:
        Sessao.remove()
    pagina = cliente.get("/planos/novo").get_data(as_text=True)
    assert 'data-filtra="origem"' in pagina
    assert 'data-filtra="destino"' in pagina
    assert "ZZSJ — São José Teste" in pagina
    trecho = re.search(r"function planoCasa\(texto, codigo, nome\) \{.*?\n\}", pagina, re.S)
    assert trecho
    saida = subprocess.run(
        [
            "node",
            "-e",
            trecho.group(0)
            + """
const r = {
  codigo: planoCasa("zzsj", "ZZSJ", "São José Teste"),
  nome: planoCasa("sao jose", "ZZSJ", "São José Teste"),
  maiuscula: planoCasa("SÃO", "ZZSJ", "São José Teste"),
  cidade: planoCasa("campinas", "ZZSJ", "São José Teste"),
  vazio: planoCasa("  ", "ZZSJ", "São José Teste")
};
console.log(JSON.stringify(r));
""",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(saida.stdout) == {
        "codigo": True,
        "nome": True,
        "maiuscula": True,
        "cidade": False,
        "vazio": True,
    }


def test_painel_diz_aceitavel_para_planejamento(cliente):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    assert criado.status_code == 201
    html = cliente.get("/painel").get_data(as_text=True)
    assert "aceitável para planejamento" in html
    assert ">calculado<" not in html


def test_alterar_recalcula_o_mesmo_plano_e_recusa_nao_substitui(cliente):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]
    formulario = cliente.get(f"/planos/{plano_id}/alterar").get_data(as_text=True)
    assert 'value="SBJD"' in formulario
    assert 'value="SBAU"' in formulario
    recusa = cliente.post(f"/planos/{plano_id}/alterar", data=plano_valido(destino="SBJD"))
    assert recusa.status_code == 400
    intacto = cliente.get(f"/planos/{plano_id}", headers=JSON).get_json()
    assert intacto["destino"] == "SBAU"
    editado = cliente.post(f"/planos/{plano_id}/alterar", data=plano_valido(peso_pessoas_kg=90))
    assert editado.status_code == 302
    corpo = cliente.get(f"/planos/{plano_id}", headers=JSON).get_json()
    assert corpo["id"] == plano_id
    assert corpo["dados_particulares"]["peso_pessoas_kg"] == 90
    outro = cliente.application.test_client()
    cadastrar(outro, "bia")
    alheio = outro.get(f"/planos/{plano_id}/alterar")
    assert alheio.status_code == 404
    assert "SBJD" not in alheio.get_data(as_text=True)


def test_tabela_vazia_nao_aparece_e_mapa_avisa_a_carta(cliente):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]
    db = Sessao()
    try:
        plano = db.get(PlanoDeVoo, plano_id)
        plano.resultado = {"aceitavel": True, "alertas": [], "linhas": [], "efeito_vento": ""}
        db.commit()
    finally:
        Sessao.remove()
    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)
    assert "<th>Grandeza</th>" not in html
    assert "<h2>Trechos</h2>" in html
    assert html.index("não substitui a carta de voo visual") < html.index('id="mapa"')
    assert (
        "Tempo, vento, carta de voo visual e radar: indisponível." in html
        or ("Indisponível:" in html and "carta de voo visual" in html)
    )
    assert "Como ler este plano" in html


def test_checklist_volta_ao_item(cliente):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]
    item_id = criado.get_json()["checklist"][1]["id"]
    resposta = cliente.post(f"/planos/{plano_id}/checklist/{item_id}", data={"marcado": "true"})
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith(f"#item-{item_id}")
    html = cliente.get(resposta.headers["Location"].split("#")[0]).get_data(as_text=True)
    assert f'id="item-{item_id}"' in html
    assert "marcado" in html
    assert "não marcado" not in html
