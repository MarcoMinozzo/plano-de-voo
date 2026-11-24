import os
import re
from xml.etree import ElementTree

import requests

INDISPONIVEL = {"estado": "indisponivel"}
TIMEOUT = 8


def _get(url, params=None, getter=None):
    obter = getter or requests.get
    return obter(url, params=params, timeout=TIMEOUT)


def meteorologia(icao, getter=None):
    saida = {"estado": "disponivel", "metar": None, "taf": None, "fonte": "Aviation Weather Center"}
    try:
        metar = _get(
            "https://aviationweather.gov/api/data/metar",
            {"ids": icao, "format": "json"},
            getter,
        )
        if getattr(metar, "status_code", 200) == 204 or not getattr(metar, "content", b"").strip():
            return dict(INDISPONIVEL)
        metar.raise_for_status()
        dados = metar.json()
        if not dados:
            return dict(INDISPONIVEL)
        item = dados[0]
        saida["metar"] = {
            "icao": icao,
            "raw": item.get("rawOb", ""),
            "hora": item.get("reportTime", ""),
            "temp_c": item.get("temp"),
            "vento_kt": item.get("wspd"),
            "unidade_vento": "kt",
        }
    except Exception:
        return dict(INDISPONIVEL)
    try:
        taf = _get(
            "https://aviationweather.gov/api/data/taf",
            {"ids": icao, "format": "json"},
            getter,
        )
        if getattr(taf, "status_code", 200) != 204 and getattr(taf, "content", b"").strip():
            taf.raise_for_status()
            lista = taf.json()
            if lista:
                saida["taf"] = {"raw": lista[0].get("rawTAF", ""), "hora": lista[0].get("issueTime", "")}
    except Exception:
        saida["taf"] = dict(INDISPONIVEL)
    return saida


def radar(origem, destino, getter=None):
    chave = os.environ.get("REDEMET_API_KEY", "").strip()
    if not chave:
        return dict(INDISPONIVEL)
    try:
        resposta = _get(
            "https://api-redemet.decea.mil.br/produtos/radar/maxcappi",
            {"api_key": chave},
            getter,
        )
        resposta.raise_for_status()
        corpo = resposta.json()
        meios_lat = (origem.lat + destino.lat) / 2
        meios_lon = (origem.lon + destino.lon) / 2
        grupos = corpo.get("data", {}).get("radar") or []
        for grupo in grupos:
            itens = grupo if isinstance(grupo, list) else [grupo]
            for item in itens:
                if not item.get("path"):
                    continue
                lat_min = float(item["lat_min"])
                lat_max = float(item["lat_max"])
                lon_min = float(item["lon_min"])
                lon_max = float(item["lon_max"])
                if lat_min <= meios_lat <= lat_max and lon_min <= meios_lon <= lon_max:
                    return {
                        "estado": "disponivel",
                        "url": item["path"],
                        "hora": item.get("data"),
                        "lat_min": lat_min,
                        "lat_max": lat_max,
                        "lon_min": lon_min,
                        "lon_max": lon_max,
                        "fonte": "REDEMET MaxCappi",
                    }
        return dict(INDISPONIVEL)
    except Exception:
        return dict(INDISPONIVEL)


def _tag(elemento):
    return elemento.tag.rsplit("}", 1)[-1].lower()


def _caixa(lat_min, lat_max, lon_min, lon_max):
    try:
        sul, norte = float(lat_min), float(lat_max)
        oeste, leste = float(lon_min), float(lon_max)
    except (TypeError, ValueError):
        return None
    if sul > norte:
        sul, norte = norte, sul
    if oeste > leste:
        oeste, leste = leste, oeste
    return sul, norte, oeste, leste


def _cobre_rota(origem, destino, caixa):
    if caixa is None:
        return False
    sul, norte, oeste, leste = caixa

    def dentro(ponto):
        return sul <= ponto.lat <= norte and oeste <= ponto.lon <= leste

    return dentro(origem) and dentro(destino)


def _area(caixa):
    sul, norte, oeste, leste = caixa
    return (norte - sul) * (leste - oeste)


def _vento_do_texto(texto):
    if not texto:
        return None
    casamento = re.search(
        r"(?:WND|WIND|VENTO)\D{0,16}(\d{3})\s*/\s*(\d{2,3})\s*KT",
        texto,
        re.IGNORECASE,
    )
    if casamento is None:
        casamento = re.search(r"\b(\d{3})\s*/\s*(\d{2,3})\s*KT\b", texto, re.IGNORECASE)
    if casamento is None:
        return None
    direcao = int(casamento.group(1))
    velocidade = int(casamento.group(2))
    if direcao > 360 or velocidade > 200:
        return None
    return direcao, velocidade


def _numero_em(item, nomes):
    if not isinstance(item, dict):
        return None
    for nome in nomes:
        if item.get(nome) not in (None, ""):
            try:
                return float(item[nome])
            except (TypeError, ValueError):
                return None
    for valor in item.values():
        if isinstance(valor, dict):
            achado = _numero_em(valor, nomes)
            if achado is not None:
                return achado
    return None


def _caixa_de_dict(item):
    return _caixa(
        _numero_em(item, ("lat_min", "latitude_min", "latMin")),
        _numero_em(item, ("lat_max", "latitude_max", "latMax")),
        _numero_em(item, ("lon_min", "lng_min", "longitude_min", "lonMin")),
        _numero_em(item, ("lon_max", "lng_max", "longitude_max", "lonMax")),
    )


