from servidor.modelos import PlanoDeVoo


CAMPOS_PARTICULARES = (
    "numero_passageiros",
    "peso_pessoas_kg",
    "peso_bagagem_kg",
)


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
            "criterio": "menor tempo de voo"
            if plano.rota_estado == "aceitavel"
            else None,
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
