import re

from reportlab.platypus import PageBreak, Table

from tests.conftest import JSON, cadastrar
from tests.conftest_rota import preparar_rota
from tests.conftest_rota import semear_perfis_sinteticos_teste
from servidor import tempo as tempo_mod
from servidor.modelos import Aerodromo, PlanoDeVoo, Sessao
from servidor.pdf_layout import _estilos
from servidor.pdf_plano import _conteudo_relatorio
from servidor.planos_consulta import construir_fontes_relatorio


def _pedido(aeronave_id):
    return {
        "aeronave_id": aeronave_id,
        "origem": "S0A1",
        "destino": "S0C3",
        "hora_partida": "2026-12-01T12:00:00+00:00",
        "numero_passageiros": 1,
        "peso_pessoas_kg": 80,
        "peso_bagagem_kg": 5,
    }


def test_html_e_pdf_trazem_trecho_reabastecimento_e_aviso(cliente):
    cadastrar(cliente)
    ids = preparar_rota()
    criado = cliente.post("/planos", json=_pedido(ids["alfa"]), headers=JSON)
    assert criado.status_code == 201
    plano_id = criado.get_json()["id"]
    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)
    assert "S0B2" in html
    assert "reabastec" in html.lower()
    assert "Uso exclusivamente didático. Este resultado não serve para planejamento de voo real. Não é autorização de voo." not in html
    assert "0.539" not in html
    pdf = cliente.get(f"/planos/{plano_id}/pdf").data
    assert b"S0B2" in pdf
    assert b"reabastec" in pdf or "reabastec".encode("utf-16-be") in pdf
    assert b"autoriza" in pdf or "autoriza".encode("utf-16-be") in pdf


def test_pdf_de_plano_de_outro_piloto_e_recusado(cliente):
    cadastrar(cliente)
    ids = preparar_rota()
    criado = cliente.post("/planos", json=_pedido(ids["alfa"]), headers=JSON)
    plano_id = criado.get_json()["id"]
    outro_piloto = cliente.application.test_client()
    cadastrar(outro_piloto, identificacao="bia")

    resposta = outro_piloto.get(f"/planos/{plano_id}/pdf", headers=JSON)

    assert resposta.status_code == 404
    assert resposta.get_json()["mensagem"] == "Acesso recusado."
    assert not resposta.data.startswith(b"%PDF")


def test_capa_pdf_identifica_piloto_rota_data_e_emblema(cliente):
    cadastrar(cliente, nome_exibicao="Marina Costa")
    alterado = cliente.post(
        "/perfil",
        json={"nome_exibicao": "Marina Atualizada"},
        headers=JSON,
    )
    assert alterado.status_code == 200
    ids = preparar_rota()
    criado = cliente.post("/planos", json=_pedido(ids["alfa"]), headers=JSON)
    plano_id = criado.get_json()["id"]

    resposta = cliente.get(f"/planos/{plano_id}/pdf")
    pdf = resposta.data

    assert resposta.status_code == 200
    assert resposta.mimetype == "application/pdf"
    assert b"Marina Atualizada" in pdf
    assert b"Marina Costa" not in pdf
    assert b"S0A1" in pdf
    assert b"S0B2" in pdf
    assert b"S0C3" in pdf
    assert b"01/12/2026" in pdf
    assert b"12:00 UTC" in pdf
    assert b"/Subtype /Image" in pdf
    assert b"[x]" not in pdf
    assert b"[ ]" not in pdf
    assert len(re.findall(rb"/Type\s*/Page\b", pdf)) >= 2


