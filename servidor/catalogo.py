import csv
import os
from io import StringIO
from pathlib import Path
from xml.etree import ElementTree

import requests

from sqlalchemy import func, or_

from servidor.modelos import Aerodromo, Aeronave, EmendaRotaer, ExtratoRab, agora

PORTE_PEQUENO_KG = 5670
URL_AISWEB = "https://aisweb.decea.gov.br/api/"
TIMEOUT = 30


def emenda_vigente(db):
    return (
        db.query(EmendaRotaer)
        .filter_by(vigente=True, estado="disponivel")
        .one_or_none()
    )


def extrato_vigente(db):
    return (
        db.query(ExtratoRab)
        .filter_by(estado="disponivel")
        .order_by(ExtratoRab.carregado_em.desc())
        .first()
    )


def aerodromos_oferecidos(db):
    emenda = emenda_vigente(db)
    if emenda is None:
        return "indisponivel", []
    lista = (
        db.query(Aerodromo)
        .filter_by(emenda_id=emenda.id, tipo="aerodromo")
        .order_by(Aerodromo.icao)
        .all()
    )
    return "disponivel", lista


def lugares_da_tela(db):
    emenda = emenda_vigente(db)
    if emenda is not None:
        return aerodromos_oferecidos(db)
    locais = (
        db.query(Aerodromo)
        .filter_by(tipo="aerodromo")
        .order_by(Aerodromo.icao)
        .all()
    )
    return "local", locais


def correspondencias(db, texto):
    emenda = emenda_vigente(db)
    if emenda is None:
        return "indisponivel", []
    bruto = " ".join((texto or "").split())
    if len(bruto) < 2:
        return "curto", []
    like = f"%{bruto}%"
    lista = (
        db.query(Aerodromo)
        .filter(
            Aerodromo.emenda_id == emenda.id,
            Aerodromo.tipo == "aerodromo",
            or_(Aerodromo.icao.ilike(like), Aerodromo.nome.ilike(like)),
        )
        .order_by(Aerodromo.icao)
        .all()
    )
    return "disponivel", lista


def modelos_visiveis(db):
    extrato = extrato_vigente(db)
    consulta = db.query(Aeronave).filter(Aeronave.peso_max_decolagem_kg <= PORTE_PEQUENO_KG)
    if extrato is not None:
        consulta = consulta.filter(Aeronave.extrato_id == extrato.id)
        estado = "disponivel"
    else:
        consulta = consulta.filter(Aeronave.manual_estado == "gravado")
        estado = "indisponivel"
    lista = consulta.order_by(Aeronave.frota.desc(), Aeronave.nome.asc()).all()
    return estado, lista


def _chaves_aisweb():
    chave = os.environ.get("AISWEB_API_KEY", "").strip()
    senha = os.environ.get("AISWEB_API_PASS", "").strip()
    return chave, senha


def _tag(elemento):
    return elemento.tag.rsplit("}", 1)[-1].lower()


def _texto(elemento, *nomes):
    procurados = {nome.lower() for nome in nomes}
    for filho in list(elemento):
        if _tag(filho) in procurados and (filho.text or "").strip():
            return filho.text.strip()
    return ""


def _decimal(valor):
    texto = (valor or "").strip().replace(",", ".")
    if not texto:
        raise ValueError("coordenada vazia")
    hemi = texto[-1].upper()
    if hemi in "NSEW":
        corpo = texto[:-1].strip().replace("°", " ").replace("'", " ").replace('"', " ")
        partes = [p for p in corpo.split() if p]
        graus = float(partes[0])
        minutos = float(partes[1]) if len(partes) > 1 else 0.0
        segundos = float(partes[2]) if len(partes) > 2 else 0.0
        numero = graus + minutos / 60 + segundos / 3600
        if hemi in "SW":
            numero = -numero
        return numero
    return float(texto)


