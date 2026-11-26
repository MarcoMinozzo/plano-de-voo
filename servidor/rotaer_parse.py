import math
import re
from datetime import date
from html.parser import HTMLParser
from xml.etree import ElementTree


def _tag(elemento):
    return elemento.tag.rsplit("}", 1)[-1].lower()


def _texto(elemento, *nomes):
    procurados = {nome.lower() for nome in nomes}
    for filho in list(elemento):
        if _tag(filho) in procurados and (filho.text or "").strip():
            return filho.text.strip()
    return ""


def _decimal(valor):
    texto = (valor or "").strip().replace(",", ".")
    if not texto:
        raise ValueError("coordenada vazia")
    hemi = texto[-1].upper()
    if hemi in "NSEW":
        corpo = texto[:-1].strip().replace("°", " ").replace("'", " ").replace('"', " ")
        partes = [p for p in corpo.split() if p]
        graus = float(partes[0])
        minutos = float(partes[1]) if len(partes) > 1 else 0.0
        segundos = float(partes[2]) if len(partes) > 2 else 0.0
        numero = graus + minutos / 60 + segundos / 3600
        if hemi in "SW":
            numero = -numero
        return numero
    return float(texto)


def _numero_rotaer(valor, campo, icao):
    try:
        numero = _decimal(valor)
    except (TypeError, ValueError):
        raise ValueError(f"campo {campo} ausente ou inválido para {icao}") from None
    if not math.isfinite(numero):
        raise ValueError(f"campo {campo} inválido para {icao}")
    return numero


def _data_rotaer(valor, icao):
    try:
        return date.fromisoformat((valor or "").strip())
    except ValueError:
        raise ValueError(
            f"data de publicação ausente ou inválida para {icao}"
        ) from None


def _tipo_lugar(valor):
    texto = (valor or "").strip().upper()
    if not texto:
        return None
    if "HELI" in texto or texto in {"HP", "H", "HL"}:
        return "heliponto"
    if "AERO" in texto or texto in {"AD", "A"}:
        return "aerodromo"
    return None


def _interpretar_pagina_rotaer(corpo):
    if isinstance(corpo, bytes):
        corpo = corpo.decode("utf-8", errors="replace")
    raiz = ElementTree.fromstring(corpo or "")
    contenedor = next(
        (
            elemento
            for elemento in raiz.iter()
            if _tag(elemento) == "rotaer" and "total" in elemento.attrib
        ),
        None,
    )
    if contenedor is None:
        return None
    try:
        total = int(contenedor.attrib["total"])
    except (KeyError, TypeError, ValueError):
        raise ValueError("total de registros ROTAER inválido") from None
    if total < 0:
        raise ValueError("total de registros ROTAER inválido")

    itens = [elemento for elemento in list(contenedor) if _tag(elemento) == "item"]
    registros = []
    for item in itens:
        tipo = _tipo_lugar(_texto(item, "type", "tipo"))
        if tipo != "aerodromo":
            continue
        icao = _texto(item, "AeroCode", "icao", "identificador").upper()
        nome = _texto(item, "name", "nome")
        versao_id = _texto(item, "id") or item.attrib.get("id", "").strip()
        if not icao or len(icao) > 16:
            raise ValueError("aeródromo ROTAER sem identificador válido")
        if not nome or len(nome) > 160:
            raise ValueError(f"nome ausente ou inválido para {icao}")
        if not versao_id or len(versao_id) > 80:
            raise ValueError(f"versão AISWEB ausente ou inválida para {icao}")
        atualizado_em = _data_rotaer(_texto(item, "dt"), icao)
        registros.append(
            {
                "icao": icao,
                "nome": nome,
                "tipo": tipo,
                "rotaer_versao_id": versao_id,
                "rotaer_atualizado_em": atualizado_em,
            }
        )
    return total, len(itens), registros


def interpretar_rotaer(corpo):
    if isinstance(corpo, bytes):
        corpo = corpo.decode("utf-8", errors="replace")
    if not (corpo or "").strip():
        return None, []
    raiz = ElementTree.fromstring(corpo)
    codigo = None
    for filho in list(raiz):
        if _tag(filho) == "emenda" and (filho.text or "").strip():
            codigo = filho.text.strip()
            break
    if codigo is None:
        for elemento in raiz.iter():
            if _tag(elemento) == "emenda" and (elemento.text or "").strip():
                codigo = elemento.text.strip()
                break
    registros = []
    for elemento in raiz.iter():
        if _tag(elemento) not in {"rotaer", "aerodromo"}:
            continue
        icao = _texto(elemento, "AeroCode", "icao", "identificador").upper()
        nome = _texto(elemento, "name", "nome")
        tipo = _tipo_lugar(_texto(elemento, "type", "tipo"))
        if not icao or not nome or tipo is None or len(icao) > 16:
            continue
        try:
            lat = _decimal(_texto(elemento, "lat", "latitude"))
            lon = _decimal(_texto(elemento, "lng", "lon", "longitude"))
            elev = float(
                _texto(elemento, "altM", "elev_m", "elevacao").replace(",", ".")
            )
        except (TypeError, ValueError):
            continue
        registros.append(
            {
                "icao": icao,
                "nome": nome,
                "tipo": tipo,
                "lat": lat,
                "lon": lon,
                "elev_m": elev,
            }
        )
    return codigo, registros


