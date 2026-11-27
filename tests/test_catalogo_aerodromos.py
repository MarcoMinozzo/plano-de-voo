from datetime import date, datetime, timezone
from types import SimpleNamespace
import time

import pytest

from servidor.catalogo import _baixar_rotaer, carregar_rotaer, sol_aerodromo
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


def test_download_rotaer_usa_endpoint_aisweb_confirmado(monkeypatch):
    monkeypatch.setenv("AISWEB_API_KEY", "teste")
    monkeypatch.setenv("AISWEB_API_PASS", "teste")
    chamadas = []

    def getter(url, params=None, timeout=None):
        chamadas.append((url, params, timeout))
        return SimpleNamespace(
            text=xml_emenda(),
            raise_for_status=lambda: None,
        )

    codigo, registros = _baixar_rotaer(getter=getter)

    assert chamadas[0][0] == "https://api.decea.mil.br/aisweb/"
    assert chamadas[0][1]["area"] == "rotaer"
    assert chamadas[0][1]["apiKey"] == "teste"
    assert chamadas[0][1]["apiPass"] == "teste"
    assert chamadas[0][2] == 30
    assert codigo
    assert registros


def test_nascer_e_por_do_sol_usa_endpoint_aisweb_confirmado(monkeypatch):
    monkeypatch.setenv("AISWEB_API_KEY", "teste")
    monkeypatch.setenv("AISWEB_API_PASS", "teste")
    monkeypatch.setenv("PLANO_CONSULTAR_SOL", "1")
    chamadas = []

    def getter(url, params=None, timeout=None):
        chamadas.append((url, params, timeout))
        return SimpleNamespace(
            text=(
                "<aisweb><day><date>2026-12-01</date><aero>SBJD</aero>"
                "<sunrise>09:30</sunrise><sunset>22:30</sunset></day></aisweb>"
            ),
            raise_for_status=lambda: None,
        )

    resultado = sol_aerodromo(
        "SBJD",
        datetime(2026, 12, 1, 12, tzinfo=timezone.utc),
        getter=getter,
    )

    assert resultado["estado"] == "disponivel"
    assert resultado["fonte"] == "AISWEB sol"
    assert resultado["nascer_do_sol"] == datetime(
        2026, 12, 1, 9, 30, tzinfo=timezone.utc
    )
    assert resultado["por_do_sol"] == datetime(
        2026, 12, 1, 22, 30, tzinfo=timezone.utc
    )
    assert chamadas[0][0] == "https://api.decea.mil.br/aisweb/"
    assert chamadas[0][1]["area"] == "sol"
    assert chamadas[0][1]["icaoCode"] == "SBJD"
    assert chamadas[0][1]["dt_i"] == "2026-12-01"
    assert chamadas[0][1]["dt_f"] == "2026-12-01"
    assert chamadas[0][1]["apiKey"] == "teste"
    assert chamadas[0][1]["apiPass"] == "teste"
    assert chamadas[0][2] == 8


@pytest.mark.parametrize(
    "xml",
    (
        "<aisweb><sunset>2026-12-01T22:30:00+00:00</sunset></aisweb>",
        "<aisweb><sunrise>2026-12-01T09:30:00+00:00</sunrise></aisweb>",
        (
            "<aisweb><sunrise>horário inválido</sunrise>"
            "<sunset>2026-12-01T22:30:00+00:00</sunset></aisweb>"
        ),
        (
            "<aisweb><sunrise>2026-12-01T09:30:00</sunrise>"
            "<sunset>2026-12-01T22:30:00+00:00</sunset></aisweb>"
        ),
        (
            "<aisweb><sunrise>2026-12-01T09:30:00+01:00</sunrise>"
            "<sunset>2026-12-01T22:30:00+00:00</sunset></aisweb>"
        ),
    ),
)
def test_sol_aisweb_incompleto_ou_fora_de_utc_fica_indisponivel(
    monkeypatch, xml
):
    monkeypatch.setenv("AISWEB_API_KEY", "teste")
    monkeypatch.setenv("AISWEB_API_PASS", "teste")
    monkeypatch.setenv("PLANO_CONSULTAR_SOL", "1")

    resultado = sol_aerodromo(
        "SBJD",
        datetime(2026, 12, 1, 12, tzinfo=timezone.utc),
        getter=lambda *args, **kwargs: SimpleNamespace(
            text=xml,
            raise_for_status=lambda: None,
        ),
    )

    assert resultado == {"estado": "indisponivel"}


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


