import json
import re
import subprocess
from datetime import date

import pytest
from flask import template_rendered

from servidor import rainviewer
from servidor import tempo as tempo_mod
from servidor.catalogo import carregar_rab
from servidor.modelos import (
    Aerodromo,
    Aeronave,
    EmendaRotaer,
    ExtratoRab,
    PlanoDeVoo,
    Sessao,
    Trecho,
)
from servidor.perfis_sinteticos import PERFIS_SINTETICOS
from tests.conftest import JSON, cadastrar, plano_valido
from tests.conftest_rota import semear_perfis_sinteticos_teste


def _meteorologia_indisponivel(origem, destino, getter=None, *, aerodromos=None):
    lugares = list(aerodromos or (origem, destino))
    for lugar in (origem, destino):
        if all(aero.icao != lugar.icao for aero in lugares):
            lugares.append(lugar)
    boletins = {
        lugar.icao: {
            "estado": "indisponivel",
            "fonte": "Aviation Weather Center",
        }
        for lugar in lugares
    }
    return {
        "estado": "indisponivel",
        "origem": boletins[origem.icao],
        "destino": boletins[destino.icao],
        "aerodromos": boletins,
    }


@pytest.fixture(autouse=True)
def _nao_consultar_metar_real(monkeypatch):
    monkeypatch.setattr(
        tempo_mod,
        "meteorologia",
        lambda *args, **kwargs: {"estado": "indisponivel"},
    )
    monkeypatch.setattr(
        tempo_mod,
        "meteorologia_rota",
        _meteorologia_indisponivel,
        raising=False,
    )


def adicionar_trecho_de_retorno(plano_id):
    db = Sessao()
    try:
        plano = db.get(PlanoDeVoo, plano_id)
        primeiro = plano.trechos[0]
        db.add(
            Trecho(
                plano_id=plano.id,
                ordem=2,
                origem_icao="SBAU",
                destino_icao="SBJD",
                distancia_valor=primeiro.distancia_valor,
                distancia_unidade=primeiro.distancia_unidade,
                distancia_fonte=primeiro.distancia_fonte,
                proa_valor=primeiro.proa_valor,
                proa_unidade=primeiro.proa_unidade,
                proa_fonte=primeiro.proa_fonte,
                tempo_valor=primeiro.tempo_valor,
                tempo_unidade=primeiro.tempo_unidade,
                tempo_fonte=primeiro.tempo_fonte,
                combustivel_valor=primeiro.combustivel_valor,
                combustivel_unidade=primeiro.combustivel_unidade,
                combustivel_fonte=primeiro.combustivel_fonte,
                vento_estado=primeiro.vento_estado,
                por_do_sol_estado=primeiro.por_do_sol_estado,
                velocidade_solo_kt=primeiro.velocidade_solo_kt,
            )
        )
        db.commit()
    finally:
        Sessao.remove()


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
    assert re.search(r'<option value="SBJD" selected>SBJD —', html)
    assert re.search(r'<select\b(?=[^>]*\bname="aeronave_id")', html)
    assert "Não é autorização de voo." in html


def test_formulario_agrupa_campos_em_duas_linhas_responsivas(cliente):
    cadastrar(cliente)
    html = cliente.get("/planos/novo").get_data(as_text=True)

    assert html.count("sm:grid-cols-2") == 2
    assert 'name="hora_partida"' in html
    assert 'name="numero_passageiros"' in html
    assert 'name="peso_pessoas_kg"' in html
    assert 'name="peso_bagagem_kg"' in html
    assert 'id="confirma-hora"' in html


def test_sem_rab_selecao_de_aeronave_vazia_e_envio_desativado(cliente, monkeypatch, tmp_path):
    cadastrar(cliente)
    monkeypatch.setenv("RAB_EXTRATO", str(tmp_path / "extrato-inexistente.csv"))
    db = Sessao()
    try:
        assert carregar_rab(db) == "indisponivel"
    finally:
        Sessao.remove()
    html = cliente.get("/planos/novo").get_data(as_text=True)

    selecao = re.search(
        r'<select\b(?=[^>]*\bname="aeronave_id")[^>]*>(.*?)</select>',
        html,
        re.S,
    )
    botao = re.search(r"<button[^>]*>Calcular</button>", html)

    assert (
        "Catálogo nacional de aeronaves factuais indisponível. "
        "Os perfis sintéticos didáticos são exibidos separadamente."
    ) in html
    assert selecao is not None
    assert "<option" not in selecao.group(1)
    assert "disabled" in selecao.group(0)
    assert botao is not None
    assert "disabled" in botao.group(0)


def test_tela_novo_plano_oferece_categoria_sintetica_sem_rab(cliente):
    cadastrar(cliente)
    db = Sessao()
    try:
        semear_perfis_sinteticos_teste(db)
        for aeronave in db.query(Aeronave).all():
            aeronave.extrato_id = None
        db.query(ExtratoRab).delete(synchronize_session=False)
        db.commit()
    finally:
        Sessao.remove()

    html = cliente.get("/planos/novo").get_data(as_text=True)
    selecao = re.search(
        r'<select\b(?=[^>]*\bname="aeronave_id")[^>]*>(.*?)</select>',
        html,
        re.S,
    )
    assert selecao is not None
    assert "Perfis sintéticos didáticos" in selecao.group(1)
    assert selecao.group(1).count("<option") == 20
    assert "Aeronave DEMO" not in selecao.group(1)
    assert "Proxy DEMO" not in selecao.group(1)
    assert re.findall(r"<option[^>]*>(.*?)</option>", selecao.group(1)) == [
        perfil.alvo_modelo for perfil in PERFIS_SINTETICOS
    ]
    card = re.search(r'<section\b(?=[^>]*id="card-plano").*?</section>', html, re.S)
    assert card is not None
    texto_aviso = (
        "Cálculos e dados dos perfis sintéticos são exclusivamente didáticos: "
        "valores não validados, que não representam dados do modelo associado. "
        "Não substituem o manual da aeronave, o treinamento de voo nem a norma "
        "vigente; não são adequados para planejamento de voo real e não autorizam "
        "o voo."
    )
    assert texto_aviso in card.group(0)
    assert card.group(0).index(texto_aviso) > card.group(0).index("</form>")
    assert card.group(0).count("Cálculos e dados dos perfis sintéticos") == 1


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
    for campo in ("origem", "destino"):
        assert re.search(
            rf'<select\b(?=[^>]*\bid="{campo}")(?=[^>]*\bname="{campo}")(?=[^>]*\brequired)',
            pagina,
        )
        assert re.search(
            rf'<input\b(?=[^>]*\bid="{campo}-busca")(?=[^>]*\brole="combobox")[^>]*>',
            pagina,
        )
        assert re.search(
            rf'<input\b(?=[^>]*\bid="{campo}-busca")(?=[^>]*\bdisabled)',
            pagina,
        )
        assert f'data-combobox="{campo}"' in pagina
    assert "Filtrar origem" not in pagina
    assert "Filtrar destino" not in pagina
    assert "SBJD —" in pagina
    assert "Modelo Base" in pagina
    assert 'size="' not in pagina
    assert "data-filtra" not in pagina
    assert 'aria-autocomplete="list"' in pagina
    assert 'role="listbox"' in pagina
    assert 'data-fallback-aerodromo' in pagina
    assert 'data-controle-busca hidden' in pagina
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
    assert 'data-combobox="origem"' in pagina
    assert 'data-combobox="destino"' in pagina
    assert "Filtrar origem" not in pagina
    assert "Filtrar destino" not in pagina
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


