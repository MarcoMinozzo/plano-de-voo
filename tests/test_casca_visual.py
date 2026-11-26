import re
from pathlib import Path

from tests.conftest import JSON, cadastrar, plano_valido

PLANTA = "/static/casca/blueprint-airport-runway.jpg"
EMBLEMA = 'alt="Plano de voo"'
MENU = ("Novo voo", "Voos planejados", "Perfil", "Imprimir voo")


def _pagina(cliente, caminho):
    resposta = cliente.get(caminho)
    assert resposta.status_code == 200
    return resposta.get_data(as_text=True)


def test_folha_tailwind_local_e_compilada(cliente):
    html = _pagina(cliente, "/entrar")
    assert 'href="/static/css/tailwind.css"' in html

    folha = Path(__file__).resolve().parents[1] / "static/css/tailwind.css"
    assert folha.is_file()
    assert ".bg-aviation-navy" in folha.read_text(encoding="utf-8")


def test_planta_e_emblema_em_todas_as_paginas(cliente):
    for caminho in ("/entrar", "/cadastro"):
        html = _pagina(cliente, caminho)
        assert PLANTA in html
        assert EMBLEMA in html
        assert 'href="/static/css/tailwind.css"' in html
        if caminho == "/cadastro":
            assert 'name="nome_exibicao"' in html
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    assert criado.status_code == 201
    plano_id = criado.get_json()["id"]
    for caminho in ("/painel", "/planos/novo", "/perfil", f"/planos/{plano_id}"):
        html = _pagina(cliente, caminho)
        assert PLANTA in html
        assert EMBLEMA in html
        assert 'href="/static/css/tailwind.css"' in html
        cabecalho = re.search(r"<header\b[^>]*>(.*?)</header>", html, re.S)
        assert cabecalho is not None
        assert EMBLEMA in cabecalho.group(1)

def test_logo_no_cartao_de_autenticacao_sem_logo_no_cabecalho(cliente):
    for caminho in ("/entrar", "/cadastro"):
        html = _pagina(cliente, caminho)
        cartao = re.search(
            r'<section class="vidro\b[^"]*"[^>]*>(.*?)</section>',
            html,
            re.S,
        )
        cabecalho = re.search(r"<header\b[^>]*>(.*?)</header>", html, re.S)
        assert cartao is not None
        assert cabecalho is not None
        logo = re.search(
            r'<img\b(?=[^>]*src="/static/casca/emblema-plano-de-voo\.png")([^>]*)>',
            cartao.group(1),
        )
        assert logo is not None
        assert 'alt="Plano de voo"' in logo.group(1)
        assert "mx-auto" in logo.group(1)
        largura_esperada = (
            "w-[103.68px]" if caminho == "/entrar" else "w-[86.4px]"
        )
        assert largura_esperada in logo.group(1)
        assert "h-auto" in logo.group(1)
        assert cartao.group(1).index(logo.group(0)) < cartao.group(1).index("<h1>")
        assert EMBLEMA not in cabecalho.group(1)
        assert html.count(EMBLEMA) == 1

def test_vidro_na_entrada_e_no_plano_novo(cliente):
    entrada = _pagina(cliente, "/entrar")
    cadastro = _pagina(cliente, "/cadastro")
    for html in (entrada, cadastro):
        assert 'class="vidro ' in html
        for item in MENU:
            assert item not in html
    assert "Criar acesso" in entrada
    cadastrar(cliente)
    novo = _pagina(cliente, "/planos/novo")
    assert 'class="vidro ' in novo
    assert re.search(
        r'<input\b(?=[^>]*\bname="confirmar_hora")(?=[^>]*\bbg-aviation-white)',
        novo,
    )
    ordem = ["Tipo de avião", "Origem", "Destino", "Data e hora", "Número de passageiros", "Peso das pessoas", "Peso da bagagem"]
    posicao = -1
    for rotulo in ordem:
        achado = novo.index(rotulo)
        assert achado > posicao
        posicao = achado
    assert "combustivel_a_bordo" not in novo
    assert "peso_piloto" not in novo
    assert "Não é autorização de voo." in novo


def test_espera_nao_calcula_voo(cliente):
    cadastrar(cliente)
    html = _pagina(cliente, "/planos/novo")
    assert "Em processamento" in html
    assert 'class="ampulheta ' in html
    inicio = html.index('<script id="espera-voo">')
    fim = html.index("</script>", inicio)
    script = html[inicio:fim].lower()
    for palavra in ("distancia", "combustivel", "vento", "carta", "pdf"):
        assert palavra not in script


def test_menu_resumo_e_impressao(cliente):
    entrada = _pagina(cliente, "/entrar")
    assert "Sair" not in entrada
    cadastrar(cliente)
    novo = _pagina(cliente, "/planos/novo")
    for item in MENU:
        assert item in novo
    assert 'method="post"' in novo
    assert ">Sair<" in novo
    assert 'href="/sair"' not in novo
    assert "Não há voo para imprimir." in novo
    assert "/pdf" not in novo
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    plano_id = criado.get_json()["id"]
    plano = _pagina(cliente, f"/planos/{plano_id}")
    assert f"/planos/{plano_id}/pdf" in plano
    assert re.search(
        rf'<a class="[^"]*text-aviation-white[^"]*" href="/planos/{plano_id}/pdf">Imprimir voo</a>',
        plano,
    )
    resumo = plano.index('id="resumo"')
    abas = plano.index('role="tablist"')
    assert resumo < abas
    fim_resumo = plano.index("</section>", resumo)
    miolo = plano[resumo:fim_resumo].lower()
    assert "técnica" not in miolo
    assert "arremeta" not in miolo
    assert 'role="tabpanel"' in plano
    assert "<h2>Checklist</h2>" not in plano
    assert "Marcar" not in plano
