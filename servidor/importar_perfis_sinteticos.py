import os
from copy import deepcopy

from sqlalchemy import MetaData, Table, create_engine, inspect, select
from sqlalchemy.engine import URL, make_url
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import Session, sessionmaker

from servidor import carregar_env
from servidor.modelos import Aeronave, FonteTecnicaAeronave
from servidor.perfis_sinteticos import PERFIS_SINTETICOS


CAMPOS_TECNICOS = (
    ("peso_vazio", "peso_vazio_kg", "kg"),
    ("peso_maximo_decolagem", "peso_max_decolagem_kg", "kg"),
    ("bagagem_maxima", "bagagem_max_kg", "kg"),
    ("combustivel_utilizavel", "combustivel_valor", "gal"),
    ("velocidade_cruzeiro", "velocidade_valor", "kt"),
    ("consumo_cruzeiro", "consumo_valor", "gal/h"),
)

ATRIBUTOS_AERONAVE = {
    "peso_vazio_kg",
    "peso_max_decolagem_kg",
    "bagagem_max_kg",
    "combustivel_valor",
    "combustivel_unidade",
    "velocidade_valor",
    "velocidade_unidade",
    "consumo_valor",
    "consumo_unidade",
}

ATRIBUTOS_FONTE = {
    "campo",
    "valor",
    "unidade",
    "tipo_fonte",
    "publicador",
    "referencia",
    "data_publicacao",
    "data_consulta",
    "modelo_variante",
    "perfil",
    "revisao_edicao",
    "pagina_tabela",
    "selecionada",
    "divergencia",
    "limite_inferior",
    "limite_superior",
    "metodo_geracao",
    "versao_semente",
    "incerteza",
    "justificativa_comparabilidade",
}

AERONAVE_COLUNAS_ORIGEM = {
    "id",
    "nome",
    "frota",
    "peso_vazio_kg",
    "peso_max_decolagem_kg",
    "bagagem_max_kg",
    "braco_bagagem_m",
    "combustivel_valor",
    "combustivel_unidade",
    "velocidade_valor",
    "velocidade_unidade",
    "consumo_valor",
    "consumo_unidade",
    "itens_manutencao",
}

FONTE_COLUNAS_ORIGEM = {
    "aeronave_id",
    "campo",
    "valor",
    "unidade",
    "tipo_fonte",
    "publicador",
    "referencia",
    "data_consulta",
    "modelo_variante",
    "selecionada",
}


def _fonte_para_copiar(fonte):
    return {
        atributo: fonte.get(atributo)
        for atributo in ATRIBUTOS_FONTE
    }


def _validar_colunas_origem(tabela, obrigatorias):
    faltantes = sorted(obrigatorias - set(tabela.c.keys()))
    if faltantes:
        raise RuntimeError(
            f"A origem não possui colunas necessárias em {tabela.name}: "
            f"{', '.join(faltantes)}."
        )


def _perfis_na_origem(db_origem):
    conexao = db_origem.connection()
    tabelas = set(inspect(conexao).get_table_names())
    necessarias = {"aeronave", "fonte_tecnica_aeronave"}
    ausentes = sorted(necessarias - tabelas)
    if ausentes:
        raise RuntimeError(
            "A origem não contém as tabelas necessárias: "
            f"{', '.join(ausentes)}."
        )

    metadata = MetaData()
    aeronave_tabela = Table(
        "aeronave",
        metadata,
        autoload_with=conexao,
    )
    fonte_tabela = Table(
        "fonte_tecnica_aeronave",
        metadata,
        autoload_with=conexao,
    )
    _validar_colunas_origem(aeronave_tabela, AERONAVE_COLUNAS_ORIGEM)
    _validar_colunas_origem(fonte_tabela, FONTE_COLUNAS_ORIGEM)

    esperados = [perfil.nome_origem for perfil in PERFIS_SINTETICOS]
    linhas_aeronave = [
        dict(linha)
        for linha in conexao.execute(
            select(aeronave_tabela).where(aeronave_tabela.c.nome.in_(esperados))
        ).mappings()
    ]
    nomes = [linha["nome"] for linha in linhas_aeronave]
    encontrados = set(nomes)
    duplicados = sorted(nome for nome in encontrados if nomes.count(nome) > 1)
    faltantes = sorted(set(esperados) - encontrados)
    if len(linhas_aeronave) != len(PERFIS_SINTETICOS) or faltantes or duplicados:
        detalhes = []
        if faltantes:
            detalhes.append(f"faltantes: {', '.join(faltantes)}")
        if duplicados:
            detalhes.append(f"duplicados: {', '.join(duplicados)}")
        raise RuntimeError(
            "A origem precisa conter exatamente 20 perfis sintéticos numerados"
            + (f" ({'; '.join(detalhes)})." if detalhes else ".")
        )

    ids = [linha["id"] for linha in linhas_aeronave]
    fontes_por_aeronave = {identificador: [] for identificador in ids}
    for fonte in conexao.execute(
        select(fonte_tabela).where(fonte_tabela.c.aeronave_id.in_(ids))
    ).mappings():
        fontes_por_aeronave[fonte["aeronave_id"]].append(dict(fonte))
    return {
        linha["nome"]: {
            "aeronave": linha,
            "fontes_tecnicas": fontes_por_aeronave[linha["id"]],
        }
        for linha in linhas_aeronave
    }


