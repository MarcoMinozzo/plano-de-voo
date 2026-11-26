from dataclasses import dataclass
import os
from typing import Mapping

from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


@dataclass(frozen=True)
class Ambiente:
    database_url: str


def resolver_ambiente(variaveis: Mapping[str, str] | None = None) -> Ambiente:
    valores = os.environ if variaveis is None else variaveis
    database_url = valores.get("DATABASE_URL", "").strip()
    if not database_url:
        raise RuntimeError("DATABASE_URL não está configurada.")
    try:
        url = make_url(database_url)
    except ArgumentError:
        raise RuntimeError("A URL de banco configurada é inválida.") from None
    if url.get_backend_name() != "postgresql":
        raise RuntimeError("DATABASE_URL precisa apontar para uma base PostgreSQL.")
    if not url.database:
        raise RuntimeError("DATABASE_URL precisa identificar uma base PostgreSQL.")
    return Ambiente(database_url=database_url)