class _ParserHtmlDetalheRotaer(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.titulos = {}
        self.linhas = []
        self.comentarios = []
        self._linha = None
        self._celula = None
        self._titulo = None
        self._texto_titulo = []

    def handle_starttag(self, tag, attrs):
        atributos = dict(attrs)
        if tag == "tr":
            self._linha = []
            self.linhas.append(self._linha)
        elif tag in {"td", "th"} and self._linha is not None:
            self._celula = []
            self._linha.append(self._celula)
        if tag == "span" and atributos.get("title"):
            self._titulo = atributos["title"]
            self._texto_titulo = []

    def handle_data(self, data):
        if self._celula is not None:
            self._celula.append(data)
        if self._titulo is not None:
            self._texto_titulo.append(data)

    def handle_endtag(self, tag):
        if tag == "span" and self._titulo is not None:
            valor = " ".join("".join(self._texto_titulo).split())
            self.titulos.setdefault(self._titulo, []).append(valor)
            self._titulo = None
            self._texto_titulo = []
        elif tag in {"td", "th"}:
            self._celula = None
        elif tag == "tr":
            self._linha = None

    def handle_comment(self, data):
        self.comentarios.append(data.strip())


def _detalhe_rotaer_html(corpo, item):
    parser = _ParserHtmlDetalheRotaer()
    parser.feed(corpo or "")
    icao = " ".join(
        parser.titulos.get("Indicador de Localidade (ICAO Code)", [""])[0].split()
    ).upper()
    if icao != item["icao"]:
        raise ValueError(f"detalhe AISWEB não corresponde a {item['icao']}")
    tipo = parser.titulos.get("Aeródromo", [""])[0]
    if _tipo_lugar(tipo) != "aerodromo":
        raise ValueError(f"tipo AISWEB inválido para {icao}")

    data_publicacao = None
    for comentario in parser.comentarios:
        correspondencia = re.search(
            r"\bemenda\s+(\d{2})/(\d{2})/(\d{4})\b",
            comentario,
            flags=re.IGNORECASE,
        )
        if correspondencia:
            dia, mes, ano = correspondencia.groups()
            data_publicacao = _data_rotaer(f"{ano}-{mes}-{dia}", icao)
            break
    if data_publicacao is None:
        raise ValueError(f"data de publicação ausente ou inválida para {icao}")
    if data_publicacao != item["rotaer_atualizado_em"]:
        raise ValueError(f"versão AISWEB mudou durante a carga de {icao}")

    if len(parser.linhas) < 2 or len(parser.linhas[0]) < 2 or len(parser.linhas[1]) < 2:
        raise ValueError(f"coordenadas ou elevação ausentes para {icao}")
    coordenadas = " ".join("".join(parser.linhas[0][1]).split())
    partes_coordenadas = coordenadas.split("/")
    if len(partes_coordenadas) != 2:
        raise ValueError(f"coordenadas ausentes ou inválidas para {icao}")
    latitude = re.sub(r"(?<=\d)\s+\.(?=\d)", ".", partes_coordenadas[0])
    longitude = re.sub(r"(?<=\d)\s+\.(?=\d)", ".", partes_coordenadas[1])
    lat = _numero_rotaer(latitude, "lat", icao)
    lon = _numero_rotaer(longitude, "lng", icao)
    altitude = " ".join("".join(parser.linhas[1][1]).split())
    correspondencia_altitude = re.match(r"(-?\d+(?:[.,]\d+)?)", altitude)
    if correspondencia_altitude is None:
        raise ValueError(f"campo altM ausente ou inválido para {icao}")
    elevacao = _numero_rotaer(correspondencia_altitude.group(1), "altM", icao)
    if not -90 <= lat <= 90:
        raise ValueError(f"campo lat fora do intervalo válido para {icao}")
    if not -180 <= lon <= 180:
        raise ValueError(f"campo lng fora do intervalo válido para {icao}")
    return {
        "lat": lat,
        "lon": lon,
        "elev_m": elevacao,
    }
