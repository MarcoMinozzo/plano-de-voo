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
    }
