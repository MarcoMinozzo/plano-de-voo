from math import asin, atan2, cos, degrees, radians, sin, sqrt

from servidor.modelos import Aeronave
from servidor.proveniencia import formatar_fonte

FONTE_RESERVA = "voo visual diurno, reserva de 30 min"
FONTE_AVGAS = "densidade de avgas 2,72 kg/gal"
RESERVA_HORAS = 0.5
KG_POR_GAL = 2.72


def _linha(nome, valor, unidade, fonte):
    return {"nome": nome, "valor": valor, "unidade": unidade, "fonte": fonte}


def campo_tecnico_faltando(aeronave):
    obrigatorios = (
        "velocidade_valor",
        "consumo_valor",
        "peso_vazio_kg",
        "peso_max_decolagem_kg",
        "bagagem_max_kg",
        "combustivel_valor",
    )
    for nome in obrigatorios:
        if getattr(aeronave, nome, None) is None:
            return nome
    return None


NM_POR_KM = 0.539957


def distancia_km(lat1, lon1, lat2, lon2):
    raio = 6371.0
    p1, p2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlmb = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(p1) * cos(p2) * sin(dlmb / 2) ** 2
    return 2 * raio * asin(sqrt(a))


def distancia_nm(lat1, lon1, lat2, lon2):
    return distancia_km(lat1, lon1, lat2, lon2) * NM_POR_KM


def _cargas(particulares):
    bruto = dict(particulares or {})
    if "peso_pessoas_kg" not in bruto:
        piloto = bruto.get("peso_piloto_kg")
        passageiro = bruto.get("peso_passageiro_kg")
        if piloto not in (None, "") or passageiro not in (None, ""):
            bruto["peso_pessoas_kg"] = float(piloto or 0) + float(passageiro or 0)
    return bruto.get("peso_pessoas_kg"), bruto.get("peso_bagagem_kg")


def grandezas_do_trecho(trecho, aeronave, particulares):
    """Valores já calculados que a ficha do trecho ainda não mostrava."""
    saida = {
        "distancia_km": None,
        "velocidade_solo_kt": None,
        "velocidade_planejamento": None,
        "velocidade_unidade": None,
        "combustivel_voo": None,
        "reserva": None,
        "unidade_combustivel": None,
        "peso_combustivel_kg": None,
        "peso_aeronave_kg": None,
    }
    if trecho is None:
        return saida
    if trecho.distancia_unidade == "nm" and trecho.distancia_valor is not None:
        saida["distancia_km"] = round(float(trecho.distancia_valor) / NM_POR_KM, 1)
    if trecho.velocidade_solo_kt is not None:
        saida["velocidade_solo_kt"] = trecho.velocidade_solo_kt
    if aeronave is None:
        return saida
    saida["velocidade_planejamento"] = aeronave.velocidade_valor
    saida["velocidade_unidade"] = aeronave.velocidade_unidade
    unidade = aeronave.combustivel_unidade or trecho.combustivel_unidade
    saida["unidade_combustivel"] = unidade
    if aeronave.consumo_valor is not None:
        reserva = round(RESERVA_HORAS * float(aeronave.consumo_valor), 2)
        saida["reserva"] = reserva
        if trecho.combustivel_valor is not None:
            voo = round(float(trecho.combustivel_valor) - reserva, 2)
            if voo >= 0:
                saida["combustivel_voo"] = voo
    if (
        aeronave.combustivel_valor is not None
        and (aeronave.combustivel_unidade or "").lower().startswith("gal")
    ):
        peso_comb = round(float(aeronave.combustivel_valor) * KG_POR_GAL, 1)
        saida["peso_combustivel_kg"] = peso_comb
        pessoas, bagagem = _cargas(particulares)
        if (
            aeronave.peso_vazio_kg is not None
            and pessoas is not None
            and bagagem is not None
        ):
            saida["peso_aeronave_kg"] = round(
                float(aeronave.peso_vazio_kg)
                + float(pessoas)
                + float(bagagem)
                + peso_comb,
                1,
            )
    return saida


def avaliar_carga(aeronave, particulares):
    peso_pessoas = float(particulares["peso_pessoas_kg"])
    peso_bagagem = float(particulares["peso_bagagem_kg"])
    combustivel_gal = float(aeronave.combustivel_valor)
    peso_combustivel = combustivel_gal * KG_POR_GAL
    peso_total = (
        float(aeronave.peso_vazio_kg)
        + peso_pessoas
        + peso_bagagem
        + peso_combustivel
    )
    alertas = []
    if peso_total > float(aeronave.peso_max_decolagem_kg):
        alertas.append(
            f"Peso {peso_total:.1f} kg acima do máximo de decolagem "
            f"{aeronave.peso_max_decolagem_kg:.1f} kg"
        )
    if peso_bagagem > float(aeronave.bagagem_max_kg):
        alertas.append(
            f"Bagagem {peso_bagagem:.1f} kg acima do máximo {aeronave.bagagem_max_kg:.1f} kg"
        )
    return alertas, peso_total, peso_combustivel


def componente_vento(proa_graus_valor, direcao_de_graus, velocidade_kt):
    """Componente ao longo da proa. Positivo é vento de proa."""
    alongamento = float(velocidade_kt) * cos(
        radians(float(direcao_de_graus) - float(proa_graus_valor))
    )
    sentido = "proa" if alongamento >= 0 else "cauda"
    return {
        "sentido": sentido,
        "componente_kt": int(round(abs(alongamento))),
        "alongamento_kt": alongamento,
    }


