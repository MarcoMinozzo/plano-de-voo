"""Foto, infográfico e mapa desenhados para o PDF do plano."""

import math
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image as ImagemFluxo
from reportlab.platypus import Paragraph, Table, TableStyle

from servidor.imagens_aeronave import imagem_da_aeronave
from servidor.pdf_layout import _html, _paragrafo

RAIZ = Path(__file__).resolve().parent.parent
PASTA_FOTOS = RAIZ / "static" / "aeronaves"
NAVY = (0, 16, 48)
GOLD = (240, 160, 0)
SKY = (0, 144, 240)
PAPER = (244, 247, 251)
CINZA = (242, 242, 242)
BORDA = (138, 160, 184)
BRANCO = (255, 255, 255)
_TILES = {}


def _fonte(tamanho, negrito=False):
    nome = "DejaVuSans-Bold.ttf" if negrito else "DejaVuSans.ttf"
    caminho = Path("/usr/share/fonts/truetype/dejavu") / nome
    if caminho.is_file():
        return ImageFont.truetype(str(caminho), tamanho)
    return ImageFont.load_default()


def _texto_centro(desenho, xy, texto, fonte, cor):
    caixa = desenho.textbbox((0, 0), texto, font=fonte)
    largura = caixa[2] - caixa[0]
    altura = caixa[3] - caixa[1]
    desenho.text(
        (xy[0] - largura / 2, xy[1] - altura / 2 - caixa[1]),
        texto,
        font=fonte,
        fill=cor,
    )


def _png(imagem):
    buffer = BytesIO()
    imagem.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def _fluxo(buffer, largura, altura_maxima):
    leitor = ImageReader(buffer)
    px_l, px_a = leitor.getSize()
    largura_pt = largura
    altura_pt = largura_pt * px_a / px_l
    if altura_pt > altura_maxima:
        altura_pt = altura_maxima
        largura_pt = altura_pt * px_l / px_a
    buffer.seek(0)
    return ImagemFluxo(buffer, width=largura_pt, height=altura_pt, hAlign="CENTER")


def _paradas(plano, aerodromos, agendas, hora_infografico):
    if not plano.trechos:
        return []
    referencia = None
    primeira = agendas.get(plano.trechos[0].ordem)
    if primeira:
        referencia = primeira.get("etd")
    paradas = []
    for indice, trecho in enumerate(plano.trechos):
        agenda = agendas.get(trecho.ordem) or {}
        if indice == 0:
            paradas.append(
                {
                    "icao": trecho.origem_icao,
                    "aero": aerodromos.get(trecho.origem_icao),
                    "papel": "saida",
                    "hora": hora_infografico(agenda.get("etd"), referencia),
                    "rotulo": "Saída",
                }
            )
        ultima = indice == len(plano.trechos) - 1
        paradas.append(
            {
                "icao": trecho.destino_icao,
                "aero": aerodromos.get(trecho.destino_icao),
                "papel": "chegada" if ultima else "escala",
                "hora": hora_infografico(agenda.get("eta"), referencia),
                "rotulo": "Chegada" if ultima else "",
            }
        )
    return paradas


def desenhar_infografico(paradas):
    if not paradas:
        return None
    escala = 2
    passo = 118 * escala
    margem = 22 * escala
    largura = margem * 2 + passo * len(paradas)
    altura = 132 * escala
    imagem = Image.new("RGB", (largura, altura), GOLD)
    desenho = ImageDraw.Draw(imagem)
    centro_y = 46 * escala
    fonte_sigla = _fonte(15 * escala, negrito=True)
    fonte_escala = _fonte(11 * escala, negrito=True)
    fonte_hora = _fonte(13 * escala, negrito=True)
    fonte_papel = _fonte(9 * escala, negrito=True)
    centros = [
        margem + passo * indice + passo / 2 for indice in range(len(paradas))
    ]
    if len(centros) > 1:
        desenho.line(
            [(centro, centro_y) for centro in centros],
            fill=NAVY,
            width=4 * escala,
        )
    for centro_x, parada in zip(centros, paradas):
        raio = 40 * escala if parada["papel"] != "escala" else 24 * escala
        if parada["papel"] == "escala":
            fundo, contorno, grossura = CINZA, BORDA, 2 * escala
            fonte = fonte_escala
        else:
            fundo, contorno, grossura = GOLD, NAVY, 3 * escala
            fonte = fonte_sigla
        desenho.ellipse(
            (centro_x - raio, centro_y - raio, centro_x + raio, centro_y + raio),
            fill=fundo,
            outline=contorno,
            width=grossura,
        )
        _texto_centro(desenho, (centro_x, centro_y), parada["icao"], fonte, NAVY)
        _texto_centro(
            desenho,
            (centro_x, centro_y + 58 * escala),
            parada["hora"],
            fonte_hora,
            NAVY,
        )
        if parada["rotulo"]:
            _texto_centro(
                desenho,
                (centro_x, centro_y + 74 * escala),
                parada["rotulo"].upper(),
                fonte_papel,
                NAVY,
            )
    return _png(imagem)


