import math

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


def _texto_fonte(valor):
    if valor is None:
        return ""
    if hasattr(valor, "isoformat"):
        return valor.isoformat()
    return str(valor)


def _horario_taf_utc(valor):
    texto = _texto_fonte(valor).strip()
    if texto and not texto.endswith(("Z", "+00:00")):
        return f"{texto} UTC"
    return texto


def linha_fonte_relatorio(
    campo,
    valor,
    fonte,
    *,
    publicador=None,
    referencia=None,
    data=None,
    unidade=None,
    aplicabilidade=None,
    estado=None,
):
    valor_texto = _texto_fonte(valor)
    fonte_texto = _texto_fonte(fonte)
    return {
        "campo": campo,
        "valor": valor_texto or "Indisponível",
        "fonte": fonte_texto or "Fonte não informada",
        "publicador": _texto_fonte(publicador),
        "referencia": _texto_fonte(referencia),
        "data": _texto_fonte(data),
        "unidade": _texto_fonte(unidade),
        "aplicabilidade": _texto_fonte(aplicabilidade),
        "estado": estado or ("disponivel" if valor_texto else "indisponivel"),
    }


def construir_fontes_relatorio(plano, aerodromos=None, meteorologia=None):
    aerodromos = aerodromos or {}
    meteorologia = meteorologia if isinstance(meteorologia, dict) else {}
    linhas = []

    for campo, fonte in (plano.resultado.get("procedencia") or {}).items():
        if not isinstance(fonte, dict):
            linhas.append(
                linha_fonte_relatorio(
                    campo, None, "Fonte técnica da aeronave", estado="indisponivel"
                )
            )
            continue
        rotulo_campo = (
            f"Dados sintéticos didáticos — {campo}"
            if fonte.get("dados_sinteticos")
            else campo
        )
        linhas.append(
            linha_fonte_relatorio(
                rotulo_campo,
                f"{fonte.get('valor', '')} {fonte.get('unidade', '')}".strip(),
                fonte.get("publicador"),
                publicador=fonte.get("publicador"),
                referencia=fonte.get("referencia"),
                data=fonte.get("data_publicacao") or fonte.get("data_consulta"),
                unidade=fonte.get("unidade"),
                aplicabilidade=fonte.get("modelo_variante"),
                estado=(
                    "nao_fornecido_pela_fonte"
                    if fonte.get("dados_sinteticos")
                    else "disponivel"
                ),
            )
        )

    for trecho in plano.trechos:
        for campo, valor, unidade, fonte in (
            ("distância", trecho.distancia_valor, trecho.distancia_unidade, trecho.distancia_fonte),
            ("proa", trecho.proa_valor, trecho.proa_unidade, trecho.proa_fonte),
            ("tempo estimado", trecho.tempo_valor, trecho.tempo_unidade, trecho.tempo_fonte),
            ("combustível estimado", trecho.combustivel_valor, trecho.combustivel_unidade, trecho.combustivel_fonte),
        ):
            linhas.append(
                linha_fonte_relatorio(
                    f"Trecho {trecho.ordem} — {campo}",
                    valor,
                    fonte,
                    unidade=unidade,
                    aplicabilidade=f"{trecho.origem_icao} → {trecho.destino_icao}",
                )
            )

    boletins = meteorologia.get("aerodromos")
    if not isinstance(boletins, dict):
        boletins = {
            icao: meteorologia.get(chave)
            for icao, chave in (
                (plano.origem_icao, "origem"),
                (plano.destino_icao, "destino"),
            )
            if isinstance(meteorologia.get(chave), dict)
        }
    codigos_rota = dict.fromkeys(
        icao
        for trecho in plano.trechos
        for icao in (trecho.origem_icao, trecho.destino_icao)
    )
    for icao in codigos_rota:
        aerodromo = aerodromos.get(icao)
        fonte_aerodromo = getattr(aerodromo, "fonte", None)
        data_rotaer = getattr(aerodromo, "rotaer_atualizado_em", None)
        dados_aero = (
            ("nome", getattr(aerodromo, "nome", None), None),
            ("tipo", getattr(aerodromo, "tipo", None), None),
            (
                "coordenadas",
                (
                    f"{aerodromo.lat}, {aerodromo.lon}"
                    if aerodromo is not None
                    else None
                ),
                "graus",
            ),
            ("elevação", getattr(aerodromo, "elev_m", None), "m"),
            (
                "emenda ROTAER",
                getattr(aerodromo, "rotaer_versao_id", None),
                None,
            ),
        )
        for campo, valor, unidade in dados_aero:
            linhas.append(
                linha_fonte_relatorio(
                    f"{icao} — {campo}",
                    valor,
                    fonte_aerodromo,
                    data=data_rotaer,
                    unidade=unidade,
                    aplicabilidade=icao,
                )
            )
        contatos_verificados = bool(
            getattr(aerodromo, "contatos_rotaer_verificados", False)
        )
        for campo, atributo in (("telefone publicado", "telefone"), ("e-mail publicado", "email")):
            valor = getattr(aerodromo, atributo, None) if contatos_verificados else None
            linhas.append(
                linha_fonte_relatorio(
                    f"{icao} — {campo}",
                    valor,
                    fonte_aerodromo,
                    data=data_rotaer,
                    aplicabilidade=icao,
                    estado=(
                        "disponivel"
                        if valor
                        else "indisponivel"
                    ),
                )
            )

        boletim = boletins.get(icao) if isinstance(boletins.get(icao), dict) else {}
        fonte_tempo = boletim.get("fonte", "Aviation Weather Center")
        for tipo in ("metar", "taf"):
            observacao = boletim.get(tipo)
            observacao = observacao if isinstance(observacao, dict) else {}
            bruto = observacao.get("raw")
            aplicabilidade = icao
            campo = f"{icao} — {tipo.upper()}"
            data = observacao.get("hora")
            if tipo == "taf":
                horarios = []
                if data:
                    horarios.append(f"Emissão: {_horario_taf_utc(data)}")
                inicio = _horario_taf_utc(observacao.get("validade_inicial"))
                fim = _horario_taf_utc(observacao.get("validade_final"))
                if inicio and fim:
                    horarios.append(f"Validade: {inicio} a {fim}")
                elif inicio or fim:
                    horarios.append(f"Validade: {inicio or fim}")
                data = "; ".join(horarios)
            if tipo == "metar" and observacao.get("regional"):
                estacao_icao = observacao.get("icao") or "indicativo indisponível"
                nome_estacao = observacao.get("nome_estacao") or estacao_icao
                campo = f"{icao} — METAR regional — {nome_estacao} ({estacao_icao})"
                distancia = observacao.get("distancia_nm")
                if (
                    isinstance(distancia, (int, float))
                    and not isinstance(distancia, bool)
                    and math.isfinite(distancia)
                ):
                    aplicabilidade = (
                        f"aeródromo {icao}; estação {estacao_icao}; "
                        f"{distancia:.1f} NM"
                    )
                else:
                    aplicabilidade = f"aeródromo {icao}; estação {estacao_icao}"
            linhas.append(
                linha_fonte_relatorio(
                    campo,
                    bruto,
                    observacao.get("fonte") or fonte_tempo,
                    referencia=bruto,
                    data=data,
                    aplicabilidade=aplicabilidade,
                )
            )

    vento = plano.vento or {}
    linhas.append(
        linha_fonte_relatorio(
            "Vento da rota",
            (
                f"{vento.get('direcao_de_graus')}° / "
                f"{vento.get('velocidade_kt')} {vento.get('unidade', 'kt')}"
                if vento.get("estado") == "disponivel"
                else None
            ),
            vento.get("fonte"),
            referencia=vento.get("referencia"),
            data=vento.get("hora"),
            unidade=vento.get("unidade", "kt"),
            aplicabilidade="rota completa",
            estado=vento.get("estado", "indisponivel"),
        )
    )

    carta = plano.carta or {}
    documentos = carta.get("documentos")
    if carta.get("estado") == "disponivel" and isinstance(documentos, list) and documentos:
        for documento in documentos:
            if not isinstance(documento, dict):
                continue
            linhas.append(
                linha_fonte_relatorio(
                    f"Carta WAC {documento.get('indice', '')}".strip(),
                    documento.get("nome"),
                    carta.get("fonte", "AISWEB WAC"),
                    publicador=carta.get("fonte", "AISWEB"),
                    referencia=documento.get("url"),
                    aplicabilidade=documento.get("icao"),
                )
            )
    else:
        linhas.append(
            linha_fonte_relatorio(
                "Carta WAC",
                None,
                carta.get("fonte", "AISWEB"),
                estado="indisponivel",
            )
        )

    radar = plano.radar or {}
    linhas.append(
        linha_fonte_relatorio(
            "Radar de chuva",
            radar.get("fonte") or radar.get("provedor"),
            radar.get("fonte") or radar.get("provedor"),
            referencia=radar.get("referencia"),
            data=radar.get("hora_frame"),
            aplicabilidade="mapa do plano",
            estado=(
                "disponivel"
                if radar.get("estado") == "disponivel"
                else "indisponivel"
            ),
        )
    )

    for item in plano.itens:
        linhas.append(
            linha_fonte_relatorio(
                f"Checklist — {item.texto}",
                item.texto,
                item.fonte,
                referencia=item.fonte,
                estado="disponivel" if item.fonte else "indisponivel",
            )
        )
    return linhas


def programacao_do_plano(plano):
    programacao = (plano.resultado or {}).get("programacao")
    if not isinstance(programacao, dict):
        return {"estado": "nao_calculada", "fuso": "UTC", "trechos": []}
    return programacao


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
                    "vento_sentido": trecho.vento_sentido,
                    "vento_componente_kt": trecho.vento_componente_kt,
                    "vento_fonte": trecho.vento_fonte,
                    "por_do_sol_estado": trecho.por_do_sol_estado,
                    "velocidade_solo_kt": trecho.velocidade_solo_kt,
                }
                for trecho in plano.trechos
            ],
        },
        "aeronave_id": plano.aeronave_id,
        "dados_particulares": plano.dados_particulares,
        "resultado": plano.resultado,
        "programacao": programacao_do_plano(plano),
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
