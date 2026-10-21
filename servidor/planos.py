from datetime import datetime, timezone

from servidor.calculo import calcular
from servidor.modelos import Aerodromo, Aeronave, ItemChecklist, PlanoDeVoo, agora
from servidor.pdf_plano import trecho_limite
from servidor import tempo as tempo_mod

CAMPOS_PARTICULARES = (
    "ocupantes",
    "peso_piloto_kg",
    "peso_passageiro_kg",
    "peso_bagagem_kg",
    "combustivel_a_bordo_gal",
)


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
    return {
        "ocupantes": int(dados["ocupantes"]),
        "peso_piloto_kg": float(dados["peso_piloto_kg"]),
        "peso_passageiro_kg": float(dados["peso_passageiro_kg"]),
        "peso_bagagem_kg": float(dados["peso_bagagem_kg"]),
        "combustivel_a_bordo_gal": float(dados["combustivel_a_bordo_gal"]),
        "unidades": {
            "peso_piloto_kg": "kg",
            "peso_passageiro_kg": "kg",
            "peso_bagagem_kg": "kg",
            "combustivel_a_bordo_gal": "gal",
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


def montar(db, piloto, dados, plano=None):
    origem_icao = (dados.get("origem") or "").strip().upper()
    destino_icao = (dados.get("destino") or "").strip().upper()
    if origem_icao == destino_icao:
        return None, "Origem e destino precisam ser diferentes."
    origem = db.get(Aerodromo, origem_icao)
    destino = db.get(Aerodromo, destino_icao)
    if origem is None or destino is None:
        qual = origem_icao if origem is None else destino_icao
        return None, f"Aeródromo desconhecido: {qual}"
    aeronave = db.get(Aeronave, int(dados.get("aeronave_id") or 0))
    if aeronave is None:
        return None, "Aeronave sem manual disponível."
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
    conta = calcular(aeronave, origem, destino, particulares, fontes["vento"])
    if not conta.get("grava"):
        return None, f"Dado do manual ausente: {conta.get('erro')}"
    if fontes["vento"].get("estado") == "disponivel":
        fontes["vento"]["efeito"] = conta["efeito_vento"]
        fontes["vento"]["proa_graus"] = conta["proa_graus"]
        fontes["vento"]["velocidade_solo_kt"] = conta["velocidade_solo_kt"]
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
    plano.resultado = {k: v for k, v in conta.items() if k != "grava"}
    plano.meteorologia = fontes["meteorologia"]
    plano.vento = fontes["vento"]
    plano.carta = fontes["carta"]
    plano.radar = fontes["radar"]
    plano.aviso = trecho_limite()
    plano.estado = "calculado" if conta["aceitavel"] else "inaceitavel"
    plano.atualizado_em = momento
    _aplicar_itens(plano, aeronave, anteriores)
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
