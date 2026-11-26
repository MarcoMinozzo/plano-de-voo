from datetime import datetime, timezone

from servidor.calculo import avaliar_carga
from servidor.catalogo import (
    PORTE_PEQUENO_KG,
    emenda_vigente,
    lugares_da_tela,
    modelos_visiveis,
    perfis_sinteticos_visiveis,
    sol_aerodromo,
)
from servidor.modelos import (
    Aerodromo,
    Aeronave,
    ItemChecklist,
    PlanoDeVoo,
    Trecho,
    agora,
)
from servidor.pdf_plano import trecho_limite
from servidor.planos_consulta import (
    CAMPOS_PARTICULARES,
    apagar as apagar,
    do_piloto as do_piloto,
    listar as listar,
    marcar_item as marcar_item,
    para_json as para_json,
    valores_do_plano as valores_do_plano,
)
from servidor.proveniencia import procedencia_aeronave
from servidor.rota import escolher
from servidor import tempo as tempo_mod


def hora_ja_passou(valor):
    try:
        return _hora(valor) < agora()
    except (TypeError, ValueError):
        return False


def _hora(valor):
    if isinstance(valor, datetime):
        hora = valor
    else:
        hora = datetime.fromisoformat(valor)
    if hora.tzinfo is None:
        hora = hora.replace(tzinfo=timezone.utc)
    return hora


def _particulares(dados):
    faltando = [nome for nome in CAMPOS_PARTICULARES if dados.get(nome) in (None, "")]
    if faltando:
        return None, f"Dado particular ausente: {', '.join(faltando)}"
    try:
        quantidade = int(dados["numero_passageiros"])
        pessoas = float(dados["peso_pessoas_kg"])
        bagagem = float(dados["peso_bagagem_kg"])
    except (TypeError, ValueError):
        return None, "Dado particular inválido."
    if quantidade < 1:
        return (
            None,
            "O número de passageiros inclui o piloto e precisa ser no mínimo 1.",
        )
    return {
        "numero_passageiros": quantidade,
        "peso_pessoas_kg": pessoas,
        "peso_bagagem_kg": bagagem,
        "unidades": {
            "peso_pessoas_kg": "kg",
            "peso_bagagem_kg": "kg",
        },
    }, None


def _itens_de(aeronave):
    itens = []
    for ordem, item in enumerate(aeronave.itens_manutencao or [], start=1):
        itens.append(
            {
                "ordem": ordem,
                "texto": item["texto"],
                "fonte": item["fonte"],
                "marcado": False,
            }
        )
    return itens


def _aplicar_itens(plano, aeronave, anteriores=None):
    marcas = {item.texto: item.marcado for item in (anteriores or [])}
    plano.itens.clear()
    for bruto in _itens_de(aeronave):
        plano.itens.append(
            ItemChecklist(
                ordem=bruto["ordem"],
                texto=bruto["texto"],
                fonte=bruto["fonte"],
                marcado=marcas.get(bruto["texto"], False),
            )
        )


def _lugar_nacional(emenda, lugar):
    return (
        lugar is not None and lugar.tipo == "aerodromo" and lugar.emenda_id == emenda.id
    )


def _gravar_trechos(plano, trechos):
    plano.trechos.clear()
    for item in trechos:
        plano.trechos.append(
            Trecho(
                ordem=item["ordem"],
                origem_icao=item["origem"],
                destino_icao=item["destino"],
                distancia_valor=item["distancia_valor"],
                distancia_unidade=item["distancia_unidade"],
                distancia_fonte=item["distancia_fonte"],
                proa_valor=item["proa_valor"],
                proa_unidade=item["proa_unidade"],
                proa_fonte=item["proa_fonte"],
                tempo_valor=item["tempo_valor"],
                tempo_unidade=item["tempo_unidade"],
                tempo_fonte=item["tempo_fonte"],
                combustivel_valor=item["combustivel_valor"],
                combustivel_unidade=item["combustivel_unidade"],
                combustivel_fonte=item["combustivel_fonte"],
                vento_estado=item["vento_estado"],
                por_do_sol_estado=item["por_do_sol_estado"],
                velocidade_solo_kt=item["velocidade_solo_kt"],
            )
        )


