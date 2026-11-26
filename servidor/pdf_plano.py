import re
from io import BytesIO
from pathlib import Path

from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph

from servidor.pdf_layout import (
    _estilos,
    _html,
    _montar_documento,
    _paragrafo,
    _partida_rotulo,
    _rota_completa,
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
}


def rotulo_lido(estado):
    return ROTULOS_LIDOS.get(estado, estado or "")


def ler_orientacao():
    return CAMINHO.read_text(encoding="utf-8")


def trecho_limite():
    texto = ler_orientacao()
    marca = "## Limite do plano"
    if marca not in texto:
        return texto.strip()
    return texto.split(marca, 1)[1].strip()


def _linhas_procedencia(plano):
    linhas = []
    if plano.resultado.get("proxy_sintetico") or plano.resultado.get("dados_sinteticos"):
        linhas.append(
            "perfil sintético didático — valores não validados; "
            "não representam dados do modelo associado"
        )
        if plano.resultado.get("modelo_alvo"):
            linhas.append(
                f"Alvo do exercício: {plano.resultado['modelo_alvo']}. "
                "A associação temática não comprova aplicabilidade."
            )
    elif plano.resultado.get("estimativa_didatica"):
        linhas.append(
            "Estimativas didáticas: não são adequadas para planejamento de voo real "
            "e não autorizam o voo."
        )
    for campo, fonte in (plano.resultado.get("procedencia") or {}).items():
        if fonte is None:
            linhas.append(f"{campo}: indisponível")
            continue
        sintetica = fonte.get("dados_sinteticos", False)
        if sintetica:
            linhas.append(
                f"Dados sintéticos didáticos — {campo}: "
                f"{fonte['valor']} {fonte['unidade']}; valor não validado."
            )
            continue
        rotulo = "Estimativa didática — " if fonte["estimativa_didatica"] else ""
        data_publicacao = fonte.get("data_publicacao") or "indisponível"
        linhas.append(
            f"{rotulo}{campo}: {fonte['valor']} {fonte['unidade']} "
            f"— {fonte['publicador']}; {fonte['referencia']}; "
            f"publicação: {data_publicacao}; "
            f"consulta: {fonte['data_consulta'] or 'indisponível'}; "
            f"aplicabilidade: {fonte['modelo_variante']}; "
            f"perfil: {fonte['perfil'] or 'não aplicável'}; "
            f"edição/revisão: {fonte['revisao_edicao'] or 'não informada'}; "
            f"página/tabela: {fonte['pagina_tabela'] or 'não informada'}"
        )
    return linhas


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


def _conteudo_relatorio(plano, estilos):
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
        for trecho in plano.trechos:
            flowables.append(
                Paragraph(
                    f"{trecho.ordem}. {trecho.origem_icao} > {trecho.destino_icao}",
                    estilos["subsection"],
                )
            )
            flowables.append(
                _tabela_pares(
                    [
                        (
                            "Distância",
                            f"{trecho.distancia_valor} {trecho.distancia_unidade} — "
                            f"{trecho.distancia_fonte}",
                        ),
                        (
                            "Proa",
                            f"{trecho.proa_valor} {trecho.proa_unidade} — "
                            f"{trecho.proa_fonte}",
                        ),
                        (
                            "Tempo",
                            f"{trecho.tempo_valor} {trecho.tempo_unidade} — "
                            f"{trecho.tempo_fonte}",
                        ),
                        (
                            "Combustível",
                            f"{trecho.combustivel_valor} {trecho.combustivel_unidade} — "
                            f"{trecho.combustivel_fonte}",
                        ),
                        ("Vento", rotulo_lido(trecho.vento_estado)),
                        ("Pôr do sol", rotulo_lido(trecho.por_do_sol_estado)),
                    ],
                    estilos,
                )
            )

    procedencia = _linhas_procedencia(plano)
    if procedencia:
        flowables.append(Paragraph("Fontes técnicas da aeronave", estilos["section"]))
        flowables.extend(_paragrafo(linha, estilos["small"]) for linha in procedencia)

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
            f"{vento.get('velocidade_kt')} {vento.get('unidade', 'kt')} "
            f"({vento.get('fonte', '')})"
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
        if camada.get("fonte"):
            descricao += f" — fonte: {camada['fonte']}"
        flowables.append(_paragrafo(descricao, estilos["body"]))

    flowables.append(Paragraph("Checklist sugerido", estilos["section"]))
    if plano.itens:
        flowables.extend(
            Paragraph(
                f"<bullet>&bull;</bullet>{_html(item.texto)} "
                f"<font color='#52677F'>— fonte: {_html(item.fonte)}</font>",
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
    return flowables


def gerar_pdf(plano, nome_piloto):
    buffer = BytesIO()
    estilos = _estilos()
    conteudo = _conteudo_relatorio(plano, estilos)
    _montar_documento(
        buffer,
        plano,
        nome_piloto,
        conteudo,
        estilos,
        rotulo_lido,
    )
    return buffer.getvalue()
