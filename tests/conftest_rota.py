from datetime import datetime, timezone

from servidor.catalogo import carregar_rab, carregar_rotaer
from servidor.modelos import Aeronave, FonteTecnicaAeronave, Sessao, agora
from servidor.perfis_sinteticos import PERFIS_SINTETICOS

GRAU_NM = 60.04


def _lon(nm):
    return nm / GRAU_NM


def xml_emenda():
    b = _lon(60)
    c = _lon(120)
    return f"""
    <aisweb>
      <emenda>FICTICIA-1</emenda>
      <rotaer>
        <AeroCode>S0A1</AeroCode><name>Um</name><type>AD</type>
        <lat>0</lat><lng>0</lng><altM>10</altM>
      </rotaer>
      <rotaer>
        <AeroCode>S0B2</AeroCode><name>Dois</name><type>AD</type>
        <lat>0</lat><lng>{b}</lng><altM>12</altM>
      </rotaer>
      <rotaer>
        <AeroCode>S0C3</AeroCode><name>Tres</name><type>AD</type>
        <lat>0</lat><lng>{c}</lng><altM>14</altM>
      </rotaer>
      <rotaer>
        <AeroCode>H0H1</AeroCode><name>Heli</name><type>HP</type>
        <lat>1</lat><lng>1</lng><altM>5</altM>
      </rotaer>
    </aisweb>
    """


REGISTROS = (
    {"nome": "Avião Alfa", "pmd_kg": 900, "categoria": "aviao", "frota": 40},
    {"nome": "Avião Beta", "pmd_kg": 860, "categoria": "aviao", "frota": 9},
    {"nome": "Modelo Sem Manual", "pmd_kg": 700, "categoria": "aviao", "frota": 3},
    {"nome": "Grande Jato", "pmd_kg": 20000, "categoria": "aviao", "frota": 4},
)


def _preencher_manual(aeronave, fonte, pesos):
    aeronave.manual_estado = "gravado"
    aeronave.fonte_manual = fonte
    aeronave.peso_vazio_kg = pesos[0]
    aeronave.peso_max_decolagem_kg = pesos[1]
    aeronave.bagagem_max_kg = pesos[2]
    aeronave.braco_bagagem_m = pesos[3]
    aeronave.combustivel_valor = pesos[4]
    aeronave.combustivel_unidade = "gal"
    aeronave.velocidade_valor = pesos[5]
    aeronave.velocidade_unidade = "kt"
    aeronave.consumo_valor = pesos[6]
    aeronave.consumo_unidade = "gal/h"
    aeronave.itens_manutencao = [{"texto": "Conferir documentos", "fonte": fonte}]
    publicado = datetime(2024, 1, 1, tzinfo=timezone.utc)
    consultado = datetime(2026, 1, 1, tzinfo=timezone.utc)
    perfil = "perfil de cruzeiro sintético de teste"
    valores = (
        ("peso_vazio", pesos[0], "kg", None),
        ("peso_maximo_decolagem", pesos[1], "kg", None),
        ("bagagem_maxima", pesos[2], "kg", None),
        ("combustivel_utilizavel", pesos[4], "gal", None),
        ("velocidade_cruzeiro", pesos[5], "kt", perfil),
        ("consumo_cruzeiro", pesos[6], "gal/h", perfil),
    )
    if not aeronave.fontes_tecnicas:
        aeronave.fontes_tecnicas.extend(
            FonteTecnicaAeronave(
                campo=campo,
                valor=valor,
                unidade=unidade,
                tipo_fonte="secundaria",
                publicador="Fonte sintética de teste",
                referencia=f"{fonte}, dado fictício para teste",
                data_publicacao=publicado,
                data_consulta=consultado,
                modelo_variante=aeronave.nome,
                perfil=perfil_campo,
                revisao_edicao="fixture 1",
                pagina_tabela="teste",
                selecionada=True,
            )
            for campo, valor, unidade, perfil_campo in valores
        )


def preparar_rota():
    db = Sessao()
    try:
        carregar_rotaer(db, corpo=xml_emenda())
        carregar_rab(db, registros=list(REGISTROS), referencia="extrato-teste")
        alfa = db.query(Aeronave).filter_by(nome="Avião Alfa").one()
        beta = db.query(Aeronave).filter_by(nome="Avião Beta").one()
        sem = db.query(Aeronave).filter_by(nome="Modelo Sem Manual").one()
        _preencher_manual(alfa, "manual de teste Alfa", (510, 900, 20, 1.1, 12, 100, 10))
        _preencher_manual(beta, "manual de teste Beta", (480, 860, 15, 1.4, 18, 95, 8))
        db.commit()
        return {"alfa": alfa.id, "beta": beta.id, "sem_manual": sem.id}
    finally:
        Sessao.remove()


def semear_perfis_sinteticos_teste(db):
    momento = agora()
    valores = {
        "peso_vazio": (500.0, "peso_vazio_kg", "kg"),
        "peso_maximo_decolagem": (1000.0, "peso_max_decolagem_kg", "kg"),
        "bagagem_maxima": (100.0, "bagagem_max_kg", "kg"),
        "combustivel_utilizavel": (40.0, "combustivel_valor", "gal"),
        "velocidade_cruzeiro": (100.0, "velocidade_valor", "kt"),
        "consumo_cruzeiro": (10.0, "consumo_valor", "gal/h"),
    }
    ids = {}
    for perfil in PERFIS_SINTETICOS:
        aeronave = db.query(Aeronave).filter_by(nome=perfil.nome_exibicao).one_or_none()
        if aeronave is None:
            aeronave = Aeronave(
                nome=perfil.nome_exibicao,
                frota=0,
                manual_estado="proxy_sintetico",
                extrato_id=None,
                fonte_manual=(
                    "Perfil sintético didático; valores de fixture sem "
                    "validação aeronáutica."
                ),
                braco_bagagem_m=None,
                itens_manutencao=[],
            )
            for campo, (valor, atributo, unidade) in valores.items():
                setattr(aeronave, atributo, valor)
                if campo in {
                    "combustivel_utilizavel",
                    "velocidade_cruzeiro",
                    "consumo_cruzeiro",
                }:
                    setattr(
                        aeronave,
                        {
                            "combustivel_utilizavel": "combustivel_unidade",
                            "velocidade_cruzeiro": "velocidade_unidade",
                            "consumo_cruzeiro": "consumo_unidade",
                        }[campo],
                        unidade,
                    )
                aeronave.fontes_tecnicas.append(
                    FonteTecnicaAeronave(
                        campo=campo,
                        valor=valor,
                        unidade=unidade,
                        tipo_fonte="sintetica",
                        publicador="Fixture de teste",
                        referencia="Valor sintético sem validação aeronáutica.",
                        data_publicacao=None,
                        data_consulta=momento,
                        modelo_variante=perfil.alvo_modelo,
                        perfil="Cruzeiro de teste"
                        if campo in {"velocidade_cruzeiro", "consumo_cruzeiro"}
                        else None,
                        selecionada=True,
                    )
                )
            db.add(aeronave)
            db.flush()
        ids[perfil.alvo_modelo] = aeronave.id
    db.commit()
    return ids
