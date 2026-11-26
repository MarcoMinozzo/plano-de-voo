from pathlib import Path
import os


def carregar_env():
    raiz = Path(__file__).resolve().parent.parent
    caminhos = (
        Path.home() / ".config" / "plano-de-voo" / "aisweb.env",
        raiz / ".env",
    )
    for caminho in caminhos:
        if not caminho.exists():
            continue
        for linha in caminho.read_text(encoding="utf-8").splitlines():
            linha = linha.strip()
            if not linha or linha.startswith("#") or "=" not in linha:
                continue
            chave, valor = linha.split("=", 1)
            os.environ.setdefault(chave.strip(), valor.strip())
