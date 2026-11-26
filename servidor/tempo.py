import json
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
        observacao = {
            "icao": icao,
            "raw": item.get("rawOb", ""),
            "hora": item.get("reportTime", ""),
            "temp_c": item.get("temp"),
            "vento_kt": item.get("wspd"),
            "unidade_vento": "kt",
            "fonte": saida["fonte"],
        }
        campos = {
            "dewp": "ponto_orvalho_c",
            "wdir": "direcao_vento",
            "wgst": "rajada_kt",
            "visib": "visibilidade_sm",
            "altim": "altimetro_hpa",
            "wxString": "fenomenos",
            "vertVis": "visibilidade_vertical_ft",
            "clouds": "nuvens",
        }
        for campo, chave in campos.items():
            valor = item.get(campo)
            if valor is not None and valor != "":
                observacao[chave] = valor
        saida["metar"] = observacao
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
        return {
            "estado": "indisponivel",
            "motivo": "Chave REDEMET não configurada.",
        }
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
        return {
            "estado": "indisponivel",
            "motivo": "Radar sem dados geográficos válidos para o trecho.",
        }
    except Exception:
        return {
            "estado": "indisponivel",
            "motivo": "Fonte REDEMET indisponível.",
        }


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
            "https://api.decea.mil.br/aisweb/",
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


def buscar(origem, destino, getter=None, *, aerodromos=None, vento=None):
    lugares = list(aerodromos or (origem, destino))
    for lugar in (origem, destino):
        if all(aero.icao != lugar.icao for aero in lugares):
            lugares.append(lugar)
    boletins = {}
    for lugar in lugares:
        if lugar.icao in boletins:
            continue
        boletim = meteorologia(lugar.icao, getter)
        if "fonte" not in boletim:
            boletim = {**boletim, "fonte": "Aviation Weather Center"}
        boletins[lugar.icao] = boletim
    if any(item.get("estado") == "disponivel" for item in boletins.values()):
        meteorologia_plano = {
            "estado": "disponivel",
            "origem": boletins[origem.icao],
            "destino": boletins[destino.icao],
            "aerodromos": boletins,
        }
    else:
        meteorologia_plano = {
            "estado": "indisponivel",
            "origem": boletins[origem.icao],
            "destino": boletins[destino.icao],
            "aerodromos": boletins,
        }
    return {
        "meteorologia": meteorologia_plano,
        "vento": vento if vento is not None else vento_area(origem, destino, getter),
        "carta": carta(origem, destino, getter),
        "radar": radar(origem, destino, getter),
    }


def campos_metar(metar):
    observacao = metar if isinstance(metar, dict) else {}
    definicoes = (
        ("temp_c", "Temperatura", "°C"),
        ("ponto_orvalho_c", "Ponto de orvalho", "°C"),
        ("direcao_vento", "Direção do vento", None),
        ("vento_kt", "Velocidade do vento", "kt"),
        ("rajada_kt", "Rajada", "kt"),
        ("visibilidade_sm", "Visibilidade", "SM"),
        ("altimetro_hpa", "Altímetro", "hPa"),
        ("fenomenos", "Fenômenos meteorológicos (código AWC)", "código AWC"),
        ("visibilidade_vertical_ft", "Visibilidade vertical", "ft"),
        ("nuvens", "Camadas de nuvens (dados AWC)", "dados AWC"),
    )
    campos = []
    for chave, nome, unidade in definicoes:
        valor = observacao.get(chave)
        if chave == "direcao_vento":
            if isinstance(valor, (int, float)) and not isinstance(valor, bool):
                unidade = "graus"
            elif valor not in (None, ""):
                unidade = "código AWC"
            else:
                unidade = "graus ou código AWC"
        elif chave == "nuvens" and valor is not None:
            valor = json.dumps(valor, ensure_ascii=False)
        campos.append(
            {
                "nome": nome,
                "valor": valor if valor is not None and valor != "" else "Indisponível",
                "unidade": unidade,
            }
        )
    return campos
