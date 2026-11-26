import json
import re
import subprocess

from flask import template_rendered

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
    assert html.index("não substitui a carta de voo visual") < html.index('id="mapa"')
    assert "Carta de voo visual indisponível" in html
    assert "Chave REDEMET não configurada." in html
    assert "Como ler este plano" in html


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


def test_mapa_recebe_somente_os_pontos_de_cada_trecho_e_exibe_wac_indisponivel(cliente):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]
    adicionar_trecho_de_retorno(plano_id)
    db = Sessao()
    try:
        aerodromos = {
            aero.icao: [aero.lat, aero.lon]
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
            "pontos": [aerodromos["SBJD"], aerodromos["SBAU"]],
        },
        {
            "ordem": 2,
            "origem": "SBAU",
            "destino": "SBJD",
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
            "pontos": [aerodromos["SBJD"], aerodromos["SBAU"]],
        },
        {
            "ordem": 2,
            "origem": "SBAU",
            "destino": "SBJD",
            "pontos": [aerodromos["SBAU"], aerodromos["SBJD"]],
        },
    ]
    assert 'id="base-wac" type="radio" name="camada-base" value="wac" disabled' in html
    assert "Carta de voo visual indisponível" in html
    assert html.count('id="mapa"') == 1
    assert html.count("L.map(elementoMapa)") == 1
    assert 'ficha-trecho-ativada' in html
    assert "linha.setLatLngs(trecho.pontos)" in html
    assert "Mapa indisponível: coordenadas do trecho não encontradas." in html
    assert "mapa.fitBounds(L.latLngBounds(trecho.pontos)" in html
    assert 'ruasInput.addEventListener("change"' in html
    assert 'radarToggle.addEventListener("change"' in html
    assert 'id="radar-toggle" type="checkbox" checked' not in html


def test_mapa_disponibiliza_openaip_com_atribuicao_e_estado_explicito(cliente, monkeypatch):
    monkeypatch.setenv("OPENAIP_API_KEY", "fake-private-key")
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]

    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)

    assert "Mapa de ruas" in html
    assert "OpenAIP — dados aeronáuticos comunitários; não é carta WAC nem fonte oficial" in html
    assert 'href="https://www.openaip.net"' in html
    assert "Radar de chuva" in html
    assert "fake-private-key" not in html


def test_fichas_mostram_metar_e_taf_dos_aerodromos_do_trecho(cliente):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]
    adicionar_trecho_de_retorno(plano_id)
    db = Sessao()
    try:
        plano = db.get(PlanoDeVoo, plano_id)
        plano.meteorologia = {
            "estado": "disponivel",
            "origem": {"estado": "disponivel"},
            "destino": {"estado": "disponivel"},
            "aerodromos": {
                "SBJD": {
                    "estado": "disponivel",
                    "fonte": "Aviation Weather Center",
                    "metar": {
                        "icao": "SBJD",
                        "raw": "METAR SBJD 011200Z 18010KT 6SM",
                        "hora": "2026-12-01T12:00:00Z",
                        "temp_c": 18,
                        "vento_kt": 10,
                        "unidade_vento": "kt",
                        "fonte": "Aviation Weather Center",
                    },
                    "taf": {"raw": "TAF SBJD 011100Z 18008KT"},
                },
                "SBAU": {
                    "estado": "disponivel",
                    "fonte": "Aviation Weather Center",
                    "metar": {
                        "icao": "SBAU",
                        "raw": "METAR SBAU 011200Z VRB05KT -RA",
                        "hora": "2026-12-01T12:00:00Z",
                        "direcao_vento": "VRB",
                        "fenomenos": "-RA",
                        "fonte": "Aviation Weather Center",
                    },
                    "taf": {"estado": "indisponivel"},
                },
            },
        }
        db.commit()
    finally:
        Sessao.remove()

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
    assert "METAR SBJD 011200Z 18010KT 6SM" in primeira
    assert "METAR SBAU 011200Z VRB05KT -RA" in primeira
    assert "TAF SBJD 011100Z 18008KT" in primeira
    assert "TAF da chegada indisponível" in primeira
    assert "Temperatura" in primeira and "18" in primeira and "°C" in primeira
    assert "Ponto de orvalho" in primeira and "Indisponível" in primeira
    assert "Direção do vento" in primeira and "VRB" in primeira
    assert "Fenômenos meteorológicos (código AWC)" in primeira and "-RA" in primeira
    assert "Aviation Weather Center" in primeira
    assert "2026-12-01T12:00:00Z" in primeira
    assert primeira.index("METAR da saída") < primeira.index("METAR da chegada")
    assert primeira.index("METAR da chegada") < primeira.index("TAF da saída")
    assert primeira.index("TAF da chegada") < primeira.index('id="mapa"')
    assert primeira.index('id="mapa"') < primeira.index("sequence-line")
    assert "METAR SBAU 011200Z VRB05KT -RA" in segunda
    assert "METAR SBJD 011200Z 18010KT 6SM" in segunda
    assert "TAF SBJD 011100Z 18008KT" in segunda


def test_mapa_mantem_openaip_indisponivel_sem_chave(cliente, monkeypatch):
    monkeypatch.delenv("OPENAIP_API_KEY", raising=False)
    monkeypatch.delenv("REDEMET_API_KEY", raising=False)
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]

    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)

    assert 'id="base-ruas" type="radio" name="camada-base" value="ruas" checked' in html
    assert 'id="base-openaip" type="radio" name="camada-base" value="openaip" disabled' in html
    assert "OpenAIP indisponível: chave de serviço não configurada." in html
    assert "Chave REDEMET não configurada." in html
    assert 'id="radar-toggle" type="checkbox" checked' not in html


def test_tabela_de_procedencia_tem_rolagem_horizontal_propria(cliente):
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]

    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)
    area = re.search(
        r'<div class="overflow-x-auto">\s*(<table\b.*?</table>)\s*</div>',
        html,
        re.S,
    )

    assert area
    cabecalhos = re.findall(r"<th(?:\s[^>]*)?>(.*?)</th>", area.group(1), re.S)
    assert cabecalhos == [
        "Grandeza",
        "Valor",
        "Unidade",
        "Faixa",
        "Publicador e referência",
        "Data",
        "Aplicabilidade e perfil",
        "Método/versão",
        "Incerteza/comparabilidade",
        "Edição/revisão",
        "Página/tabela",
    ]


def test_plano_antigo_mostra_indisponibilidade_generica_do_radar(cliente):
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
    estado = re.search(r'<p[^>]*id="estado-radar"[^>]*>(.*?)</p>', html, re.S)

    assert estado
    assert estado.group(1).strip() == "Radar indisponível."


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
