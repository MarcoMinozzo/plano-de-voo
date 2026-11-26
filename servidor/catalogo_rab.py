import csv
import os
from io import StringIO
from pathlib import Path

from sqlalchemy import func

from servidor.modelos import Aeronave, ExtratoRab, agora

PORTE_PEQUENO_KG = 5670


def _numero(valor):
    texto = str(valor).strip()
    if not texto:
        raise ValueError("número vazio")
    if "," in texto and "." in texto:
        texto = texto.replace(".", "").replace(",", ".")
    elif "," in texto:
        texto = texto.replace(",", ".")
    return float(texto)


def _linha_aviao(categoria, tipo, pmd):
    texto = f"{categoria or ''} {tipo or ''}".upper()
    if any(p in texto for p in ("HELIC", "HELI", "PLANAD", "BALAO", "BALÃO", "GIRO", "DIRIG", "DRONE", "RPAS")):
        return False
    if pmd is None or pmd > PORTE_PEQUENO_KG:
        return False
    if any(p in texto for p in ("AVIAO", "AVIÃO", "AVIA", "AIRPLANE")):
        return True
    classe = (categoria or "").strip().upper()
    return classe[:1] in {"L", "A", "S"}


def _agrupar_rab(registros):
    grupos = {}
    for bruto in registros:
        nome = str(bruto.get("nome") or bruto.get("modelo") or "").strip()
        if not nome or len(nome) > 200:
            continue
        if str(bruto.get("cancelado") or "").strip():
            continue
        try:
            pmd = _numero(bruto.get("pmd_kg") if bruto.get("pmd_kg") is not None else bruto.get("pmd"))
        except (TypeError, ValueError):
            continue
        if not _linha_aviao(bruto.get("categoria") or "", bruto.get("tipo") or "", pmd):
            continue
        frota = bruto.get("frota")
        chave = nome.casefold()
        grupo = grupos.setdefault(
            chave,
            {"nome": nome, "pmd": pmd, "frota": 0, "fabricante": str(bruto.get("fabricante") or "").strip()},
        )
        grupo["pmd"] = max(grupo["pmd"], pmd)
        if frota is None or str(frota).strip() == "":
            grupo["frota"] += 1
        else:
            grupo["frota"] += int(float(str(frota).replace(",", ".")))
    return list(grupos.values())


def _ler_csv_rab(texto):
    linhas = texto.splitlines()
    inicio = next(
        (indice for indice, linha in enumerate(linhas[:30]) if "DS_MODELO" in linha.upper()),
        0,
    )
    texto = "\n".join(linhas[inicio:])
    amostra = texto[:4000]
    delim = ";" if amostra.count(";") >= amostra.count(",") else ","
    leitor = csv.DictReader(StringIO(texto), delimiter=delim)
    if not leitor.fieldnames:
        return []

    def achar(*opcoes):
        for nome in leitor.fieldnames:
            if nome and nome.strip().upper() in opcoes:
                return nome
        return None

    col_nome = achar("DS_MODELO", "MODELO", "NOME", "NM_MODELO")
    col_pmd = achar("NR_PMD", "PMD", "PMD_KG", "PESO_MAX_DECOLAGEM_KG")
    col_cat = achar("CD_CLS", "CD_CATEGORIA", "CATEGORIA", "DS_CATEGORIA")
    col_tipo = achar("TP_POUSO", "DS_TIPO", "TIPO")
    col_fab = achar("NM_FABRICANTE", "FABRICANTE")
    col_frota = achar("FROTA", "QT", "QUANTIDADE")
    col_canc = achar("DT_CANC", "CANCELADO")
    if col_nome is None or col_pmd is None:
        return []
    saida = []
    for linha in leitor:
        saida.append(
            {
                "nome": linha.get(col_nome),
                "pmd_kg": linha.get(col_pmd),
                "categoria": linha.get(col_cat) if col_cat else "aviao",
                "tipo": linha.get(col_tipo) if col_tipo else "",
                "fabricante": linha.get(col_fab) if col_fab else "",
                "frota": linha.get(col_frota) if col_frota else None,
                "cancelado": linha.get(col_canc) if col_canc else "",
            }
        )
    return saida


def _marcar_rab_indisponivel(db):
    for extrato in db.query(ExtratoRab).filter_by(estado="disponivel"):
        extrato.estado = "indisponivel"
    db.add(ExtratoRab(referencia="indisponivel", carregado_em=agora(), estado="indisponivel"))
    db.commit()
    return "indisponivel"


def _modelo_exato(db, grupo):
    return db.query(Aeronave).filter(
        func.lower(Aeronave.nome) == grupo["nome"].casefold()
    ).first()


def carregar_rab(db, registros=None, referencia="extrato-publico"):
    if registros is None:
        caminho = os.environ.get("RAB_EXTRATO", "").strip()
        if not caminho or not Path(caminho).is_file():
            return _marcar_rab_indisponivel(db)
        arquivo = Path(caminho)
        referencia = arquivo.name
        try:
            texto = arquivo.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            texto = arquivo.read_text(encoding="latin-1")
        except OSError:
            return _marcar_rab_indisponivel(db)
        registros = _ler_csv_rab(texto)
    grupos = _agrupar_rab(registros)
    for extrato in db.query(ExtratoRab).filter_by(estado="disponivel"):
        extrato.estado = "indisponivel"
    extrato = ExtratoRab(
        referencia=referencia[:160],
        carregado_em=agora(),
        estado="disponivel",
    )
    db.add(extrato)
    db.flush()
    for grupo in grupos:
        atual = _modelo_exato(db, grupo)
        if atual is not None and atual.manual_estado == "gravado":
            atual.frota = grupo["frota"]
            atual.extrato_id = extrato.id
            continue
        if atual is None:
            db.add(Aeronave(
                nome=grupo["nome"],
                frota=grupo["frota"],
                manual_estado="ausente",
                extrato_id=extrato.id,
                fonte_manual=None,
                peso_max_decolagem_kg=grupo["pmd"],
                itens_manutencao=[],
            ))
        else:
            atual.frota = grupo["frota"]
            atual.extrato_id = extrato.id
            atual.manual_estado = "ausente"
    db.commit()
    return "disponivel"