def _mensagens(corpo, achados=None):
    if achados is None:
        achados = []
    if isinstance(corpo, dict):
        texto = corpo.get("mens") or corpo.get("mensagem") or corpo.get("message")
        if isinstance(texto, str) or _caixa_de_dict(corpo):
            achados.append(corpo)
        for valor in corpo.values():
            _mensagens(valor, achados)
    elif isinstance(corpo, list):
        for valor in corpo:
            _mensagens(valor, achados)
    return achados


def _texto_filho(elemento, nomes):
    procurados = {nome.lower() for nome in nomes}
    for filho in elemento.iter():
        if _tag(filho) in procurados and (filho.text or "").strip():
            return filho.text.strip()
    return None


def _link_de(elemento):
    for filho in elemento.iter():
        texto = (filho.text or "").strip()
        if texto.startswith("http"):
            return texto
    return None


def carta(origem, destino, getter=None):
    chave = os.environ.get("AISWEB_API_KEY", "").strip()
    senha = os.environ.get("AISWEB_API_PASS", "").strip()
    if not chave or not senha:
        return dict(INDISPONIVEL)
    try:
        resposta = _get(
            "https://aisweb.decea.gov.br/api/",
            {
                "apiKey": chave,
                "apiPass": senha,
                "area": "cartas",
                "especie": "VFR",
                "tipo": "WAC",
            },
            getter,
        )
        resposta.raise_for_status()
        raiz = ElementTree.fromstring(resposta.text or "")
        escolhida = None
        for elemento in raiz.iter():
            if _tag(elemento) not in {"item", "carta"}:
                continue
            link = _link_de(elemento)
            caixa = _caixa(
                _texto_filho(elemento, ("lat_min", "latitude_min")),
                _texto_filho(elemento, ("lat_max", "latitude_max")),
                _texto_filho(elemento, ("lon_min", "lng_min", "longitude_min")),
                _texto_filho(elemento, ("lon_max", "lng_max", "longitude_max")),
            )
            if not link or not _cobre_rota(origem, destino, caixa):
                continue
            if escolhida is None or _area(caixa) < escolhida[0]:
                nome = _texto_filho(elemento, ("nome", "name")) or "WAC"
                escolhida = (_area(caixa), link, nome)
        if escolhida is None:
            return dict(INDISPONIVEL)
        _tamanho, link, nome = escolhida
        return {"estado": "disponivel", "url": link, "fonte": f"AISWEB {nome}"}
    except Exception:
        return dict(INDISPONIVEL)


def vento_area(origem, destino, getter=None):
    chave = os.environ.get("REDEMET_API_KEY", "").strip()
    if not chave:
        return dict(INDISPONIVEL)
    try:
        resposta = _get(
            "https://api-redemet.decea.mil.br/mensagens/gamet",
            {"api_key": chave},
            getter,
        )
        resposta.raise_for_status()
        for item in _mensagens(resposta.json()):
            texto = item.get("mens") or item.get("mensagem") or item.get("message") or ""
            lido = _vento_do_texto(texto if isinstance(texto, str) else "")
            caixa = _caixa_de_dict(item)
            if lido is None or not _cobre_rota(origem, destino, caixa):
                continue
            direcao, velocidade = lido
            local = str(item.get("id_localidade") or item.get("localidade") or "área").strip()
            return {
                "estado": "disponivel",
                "direcao_de_graus": direcao,
                "velocidade_kt": velocidade,
                "unidade": "kt",
                "fonte": f"REDEMET área {local}",
            }
        return dict(INDISPONIVEL)
    except Exception:
        return dict(INDISPONIVEL)


def linhas_boletim(meteorologia):
    if not meteorologia or meteorologia.get("estado") != "disponivel":
        return []
    linhas = []
    for papel, rotulo in (("origem", "saída"), ("destino", "destino")):
        bloco = meteorologia.get(papel) or {}
        if bloco.get("estado") == "indisponivel":
            linhas.append(f"METAR {rotulo}: indisponível")
            linhas.append(f"TAF {rotulo}: indisponível")
            continue
        metar = bloco.get("metar") if isinstance(bloco.get("metar"), dict) else {}
        texto_metar = (metar.get("raw") or "").strip()
        linhas.append(f"METAR {rotulo}: {texto_metar}" if texto_metar else f"METAR {rotulo}: indisponível")
        taf = bloco.get("taf")
        texto_taf = taf.get("raw").strip() if isinstance(taf, dict) and isinstance(taf.get("raw"), str) else ""
        if texto_taf and taf.get("estado") != "indisponivel":
            linhas.append(f"TAF {rotulo}: {texto_taf}")
        else:
            linhas.append(f"TAF {rotulo}: indisponível")
    return linhas


def buscar(origem, destino, getter=None):
    met_origem = meteorologia(origem.icao, getter)
    met_destino = meteorologia(destino.icao, getter)
    if met_origem.get("estado") == "indisponivel" and met_destino.get("estado") == "indisponivel":
        meteorologia_plano = dict(INDISPONIVEL)
    else:
        meteorologia_plano = {"estado": "disponivel", "origem": met_origem, "destino": met_destino}
    return {
        "meteorologia": meteorologia_plano,
        "vento": vento_area(origem, destino, getter),
        "carta": carta(origem, destino, getter),
        "radar": radar(origem, destino, getter),
    }
