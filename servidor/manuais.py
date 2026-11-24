import json
import os
import sys
from pathlib import Path

from sqlalchemy import func

from servidor.catalogo import PORTE_PEQUENO_KG
from servidor.modelos import Aeronave

PASTA = Path(__file__).resolve().parent / "manuais"
NOME_SEMENTE = "Cessna 140"
KG_POR_LB = 0.45359237
M_POR_IN = 0.0254
L_POR_GAL = 3.785411784
KT_POR_MPH = 0.868976
KT_POR_KMH = 1 / 1.852

PESO = {"kg": 1.0, "lb": KG_POR_LB}
BRACO = {"m": 1.0, "in": M_POR_IN}
VOLUME = {"gal": 1.0, "L": 1 / L_POR_GAL}
MASSA_GALAO = {"kg/gal": 1.0, "lb/gal": KG_POR_LB}
VELOCIDADE = {"kt": 1.0, "mph": KT_POR_MPH, "km/h": KT_POR_KMH}
CONSUMO = {"gal/h": 1.0, "L/h": 1 / L_POR_GAL, "lb/h": KG_POR_LB}

GRANDEZAS = (
    ("peso_vazio", "peso_vazio_kg", PESO, "vazio"),
    ("peso_max_decolagem", "peso_max_decolagem_kg", PESO, "máximo de decolagem"),
    ("bagagem_max", "bagagem_max_kg", PESO, "bagagem"),
    ("braco_bagagem", "braco_bagagem_m", BRACO, "braço da bagagem"),
    ("combustivel_utilizavel", "combustivel_valor", VOLUME, "combustível utilizável"),
    ("massa_por_galao", "combustivel_kg_por_gal", MASSA_GALAO, "massa por galão"),
)
CAMPOS_DOCUMENTO = ("titulo", "numero", "revisao", "copia_publica")


class ManualInvalido(ValueError):
    pass


def _texto(dados, campo, nome=None):
    valor = dados.get(campo) if isinstance(dados, dict) else None
    if not isinstance(valor, str) or not valor.strip():
        raise ManualInvalido(nome or campo)
    return valor.strip()


def _grandeza(dados, campo, unidades, nome=None):
    nome = nome or campo
    item = dados.get(campo)
    if not isinstance(item, dict):
        raise ManualInvalido(nome)
    valor = item.get("valor")
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor <= 0:
        raise ManualInvalido(f"{nome}.valor")
    if item.get("unidade") not in unidades:
        raise ManualInvalido(f"{nome}.unidade")
    pagina = str(item.get("pagina") or "").strip()
    if not pagina:
        raise ManualInvalido(f"{nome}.pagina")
    return float(valor), item["unidade"], pagina


def _documento(dados):
    documento = dados.get("documento")
    valores = {campo: _texto(documento, campo, f"documento.{campo}") for campo in CAMPOS_DOCUMENTO}
    if not valores["copia_publica"].startswith(("https://", "http://")):
        raise ManualInvalido("documento.copia_publica")
    return valores


def _cruzeiro(dados, kg_por_gal):
    cruzeiro = dados.get("cruzeiro")
    if not isinstance(cruzeiro, dict):
        raise ManualInvalido("cruzeiro")
    condicao = _texto(cruzeiro, "condicao", "cruzeiro.condicao")
    valor, unidade, pagina_v = _grandeza(cruzeiro, "velocidade", VELOCIDADE, "cruzeiro.velocidade")
    velocidade = valor * VELOCIDADE[unidade]
    valor, unidade, pagina_c = _grandeza(cruzeiro, "consumo", CONSUMO, "cruzeiro.consumo")
    consumo = valor * CONSUMO[unidade]
    if unidade == "lb/h":
        consumo = consumo / kg_por_gal
    return condicao, velocidade, consumo, pagina_v, pagina_c


