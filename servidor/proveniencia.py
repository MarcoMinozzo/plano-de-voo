from math import isfinite

PORTE_PEQUENO_KG = 5670

CAMPOS_TECNICOS_OBRIGATORIOS = (
    "peso_vazio",
    "peso_maximo_decolagem",
    "bagagem_maxima",
    "combustivel_utilizavel",
    "velocidade_cruzeiro",
    "consumo_cruzeiro",
)

ATRIBUTOS_AERONAVE = {
    "peso_vazio": ("peso_vazio_kg", "kg"),
    "peso_maximo_decolagem": ("peso_max_decolagem_kg", "kg"),
    "bagagem_maxima": ("bagagem_max_kg", "kg"),
    "combustivel_utilizavel": ("combustivel_valor", "gal"),
    "velocidade_cruzeiro": ("velocidade_valor", "kt"),
    "consumo_cruzeiro": ("consumo_valor", "gal/h"),
}


def _campos_base_validos(fonte, campo, tipo):
    return (
        bool((fonte.publicador or "").strip())
        and bool((fonte.referencia or "").strip())
        and bool((fonte.modelo_variante or "").strip())
        and fonte.data_consulta is not None
        and (tipo == "sintetica" or fonte.data_publicacao is not None)
        and fonte.unidade == ATRIBUTOS_AERONAVE.get(campo, (None, None))[1]
        and isfinite(fonte.valor)
        and fonte.valor > 0
        and (
            campo not in {"velocidade_cruzeiro", "consumo_cruzeiro"}
            or bool((fonte.perfil or "").strip())
        )
    )


def _fonte_valida(fonte, campo, tipo):
    return fonte.tipo_fonte == tipo and _campos_base_validos(fonte, campo, tipo)


def _marcar_selecionada(db, fontes, vencedora):
    for fonte in fontes:
        fonte.selecionada = fonte.id == vencedora.id
        fonte.divergencia = None
    db.flush()
    return vencedora


def _selecionar_rastreavel(db, fontes, candidatas):
    mais_recente = max(fonte.data_publicacao for fonte in candidatas)
    mais_recentes = [
        fonte for fonte in candidatas
        if fonte.data_publicacao == mais_recente
    ]
    if len(mais_recentes) != 1:
        for fonte in fontes:
            fonte.selecionada = False
            fonte.divergencia = "Empate temporal; nenhuma fonte foi selecionada."
        db.flush()
        return None
    vencedora = _marcar_selecionada(db, fontes, mais_recentes[0])
    divergentes = [
        fonte for fonte in candidatas
        if fonte.id != vencedora.id
        and (fonte.valor != vencedora.valor or fonte.unidade != vencedora.unidade)
    ]
    if divergentes:
        alternativas = "; ".join(
            f"{fonte.publicador} ({fonte.data_publicacao.isoformat()}): "
            f"{fonte.valor} {fonte.unidade}, {fonte.referencia}"
            for fonte in divergentes
        )
        vencedora.divergencia = (
            f"Selecionada a fonte de {vencedora.data_publicacao.isoformat()}; "
            f"valores alternativos: {alternativas}. Nenhuma média foi usada."
        )
    return vencedora


def selecionar_fonte_aplicavel(db, aeronave, campo):
    from servidor.modelos import FonteTecnicaAeronave

    fontes = db.query(FonteTecnicaAeronave).filter_by(
        aeronave_id=aeronave.id, campo=campo
    ).all()
    if aeronave.manual_estado == "proxy_sintetico":
        sinteticas = [
            fonte
            for fonte in fontes
            if fonte.tipo_fonte == "sintetica" and fonte.selecionada
        ]
        if len(sinteticas) > 1:
            raise RuntimeError(
                f"Mais de uma fonte sintética selecionada para {aeronave.nome}: {campo}."
            )
        return sinteticas[0] if sinteticas else None

    rastreaveis = [
        fonte
        for fonte in fontes
        if fonte.tipo_fonte in {"oficial", "secundaria"}
        and _fonte_valida(fonte, campo, fonte.tipo_fonte)
    ]
    if rastreaveis:
        return _selecionar_rastreavel(db, fontes, rastreaveis)
    return None


