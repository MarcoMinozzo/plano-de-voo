import json
import logging
import math
import os
import re
from datetime import datetime, timezone
from urllib.parse import urlparse
from xml.etree import ElementTree

import requests

INDISPONIVEL = {"estado": "indisponivel"}
TIMEOUT = 8
RAIO_TERRA_NM = 3440.065
LIMITE_METAR_REGIONAL_NM = 50
MARGEM_BUSCA_METAR_NM = 1
logger = logging.getLogger(__name__)


def _get(url, params=None, getter=None):
    obter = getter or requests.get
    return obter(url, params=params, timeout=TIMEOUT)


def _coordenadas_validas(lat, lon):
    try:
        latitude = float(lat)
        longitude = float(lon)
    except (TypeError, ValueError):
        return None
    if (
        not math.isfinite(latitude)
        or not math.isfinite(longitude)
        or not -90 <= latitude <= 90
        or not -180 <= longitude <= 180
    ):
        return None
    return latitude, longitude


def _distancia_nm(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    return 2 * RAIO_TERRA_NM * math.asin(min(1.0, math.sqrt(a)))


def _metar_de_item(item, icao, *, regional=False, distancia_nm=None):
    bruto = item.get("rawOb")
    if not isinstance(bruto, str) or not bruto.strip():
        return None
    estacao_icao = str(item.get("icaoId") or icao).strip().upper()
    nome_estacao = item.get("name")
    if regional and (
        not estacao_icao
        or not isinstance(nome_estacao, str)
        or not nome_estacao.strip()
    ):
        return None
    observacao = {
        "icao": estacao_icao,
        "nome_estacao": nome_estacao.strip() if isinstance(nome_estacao, str) else "",
        "raw": bruto.strip(),
        "hora": item.get("reportTime", ""),
        "temp_c": item.get("temp"),
        "vento_kt": item.get("wspd"),
        "unidade_vento": "kt",
        "fonte": "Aviation Weather Center",
        "regional": regional,
    }
    if regional:
        observacao.update(
            aerodromo_referencia=icao,
            distancia_nm=distancia_nm,
        )
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
    return observacao


def _instante_redemet(valor):
    if not isinstance(valor, str) or not valor.strip():
        return None
    texto = valor.strip()
    if texto.endswith("Z"):
        texto = f"{texto[:-1]}+00:00"
    try:
        instante = datetime.fromisoformat(texto)
    except ValueError:
        return None
    if instante.tzinfo is None:
        instante = instante.replace(tzinfo=timezone.utc)
    return instante.astimezone(timezone.utc)


def _agora_utc():
    return datetime.now(timezone.utc)


def _taf_redemet(icao, getter=None):
    chave = os.environ.get("REDEMET_API_KEY", "").strip()
    indicativo = str(icao or "").strip().upper()
    if not chave or not re.fullmatch(r"[A-Z0-9]{4}", indicativo):
        return None

    try:
        resposta = _get(
            f"https://api-redemet.decea.mil.br/mensagens/taf/{indicativo}",
            {"api_key": chave},
            getter,
        )
        resposta.raise_for_status()
        corpo = resposta.json()
    except (requests.RequestException, ValueError, TypeError, AttributeError):
        logger.warning("Falha ao consultar TAF REDEMET para %s", indicativo)
        return None

    if not isinstance(corpo, dict) or corpo.get("status") is not True:
        logger.warning("Resposta TAF REDEMET inválida para %s", indicativo)
        return None

    validos = []
    for item in _mensagens(corpo):
        localidade = str(
            item.get("id_localidade") or item.get("localidade") or ""
        ).strip().upper()
        mensagem = item.get("mens") or item.get("mensagem") or item.get("message")
        if (
            localidade != indicativo
            or not isinstance(mensagem, str)
            or not re.match(r"^TAF\s", mensagem.strip(), re.IGNORECASE)
            or not re.search(
                rf"\b{re.escape(indicativo)}\b", mensagem, re.IGNORECASE
            )
        ):
            continue

        recebido = item.get("recebimento")
        inicio = item.get("validade_inicial")
        fim = item.get("validade_final")
        recebido_dt = _instante_redemet(recebido)
        inicio_dt = _instante_redemet(inicio)
        fim_dt = _instante_redemet(fim)
        if (
            recebido_dt is None
            or inicio_dt is None
            or fim_dt is None
            or inicio_dt > fim_dt
            or fim_dt <= _agora_utc()
        ):
            continue

        validos.append(
            (
                recebido_dt,
                {
                    "raw": mensagem.strip(),
                    "hora": recebido.strip(),
                    "fonte": "REDEMET",
                    "icao": indicativo,
                    "validade_inicial": inicio.strip(),
                    "validade_final": fim.strip(),
                },
            )
        )

    if not validos:
        logger.warning("TAF REDEMET sem mensagem válida para %s", indicativo)
        return None
    return max(validos, key=lambda candidato: candidato[0])[1]


def meteorologia(icao, getter=None):
    saida = {"estado": "disponivel", "metar": None, "taf": None, "fonte": "Aviation Weather Center"}
    try:
        metar = _get(
            "https://aviationweather.gov/api/data/metar",
            {"ids": icao, "format": "json"},
            getter,
        )
        conteudo = getattr(metar, "content", b"") or b""
        if (
            getattr(metar, "status_code", 200) != 204
            and conteudo.strip()
        ):
            metar.raise_for_status()
            dados = metar.json()
            if not isinstance(dados, list):
                raise ValueError("Resposta METAR AWC inválida")
            if dados:
                if not isinstance(dados[0], dict):
                    raise ValueError("Resposta METAR AWC inválida")
                observacao = _metar_de_item(dados[0], icao)
                if observacao:
                    saida["metar"] = observacao
                else:
                    logger.warning("Resposta METAR AWC sem observação válida para %s", icao)
    except (requests.RequestException, ValueError, TypeError, AttributeError):
        logger.warning("Falha ao consultar METAR AWC para %s", icao, exc_info=True)
    taf_redemet = _taf_redemet(icao, getter)
    if taf_redemet:
        saida["taf"] = taf_redemet
    else:
        try:
            taf = _get(
                "https://aviationweather.gov/api/data/taf",
                {"ids": icao, "format": "json"},
                getter,
            )
            conteudo = getattr(taf, "content", b"") or b""
            if getattr(taf, "status_code", 200) != 204 and conteudo.strip():
                taf.raise_for_status()
                lista = taf.json()
                if not isinstance(lista, list):
                    raise ValueError("Resposta TAF AWC inválida")
                if lista:
                    if not isinstance(lista[0], dict):
                        raise ValueError("Resposta TAF AWC inválida")
                    bruto = lista[0].get("rawTAF")
                    if isinstance(bruto, str) and bruto.strip():
                        saida["taf"] = {
                            "raw": bruto.strip(),
                            "hora": lista[0].get("issueTime", ""),
                            "fonte": saida["fonte"],
                        }
        except (requests.RequestException, ValueError, TypeError, AttributeError):
            logger.warning("Falha ao consultar TAF AWC para %s", icao, exc_info=True)
            saida["taf"] = dict(INDISPONIVEL)
    if saida["metar"] or (
        isinstance(saida["taf"], dict)
        and saida["taf"].get("estado") != "indisponivel"
    ):
        saida["estado"] = "disponivel"
    else:
        saida["estado"] = "indisponivel"
    return saida


def _metar_regional(aerodromo, getter=None):
    icao = str(getattr(aerodromo, "icao", "") or "").strip().upper()
    coordenadas = _coordenadas_validas(
        getattr(aerodromo, "lat", None),
        getattr(aerodromo, "lon", None),
    )
    if not icao or coordenadas is None:
        return None

    latitude, longitude = coordenadas
    raio_busca_nm = LIMITE_METAR_REGIONAL_NM + MARGEM_BUSCA_METAR_NM
    raio_angular = raio_busca_nm / RAIO_TERRA_NM
    delta_lat = math.degrees(raio_angular)
    lat_min = max(-90.0, latitude - delta_lat)
    lat_max = min(90.0, latitude + delta_lat)
    if abs(math.radians(latitude)) + raio_angular >= math.pi / 2:
        delta_lon = 180.0
    else:
        delta_lon = math.degrees(
            math.asin(
                min(1.0, math.sin(raio_angular) / math.cos(math.radians(latitude)))
            )
        )
    if longitude - delta_lon < -180 or longitude + delta_lon > 180:
        lon_min, lon_max = -180.0, 180.0
    else:
        lon_min, lon_max = longitude - delta_lon, longitude + delta_lon
    bbox = f"{lat_min:.3f},{lon_min:.3f},{lat_max:.3f},{lon_max:.3f}"

    try:
        resposta = _get(
            "https://aviationweather.gov/api/data/metar",
            {"bbox": bbox, "format": "json"},
            getter,
        )
        conteudo = getattr(resposta, "content", b"") or b""
        if getattr(resposta, "status_code", 200) == 204 or not conteudo.strip():
            return None
        resposta.raise_for_status()
        dados = resposta.json()
        if not isinstance(dados, list):
            raise ValueError("Resposta METAR regional AWC inválida")
    except (requests.RequestException, ValueError, TypeError, AttributeError):
        logger.warning("Falha ao consultar METAR regional AWC para %s", icao, exc_info=True)
        return None

    candidatos = []
    for item in dados:
        if not isinstance(item, dict):
            continue
        posicao = _coordenadas_validas(item.get("lat"), item.get("lon"))
        if posicao is None:
            continue
        distancia = _distancia_nm(latitude, longitude, *posicao)
        if distancia > LIMITE_METAR_REGIONAL_NM + 1e-9:
            continue
        observacao = _metar_de_item(
            item,
            icao,
            regional=True,
            distancia_nm=distancia,
        )
        if observacao:
            candidatos.append((distancia, observacao["icao"], observacao))
    if not candidatos:
        return None
    candidatos.sort(key=lambda candidato: (candidato[0], candidato[1]))
    return candidatos[0][2]


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


def satelite(getter=None):
    chave = os.environ.get("REDEMET_API_KEY", "").strip()
    if not chave:
        return dict(INDISPONIVEL)
    try:
        resposta = _get(
            "https://api-redemet.decea.mil.br/produtos/satelite/realcada",
            {"api_key": chave, "anima": 10},
            getter,
        )
        resposta.raise_for_status()
        corpo = resposta.json()
    except (requests.RequestException, ValueError):
        return dict(INDISPONIVEL)

    if not isinstance(corpo, dict) or corpo.get("status") is not True:
        return dict(INDISPONIVEL)
    dados = corpo.get("data")
    if not isinstance(dados, dict) or dados.get("tipo") != "realcada":
        return dict(INDISPONIVEL)
    caixa = dados.get("lat_lon")
    quadros = dados.get("satelite")
    if not isinstance(caixa, dict) or not isinstance(quadros, list):
        return dict(INDISPONIVEL)

    limites = {}
    for nome, minimo, maximo in (
        ("lat_min", -90, 90),
        ("lat_max", -90, 90),
        ("lon_min", -180, 180),
        ("lon_max", -180, 180),
    ):
        valor = caixa.get(nome)
        if isinstance(valor, bool):
            return dict(INDISPONIVEL)
        try:
            numero = float(valor)
        except (TypeError, ValueError):
            return dict(INDISPONIVEL)
        if not math.isfinite(numero) or not minimo <= numero <= maximo:
            return dict(INDISPONIVEL)
        limites[nome] = numero
    if (
        limites["lat_min"] >= limites["lat_max"]
        or limites["lon_min"] >= limites["lon_max"]
    ):
        return dict(INDISPONIVEL)

    validos = []
    for quadro in quadros:
        if not isinstance(quadro, dict):
            continue
        url = quadro.get("path")
        hora = quadro.get("data")
        if not isinstance(url, str) or not isinstance(hora, str) or not hora.strip():
            continue
        parsed_url = urlparse(url)
        if (
            parsed_url.scheme != "https"
            or parsed_url.netloc != "estatico-redemet.decea.mil.br"
            or not parsed_url.path.lower().endswith(".png")
            or parsed_url.query
            or parsed_url.fragment
        ):
            continue
        try:
            instante = datetime.strptime(hora, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        validos.append((instante, url, hora))
    if not validos:
        return dict(INDISPONIVEL)

    _, url, hora = max(validos, key=lambda quadro: quadro[0])
    return {
        "estado": "disponivel",
        "url": url,
        "hora": hora,
        **limites,
        "fonte": "REDEMET Satélite realçada",
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


def carta(origem, destino, getter=None, aerodromos=None):
    chave = os.environ.get("AISWEB_API_KEY", "").strip()
    senha = os.environ.get("AISWEB_API_PASS", "").strip()
    if not chave or not senha:
        return dict(INDISPONIVEL)
    try:
        rota = list(aerodromos or (origem, destino))
        unicos = []
        vistos_icao = set()
        for aerodromo in rota:
            if aerodromo is None or aerodromo.icao in vistos_icao:
                continue
            vistos_icao.add(aerodromo.icao)
            unicos.append(aerodromo)
        if len(unicos) < 2:
            return dict(INDISPONIVEL)

        documentos = []
        vistos_documentos = set()
        for aerodromo in unicos:
            resposta = _get(
                "https://api.decea.mil.br/aisweb/",
                {
                    "apiKey": chave,
                    "apiPass": senha,
                    "area": "cartas",
                    "especie": "VFR",
                    "tipo": "WAC",
                    "icaoCode": aerodromo.icao,
                },
                getter,
            )
            resposta.raise_for_status()
            raiz = ElementTree.fromstring(resposta.text or "")
            documentos_aerodromo = []
            for elemento in raiz.iter():
                if _tag(elemento) not in {"item", "carta"}:
                    continue
                tipo = (_texto_filho(elemento, ("tipo",)) or "").strip().upper()
                icao = (_texto_filho(elemento, ("IcaoCode", "icaoCode")) or "").upper()
                nome = _texto_filho(elemento, ("nome", "name")) or ""
                link = _link_de(elemento)
                parsed_link = urlparse(link or "")
                indice = _texto_filho(elemento, ("indiceMapa", "indice_mapa"))
                if indice is None:
                    encontrado = re.search(r"\bWAC[\s_-]*(\d{4})\b", nome, re.IGNORECASE)
                    indice = encontrado.group(1) if encontrado else None
                if (
                    tipo != "WAC"
                    or icao != aerodromo.icao
                    or not indice
                    or parsed_link.scheme != "https"
                    or not parsed_link.netloc
                ):
                    continue
                documento = {
                    "indice": indice,
                    "nome": nome or f"WAC {indice}",
                    "icao": aerodromo.icao,
                    "url": link,
                }
                chave_documento = (indice, link)
                if chave_documento not in vistos_documentos:
                    vistos_documentos.add(chave_documento)
                    documentos.append(documento)
                documentos_aerodromo.append(documento)
            if not documentos_aerodromo:
                return dict(INDISPONIVEL)
        if not documentos:
            return dict(INDISPONIVEL)
        return {
            "estado": "disponivel",
            "tipo": "pdf",
            "fonte": "AISWEB WAC",
            "documentos": documentos,
        }
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
        if texto_metar and metar.get("regional"):
            nome_estacao = (metar.get("nome_estacao") or "").strip()
            icao_estacao = (metar.get("icao") or "").strip()
            estacao = (
                f"{nome_estacao} ({icao_estacao})"
                if nome_estacao
                else icao_estacao
            )
            distancia = metar.get("distancia_nm")
            if (
                isinstance(distancia, (int, float))
                and not isinstance(distancia, bool)
                and math.isfinite(distancia)
            ):
                texto_distancia = f"{distancia:.1f} NM"
            else:
                texto_distancia = "distância indisponível"
            referencia = metar.get("aerodromo_referencia") or "aeródromo solicitado"
            hora = (metar.get("hora") or "").strip()
            texto_hora = f"; observado {hora} UTC" if hora else ""
            linhas.append(
                f"METAR regional {rotulo}: estação {estacao}, "
                f"{texto_distancia} do aeródromo {referencia}"
                f"{texto_hora}: {texto_metar}"
            )
        else:
            linhas.append(
                f"METAR {rotulo}: {texto_metar}"
                if texto_metar
                else f"METAR {rotulo}: indisponível"
            )
        taf = bloco.get("taf")
        texto_taf = taf.get("raw").strip() if isinstance(taf, dict) and isinstance(taf.get("raw"), str) else ""
        if texto_taf and taf.get("estado") != "indisponivel":
            linhas.append(f"TAF {rotulo}: {texto_taf}")
        else:
            linhas.append(f"TAF {rotulo}: indisponível")
    return linhas


def meteorologia_rota(origem, destino, getter=None, *, aerodromos=None):
    lugares = list(aerodromos or (origem, destino))
    for lugar in (origem, destino):
        if all(aero.icao != lugar.icao for aero in lugares):
            lugares.append(lugar)
    boletins = {}
    for lugar in lugares:
        if lugar.icao in boletins:
            continue
        boletim = meteorologia(lugar.icao, getter)
        if not isinstance(boletim.get("metar"), dict):
            metar_regional = _metar_regional(lugar, getter)
            if metar_regional:
                boletim["metar"] = metar_regional
                boletim["estado"] = "disponivel"
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
    return meteorologia_plano


def buscar(origem, destino, getter=None, *, aerodromos=None, vento=None):
    meteorologia_plano = meteorologia_rota(
        origem,
        destino,
        getter,
        aerodromos=aerodromos,
    )
    return {
        "meteorologia": meteorologia_plano,
        "vento": vento if vento is not None else vento_area(origem, destino, getter),
        "carta": carta(origem, destino, getter, aerodromos),
        "radar": dict(INDISPONIVEL),
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
        if chave == "fenomenos" and isinstance(valor, str) and valor.strip():
            campos[-1]["explicacao"] = _traduzir_fenomenos(valor)
    return campos


_FENOMENOS_METEO = (
    "DZ", "RA", "SN", "SG", "IC", "PL", "GR", "GS", "UP",
    "BR", "FG", "FU", "VA", "DU", "SA", "HZ", "PY", "TS",
    "PO", "SQ", "FC", "SS", "DS", "NSW",
)
_DESCRITORES_METEO = ("MI", "PR", "BC", "DR", "BL", "SH", "TS", "FZ")
_DESCRICAO_FENOMENO = {
    "DZ": "chuvisco",
    "RA": "chuva",
    "SN": "neve",
    "SG": "grãos de neve",
    "IC": "cristais de gelo",
    "PL": "pelotas de gelo",
    "GR": "granizo",
    "GS": "granizo pequeno ou pelotas de neve",
    "UP": "precipitação não especificada",
    "BR": "névoa úmida",
    "FG": "nevoeiro",
    "FU": "fumaça",
    "VA": "cinzas vulcânicas",
    "DU": "poeira",
    "SA": "areia",
    "HZ": "névoa seca",
    "PY": "borrifo",
    "PO": "redemoinhos de poeira ou areia",
    "SQ": "rajada de vento",
    "FC": "nuvem funil ou tornado",
    "TS": "trovoada",
    "SS": "tempestade de areia",
    "DS": "tempestade de poeira",
}
_PRECIPITACAO_METEO = {"DZ", "RA", "SN", "SG", "IC", "PL", "GR", "GS", "UP"}
_INTENSIDADE_METEO = {"-": "fraca", "+": "forte"}
_INTENSIDADE_PANCADAS_METEO = {"-": "fracas", "+": "fortes"}
_COBERTURA_NUVENS = {
    "FEW": "poucas nuvens",
    "SCT": "nuvens esparsas",
    "BKN": "nuvens fragmentadas",
    "OVC": "céu encoberto",
    "VV": "visibilidade vertical",
}


def _traduzir_token_fenomeno(token):
    original = token.strip()
    codigo = original.upper()
    if codigo == "NSW":
        return "Sem fenômenos meteorológicos significativos"

    intensidade = codigo[0] if codigo[:1] in {"+", "-"} else ""
    if intensidade:
        codigo = codigo[1:]
    nas_proximidades = codigo.startswith("VC")
    if nas_proximidades:
        codigo = codigo[2:]

    descritor = ""
    for candidato in _DESCRITORES_METEO:
        if codigo.startswith(candidato) and len(codigo) > len(candidato):
            descritor = candidato
            codigo = codigo[len(candidato):]
            break

    fenomenos = []
    restante = codigo
    codigos_ordenados = sorted(_DESCRICAO_FENOMENO, key=len, reverse=True)
    while restante:
        encontrado = next(
            (item for item in codigos_ordenados if restante.startswith(item)),
            None,
        )
        if encontrado is None:
            break
        fenomenos.append(encontrado)
        restante = restante[len(encontrado):]

    if not fenomenos:
        return f"Código não interpretado: {original}"

    nomes = []
    intensidade_aplicada = False
    for fenomeno in fenomenos:
        nome = _DESCRICAO_FENOMENO[fenomeno]
        if descritor == "FZ":
            nome = f"{nome} congelante"
        if (
            intensidade
            and not intensidade_aplicada
            and descritor != "SH"
            and fenomeno in _PRECIPITACAO_METEO
        ):
            nome = f"{nome} {_INTENSIDADE_METEO[intensidade]}"
            intensidade_aplicada = True
        nomes.append(nome)

    if descritor == "SH":
        intensidade_texto = _INTENSIDADE_PANCADAS_METEO.get(intensidade)
        modificador = f" {intensidade_texto}" if intensidade_texto else ""
        descricao = f"Pancadas{modificador} de {' e '.join(nomes)}"
    elif descritor == "TS":
        conteudo = " e ".join(nomes)
        descricao = (
            f"Trovoada com {conteudo}"
            if fenomenos != ["TS"]
            else "Trovoada"
        )
    elif descritor == "FZ":
        descricao = " e ".join(nomes)
    elif descritor == "MI":
        descricao = "Raso " + " e ".join(nomes)
    elif descritor == "PR":
        descricao = "Parcial " + " e ".join(nomes)
    elif descritor == "BC":
        descricao = "Bancos de " + " e ".join(nomes)
    elif descritor == "DR":
        descricao = " ".join(nomes) + " levantada pelo vento perto do solo"
    elif descritor == "BL":
        descricao = " ".join(nomes) + " soprada pelo vento"
    else:
        descricao = " e ".join(nomes)

    if nas_proximidades:
        descricao += " nas proximidades"
    if restante:
        descricao += f"; código não interpretado: {restante}"
    return descricao[0].upper() + descricao[1:]


def _traduzir_fenomenos(codigos):
    return "; ".join(
        _traduzir_token_fenomeno(token)
        for token in codigos.split()
    )


def _campo_taf(nome, valor, unidade=""):
    return {"nome": nome, "valor": valor, "unidade": unidade}


def _fenomeno_metar_taf(token):
    sequencia = r"(?:DZ|RA|SN|SG|IC|PL|GR|GS|UP|BR|FG|FU|VA|DU|SA|HZ|PY|PO|SQ|FC|TS|SS|DS|NSW)+"
    descritores = r"(?:(?:MI|PR|BC|DR|BL|SH|TS|FZ))*"
    return re.fullmatch(
        rf"(?:[+-])?(?:VC)?{descritores}{sequencia}",
        token.upper(),
    ) is not None


def _campos_grupo_taf(tokens):
    campos = []
    for token in tokens:
        vento = re.fullmatch(
            r"(VRB|\d{3})(\d{2,3})(?:G(\d{2,3}))?KT",
            token,
            re.IGNORECASE,
        )
        temperatura = re.fullmatch(
            r"T([NX])(\d{2})/(\d{2})(\d{2})Z",
            token,
            re.IGNORECASE,
        )
        if temperatura:
            extremo, valor, dia, hora = temperatura.groups()
            nome = (
                "Temperatura máxima"
                if extremo.upper() == "X"
                else "Temperatura mínima"
            )
            campos.append(_campo_taf(nome, str(int(valor)), "°C"))
            campos.append(
                _campo_taf(
                    "Horário da temperatura",
                    f"dia {int(dia)}, {hora} UTC",
                    "UTC",
                )
            )
            continue

        if vento:
            direcao, velocidade, rajada = vento.groups()
            campos.append(
                _campo_taf(
                    "Direção do vento",
                    "Variável" if direcao.upper() == "VRB" else direcao,
                    "código" if direcao.upper() == "VRB" else "graus",
                )
            )
            campos.append(
                _campo_taf("Velocidade do vento", str(int(velocidade)), "kt")
            )
            if rajada:
                campos.append(_campo_taf("Rajada", str(int(rajada)), "kt"))
            continue

        variacao = re.fullmatch(r"(\d{3})V(\d{3})", token, re.IGNORECASE)
        if variacao:
            campos.append(
                _campo_taf(
                    "Variação da direção",
                    f"{variacao.group(1)} a {variacao.group(2)}",
                    "graus",
                )
            )
            continue

        if token.upper() == "CAVOK":
            campos.append(_campo_taf("Visibilidade", "CAVOK", "código"))
            continue
        if re.fullmatch(r"\d{4}", token):
            campos.append(
                _campo_taf(
                    "Visibilidade",
                    "10 km ou mais" if token == "9999" else token,
                    "km" if token == "9999" else "m",
                )
            )
            continue

        nuvens = re.fullmatch(
            r"(FEW|SCT|BKN|OVC|VV)(\d{3})(CB|TCU)?",
            token,
            re.IGNORECASE,
        )
        if nuvens:
            cobertura, base, tipo = nuvens.groups()
            base_ft = int(base) * 100
            descricao = _COBERTURA_NUVENS[cobertura.upper()]
            if tipo:
                descricao = f"{descricao}; {tipo.upper()}"
            campos.append(
                _campo_taf(
                    "Nuvens",
                    f"{token.upper()} — {descricao}, base {base_ft:,} ft".replace(",", "."),
                    "ft",
                )
            )
            continue

        cobertura = token.upper()
        if cobertura in {"NSC", "NCD", "SKC", "CLR"}:
            descricoes = {
                "NSC": "sem nuvens significativas",
                "NCD": "nuvens não detectadas",
                "SKC": "céu claro",
                "CLR": "sem nuvens abaixo de 12.000 ft",
            }
            campos.append(
                _campo_taf("Nuvens", f"{cobertura} — {descricoes[cobertura]}", "código")
            )
            continue

        if _fenomeno_metar_taf(token):
            campo = _campo_taf("Fenômenos meteorológicos", token.upper(), "código")
            campo["explicacao"] = _traduzir_fenomenos(token)
            campos.append(campo)
            continue

        campos.append(
            {
                **_campo_taf("Código não interpretado", token, ""),
                "explicacao": "Código não interpretado; não foi atribuída uma descrição.",
            }
        )
    return campos


def legenda_periodo_taf(periodo):
    """Traduz DDH1H1/DDH2H2. Hora 24 é o fim daquele dia."""
    texto = (periodo or "").strip()
    casamento = re.fullmatch(r"(\d{2})(\d{2})/(\d{2})(\d{2})", texto)
    if not casamento:
        return texto

    def instante(dia, hora):
        if hora == "24":
            return f"fim do dia {int(dia)}"
        return f"dia {int(dia)}, {hora} UTC"

    dia1, hora1, dia2, hora2 = casamento.groups()
    return f"{texto} ({instante(dia1, hora1)} até {instante(dia2, hora2)})"


def vento_de_boletim(bloco):
    """Vento numérico do METAR ou, na falta dele, do TAF. VRB não entra na conta."""
    if not isinstance(bloco, dict):
        return None
    metar = bloco.get("metar") if isinstance(bloco.get("metar"), dict) else None
    if metar:
        direcao = metar.get("direcao_vento")
        velocidade = metar.get("vento_kt")
        if (
            isinstance(direcao, (int, float))
            and not isinstance(direcao, bool)
            and isinstance(velocidade, (int, float))
            and not isinstance(velocidade, bool)
            and 0 <= float(direcao) <= 360
            and 0 <= float(velocidade) <= 200
        ):
            return {
                "direcao_de_graus": int(direcao),
                "velocidade_kt": float(velocidade),
                "fonte": "METAR",
            }
        lido = _vento_numerico_texto(metar.get("raw"))
        if lido:
            return {
                "direcao_de_graus": lido[0],
                "velocidade_kt": lido[1],
                "fonte": "METAR",
            }
    taf = bloco.get("taf") if isinstance(bloco.get("taf"), dict) else None
    if taf:
        lido = _vento_numerico_texto(taf.get("raw"))
        if lido:
            return {
                "direcao_de_graus": lido[0],
                "velocidade_kt": lido[1],
                "fonte": "TAF",
            }
    return None


def _vento_numerico_texto(texto):
    if not isinstance(texto, str):
        return None
    casamento = re.search(
        r"\b(\d{3})(\d{2,3})(?:G\d{2,3})?KT\b",
        texto,
        re.IGNORECASE,
    )
    if not casamento:
        return None
    direcao = int(casamento.group(1))
    velocidade = int(casamento.group(2))
    if direcao > 360 or velocidade > 200:
        return None
    return direcao, float(velocidade)


def campos_taf(taf):
    observacao = taf if isinstance(taf, dict) else {}
    bruto = observacao.get("raw")
    if not isinstance(bruto, str) or not bruto.strip():
        return []

    tokens = [
        token.rstrip("=")
        for token in bruto.replace("BEC-MG", "BECMG").replace("bec-mg", "BECMG").split()
    ]
    tokens = [token for token in tokens if token]
    try:
        inicio_periodo = next(
            indice
            for indice, token in enumerate(tokens)
            if re.fullmatch(r"\d{4}/\d{4}", token)
        )
    except StopIteration:
        return []

    grupos = [
        {
            "tipo": "Previsão base",
            "periodo": tokens[inicio_periodo],
            "campos": [],
        }
    ]
    acumulados = []

    def concluir_grupo():
        if acumulados:
            grupos[-1]["campos"] = _campos_grupo_taf(acumulados.copy())
            acumulados.clear()

    indice = inicio_periodo + 1
    while indice < len(tokens):
        token = tokens[indice]
        fm = re.fullmatch(r"FM(\d{6})", token, re.IGNORECASE)
        if fm:
            concluir_grupo()
            grupos.append(
                {
                    "tipo": "FM",
                    "periodo": f"{fm.group(1)}Z",
                    "campos": [],
                }
            )
        elif token.upper() in {"BECMG", "TEMPO"}:
            concluir_grupo()
            periodo = tokens[indice + 1] if indice + 1 < len(tokens) else ""
            grupos.append(
                {
                    "tipo": token.upper(),
                    "periodo": periodo,
                    "campos": [],
                }
            )
            indice += bool(periodo)
        elif re.fullmatch(r"PROB\d{2}", token, re.IGNORECASE):
            concluir_grupo()
            tipo = token.upper()
            proximo = tokens[indice + 1] if indice + 1 < len(tokens) else ""
            if proximo.upper() == "TEMPO":
                tipo = f"{tipo} TEMPO"
                indice += 1
                proximo = tokens[indice + 1] if indice + 1 < len(tokens) else ""
            grupos.append(
                {
                    "tipo": tipo,
                    "periodo": proximo,
                    "campos": [],
                }
            )
            indice += bool(proximo)
        else:
            acumulados.append(token)
        indice += 1

    concluir_grupo()
    return grupos