def test_combobox_seleciona_com_teclado_e_clique_e_recusa_texto_livre(cliente):
    cadastrar(cliente)
    db = Sessao()
    try:
        emenda = db.query(EmendaRotaer).filter_by(vigente=True).one()
        for icao, nome in (("ZZSJ", "São José Teste"), ("ZZSP", "São Pedro Teste")):
            db.add(
                Aerodromo(
                    icao=icao,
                    nome=nome,
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
    script = re.search(
        r"<script>\s*(function planoCasa.*?)(?=</script>)",
        pagina,
        re.S,
    )
    assert script
    programa = r"""
const listeners = (element) => element.listeners || (element.listeners = {});
const emitir = (element, tipo, dados = {}) =>
  (listeners(element)[tipo] || []).forEach((handler) =>
    handler(Object.assign({preventDefault() {}}, dados))
  );
const classes = () => ({
  values: new Set(),
  add(...names) { names.forEach((name) => this.values.add(name)); },
  remove(...names) { names.forEach((name) => this.values.delete(name)); }
});
const dados = [
  {value: "SBJD", textContent: "SBJD — Jundiaí"},
  {value: "SBAU", textContent: "SBAU — Araçatuba"},
  {value: "ZZSJ", textContent: "ZZSJ — São José Teste"},
  {value: "ZZSP", textContent: "ZZSP — São Pedro Teste"}
];
function criarOpcao() {
  return {
    dataset: {}, hidden: false, classList: classes(), attributes: {},
    setAttribute(name, value) { this.attributes[name] = value; },
    scrollIntoView() {}
  };
}
function criarCombo(nome, codigoInicial) {
  const seletor = {
    value: codigoInicial,
    selectedIndex: dados.findIndex((opcao) => opcao.value === codigoInicial),
    options: dados, hidden: false, required: true
  };
  const campo = {
    id: nome + "-busca", value: "", focused: false, disabled: true, attributes: {},
    addEventListener(tipo, handler) { (listeners(this)[tipo] ||= []).push(handler); },
    setAttribute(name, value) { this.attributes[name] = value; },
    removeAttribute(name) { delete this.attributes[name]; },
    setCustomValidity(value) { this.validityMessage = value; },
    focus() { if (!this.focused) { this.focused = true; emitir(this, "focus"); } }
  };
  const opcoes = [];
  const lista = {
    hidden: true,
    appendChild(opcao) { opcoes.push(opcao); },
    querySelectorAll: () => opcoes,
    addEventListener(tipo, handler) { (listeners(this)[tipo] ||= []).push(handler); }
  };
  const status = {hidden: true, textContent: ""};
  const controle = {
    hidden: true,
    querySelector(seletor) {
      return seletor === '[role="listbox"]' ? lista : status;
    }
  };
  const rotulo = {htmlFor: nome};
  const container = {
    dataset: {combobox: nome},
    querySelector(seletor) {
      if (seletor === "[data-fallback-aerodromo]") return this.seletor;
      if (seletor === "[data-controle-busca]") return controle;
      if (seletor === "[data-busca-aerodromo]") return campo;
      if (seletor === "label") return rotulo;
    },
    contains(alvo) {
      return alvo === this || alvo === campo || alvo === seletor || alvo === lista ||
        alvo === controle || alvo === status || opcoes.includes(alvo);
    },
    seletor
  };
  return {container, campo, seletor, lista, status, controle, rotulo, opcoes};
}
const origem = criarCombo("origem", "SBJD");
const destino = criarCombo("destino", "SBAU");
const combos = [origem, destino];
global.document = {
  listeners: {},
  querySelectorAll: () => combos.map((combo) => combo.container),
  createElement: (tag) => tag === "li" ? criarOpcao() : null,
  addEventListener(tipo, handler) { (listeners(this)[tipo] ||= []).push(handler); }
};
"""
    programa += script.group(1)
    programa += r"""
emitir(origem.campo, "focus");
origem.campo.value = "sao";
emitir(origem.campo, "input");
const buscaSemAcento = origem.opcoes.filter((opcao) => !opcao.hidden).map((opcao) => opcao.dataset.icao);
emitir(origem.campo, "keydown", {key: "ArrowDown"});
const primeiraAtiva = origem.campo.attributes["aria-activedescendant"];
emitir(origem.campo, "keydown", {key: "ArrowDown"});
emitir(origem.campo, "keydown", {key: "ArrowUp"});
emitir(origem.campo, "keydown", {key: "ArrowDown"});
const segundaAtiva = origem.campo.attributes["aria-activedescendant"];
emitir(origem.campo, "keydown", {key: "Enter"});
const selecaoTeclado = {
  codigo: origem.seletor.value,
  rotulo: origem.campo.value,
  listaFechada: origem.lista.hidden,
  focoMantido: origem.campo.focused
};
origem.campo.value = "sem correspondencia";
emitir(origem.campo, "input");
const mensagemSemResultado = origem.status.textContent;
const textoLivreRecusado = !origem.seletor.value &&
  origem.campo.validityMessage === "Escolha um aeródromo da lista.";
emitir(origem.campo, "keydown", {key: "Escape"});
const escapeRestaura = {codigo: origem.seletor.value, rotulo: origem.campo.value};
emitir(origem.campo, "focus");
emitir(document, "focusin", {target: {}});
const focoForaFechaLista = origem.lista.hidden;
destino.campo.focused = false;
destino.campo.focus();
destino.campo.value = "jundiai";
emitir(destino.campo, "input");
const opcaoDestino = destino.opcoes.find((opcao) => !opcao.hidden);
destino.campo.focused = false;
destino.lista.listeners.click[0]({target: {closest: () => opcaoDestino}});
console.log(JSON.stringify({
  buscaSemAcento,
  primeiraAtiva,
  segundaAtiva,
  selecaoTeclado,
  mensagemSemResultado,
  escapeRestaura,
  focoForaFechaLista,
  fallbackNativo: combos.map((combo) => ({
    selectOculto: combo.seletor.hidden,
    selectSemRequired: !combo.seletor.required,
    controleVisivel: !combo.controle.hidden,
    campoHabilitado: !combo.campo.disabled,
    rotuloLigado: combo.rotulo.htmlFor === combo.campo.id
  })),
  selecaoClique: {
    origem: origem.seletor.value,
    destino: destino.seletor.value,
    rotuloDestino: destino.campo.value,
    listaFechada: destino.lista.hidden
  },
  textoLivreRecusado
}));
"""
    saida = subprocess.run(
        ["node", "-e", programa],
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(saida.stdout) == {
        "buscaSemAcento": ["ZZSJ", "ZZSP"],
        "primeiraAtiva": "origem-opcao-3",
        "segundaAtiva": "origem-opcao-4",
        "selecaoTeclado": {
            "codigo": "ZZSP",
            "rotulo": "ZZSP — São Pedro Teste",
            "listaFechada": True,
            "focoMantido": True,
        },
        "mensagemSemResultado": "Nenhum aeródromo encontrado.",
        "escapeRestaura": {
            "codigo": "ZZSP",
            "rotulo": "ZZSP — São Pedro Teste",
        },
        "focoForaFechaLista": True,
        "fallbackNativo": [
            {
                "selectOculto": True,
                "selectSemRequired": True,
                "controleVisivel": True,
                "campoHabilitado": True,
                "rotuloLigado": True,
            },
            {
                "selectOculto": True,
                "selectSemRequired": True,
                "controleVisivel": True,
                "campoHabilitado": True,
                "rotuloLigado": True,
            },
        ],
        "selecaoClique": {
            "origem": "ZZSP",
            "destino": "SBJD",
            "rotuloDestino": "SBJD — Jundiaí",
            "listaFechada": True,
        },
        "textoLivreRecusado": True,
    }


def test_painel_oferece_editar_e_apagar_somente_o_proprio_plano(cliente):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]
    html = cliente.get("/painel").get_data(as_text=True)
    assert f'href="/planos/{plano_id}/alterar"' in html
    assert 'aria-label="Editar plano SBJD SBAU"' in html
    assert 'aria-label="Apagar plano SBJD SBAU"' in html
    assert ">Editar<" not in html
    assert ">Apagar<" not in html
    assert f'action="/planos/{plano_id}/apagar"' in html
    assert "Confirmar exclusão" in html

    sem_confirmacao = cliente.post(f"/planos/{plano_id}/apagar")
    assert sem_confirmacao.status_code == 302
    assert cliente.get(f"/planos/{plano_id}", headers=JSON).status_code == 200

    outro = cliente.application.test_client()
    cadastrar(outro, "bia")
    alheio = outro.post(f"/planos/{plano_id}/apagar", data={"confirmar": "on"})
    assert alheio.status_code == 404

    apagado = cliente.post(f"/planos/{plano_id}/apagar", data={"confirmar": "on"})
    assert apagado.status_code == 302
    assert cliente.get(f"/planos/{plano_id}", headers=JSON).status_code == 404
    assert "Não há voo planejado." in cliente.get("/painel").get_data(as_text=True)


def test_painel_mostra_partida_na_linha_do_titulo_sem_rotulo_de_estado(cliente):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    assert criado.status_code == 201
    html = cliente.get("/painel").get_data(as_text=True)
    cabecalho = html.split('class="plano-cabecalho"', 1)[1].split('class="plano-acoes"', 1)[0]
    assert "SBJD → SBAU" in cabecalho
    assert "Partida 01/12/2026 12:00 TL" in cabecalho
    assert "aceitável para planejamento" not in html
    assert ">calculado<" not in html


def test_atualizar_recalcula_o_relatorio_sem_texto_no_botao(cliente):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]
    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)
    assert f'action="/planos/{plano_id}/atualizar"' in html
    botao = re.search(
        r'<button\b[^>]*aria-label="Atualizar relatório"[^>]*>(.*?)</button>',
        html,
        re.S,
    )
    assert botao is not None
    assert re.sub(r"<[^>]+>", "", botao.group(1)).strip() == ""
    assert 'class="recalculando"' in html
    assert "Recalculando..." in html
    assert "is-recalculando" in html
    db = Sessao()
    try:
        plano = db.get(PlanoDeVoo, plano_id)
        plano.resultado = {**plano.resultado, "efeito_vento": "marcador-antigo"}
        db.commit()
    finally:
        Sessao.remove()
    resposta = cliente.post(f"/planos/{plano_id}/atualizar")
    assert resposta.status_code == 302
    corpo = cliente.get(f"/planos/{plano_id}", headers=JSON).get_json()
    assert corpo["id"] == plano_id
    assert corpo["resultado"]["efeito_vento"] != "marcador-antigo"
    outro = cliente.application.test_client()
    cadastrar(outro, "bia")
    alheio = outro.post(f"/planos/{plano_id}/atualizar")
    assert alheio.status_code == 404


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