def _tipo_lugar(valor):
    texto = (valor or "").strip().upper()
    if not texto:
        return None
    if "HELI" in texto or texto in {"HP", "H", "HL"}:
        return "heliponto"
    if "AERO" in texto or texto in {"AD", "A"}:
        return "aerodromo"
    return None


def interpretar_rotaer(corpo):
    if isinstance(corpo, bytes):
        corpo = corpo.decode("utf-8", errors="replace")
    if not (corpo or "").strip():
        return None, []
    raiz = ElementTree.fromstring(corpo)
    codigo = None
    for filho in list(raiz):
        if _tag(filho) == "emenda" and (filho.text or "").strip():
            codigo = filho.text.strip()
            break
    if codigo is None:
        for elemento in raiz.iter():
            if _tag(elemento) == "emenda" and (elemento.text or "").strip():
                codigo = elemento.text.strip()
                break
    registros = []
    for elemento in raiz.iter():
        if _tag(elemento) not in {"rotaer", "aerodromo"}:
            continue
        icao = _texto(elemento, "AeroCode", "icao", "identificador").upper()
        nome = _texto(elemento, "name", "nome")
        tipo = _tipo_lugar(_texto(elemento, "type", "tipo"))
        if not icao or not nome or tipo is None or len(icao) > 16:
            continue
        try:
            lat = _decimal(_texto(elemento, "lat", "latitude"))
            lon = _decimal(_texto(elemento, "lng", "lon", "longitude"))
            elev = float(_texto(elemento, "altM", "elev_m", "elevacao").replace(",", "."))
        except (TypeError, ValueError):
            continue
        registros.append(
            {"icao": icao, "nome": nome, "tipo": tipo, "lat": lat, "lon": lon, "elev_m": elev}
        )
    return codigo, registros


def _marcar_rotaer_indisponivel(db):
    for emenda in db.query(EmendaRotaer).filter_by(vigente=True):
        emenda.vigente = False
    db.flush()
    db.add(
        EmendaRotaer(
            codigo_emenda="indisponivel",
            vigente=False,
            carregada_em=agora(),
            estado="indisponivel",
        )
    )
    db.commit()
    return "indisponivel"


def _gravar_emenda(db, codigo, registros):
    for emenda in db.query(EmendaRotaer).filter_by(vigente=True):
        emenda.vigente = False
    db.flush()
    emenda = EmendaRotaer(
        codigo_emenda=codigo,
        vigente=True,
        carregada_em=agora(),
        estado="disponivel",
    )
    db.add(emenda)
    db.flush()
    fonte = f"ROTAER emenda {codigo}"
    for item in registros:
        atual = db.get(Aerodromo, item["icao"])
        if atual is None:
            db.add(
                Aerodromo(
                    icao=item["icao"],
                    nome=item["nome"],
                    tipo=item["tipo"],
                    lat=item["lat"],
                    lon=item["lon"],
                    elev_m=item["elev_m"],
                    emenda_id=emenda.id,
                    fonte=fonte,
                )
            )
        else:
            atual.nome = item["nome"]
            atual.tipo = item["tipo"]
            atual.lat = item["lat"]
            atual.lon = item["lon"]
            atual.elev_m = item["elev_m"]
            atual.emenda_id = emenda.id
            atual.fonte = fonte
    db.commit()
    return "disponivel"


def _baixar_rotaer(getter=None):
    chave, senha = _chaves_aisweb()
    obter = getter or requests.get
    vistos = set()
    registros = []
    codigo = None
    inicio = 0
    passo = 100
    while inicio < 20000:
        resposta = obter(
            URL_AISWEB,
            params={
                "apiKey": chave,
                "apiPass": senha,
                "area": "rotaer",
                "rowstart": inicio,
                "rowend": inicio + passo - 1,
            },
            timeout=TIMEOUT,
        )
        resposta.raise_for_status()
        pagina_codigo, pagina = interpretar_rotaer(resposta.text or "")
        if pagina_codigo and not codigo:
            codigo = pagina_codigo
        novos = 0
        for item in pagina:
            if item["icao"] in vistos:
                continue
            vistos.add(item["icao"])
            registros.append(item)
            novos += 1
        if novos == 0 or len(pagina) < passo:
            break
        inicio += passo
    return codigo, registros


