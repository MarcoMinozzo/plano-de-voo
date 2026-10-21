from math import asin, atan2, cos, degrees, radians, sin, sqrt

from servidor.modelos import Aeronave

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


def distancia_km(lat1, lon1, lat2, lon2):
    raio = 6371.0
    p1, p2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlmb = radians(lon2 - lon1)
    a = sin(dphi / 2) ** 2 + cos(p1) * cos(p2) * sin(dlmb / 2) ** 2
    return 2 * raio * asin(sqrt(a))


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
    nm = km * 0.539957
    tas = float(aeronave.velocidade_valor)
    proa = proa_graus(origem.lat, origem.lon, destino.lat, destino.lon)
    fonte_manual = aeronave.fonte_manual
    vento_aplicado = False
    efeito = "vento não aplicado"
    gs = tas
    if vento and vento.get("estado") == "disponivel":
        vem_de = float(vento["direcao_de_graus"])
        velocidade = float(vento["velocidade_kt"])
        proa_rad = radians(proa)
        vento_rad = radians(vem_de)
        componente = velocidade * cos(vento_rad - proa_rad)
        gs = tas - componente
        vento_aplicado = True
        if componente >= 0:
            efeito = f"vento de proa {componente:.0f} kt"
        else:
            efeito = f"vento de cauda {abs(componente):.0f} kt"
        if gs <= 0:
            return {"erro": "vento de proa maior que a velocidade de planejamento", "grava": False}

    horas = nm / gs
    consumo = float(aeronave.consumo_valor)
    necessario = horas * consumo
    reserva = RESERVA_HORAS * consumo
    total = necessario + reserva

    peso_piloto = float(particulares["peso_piloto_kg"])
    peso_passageiro = float(particulares["peso_passageiro_kg"])
    peso_bagagem = float(particulares["peso_bagagem_kg"])
    combustivel_gal = float(particulares["combustivel_a_bordo_gal"])
    peso_combustivel = combustivel_gal * KG_POR_GAL
    peso_total = (
        float(aeronave.peso_vazio_kg)
        + peso_piloto
        + peso_passageiro
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
    if total > float(aeronave.combustivel_valor):
        alertas.append(
            f"Combustível necessário {total:.1f} {aeronave.combustivel_unidade} "
            f"acima do planejamento {aeronave.combustivel_valor:.1f} {aeronave.combustivel_unidade}"
        )

    fonte_coord = f"coordenadas de {origem.icao} e {destino.icao}, {origem.fonte}"
    linhas = [
        _linha("Distância", round(km, 1), "km", fonte_coord),
        _linha("Distância", round(nm, 1), "nm", fonte_coord),
        _linha("Proa", round(proa, 0), "graus", fonte_coord),
        _linha("Velocidade de planejamento", tas, aeronave.velocidade_unidade, fonte_manual),
        _linha("Velocidade em relação ao solo", round(gs, 1), "kt", fonte_manual if not vento_aplicado else vento.get("fonte", fonte_manual)),
        _linha("Tempo de voo", round(horas, 2), "h", fonte_manual),
        _linha("Combustível de voo", round(necessario, 2), aeronave.consumo_unidade.split("/")[0], fonte_manual),
        _linha("Reserva", round(reserva, 2), aeronave.combustivel_unidade, FONTE_RESERVA),
        _linha("Combustível necessário", round(total, 2), aeronave.combustivel_unidade, fonte_manual),
        _linha("Peso total", round(peso_total, 1), "kg", fonte_manual),
        _linha("Peso de combustível", round(peso_combustivel, 1), "kg", FONTE_AVGAS),
    ]
    return {
        "grava": True,
        "aceitavel": len(alertas) == 0,
        "alertas": alertas,
        "linhas": linhas,
        "efeito_vento": efeito,
        "proa_graus": round(proa, 0),
        "velocidade_solo_kt": round(gs, 1),
    }