def _xml_lista_rotaer(registros, total):
    itens = "".join(
        f"""
        <item ciad_id="{indice}">
          <id>{item['versao']}</id><type>{item['tipo']}</type>
          <AeroCode>{item['icao']}</AeroCode><name>{item['nome']}</name>
          <dt>{item['data']}</dt>
        </item>
        """
        for indice, item in enumerate(registros, start=1)
    )
    return f'<aisweb><rotaer total="{total}" pagesize="100">{itens}</rotaer></aisweb>'


def _xml_detalhe_rotaer(icao, tipo="AD", altitude="12"):
    return f"""
    <aisweb>
      <status>ativo</status><dt>2026-11-25</dt>
      <AeroCode>{icao}</AeroCode><name>Local {icao}</name>
      <lat>-23.5</lat><lng>-46.6</lng><type>{tipo}</type><altM>{altitude}</altM>
    </aisweb>
    """


def _html_detalhe_rotaer():
    return """
    <!-- emenda 30/07/2026 -->
    <table class="rotaer">
      <tr>
        <td><span title="Nome do Aeródromo">Fazenda Canadá</span>
          (<span title="Indicador de Localidade (ICAO Code)">SI5J</span>)</td>
        <td>17 40 51.41S/050 05 05 .06W</td>
      </tr>
      <tr>
        <td><span title="Aeródromo">AD</span></td>
        <td>498 <strong>(1634)</strong></td>
      </tr>
    </table>
    <p>RMK: Atendimento local. THRU TEL: (63) 99985- 0868, (63) 2993-0183 ou pelo e-mail gerencia.swgn@esaero.com.br</p>
    """


def _item_rotaer(icao, versao="v1", tipo="AD"):
    return {
        "icao": icao,
        "versao": versao,
        "tipo": tipo,
        "nome": f"Local {icao}",
        "data": "2026-11-25",
    }


def test_download_rotaer_interpreta_lista_atual_e_pagina_por_quantidade(monkeypatch):
    monkeypatch.setenv("AISWEB_API_KEY", "teste")
    monkeypatch.setenv("AISWEB_API_PASS", "teste")
    itens = [_item_rotaer(f"T{indice:03d}") for indice in range(101)]
    chamadas_lista = []
    chamadas_detalhe = []
    ativa = 0
    max_ativa = 0
    from threading import Lock

    lock = Lock()

    def getter(url, params=None, timeout=None):
        nonlocal ativa, max_ativa
        if "icaoCode" in params:
            with lock:
                ativa += 1
                max_ativa = max(max_ativa, ativa)
            time.sleep(0.001)
            chamadas_detalhe.append(params["icaoCode"])
            resposta = SimpleNamespace(
                text=_xml_detalhe_rotaer(params["icaoCode"]),
                raise_for_status=lambda: None,
            )
            with lock:
                ativa -= 1
            return resposta
        chamadas_lista.append(dict(params))
        inicio = int(params["rowstart"])
        quantidade = int(params["rowend"])
        pagina = itens[inicio : inicio + quantidade]
        return SimpleNamespace(
            text=_xml_lista_rotaer(pagina, len(itens)),
            raise_for_status=lambda: None,
        )

    codigo, registros = _baixar_rotaer(getter=getter)

    assert codigo
    assert len(registros) == 101
    assert len(chamadas_lista) == 2
    assert [chamada["rowstart"] for chamada in chamadas_lista] == [0, 100]
    assert all(chamada["rowend"] == 100 for chamada in chamadas_lista)
    assert all(chamada["type"] == "AD" for chamada in chamadas_lista)
    assert "amdt" not in chamadas_lista[0]
    assert len(chamadas_detalhe) == 101
    assert max_ativa <= 4
    assert all(item["elev_m"] == 12 for item in registros)
    assert all(item["rotaer_versao_id"].startswith("v") for item in registros)
    assert all(item["rotaer_atualizado_em"] == date(2026, 11, 25) for item in registros)