def test_pdf_apresenta_apendice_de_fontes_e_so_contatos_verificados(
    cliente, monkeypatch
):
    monkeypatch.setattr(
        tempo_mod,
        "meteorologia_rota",
        lambda *args, **kwargs: {
            "estado": "indisponivel",
            "origem": {"estado": "indisponivel"},
            "destino": {"estado": "indisponivel"},
            "aerodromos": {},
        },
    )
    cadastrar(cliente)
    ids = preparar_rota()
    criado = cliente.post("/planos", json=_pedido(ids["alfa"]), headers=JSON)
    plano_id = criado.get_json()["id"]

    db = Sessao()
    try:
        origem = db.get(Aerodromo, "S0A1")
        origem.telefone = "(11) 5555-0101"
        origem.email = "operacoes@origem.example"
        origem.contatos_rotaer_verificados = True
        origem.fonte = "ROTAER AISWEB"
        destino = db.get(Aerodromo, "S0C3")
        destino.telefone = "(11) 5555-0303"
        destino.email = "contato@destino.example"
        destino.contatos_rotaer_verificados = False
        plano = db.get(PlanoDeVoo, plano_id)
        boletim_regional = {
            "estado": "disponivel",
            "fonte": "Aviation Weather Center",
            "metar": {
                "icao": "SBST",
                "nome_estacao": "Estação regional de teste",
                "raw": "METAR SBST 011200Z",
                "hora": "2026-12-01T12:00:00Z",
                "regional": True,
                "aerodromo_referencia": "S0A1",
                "distancia_nm": 32.4,
                "fonte": "Aviation Weather Center",
            },
        }
        plano.meteorologia = {
            "estado": "disponivel",
            "origem": boletim_regional,
            "destino": {"estado": "indisponivel"},
            "aerodromos": {
                "S0A1": boletim_regional,
                "S0C3": {"estado": "indisponivel"},
            },
        }
        aerodromos = {"S0A1": origem, "S0C3": destino}
        fontes = construir_fontes_relatorio(plano, aerodromos, plano.meteorologia)
        conteudo = _conteudo_relatorio(
            plano,
            _estilos(),
            fontes_relatorio=fontes,
            aerodromos=aerodromos,
        )
        texto_relatorio = " ".join(
            item.getPlainText()
            for item in conteudo
            if hasattr(item, "getPlainText")
        )
        indice_apendice = next(
            indice
            for indice, item in enumerate(conteudo)
            if hasattr(item, "getPlainText")
            and item.getPlainText() == "Fontes do relatório"
        )
        assert isinstance(conteudo[indice_apendice - 1], PageBreak)
        assert isinstance(conteudo[indice_apendice + 1], Table)
        valores_fontes = [
            celula.getPlainText()
            for flowable in conteudo
            if isinstance(flowable, Table)
            for linha in flowable._cellvalues
            for celula in linha
            if hasattr(celula, "getPlainText")
        ]
        db.commit()
    finally:
        Sessao.remove()

    resposta = cliente.get(f"/planos/{plano_id}/pdf")

    assert resposta.status_code == 200
    assert b"Fontes do relat" in resposta.data
    assert any("ROTAER AISWEB" in valor for valor in valores_fontes)
    assert "(11) 5555-0101" in valores_fontes
    assert "operacoes@origem.example" in valores_fontes
    assert "(11) 5555-0303" not in valores_fontes
    assert "contato@destino.example" not in valores_fontes
    assert "METAR regional" in texto_relatorio
    assert "Estação regional de teste" in texto_relatorio
    assert any("METAR regional" in valor and "SBST" in valor for valor in valores_fontes)
    assert any("32.4 NM" in valor for valor in valores_fontes)