def test_tabela_vazia_nao_aparece_e_mapa_avisa_a_carta(cliente, monkeypatch):
    monkeypatch.delenv("REDEMET_API_KEY", raising=False)
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
    assert 'role="tablist"' in html
    assert html.index('id="mapa"') < html.index('id="estado-mapa"')
    assert "Carta WAC indisponível" not in html
    assert "Chave REDEMET não configurada." not in html
    assert "Mapa de ruas; não substitui a carta de voo visual oficial." not in html
    assert "Como ler este plano" not in html
    assert "Imprimir PDF" not in html


def test_detalhe_plano_apresenta_rota_completa_contatos_e_alerta_destacado(cliente):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]
    adicionar_trecho_de_retorno(plano_id)

    db = Sessao()
    try:
        origem = db.get(Aerodromo, "SBJD")
        origem.nome = "Aeroporto de Jundiaí"
        origem.tipo = "aerodromo"
        origem.rotaer_versao_id = "origem-1"
        origem.rotaer_atualizado_em = date(2026, 11, 26)
        origem.telefone = "(11) 99999-1234"
        origem.email = "operacoes@jundiai.example"
        origem.contatos_rotaer_verificados = True
        destino = db.get(Aerodromo, "SBAU")
        destino.nome = "Aeroporto de Araçatuba"
        destino.tipo = "aerodromo"
        destino.rotaer_versao_id = "destino-1"
        destino.rotaer_atualizado_em = date(2026, 11, 26)
        destino.telefone = "(18) 99999-9999"
        destino.email = "contato@aracatuba.example"
        destino.contatos_rotaer_verificados = False
        plano = db.get(PlanoDeVoo, plano_id)
        plano.resultado = {
            **plano.resultado,
            "alertas": ["Excesso de peso: limite de planejamento excedido."],
        }
        db.commit()
    finally:
        Sessao.remove()

    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)
    assert 'class="foto-aeronave"' in html
    assert "Foto indisponível." in html
    inicio_rota = html.index('aria-label="Rota completa"')
    trecho_rota = html[inicio_rota : html.index('id="mapa"', inicio_rota)]

    assert '<th class="titulo-rota">Etapa</th>' in trecho_rota
    assert '<th class="titulo-rota">Aeródromo</th>' in trecho_rota
    cabecalho = trecho_rota[trecho_rota.index("<thead>") : trecho_rota.index("</thead>")]
    assert cabecalho.index("Chegada estimada (UTC)") < cabecalho.index(
        "Partida estimada (UTC)"
    )
    assert cabecalho.index("Partida estimada (UTC)") < cabecalho.index(
        "Pôr do sol (UTC)"
    )
    assert '<th class="titulo-rota">Latitude (graus)</th>' in trecho_rota
    assert '<th class="titulo-rota">Longitude (graus)</th>' in trecho_rota
    assert '<th class="titulo-rota">Elevação (m)</th>' in trecho_rota
    assert "Aeroporto de Jundiaí" in trecho_rota
    assert "Aeroporto de Araçatuba" in trecho_rota
    assert trecho_rota.index("Aeroporto de Jundiaí") < trecho_rota.index(
        "Aeroporto de Araçatuba"
    )
    assert "SBJD" in trecho_rota and "SBAU" in trecho_rota
    assert re.search(r"-?\d+\.\d{4}", trecho_rota)
    assert not re.search(r"-?\d+\.\d{5,}", trecho_rota)
    assert "Aeródromos de origem e destino" not in html
    assert "operacoes@jundiai.example" not in html
    assert "(11) 99999-1234" not in html
    assert "(18) 99999-9999" not in html
    assert "contato@aracatuba.example" not in html
    assert "Indisponível" in html
    assert "Excesso de peso: limite de planejamento excedido." in html
    assert 'role="alert"' in html
    assert "text-[#B42318]" in html
    assert 'id="dialogo-fontes"' not in html
    assert "Informações sobre fontes" not in html
    assert "Fontes e dados do relatório" not in html
    assert html.index("IMPRIMIR VOO") < html.index('role="tablist"')
    assert "Como ler este plano" not in html
    assert "Imprimir PDF" not in html


