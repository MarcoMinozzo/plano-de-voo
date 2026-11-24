import heapq
from datetime import timedelta

from servidor.calculo import RESERVA_HORAS, calcular, distancia_nm

CRITERIO = "menor tempo de voo"
MOTIVO_COMBUSTIVEL = (
    "Nenhuma sequência de aeródromos publicados deixa todos os trechos dentro "
    "do combustível de planejamento e da reserva de 30 minutos."
)
MOTIVO_SOL = "Um trecho chegaria depois do pôr do sol no aeródromo de chegada."


def hipotese_reabastecimento(aeronave):
    return (
        "Em cada escala, a hipótese é reabastecer até o combustível de planejamento do manual. "
        f"Fonte: {aeronave.fonte_manual}."
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


def _montar_trecho(ordem, origem, destino, conta, sol_estado):
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
        "por_do_sol_estado": sol_estado,
        "velocidade_solo_kt": conta["velocidade_solo_kt"],
        "conta": conta,
    }


def _sol_bloqueia(sol_de, destino, chegada):
    if sol_de is None or chegada is None:
        return False, "indisponivel"
    info = sol_de(destino, chegada) or {"estado": "indisponivel"}
    if info.get("estado") != "disponivel":
        return False, "indisponivel"
    limite = info.get("por_do_sol")
    if getattr(limite, "tzinfo", None) is None:
        return False, "indisponivel"
    if chegada > limite:
        return True, "disponivel"
    return False, "disponivel"


def escolher(aeronave, aerodromos, origem, destino, particulares, vento_de=None, sol_de=None, hora_partida=None):
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
    arestas = {icao: [] for icao in por_icao}
    for saida in lugares:
        for chegada in lugares:
            if saida.icao == chegada.icao:
                continue
            if caixa and (
                abs(saida.lat - chegada.lat) > caixa or abs(saida.lon - chegada.lon) > caixa
            ):
                continue
            milhas = distancia_nm(saida.lat, saida.lon, chegada.lat, chegada.lon)
            if milhas <= alcance:
                arestas[saida.icao].append(chegada)

    contas = {}

    def conta_de(saida, chegada):
        chave = (saida.icao, chegada.icao)
        if chave not in contas:
            vento = {"estado": "indisponivel"}
            if vento_de is not None:
                vento = vento_de(saida, chegada) or vento
            contas[chave] = calcular(aeronave, saida, chegada, particulares, vento)
        return contas[chave]

    def buscar(usar_sol):
        heap = [(0.0, 0, 0.0, (origem.icao,))]
        visitados = set()
        while heap:
            tempo, etapas, dist, caminho = heapq.heappop(heap)
            atual = caminho[-1]
            if atual in visitados:
                continue
            visitados.add(atual)
            if atual == destino.icao:
                return tempo, dist, caminho
            aero = por_icao[atual]
            for vizinho in arestas[atual]:
                if vizinho.icao in caminho:
                    continue
                conta = conta_de(aero, vizinho)
                if not conta.get("grava") or not conta.get("cabe_reserva"):
                    continue
                leg_h = round(float(conta["tempo_h"]), 2)
                chegada_h = round(tempo + leg_h, 2)
                if usar_sol and hora_partida is not None:
                    chegada = hora_partida + timedelta(hours=chegada_h)
                    bloqueia, _estado = _sol_bloqueia(sol_de, vizinho, chegada)
                    if bloqueia:
                        continue
                novo = caminho + (vizinho.icao,)
                milhas = distancia_nm(aero.lat, aero.lon, vizinho.lat, vizinho.lon)
                heapq.heappush(heap, (chegada_h, etapas + 1, dist + milhas, novo))
        return None

    usar_sol = sol_de is not None and hora_partida is not None
    achado = buscar(usar_sol)
    motivo = None
    if achado is None and usar_sol and buscar(False) is not None:
        motivo = MOTIVO_SOL
    elif achado is None:
        motivo = MOTIVO_COMBUSTIVEL
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

    tempo_total, distancia_total, caminho = achado
    trechos = []
    acumulado = 0.0
    for ordem, (saida_icao, chegada_icao) in enumerate(zip(caminho, caminho[1:]), start=1):
        saida = por_icao[saida_icao]
        chegada = por_icao[chegada_icao]
        conta = conta_de(saida, chegada)
        leg_h = round(float(conta["tempo_h"]), 2)
        acumulado = round(acumulado + leg_h, 2)
        sol_estado = "indisponivel"
        if hora_partida is not None:
            instante = hora_partida + timedelta(hours=acumulado)
            _bloqueia, sol_estado = _sol_bloqueia(sol_de, chegada, instante)
        trechos.append(_montar_trecho(ordem, saida, chegada, conta, sol_estado))
    return {
        "rota_estado": "aceitavel",
        "motivo": None,
        "criterio": CRITERIO,
        "hipotese": frase,
        "trechos": trechos,
        "tempo_total": tempo_total,
        "distancia_total": distancia_total,
    }
