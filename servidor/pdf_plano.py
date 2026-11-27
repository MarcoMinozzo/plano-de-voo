import re
from io import BytesIO
from pathlib import Path

from reportlab.platypus import PageBreak, Paragraph

from servidor.pdf_layout import (
    _estilos,
    _html,
    _montar_documento,
    _paragrafo,
    _partida_rotulo,
    _rota_completa,
    _tabela_fontes,
    _tabela_pares,
    _tabela_resultados,
)
from servidor.tempo import linhas_boletim

CAMINHO = Path(__file__).resolve().parent.parent / "documentacao" / "piloto.md"

ROTULOS_LIDOS = {
    "calculado": "aceitável para planejamento",
    "inaceitavel": "não aceitável",
    "aceitavel": "aceitável para planejamento",
    "indisponivel": "indisponível",
    "disponivel": "disponível",
    "nao_fornecido_pela_fonte": "não fornecido pela fonte",
}


def rotulo_lido(estado):
    return ROTULOS_LIDOS.get(estado, estado or "")


def ler_orientacao():
    return CAMINHO.read_text(encoding="utf-8")


def ler_orientacao_plano():
    texto = ler_orientacao()
    return re.sub(
        r"(?ms)^## Perfis sintéticos didáticos\s*\n.*?(?=^## |\Z)",
        "",
        texto,
    ).strip()


def trecho_limite():
    texto = ler_orientacao()
    marca = "## Limite do plano"
    if marca not in texto:
        return texto.strip()
    return texto.split(marca, 1)[1].strip()


def _markdown_flowables(texto, estilos):
    flowables = []
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha or linha in ("---", "***"):
            continue
        if linha.startswith("#"):
            nivel = len(linha) - len(linha.lstrip("#"))
            titulo = linha[nivel:].strip()
            if nivel == 1 and titulo.casefold() == "plano de voo":
                continue
            estilo = estilos["section"] if nivel <= 2 else estilos["subsection"]
            flowables.append(Paragraph(_html(titulo), estilo))
        elif linha.startswith(("- ", "* ")):
            flowables.append(
                Paragraph(f"<bullet>&bull;</bullet>{_html(linha[2:])}", estilos["bullet"])
            )
        elif re.fullmatch(r"\|?[\s|:-]+\|?", linha):
            continue
        else:
            texto_formatado = _html(linha)
            texto_formatado = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto_formatado)
            texto_formatado = re.sub(
                r"`([^`]+)`", r'<font name="Courier">\1</font>', texto_formatado
            )
            texto_formatado = re.sub(
                r"\[([^\]]+)\]\((https?://[^)]+)\)",
                r'<link href="\2" color="#0090F0">\1</link>',
                texto_formatado,
            )
            flowables.append(Paragraph(texto_formatado, estilos["body"]))
    return flowables