def _itens(dados, titulo):
    itens = dados.get("itens_checklist", [])
    if not isinstance(itens, list):
        raise ManualInvalido("itens_checklist")
    saida = []
    for item in itens:
        texto = _texto(item, "texto", "itens_checklist.texto")
        pagina = _texto(item, "pagina", "itens_checklist.pagina")
        saida.append({"texto": texto, "fonte": f"{titulo}, p. {pagina}"})
    return saida


def _modelo(dados):
    modelo = _texto(dados, "modelo_rab")
    if modelo.casefold() == NOME_SEMENTE.casefold():
        raise ManualInvalido("modelo_rab")
    if dados.get("experimental") is not False:
        raise ManualInvalido("experimental")
    return modelo


def ler_manual(dados):
    if not isinstance(dados, dict):
        raise ManualInvalido("json")
    modelo = _modelo(dados)
    fabricante = _texto(dados, "fabricante")
    documento = _documento(dados)
    campos, paginas = {}, []
    for campo, coluna, unidades, rotulo in GRANDEZAS:
        valor, unidade, pagina = _grandeza(dados, campo, unidades)
        campos[coluna] = round(valor * unidades[unidade], 4)
        paginas.append(f"{rotulo} p. {pagina}")
    if campos["peso_max_decolagem_kg"] > PORTE_PEQUENO_KG:
        raise ManualInvalido("peso_max_decolagem")
    if campos["peso_vazio_kg"] >= campos["peso_max_decolagem_kg"]:
        raise ManualInvalido("peso_vazio")
    condicao, velocidade, consumo, pagina_v, pagina_c = _cruzeiro(dados, campos["combustivel_kg_por_gal"])
    paginas += [f"velocidade p. {pagina_v}", f"consumo p. {pagina_c}"]
    campos.update(
        velocidade_valor=round(velocidade, 2),
        velocidade_unidade="kt",
        consumo_valor=round(consumo, 2),
        consumo_unidade="gal/h",
        combustivel_unidade="gal",
        itens_manutencao=_itens(dados, documento["titulo"]),
        fonte_manual=(
            f"{documento['titulo']}, {documento['numero']}, {documento['revisao']}, {fabricante}. "
            f"Páginas: {'; '.join(paginas)}. Cruzeiro: {condicao}. "
            f"Cópia pública: {documento['copia_publica']}"
        ),
    )
    return modelo, campos


def _gravar(db, modelo, campos):
    atual = db.query(Aeronave).filter(func.lower(Aeronave.nome) == modelo.casefold()).first()
    if atual is None:
        atual = Aeronave(nome=modelo, frota=0, itens_manutencao=[])
        db.add(atual)
    for coluna, valor in campos.items():
        setattr(atual, coluna, valor)
    atual.manual_estado = "gravado"


def _ler_arquivo(caminho):
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        raise ManualInvalido("json") from None


def carregar_manuais(db, pasta=PASTA):
    gravados, recusados, vistos = [], [], set()
    for caminho in sorted(Path(pasta).glob("*.json")):
        try:
            modelo, campos = ler_manual(_ler_arquivo(caminho))
            if modelo.casefold() in vistos:
                raise ManualInvalido("modelo_rab repetido")
        except ManualInvalido as erro:
            recusados.append((caminho.name, str(erro)))
            continue
        vistos.add(modelo.casefold())
        _gravar(db, modelo, campos)
        gravados.append(modelo)
    db.commit()
    return gravados, recusados


def main():
    from servidor import carregar_env
    from servidor.modelos import Sessao, configurar

    carregar_env()
    configurar(os.environ["DATABASE_URL"])
    db = Sessao()
    try:
        gravados, recusados = carregar_manuais(db)
    finally:
        Sessao.remove()
    for modelo in gravados:
        print(f"gravado: {modelo}")
    for arquivo, campo in recusados:
        print(f"recusado: {arquivo}: {campo}")
    sys.exit(1 if recusados else 0)


if __name__ == "__main__":
    main()