def test_plano_com_varios_trechos_apresenta_fichas_e_remove_checklist_da_tela(cliente):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]
    adicionar_trecho_de_retorno(plano_id)

    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)

    assert html.index('id="resumo"') < html.index('role="tablist"')
    assert html.count('role="tab"') == 2
    assert html.count('role="tabpanel"') == 2
    assert 'aria-selected="true"' in html
    assert "SBJD — SBAU" in html
    assert "SBAU — SBJD" in html
    assert "<h2>Checklist</h2>" not in html
    assert "Marcar" not in html
    assert f"/planos/{plano_id}/pdf" in html


def test_mapa_recebe_somente_os_pontos_de_cada_trecho_sem_mensagens_redundantes(cliente):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]
    adicionar_trecho_de_retorno(plano_id)
    db = Sessao()
    try:
        db.get(PlanoDeVoo, plano_id).carta = {"estado": "indisponivel"}
        db.commit()
        aerodromos = {
            aero.icao: [aero.lat, aero.lon]
            for aero in db.query(Aerodromo).filter(Aerodromo.icao.in_(("SBJD", "SBAU"))).all()
        }
        nomes = {
            aero.icao: aero.nome
            for aero in db.query(Aerodromo).filter(Aerodromo.icao.in_(("SBJD", "SBAU"))).all()
        }
    finally:
        Sessao.remove()

    renderizado = {}

    def capturar_contexto(sender, template, context, **extra):
        if template.name == "plano.html":
            renderizado.update(context)

    with template_rendered.connected_to(capturar_contexto, cliente.application):
        html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)
    assert renderizado["pontos_por_trecho"] == [
        {
            "ordem": 1,
            "origem": "SBJD",
            "destino": "SBAU",
            "origem_nome": nomes["SBJD"],
            "destino_nome": nomes["SBAU"],
            "pontos": [aerodromos["SBJD"], aerodromos["SBAU"]],
        },
        {
            "ordem": 2,
            "origem": "SBAU",
            "destino": "SBJD",
            "origem_nome": nomes["SBAU"],
            "destino_nome": nomes["SBJD"],
            "pontos": [aerodromos["SBAU"], aerodromos["SBJD"]],
        },
    ]
    serializado = re.search(
        r'<script id="pontos-por-trecho" type="application/json">(.*?)</script>',
        html,
        re.S,
    )
    assert serializado
    assert json.loads(serializado.group(1)) == [
        {
            "ordem": 1,
            "origem": "SBJD",
            "destino": "SBAU",
            "origem_nome": nomes["SBJD"],
            "destino_nome": nomes["SBAU"],
            "pontos": [aerodromos["SBJD"], aerodromos["SBAU"]],
        },
        {
            "ordem": 2,
            "origem": "SBAU",
            "destino": "SBJD",
            "origem_nome": nomes["SBAU"],
            "destino_nome": nomes["SBJD"],
            "pontos": [aerodromos["SBAU"], aerodromos["SBJD"]],
        },
    ]
    assert html.count('id="wac-toggle"') == 1
    assert 'id="wac-toggle" type="button" disabled aria-label="Carta WAC, indisponível"' in html
    assert "Carta WAC indisponível" not in html
    assert 'id="dialogo-wac"' not in html
    assert html.count('id="mapa"') == 1
    assert html.count('L.map(elementoMapa, {zoomControl: false, scrollWheelZoom: false})') == 1
    assert 'mapa.scrollWheelZoom.enable()' in html
    assert 'L.control.zoom({position: "bottomleft"}).addTo(mapa)' in html
    assert "linha.setLatLngs(segmentos)" in html
    assert 'className: "rotulo-trecho ' in html
    assert 'return "Trecho " + trecho.ordem + " " + trecho.origem + " → " + trecho.destino;' in html
    assert "Mapa indisponível: coordenadas do trecho não encontradas." in html
    assert "mapa.fitBounds(L.latLngBounds(limites)" in html
    assert "Rota completa exibida." in html
    assert 'radarToggle.addEventListener("click"' in html
    assert 'id="radar-toggle" type="button" aria-label="Radar de chuva" aria-pressed="false"' in html
    assert 'id="satelite-toggle" type="button" aria-label="Imagem de satélite REDEMET" aria-pressed="false"' in html
    assert 'id="estado-satelite" role="status" aria-live="polite"' in html
    assert 'id="toggle-ruas"' not in html
    assert 'id="toggle-google"' not in html
    assert 'id="toggle-openaip"' not in html
    assert 'id="rainviewer-toggle"' not in html
    assert 'mapa.createPane("radarPane")' in html
    assert 'pane: "radarPane"' in html


