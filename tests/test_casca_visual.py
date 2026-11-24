from tests.conftest import JSON, cadastrar, plano_valido

PLANTA = "/static/casca/blueprint-airport-runway.jpg"
EMBLEMA = 'alt="Plano de voo"'
MENU = ("Novo voo", "Voos planejados", "Imprimir voo")


def _pagina(cliente, caminho):
    resposta = cliente.get(caminho)
    assert resposta.status_code == 200
    return resposta.get_data(as_text=True)


def test_planta_e_emblema_em_todas_as_paginas(cliente):
    for caminho in ("/entrar", "/cadastro"):
        html = _pagina(cliente, caminho)
        assert PLANTA in html
        assert EMBLEMA in html
    cadastrar(cliente)
    criado = cliente.post("/planos", json=plano_valido(), headers=JSON)
    assert criado.status_code == 201
    plano_id = criado.get_json()["id"]
    for caminho in ("/painel", "/planos/novo", f"/planos/{plano_id}"):
        html = _pagina(cliente, caminho)
        assert PLANTA in html
        assert EMBLEMA in html


def test_vidro_na_entrada_e_no_plano_novo(cliente):
    entrada = _pagina(cliente, "/entrar")
    cadastro = _pagina(cliente, "/cadastro")
    for html in (entrada, cadastro):
        assert 'class="vidro"' in html
        for item in MENU:
            assert item not in html
    assert "Criar acesso" in entrada
    cadastrar(cliente)
    novo = _pagina(cliente, "/planos/novo")
    assert 'class="vidro"' in novo
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
    assert 'class="ampulheta"' in html
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
    resumo = plano.index('id="resumo"')
    trechos = plano.index("<h2>Trechos</h2>")
    assert resumo < trechos
    miolo = plano[resumo:trechos].lower()
    assert "técnica" not in miolo
    assert "arremeta" not in miolo