def test_pdf_apresenta_programacao_utc_por_trecho_e_pernoite(cliente):
    cadastrar(cliente)
    ids = preparar_rota()
    criado = cliente.post("/planos", json=_pedido(ids["alfa"]), headers=JSON)
    plano_id = criado.get_json()["id"]
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
                            "icao": "S0A1",
                            "nascer_do_sol": "2026-12-01T09:00:00+00:00",
                            "por_do_sol": "2026-12-01T22:00:00+00:00",
                        },
                        "destino": {
                            "icao": "S0B2",
                            "nascer_do_sol": "2026-12-01T08:30:00+00:00",
                            "por_do_sol": "2026-12-01T22:30:00+00:00",
                        },
                        "pernoite": None,
                    },
                    {
                        "ordem": 2,
                        "estado": "disponivel",
                        "etd": "2026-12-02T06:00:00+00:00",
                        "eta": "2026-12-02T07:00:00+00:00",
                        "origem": {
                            "icao": "S0B2",
                            "nascer_do_sol": "2026-12-02T06:00:00+00:00",
                            "por_do_sol": "2026-12-02T22:30:00+00:00",
                        },
                        "destino": {
                            "icao": "S0C3",
                            "nascer_do_sol": "2026-12-02T09:00:00+00:00",
                            "por_do_sol": "2026-12-02T22:00:00+00:00",
                        },
                        "pernoite": {"icao": "S0B2", "data": "2026-12-01"},
                    },
                ],
            },
        }
        aerodromos = {
            icao: db.get(Aerodromo, icao) for icao in ("S0A1", "S0B2", "S0C3")
        }
        fontes = construir_fontes_relatorio(plano, aerodromos, plano.meteorologia)
        conteudo = _conteudo_relatorio(
            plano,
            _estilos(),
            fontes_relatorio=fontes,
            aerodromos=aerodromos,
        )
        textos = [
            celula.getPlainText()
            for item in conteudo
            if isinstance(item, Table)
            for linha in item._cellvalues
            for celula in linha
            if hasattr(celula, "getPlainText")
        ]
        textos.extend(
            item.getPlainText()
            for item in conteudo
            if hasattr(item, "getPlainText")
        )
        db.commit()
    finally:
        Sessao.remove()

    resposta = cliente.get(f"/planos/{plano_id}/pdf")

    assert resposta.status_code == 200
    assert any("2026-12-01T10:00:00+00:00" in texto for texto in textos)
    assert any("2026-12-02T07:00:00+00:00" in texto for texto in textos)
    assert any("Nascer do sol" in texto for texto in textos)
    assert any("Pôr do sol" in texto for texto in textos)
    assert any("Pernoite" in texto for texto in textos)
    assert any("S0B2" in texto for texto in textos)
    assert any("01/12/2026" in texto for texto in textos)


def test_pdf_identifica_fonte_e_validade_do_taf_redemet(cliente, monkeypatch):
    monkeypatch.setattr(
        tempo_mod,
        "meteorologia_rota",
        lambda *args, **kwargs: {
            "estado": "indisponivel",
            "origem": {"estado": "indisponivel"},
            "destino": {"estado": "indisponivel"},
            "aerodromos": {},
        },
    )
    cadastrar(cliente)
    ids = preparar_rota()
    criado = cliente.post("/planos", json=_pedido(ids["alfa"]), headers=JSON)
    plano_id = criado.get_json()["id"]

    db = Sessao()
    try:
        plano = db.get(PlanoDeVoo, plano_id)
        plano.meteorologia = {
            "estado": "disponivel",
            "aerodromos": {
                "S0A1": {
                    "estado": "disponivel",
                    "taf": {
                        "raw": "TAF S0A1 270400Z 2706/2718 19010KT",
                        "fonte": "REDEMET",
                        "hora": "2026-11-27 04:20:00",
                        "validade_inicial": "2026-11-27 06:00:00",
                        "validade_final": "2026-11-27 18:00:00",
                    },
                },
            },
        }
        aerodromos = {
            icao: db.get(Aerodromo, icao) for icao in ("S0A1", "S0C3")
        }
        fontes = construir_fontes_relatorio(plano, aerodromos, plano.meteorologia)
        taf_fonte = next(fonte for fonte in fontes if fonte["campo"] == "S0A1 — TAF")
        assert taf_fonte["fonte"] == "REDEMET"
        assert taf_fonte["data"] == (
            "Emissão: 2026-11-27 04:20:00 UTC; "
            "Validade: 2026-11-27 06:00:00 UTC a 2026-11-27 18:00:00 UTC"
        )
        conteudo = _conteudo_relatorio(
            plano,
            _estilos(),
            fontes_relatorio=fontes,
            aerodromos=aerodromos,
        )
        texto_fontes = [
            celula.getPlainText()
            for item in conteudo
            if isinstance(item, Table)
            for linha in item._cellvalues
            for celula in linha
            if hasattr(celula, "getPlainText")
        ]
        assert any("Validade: 2026-11-27 06:00:00 UTC" in texto for texto in texto_fontes)
        db.commit()
    finally:
        Sessao.remove()

    resposta = cliente.get(f"/planos/{plano_id}/pdf")

    assert resposta.status_code == 200
    assert b"REDEMET" in resposta.data
    assert b"2026-11-27 04:20:00" in resposta.data