def _capturar_perfil(origem, perfil):
    fontes = [
        fonte
        for fonte in origem["fontes_tecnicas"]
        if fonte["tipo_fonte"] == "sintetica" and fonte["selecionada"]
    ]
    fontes_por_campo = {}
    for fonte in fontes:
        if fonte["campo"] in fontes_por_campo:
            raise RuntimeError(
                f"Fonte sintética duplicada no perfil {perfil.alvo_modelo}: "
                f"{fonte['campo']}."
            )
        fontes_por_campo[fonte["campo"]] = fonte
    campos_esperados = {campo for campo, _atributo, _unidade in CAMPOS_TECNICOS}
    inesperados = fontes_por_campo.keys() - campos_esperados
    if inesperados:
        raise RuntimeError(
            f"Campos sintéticos não esperados no perfil {perfil.alvo_modelo}: "
            f"{', '.join(sorted(inesperados))}."
        )
    faltantes = campos_esperados - fontes_por_campo.keys()
    if faltantes:
        raise RuntimeError(
            f"Fontes técnicas ausentes no perfil {perfil.alvo_modelo}: "
            f"{', '.join(sorted(faltantes))}."
        )

    dados_aeronave = {
        "nome": perfil.nome_exibicao,
        "frota": origem["aeronave"]["frota"],
        "manual_estado": "proxy_sintetico",
        "extrato_id": None,
        "fonte_manual": (
            "Perfil sintético didático; alvo do exercício: "
            f"{perfil.alvo_modelo}. Valores não validados."
        ),
        "peso_vazio_kg": origem["aeronave"]["peso_vazio_kg"],
        "peso_max_decolagem_kg": origem["aeronave"]["peso_max_decolagem_kg"],
        "bagagem_max_kg": origem["aeronave"]["bagagem_max_kg"],
        "braco_bagagem_m": origem["aeronave"]["braco_bagagem_m"],
        "combustivel_valor": origem["aeronave"]["combustivel_valor"],
        "combustivel_unidade": origem["aeronave"]["combustivel_unidade"],
        "velocidade_valor": origem["aeronave"]["velocidade_valor"],
        "velocidade_unidade": origem["aeronave"]["velocidade_unidade"],
        "consumo_valor": origem["aeronave"]["consumo_valor"],
        "consumo_unidade": origem["aeronave"]["consumo_unidade"],
        "itens_manutencao": deepcopy(origem["aeronave"]["itens_manutencao"] or []),
    }
    for campo, atributo, _unidade in CAMPOS_TECNICOS:
        fonte = fontes_por_campo[campo]
        if fonte["valor"] is None or not fonte["unidade"]:
            raise RuntimeError(
                f"Valor ou unidade ausente no perfil {perfil.alvo_modelo}: {campo}."
            )
        if origem["aeronave"][atributo] is None:
            raise RuntimeError(
                f"Valor técnico ausente no perfil {perfil.alvo_modelo}: {campo}."
            )
        if campo in {"combustivel_utilizavel", "velocidade_cruzeiro", "consumo_cruzeiro"}:
            atributo_unidade = {
                "combustivel_utilizavel": "combustivel_unidade",
                "velocidade_cruzeiro": "velocidade_unidade",
                "consumo_cruzeiro": "consumo_unidade",
            }[campo]
            if not origem["aeronave"][atributo_unidade]:
                raise RuntimeError(
                    f"Unidade técnica ausente no perfil {perfil.alvo_modelo}: {campo}."
                )

    fontes_para_copiar = [
        _fonte_para_copiar(fontes_por_campo[campo])
        for campo, _atributo, _unidade in CAMPOS_TECNICOS
    ]
    return dados_aeronave, fontes_para_copiar


def _valores_tecnicos_iguais(aeronave, esperado, fontes_esperadas):
    if aeronave.manual_estado != "proxy_sintetico" or aeronave.extrato_id is not None:
        return False
    if any(
        getattr(aeronave, atributo) != esperado[atributo]
        for atributo in ATRIBUTOS_AERONAVE
    ):
        return False

    fontes = [
        fonte
        for fonte in aeronave.fontes_tecnicas
        if fonte.tipo_fonte == "sintetica" and fonte.selecionada
    ]
    atuais = {fonte.campo: fonte for fonte in fontes}
    if len(fontes) != len(CAMPOS_TECNICOS) or len(atuais) != len(fontes):
        return False
    for fonte_esperada in fontes_esperadas:
        fonte_atual = atuais.get(fonte_esperada["campo"])
        if fonte_atual is None:
            return False
        if (
            fonte_atual.valor != fonte_esperada["valor"]
            or fonte_atual.unidade != fonte_esperada["unidade"]
        ):
            return False
    return True


