from pathlib import Path


def test_operacao_nao_tem_segredo_e_cita_comandos():
    texto = Path("documentacao/operacao.md").read_text(encoding="utf-8")
    assert "alembic upgrade head" in texto
    assert "python -m servidor.semente" in texto
    assert "flask --app app:criar_app run" in texto
    assert "postgresql+" not in texto
    assert "REDEMET_API_KEY=" not in texto
    assert "AISWEB_API_PASS=" not in texto
    assert "SECRET_KEY=" not in texto