def test_download_rotaer_rejeita_total_alterado_durante_paginacao(monkeypatch):
    monkeypatch.setenv("AISWEB_API_KEY", "teste")
    monkeypatch.setenv("AISWEB_API_PASS", "teste")
    chamadas = []

    def getter(url, params=None, timeout=None):
        chamadas.append(params["rowstart"])
        total = 2 if params["rowstart"] == 0 else 3
        item = _item_rotaer(f"T{params['rowstart']:03d}")
        return SimpleNamespace(
            text=_xml_lista_rotaer([item], total),
            raise_for_status=lambda: None,
        )

    with pytest.raises(ValueError, match="total ROTAER mudou"):
        _baixar_rotaer(getter=getter)

    assert chamadas == [0, 1]


def test_download_rotaer_rejeita_pagina_vazia_antes_do_total(monkeypatch):
    monkeypatch.setenv("AISWEB_API_KEY", "teste")
    monkeypatch.setenv("AISWEB_API_PASS", "teste")
    chamadas = []

    def getter(url, params=None, timeout=None):
        chamadas.append(params["rowstart"])
        itens = [_item_rotaer("T001")] if params["rowstart"] == 0 else []
        return SimpleNamespace(
            text=_xml_lista_rotaer(itens, 2),
            raise_for_status=lambda: None,
        )

    with pytest.raises(ValueError, match="página ROTAER vazia"):
        _baixar_rotaer(getter=getter)

    assert chamadas == [0, 1]


def test_download_rotaer_reutiliza_detalhe_quando_versao_nao_muda(monkeypatch):
    monkeypatch.setenv("AISWEB_API_KEY", "teste")
    monkeypatch.setenv("AISWEB_API_PASS", "teste")
    item = _item_rotaer("T001")
    chamadas = []
    cache = {
        "T001": {
            "rotaer_versao_id": "v1",
            "rotaer_atualizado_em": date(2026, 11, 25),
            "lat": -23.5,
            "lon": -46.6,
            "elev_m": 12,
            "telefone": None,
            "email": None,
            "contatos_rotaer_verificados": True,
        }
    }

    def getter(url, params=None, timeout=None):
        chamadas.append(dict(params))
        return SimpleNamespace(
            text=_xml_lista_rotaer([item], 1),
            raise_for_status=lambda: None,
        )

    _, registros = _baixar_rotaer(getter=getter, cache=cache)

    assert len(registros) == 1
    assert registros[0]["lat"] == -23.5
    assert registros[0]["elev_m"] == 12
    assert len(chamadas) == 1


@pytest.mark.parametrize(
    "xml_inicial",
    ["<aisweb/>", "<aisweb><AeroCode>SBSP</AeroCode></aisweb>"],
)
def test_download_rotaer_faz_fallback_para_html_sem_icao_correspondente(
    monkeypatch, xml_inicial
):
    monkeypatch.setenv("AISWEB_API_KEY", "teste")
    monkeypatch.setenv("AISWEB_API_PASS", "teste")
    item = {
        **_item_rotaer("SI5J", versao="3051277a"),
        "data": "2026-07-30",
        "nome": "Fazenda Canadá",
    }
    chamadas_detalhe = []

    def getter(url, params=None, timeout=None):
        if "icaoCode" not in params:
            return SimpleNamespace(
                text=_xml_lista_rotaer([item], 1),
                raise_for_status=lambda: None,
            )
        chamadas_detalhe.append(dict(params))
        corpo = _html_detalhe_rotaer() if params.get("force") == "html" else xml_inicial
        return SimpleNamespace(text=corpo, raise_for_status=lambda: None)

    _, registros = _baixar_rotaer(getter=getter)

    assert len(chamadas_detalhe) == 2
    assert chamadas_detalhe[1]["force"] == "html"
    assert registros[0]["icao"] == "SI5J"
    assert registros[0]["nome"] == "Fazenda Canadá"
    assert registros[0]["lat"] == pytest.approx(-(17 + 40 / 60 + 51.41 / 3600))
    assert registros[0]["lon"] == pytest.approx(-(50 + 5 / 60 + 5.06 / 3600))
    assert registros[0]["elev_m"] == 498
    assert registros[0]["rotaer_atualizado_em"] == date(2026, 7, 30)
    assert registros[0]["telefone"] == "(63) 99985-0868, (63) 2993-0183"
    assert registros[0]["email"] == "gerencia.swgn@esaero.com.br"
    assert registros[0]["contatos_rotaer_verificados"] is True


