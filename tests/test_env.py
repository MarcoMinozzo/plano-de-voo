import os
from pathlib import Path

from servidor import carregar_env


def test_carregar_env_le_credenciais_aisweb_fora_do_repositorio(
    monkeypatch, tmp_path
):
    arquivo = tmp_path / ".config" / "plano-de-voo" / "aisweb.env"
    arquivo.parent.mkdir(parents=True)
    arquivo.write_text(
        "AISWEB_API_KEY=chave-teste\nAISWEB_API_PASS=senha-teste\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    monkeypatch.delenv("AISWEB_API_KEY", raising=False)
    monkeypatch.delenv("AISWEB_API_PASS", raising=False)

    carregar_env()

    assert os.environ["AISWEB_API_KEY"] == "chave-teste"
    assert os.environ["AISWEB_API_PASS"] == "senha-teste"
