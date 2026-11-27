import math
import os
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from xml.etree import ElementTree

import requests

from servidor.modelos import Aerodromo
from servidor.rotaer_parse import (
    _data_rotaer,
    _contatos_rotaer_elemento,
    _detalhe_rotaer_html,
    _interpretar_pagina_rotaer,
    _numero_rotaer,
    _tag,
    _texto,
    _tipo_lugar,
    interpretar_rotaer,
)


URL_AISWEB = "https://api.decea.mil.br/aisweb/"

TIMEOUT = 30

TAMANHO_PAGINA_ROTAER = 100

CONCORRENCIA_ROTAER = 4


def _chaves_aisweb():
    chave = os.environ.get("AISWEB_API_KEY", "").strip()
    senha = os.environ.get("AISWEB_API_PASS", "").strip()
    return chave, senha


def _buscar_detalhe_rotaer_html(item, obter, chave, senha):
    resposta = obter(
        URL_AISWEB,
        params={
            "apiKey": chave,
            "apiPass": senha,
            "area": "rotaer",
            "icaoCode": item["icao"],
            "force": "html",
        },
        timeout=TIMEOUT,
    )
    resposta.raise_for_status()
    return _detalhe_rotaer_html(resposta.text or "", item)


def _detalhe_rotaer(item, obter, chave, senha):
    resposta = obter(
        URL_AISWEB,
        params={
            "apiKey": chave,
            "apiPass": senha,
            "area": "rotaer",
            "icaoCode": item["icao"],
        },
        timeout=TIMEOUT,
    )
    resposta.raise_for_status()
    try:
        raiz = ElementTree.fromstring(resposta.text or "")
    except ElementTree.ParseError:
        return _buscar_detalhe_rotaer_html(item, obter, chave, senha)
    icao = _texto(raiz, "AeroCode", "icao", "identificador").upper()
    if icao != item["icao"]:
        return _buscar_detalhe_rotaer_html(item, obter, chave, senha)
    if _tipo_lugar(_texto(raiz, "type", "tipo")) != "aerodromo":
        raise ValueError(f"tipo AISWEB inválido para {icao}")
    atualizado_em = _data_rotaer(_texto(raiz, "dt"), icao)
    if atualizado_em != item["rotaer_atualizado_em"]:
        raise ValueError(f"versão AISWEB mudou durante a carga de {icao}")
    lat = _numero_rotaer(_texto(raiz, "lat", "latitude"), "lat", icao)
    lon = _numero_rotaer(_texto(raiz, "lng", "lon", "longitude"), "lng", icao)
    if not -90 <= lat <= 90:
        raise ValueError(f"campo lat fora do intervalo válido para {icao}")
    if not -180 <= lon <= 180:
        raise ValueError(f"campo lng fora do intervalo válido para {icao}")
    return {
        "lat": lat,
        "lon": lon,
        "elev_m": _numero_rotaer(
            _texto(raiz, "altM", "elev_m", "elevacao"), "altM", icao
        ),
        **_contatos_rotaer_elemento(raiz),
    }


def _pagina_rotaer(obter, chave, senha, inicio, total):
    resposta = obter(
        URL_AISWEB,
        params={
            "apiKey": chave,
            "apiPass": senha,
            "area": "rotaer",
            "rowstart": inicio,
            "rowend": TAMANHO_PAGINA_ROTAER,
            "type": "AD",
        },
        timeout=TIMEOUT,
    )
    resposta.raise_for_status()
    pagina = _interpretar_pagina_rotaer(resposta.text or "")
    if pagina is None:
        if inicio == 0:
            codigo_legado, registros_legados = interpretar_rotaer(resposta.text or "")
            if codigo_legado and registros_legados:
                return codigo_legado, None, 0, registros_legados
        raise ValueError("resposta AISWEB sem lista ROTAER reconhecível")
    total_pagina, quantidade, registros = pagina
    if total is not None and total != total_pagina:
        raise ValueError("total ROTAER mudou durante a paginação")
    total = total_pagina if total is None else total
    if quantidade == 0 and inicio < total:
        raise ValueError("página ROTAER vazia antes do total anunciado")
    return None, total, quantidade, registros


def _baixar_lista_rotaer(obter, chave, senha, progresso):
    lista = []
    total = None
    inicio = 0
    codigo = "AISWEB ROTAER vigente"
    while total is None or inicio < total:
        legado, total, quantidade, registros_pagina = _pagina_rotaer(
            obter, chave, senha, inicio, total
        )
        if legado:
            return legado, registros_pagina, None
        lista.extend(registros_pagina)
        inicio += quantidade
        if progresso:
            progresso("lista", min(inicio, total), total, 0)
    if total is None or total == 0 or inicio != total or not lista:
        raise ValueError("lista ROTAER vazia ou incompleta")
    return codigo, lista, total


def _validar_lista_rotaer(lista, total):
    por_icao = {}
    for item in lista:
        anterior = por_icao.get(item["icao"])
        if anterior is not None:
            raise ValueError(f"ICAO duplicado na lista ROTAER: {item['icao']}")
        por_icao[item["icao"]] = item
    lista = list(por_icao.values())
    if len(lista) != total:
        raise ValueError("quantidade de aeródromos ROTAER não corresponde ao total")
    return lista


def _valores_cache_rotaer(item, cache):
    existente = cache.get(item["icao"], {})
    if not existente.get("contatos_rotaer_verificados"):
        return None
    try:
        valores = {campo: float(existente[campo]) for campo in ("lat", "lon", "elev_m")}
    except (KeyError, TypeError, ValueError, OverflowError):
        return None
    if (
        existente.get("rotaer_versao_id") != item["rotaer_versao_id"]
        or existente.get("rotaer_atualizado_em") != item["rotaer_atualizado_em"]
        or not all(math.isfinite(valor) for valor in valores.values())
        or not -90 <= valores["lat"] <= 90
        or not -180 <= valores["lon"] <= 180
    ):
        return None
    valores["telefone"] = existente.get("telefone")
    valores["email"] = existente.get("email")
    valores["contatos_rotaer_verificados"] = True
    return valores