def _resultado_de(rota, aeronave, particulares):
    trechos = rota["trechos"]
    if len(trechos) == 1:
        conta = trechos[0]["conta"]
        return {k: v for k, v in conta.items() if k != "grava"}
    alertas, _peso, _combustivel = avaliar_carga(aeronave, particulares)
    return {
        "aceitavel": len(alertas) == 0,
        "alertas": alertas,
        "linhas": [],
        "efeito_vento": "vento não aplicado",
    }


def _aeronave_selecionada(db, dados):
    try:
        aeronave = db.get(Aeronave, int(dados.get("aeronave_id") or 0))
    except (TypeError, ValueError):
        aeronave = None
    if aeronave is None:
        return None, "Aeronave sem manual disponível."
    if aeronave.manual_estado == "proxy_sintetico":
        perfis = perfis_sinteticos_visiveis(db)
        if not any(perfil.id == aeronave.id for perfil in perfis):
            return (
                None,
                f"Perfil sintético didático fora da lista permitida: {aeronave.nome}.",
            )
        procedencia = procedencia_aeronave(db, aeronave)
        if any(fonte is None for fonte in procedencia.values()):
            return None, f"Perfil sintético didático incompleto: {aeronave.nome}."
        return aeronave, None

    estado_modelos, modelos = modelos_visiveis(db)
    if estado_modelos != "disponivel":
        return None, "Catálogo nacional de aeronaves indisponível."
    if not any(modelo.id == aeronave.id for modelo in modelos):
        return None, f"Aeronave fora da seleção elegível do MVP: {aeronave.nome}."
    if aeronave.manual_estado == "ausente":
        return None, f"Manual ausente: {aeronave.nome}."
    if (
        aeronave.peso_max_decolagem_kg is None
        or aeronave.peso_max_decolagem_kg > PORTE_PEQUENO_KG
    ):
        return None, "Avião acima de 5.670 kg, fora do catálogo de avião pequeno."
    return aeronave, None


def _aerodromos_selecionados(db, origem_icao, destino_icao):
    emenda = emenda_vigente(db)
    origem = db.get(Aerodromo, origem_icao)
    destino = db.get(Aerodromo, destino_icao)
    if emenda is None:
        return None, None, "Catálogo nacional indisponível."
    if not _lugar_nacional(emenda, origem) or not _lugar_nacional(emenda, destino):
        return None, None, "Não é aeródromo de avião na publicação vigente."
    return origem, destino, None


def _vento_para_rota(vento_plano):
    if not vento_plano or vento_plano.get("estado") != "disponivel":
        return None, 0.0

    def vento_de(_saida, _chegada):
        return vento_plano

    return vento_de, float(vento_plano["velocidade_kt"])


def _preparar_entrada(db, dados):
    origem_icao = (dados.get("origem") or "").strip().upper()
    destino_icao = (dados.get("destino") or "").strip().upper()
    if origem_icao == destino_icao:
        return None, "Origem e destino precisam ser diferentes."
    aeronave, erro = _aeronave_selecionada(db, dados)
    if erro is not None:
        return None, erro
    origem, destino, erro = _aerodromos_selecionados(db, origem_icao, destino_icao)
    if erro is not None:
        if aeronave.manual_estado == "proxy_sintetico":
            erro = "Catálogo ROTAER oficial vigente indisponível."
        return None, erro
    try:
        hora = _hora(dados.get("hora_partida"))
    except (TypeError, ValueError):
        return None, "Hora de partida inválida."
    if hora < agora() and not dados.get("confirmar_hora"):
        return (
            None,
            "Hora de partida no passado. Confirme se ainda quer planejar esse horário.",
        )
    particulares, erro = _particulares(dados)
    if erro:
        return None, erro
    return (
        origem_icao,
        destino_icao,
        aeronave,
        origem,
        destino,
        hora,
        particulares,
    ), None


