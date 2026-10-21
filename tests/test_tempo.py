import requests

from servidor.tempo import meteorologia


class Resposta:
    def __init__(self, status=200, conteudo=b"[]", json_dados=None):
        self.status_code = status
        self.content = conteudo
        self._json = json_dados if json_dados is not None else []
        self.text = conteudo.decode() if isinstance(conteudo, bytes) else conteudo

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(self.status_code)

    def json(self):
        return self._json


def test_corpo_vazio_fica_indisponivel():
    def getter(url, params=None, timeout=None):
        assert timeout == 8
        return Resposta(204, b"")

    assert meteorologia("SBJD", getter).get("estado") == "indisponivel"


def test_falha_de_rede_fica_indisponivel():
    def getter(url, params=None, timeout=None):
        assert timeout == 8
        raise requests.Timeout()

    assert meteorologia("SBJD", getter).get("estado") == "indisponivel"


def test_sem_dado_nao_inventa_valor():
    def getter(url, params=None, timeout=None):
        return Resposta(200, b"[]", [])

    resultado = meteorologia("SBJD", getter)
    assert resultado.get("estado") == "indisponivel"
    assert "raw" not in resultado