def test_perfil_sintetico_preserva_rotulo_no_resultado_e_no_pdf(cliente):
    cadastrar(cliente)
    preparar_rota()
    db = Sessao()
    try:
        ids = semear_perfis_sinteticos_teste(db)
    finally:
        Sessao.remove()

    aeronave_id = ids["CESSNA AIRCRAFT 152"]
    criado = cliente.post("/planos", json=_pedido(aeronave_id), headers=JSON)
    assert criado.status_code == 201
    plano_id = criado.get_json()["id"]

    html = cliente.get(f"/planos/{plano_id}").get_data(as_text=True)
    pdf = cliente.get(f"/planos/{plano_id}/pdf").data
    db = Sessao()
    try:
        plano = db.query(PlanoDeVoo).filter_by(id=plano_id).one()
        procedencia = plano.resultado["procedencia"]["velocidade_cruzeiro"]
        assert plano.resultado["proxy_sintetico"] is True
        assert plano.resultado["modelo_alvo"] == "CESSNA AIRCRAFT 152"
        assert procedencia["dados_sinteticos"] is True
        assert procedencia["unidade"] == "kt"
        assert procedencia["valor"] == 100
        conteudo = _conteudo_relatorio(
            plano,
            _estilos(),
            fontes_relatorio=construir_fontes_relatorio(plano),
        )
    finally:
        Sessao.remove()

    assert "Estado: aceitável para planejamento" not in html
    assert "perfil sintético didático — valores não validados" not in html
    assert "Alvo do exercício:" not in html
    assert "Em cada escala, a hipótese é reabastecer" not in html
    assert "<h2>Fontes técnicas da aeronave</h2>" not in html
    assert "Aeronave: CESSNA AIRCRAFT 152." in html
    assert "aeronaves/cessna-152.jpg" in html
    assert "Md Shaifuzzaman Ayon" in html
    assert "CC BY-SA 4.0" not in html
    assert "Foto ilustrativa" not in html
    assert "Uso exclusivamente didático. Este resultado não serve para planejamento de voo real. Não é autorização de voo." not in html
    assert "CESSNA AIRCRAFT 152" in html
    assert "faixa de teste" not in html
    assert "DEMO" not in html
    assert b"DEMO" not in pdf
    textos_paragrafos = [
        item.getPlainText()
        for item in conteudo
        if hasattr(item, "getPlainText")
    ]
    textos_tabelas = [
        celula.getPlainText()
        for item in conteudo
        if isinstance(item, Table)
        for linha in item._cellvalues
        for celula in linha
        if hasattr(celula, "getPlainText")
    ]
    assert any("Dados sintéticos didáticos" in texto for texto in textos_tabelas)
    assert any(
        "Cálculos e dados dos perfis sintéticos são exclusivamente didáticos"
        in texto
        for texto in textos_paragrafos
    )
    assert any(texto == (
        "Cálculos e dados dos perfis sintéticos são exclusivamente didáticos: "
        "valores não validados, que não representam dados do modelo associado. "
        "Não substituem o manual da aeronave, o treinamento de voo nem a norma "
        "vigente; não são adequados para planejamento de voo real e não autorizam "
        "o voo."
    ) for texto in textos_paragrafos)
