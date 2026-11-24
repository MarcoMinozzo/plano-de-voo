from servidor.catalogo import carregar_rab, carregar_rotaer
from servidor.modelos import Aeronave, Sessao

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