def montar(db, piloto, dados, plano=None):
    entrada, erro = _preparar_entrada(db, dados)
    if erro is not None:
        return None, erro
    (
        origem_icao,
        destino_icao,
        aeronave,
        origem,
        destino,
        hora,
        particulares,
    ) = entrada
    vento_plano = tempo_mod.vento_area(origem, destino)
    vento_de, limite_vento_kt = _vento_para_rota(vento_plano)
    cache_sol = {}

    def sol_de(chegada, instante):
        chave = (chegada.icao, instante.date().isoformat())
        if chave not in cache_sol:
            cache_sol[chave] = sol_aerodromo(chegada.icao, instante)
        return cache_sol[chave]

    _estado, lugares = lugares_da_tela(db)
    rota = escolher(
        aeronave,
        lugares,
        origem,
        destino,
        particulares,
        vento_de=vento_de,
        sol_de=sol_de,
        hora_partida=hora,
        limite_vento_kt=limite_vento_kt,
    )
    aerodromos_rota = []
    vistos = set()
    for trecho in rota["trechos"]:
        for icao in (trecho["origem"], trecho["destino"]):
            if icao in vistos:
                continue
            vistos.add(icao)
            aerodromo = db.get(Aerodromo, icao)
            if aerodromo is not None:
                aerodromos_rota.append(aerodromo)
    fontes = tempo_mod.buscar(
        origem,
        destino,
        aerodromos=aerodromos_rota,
        vento=vento_plano,
    )
    if rota["rota_estado"] != "aceitavel":
        resultado = {
            "aceitavel": False,
            "alertas": [],
            "linhas": [],
            "efeito_vento": "vento não aplicado",
        }
        estado = "inaceitavel"
        motivo = rota["motivo"]
    else:
        resultado = _resultado_de(rota, aeronave, particulares)
        if resultado["alertas"]:
            estado = "inaceitavel"
            motivo = None
        else:
            estado = "calculado"
            motivo = None
        if len(rota["trechos"]) == 1 and vento_plano.get("estado") == "disponivel":
            conta = rota["trechos"][0]["conta"]
            vento_plano["efeito"] = conta["efeito_vento"]
            vento_plano["proa_graus"] = conta["proa_graus"]
            vento_plano["velocidade_solo_kt"] = conta["velocidade_solo_kt"]
    procedencia = procedencia_aeronave(db, aeronave)
    resultado["procedencia"] = procedencia
    resultado["estimativa_didatica"] = any(
        fonte and fonte["estimativa_didatica"] for fonte in procedencia.values()
    )
    resultado["dados_sinteticos"] = any(
        fonte and fonte["dados_sinteticos"] for fonte in procedencia.values()
    )
    resultado["proxy_sintetico"] = aeronave.manual_estado == "proxy_sintetico"
    resultado["modelo_alvo"] = aeronave.nome if resultado["proxy_sintetico"] else None
    momento = agora()
    if plano is None:
        plano = PlanoDeVoo(piloto_id=piloto.id, criado_em=momento)
        db.add(plano)
    anteriores = list(plano.itens)
    plano.aeronave_id = aeronave.id
    plano.origem_icao = origem.icao
    plano.destino_icao = destino.icao
    plano.hora_partida = hora
    plano.dados_particulares = particulares
    plano.resultado = resultado
    plano.meteorologia = fontes["meteorologia"]
    plano.vento = vento_plano
    plano.carta = fontes["carta"]
    plano.radar = fontes["radar"]
    plano.aviso = trecho_limite()
    plano.estado = estado
    plano.rota_estado = rota["rota_estado"]
    plano.motivo = motivo
    plano.hipotese_reabastecimento = rota["hipotese"]
    plano.atualizado_em = momento
    _aplicar_itens(plano, aeronave, anteriores)
    _gravar_trechos(plano, rota["trechos"])
    db.commit()
    db.refresh(plano)
    return plano, None
