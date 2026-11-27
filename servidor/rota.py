import heapq
from collections import defaultdict
from math import floor

from servidor.calculo import RESERVA_HORAS, calcular, distancia_nm
from servidor.proveniencia import formatar_fonte

CRITERIO = "menor tempo de voo"
MOTIVO_COMBUSTIVEL = (
    "Nenhuma sequência de aeródromos publicados deixa todos os trechos dentro "
    "do combustível de planejamento e da reserva de 30 minutos."
)
def hipotese_reabastecimento(aeronave):
    fontes = getattr(aeronave, "procedencia_tecnica", {})
    fonte = (
        formatar_fonte(fontes.get("combustivel_utilizavel"))
        if fontes
        else aeronave.fonte_manual or "fonte indisponível"
    )
    return (
        "Em cada escala, a hipótese é reabastecer até o combustível de planejamento "
        f"da fonte técnica aplicável. Fonte: {fonte}."
    )


def alcance_nm(aeronave):
    consumo = float(aeronave.consumo_valor)
    if consumo <= 0:
        return 0.0
    util = float(aeronave.combustivel_valor) - RESERVA_HORAS * consumo
    if util <= 0:
        return 0.0
    return (util / consumo) * float(aeronave.velocidade_valor)


def _linha(conta, nome, unidade):
    for linha in conta["linhas"]:
        if linha["nome"] == nome and linha["unidade"] == unidade:
            return linha
    return None


def _montar_trecho(ordem, origem, destino, conta):
    distancia = _linha(conta, "Distância", "nm")
    proa = _linha(conta, "Proa", "graus")
    tempo = _linha(conta, "Tempo de voo", "h")
    combustivel = _linha(conta, "Combustível necessário", conta["linhas"][-4]["unidade"])
    for linha in conta["linhas"]:
        if linha["nome"] == "Combustível necessário":
            combustivel = linha
            break
    return {
        "ordem": ordem,
        "origem": origem.icao,
        "destino": destino.icao,
        "distancia_valor": distancia["valor"],
        "distancia_unidade": distancia["unidade"],
        "distancia_fonte": distancia["fonte"],
        "proa_valor": proa["valor"],
        "proa_unidade": proa["unidade"],
        "proa_fonte": proa["fonte"],
        "tempo_valor": tempo["valor"],
        "tempo_unidade": tempo["unidade"],
        "tempo_fonte": tempo["fonte"],
        "combustivel_valor": combustivel["valor"],
        "combustivel_unidade": combustivel["unidade"],
        "combustivel_fonte": combustivel["fonte"],
        "vento_estado": conta.get("vento_estado", "indisponivel"),
        "vento_sentido": conta.get("vento_sentido"),
        "vento_componente_kt": conta.get("vento_componente_kt"),
        "vento_fonte": conta.get("vento_fonte"),
        "por_do_sol_estado": "indisponivel",
        "velocidade_solo_kt": conta["velocidade_solo_kt"],
        "conta": conta,
    }


