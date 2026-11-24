from io import BytesIO
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

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
        f"Estado: {rotulo_lido(plano.estado)}",
    ]
    if plano.motivo:
        linhas.append(f"Motivo: {plano.motivo}")
    if plano.hipotese_reabastecimento:
        linhas.append(plano.hipotese_reabastecimento)
    for trecho in plano.trechos or []:
        linhas.append(f"Trecho {trecho.ordem}: {trecho.origem_icao} -> {trecho.destino_icao}")
        linhas.append(
            f"Distância: {trecho.distancia_valor} {trecho.distancia_unidade} ({trecho.distancia_fonte})"
        )
        linhas.append(f"Proa: {trecho.proa_valor} {trecho.proa_unidade} ({trecho.proa_fonte})")
        linhas.append(f"Tempo: {trecho.tempo_valor} {trecho.tempo_unidade} ({trecho.tempo_fonte})")
        linhas.append(
            f"Combustível: {trecho.combustivel_valor} {trecho.combustivel_unidade} ({trecho.combustivel_fonte})"
        )
        linhas.append(f"Vento: {rotulo_lido(trecho.vento_estado)}")
        linhas.append(f"Pôr do sol: {rotulo_lido(trecho.por_do_sol_estado)}")
    for linha in plano.resultado.get("linhas", []):
        linhas.append(f"{linha['nome']}: {linha['valor']} {linha['unidade']} ({linha['fonte']})")
    vento = plano.vento or {}
    if vento.get("estado") == "disponivel":
        linhas.append(
            f"Vento: {vento.get('direcao_de_graus')} graus, {vento.get('velocidade_kt')} "
            f"{vento.get('unidade', 'kt')} ({vento.get('fonte', '')})"
        )
        if vento.get("efeito"):
            linhas.append(vento["efeito"])
    else:
        linhas.append("Vento: indisponível")
    boletins = linhas_boletim(plano.meteorologia or {})
    if boletins:
        linhas.extend(boletins)
    else:
        linhas.append("Tempo: indisponível")
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