def _coordenada(parada):
    aero = parada.get("aero")
    try:
        lat = float(getattr(aero, "lat", None))
        lon = float(getattr(aero, "lon", None))
    except (TypeError, ValueError):
        return None
    if not math.isfinite(lat) or not math.isfinite(lon):
        return None
    if not -90 <= lat <= 90 or not -180 <= lon <= 180:
        return None
    return lat, lon


def _mercator(lat, lon, zoom):
    n = 2**zoom
    x = (lon + 180.0) / 360.0 * n
    seno = math.sin(math.radians(max(-85.0, min(85.0, lat))))
    y = (1 - math.log((1 + seno) / (1 - seno)) / (2 * math.pi)) / 2 * n
    return x, y


def _tile(zoom, x, y):
    chave = (zoom, x, y)
    if chave in _TILES:
        return _TILES[chave]
    try:
        resposta = requests.get(
            f"https://tile.openstreetmap.org/{zoom}/{x}/{y}.png",
            timeout=2.5,
            headers={"User-Agent": "PlanoDeVoo/didatico (relatorio de voo)"},
        )
        resposta.raise_for_status()
        imagem = Image.open(BytesIO(resposta.content)).convert("RGB")
    except (requests.RequestException, OSError, ValueError):
        return None
    _TILES[chave] = imagem
    return imagem


def _mapa_osm(pontos):
    lats = [ponto[0] for ponto in pontos]
    lons = [ponto[1] for ponto in pontos]
    escolhido = None
    for zoom in range(10, 3, -1):
        xs, ys = zip(*(_mercator(lat, lon, zoom) for lat, lon in pontos))
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)
        if x1 - x0 < 0.35:
            meio = (x0 + x1) / 2
            x0, x1 = meio - 0.45, meio + 0.45
        if y1 - y0 < 0.25:
            meio = (y0 + y1) / 2
            y0, y1 = meio - 0.35, meio + 0.35
        tx0, tx1 = math.floor(x0 - 0.3), math.floor(x1 + 0.3)
        ty0, ty1 = math.floor(y0 - 0.3), math.floor(y1 + 0.3)
        colunas, linhas = tx1 - tx0 + 1, ty1 - ty0 + 1
        if colunas * linhas <= 6 and colunas <= 4 and linhas <= 3:
            escolhido = (zoom, tx0, ty0, tx1, ty1)
            break
    if escolhido is None:
        return None
    zoom, tx0, ty0, tx1, ty1 = escolhido
    tiles = []
    for ty in range(ty0, ty1 + 1):
        linha = []
        for tx in range(tx0, tx1 + 1):
            tile = _tile(zoom, tx, ty)
            if tile is None:
                return None
            linha.append(tile)
        tiles.append(linha)
    largura_tile = tiles[0][0].width
    imagem = Image.new(
        "RGB",
        (largura_tile * len(tiles[0]), largura_tile * len(tiles)),
        PAPER,
    )
    for linha, faixa in enumerate(tiles):
        for coluna, tile in enumerate(faixa):
            imagem.paste(tile, (coluna * largura_tile, linha * largura_tile))
    pixels = []
    for lat, lon in pontos:
        x, y = _mercator(lat, lon, zoom)
        pixels.append(((x - tx0) * largura_tile, (y - ty0) * largura_tile))
    return imagem, pixels, "Mapa © OpenStreetMap. Não substitui a carta de voo."


def _mapa_esquema(pontos):
    lats = [ponto[0] for ponto in pontos]
    lons = [ponto[1] for ponto in pontos]
    lat0, lat1 = min(lats), max(lats)
    lon0, lon1 = min(lons), max(lons)
    if lat1 - lat0 < 0.4:
        meio = (lat0 + lat1) / 2
        lat0, lat1 = meio - 0.35, meio + 0.35
    if lon1 - lon0 < 0.4:
        meio = (lon0 + lon1) / 2
        lon0, lon1 = meio - 0.45, meio + 0.45
    margem_lat = (lat1 - lat0) * 0.18
    margem_lon = (lon1 - lon0) * 0.14
    lat0 -= margem_lat
    lat1 += margem_lat
    lon0 -= margem_lon
    lon1 += margem_lon
    largura, altura = 1200, 620
    imagem = Image.new("RGB", (largura, altura), PAPER)
    desenho = ImageDraw.Draw(imagem)
    for passo in range(1, 4):
        y = altura * passo / 4
        x = largura * passo / 4
        desenho.line((0, y, largura, y), fill=(203, 213, 225), width=2)
        desenho.line((x, 0, x, altura), fill=(203, 213, 225), width=2)
    pixels = []
    for lat, lon in pontos:
        x = (lon - lon0) / (lon1 - lon0) * largura
        y = (lat1 - lat) / (lat1 - lat0) * altura
        pixels.append((x, y))
    return (
        imagem,
        pixels,
        "Posição relativa dos aeródromos. Não substitui a carta de voo.",
    )