def _conteudo_relatorio(plano, estilos, fontes_relatorio=None, aerodromos=None):
    aerodromos = aerodromos or {}
    flowables = [
        Paragraph("Resumo do voo", estilos["section"]),
        _tabela_pares(
            [
                ("Rota", _rota_completa(plano)),
                ("Partida", _partida_rotulo(plano.hora_partida)),
                ("Estado", rotulo_lido(plano.estado)),
            ]
            + ([("Motivo", plano.motivo)] if plano.motivo else [])
            + (
                [("Reabastecimento", plano.hipotese_reabastecimento)]
                if plano.hipotese_reabastecimento
                else []
            ),
            estilos,
        ),
    ]

    if aerodromos:
        flowables.append(
            Paragraph("Aeródromos de origem e destino", estilos["section"])
        )
        for papel, icao in (
            ("Origem", plano.origem_icao),
            ("Destino", plano.destino_icao),
        ):
            aerodromo = aerodromos.get(icao)
            contatos_verificados = bool(
                getattr(aerodromo, "contatos_rotaer_verificados", False)
            )
            flowables.append(
                Paragraph(
                    f"{_html(getattr(aerodromo, 'nome', 'Nome indisponível'))} "
                    f"({icao}) — {papel}",
                    estilos["subsection"],
                )
            )
            flowables.append(
                _tabela_pares(
                    [
                        ("Tipo", getattr(aerodromo, "tipo", None) or "Indisponível"),
                        (
                            "Coordenadas",
                            (
                                f"{aerodromo.lat}, {aerodromo.lon}"
                                if aerodromo is not None
                                else "Indisponível"
                            ),
                        ),
                        ("Elevação (m)", getattr(aerodromo, "elev_m", None) or "Indisponível"),
                        (
                            "Telefone publicado",
                            (
                                getattr(aerodromo, "telefone", None)
                                if contatos_verificados
                                else None
                            )
                            or "Indisponível",
                        ),
                        (
                            "E-mail publicado",
                            (
                                getattr(aerodromo, "email", None)
                                if contatos_verificados
                                else None
                            )
                            or "Indisponível",
                        ),
                    ],
                    estilos,
                )
            )

    if plano.aviso:
        flowables.append(
            Paragraph(
                f"<b>Aviso:</b> {_html(plano.aviso)}",
                estilos["body"],
            )
        )
    if plano.resultado.get("alertas"):
        flowables.append(Paragraph("Alertas", estilos["subsection"]))
        flowables.extend(
            Paragraph(
                f"<bullet>&bull;</bullet>{_html(alerta)}",
                estilos["bullet"],
            )
            for alerta in plano.resultado["alertas"]
        )

    if plano.trechos:
        flowables.append(Paragraph("Trechos", estilos["section"]))
        programacao = plano.resultado.get("programacao")
        agendas = (
            programacao.get("trechos", [])
            if isinstance(programacao, dict)
            else []
        )
        agendas_por_ordem = {
            agenda.get("ordem"): agenda
            for agenda in agendas
            if isinstance(agenda, dict)
        }
        for trecho in plano.trechos:
            origem = aerodromos.get(trecho.origem_icao)
            destino = aerodromos.get(trecho.destino_icao)
            flowables.append(
                Paragraph(
                    f"{trecho.ordem}. "
                    f"{_html(getattr(origem, 'nome', 'Nome indisponível'))} "
                    f"({trecho.origem_icao}) &gt; "
                    f"{_html(getattr(destino, 'nome', 'Nome indisponível'))} "
                    f"({trecho.destino_icao})",
                    estilos["subsection"],
                )
            )
            flowables.append(
                _tabela_pares(
                    [
                        (
                            "Distância",
                            f"{trecho.distancia_valor} {trecho.distancia_unidade}",
                        ),
                        (
                            "Proa",
                            f"{trecho.proa_valor} {trecho.proa_unidade}",
                        ),
                        (
                            "Tempo",
                            f"{trecho.tempo_valor} {trecho.tempo_unidade}",
                        ),
                        (
                            "Combustível",
                            f"{trecho.combustivel_valor} {trecho.combustivel_unidade}",
                        ),
                        ("Vento", rotulo_lido(trecho.vento_estado)),
                        ("Pôr do sol", rotulo_lido(trecho.por_do_sol_estado)),
                    ],
                    estilos,
                )
            )
            agenda = agendas_por_ordem.get(trecho.ordem)
            if not isinstance(programacao, dict) or programacao.get("estado") == "nao_calculada":
                linhas_programacao = [
                    ("Programação diurna", "Não calculada.")
                ]
            elif agenda and agenda.get("estado") == "disponivel":
                solar_origem = agenda.get("origem") or {}
                solar_destino = agenda.get("destino") or {}
                linhas_programacao = [
                    ("Partida estimada (ETD, UTC)", agenda.get("etd") or "Indisponível"),
                    ("Chegada estimada (ETA, UTC)", agenda.get("eta") or "Indisponível"),
                    (
                        f"Nascer do sol — {trecho.origem_icao} (UTC)",
                        solar_origem.get("nascer_do_sol") or "Indisponível",
                    ),
                    (
                        f"Pôr do sol — {trecho.origem_icao} (UTC)",
                        solar_origem.get("por_do_sol") or "Indisponível",
                    ),
                    (
                        f"Nascer do sol — {trecho.destino_icao} (UTC)",
                        solar_destino.get("nascer_do_sol") or "Indisponível",
                    ),
                    (
                        f"Pôr do sol — {trecho.destino_icao} (UTC)",
                        solar_destino.get("por_do_sol") or "Indisponível",
                    ),
                ]
                pernoite = agenda.get("pernoite")
                if pernoite:
                    linhas_programacao.append(
                        (
                            "Pernoite",
                            f"{pernoite.get('icao', 'Indisponível')} — "
                            f"{pernoite.get('data', 'Data indisponível')}",
                        )
                    )
            else:
                linhas_programacao = [
                    ("Programação diurna", "Indisponível para este trecho.")
                ]
            flowables.append(_tabela_pares(linhas_programacao, estilos))

    linhas_resultado = plano.resultado.get("linhas", [])
    if linhas_resultado:
        flowables.append(Paragraph("Resultados técnicos", estilos["section"]))
        flowables.append(_tabela_resultados(linhas_resultado, estilos))

    flowables.append(Paragraph("Tempo, vento, carta e radar", estilos["section"]))
    boletins = linhas_boletim(plano.meteorologia or {})
    if boletins:
        flowables.extend(_paragrafo(linha, estilos["body"]) for linha in boletins)
    else:
        flowables.append(_paragrafo("Tempo: indisponível.", estilos["body"]))

    vento = plano.vento or {}
    if vento.get("estado") == "disponivel":
        texto_vento = (
            f"Vento: {vento.get('direcao_de_graus')} graus, "
            f"{vento.get('velocidade_kt')} {vento.get('unidade', 'kt')}"
        )
        if vento.get("efeito"):
            texto_vento += f" — {vento['efeito']}"
    else:
        texto_vento = "Vento: indisponível."
    flowables.append(_paragrafo(texto_vento, estilos["body"]))

    for rotulo, camada in (
        ("Carta de voo visual", plano.carta or {}),
        ("Radar de chuva", plano.radar or {}),
    ):
        descricao = f"{rotulo}: {rotulo_lido(camada.get('estado', 'indisponivel'))}"
        flowables.append(_paragrafo(descricao, estilos["body"]))

    flowables.append(Paragraph("Checklist sugerido", estilos["section"]))
    if plano.itens:
        flowables.extend(
            Paragraph(
                f"<bullet>&bull;</bullet>{_html(item.texto)}",
                estilos["bullet"],
            )
            for item in plano.itens
        )
    else:
        flowables.append(_paragrafo("Não há itens de checklist sugeridos.", estilos["body"]))

    flowables.extend(_markdown_flowables(ler_orientacao(), estilos))
    if plano.resultado.get("proxy_sintetico") or plano.resultado.get("dados_sinteticos"):
        flowables.append(
            Paragraph("Aviso sobre dados didáticos", estilos["section"])
        )
        flowables.append(
            _paragrafo(
                "Cálculos e dados dos perfis sintéticos são exclusivamente didáticos: "
                "valores não validados, que não representam dados do modelo associado. "
                "Não substituem o manual da aeronave, o treinamento de voo nem a norma "
                "vigente; não são adequados para planejamento de voo real e não "
                "autorizam o voo.",
                estilos["body"],
            )
        )
    if fontes_relatorio:
        linhas_fontes = [
            {**linha, "estado": rotulo_lido(linha["estado"])}
            for linha in fontes_relatorio
        ]
        flowables.extend(
            (
                PageBreak(),
                Paragraph("Fontes do relatório", estilos["section"]),
                _tabela_fontes(linhas_fontes, estilos),
            )
        )
    return flowables


def gerar_pdf(plano, nome_piloto, aerodromos=None, fontes_relatorio=None):
    buffer = BytesIO()
    estilos = _estilos()
    conteudo = _conteudo_relatorio(
        plano,
        estilos,
        fontes_relatorio=fontes_relatorio,
        aerodromos=aerodromos,
    )
    _montar_documento(
        buffer,
        plano,
        nome_piloto,
        conteudo,
        estilos,
        rotulo_lido,
    )
    return buffer.getvalue()