def transferir_perfis_sinteticos(db_origem: Session, db_destino: Session):
    origem_por_nome = _perfis_na_origem(db_origem)
    perfis_capturados = []
    for perfil in PERFIS_SINTETICOS:
        dados_aeronave, fontes = _capturar_perfil(
            origem_por_nome[perfil.nome_origem],
            perfil,
        )
        perfis_capturados.append((perfil, dados_aeronave, fontes))

    importados = 0
    ja_presentes = 0
    with db_destino.begin():
        existentes = {}
        for perfil, _dados, _fontes in perfis_capturados:
            registros = (
                db_destino.query(Aeronave)
                .filter_by(
                    nome=perfil.nome_exibicao,
                    manual_estado="proxy_sintetico",
                )
                .all()
            )
            if len(registros) > 1:
                raise RuntimeError(
                    f"Conflito: mais de um registro para {perfil.alvo_modelo}."
                )
            if registros:
                existentes[perfil.nome_exibicao] = registros[0]

        conflitos = []
        for perfil, dados, fontes in perfis_capturados:
            existente = existentes.get(perfil.nome_exibicao)
            if existente is not None and not _valores_tecnicos_iguais(
                existente, dados, fontes
            ):
                conflitos.append(perfil.alvo_modelo)
        if conflitos:
            raise RuntimeError(
                "Conflito de valores em perfis já existentes: "
                + ", ".join(conflitos)
                + ". Nenhum dado foi alterado."
            )

        for perfil, dados, fontes in perfis_capturados:
            if perfil.nome_exibicao in existentes:
                ja_presentes += 1
                continue
            aeronave = Aeronave(**dados)
            db_destino.add(aeronave)
            db_destino.flush()
            for dados_fonte in fontes:
                db_destino.add(
                    FonteTecnicaAeronave(
                        aeronave_id=aeronave.id,
                        **dados_fonte,
                    )
                )
            importados += 1

    return importados, ja_presentes


def _url_banco(valor, variavel):
    try:
        url = make_url(valor)
    except ArgumentError:
        raise RuntimeError(f"{variavel} contém uma URL inválida.") from None
    if url.get_backend_name() != "postgresql" or not url.database:
        raise RuntimeError(f"{variavel} precisa apontar para uma base PostgreSQL.")
    return url


def _mesma_base(url_origem: URL, url_destino: URL):
    return (
        url_origem.get_backend_name(),
        (url_origem.host or "").casefold(),
        url_origem.port or 5432,
        url_origem.database,
    ) == (
        url_destino.get_backend_name(),
        (url_destino.host or "").casefold(),
        url_destino.port or 5432,
        url_destino.database,
    )


def main():
    carregar_env()
    origem_raw = os.environ.get("DATABASE_URL_DEMO_ORIGEM", "").strip()
    destino_raw = os.environ.get("DATABASE_URL", "").strip()
    if not origem_raw:
        raise RuntimeError("DATABASE_URL_DEMO_ORIGEM não está configurada.")
    if not destino_raw:
        raise RuntimeError("DATABASE_URL não está configurada.")
    url_origem = _url_banco(origem_raw, "DATABASE_URL_DEMO_ORIGEM")
    url_destino = _url_banco(destino_raw, "DATABASE_URL")
    if _mesma_base(url_origem, url_destino):
        raise RuntimeError("Origem e destino precisam ser bases PostgreSQL distintas.")

    engine_origem = create_engine(url_origem)
    engine_destino = create_engine(url_destino)
    sessao_origem = None
    sessao_destino = None
    try:
        with engine_origem.connect() as conexao_origem:
            with conexao_origem.begin():
                conexao_origem.exec_driver_sql("SET TRANSACTION READ ONLY")
                sessao_origem = sessionmaker(
                    bind=conexao_origem,
                    expire_on_commit=False,
                )()
                sessao_destino = sessionmaker(
                    bind=engine_destino,
                    expire_on_commit=False,
                )()
                importados, ja_presentes = transferir_perfis_sinteticos(
                    sessao_origem,
                    sessao_destino,
                )
    finally:
        if sessao_origem is not None:
            sessao_origem.close()
        if sessao_destino is not None:
            sessao_destino.close()
        engine_origem.dispose()
        engine_destino.dispose()

    print(
        "Perfis sintéticos importados: "
        f"{importados}; já presentes: {ja_presentes}."
    )


if __name__ == "__main__":
    main()
