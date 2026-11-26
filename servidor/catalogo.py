import logging
import sys
from xml.etree import ElementTree

import requests

from sqlalchemy import or_

from servidor.modelos import (
    Aerodromo,
    Aeronave,
    EmendaRotaer,
    ExtratoRab,
    agora,
)
from servidor.proveniencia import (
    PORTE_PEQUENO_KG as PORTE_PEQUENO_KG,
    modelo_tecnicamente_completo,
    procedencia_aeronave as procedencia_aeronave,
    selecionar_fonte_aplicavel as selecionar_fonte_aplicavel,
)
from servidor.catalogo_rab import carregar_rab
from servidor.perfis_sinteticos import PERFIS_SINTETICOS
from servidor.rotaer_aisweb import (
    TAMANHO_PAGINA_ROTAER,
    _baixar_rotaer,
    _cache_rotaer,
    _chaves_aisweb,
    sol_aerodromo as sol_aerodromo,
)
from servidor.rotaer_parse import interpretar_rotaer

logger = logging.getLogger(__name__)


def emenda_vigente(db):
    return (
        db.query(EmendaRotaer)
        .filter_by(vigente=True, estado="disponivel")
        .one_or_none()
    )


def extrato_vigente(db):
    return (
        db.query(ExtratoRab)
        .filter_by(estado="disponivel")
        .order_by(ExtratoRab.carregado_em.desc())
        .first()
    )


def aerodromos_oferecidos(db):
    emenda = emenda_vigente(db)
    if emenda is None:
        return "indisponivel", []
    lista = (
        db.query(Aerodromo)
        .filter_by(emenda_id=emenda.id, tipo="aerodromo")
        .order_by(Aerodromo.icao)
        .all()
    )
    return "disponivel", lista


def lugares_da_tela(db):
    emenda = emenda_vigente(db)
    if emenda is not None:
        return aerodromos_oferecidos(db)
    locais = (
        db.query(Aerodromo).filter_by(tipo="aerodromo").order_by(Aerodromo.icao).all()
    )
    return "local", locais


def correspondencias(db, texto):
    emenda = emenda_vigente(db)
    if emenda is None:
        return "indisponivel", []
    bruto = " ".join((texto or "").split())
    if len(bruto) < 2:
        return "curto", []
    like = f"%{bruto}%"
    lista = (
        db.query(Aerodromo)
        .filter(
            Aerodromo.emenda_id == emenda.id,
            Aerodromo.tipo == "aerodromo",
            or_(Aerodromo.icao.ilike(like), Aerodromo.nome.ilike(like)),
        )
        .order_by(Aerodromo.icao)
        .all()
    )
    return "disponivel", lista


def modelos_visiveis(db):
    extrato = extrato_vigente(db)
    if extrato is None:
        return "indisponivel", []
    lista = (
        db.query(Aeronave)
        .filter(
            Aeronave.extrato_id == extrato.id,
            Aeronave.manual_estado == "gravado",
        )
        .order_by(Aeronave.frota.desc(), Aeronave.nome.asc())
        .all()
    )
    completa = [
        aeronave for aeronave in lista if modelo_tecnicamente_completo(db, aeronave)
    ]
    return "disponivel", completa[:30]


def perfis_sinteticos_visiveis(db):
    nomes = {perfil.nome_exibicao for perfil in PERFIS_SINTETICOS}
    encontrados = (
        db.query(Aeronave)
        .filter(
            Aeronave.manual_estado == "proxy_sintetico",
            Aeronave.nome.in_(nomes),
        )
        .order_by(Aeronave.nome)
        .all()
    )
    por_nome = {}
    for aeronave in encontrados:
        if aeronave.nome in por_nome:
            raise RuntimeError(
                f"Mais de um perfil sintético didático para {aeronave.nome}."
            )
        por_nome[aeronave.nome] = aeronave
    return [
        por_nome[perfil.nome_exibicao]
        for perfil in PERFIS_SINTETICOS
        if perfil.nome_exibicao in por_nome
    ]


def _marcar_rotaer_indisponivel(db):
    for emenda in db.query(EmendaRotaer).filter_by(vigente=True):
        emenda.vigente = False
    db.flush()
    db.add(
        EmendaRotaer(
            codigo_emenda="indisponivel",
            vigente=False,
            carregada_em=agora(),
            estado="indisponivel",
        )
    )
    db.commit()
    return "indisponivel"


