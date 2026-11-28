from datetime import timezone
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Table,
    TableStyle,
)

RAIZ = Path(__file__).resolve().parent.parent
EMBLEMA = RAIZ / "static" / "casca" / "emblema-plano-de-voo.png"

NAVY = colors.HexColor("#001030")
SKY = colors.HexColor("#0090F0")
GOLD = colors.HexColor("#F0A000")
PAPER = colors.HexColor("#F4F7FB")
INK = colors.HexColor("#182B42")
MUTED = colors.HexColor("#52677F")
GRID = colors.HexColor("#CBD5E1")


def _estilos():
    base = getSampleStyleSheet()
    return {
        "body": ParagraphStyle(
            "PlanoBody",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=INK,
            spaceAfter=4,
            splitLongWords=1,
        ),
        "small": ParagraphStyle(
            "PlanoSmall",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.5,
            leading=10,
            textColor=INK,
            splitLongWords=1,
        ),
        "label": ParagraphStyle(
            "PlanoLabel",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=MUTED,
            splitLongWords=1,
        ),
        "section_bar": ParagraphStyle(
            "PlanoSectionBar",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=14,
            textColor=colors.white,
            spaceBefore=0,
            spaceAfter=0,
        ),
        "section": ParagraphStyle(
            "PlanoSection",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=16,
            textColor=NAVY,
            spaceBefore=10,
            spaceAfter=6,
            keepWithNext=True,
        ),
        "subsection": ParagraphStyle(
            "PlanoSubsection",
            parent=base["Heading3"],
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=13,
            textColor=NAVY,
            spaceBefore=7,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "bullet": ParagraphStyle(
            "PlanoBullet",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=8.5,
            leading=11,
            textColor=INK,
            leftIndent=10,
            firstLineIndent=-8,
            spaceAfter=3,
            splitLongWords=1,
        ),
        "table": ParagraphStyle(
            "PlanoTable",
            parent=base["BodyText"],
            fontName="Helvetica",
            fontSize=7.4,
            leading=9.4,
            textColor=INK,
            splitLongWords=1,
        ),
        "table_head": ParagraphStyle(
            "PlanoTableHead",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=9,
            textColor=colors.white,
        ),
        "cover_name": ParagraphStyle(
            "PlanoCoverName",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=19,
            leading=23,
            textColor=NAVY,
            splitLongWords=1,
        ),
        "cover_route": ParagraphStyle(
            "PlanoCoverRoute",
            parent=base["BodyText"],
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=19,
            textColor=NAVY,
            splitLongWords=1,
        ),
    }


def _html(texto):
    return escape(str(texto if texto is not None else "")).replace("\n", "<br/>")


def _paragrafo(texto, estilo):
    return Paragraph(_html(texto), estilo)


def _estilo_grade(com_cabecalho):
    comandos = [
        ("GRID", (0, 0), (-1, -1), 0.4, GRID),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if com_cabecalho:
        comandos.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PAPER]),
            ]
        )
    else:
        comandos.append(("BACKGROUND", (0, 0), (-1, -1), PAPER))
    return TableStyle(comandos)


def _titulo_secao(texto, estilos):
    tabela = Table(
        [[Paragraph(_html(texto), estilos["section_bar"])]],
        colWidths=[176 * mm],
        hAlign="LEFT",
    )
    tabela.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), NAVY),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    tabela.spaceBefore = 10
    tabela.spaceAfter = 6
    return tabela


def _tabela_grade(cabecalho, linhas, estilos, larguras):
    dados = [[_paragrafo(valor, estilos["table_head"]) for valor in cabecalho]]
    dados.extend(
        [_paragrafo(valor, estilos["table"]) for valor in linha] for linha in linhas
    )
    tabela = Table(
        dados,
        colWidths=larguras,
        repeatRows=1,
        hAlign="LEFT",
        splitByRow=1,
    )
    tabela.setStyle(_estilo_grade(True))
    return tabela


def _tabela_pares(linhas, estilos):
    dados = [
        [_paragrafo(rotulo, estilos["label"]), _paragrafo(valor, estilos["body"])]
        for rotulo, valor in linhas
    ]
    tabela = Table(
        dados,
        colWidths=[34 * mm, 142 * mm],
        hAlign="LEFT",
        splitByRow=1,
    )
    tabela.setStyle(_estilo_grade(False))
    return tabela