def proa_graus(lat1, lon1, lat2, lon2):
    p1, p2 = radians(lat1), radians(lat2)
    dlmb = radians(lon2 - lon1)
    y = sin(dlmb) * cos(p2)
    x = cos(p1) * sin(p2) - sin(p1) * cos(p2) * cos(dlmb)
    return (degrees(atan2(y, x)) + 360) % 360


def calcular(aeronave, origem, destino, particulares, vento=None):
    faltando = campo_tecnico_faltando(aeronave)
    if faltando:
        return {"erro": faltando, "grava": False}

    km = distancia_km(origem.lat, origem.lon, destino.lat, destino.lon)
    nm = distancia_nm(origem.lat, origem.lon, destino.lat, destino.lon)
    tas = float(aeronave.velocidade_valor)
    proa = proa_graus(origem.lat, origem.lon, destino.lat, destino.lon)
    fontes = getattr(aeronave, "procedencia_tecnica", {})
    fonte_velocidade = formatar_fonte(fontes.get("velocidade_cruzeiro"))
    fonte_consumo = formatar_fonte(fontes.get("consumo_cruzeiro"))
    fonte_vazio = formatar_fonte(fontes.get("peso_vazio"))
    fonte_bagagem = formatar_fonte(fontes.get("bagagem_maxima"))
    fonte_combustivel = formatar_fonte(fontes.get("combustivel_utilizavel"))
    if not fontes:
        fonte_velocidade = fonte_consumo = fonte_vazio = fonte_bagagem = fonte_combustivel = (
            aeronave.fonte_manual or "fonte indisponível"
        )
    vento_aplicado = False
    efeito = "vento não aplicado"
    vento_sentido = None
    vento_componente_kt = None
    vento_fonte = None
    gs = tas
    if vento and vento.get("estado") == "disponivel":
        conta_vento = componente_vento(
            proa, vento["direcao_de_graus"], vento["velocidade_kt"]
        )
        componente = conta_vento["alongamento_kt"]
        gs = tas - componente
        vento_aplicado = True
        vento_sentido = conta_vento["sentido"]
        vento_componente_kt = conta_vento["componente_kt"]
        vento_fonte = vento.get("fonte")
        efeito = f"vento de {vento_sentido} {vento_componente_kt} kt"
        if gs <= 0:
            return {"erro": "vento de proa maior que a velocidade de planejamento", "grava": False}

    horas = nm / gs
    consumo = float(aeronave.consumo_valor)
    necessario = horas * consumo
    reserva = RESERVA_HORAS * consumo
    total = necessario + reserva

    alertas_carga, peso_total, peso_combustivel = avaliar_carga(aeronave, particulares)
    alertas = list(alertas_carga)
    if total > float(aeronave.combustivel_valor):
        alertas.append(
            f"Combustível necessário {total:.1f} {aeronave.combustivel_unidade} "
            f"acima do planejamento {aeronave.combustivel_valor:.1f} {aeronave.combustivel_unidade}"
        )

    fonte_coord = f"coordenadas de {origem.icao} e {destino.icao}, {origem.fonte}"
    fonte_tempo = f"{fonte_velocidade}; {fonte_coord}"
    fonte_consumo_trecho = f"{fonte_velocidade}; {fonte_consumo}; {fonte_coord}"
    fonte_peso = (
        f"peso vazio: {fonte_vazio}; bagagem: {fonte_bagagem}; "
        f"combustível utilizável: {fonte_combustivel}"
    )
    linhas = [
        _linha("Distância", round(km, 1), "km", fonte_coord),
        _linha("Distância", round(nm, 1), "nm", fonte_coord),
        _linha("Proa", round(proa, 0), "graus", fonte_coord),
        _linha("Velocidade de planejamento", tas, aeronave.velocidade_unidade, fonte_velocidade),
    ]
    if vento_aplicado:
        linhas.append(
            _linha(
                "Velocidade em relação ao solo",
                round(gs, 1),
                "kt",
                vento.get("fonte", fonte_velocidade),
            )
        )
    linhas.extend(
        [
            _linha("Tempo de voo", round(horas, 2), "h", fonte_tempo),
            _linha(
                "Combustível de voo",
                round(necessario, 2),
                aeronave.consumo_unidade.split("/")[0],
                fonte_consumo_trecho,
            ),
            _linha(
                "Reserva",
                round(reserva, 2),
                aeronave.combustivel_unidade,
                f"{FONTE_RESERVA}; consumo: {fonte_consumo}",
            ),
            _linha(
                "Combustível necessário",
                round(total, 2),
                aeronave.combustivel_unidade,
                fonte_consumo_trecho,
            ),
            _linha("Peso total", round(peso_total, 1), "kg", fonte_peso),
            _linha(
                "Peso de combustível",
                round(peso_combustivel, 1),
                "kg",
                f"{FONTE_AVGAS}; combustível utilizável: {fonte_combustivel}",
            ),
        ]
    )
    return {
        "grava": True,
        "aceitavel": len(alertas) == 0,
        "alertas": alertas,
        "linhas": linhas,
        "efeito_vento": efeito,
        "proa_graus": round(proa, 0),
        "velocidade_solo_kt": round(gs, 1),
        "tempo_h": horas,
        "distancia_nm": nm,
        "cabe_reserva": total <= float(aeronave.combustivel_valor) + 1e-6,
        "vento_estado": "disponivel" if vento_aplicado else "indisponivel",
        "vento_sentido": vento_sentido,
        "vento_componente_kt": vento_componente_kt,
        "vento_fonte": vento_fonte,
    }