def carregar_rotaer(db, corpo=None, getter=None):
    if corpo is None:
        chave, senha = _chaves_aisweb()
        if not chave or not senha:
            if emenda_vigente(db) is not None:
                return "disponivel"
            return _marcar_rotaer_indisponivel(db)
        try:
            codigo, registros = _baixar_rotaer(getter)
        except Exception:
            return _marcar_rotaer_indisponivel(db)
    else:
        try:
            codigo, registros = interpretar_rotaer(corpo)
        except ElementTree.ParseError:
            return _marcar_rotaer_indisponivel(db)
    if not codigo or not registros:
        return _marcar_rotaer_indisponivel(db)
    return _gravar_emenda(db, codigo, registros)


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
        canc = str(bruto.get("cancelado") or "").strip()
        if canc:
            continue
        try:
            pmd = _numero(bruto.get("pmd_kg") if bruto.get("pmd_kg") is not None else bruto.get("pmd"))
        except (TypeError, ValueError):
            continue
        categoria = bruto.get("categoria") or ""
        tipo = bruto.get("tipo") or ""
        if not _linha_aviao(categoria, tipo, pmd):
            continue
        frota = bruto.get("frota")
        chave = nome.casefold()
        grupo = grupos.setdefault(
            chave,
            {
                "nome": nome,
                "pmd": pmd,
                "frota": 0,
                "contou": False,
                "fabricante": str(bruto.get("fabricante") or "").strip(),
            },
        )
        grupo["pmd"] = max(grupo["pmd"], pmd)
        if frota is None or str(frota).strip() == "":
            grupo["frota"] += 1
        else:
            grupo["frota"] += int(float(str(frota).replace(",", ".")))
            grupo["contou"] = True
    return list(grupos.values())