def _registro_procedencia(fonte, campo):
    sintetica = fonte.tipo_fonte == "sintetica"
    return {
        "campo": campo,
        "valor": fonte.valor,
        "unidade": fonte.unidade,
        "tipo_fonte": fonte.tipo_fonte,
        "publicador": None if sintetica else fonte.publicador,
        "referencia": (
            "Valor sintético didático; não representa dados do modelo associado."
            if sintetica
            else fonte.referencia
        ),
        "data_publicacao": (
            fonte.data_publicacao.isoformat()
            if fonte.data_publicacao and not sintetica
            else None
        ),
        "data_consulta": (
            fonte.data_consulta.isoformat()
            if fonte.data_consulta and not sintetica
            else None
        ),
        "modelo_variante": None if sintetica else fonte.modelo_variante,
        "perfil": None if sintetica else fonte.perfil,
        "revisao_edicao": None if sintetica else fonte.revisao_edicao,
        "pagina_tabela": None if sintetica else fonte.pagina_tabela,
        "limite_inferior": None if sintetica else fonte.limite_inferior,
        "limite_superior": None if sintetica else fonte.limite_superior,
        "metodo_geracao": None if sintetica else fonte.metodo_geracao,
        "versao_semente": None if sintetica else fonte.versao_semente,
        "incerteza": None if sintetica else fonte.incerteza,
        "justificativa_comparabilidade": (
            None if sintetica else fonte.justificativa_comparabilidade
        ),
        "estimativa_didatica": fonte.tipo_fonte == "secundaria" and not sintetica,
        "dados_sinteticos": sintetica,
        "divergencia": None if sintetica else fonte.divergencia,
    }


def _aplicar_valor_fonte(aeronave, campo, fonte):
    atributo, unidade = ATRIBUTOS_AERONAVE[campo]
    setattr(aeronave, atributo, fonte.valor)
    if campo == "combustivel_utilizavel":
        aeronave.combustivel_unidade = unidade
    elif campo == "velocidade_cruzeiro":
        aeronave.velocidade_unidade = unidade
    elif campo == "consumo_cruzeiro":
        aeronave.consumo_unidade = unidade


def procedencia_aeronave(db, aeronave):
    fontes = {}
    for campo in CAMPOS_TECNICOS_OBRIGATORIOS:
        fonte = selecionar_fonte_aplicavel(db, aeronave, campo)
        if fonte is None:
            fontes[campo] = None
            continue
        fontes[campo] = _registro_procedencia(fonte, campo)
        _aplicar_valor_fonte(aeronave, campo, fonte)

    aeronave.procedencia_tecnica = fontes
    return fontes


def formatar_fonte(fonte):
    if not fonte:
        return "fonte indisponível"
    if fonte.get("dados_sinteticos", False):
        return (
            "Perfil sintético didático — valores não validados; "
            "não representam dados do modelo associado."
        )
    rotulo = "Estimativa didática — " if fonte["estimativa_didatica"] else ""
    perfil = f"; perfil: {fonte['perfil']}" if fonte["perfil"] else ""
    return (
        f"{rotulo}{fonte['publicador']}; {fonte['referencia']}; "
        f"data: {fonte['data_publicacao']}; "
        f"aplicabilidade: {fonte['modelo_variante']}{perfil}"
    )


def modelo_tecnicamente_completo(db, aeronave):
    if aeronave.manual_estado != "gravado":
        return False
    campos = procedencia_aeronave(db, aeronave)
    if any(campos[campo] is None for campo in CAMPOS_TECNICOS_OBRIGATORIOS):
        return False
    peso_vazio = campos["peso_vazio"]["valor"]
    peso_maximo = campos["peso_maximo_decolagem"]["valor"]
    if peso_maximo > PORTE_PEQUENO_KG or peso_maximo <= peso_vazio:
        return False
    if campos["bagagem_maxima"]["valor"] > peso_maximo - peso_vazio:
        return False
    perfil_velocidade = campos["velocidade_cruzeiro"]["perfil"]
    perfil_consumo = campos["consumo_cruzeiro"]["perfil"]
    return bool(perfil_velocidade and perfil_velocidade == perfil_consumo)