def _separar_detalhes_em_cache(lista, cache):
    detalhes = {}
    pendentes = []
    for item in lista:
        valores = _valores_cache_rotaer(item, cache)
        if valores is None:
            pendentes.append(item)
        else:
            detalhes[item["icao"]] = valores
    return detalhes, pendentes


def _baixar_detalhes_pendentes(
    pendentes, lista, detalhes, obter, chave, senha, progresso
):
    concluidos = len(detalhes)
    reutilizados = concluidos
    if progresso:
        progresso("detalhes", concluidos, len(lista), reutilizados)

    with ThreadPoolExecutor(max_workers=CONCORRENCIA_ROTAER) as executor:
        iterador = iter(pendentes)
        futures = {}
        for _ in range(CONCORRENCIA_ROTAER):
            item = next(iterador, None)
            if item is not None:
                futures[executor.submit(_detalhe_rotaer, item, obter, chave, senha)] = (
                    item
                )
        while futures:
            concluidas, _ = wait(futures, return_when=FIRST_COMPLETED)
            for futuro in concluidas:
                item = futures.pop(futuro)
                detalhes[item["icao"]] = futuro.result()
                concluidos += 1
                if progresso:
                    progresso("detalhes", concluidos, len(lista), reutilizados)
                proximo = next(iterador, None)
                if proximo is not None:
                    futures[
                        executor.submit(_detalhe_rotaer, proximo, obter, chave, senha)
                    ] = proximo


def _baixar_rotaer(getter=None, cache=None, progresso=None):
    chave, senha = _chaves_aisweb()
    obter = getter or requests.get
    codigo, lista, total = _baixar_lista_rotaer(obter, chave, senha, progresso)
    if total is None:
        return codigo, lista
    lista = _validar_lista_rotaer(lista, total)
    cache = cache or {}
    detalhes, pendentes = _separar_detalhes_em_cache(lista, cache)
    _baixar_detalhes_pendentes(
        pendentes, lista, detalhes, obter, chave, senha, progresso
    )

    registros = []
    for item in lista:
        registros.append({**item, **detalhes[item["icao"]]})
    return codigo, registros


def _cache_rotaer(db):
    return {
        item.icao: {
            "rotaer_versao_id": item.rotaer_versao_id,
            "rotaer_atualizado_em": item.rotaer_atualizado_em,
            "lat": item.lat,
            "lon": item.lon,
            "elev_m": item.elev_m,
            "telefone": item.telefone,
            "email": item.email,
            "contatos_rotaer_verificados": item.contatos_rotaer_verificados,
        }
        for item in db.query(Aerodromo).all()
        if item.rotaer_versao_id and item.rotaer_atualizado_em
    }


def _instante_solar_utc(texto, data):
    from datetime import datetime, timezone

    bruto = (texto or "").strip()
    if bruto.upper().endswith(" UTC"):
        bruto = bruto[:-4].strip()
    if len(bruto) == 5 and bruto[2] == ":":
        try:
            hora = int(bruto[:2])
            minuto = int(bruto[3:])
        except ValueError:
            return None
        if hora > 23 or minuto > 59:
            return None
        return datetime(data.year, data.month, data.day, hora, minuto, tzinfo=timezone.utc)
    try:
        instante = datetime.fromisoformat(
            bruto[:-1] + "+00:00" if bruto.endswith("Z") else bruto
        )
    except ValueError:
        return None
    from datetime import timedelta

    if (
        instante.tzinfo is None
        or instante.utcoffset() != timedelta(0)
        or instante.date() != data
    ):
        return None
    return instante.astimezone(timezone.utc)


def sol_aerodromo(icao, hora, getter=None):
    from datetime import datetime, timedelta

    if os.environ.get("PLANO_CONSULTAR_SOL", "1") == "0":
        return {"estado": "indisponivel"}
    if (
        not isinstance(hora, datetime)
        or hora.tzinfo is None
        or hora.utcoffset() != timedelta(0)
        or not isinstance(icao, str)
        or not icao.strip()
    ):
        return {"estado": "indisponivel"}
    chave, senha = _chaves_aisweb()
    if not chave or not senha:
        return {"estado": "indisponivel"}
    data = hora.date().isoformat()
    obter = getter or requests.get
    try:
        resposta = obter(
            URL_AISWEB,
            params={
                "apiKey": chave,
                "apiPass": senha,
                "area": "sol",
                "icaoCode": icao,
                "dt_i": data,
                "dt_f": data,
            },
            timeout=8,
        )
        resposta.raise_for_status()
        raiz = ElementTree.fromstring(resposta.text or "")
    except Exception:
        return {"estado": "indisponivel"}
    nascer = None
    por = None
    for dia in raiz.iter():
        if _tag(dia) != "day":
            continue
        campos = {
            _tag(filho): (filho.text or "").strip()
            for filho in list(dia)
        }
        aero = (campos.get("aero") or "").upper()
        if campos.get("date") != data or (aero and aero != icao.upper()):
            continue
        nascer = _instante_solar_utc(campos.get("sunrise"), hora.date())
        por = _instante_solar_utc(campos.get("sunset"), hora.date())
        break
    if nascer is None or por is None or nascer >= por:
        return {"estado": "indisponivel"}
    return {
        "estado": "disponivel",
        "nascer_do_sol": nascer,
        "por_do_sol": por,
        "fonte": "AISWEB sol",
    }