def test_mapa_exibe_um_unico_controle_de_radar_e_wac_pdf_validada(cliente):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]
    db = Sessao()
    try:
        db.get(PlanoDeVoo, plano_id).carta = {
            "estado": "disponivel",
            "tipo": "pdf",
            "documentos": [
                {
                    "indice": "3182",
                    "nome": "WAC 3182",
                    "icao": "SBJD",
                    "url": "https://aisweb.example/3182.pdf",
                }
            ],
        }
        db.commit()
    finally:
        Sessao.remove()

    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)

    assert html.count('id="radar-toggle"') == 1
    assert 'aria-label="Radar de chuva"' in html
    assert "Carta WAC" in html
    assert 'href="https://aisweb.example/3182.pdf"' in html
    assert html.count('id="wac-toggle"') == 1
    assert "document.body.appendChild(dialogoWac)" in html
    assert "dialogoWac.showModal()" in html
    assert 'id="toggle-ruas"' not in html
    assert 'id="toggle-google"' not in html
    assert 'id="toggle-openaip"' not in html
    assert 'id="rainviewer-toggle"' not in html
    assert "Google Maps" not in html
    assert "OpenAIP" not in html


def test_resolvedor_radar_prioriza_rainviewer_e_usa_redemet_se_indisponivel(
    cliente, monkeypatch
):
    redemet = {
        "estado": "disponivel",
        "url": "https://radar.example/frame.png",
        "hora": "2026-12-01T12:00:00+00:00",
        "lat_min": -25.0,
        "lat_max": -20.0,
        "lon_min": -52.0,
        "lon_max": -45.0,
        "fonte": "REDEMET MaxCappi",
    }
    monkeypatch.setattr(tempo_mod, "radar", lambda *args: redemet)
    monkeypatch.setattr(
        rainviewer,
        "buscar_frame",
        lambda: {"frame": "frame-1", "hora": 1796126400, "max_zoom": 7},
    )

    sem_sessao = cliente.get("/planos/1/camadas/radar", headers=JSON)
    assert sem_sessao.status_code == 401
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]

    prioridade = cliente.get(
        f"/planos/{plano_id}/camadas/radar",
        headers=JSON,
    )
    assert prioridade.status_code == 200
    assert prioridade.get_json()["provedor"] == "RainViewer"
    assert "{z}/{x}/{y}.png" in prioridade.get_json()["radar_url"]
    assert prioridade.get_json()["hora_frame"] == "2026-12-01T12:00:00+00:00"
    assert prioridade.get_json()["atribuicao"]["url"] == "https://www.rainviewer.com/"
    assert prioridade.get_json()["aviso_cobertura"]
    assert prioridade.get_json()["fonte_relatorio"]["campo"] == "Radar de chuva"
    assert prioridade.get_json()["fonte_relatorio"]["publicador"] == "RainViewer"
    assert redemet["url"] not in prioridade.get_data(as_text=True)

    reserva = cliente.get(
        f"/planos/{plano_id}/camadas/radar?exclude=RainViewer",
        headers=JSON,
    )
    assert reserva.status_code == 200
    assert reserva.get_json()["provedor"] == "REDEMET"
    assert reserva.get_json()["radar_url"] == redemet["url"]
    assert reserva.get_json()["fonte_relatorio"]["publicador"] == "REDEMET"

    invalido = cliente.get(
        f"/planos/{plano_id}/camadas/radar?exclude=Google",
        headers=JSON,
    )
    assert invalido.status_code == 400

    cadastrar(cliente, identificacao="bia")
    negado = cliente.get(
        f"/planos/{plano_id}/camadas/radar",
        headers=JSON,
    )
    assert negado.status_code == 404


def test_resolvedor_satelite_exige_sessao_propriedade_e_nao_expoe_chave(
    cliente, monkeypatch
):
    manifesto = {
        "estado": "disponivel",
        "url": "https://estatico-redemet.decea.mil.br/satelite/frame.png",
        "hora": "2026-11-27 22:40:00",
        "lat_min": -56.0,
        "lat_max": 12.52,
        "lon_min": -100.0,
        "lon_max": -25.24,
        "fonte": "REDEMET Satélite realçada",
    }
    monkeypatch.setenv("REDEMET_API_KEY", "chave-privada-de-teste")
    monkeypatch.setattr(tempo_mod, "satelite", lambda *args: manifesto, raising=False)

    sem_sessao = cliente.get("/planos/1/camadas/satelite", headers=JSON)
    assert sem_sessao.status_code == 401

    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]
    resposta = cliente.get(
        f"/planos/{plano_id}/camadas/satelite",
        headers=JSON,
    )

    assert resposta.status_code == 200
    corpo = resposta.get_json()
    assert corpo["estado"] == "disponivel"
    assert corpo["provedor"] == "REDEMET"
    assert corpo["imagem_url"] == manifesto["url"]
    assert corpo["hora_frame"] == manifesto["hora"]
    assert "chave-privada-de-teste" not in resposta.get_data(as_text=True)

    cadastrar(cliente, identificacao="bia")
    negado = cliente.get(
        f"/planos/{plano_id}/camadas/satelite",
        headers=JSON,
    )
    assert negado.status_code == 404


def test_controles_do_mapa_nao_expoem_openaip(cliente, monkeypatch):
    monkeypatch.setenv("OPENAIP_API_KEY", "fake-private-key")
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]

    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)

    assert html.count('id="radar-toggle"') == 1
    assert 'id="rainviewer-toggle"' not in html
    assert 'id="toggle-openaip"' not in html
    assert "OpenAIP" not in html
    assert "Google Maps" not in html
    assert "Mapa de ruas" not in html
    assert "fake-private-key" not in html


