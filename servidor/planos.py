from datetime import datetime, timezone

from servidor.calculo import avaliar_carga
from servidor.catalogo import PORTE_PEQUENO_KG, emenda_vigente, lugares_da_tela, sol_aerodromo
from servidor.modelos import Aerodromo, Aeronave, ItemChecklist, PlanoDeVoo, Trecho, agora
from servidor.pdf_plano import trecho_limite
from servidor.rota import escolher
from servidor import tempo as tempo_mod

CAMPOS_PARTICULARES = (
    "numero_passageiros",
    "peso_pessoas_kg",
    "peso_bagagem_kg",
)


def hora_ja_passou(valor):
    try:
        return _hora(valor) < agora()
    except (TypeError, ValueError):
        return False


def valores_do_plano(plano):
    dados = {
        "aeronave_id": plano.aeronave_id,
        "origem": plano.origem_icao,
        "destino": plano.destino_icao,
        "hora_partida": plano.hora_partida.strftime("%Y-%m-%dT%H:%M"),
    }
    bruto = dict(plano.dados_particulares or {})
    if "peso_pessoas_kg" not in bruto:
        piloto = bruto.get("peso_piloto_kg")
        passageiro = bruto.get("peso_passageiro_kg")
        if piloto not in (None, "") or passageiro not in (None, ""):
            bruto["peso_pessoas_kg"] = float(piloto or 0) + float(passageiro or 0)
    if "numero_passageiros" not in bruto and bruto.get("ocupantes") not in (None, ""):
        bruto["numero_passageiros"] = bruto["ocupantes"]
    for chave in CAMPOS_PARTICULARES:
        if chave in bruto:
            dados[chave] = bruto[chave]
    return dados


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
        return None, "O número de passageiros inclui o piloto e precisa ser no mínimo 1."
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
        lugar is not None
        and lugar.tipo == "aerodromo"
        and lugar.emenda_id == emenda.id
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


def montar(db, piloto, dados, plano=None):
    origem_icao = (dados.get("origem") or "").strip().upper()
    destino_icao = (dados.get("destino") or "").strip().upper()
    if origem_icao == destino_icao:
        return None, "Origem e destino precisam ser diferentes."
    emenda = emenda_vigente(db)
    origem = db.get(Aerodromo, origem_icao)
    destino = db.get(Aerodromo, destino_icao)
    if emenda is None:
        if origem is None or origem.tipo != "aerodromo" or destino is None or destino.tipo != "aerodromo":
            return None, "Catálogo nacional indisponível."
    elif not _lugar_nacional(emenda, origem) or not _lugar_nacional(emenda, destino):
        return None, "Não é aeródromo de avião na publicação vigente."
    try:
        aeronave = db.get(Aeronave, int(dados.get("aeronave_id") or 0))
    except (TypeError, ValueError):
        aeronave = None
    if aeronave is None:
        return None, "Aeronave sem manual disponível."
    if aeronave.manual_estado == "ausente":
        return None, f"Manual ausente: {aeronave.nome}."
    if aeronave.peso_max_decolagem_kg is None or aeronave.peso_max_decolagem_kg > PORTE_PEQUENO_KG:
        return None, "Avião acima de 5.670 kg, fora do catálogo de avião pequeno."
    try:
        hora = _hora(dados.get("hora_partida"))
    except (TypeError, ValueError):
        return None, "Hora de partida inválida."
    if hora < agora() and not dados.get("confirmar_hora"):
        return None, "Hora de partida no passado. Confirme se ainda quer planejar esse horário."
    particulares, erro = _particulares(dados)
    if erro:
        return None, erro
    fontes = tempo_mod.buscar(origem, destino)
    vento_plano = fontes["vento"]
    cache_sol = {}

    def vento_de(_saida, _chegada):
        if not vento_plano or vento_plano.get("estado") != "disponivel":
            return {"estado": "indisponivel"}
        return vento_plano

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


def do_piloto(db, piloto_id, plano_id):
    return (
        db.query(PlanoDeVoo)
        .filter(PlanoDeVoo.id == plano_id, PlanoDeVoo.piloto_id == piloto_id)
        .one_or_none()
    )


def listar(db, piloto_id):
    return (
        db.query(PlanoDeVoo)
        .filter(PlanoDeVoo.piloto_id == piloto_id)
        .order_by(PlanoDeVoo.atualizado_em.desc())
        .all()
    )


def marcar_item(db, piloto, plano_id, item_id, marcado):
    plano = do_piloto(db, piloto.id, plano_id)
    if plano is None:
        return None
    item = next((i for i in plano.itens if i.id == item_id), None)
    if item is None:
        return None
    item.marcado = bool(marcado)
    db.commit()
    return item


def apagar(db, piloto, plano_id, confirmar):
    plano = do_piloto(db, piloto.id, plano_id)
    if plano is None:
        return False, "ausente"
    if not confirmar:
        return False, "sem_confirmacao"
    db.delete(plano)
    db.commit()
    return True, None


def para_json(plano):
    return {
        "id": plano.id,
        "estado": plano.estado,
        "origem": plano.origem_icao,
        "destino": plano.destino_icao,
        "hora_partida": plano.hora_partida.isoformat(),
        "motivo": plano.motivo,
        "rota": {
            "estado": plano.rota_estado,
            "criterio": "menor tempo de voo" if plano.rota_estado == "aceitavel" else None,
            "hipotese_reabastecimento": plano.hipotese_reabastecimento,
            "trechos": [
                {
                    "ordem": trecho.ordem,
                    "origem": trecho.origem_icao,
                    "destino": trecho.destino_icao,
                    "distancia": {
                        "valor": trecho.distancia_valor,
                        "unidade": trecho.distancia_unidade,
                        "fonte": trecho.distancia_fonte,
                    },
                    "proa": {
                        "valor": trecho.proa_valor,
                        "unidade": trecho.proa_unidade,
                        "fonte": trecho.proa_fonte,
                    },
                    "tempo": {
                        "valor": trecho.tempo_valor,
                        "unidade": trecho.tempo_unidade,
                        "fonte": trecho.tempo_fonte,
                    },
                    "combustivel": {
                        "valor": trecho.combustivel_valor,
                        "unidade": trecho.combustivel_unidade,
                        "fonte": trecho.combustivel_fonte,
                    },
                    "vento_estado": trecho.vento_estado,
                    "por_do_sol_estado": trecho.por_do_sol_estado,
                    "velocidade_solo_kt": trecho.velocidade_solo_kt,
                }
                for trecho in plano.trechos
            ],
        },
        "aeronave_id": plano.aeronave_id,
        "dados_particulares": plano.dados_particulares,
        "resultado": plano.resultado,
        "meteorologia": plano.meteorologia,
        "vento": plano.vento,
        "carta": plano.carta,
        "radar": plano.radar,
        "aviso": plano.aviso,
        "checklist": [
            {
                "id": item.id,
                "ordem": item.ordem,
                "texto": item.texto,
                "fonte": item.fonte,
                "marcado": item.marcado,
            }
            for item in plano.itens
        ],
        "criado_em": plano.criado_em.isoformat(),
        "atualizado_em": plano.atualizado_em.isoformat(),
    }