def _tabela_resultados(linhas, estilos):
    cabecalho = ("Dado", "Valor", "Unidade")
    dados = [[_paragrafo(valor, estilos["table_head"]) for valor in cabecalho]]
    for linha in linhas:
        dados.append(
            [
                _paragrafo(linha.get("nome", ""), estilos["table"]),
                _paragrafo(linha.get("valor", ""), estilos["table"]),
                _paragrafo(linha.get("unidade", ""), estilos["table"]),
            ]
        )
    tabela = Table(
        dados,
        colWidths=[70 * mm, 70 * mm, 38 * mm],
        repeatRows=1,
        hAlign="LEFT",
        splitByRow=1,
    )
    tabela.setStyle(_estilo_grade(True))
    return tabela


def _tabela_fontes(linhas, estilos):
    cabecalho = (
        "Dado",
        "Valor",
        "Fonte / publicador",
        "Referência / data",
        "Unidade / aplicabilidade / estado",
    )
    dados = [[_paragrafo(valor, estilos["table_head"]) for valor in cabecalho]]

    def multilinha(*valores):
        texto = "<br/>".join(filter(None, (_html(valor) for valor in valores)))
        return Paragraph(texto, estilos["table"])

    for linha in linhas:
        dados.append(
            [
                _paragrafo(linha.get("campo", ""), estilos["table"]),
                _paragrafo(linha.get("valor", ""), estilos["table"]),
                multilinha(
                    linha.get("fonte", ""),
                    linha.get("publicador", ""),
                ),
                multilinha(
                    linha.get("referencia", ""),
                    linha.get("data", ""),
                ),
                multilinha(
                    linha.get("unidade", ""),
                    linha.get("aplicabilidade", ""),
                    linha.get("estado", ""),
                ),
            ]
        )
    tabela = Table(
        dados,
        colWidths=[31 * mm, 29 * mm, 36 * mm, 42 * mm, 40 * mm],
        repeatRows=1,
        hAlign="LEFT",
        splitByRow=1,
    )
    tabela.setStyle(_estilo_grade(True))
    return tabela


def _rota_completa(plano):
    rota = []
    for trecho in plano.trechos or []:
        if not rota or rota[-1] != trecho.origem_icao:
            rota.append(trecho.origem_icao)
        rota.append(trecho.destino_icao)
    if not rota:
        rota = [plano.origem_icao, plano.destino_icao]
    return " > ".join(rota)


def nome_relatorio(plano):
    hora = plano.hora_partida
    if hora.tzinfo is None or hora.utcoffset() is None:
        hora = hora.replace(tzinfo=timezone.utc)
    else:
        hora = hora.astimezone(timezone.utc)
    return f"{plano.origem_icao}-{plano.destino_icao}-{hora.strftime('%d-%m-%Y')}"


def _partida_rotulo(hora):
    if hora.tzinfo is None or hora.utcoffset() is None:
        hora = hora.replace(tzinfo=timezone.utc)
    deslocamento = hora.strftime("%z")
    if len(deslocamento) == 5:
        deslocamento = f"{deslocamento[:3]}:{deslocamento[3:]}"
    fuso = "UTC" if deslocamento in ("", "+00:00") else f"UTC{deslocamento}"
    return f"{hora.strftime('%d/%m/%Y')}  {hora.strftime('%H:%M')} {fuso}"


def _desenhar_paragrafo(canvas, texto, estilo, x, topo, largura, altura_maxima):
    paragrafo = Paragraph(_html(texto), estilo)
    _, altura = paragrafo.wrap(largura, altura_maxima)
    paragrafo.drawOn(canvas, x, topo - altura)
    return topo - altura