def test_fichas_mostram_metar_e_taf_dos_aerodromos_do_trecho(cliente, monkeypatch):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]
    adicionar_trecho_de_retorno(plano_id)
    db = Sessao()
    try:
        plano = db.get(PlanoDeVoo, plano_id)
        meteorologia = {
            "estado": "disponivel",
            "origem": {"estado": "disponivel"},
            "destino": {"estado": "disponivel"},
            "aerodromos": {
                "SBJD": {
                    "estado": "disponivel",
                    "fonte": "Aviation Weather Center",
                    "metar": {
                        "icao": "SBJD",
                        "raw": "METAR SBJD 011200Z 18010KT 6SM -RA BKN020",
                        "hora": "2026-12-01T12:00:00Z",
                        "temp_c": 18,
                        "fenomenos": "-RA",
                        "vento_kt": 10,
                        "unidade_vento": "kt",
                        "fonte": "Aviation Weather Center",
                    },
                    "taf": {
                        "raw": "TAF SBJD 011100Z 0112/0200 18008KT 9999 -RA BKN030",
                        "fonte": "REDEMET",
                        "hora": "2026-12-01 11:10:00",
                        "validade_inicial": "2026-12-01 12:00:00",
                        "validade_final": "2026-12-02 00:00:00",
                    },
                },
                "SBAU": {
                    "estado": "disponivel",
                    "fonte": "Aviation Weather Center",
                    "metar": {
                        "icao": "SBST",
                        "nome_estacao": "Estação regional de teste",
                        "raw": "METAR SBST 011200Z VRB05KT -RA",
                        "hora": "2026-12-01T12:00:00Z",
                        "direcao_vento": "VRB",
                        "fenomenos": "-RA",
                        "regional": True,
                        "aerodromo_referencia": "SBAU",
                        "distancia_nm": 32.4,
                        "fonte": "Aviation Weather Center",
                    },
                    "taf": {"estado": "indisponivel"},
                },
            },
        }
        plano.meteorologia = meteorologia
        db.commit()
    finally:
        Sessao.remove()
    monkeypatch.setattr(
        tempo_mod,
        "meteorologia_rota",
        lambda *args, **kwargs: meteorologia,
    )

    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)
    primeira_ficha = re.search(
        r'<article[^>]*id="ficha-trecho-1"[^>]*>(.*?)</article>',
        html,
        re.S,
    )
    segunda_ficha = re.search(
        r'<article[^>]*id="ficha-trecho-2"[^>]*>(.*?)</article>',
        html,
        re.S,
    )
    assert primeira_ficha and segunda_ficha
    primeira = primeira_ficha.group(1)
    segunda = segunda_ficha.group(1)
    assert "METAR SBJD 011200Z 18010KT 6SM -RA BKN020" in primeira
    assert "METAR SBST 011200Z VRB05KT -RA" in primeira
    assert "METAR regional" in primeira
    assert "Estação regional de teste" in primeira
    assert "32.4 NM" in primeira
    assert "SBAU" in primeira
    assert "TAF SBJD 011100Z 0112/0200 18008KT 9999 -RA BKN030" in primeira
    assert "TAF da chegada indisponível" in primeira
    assert "Temperatura" in primeira and "18" in primeira and "°C" in primeira
    assert "Ponto de orvalho" in primeira and "Indisponível" in primeira
    assert "Direção do vento" in primeira and "VRB" in primeira
    assert "Fenômenos meteorológicos (código AWC)" in primeira and "-RA" in primeira
    assert "Chuva fraca" in primeira
    assert "Chuva fraca" in primeira.split("Leitura do TAF", 1)[1]
    assert "Aviation Weather Center" not in primeira
    assert "2026-12-01T12:00:00Z" in primeira
    assert primeira.index("Partida —") < primeira.index("METAR da saída")
    assert primeira.index("METAR da saída") < primeira.index("TAF da saída")
    assert primeira.index("TAF da saída") < primeira.index("Chegada —")
    assert primeira.index("Chegada —") < primeira.index("METAR da chegada")
    assert primeira.index("METAR da chegada") < primeira.index("TAF da chegada")
    assert "sm:grid-cols-2" not in primeira
    assert 'id="mapa"' not in primeira
    assert html.index('aria-label="Rota completa"') < html.index('id="mapa"')
    assert html.index('id="mapa"') < html.index('role="tablist"')
    assert "sequence-line" not in primeira
    assert "METAR SBST 011200Z VRB05KT -RA" in segunda
    assert "METAR SBJD 011200Z 18010KT 6SM" in segunda
    assert "TAF SBJD 011100Z 0112/0200 18008KT 9999 -RA BKN030" in segunda
    assert '<pre id="metar-original-' in primeira
    assert '<pre id="taf-original-' in primeira
    assert "Leitura do METAR" in primeira
    assert "Leitura do TAF" in primeira


def test_controles_do_mapa_sao_compactos_e_nao_exibem_estados_redundantes(
    cliente, monkeypatch
):
    monkeypatch.delenv("OPENAIP_API_KEY", raising=False)
    monkeypatch.delenv("REDEMET_API_KEY", raising=False)
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]

    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)

    assert 'id="radar-toggle" type="button" aria-label="Radar de chuva" aria-pressed="false"' in html
    assert html.count('id="radar-toggle"') == 1
    assert 'id="toggle-ruas"' not in html
    assert 'id="toggle-google"' not in html
    assert 'id="toggle-openaip"' not in html
    assert 'id="rainviewer-toggle"' not in html
    assert "OpenAIP indisponível: chave de serviço não configurada." not in html
    assert "OpenAIP disponível" not in html
    assert "Radar de chuva desativado." not in html
    assert "Radar de chuva desativado" not in html
    assert "Carta WAC indisponível" not in html
    assert "Chave REDEMET não configurada." not in html
    assert "Mapa de ruas; não substitui" not in html


def test_pagina_plano_omite_tabela_de_procedencia(cliente):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]

    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)
    assert "<h2>Fontes técnicas da aeronave</h2>" not in html


def test_plano_antigo_nao_mostra_detalhe_de_configuracao_do_radar(cliente, monkeypatch):
    monkeypatch.delenv("REDEMET_API_KEY", raising=False)
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]

    db = Sessao()
    try:
        db.get(PlanoDeVoo, plano_id).radar = {"estado": "indisponivel"}
        db.commit()
    finally:
        Sessao.remove()

    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)
    assert "Chave REDEMET não configurada." not in html
    assert 'id="informacao-radar" hidden' in html
    assert 'id="estado-radar" role="status" aria-live="polite"' in html


def test_provedor_radar_nao_e_consultado_ao_abrir_o_plano(cliente, monkeypatch):
    chamadas = []
    monkeypatch.setattr(
        rainviewer,
        "buscar_frame",
        lambda: chamadas.append("manifesto"),
    )
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]

    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)

    assert chamadas == []
    assert html.count('id="radar-toggle"') == 1
    assert 'id="rainviewer-toggle"' not in html
    assert "RainViewer — não oficial" not in html


