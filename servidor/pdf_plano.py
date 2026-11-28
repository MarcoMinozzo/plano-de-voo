import re
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path

from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph

from servidor.pdf_layout import (
    _estilos,
    _html,
    _montar_documento,
    nome_relatorio,
    _paragrafo,
    _partida_rotulo,
    _rota_completa,
    _tabela_fontes,
    _tabela_grade,
    _tabela_resultados,
    _titulo_secao,
)

CAMINHO = Path(__file__).resolve().parent.parent / "documentacao" / "piloto.md"

ROTULOS_LIDOS = {
    "calculado": "aceitável para planejamento",
    "inaceitavel": "não aceitável",
    "aceitavel": "aceitável para planejamento",
    "indisponivel": "indisponível",
    "disponivel": "disponível",
    "nao_fornecido_pela_fonte": "não fornecido pela fonte",
}


def rotulo_lido(estado):
    return ROTULOS_LIDOS.get(estado, estado or "")


def ler_orientacao():
    return CAMINHO.read_text(encoding="utf-8")


def ler_orientacao_plano():
    texto = ler_orientacao()
    return re.sub(
        r"(?ms)^## Perfis sintéticos didáticos\s*\n.*?(?=^## |\Z)",
        "",
        texto,
    ).strip()


def trecho_limite():
    texto = ler_orientacao()
    marca = "## Limite do plano"
    if marca not in texto:
        return texto.strip()
    return texto.split(marca, 1)[1].strip()


def _markdown_flowables(texto, estilos):
    flowables = []
    for linha in texto.splitlines():
        linha = linha.strip()
        if not linha or linha in ("---", "***"):
            continue
        if linha.startswith("#"):
            nivel = len(linha) - len(linha.lstrip("#"))
            titulo = linha[nivel:].strip()
            if nivel == 1 and titulo.casefold() == "plano de voo":
                continue
            estilo = estilos["section"] if nivel <= 2 else estilos["subsection"]
            flowables.append(Paragraph(_html(titulo), estilo))
        elif linha.startswith(("- ", "* ")):
            flowables.append(
                Paragraph(f"<bullet>&bull;</bullet>{_html(linha[2:])}", estilos["bullet"])
            )
        elif re.fullmatch(r"\|?[\s|:-]+\|?", linha):
            continue
        else:
            texto_formatado = _html(linha)
            texto_formatado = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto_formatado)
            texto_formatado = re.sub(
                r"`([^`]+)`", r'<font name="Courier">\1</font>', texto_formatado
            )
            texto_formatado = re.sub(
                r"\[([^\]]+)\]\((https?://[^)]+)\)",
                r'<link href="\2" color="#0090F0">\1</link>',
                texto_formatado,
            )
            flowables.append(Paragraph(texto_formatado, estilos["body"]))
    return flowables


def _instante_utc(valor):
    if not isinstance(valor, str) or not valor.strip():
        return None
    texto = valor.strip()
    if texto.endswith("Z"):
        texto = texto[:-1] + "+00:00"
    try:
        instante = datetime.fromisoformat(texto)
    except ValueError:
        return None
    if instante.tzinfo is None:
        return None
    return instante.astimezone(timezone.utc)


def _hora_legivel(valor):
    instante = _instante_utc(valor)
    if instante is None:
        return "Indisponível"
    return instante.strftime("%d/%m/%Y %H:%M UTC")


def _data_br(valor):
    if isinstance(valor, str) and len(valor) >= 10 and valor[4] == "-":
        ano, mes, dia = valor[:10].split("-")
        return f"{dia}/{mes}/{ano}"
    return valor or "Indisponível"


def _agenda_por_ordem(plano):
    programacao = plano.resultado.get("programacao")
    agendas = programacao.get("trechos", []) if isinstance(programacao, dict) else []
    return {
        agenda.get("ordem"): agenda
        for agenda in agendas
        if isinstance(agenda, dict)
    }