def escolher(
    aeronave,
    aerodromos,
    origem,
    destino,
    particulares,
    vento_de=None,
    limite_vento_kt=None,
):
    frase = hipotese_reabastecimento(aeronave)
    lugares = [a for a in aerodromos if getattr(a, "tipo", "aerodromo") == "aerodromo"]
    por_icao = {a.icao: a for a in lugares}
    if origem.icao not in por_icao or destino.icao not in por_icao:
        return {
            "rota_estado": "inaceitavel",
            "motivo": "Não é aeródromo de avião na publicação vigente.",
            "criterio": None,
            "hipotese": frase,
            "trechos": [],
            "tempo_total": None,
            "distancia_total": None,
        }

    alcance = alcance_nm(aeronave)
    caixa = (alcance / 25.0) + 0.01 if alcance > 0 else 0
    celulas = defaultdict(list)
    if caixa:
        for lugar in lugares:
            celula = (floor(lugar.lat / caixa), floor(lugar.lon / caixa))
            celulas[celula].append(lugar)

    def vizinhos(saida):
        if not caixa:
            return []
        x, y = floor(saida.lat / caixa), floor(saida.lon / caixa)
        encontrados = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for chegada in celulas.get((x + dx, y + dy), ()):
                    if chegada.icao == saida.icao:
                        continue
                    if (
                        abs(saida.lat - chegada.lat) > caixa
                        or abs(saida.lon - chegada.lon) > caixa
                    ):
                        continue
                    milhas = distancia_nm(
                        saida.lat, saida.lon, chegada.lat, chegada.lon
                    )
                    if milhas <= alcance:
                        encontrados.append((chegada, milhas))
        return sorted(encontrados, key=lambda item: item[0].icao)

    contas = {}

    def conta_de(saida, chegada):
        chave = (saida.icao, chegada.icao)
        if chave not in contas:
            vento = {"estado": "indisponivel"}
            if vento_de is not None:
                vento = vento_de(saida, chegada) or vento
            contas[chave] = calcular(aeronave, saida, chegada, particulares, vento)
        return contas[chave]

    if limite_vento_kt is None:
        limite_vento_kt = 200.0 if vento_de is not None else 0.0
    velocidade_maxima = float(aeronave.velocidade_valor) + max(
        float(limite_vento_kt), 0.0
    )

    def heuristica(lugar):
        if velocidade_maxima <= 0:
            return 0.0
        return distancia_nm(
            lugar.lat, lugar.lon, destino.lat, destino.lon
        ) / velocidade_maxima

    def estado_melhor(candidato, atual):
        if candidato[0] < atual[0] - 1e-9:
            return True
        if candidato[0] > atual[0] + 1e-9:
            return False
        return candidato[1:] < atual[1:]

    def buscar():
        inicial = (0.0, 0, 0.0, (origem.icao,))
        heap = [(heuristica(origem), *inicial)]
        melhores = {origem.icao: inicial}
        melhor_destino = None
        while heap:
            estimativa, tempo, etapas, dist, caminho = heapq.heappop(heap)
            atual = caminho[-1]
            estado = (tempo, etapas, dist, caminho)
            if (
                melhor_destino is not None
                and estimativa > melhor_destino[0] + 2e-9
            ):
                break
            if estado != melhores.get(atual):
                continue
            if atual == destino.icao:
                if melhor_destino is None or estado_melhor(
                    estado, melhor_destino
                ):
                    melhor_destino = estado
                continue
            aero = por_icao[atual]
            for vizinho, milhas in vizinhos(aero):
                if vizinho.icao in caminho:
                    continue
                conta = conta_de(aero, vizinho)
                if not conta.get("grava") or not conta.get("cabe_reserva"):
                    continue
                chegada_h = tempo + float(conta["tempo_h"])
                novo = caminho + (vizinho.icao,)
                estado_novo = (chegada_h, etapas + 1, dist + milhas, novo)
                anterior = melhores.get(vizinho.icao)
                if anterior is not None and not estado_melhor(
                    estado_novo, anterior
                ):
                    continue
                melhores[vizinho.icao] = estado_novo
                heapq.heappush(
                    heap,
                    (chegada_h + heuristica(vizinho), *estado_novo),
                )
        return melhor_destino

    achado = buscar()
    motivo = MOTIVO_COMBUSTIVEL if achado is None else None
    if achado is None:
        return {
            "rota_estado": "inaceitavel",
            "motivo": motivo,
            "criterio": None,
            "hipotese": frase,
            "trechos": [],
            "tempo_total": None,
            "distancia_total": None,
        }

    tempo_total, _etapas, distancia_total, caminho = achado
    trechos = []
    for ordem, (saida_icao, chegada_icao) in enumerate(zip(caminho, caminho[1:]), start=1):
        saida = por_icao[saida_icao]
        chegada = por_icao[chegada_icao]
        conta = conta_de(saida, chegada)
        trechos.append(_montar_trecho(ordem, saida, chegada, conta))
    return {
        "rota_estado": "aceitavel",
        "motivo": None,
        "criterio": CRITERIO,
        "hipotese": frase,
        "trechos": trechos,
        "tempo_total": tempo_total,
        "distancia_total": distancia_total,
    }