def test_carregar_rotaer_atualiza_e_limpa_contatos_da_emenda(cliente):
    cadastrar(cliente)
    db = _db()
    try:
        com_contatos = """
        <aisweb><emenda>CONTATOS-1</emenda><rotaer>
          <AeroCode>S0A1</AeroCode><name>Aeródromo Um</name><type>AD</type>
          <lat>0</lat><lng>0</lng><altM>10</altM>
          <telefone>(11) 99999-1234</telefone><email>ops@example.br</email>
        </rotaer></aisweb>
        """
        assert carregar_rotaer(db, corpo=com_contatos) == "disponivel"
        aero = db.get(Aerodromo, "S0A1")
        assert aero.telefone == "(11) 99999-1234"
        assert aero.email == "ops@example.br"
        assert aero.contatos_rotaer_verificados is True

        sem_contatos = com_contatos.replace(
            "<telefone>(11) 99999-1234</telefone><email>ops@example.br</email>",
            "",
        ).replace("CONTATOS-1", "CONTATOS-2")
        assert carregar_rotaer(db, corpo=sem_contatos) == "disponivel"
        assert aero.telefone is None
        assert aero.email is None
        assert aero.contatos_rotaer_verificados is True
    finally:
        Sessao.remove()


def test_carregar_rotaer_busca_contatos_para_cache_antigo(cliente, monkeypatch):
    monkeypatch.setenv("AISWEB_API_KEY", "teste")
    monkeypatch.setenv("AISWEB_API_PASS", "teste")
    item = _item_rotaer("S9Z7", versao="v1")
    chamadas_detalhe = []

    def getter(url, params=None, timeout=None):
        if "icaoCode" in params:
            chamadas_detalhe.append(params["icaoCode"])
            return SimpleNamespace(
                text="""
                <aisweb><AeroCode>S9Z7</AeroCode><type>AD</type>
                  <dt>2026-11-25</dt><lat>-23.5</lat><lng>-46.6</lng>
                  <altM>12</altM><telefone>(21) 3333-4444</telefone>
                  <email>contato@example.br</email>
                </aisweb>
                """,
                raise_for_status=lambda: None,
            )
        return SimpleNamespace(
            text=_xml_lista_rotaer([item], 1),
            raise_for_status=lambda: None,
        )

    db = _db()
    try:
        db.add(
            Aerodromo(
                icao="S9Z7",
                nome="Local S9Z7",
                tipo="aerodromo",
                lat=-23.5,
                lon=-46.6,
                elev_m=12,
                rotaer_versao_id="v1",
                rotaer_atualizado_em=date(2026, 11, 25),
                fonte="ROTAER anterior",
                contatos_rotaer_verificados=False,
            )
        )
        db.commit()
        assert carregar_rotaer(db, getter=getter) == "disponivel"
        aero = db.get(Aerodromo, "S9Z7")
        assert chamadas_detalhe == ["S9Z7"]
        assert aero.telefone == "(21) 3333-4444"
        assert aero.email == "contato@example.br"
        assert aero.contatos_rotaer_verificados is True

        assert carregar_rotaer(db, getter=getter) == "disponivel"
        assert chamadas_detalhe == ["S9Z7"]
    finally:
        Sessao.remove()