def _nome_aero(aerodromos, icao):
    aero = aerodromos.get(icao)
    nome = getattr(aero, "nome", None) or "Nome indisponível"
    return f"{icao} — {nome}"


def _linhas_trecho(trecho, grandeza, agenda):
    linhas = [
        ("Distância", trecho.distancia_valor, trecho.distancia_unidade),
    ]
    if grandeza and grandeza.get("distancia_km") is not None:
        linhas.append(("Distância", grandeza["distancia_km"], "km"))
    linhas.extend(
        [
            ("Proa", trecho.proa_valor, trecho.proa_unidade),
            ("Tempo estimado", trecho.tempo_valor, trecho.tempo_unidade),
        ]
    )
    if grandeza and grandeza.get("velocidade_planejamento") is not None:
        linhas.append(
            (
                "Velocidade de planejamento",
                grandeza["velocidade_planejamento"],
                grandeza.get("velocidade_unidade") or "—",
            )
        )
    if grandeza and grandeza.get("velocidade_solo_kt") is not None:
        linhas.append(
            ("Velocidade em relação ao solo", grandeza["velocidade_solo_kt"], "kt")
        )
    if grandeza and grandeza.get("combustivel_voo") is not None:
        linhas.append(
            (
                "Combustível de voo",
                grandeza["combustivel_voo"],
                grandeza.get("unidade_combustivel") or "—",
            )
        )
    if grandeza and grandeza.get("reserva") is not None:
        linhas.append(
            (
                "Reserva de combustível",
                grandeza["reserva"],
                grandeza.get("unidade_combustivel") or "—",
            )
        )
    linhas.append(
        ("Combustível estimado", trecho.combustivel_valor, trecho.combustivel_unidade)
    )
    if grandeza and grandeza.get("peso_combustivel_kg") is not None:
        linhas.append(("Peso do combustível", grandeza["peso_combustivel_kg"], "kg"))
    if grandeza and grandeza.get("peso_aeronave_kg") is not None:
        linhas.append(("Peso da aeronave", grandeza["peso_aeronave_kg"], "kg"))
    linhas.append(("Vento", rotulo_lido(trecho.vento_estado), "—"))
    if trecho.vento_componente_kt is not None:
        sentido = "Vento de cauda" if trecho.vento_sentido == "cauda" else "Vento de proa"
        if trecho.vento_fonte:
            sentido = f"{sentido} ({trecho.vento_fonte})"
        linhas.append((sentido, trecho.vento_componente_kt, "kt"))
    if agenda and agenda.get("estado") == "disponivel":
        origem = (agenda.get("origem") or {}).get("por_do_sol")
        destino = (agenda.get("destino") or {}).get("por_do_sol")
        valor = (
            f"{_hora_legivel(origem)} ({trecho.origem_icao}); "
            f"{_hora_legivel(destino)} ({trecho.destino_icao})"
        )
        unidade = "UTC"
    else:
        valor = rotulo_lido(trecho.por_do_sol_estado)
        unidade = "—"
    linhas.append(("Pôr do sol", valor, unidade))
    return linhas


def _leitura_boletim(flowables, estilos, titulo, bruto, campos):
    from servidor.tempo import legenda_periodo_taf

    flowables.append(Paragraph(_html(titulo), estilos["subsection"]))
    if bruto:
        flowables.append(_paragrafo(bruto, estilos["small"]))
    if not campos:
        flowables.append(_paragrafo("Leitura estruturada indisponível.", estilos["body"]))
        return
    grupos = campos if isinstance(campos, list) and campos and "campos" in campos[0] else None
    if grupos is None:
        flowables.append(
            _tabela_grade(
                ("Dado", "Valor", "Unidade", "Explicação"),
                [
                    (
                        campo.get("nome", ""),
                        campo.get("valor", ""),
                        campo.get("unidade") or "—",
                        campo.get("explicacao") or "—",
                    )
                    for campo in campos
                ],
                estilos,
                [42 * mm, 40 * mm, 28 * mm, 66 * mm],
            )
        )
        return
    for grupo in grupos:
        periodo = grupo.get("periodo") or ""
        legenda = legenda_periodo_taf(periodo) if periodo else ""
        rotulo = grupo.get("tipo", "Grupo")
        if legenda:
            rotulo = f"{rotulo} — {legenda}"
        flowables.append(Paragraph(_html(rotulo), estilos["subsection"]))
        flowables.append(
            _tabela_grade(
                ("Dado", "Valor", "Unidade", "Explicação"),
                [
                    (
                        campo.get("nome", ""),
                        campo.get("valor", ""),
                        campo.get("unidade") or "—",
                        campo.get("explicacao") or "—",
                    )
                    for campo in grupo.get("campos") or []
                ],
                estilos,
                [42 * mm, 40 * mm, 28 * mm, 66 * mm],
            )
        )