def _ler_csv_rab(texto):
    linhas = texto.splitlines()
    inicio = 0
    for indice, linha in enumerate(linhas[:30]):
        if "DS_MODELO" in linha.upper():
            inicio = indice
            break
    texto = "\n".join(linhas[inicio:])
    amostra = texto[:4000]
    delim = ";" if amostra.count(";") >= amostra.count(",") else ","
    leitor = csv.DictReader(StringIO(texto), delimiter=delim)
    if not leitor.fieldnames:
        return []
    campos = {nome: nome for nome in leitor.fieldnames}

    def achar(*opcoes):
        for nome in campos:
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
        classe = linha.get(col_cat) if col_cat else ""
        pouso = linha.get(col_tipo) if col_tipo else ""
        saida.append(
            {
                "nome": linha.get(col_nome),
                "pmd_kg": linha.get(col_pmd),
                "categoria": classe if classe or col_cat else "aviao",
                "tipo": pouso or "",
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


def _compativel_com_manual(atual, grupo):
    if atual.nome.casefold() == grupo["nome"].casefold():
        return True
    fabricante = (grupo.get("fabricante") or "").strip()
    if not fabricante or atual.manual_estado != "gravado":
        return atual.nome.casefold() == grupo["nome"].casefold()
    token = fabricante.casefold().split()[0]
    nome = atual.nome.casefold()
    modelo = grupo["nome"].casefold()
    if len(token) < 4 or token not in nome:
        return False
    if atual.peso_max_decolagem_kg is not None and abs(float(atual.peso_max_decolagem_kg) - float(grupo["pmd"])) > 1:
        return False
    return nome == modelo or nome.endswith(" " + modelo)


def _manual_gravado(db, grupo):
    exatos = (
        db.query(Aeronave)
        .filter(func.lower(Aeronave.nome) == grupo["nome"].casefold())
        .all()
    )
    for atual in exatos:
        if _compativel_com_manual(atual, grupo):
            return atual
    if not (grupo.get("fabricante") or "").strip():
        return None
    achados = [
        atual
        for atual in db.query(Aeronave).filter_by(manual_estado="gravado")
        if atual.nome.casefold() != grupo["nome"].casefold() and _compativel_com_manual(atual, grupo)
    ]
    if len(achados) == 1:
        return achados[0]
    return None


def carregar_rab(db, registros=None, referencia="extrato-publico"):
    if registros is None:
        caminho = os.environ.get("RAB_EXTRATO", "").strip()
        if not caminho or not Path(caminho).is_file():
            return _marcar_rab_indisponivel(db)
        arquivo = Path(caminho)
        referencia = arquivo.name
        try:
            try:
                texto = arquivo.read_text(encoding="utf-8-sig")
            except UnicodeDecodeError:
                texto = arquivo.read_text(encoding="latin-1")
            registros = _ler_csv_rab(texto)
        except OSError:
            return _marcar_rab_indisponivel(db)
    grupos = _agrupar_rab(registros)
    for extrato in db.query(ExtratoRab).filter_by(estado="disponivel"):
        extrato.estado = "indisponivel"
    extrato = ExtratoRab(referencia=referencia[:160], carregado_em=agora(), estado="disponivel")
    db.add(extrato)
    db.flush()
    for grupo in grupos:
        atual = _manual_gravado(db, grupo)
        if atual is not None and atual.manual_estado == "gravado":
            atual.frota = grupo["frota"]
            atual.extrato_id = extrato.id
            continue
        if atual is None:
            db.add(
                Aeronave(
                    nome=grupo["nome"],
                    frota=grupo["frota"],
                    manual_estado="ausente",
                    extrato_id=extrato.id,
                    fonte_manual=None,
                    peso_max_decolagem_kg=grupo["pmd"],
                    itens_manutencao=[],
                )
            )
        else:
            atual.frota = grupo["frota"]
            atual.extrato_id = extrato.id
            atual.manual_estado = "ausente"
            atual.peso_max_decolagem_kg = grupo["pmd"]
            atual.fonte_manual = None
    db.commit()
    return "disponivel"


def sol_aerodromo(icao, hora, getter=None):
    from datetime import datetime

    if os.environ.get("PLANO_CONSULTAR_SOL", "1") == "0":
        return {"estado": "indisponivel"}
    chave, senha = _chaves_aisweb()
    if not chave or not senha:
        return {"estado": "indisponivel"}
    obter = getter or requests.get
    try:
        resposta = obter(
            URL_AISWEB,
            params={
                "apiKey": chave,
                "apiPass": senha,
                "area": "sol",
                "icao": icao,
                "dt": hora.date().isoformat(),
            },
            timeout=8,
        )
        resposta.raise_for_status()
        raiz = ElementTree.fromstring(resposta.text or "")
    except Exception:
        return {"estado": "indisponivel"}
    for elemento in raiz.iter():
        if _tag(elemento) not in {"sunset", "por_do_sol", "sunset_utc"}:
            continue
        texto = (elemento.text or "").strip()
        if not texto:
            continue
        try:
            instante = datetime.fromisoformat(texto)
        except ValueError:
            continue
        if instante.tzinfo is None:
            continue
        return {"estado": "disponivel", "por_do_sol": instante, "fonte": "AISWEB sol"}
    return {"estado": "indisponivel"}


def main():
    from servidor import carregar_env
    from servidor.modelos import Sessao, configurar

    carregar_env()
    configurar(os.environ["DATABASE_URL"])
    db = Sessao()
    try:
        rotaer = carregar_rotaer(db)
        rab = carregar_rab(db)
    finally:
        Sessao.remove()
    print(f"ROTAER: {rotaer}")
    print(f"RAB: {rab}")


if __name__ == "__main__":
    main()