def test_carregar_rotaer_reutiliza_cache_persistido_e_invalida_versao(cliente, monkeypatch):
    monkeypatch.setenv("AISWEB_API_KEY", "teste")
    monkeypatch.setenv("AISWEB_API_PASS", "teste")
    versao = ["v1"]
    chamadas_detalhe = []
    item = _item_rotaer("S9Z8")

    def getter(url, params=None, timeout=None):
        if "icaoCode" in params:
            chamadas_detalhe.append(params["icaoCode"])
            return SimpleNamespace(
                text=_xml_detalhe_rotaer(params["icaoCode"]),
                raise_for_status=lambda: None,
            )
        return SimpleNamespace(
            text=_xml_lista_rotaer([{**item, "versao": versao[0]}], 1),
            raise_for_status=lambda: None,
        )

    db = Sessao()
    try:
        assert carregar_rotaer(db, getter=getter) == "disponivel"
        assert db.get(Aerodromo, "S9Z8").rotaer_versao_id == "v1"
        assert carregar_rotaer(db, getter=getter) == "disponivel"
        assert chamadas_detalhe == ["S9Z8"]

        versao[0] = "v2"
        assert carregar_rotaer(db, getter=getter) == "disponivel"
        assert chamadas_detalhe == ["S9Z8", "S9Z8"]
        assert db.get(Aerodromo, "S9Z8").rotaer_versao_id == "v2"
    finally:
        Sessao.remove()


def test_download_rotaer_rejeita_detalhe_sem_elevacao(monkeypatch):
    monkeypatch.setenv("AISWEB_API_KEY", "teste")
    monkeypatch.setenv("AISWEB_API_PASS", "teste")
    item = _item_rotaer("T001")

    def getter(url, params=None, timeout=None):
        detalhe = _xml_detalhe_rotaer("T001").replace("<altM>12</altM>", "")
        return SimpleNamespace(
            text=detalhe if "icaoCode" in params else _xml_lista_rotaer([item], 1),
            raise_for_status=lambda: None,
        )

    with pytest.raises(ValueError, match="altM"):
        _baixar_rotaer(getter=getter)


@pytest.mark.parametrize(("campo", "valor"), [("lat", "91"), ("lng", "181")])
def test_download_rotaer_rejeita_coordenada_fora_do_intervalo(monkeypatch, campo, valor):
    monkeypatch.setenv("AISWEB_API_KEY", "teste")
    monkeypatch.setenv("AISWEB_API_PASS", "teste")
    item = _item_rotaer("T001")

    def getter(url, params=None, timeout=None):
        detalhe = _xml_detalhe_rotaer("T001").replace(
            "<lat>-23.5</lat>" if campo == "lat" else "<lng>-46.6</lng>",
            f"<{campo}>{valor}</{campo}>",
        )
        return SimpleNamespace(
            text=detalhe if "icaoCode" in params else _xml_lista_rotaer([item], 1),
            raise_for_status=lambda: None,
        )

    with pytest.raises(ValueError, match=f"campo {campo} fora do intervalo"):
        _baixar_rotaer(getter=getter)


def test_falha_em_detalhe_nao_publica_catalogo_parcial(cliente, caplog, monkeypatch):
    monkeypatch.setenv("AISWEB_API_KEY", "chave-teste-secreta")
    monkeypatch.setenv("AISWEB_API_PASS", "senha-teste-secreta")
    itens = [_item_rotaer("S9Z1"), _item_rotaer("S9Z2")]

    def getter(url, params=None, timeout=None):
        if "icaoCode" in params:
            icao = params["icaoCode"]
            if icao == "S9Z2":
                return SimpleNamespace(
                    text=_xml_detalhe_rotaer("S9ZZ"),
                    raise_for_status=lambda: None,
                )
            return SimpleNamespace(
                text=_xml_detalhe_rotaer(icao),
                raise_for_status=lambda: None,
            )
        return SimpleNamespace(
            text=_xml_lista_rotaer(itens, len(itens)),
            raise_for_status=lambda: None,
        )

    db = Sessao()
    try:
        assert carregar_rotaer(db, getter=getter) == "indisponivel"
        assert db.get(Aerodromo, "S9Z1") is None
        assert db.get(Aerodromo, "S9Z2") is None
    finally:
        Sessao.remove()

    assert "chave-teste-secreta" not in caplog.text
    assert "senha-teste-secreta" not in caplog.text