def test_rotas_rainviewer_exigem_sessao_e_propriedade_do_plano(cliente, monkeypatch):
    chamadas = []
    chamadas_tiles = []
    chamadas_cobertura = []

    def buscar_tile_falso(frame, z, x, y):
        chamadas_tiles.append((frame, z, x, y))
        return b"\x89PNG\r\n\x1a\n tile", "public, max-age=60"

    def buscar_mascara_falsa(z, x, y):
        chamadas_cobertura.append((z, x, y))
        return b"\x89PNG\r\n\x1a\n mask", "public, max-age=60"

    monkeypatch.setattr(
        rainviewer,
        "buscar_frame",
        lambda: (
            chamadas.append("manifesto")
            or {"frame": "current-frame", "hora": 200, "max_zoom": 7}
        ),
    )
    monkeypatch.setattr(
        rainviewer,
        "buscar_tile",
        buscar_tile_falso,
    )
    monkeypatch.setattr(
        rainviewer,
        "buscar_mascara",
        buscar_mascara_falsa,
    )

    sem_sessao = cliente.get("/planos/1/camadas/rainviewer", headers=JSON)
    assert sem_sessao.status_code == 401

    cadastrar(cliente, identificacao="ana")
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]

    manifesto = cliente.get(
        f"/planos/{plano_id}/camadas/rainviewer",
        headers=JSON,
    )
    assert manifesto.status_code == 200
    assert manifesto.get_json()["hora_frame"] == 200
    assert "current-frame" in manifesto.get_json()["radar_url"]
    assert len(chamadas) == 1

    tile = cliente.get(
        f"/planos/{plano_id}/camadas/rainviewer/radar/current-frame/3/2/5.png",
        headers=JSON,
    )
    assert tile.status_code == 200
    assert tile.mimetype == "image/png"
    assert tile.headers["X-Content-Type-Options"] == "nosniff"
    assert chamadas_tiles == [("current-frame", 3, 2, 5)]

    cobertura = cliente.get(
        f"/planos/{plano_id}/camadas/rainviewer/cobertura/3/2/5.png",
        headers=JSON,
    )
    assert cobertura.status_code == 200
    assert cobertura.mimetype == "image/png"
    assert cobertura.headers["Cache-Control"] == "public, max-age=60"
    assert chamadas_cobertura == [(3, 2, 5)]

    cadastrar(cliente, identificacao="bob")
    negado = cliente.get(
        f"/planos/{plano_id}/camadas/rainviewer",
        headers=JSON,
    )
    assert negado.status_code == 404


def test_detalhe_atualiza_meteorologia_html_e_json_sem_persistir(cliente, monkeypatch):
    monkeypatch.delenv("REDEMET_API_KEY", raising=False)
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]

    db = Sessao()
    try:
        plano = db.get(PlanoDeVoo, plano_id)
        trechos_antes = [
            (
                trecho.ordem,
                trecho.origem_icao,
                trecho.destino_icao,
                trecho.tempo_valor,
                trecho.combustivel_valor,
            )
            for trecho in plano.trechos
        ]
        resultado_antes = dict(plano.resultado)
        plano.meteorologia = {
            "estado": "disponivel",
            "aerodromos": {
                "SBJD": {
                    "estado": "disponivel",
                    "metar": {"raw": "METAR SBJD OLD"},
                }
            },
        }
        plano.radar = {"estado": "disponivel", "url": "https://example.test/old.png"}
        db.commit()
    finally:
        Sessao.remove()

    boletim_atual = {
        "estado": "disponivel",
        "fonte": "Aviation Weather Center",
        "metar": {
            "icao": "SBJD",
            "raw": "METAR SBJD 011200Z 18010KT",
            "hora": "2026-12-01T12:00:00Z",
            "vento_kt": 10,
            "unidade_vento": "kt",
            "fonte": "Aviation Weather Center",
        },
        "taf": {"raw": "TAF SBJD 011100Z 18008KT"},
    }
    meteorologia_atual = {
        "estado": "disponivel",
        "origem": boletim_atual,
        "destino": {"estado": "indisponivel", "fonte": "Aviation Weather Center"},
        "aerodromos": {
            "SBJD": boletim_atual,
            "SBAU": {"estado": "indisponivel", "fonte": "Aviation Weather Center"},
        },
    }
    radar_atual = {
        "estado": "disponivel",
        "url": "https://example.test/current.png",
        "hora": "2026-12-01T12:00:00Z",
        "lat_min": -25.0,
        "lat_max": -20.0,
        "lon_min": -52.0,
        "lon_max": -45.0,
        "fonte": "REDEMET MaxCappi",
    }
    chamadas_meteorologia = []
    chamadas_radar = []

    def meteorologia_falsa(*args, **kwargs):
        chamadas_meteorologia.append(1)
        return meteorologia_atual

    def radar_falso(*args, **kwargs):
        chamadas_radar.append(1)
        return radar_atual

    monkeypatch.setattr(tempo_mod, "meteorologia_rota", meteorologia_falsa)
    monkeypatch.setattr(tempo_mod, "radar", radar_falso)

    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)
    resposta_json = cliente.get(f"/planos/{plano_id}", headers=JSON)
    corpo = resposta_json.get_json()

    assert resposta_json.status_code == 200
    assert "METAR SBJD 011200Z 18010KT" in html
    assert "METAR SBJD OLD" not in html
    assert "https://example.test/current.png" not in html
    assert corpo["meteorologia"] == meteorologia_atual
    assert corpo["radar"] == {"estado": "indisponivel"}
    assert len(chamadas_meteorologia) == 2
    assert len(chamadas_radar) == 0

    db = Sessao()
    try:
        plano = db.get(PlanoDeVoo, plano_id)
        assert plano.meteorologia["aerodromos"]["SBJD"]["metar"]["raw"] == "METAR SBJD OLD"
        assert plano.radar["url"] == "https://example.test/old.png"
        assert plano.destino_icao == "SBAU"
        assert plano.resultado == resultado_antes
        assert [
            (
                trecho.ordem,
                trecho.origem_icao,
                trecho.destino_icao,
                trecho.tempo_valor,
                trecho.combustivel_valor,
            )
            for trecho in plano.trechos
        ] == trechos_antes
    finally:
        Sessao.remove()