def _gravar_emenda(db, codigo, registros):
    for emenda in db.query(EmendaRotaer).filter_by(vigente=True):
        emenda.vigente = False
    db.flush()
    emenda = EmendaRotaer(
        codigo_emenda=codigo,
        vigente=True,
        carregada_em=agora(),
        estado="disponivel",
    )
    db.add(emenda)
    db.flush()
    for item in registros:
        fonte = (
            f"ROTAER AISWEB vigente; registro {item['rotaer_versao_id']}; "
            f"atualizado em {item['rotaer_atualizado_em'].isoformat()}"
            if item.get("rotaer_versao_id")
            else f"ROTAER emenda {codigo}"
        )
        atual = db.get(Aerodromo, item["icao"])
        if atual is None:
            db.add(
                Aerodromo(
                    icao=item["icao"],
                    nome=item["nome"],
                    tipo=item["tipo"],
                    lat=item["lat"],
                    lon=item["lon"],
                    elev_m=item["elev_m"],
                    rotaer_versao_id=item.get("rotaer_versao_id"),
                    rotaer_atualizado_em=item.get("rotaer_atualizado_em"),
                    telefone=item.get("telefone"),
                    email=item.get("email"),
                    contatos_rotaer_verificados=item.get(
                        "contatos_rotaer_verificados", False
                    ),
                    emenda_id=emenda.id,
                    fonte=fonte,
                )
            )
        else:
            atual.nome = item["nome"]
            atual.tipo = item["tipo"]
            atual.lat = item["lat"]
            atual.lon = item["lon"]
            atual.elev_m = item["elev_m"]
            atual.rotaer_versao_id = item.get("rotaer_versao_id")
            atual.rotaer_atualizado_em = item.get("rotaer_atualizado_em")
            atual.telefone = item.get("telefone")
            atual.email = item.get("email")
            atual.contatos_rotaer_verificados = item.get(
                "contatos_rotaer_verificados", False
            )
            atual.emenda_id = emenda.id
            atual.fonte = fonte
    db.commit()
    return "disponivel"


def _motivo_falha_rotaer(erro):
    if isinstance(erro, requests.RequestException):
        status = getattr(getattr(erro, "response", None), "status_code", None)
        if status is not None:
            return f"falha HTTP AISWEB (status {status})"
        return f"falha de rede AISWEB ({type(erro).__name__})"
    if isinstance(erro, ElementTree.ParseError):
        return "resposta XML AISWEB inválida"
    return str(erro)


def carregar_rotaer(db, corpo=None, getter=None, progresso=None):
    if corpo is None:
        chave, senha = _chaves_aisweb()
        if not chave or not senha:
            logger.warning("ROTAER indisponível: credenciais AISWEB não configuradas.")
            return _marcar_rotaer_indisponivel(db)
        try:
            codigo, registros = _baixar_rotaer(
                getter=getter,
                cache=_cache_rotaer(db),
                progresso=progresso,
            )
        except (ElementTree.ParseError, requests.RequestException, ValueError) as erro:
            logger.warning("ROTAER indisponível: %s", _motivo_falha_rotaer(erro))
            return _marcar_rotaer_indisponivel(db)
    else:
        try:
            codigo, registros = interpretar_rotaer(corpo)
        except (ElementTree.ParseError, ValueError) as erro:
            logger.warning("ROTAER indisponível: %s", _motivo_falha_rotaer(erro))
            return _marcar_rotaer_indisponivel(db)
    if not codigo or not registros:
        logger.warning(
            "ROTAER indisponível: a resposta não contém uma publicação completa."
        )
        return _marcar_rotaer_indisponivel(db)
    return _gravar_emenda(db, codigo, registros)


def _progresso_catalogo(fase, atual, total, reutilizados):
    if fase == "lista":
        if atual % TAMANHO_PAGINA_ROTAER and atual != total:
            return
        print(f"ROTAER lista: {atual}/{total}", file=sys.stderr)
        return
    if atual == 0 or atual % TAMANHO_PAGINA_ROTAER == 0 or atual == total:
        print(
            f"ROTAER detalhes: {atual}/{total} (reutilizados: {reutilizados})",
            file=sys.stderr,
        )


def main():
    from servidor import carregar_env
    from servidor.ambiente import resolver_ambiente
    from servidor.modelos import Sessao, configurar

    carregar_env()
    ambiente = resolver_ambiente()
    configurar(ambiente.database_url)
    db = Sessao()
    try:
        rotaer = carregar_rotaer(db, progresso=_progresso_catalogo)
        rab = carregar_rab(db)
    finally:
        Sessao.remove()
    print(f"ROTAER: {rotaer}")
    print(f"RAB: {rab}")


if __name__ == "__main__":
    main()