def _marcar_rota(imagem, pixels, paradas):
    desenho = ImageDraw.Draw(imagem)
    if len(pixels) >= 2:
        desenho.line(pixels, fill=NAVY, width=6)
    fonte = _fonte(18, negrito=True)
    for pixel, parada in zip(pixels, paradas):
        raio = 16 if parada["papel"] != "escala" else 11
        if parada["papel"] == "saida":
            cor = GOLD
        elif parada["papel"] == "chegada":
            cor = SKY
        else:
            cor = CINZA
        x, y = pixel
        desenho.ellipse(
            (x - raio, y - raio, x + raio, y + raio),
            fill=cor,
            outline=NAVY,
            width=3,
        )
        caixa = desenho.textbbox((0, 0), parada["icao"], font=fonte)
        origem = (x - (caixa[2] - caixa[0]) / 2, y - raio - 24)
        for deslocamento in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            desenho.text(
                (origem[0] + deslocamento[0], origem[1] + deslocamento[1]),
                parada["icao"],
                font=fonte,
                fill=BRANCO,
            )
        desenho.text(origem, parada["icao"], font=fonte, fill=NAVY)
    return imagem


def desenhar_mapa(paradas):
    pontos = []
    usadas = []
    for parada in paradas:
        coordenada = _coordenada(parada)
        if coordenada is None:
            continue
        pontos.append(coordenada)
        usadas.append(parada)
    if len(pontos) < 2:
        return None
    montado = _mapa_osm(pontos)
    if montado is None:
        montado = _mapa_esquema(pontos)
    imagem, pixels, legenda = montado
    xs = [pixel[0] for pixel in pixels]
    ys = [pixel[1] for pixel in pixels]
    margem = 72
    caixa = (
        max(0, math.floor(min(xs) - margem)),
        max(0, math.floor(min(ys) - margem)),
        min(imagem.width, math.ceil(max(xs) + margem)),
        min(imagem.height, math.ceil(max(ys) + margem)),
    )
    if caixa[2] - caixa[0] > 40 and caixa[3] - caixa[1] > 40:
        deslocado = [(x - caixa[0], y - caixa[1]) for x, y in pixels]
        imagem = imagem.crop(caixa)
        pixels = deslocado
    imagem = _marcar_rota(imagem, pixels, usadas)
    return _png(imagem), legenda


def faixa_do_relatorio(plano, aeronave, aerodromos, agendas, estilos, hora_infografico):
    paradas = _paradas(plano, aerodromos, agendas, hora_infografico)
    nome = getattr(aeronave, "nome", None) or "Indisponível"
    foto = imagem_da_aeronave(nome)
    caminho = PASTA_FOTOS / foto.arquivo if foto else None
    coluna = []
    if caminho and caminho.is_file():
        with Image.open(caminho) as original:
            copia = original.convert("RGB")
            buffer = _png(copia)
        coluna.append(_fluxo(buffer, 62 * mm, 46 * mm))
        coluna.append(_paragrafo(f"Aeronave: {nome}.", estilos["small"]))
        coluna.append(_paragrafo(foto.autor, estilos["small"]))
    else:
        coluna.append(_paragrafo(f"Aeronave: {nome}.", estilos["body"]))
        coluna.append(_paragrafo("Foto indisponível.", estilos["body"]))
    info = desenhar_infografico(paradas)
    if info is None:
        return coluna
    grafico = _fluxo(info, 108 * mm, 48 * mm)
    foto = Table([[item] for item in coluna], colWidths=[64 * mm])
    foto.setStyle(
        TableStyle(
            [
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 1),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    tabela = Table(
        [[foto, grafico]],
        colWidths=[68 * mm, 108 * mm],
    )
    tabela.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("ALIGN", (1, 0), (1, 0), "CENTER"),
            ]
        )
    )
    tabela.hAlign = "CENTER"
    return [tabela]


def mapa_do_relatorio(paradas, estilos):
    montado = desenhar_mapa(paradas)
    if montado is None:
        return [
            _paragrafo(
                "Mapa indisponível: coordenadas do trecho não encontradas.",
                estilos["body"],
            )
        ]
    buffer, legenda = montado
    return [
        _fluxo(buffer, 176 * mm, 92 * mm),
        Paragraph(_html(legenda), estilos["small"]),
    ]
