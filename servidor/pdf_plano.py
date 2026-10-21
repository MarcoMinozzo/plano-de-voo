from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

CAMINHO = Path(__file__).resolve().parent.parent / "documentacao" / "piloto.md"


def ler_orientacao():
    return CAMINHO.read_text(encoding="utf-8")


def trecho_limite():
    texto = ler_orientacao()
    marca = "## Limite do plano"
    if marca not in texto:
        return texto.strip()
    return texto.split(marca, 1)[1].strip()


def _quebrar(texto, largura=90):
    palavras = texto.split(" ")
    if not palavras:
        return [""]
    linhas = []
    atual = ""
    for palavra in palavras:
        candidato = palavra if not atual else f"{atual} {palavra}"
        if len(candidato) <= largura:
            atual = candidato
        else:
            if atual:
                linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas or [""]


def gerar_pdf(plano):
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setPageCompression(0)
    pdf.setFont("Helvetica", 11)
    y = 800
    linhas = [
        "Plano de voo",
        f"{plano.origem_icao} -> {plano.destino_icao}",
        f"Partida: {plano.hora_partida.isoformat()}",
        f"Estado: {plano.estado}",
    ]
    for linha in plano.resultado.get("linhas", []):
        linhas.append(f"{linha['nome']}: {linha['valor']} {linha['unidade']} ({linha['fonte']})")
    vento = plano.vento or {}
    if vento.get("estado") == "disponivel":
        linhas.append(f"Vento: {vento.get('efeito', '')} ({vento.get('fonte', '')})")
    else:
        linhas.append("Vento: indisponivel")
    met = plano.meteorologia or {}
    if met.get("estado") == "disponivel":
        linhas.append("Tempo: resumo meteorologico disponivel")
    else:
        linhas.append("Tempo: indisponivel")
    linhas.append("Checklist:")
    for item in plano.itens:
        marca = "x" if item.marcado else " "
        linhas.append(f"[{marca}] {item.texto} ({item.fonte})")
    linhas.append("")
    linhas.extend(ler_orientacao().splitlines())
    for texto in linhas:
        for pedaco in _quebrar(texto):
            if y < 50:
                pdf.showPage()
                pdf.setFont("Helvetica", 11)
                y = 800
            pdf.drawString(40, y, pedaco)
            y -= 16
    pdf.save()
    return buffer.getvalue()