def _conteudo_relatorio(plano, estilos, fontes_relatorio=None, aerodromos=None):
    from servidor.calculo import grandezas_do_trecho
    from servidor.modelos import Aeronave, Sessao
    from servidor.planos import coordenada_graus, hora_infografico, horario_rota
    from servidor.pdf_visuais import faixa_do_relatorio, mapa_do_relatorio, _paradas
    from servidor.planos_consulta import valores_do_plano
    from servidor.tempo import campos_metar, campos_taf

    aerodromos = aerodromos or {}
    agendas = _agenda_por_ordem(plano)
    aeronave = Sessao.get(Aeronave, plano.aeronave_id)
    particulares = valores_do_plano(plano)
    flowables = [
        _titulo_secao("Relatório de voo", estilos),
        *faixa_do_relatorio(
            plano, aeronave, aerodromos, agendas, estilos, hora_infografico
        ),
        _tabela_grade(
            ("Dado", "Valor"),
            [
                ("Rota", _rota_completa(plano).replace(" > ", " → ")),
                ("Aeronave", getattr(aeronave, "nome", None) or "Indisponível"),
                ("Partida", _partida_rotulo(plano.hora_partida)),
                ("Estado", rotulo_lido(plano.estado)),
            ]
            + ([("Motivo", plano.motivo)] if plano.motivo else [])
            + (
                [("Reabastecimento", plano.hipotese_reabastecimento)]
                if plano.hipotese_reabastecimento
                else []
            ),
            estilos,
            [40 * mm, 136 * mm],
        ),
    ]
    if plano.aviso:
        flowables.append(_paragrafo(plano.aviso, estilos["body"]))

    if plano.resultado.get("alertas"):
        flowables.append(_titulo_secao("Alertas", estilos))
        flowables.extend(
            Paragraph(f"<bullet>&bull;</bullet>{_html(alerta)}", estilos["bullet"])
            for alerta in plano.resultado["alertas"]
        )

    if plano.trechos:
        flowables.append(_titulo_secao("Rota completa", estilos))
        flowables.append(
            Paragraph(
                "Aeródromos na ordem da viagem, com chegada, partida e posição.",
                estilos["body"],
            )
        )
        linhas_rota = []
        for trecho in plano.trechos:
            agenda = agendas.get(trecho.ordem)
            if trecho.ordem == plano.trechos[0].ordem:
                saida = aerodromos.get(trecho.origem_icao)
                linhas_rota.append(
                    [
                        "1",
                        trecho.origem_icao,
                        "—",
                        horario_rota(agenda.get("etd") if agenda else None),
                        horario_rota(
                            (agenda.get("origem") or {}).get("por_do_sol") if agenda else None
                        ),
                        coordenada_graus(getattr(saida, "lat", None)),
                        coordenada_graus(getattr(saida, "lon", None)),
                        getattr(saida, "elev_m", None) if saida and saida.elev_m is not None else "Indisponível",
                    ]
                )
            chegada = aerodromos.get(trecho.destino_icao)
            proximo = next(
                (item for item in plano.trechos if item.ordem == trecho.ordem + 1),
                None,
            )
            agenda_saida = agendas.get(proximo.ordem) if proximo else None
            por_partida = (
                (agenda_saida.get("origem") or {}).get("por_do_sol") if agenda_saida else None
            )
            por_chegada = (agenda.get("destino") or {}).get("por_do_sol") if agenda else None
            linhas_rota.append(
                [
                    str(trecho.ordem + 1),
                    trecho.destino_icao,
                    horario_rota(agenda.get("eta") if agenda else None),
                    horario_rota(agenda_saida.get("etd") if agenda_saida else None)
                    if proximo
                    else "—",
                    horario_rota(por_partida or por_chegada),
                    coordenada_graus(getattr(chegada, "lat", None)),
                    coordenada_graus(getattr(chegada, "lon", None)),
                    getattr(chegada, "elev_m", None)
                    if chegada and chegada.elev_m is not None
                    else "Indisponível",
                ]
            )
        flowables.append(
            _tabela_grade(
                (
                    "Etapa",
                    "Aeródromo",
                    "Chegada",
                    "Partida",
                    "Pôr do sol",
                    "Latitude (°)",
                    "Longitude (°)",
                    "Elevação (m)",
                ),
                linhas_rota,
                estilos,
                [14 * mm, 24 * mm, 24 * mm, 24 * mm, 24 * mm, 24 * mm, 24 * mm, 18 * mm],
            )
        )
        flowables.append(Paragraph("Observações", estilos["subsection"]))
        if len(plano.trechos) > 1 and plano.hipotese_reabastecimento:
            flowables.append(
                _paragrafo(
                    "Reabastecimento previsto em cada escala, com intervalo de 1 hora "
                    "entre a chegada e a partida seguinte.",
                    estilos["body"],
                )
            )
        for agenda in agendas.values():
            pernoite = agenda.get("pernoite") if isinstance(agenda, dict) else None
            if pernoite:
                flowables.append(
                    _paragrafo(
                        f"Pernoite em {pernoite.get('icao', 'Indisponível')} em "
                        f"{_data_br(pernoite.get('data'))}. A partida fica no nascer "
                        "do sol do dia seguinte.",
                        estilos["body"],
                    )
                )
        flowables.append(
            _paragrafo(
                "Todos os tempos em UTC — Tempo Universal Coordenado.",
                estilos["body"],
            )
        )
        flowables.append(_titulo_secao("Mapa da rota", estilos))
        flowables.extend(
            mapa_do_relatorio(
                _paradas(plano, aerodromos, agendas, hora_infografico),
                estilos,
            )
        )

    linhas_resultado = plano.resultado.get("linhas", [])
    if linhas_resultado:
        flowables.append(_titulo_secao("Dados do plano", estilos))
        flowables.append(
            Paragraph(
                "Distância, tempo, combustível e peso usados neste plano.",
                estilos["body"],
            )
        )
        flowables.append(_tabela_resultados(linhas_resultado, estilos))

    for trecho in plano.trechos or []:
        agenda = agendas.get(trecho.ordem)
        grandeza = grandezas_do_trecho(trecho, aeronave, particulares)
        flowables.append(
            _titulo_secao(
                f"Trecho {trecho.ordem} — {trecho.origem_icao} → {trecho.destino_icao}",
                estilos,
            )
        )
        flowables.append(
            _paragrafo(
                f"Origem: {_nome_aero(aerodromos, trecho.origem_icao)}. "
                f"Horário estimado de partida: "
                f"{_hora_legivel(agenda.get('etd') if agenda else None)}.",
                estilos["body"],
            )
        )
        flowables.append(
            _paragrafo(
                f"Destino: {_nome_aero(aerodromos, trecho.destino_icao)}. "
                f"Horário estimado de chegada: "
                f"{_hora_legivel(agenda.get('eta') if agenda else None)}.",
                estilos["body"],
            )
        )
        flowables.append(
            _tabela_grade(
                ("Dado", "Valor", "Unidade"),
                _linhas_trecho(trecho, grandeza, agenda),
                estilos,
                [70 * mm, 70 * mm, 36 * mm],
            )
        )
        blocos = (plano.meteorologia or {}).get("aerodromos") or {}
        for papel, icao in (
            ("saída", trecho.origem_icao),
            ("chegada", trecho.destino_icao),
        ):
            bloco = blocos.get(icao) if isinstance(blocos, dict) else None
            metar = bloco.get("metar") if isinstance(bloco, dict) else None
            taf = bloco.get("taf") if isinstance(bloco, dict) else None
            rotulo = "Partida" if papel == "saída" else "Chegada"
            flowables.append(Paragraph(f"{rotulo} — {icao}", estilos["subsection"]))
            if isinstance(metar, dict) and metar.get("regional"):
                flowables.append(
                    _paragrafo(
                        "METAR regional: estação "
                        f"{metar.get('nome_estacao') or metar.get('icao')} "
                        f"({metar.get('icao')}), "
                        f"{metar.get('distancia_nm')} NM do aeródromo {icao}.",
                        estilos["body"],
                    )
                )
            if isinstance(metar, dict) and (metar.get("raw") or metar.get("estado")):
                _leitura_boletim(
                    flowables,
                    estilos,
                    f"METAR da {papel} — {icao}",
                    metar.get("raw") or "indisponível",
                    campos_metar(metar),
                )
            else:
                flowables.append(_paragrafo(f"METAR da {papel} indisponível.", estilos["body"]))
            if isinstance(taf, dict) and taf.get("raw"):
                _leitura_boletim(
                    flowables,
                    estilos,
                    f"TAF da {papel} — {icao}",
                    taf.get("raw"),
                    campos_taf(taf),
                )
            else:
                flowables.append(_paragrafo(f"TAF da {papel} indisponível.", estilos["body"]))

    vento = plano.vento or {}
    flowables.append(_titulo_secao("Vento da rota", estilos))
    if vento.get("estado") == "disponivel":
        texto_vento = (
            f"Vento: {vento.get('direcao_de_graus')} graus, de onde vem, "
            f"{vento.get('velocidade_kt')} {vento.get('unidade', 'kt')}"
        )
        if vento.get("efeito"):
            texto_vento += f" — {vento['efeito']}"
        texto_vento += "."
    else:
        texto_vento = "Vento de rota: indisponível."
    flowables.append(_paragrafo(texto_vento, estilos["body"]))
    flowables.append(
        _paragrafo("Este relatório não autoriza o voo.", estilos["body"])
    )

    if plano.resultado.get("proxy_sintetico") or plano.resultado.get("dados_sinteticos"):
        flowables.append(
            Paragraph("Aviso sobre dados didáticos", estilos["section"])
        )
        flowables.append(
            _paragrafo(
                "Cálculos e dados dos perfis sintéticos são exclusivamente didáticos: "
                "valores não validados, que não representam dados do modelo associado. "
                "Não substituem o manual da aeronave, o treinamento de voo nem a norma "
                "vigente; não são adequados para planejamento de voo real e não "
                "autorizam o voo.",
                estilos["body"],
            )
        )
    if fontes_relatorio:
        linhas_fontes = [
            {**linha, "estado": rotulo_lido(linha["estado"])}
            for linha in fontes_relatorio
        ]
        flowables.extend(
            (
                PageBreak(),
                Paragraph("Fontes do relatório", estilos["section"]),
                _tabela_fontes(linhas_fontes, estilos),
            )
        )
    return flowables


def gerar_pdf(plano, nome_piloto, aerodromos=None, fontes_relatorio=None):
    buffer = BytesIO()
    estilos = _estilos()
    conteudo = _conteudo_relatorio(
        plano,
        estilos,
        fontes_relatorio=fontes_relatorio,
        aerodromos=aerodromos,
    )
    _montar_documento(
        buffer,
        plano,
        nome_piloto,
        conteudo,
        estilos,
        rotulo_lido,
    )
    return buffer.getvalue()
