import re

from servidor.modelos import Aeronave, ExtratoRab, Sessao
from servidor.perfis_sinteticos import PERFIS_SINTETICOS
from tests.conftest import JSON, cadastrar
from tests.conftest_rota import semear_perfis_sinteticos_teste


def test_perfis_sinteticos_aparecem_separados_sem_rab(cliente):
    cadastrar(cliente)
    db = Sessao()
    try:
        semear_perfis_sinteticos_teste(db)
        for aeronave in db.query(Aeronave).all():
            aeronave.extrato_id = None
        db.query(ExtratoRab).delete(synchronize_session=False)
        db.commit()
    finally:
        Sessao.remove()

    resposta = cliente.get("/aeronaves", headers=JSON).get_json()
    html = cliente.get("/planos/novo").get_data(as_text=True)
    perfis = resposta["perfis_sinteticos"]

    assert resposta["estado"] == "indisponivel"
    assert resposta["modelos"] == []
    assert len(perfis) == 20
    assert "modo_demo" not in resposta
    assert [perfil["nome"] for perfil in perfis] == [
        perfil.alvo_modelo for perfil in PERFIS_SINTETICOS
    ]
    assert all(perfil["dados_sinteticos"] for perfil in perfis)
    assert all(
        perfil["rotulo"]
        == "perfil sintético didático — valores não validados; "
        "não representam dados do modelo associado"
        for perfil in perfis
    )
    assert not any("Aeronave DEMO" in perfil["nome"] for perfil in perfis)
    assert "Aeronave DEMO" not in html
    assert "Proxy DEMO" not in html
    assert '<optgroup label="Perfis sintéticos didáticos">' in html
    grupo_sintetico = re.search(
        r'<optgroup label="Perfis sintéticos didáticos">(.*?)</optgroup>',
        html,
        re.S,
    )
    assert grupo_sintetico is not None
    assert re.findall(r"<option[^>]*>(.*?)</option>", grupo_sintetico.group(1)) == [
        perfil.alvo_modelo for perfil in PERFIS_SINTETICOS
    ]
    assert "não autorizam o voo" in html
