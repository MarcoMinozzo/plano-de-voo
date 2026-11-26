from servidor.modelos import Aeronave, Sessao
from servidor.proveniencia import procedencia_aeronave, selecionar_fonte_aplicavel
from tests.conftest_rota import semear_perfis_sinteticos_teste


def test_proxies_nao_dependem_de_intervalos_ou_referencias_aeronauticas(cliente):
    with cliente.application.app_context():
        db = Sessao()
        ids = semear_perfis_sinteticos_teste(db)
        aeronave = db.get(Aeronave, ids["CESSNA AIRCRAFT 152"])

        fonte = selecionar_fonte_aplicavel(db, aeronave, "peso_vazio")
        procedencia = procedencia_aeronave(db, aeronave)

        assert fonte is not None
        assert fonte.limite_inferior is None
        assert fonte.metodo_geracao is None
        assert set(procedencia) == {
            "peso_vazio",
            "peso_maximo_decolagem",
            "bagagem_maxima",
            "combustivel_utilizavel",
            "velocidade_cruzeiro",
            "consumo_cruzeiro",
        }
        assert all(item is not None for item in procedencia.values())
        assert procedencia["peso_vazio"]["valor"] == 500
        assert procedencia["peso_vazio"]["unidade"] == "kg"
        assert procedencia["peso_vazio"]["dados_sinteticos"] is True
        assert procedencia["velocidade_cruzeiro"]["unidade"] == "kt"
        assert procedencia["consumo_cruzeiro"]["unidade"] == "gal/h"