def _desenhar_capa(canvas, doc, plano, nome_piloto, estilos, rotulo_lido):
    largura, altura = A4
    canvas.saveState()
    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, largura, altura, fill=1, stroke=0)
    canvas.setFillColor(NAVY)
    canvas.rect(0, altura - 58 * mm, largura, 58 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, altura - 60 * mm, largura, 2 * mm, fill=1, stroke=0)
    canvas.drawImage(
        ImageReader(str(EMBLEMA)),
        18 * mm,
        altura - 49 * mm,
        width=30 * mm,
        height=30 * mm,
        preserveAspectRatio=True,
        anchor="c",
        mask="auto",
    )
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 18)
    canvas.drawString(55 * mm, altura - 31 * mm, "PLANO DE VOO")
    canvas.setFont("Helvetica", 9)
    canvas.drawString(55 * mm, altura - 40 * mm, "RELATÓRIO TÉCNICO")

    cartao_x = 18 * mm
    cartao_largura = largura - 36 * mm
    cartao_base = 38 * mm
    cartao_altura = 171 * mm
    cartao_topo = cartao_base + cartao_altura
    canvas.setFillColor(colors.white)
    canvas.roundRect(
        cartao_x,
        cartao_base,
        cartao_largura,
        cartao_altura,
        5 * mm,
        fill=1,
        stroke=0,
    )

    esquerda = cartao_x + 12 * mm
    largura_texto = cartao_largura - 24 * mm
    y = cartao_topo - 16 * mm
    canvas.setFillColor(SKY)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(esquerda, y, "PILOTO")
    y -= 4 * mm
    y = _desenhar_paragrafo(
        canvas, nome_piloto, estilos["cover_name"], esquerda, y, largura_texto, 30 * mm
    )

    y -= 12 * mm
    canvas.setFillColor(SKY)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(esquerda, y, "ROTA")
    y -= 5 * mm
    rota = _rota_completa(plano)
    estilo_rota = estilos["cover_route"]
    paragrafo_rota = Paragraph(_html(rota), estilo_rota)
    _, altura_rota = paragrafo_rota.wrap(largura_texto, 48 * mm)
    if altura_rota > 48 * mm:
        estilo_rota = ParagraphStyle(
            "PlanoCoverRouteCompact",
            parent=estilos["cover_route"],
            fontSize=9,
            leading=11,
        )
        paragrafo_rota = Paragraph(_html(rota), estilo_rota)
        _, altura_rota = paragrafo_rota.wrap(largura_texto, 48 * mm)
    paragrafo_rota.drawOn(canvas, esquerda, y - altura_rota)
    y -= altura_rota + 14 * mm

    canvas.setStrokeColor(GRID)
    canvas.setLineWidth(0.6)
    canvas.line(esquerda, y, cartao_x + cartao_largura - 12 * mm, y)
    y -= 12 * mm
    canvas.setFillColor(SKY)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(esquerda, y, "PARTIDA")
    y -= 7 * mm
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 13)
    canvas.drawString(esquerda, y, _partida_rotulo(plano.hora_partida))
    y -= 13 * mm
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 9)
    canvas.drawString(esquerda, y, f"Estado: {rotulo_lido(plano.estado)}")

    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawCentredString(
        largura / 2,
        20 * mm,
        "PLANEJAMENTO DIDÁTICO  |  NÃO É AUTORIZAÇÃO DE VOO",
    )
    canvas.restoreState()


def _cabecalho_relatorio(canvas, doc, rota):
    largura, altura = A4
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(17 * mm, altura - 10 * mm, "PLANO DE VOO")
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(largura - 17 * mm, altura - 10 * mm, "RELATÓRIO TÉCNICO")
    canvas.setStrokeColor(GRID)
    canvas.setLineWidth(0.5)
    canvas.line(17 * mm, altura - 13 * mm, largura - 17 * mm, altura - 13 * mm)
    canvas.line(17 * mm, 13 * mm, largura - 17 * mm, 13 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(17 * mm, 8 * mm, rota)
    canvas.drawRightString(largura - 17 * mm, 8 * mm, f"Página {doc.page}")
    canvas.restoreState()


def _montar_documento(buffer, plano, nome_piloto, conteudo, estilos, rotulo_lido):
    rota = _rota_completa(plano)
    doc = BaseDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=17 * mm,
        rightMargin=17 * mm,
        topMargin=20 * mm,
        bottomMargin=18 * mm,
        title=nome_relatorio(plano),
        author=nome_piloto,
        pageCompression=0,
    )
    frame = Frame(
        17 * mm,
        18 * mm,
        A4[0] - 34 * mm,
        A4[1] - 38 * mm,
        leftPadding=0,
        rightPadding=0,
        topPadding=0,
        bottomPadding=0,
        id="relatorio",
    )
    doc.addPageTemplates(
        [
            PageTemplate(
                id="capa",
                frames=[frame],
                onPage=lambda canvas, documento: _desenhar_capa(
                    canvas, documento, plano, nome_piloto, estilos, rotulo_lido
                ),
            ),
            PageTemplate(
                id="relatorio",
                frames=[frame],
                onPage=lambda canvas, documento: _cabecalho_relatorio(
                    canvas, documento, rota
                ),
            ),
        ]
    )
    doc.build([NextPageTemplate("relatorio"), PageBreak(), *conteudo])
