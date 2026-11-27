from datetime import datetime, time, timedelta, timezone
from math import isfinite


UTC = timezone.utc
INTERVALO_ABASTECIMENTO = timedelta(hours=1)


def _hora_utc(valor):
    if isinstance(valor, str):
        try:
            valor = datetime.fromisoformat(
                valor[:-1] + "+00:00" if valor.endswith("Z") else valor
            )
        except ValueError:
            return None
    if not isinstance(valor, datetime) or valor.tzinfo is None:
        return None
    try:
        return valor.astimezone(UTC)
    except (OverflowError, ValueError):
        return None


def _solar_utc(valor, data):
    instante = _hora_utc(valor)
    if (
        instante is None
        or getattr(valor, "tzinfo", None) is None
        or valor.utcoffset() != timedelta(0)
        or instante.date() != data
    ):
        return None
    return instante


def _normalizar_solar(resposta, data):
    if not isinstance(resposta, dict) or resposta.get("estado") != "disponivel":
        return None
    if resposta.get("fonte") != "AISWEB sol":
        return None
    nascer = _solar_utc(resposta.get("nascer_do_sol"), data)
    por = _solar_utc(resposta.get("por_do_sol"), data)
    if nascer is None or por is None or nascer >= por:
        return None
    return {
        "nascer_do_sol": nascer,
        "por_do_sol": por,
        "fonte": resposta["fonte"],
    }


def _duracao(trecho):
    valor = trecho.get("tempo_valor")
    unidade = (trecho.get("tempo_unidade") or "").strip().lower()
    if isinstance(valor, bool) or unidade != "h":
        return None
    try:
        horas = float(valor)
    except (TypeError, ValueError):
        return None
    if not isfinite(horas) or horas < 0:
        return None
    try:
        return timedelta(hours=horas)
    except OverflowError:
        return None


def _iso(instante):
    return instante.isoformat() if instante is not None else None


def _solar_para_json(icao, solar):
    return {
        "icao": icao,
        "nascer_do_sol": _iso(solar["nascer_do_sol"]) if solar else None,
        "por_do_sol": _iso(solar["por_do_sol"]) if solar else None,
    }


def _registro_indisponivel(
    trecho,
    motivo,
    origem_solar=None,
    destino_solar=None,
    pernoite=None,
):
    return {
        "ordem": trecho.get("ordem"),
        "estado": "indisponivel",
        "motivo": motivo,
        "etd": None,
        "eta": None,
        "origem": _solar_para_json(trecho.get("origem"), origem_solar),
        "destino": _solar_para_json(trecho.get("destino"), destino_solar),
        "pernoite": pernoite,
        "fonte": "AISWEB sol",
    }


def _resposta_indisponivel(trechos, motivo):
    return {
        "estado": "indisponivel",
        "motivo": motivo,
        "fuso": "UTC",
        "trechos": [
            _registro_indisponivel(trecho, motivo)
            for trecho in trechos
        ],
    }


def programar(trechos, hora_partida, consultar_sol):
    """Calcula os horários UTC por trecho usando somente pares solares AISWEB."""
    solicitada = _hora_utc(hora_partida)
    if solicitada is None:
        return _resposta_indisponivel(trechos, "hora_partida_invalida")
    ordenados = sorted(trechos, key=lambda trecho: trecho.get("ordem", 0))
    if not ordenados:
        return _resposta_indisponivel([], "rota_sem_trechos")

    cache = {}

    def obter_sol(icao, instante):
        chave = (icao, instante.date())
        if chave not in cache:
            cache[chave] = _normalizar_solar(
                consultar_sol(icao, instante),
                instante.date(),
            )
        return cache[chave]

    programados = []
    candidato = solicitada
    for indice, trecho in enumerate(ordenados):
        origem = trecho.get("origem")
        destino = trecho.get("destino")
        duracao = _duracao(trecho)
        if not isinstance(origem, str) or not origem or not isinstance(destino, str) or not destino:
            motivo = "trecho_invalido"
            programados.append(_registro_indisponivel(trecho, motivo))
            programados.extend(
                _registro_indisponivel(pendente, "programacao_interrompida")
                for pendente in ordenados[indice + 1 :]
            )
            return {
                "estado": "indisponivel",
                "motivo": motivo,
                "fuso": "UTC",
                "trechos": programados,
            }
        if duracao is None:
            motivo = "duracao_indisponivel"
            programados.append(_registro_indisponivel(trecho, motivo))
            programados.extend(
                _registro_indisponivel(pendente, "programacao_interrompida")
                for pendente in ordenados[indice + 1 :]
            )
            return {
                "estado": "indisponivel",
                "motivo": motivo,
                "fuso": "UTC",
                "trechos": programados,
            }

        pernoite = None
        origem_solar = None
        destino_solar = None
        motivo = None
        tentativa = candidato
        for numero_tentativa in range(2):
            origem_solar = obter_sol(origem, tentativa)
            if origem_solar is None:
                motivo = "dados_solares_indisponiveis"
                break

            etd = max(tentativa, origem_solar["nascer_do_sol"])
            if etd > origem_solar["por_do_sol"]:
                excedeu_janela = True
            else:
                eta = etd + duracao
                destino_solar = obter_sol(destino, eta)
                if destino_solar is None:
                    motivo = "dados_solares_indisponiveis"
                    break
                excedeu_janela = eta > destino_solar["por_do_sol"]
                if not excedeu_janela and eta >= etd:
                    programados.append(
                        {
                            "ordem": trecho.get("ordem"),
                            "estado": "disponivel",
                            "etd": _iso(etd),
                            "eta": _iso(eta),
                            "origem": _solar_para_json(origem, origem_solar),
                            "destino": _solar_para_json(destino, destino_solar),
                            "pernoite": pernoite,
                            "fonte": "AISWEB sol",
                        }
                    )
                    candidato = eta + INTERVALO_ABASTECIMENTO
                    break

            if numero_tentativa == 1:
                motivo = "nao_cabe_no_periodo_diurno"
                break

            pernoite = {
                "icao": origem,
                "data": tentativa.date().isoformat(),
            }
            proxima_data = tentativa.date() + timedelta(days=1)
            meia_noite = datetime.combine(proxima_data, time.min, tzinfo=UTC)
            proxima_origem = obter_sol(origem, meia_noite)
            if proxima_origem is None:
                motivo = "dados_solares_indisponiveis"
                break
            tentativa = proxima_origem["nascer_do_sol"]

        if motivo is not None:
            programados.append(
                _registro_indisponivel(
                    trecho,
                    motivo,
                    origem_solar,
                    destino_solar,
                    pernoite,
                )
            )
            programados.extend(
                _registro_indisponivel(pendente, "programacao_interrompida")
                for pendente in ordenados[indice + 1 :]
            )
            return {
                "estado": "indisponivel",
                "motivo": motivo,
                "fuso": "UTC",
                "trechos": programados,
            }

    return {
        "estado": "disponivel",
        "fuso": "UTC",
        "intervalo_abastecimento_h": 1,
        "trechos": programados,
    }