def test_tile_openaip_exige_sessao_e_propriedade_do_plano(cliente, monkeypatch):
    from servidor import openaip

    sem_sessao = cliente.get("/planos/1/camadas/openaip/3/2/5.png", headers=JSON)
    assert sem_sessao.status_code == 401

    monkeypatch.setenv("OPENAIP_API_KEY", "fake-private-key")
    chamadas = []
    monkeypatch.setattr(
        openaip,
        "buscar_tile",
        lambda z, x, y: (chamadas.append((z, x, y)) or (b"png", "public, max-age=60")),
    )
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]
    path = f"/planos/{plano_id}/camadas/openaip/3/2/5.png"

    proprio = cliente.get(path, headers=JSON)
    assert proprio.status_code == 200
    assert proprio.mimetype == "image/png"
    assert proprio.headers["Cache-Control"] == "public, max-age=60"

    outro_piloto = cliente.application.test_client()
    cadastrar(outro_piloto, "bia")
    alheio = outro_piloto.get(path, headers=JSON)
    assert alheio.status_code == 404
    assert chamadas == [(3, 2, 5)]


def test_checklist_nao_aparece_na_tela_do_plano(cliente):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]
    item_id = criado.get_json()["checklist"][1]["id"]
    resposta = cliente.post(f"/planos/{plano_id}/checklist/{item_id}", data={"marcado": "true"})
    assert resposta.status_code == 302
    assert resposta.headers["Location"].endswith(f"/planos/{plano_id}")
    html = cliente.get(resposta.headers["Location"].split("#")[0]).get_data(as_text=True)
    assert "<h2>Checklist</h2>" not in html
    assert "Marcar" not in html
    detalhe = cliente.get(f"/planos/{plano_id}", headers=JSON).get_json()
    assert next(item for item in detalhe["checklist"] if item["id"] == item_id)["marcado"]


def test_programacao_por_trecho_mostra_horarios_solares_e_pernoite(cliente):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]
    adicionar_trecho_de_retorno(plano_id)
    db = Sessao()
    try:
        plano = db.get(PlanoDeVoo, plano_id)
        plano.resultado = {
            **plano.resultado,
            "programacao": {
                "estado": "disponivel",
                "fuso": "UTC",
                "trechos": [
                    {
                        "ordem": 1,
                        "estado": "disponivel",
                        "etd": "2026-12-01T10:00:00+00:00",
                        "eta": "2026-12-01T11:00:00+00:00",
                        "origem": {
                            "icao": "SBJD",
                            "nascer_do_sol": "2026-12-01T09:00:00+00:00",
                            "por_do_sol": "2026-12-01T22:00:00+00:00",
                        },
                        "destino": {
                            "icao": "SBAU",
                            "nascer_do_sol": "2026-12-01T08:30:00+00:00",
                            "por_do_sol": "2026-12-01T22:30:00+00:00",
                        },
                        "pernoite": None,
                        "fonte": "AISWEB sol",
                    },
                    {
                        "ordem": 2,
                        "estado": "disponivel",
                        "etd": "2026-12-02T06:00:00+00:00",
                        "eta": "2026-12-02T07:00:00+00:00",
                        "origem": {
                            "icao": "SBAU",
                            "nascer_do_sol": "2026-12-02T06:00:00+00:00",
                            "por_do_sol": "2026-12-02T22:30:00+00:00",
                        },
                        "destino": {
                            "icao": "SBJD",
                            "nascer_do_sol": "2026-12-02T09:00:00+00:00",
                            "por_do_sol": "2026-12-02T22:00:00+00:00",
                        },
                        "pernoite": {"icao": "SBAU", "data": "2026-12-01"},
                        "fonte": "AISWEB sol",
                    },
                ],
            },
        }
        db.commit()
    finally:
        Sessao.remove()

    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)
    primeira = re.search(
        r'<article[^>]*id="ficha-trecho-1"[^>]*>(.*?)</article>', html, re.S
    )
    segunda = re.search(
        r'<article[^>]*id="ficha-trecho-2"[^>]*>(.*?)</article>', html, re.S
    )

    assert primeira and segunda
    assert "Horário estimado de partida" in primeira.group(1)
    assert ">km<" in primeira.group(1)
    assert "Reserva de combustível" in primeira.group(1)
    assert "Peso do combustível" in primeira.group(1)
    assert "Peso da aeronave" in primeira.group(1)
    assert "Velocidade de planejamento" in primeira.group(1)
    assert "Horário estimado de chegada" in primeira.group(1)
    assert "01/12/2026 10:00 UTC" in primeira.group(1)
    assert "01/12/2026 11:00 UTC" in primeira.group(1)
    assert "Pôr do sol" in primeira.group(1)
    assert "Programação diurna" not in primeira.group(1)
    assert "Programação diurna" not in segunda.group(1)
    assert "02/12/2026 06:00 UTC" in segunda.group(1)
    rota = html[html.index('aria-label="Rota completa"') : html.index('id="mapa"')]
    assert "01/12 10:00" in rota
    assert "01/12 11:00" in rota
    assert "02/12 06:00" in rota
    assert "02/12 07:00" in rota
    assert "01/12/2026 10:00" not in rota
    assert "02/12/2026 07:00" not in rota
    assert " UTC" not in rota
    assert "Pôr do sol (UTC)" in rota
    assert "01/12 22:00" in rota
    assert "02/12 22:30" in rota
    assert "02/12 22:00" in rota
    assert "01/12/2026 22:00" not in rota
    assert "02/12/2026 22:30" not in rota
    assert "Pernoite em SBAU em 01/12/2026. A partida fica no nascer do sol do dia seguinte." in rota
    assert "SBAU" in segunda.group(1)


def test_plano_legacy_e_agenda_indisponivel_nao_inventam_horarios(cliente):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]
    db = Sessao()
    try:
        plano = db.get(PlanoDeVoo, plano_id)
        resultado = dict(plano.resultado)
        resultado.pop("programacao", None)
        plano.resultado = resultado
        db.commit()
    finally:
        Sessao.remove()

    legacy = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)
    detalhe = cliente.get(f"/planos/{plano_id}", headers=JSON).get_json()
    assert "Programação diurna" not in legacy
    assert detalhe["programacao"] == {
        "estado": "nao_calculada",
        "fuso": "UTC",
        "trechos": [],
    }

    db = Sessao()
    try:
        plano = db.get(PlanoDeVoo, plano_id)
        plano.resultado = {
            **plano.resultado,
            "programacao": {
                "estado": "indisponivel",
                "motivo": "dados_solares_indisponiveis",
                "fuso": "UTC",
                "trechos": [],
            },
        }
        db.commit()
    finally:
        Sessao.remove()

    indisponivel = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)
    assert "Programação diurna" not in indisponivel
