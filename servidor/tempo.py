import os
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


def carta(getter=None):
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
        texto = resposta.text or ""
        raiz = ElementTree.fromstring(texto)
        link = None
        for elemento in raiz.iter():
            if elemento.text and elemento.text.startswith("http"):
                link = elemento.text.strip()
                break
        if not link:
            return dict(INDISPONIVEL)
        return {"estado": "disponivel", "url": link, "fonte": "AISWEB WAC vigente"}
    except Exception:
        return dict(INDISPONIVEL)


def vento_area(getter=None):
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
        corpo = resposta.json()
        texto = str(corpo)
        if "KT" not in texto.upper() and "vento" not in texto.lower():
            return dict(INDISPONIVEL)
        return dict(INDISPONIVEL)
    except Exception:
        return dict(INDISPONIVEL)


def buscar(origem, destino, getter=None):
    met_origem = meteorologia(origem.icao, getter)
    met_destino = meteorologia(destino.icao, getter)
    if met_origem.get("estado") == "indisponivel" and met_destino.get("estado") == "indisponivel":
        meteorologia_plano = dict(INDISPONIVEL)
    else:
        meteorologia_plano = {"estado": "disponivel", "origem": met_origem, "destino": met_destino}
    return {
        "meteorologia": meteorologia_plano,
        "vento": vento_area(getter),
        "carta": carta(getter),
        "radar": radar(origem, destino, getter),
    }
