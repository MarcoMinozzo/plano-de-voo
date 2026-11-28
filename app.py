import os
from datetime import datetime, timedelta, timezone
from math import isfinite
from urllib.parse import urlparse

from flask import Flask, flash, g, jsonify, redirect, render_template, request, session, url_for

from servidor import carregar_env
from servidor import openaip
from servidor import rainviewer
from servidor import tempo
from servidor.ambiente import resolver_ambiente
from servidor.imagens_aeronave import imagem_da_aeronave
from servidor.auth import (
    MENSAGEM_RECUSA,
    MENSAGEM_NOME_EXIBICAO,
    alterar_senha,
    cadastrar,
    entrar,
    normalizar_nome_exibicao,
    sessao_expirada,
)
from servidor.catalogo import (
    aerodromos_oferecidos,
    correspondencias,
    lugares_da_tela,
    modelos_visiveis,
    perfis_sinteticos_visiveis,
    procedencia_aeronave,
)
from servidor.modelos import Aeronave, Aerodromo, Sessao, agora, configurar
from servidor.planos_consulta import construir_fontes_relatorio, linha_fonte_relatorio
from servidor.pdf_plano import (
    gerar_pdf,
    ler_orientacao,
    nome_relatorio,
    rotulo_lido,
)
from servidor.tempo import campos_metar, campos_taf, legenda_periodo_taf, linhas_boletim
from servidor.planos import (
    apagar,
    completar_programacao_solar,
    do_piloto,
    coordenada_graus,
    hora_infografico,
    hora_ja_passou,
    horario_rota,
    listar,
    marcar_item,
    montar,
    para_json,
    recalcular,
    valores_do_plano,
)


def _visto(valor):
    if not valor:
        return None
    hora = datetime.fromisoformat(valor)
    if hora.tzinfo is None:
        hora = hora.replace(tzinfo=timezone.utc)
    return hora


def data_br(valor):
    try:
        return datetime.strptime(valor, "%Y-%m-%d").strftime("%d/%m/%Y")
    except (TypeError, ValueError):
        return "Data indisponível"


def hora_utc_legivel(valor, com_fuso=True):
    if not isinstance(valor, str) or not valor.strip():
        return "Indisponível"
    texto = valor.strip()
    if texto.endswith("Z"):
        texto = texto[:-1] + "+00:00"
    try:
        instante = datetime.fromisoformat(texto)
    except ValueError:
        return "Indisponível"
    if instante.tzinfo is None:
        return "Indisponível"
    texto = instante.astimezone(timezone.utc).strftime("%d/%m/%Y %H:%M")
    return f"{texto} UTC" if com_fuso else texto


def _boletins_por_aerodromo(plano, meteorologia_atual):
    meteorologia = meteorologia_atual if isinstance(meteorologia_atual, dict) else {}
    aerodromos = meteorologia.get("aerodromos")
    if not isinstance(aerodromos, dict):
        aerodromos = {}
    if not aerodromos:
        for icao, chave in (
            (plano.origem_icao, "origem"),
            (plano.destino_icao, "destino"),
        ):
            bloco = meteorologia.get(chave)
            if isinstance(bloco, dict):
                aerodromos[icao] = bloco

    boletins = {}
    for trecho in plano.trechos:
        for icao in (trecho.origem_icao, trecho.destino_icao):
            if icao in boletins:
                continue
            bloco = aerodromos.get(icao)
            if not isinstance(bloco, dict):
                bloco = {"estado": "indisponivel"}
            metar = bloco.get("metar") if isinstance(bloco.get("metar"), dict) else None
            taf = bloco.get("taf") if isinstance(bloco.get("taf"), dict) else None
            boletins[icao] = {
                "estado": bloco.get("estado", "indisponivel"),
                "fonte": bloco.get("fonte") or (metar or {}).get("fonte") or "Aviation Weather Center",
                "metar": metar,
                "campos_metar": campos_metar(metar),
                "taf": taf or {"estado": "indisponivel"},
                "campos_taf": campos_taf(taf),
            }
    return boletins


def criar_app():
    carregar_env()
    ambiente = resolver_ambiente()
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "dev")
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = os.environ.get("COOKIE_SECURE", "0") == "1"
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=8)
    app.add_template_global(rotulo_lido)
    app.add_template_global(data_br)
    app.add_template_global(hora_utc_legivel)
    app.add_template_global(legenda_periodo_taf)
    app.add_template_global(horario_rota)
    app.add_template_global(hora_infografico)
    app.add_template_global(coordenada_graus)
    app.add_template_global(imagem_da_aeronave)
    configurar(ambiente.database_url)

    @app.before_request
    def abrir_sessao_db():
        g.db = Sessao()

    @app.teardown_request
    def fechar_sessao_db(_exc):
        Sessao.remove()

    @app.route("/favicon.ico")
    def favicon():
        return app.send_static_file("casca/favicon.ico")

    def quer_json():
        return request.is_json or request.headers.get("Accept") == "application/json"

    def piloto_logado():
        from servidor.modelos import Piloto

        piloto_id = session.get("piloto_id")
        visto = _visto(session.get("visto_em"))
        if not piloto_id or sessao_expirada(visto):
            session.clear()
            return None
        piloto = g.db.get(Piloto, piloto_id)
        if piloto is None:
            session.clear()
            return None
        session["visto_em"] = agora().isoformat()
        session.permanent = True
        return piloto

    @app.context_processor
    def injetar_piloto_menu():
        return {"piloto_menu": piloto_logado()}

    def entrar_sessao(piloto):
        session.clear()
        session.permanent = True
        session["piloto_id"] = piloto.id
        session["visto_em"] = agora().isoformat()

    def catalogo_da_tela():
        estado_aero, aerodromos = lugares_da_tela(g.db)
        estado_modelos, modelos = modelos_visiveis(g.db)
        perfis_sinteticos = perfis_sinteticos_visiveis(g.db)
        return (
            estado_aero,
            aerodromos,
            estado_modelos,
            modelos,
            perfis_sinteticos,
        )

    def informado_de(dados):
        if not dados:
            return {}
        bruto = dados.to_dict(flat=True) if hasattr(dados, "to_dict") else dict(dados)
        chaves = (
            "aeronave_id",
            "origem",
            "destino",
            "hora_partida",
            "numero_passageiros",
            "peso_pessoas_kg",
            "peso_bagagem_kg",
            "confirmar_hora",
        )
        saida = {}
        for chave in chaves:
            valor = bruto.get(chave, "")
            saida[chave] = "" if valor is None else valor
        return saida

    def tela_plano(mensagem, dados, action=None):
        (
            estado_aero,
            aerodromos,
            estado_modelos,
            modelos,
            perfis_sinteticos,
        ) = catalogo_da_tela()
        informado = informado_de(dados)
        return render_template(
            "plano_novo.html",
            mensagem=mensagem,
            aeronaves=modelos + perfis_sinteticos,
            modelos_fatuais=modelos,
            perfis_sinteticos=perfis_sinteticos,
            aeronave_padrao_id=(
                modelos[0].id
                if modelos
                else perfis_sinteticos[0].id
                if perfis_sinteticos
                else None
            ),
            modelos_estado=estado_modelos,
            aerodromos=aerodromos,
            catalogo_estado=estado_aero,
            orientacao=ler_orientacao(),
            informado=informado,
            mostrar_confirmacao=hora_ja_passou(informado.get("hora_partida")),
            action=action,
        )

    def exigir():
        piloto = piloto_logado()
        if piloto is None:
            if quer_json():
                return None, (jsonify({"mensagem": MENSAGEM_RECUSA}), 401)
            return None, redirect(url_for("entrar_pagina"))
        return piloto, None

    @app.get("/")
    def inicio():
        if piloto_logado():
            return redirect(url_for("painel"))
        return redirect(url_for("entrar_pagina"))

    @app.route("/cadastro", methods=["GET", "POST"])
    def cadastro():
        if request.method == "GET":
            return render_template("cadastro.html")
        dados = request.get_json(silent=True) or request.form
        piloto, erro = cadastrar(
            g.db,
            dados.get("identificacao"),
            dados.get("senha"),
            dados.get("nome_exibicao"),
        )
        if erro:
            if quer_json():
                return jsonify({"mensagem": erro}), 400
            return render_template("cadastro.html", mensagem=erro), 400
        entrar_sessao(piloto)
        if quer_json():
            return jsonify({"ok": True, "id": piloto.id})
        return redirect(url_for("painel"))

    @app.route("/perfil", methods=["GET", "POST"])
    def perfil():
        piloto, resposta = exigir()
        if piloto is None:
            return resposta
        if request.method == "GET":
            return render_template("perfil.html", piloto=piloto)

        dados = request.get_json(silent=True) or request.form
        if dados.get("acao") == "senha" or "senha_nova" in dados:
            erro = alterar_senha(
                g.db,
                piloto,
                dados.get("senha_atual"),
                dados.get("senha_nova"),
                dados.get("senha_confirmacao"),
            )
            if erro:
                if quer_json():
                    return jsonify({"mensagem": erro}), 400
                return render_template("perfil.html", piloto=piloto, mensagem=erro), 400
            if quer_json():
                return jsonify({"ok": True})
            flash("Senha alterada.", "sucesso")
            return redirect(url_for("painel"))

        nome_exibicao = normalizar_nome_exibicao(dados.get("nome_exibicao"))
        if nome_exibicao is None:
            if quer_json():
                return jsonify({"mensagem": MENSAGEM_NOME_EXIBICAO}), 400
            return (
                render_template(
                    "perfil.html",
                    piloto=piloto,
                    mensagem=MENSAGEM_NOME_EXIBICAO,
                ),
                400,
            )

        piloto.nome_exibicao = nome_exibicao
        g.db.commit()
        if quer_json():
            return jsonify({"ok": True, "nome_exibicao": piloto.nome_exibicao})
        flash("Nome de exibição salvo.", "sucesso")
        return redirect(url_for("painel"))

    @app.route("/entrar", methods=["GET", "POST"])
    def entrar_pagina():
        if request.method == "GET":
            return render_template("entrar.html")
        dados = request.get_json(silent=True) or request.form
        piloto, erro = entrar(g.db, dados.get("identificacao"), dados.get("senha"))
        if erro:
            if quer_json():
                return jsonify({"mensagem": erro}), 401
            return render_template("entrar.html", mensagem=erro), 401
        entrar_sessao(piloto)
        if quer_json():
            return jsonify({"ok": True, "id": piloto.id})
        return redirect(url_for("painel"))

    @app.post("/sair")
    def sair():
        session.clear()
        if quer_json():
            return jsonify({"ok": True})
        return redirect(url_for("entrar_pagina"))

    @app.get("/painel")
    def painel():
        piloto, resposta = exigir()
        if piloto is None:
            return resposta
        planos = listar(g.db, piloto.id)
        if quer_json():
            return jsonify([
                {
                    "id": p.id,
                    "origem": p.origem_icao,
                    "destino": p.destino_icao,
                    "hora_partida": p.hora_partida.isoformat(),
                    "estado": p.estado,
                }
                for p in planos
            ])
        return render_template("painel.html", planos=planos, piloto=piloto)

    @app.route("/planos", methods=["GET", "POST"])
    def planos():
        piloto, resposta = exigir()
        if piloto is None:
            return resposta
        if request.method == "GET":
            return redirect(url_for("painel"))
        dados = request.get_json(silent=True) or request.form
        plano, erro = montar(g.db, piloto, dados)
        if erro:
            if quer_json():
                return jsonify({"mensagem": erro}), 400
            return tela_plano(erro, dados), 400
        if quer_json():
            return jsonify(para_json(plano)), 201
        return redirect(url_for("ver_plano", plano_id=plano.id))

    @app.get("/planos/novo")
    def novo_plano():
        piloto, resposta = exigir()
        if piloto is None:
            return resposta
        return tela_plano(None, {})

    @app.route("/planos/<int:plano_id>/alterar", methods=["GET", "POST"])
    def alterar_plano(plano_id):
        piloto, resposta = exigir()
        if piloto is None:
            return resposta
        plano = do_piloto(g.db, piloto.id, plano_id)
        if plano is None:
            if quer_json():
                return jsonify({"mensagem": MENSAGEM_RECUSA}), 404
            return render_template("recusa.html"), 404
        action = url_for("alterar_plano", plano_id=plano.id)
        if request.method == "GET":
            return tela_plano(None, valores_do_plano(plano), action)
        dados = request.get_json(silent=True) or request.form
        atualizado, erro = montar(g.db, piloto, dados, plano)
        if erro:
            if quer_json():
                return jsonify({"mensagem": erro}), 400
            return tela_plano(erro, dados, action), 400
        if quer_json():
            return jsonify(para_json(atualizado))
        return redirect(url_for("ver_plano", plano_id=atualizado.id))

    @app.post("/planos/<int:plano_id>/atualizar")
    def atualizar_plano(plano_id):
        piloto, resposta = exigir()
        if piloto is None:
            return resposta
        plano = do_piloto(g.db, piloto.id, plano_id)
        if plano is None:
            if quer_json():
                return jsonify({"mensagem": MENSAGEM_RECUSA}), 404
            return render_template("recusa.html"), 404
        atualizado, erro = recalcular(g.db, piloto, plano)
        if erro:
            if quer_json():
                return jsonify({"mensagem": erro}), 400
            flash(erro, "erro")
            return redirect(url_for("ver_plano", plano_id=plano.id))
        if quer_json():
            return jsonify(para_json(atualizado))
        return redirect(url_for("ver_plano", plano_id=atualizado.id))

    @app.route("/planos/<int:plano_id>", methods=["GET", "PUT"])
    def ver_plano(plano_id):
        piloto, resposta = exigir()
        if piloto is None:
            return resposta
        if request.method == "PUT":
            plano = do_piloto(g.db, piloto.id, plano_id)
            if plano is None:
                return jsonify({"mensagem": MENSAGEM_RECUSA}), 404
            dados = request.get_json(silent=True) or request.form
            plano, erro = montar(
                g.db,
                piloto,
                dados,
                plano,
            )
            if erro:
                return jsonify({"mensagem": erro}), 400
            if quer_json():
                return jsonify(para_json(plano))
            return redirect(url_for("ver_plano", plano_id=plano.id))
        plano = do_piloto(g.db, piloto.id, plano_id)
        if plano is None:
            if quer_json():
                return jsonify({"mensagem": MENSAGEM_RECUSA}), 404
            return render_template("recusa.html"), 404
        completar_programacao_solar(g.db, plano)
        aeronave = g.db.get(Aeronave, plano.aeronave_id)
        pontos_por_trecho = []
        aerodromos_rota = {}
        for trecho in plano.trechos:
            for icao in (trecho.origem_icao, trecho.destino_icao):
                if icao not in aerodromos_rota:
                    aerodromos_rota[icao] = g.db.get(Aerodromo, icao)
            saida = aerodromos_rota[trecho.origem_icao]
            chegada = aerodromos_rota[trecho.destino_icao]
            if saida is None or chegada is None:
                pontos_por_trecho.append(
                    {
                        "ordem": trecho.ordem,
                        "origem": trecho.origem_icao,
                        "destino": trecho.destino_icao,
                        "origem_nome": saida.nome if saida is not None else None,
                        "destino_nome": chegada.nome if chegada is not None else None,
                        "pontos": [],
                    }
                )
                continue
            pontos_do_trecho = [[saida.lat, saida.lon], [chegada.lat, chegada.lon]]
            pontos_por_trecho.append(
                {
                    "ordem": trecho.ordem,
                    "origem": trecho.origem_icao,
                    "destino": trecho.destino_icao,
                    "origem_nome": saida.nome,
                    "destino_nome": chegada.nome,
                    "pontos": pontos_do_trecho,
                }
            )
        aerodromos_rota.setdefault(
            plano.origem_icao,
            g.db.get(Aerodromo, plano.origem_icao),
        )
        aerodromos_rota.setdefault(
            plano.destino_icao,
            g.db.get(Aerodromo, plano.destino_icao),
        )
        origem = aerodromos_rota.get(plano.origem_icao)
        destino = aerodromos_rota.get(plano.destino_icao)
        if origem is not None and destino is not None:
            meteorologia_atual = tempo.meteorologia_rota(
                origem,
                destino,
                aerodromos=[
                    aerodromo
                    for aerodromo in aerodromos_rota.values()
                    if aerodromo is not None
                ],
            )
        else:
            meteorologia_atual = {
                "estado": "indisponivel",
                "origem": {"estado": "indisponivel"},
                "destino": {"estado": "indisponivel"},
                "aerodromos": {},
            }
        radar_atual = {"estado": "indisponivel"}
        if quer_json():
            dados = para_json(plano)
            dados["meteorologia"] = meteorologia_atual
            dados["radar"] = radar_atual
            return jsonify(dados)
        from servidor.calculo import grandezas_do_trecho

        grandezas_por_trecho = {
            trecho.ordem: grandezas_do_trecho(
                trecho, aeronave, plano.dados_particulares
            )
            for trecho in plano.trechos
        }
        return render_template(
            "plano.html",
            plano=plano,
            aeronave=aeronave,
            grandezas_por_trecho=grandezas_por_trecho,
            aerodromos_rota=aerodromos_rota,
            pontos_por_trecho=pontos_por_trecho,
            boletins=linhas_boletim(meteorologia_atual),
            boletins_por_aerodromo=_boletins_por_aerodromo(plano, meteorologia_atual),
            meteorologia=meteorologia_atual,
            radar=radar_atual,
            fontes_relatorio=construir_fontes_relatorio(
                plano, aerodromos_rota, meteorologia_atual
            ),
        )

    @app.get("/planos/<int:plano_id>/camadas/radar")
    def camada_radar(plano_id):
        piloto, resposta = exigir()
        if piloto is None:
            return resposta
        exclusoes = request.args.getlist("exclude")
        if len(exclusoes) > 1 or (
            exclusoes and exclusoes[0] not in {"REDEMET", "RainViewer"}
        ):
            return jsonify({"estado": "indisponivel"}), 400
        excluir = exclusoes[0] if exclusoes else None
        plano = do_piloto(g.db, piloto.id, plano_id)
        if plano is None:
            return jsonify({"mensagem": MENSAGEM_RECUSA}), 404

        origem = g.db.get(Aerodromo, plano.origem_icao)
        destino = g.db.get(Aerodromo, plano.destino_icao)
        if excluir != "RainViewer":
            try:
                frame = rainviewer.buscar_frame()
            except rainviewer.RainViewerIndisponivel:
                frame = None
            if (
                isinstance(frame, dict)
                and isinstance(frame.get("frame"), str)
                and isinstance(frame.get("hora"), int)
                and not isinstance(frame.get("hora"), bool)
                and frame["hora"] > 0
                and isinstance(frame.get("max_zoom"), int)
            ):
                radar_url = url_for(
                    "tile_rainviewer",
                    plano_id=plano_id,
                    frame=frame["frame"],
                    z=0,
                    x=0,
                    y=0,
                ).replace("/0/0/0.png", "/{z}/{x}/{y}.png")
                cobertura_url = url_for(
                    "cobertura_rainviewer",
                    plano_id=plano_id,
                    z=0,
                    x=0,
                    y=0,
                ).replace("/0/0/0.png", "/{z}/{x}/{y}.png")
                return jsonify(
                    {
                        "estado": "disponivel",
                        "provedor": "RainViewer",
                        "fonte": "RainViewer — radar não oficial",
                        "hora_frame": datetime.fromtimestamp(
                            frame["hora"], timezone.utc
                        ).isoformat(),
                        "max_zoom": frame["max_zoom"],
                        "radar_url": radar_url,
                        "cobertura_url": cobertura_url,
                        "atribuicao": {
                            "texto": "Weather data by RainViewer",
                            "url": "https://www.rainviewer.com/",
                        },
                        "aviso_cobertura": (
                            "A máscara de cobertura pode estar desatualizada. "
                            "Área sem cobertura não significa ausência de chuva."
                        ),
                        "fonte_relatorio": linha_fonte_relatorio(
                            "Radar de chuva",
                            "RainViewer — radar não oficial",
                            "RainViewer",
                            publicador="RainViewer",
                            referencia="https://www.rainviewer.com/",
                            data=datetime.fromtimestamp(
                                frame["hora"], timezone.utc
                            ).isoformat(),
                            aplicabilidade="mapa do plano",
                        ),
                    }
                )

        if excluir != "REDEMET" and origem is not None and destino is not None:
            radar = tempo.radar(origem, destino)
            url = radar.get("url") if isinstance(radar, dict) else None
            parsed_url = urlparse(url or "")
            hora = radar.get("hora") if isinstance(radar, dict) else None
            limites = (
                radar.get("lat_min"),
                radar.get("lat_max"),
                radar.get("lon_min"),
                radar.get("lon_max"),
            ) if isinstance(radar, dict) else ()
            limites_validos = (
                len(limites) == 4
                and all(
                    isinstance(valor, (int, float))
                    and not isinstance(valor, bool)
                    and isfinite(valor)
                    for valor in limites
                )
                and limites[0] < limites[1]
                and limites[2] < limites[3]
            )
            if (
                isinstance(radar, dict)
                and radar.get("estado") == "disponivel"
                and parsed_url.scheme == "https"
                and parsed_url.netloc
                and isinstance(hora, str)
                and hora.strip()
                and limites_validos
            ):
                return jsonify(
                    {
                        "estado": "disponivel",
                        "provedor": "REDEMET",
                        "fonte": radar.get("fonte") or "REDEMET MaxCappi",
                        "hora_frame": hora,
                        "radar_url": url,
                        "bounds": {
                            "lat_min": limites[0],
                            "lat_max": limites[1],
                            "lon_min": limites[2],
                            "lon_max": limites[3],
                        },
                        "atribuicao": None,
                        "aviso_cobertura": None,
                        "fonte_relatorio": linha_fonte_relatorio(
                            "Radar de chuva",
                            radar.get("fonte") or "REDEMET MaxCappi",
                            radar.get("fonte") or "REDEMET MaxCappi",
                            publicador="REDEMET",
                            referencia=url,
                            data=hora,
                            aplicabilidade="mapa do plano",
                        ),
                    }
                )

        return jsonify({"estado": "indisponivel"})

    @app.get("/planos/<int:plano_id>/camadas/satelite")
    def camada_satelite(plano_id):
        piloto, resposta = exigir()
        if piloto is None:
            return resposta
        if do_piloto(g.db, piloto.id, plano_id) is None:
            return jsonify({"mensagem": MENSAGEM_RECUSA}), 404

        quadro = tempo.satelite()
        if not isinstance(quadro, dict) or quadro.get("estado") != "disponivel":
            return jsonify({"estado": "indisponivel"})

        url = quadro.get("url")
        hora = quadro.get("hora")
        parsed_url = urlparse(url) if isinstance(url, str) else None
        limites = (
            quadro.get("lat_min"),
            quadro.get("lat_max"),
            quadro.get("lon_min"),
            quadro.get("lon_max"),
        )
        limites_validos = (
            all(
                isinstance(valor, (int, float))
                and not isinstance(valor, bool)
                and isfinite(valor)
                for valor in limites
            )
            and -90 <= limites[0] < limites[1] <= 90
            and -180 <= limites[2] < limites[3] <= 180
        )
        if (
            parsed_url is None
            or parsed_url.scheme != "https"
            or parsed_url.netloc != "estatico-redemet.decea.mil.br"
            or not parsed_url.path.lower().endswith(".png")
            or parsed_url.query
            or parsed_url.fragment
            or not isinstance(hora, str)
            or not hora.strip()
            or not limites_validos
        ):
            return jsonify({"estado": "indisponivel"})

        return jsonify(
            {
                "estado": "disponivel",
                "provedor": "REDEMET",
                "fonte": quadro.get("fonte") or "REDEMET Satélite realçada",
                "hora_frame": hora,
                "imagem_url": url,
                "bounds": {
                    "lat_min": limites[0],
                    "lat_max": limites[1],
                    "lon_min": limites[2],
                    "lon_max": limites[3],
                },
            }
        )

    @app.get("/planos/<int:plano_id>/camadas/openaip/<z>/<x>/<y>.png")
    def tile_openaip(plano_id, z, x, y):
        piloto, resposta = exigir()
        if piloto is None:
            return resposta
        if do_piloto(g.db, piloto.id, plano_id) is None:
            return jsonify({"mensagem": MENSAGEM_RECUSA}), 404
        try:
            coordenadas = tuple(int(valor) for valor in (z, x, y))
            conteudo, cache_control = openaip.buscar_tile(*coordenadas)
        except ValueError:
            return jsonify({"mensagem": "Coordenadas de tile inválidas."}), 400
        except openaip.TileIndisponivel:
            return jsonify({"mensagem": "Camada OpenAIP indisponível."}), 503

        resposta = app.response_class(conteudo, mimetype="image/png")
        resposta.headers["X-Content-Type-Options"] = "nosniff"
        if cache_control:
            resposta.headers["Cache-Control"] = cache_control
        return resposta

    @app.get("/planos/<int:plano_id>/camadas/rainviewer")
    def camada_rainviewer(plano_id):
        piloto, resposta = exigir()
        if piloto is None:
            return resposta
        if do_piloto(g.db, piloto.id, plano_id) is None:
            return jsonify({"mensagem": MENSAGEM_RECUSA}), 404
        try:
            frame = rainviewer.buscar_frame()
        except rainviewer.RainViewerIndisponivel:
            return jsonify(
                {
                    "estado": "indisponivel",
                    "motivo": "Camada RainViewer indisponível.",
                }
            ), 503

        radar_url = url_for(
            "tile_rainviewer",
            plano_id=plano_id,
            frame=frame["frame"],
            z=0,
            x=0,
            y=0,
        ).replace("/0/0/0.png", "/{z}/{x}/{y}.png")
        cobertura_url = url_for(
            "cobertura_rainviewer",
            plano_id=plano_id,
            z=0,
            x=0,
            y=0,
        ).replace("/0/0/0.png", "/{z}/{x}/{y}.png")
        return jsonify(
            {
                "estado": "disponivel",
                "fonte": "RainViewer — radar não oficial",
                "atribuicao": {
                    "texto": "Weather data by RainViewer",
                    "url": "https://www.rainviewer.com/",
                },
                "hora_frame": frame["hora"],
                "max_zoom": frame["max_zoom"],
                "radar_url": radar_url,
                "cobertura_url": cobertura_url,
            }
        )

    @app.get(
        "/planos/<int:plano_id>/camadas/rainviewer/radar/<frame>/<z>/<x>/<y>.png"
    )
    def tile_rainviewer(plano_id, frame, z, x, y):
        piloto, resposta = exigir()
        if piloto is None:
            return resposta
        if do_piloto(g.db, piloto.id, plano_id) is None:
            return jsonify({"mensagem": MENSAGEM_RECUSA}), 404
        try:
            coordenadas = tuple(int(valor) for valor in (z, x, y))
            conteudo, cache_control = rainviewer.buscar_tile(frame, *coordenadas)
        except ValueError:
            return jsonify({"mensagem": "Coordenadas de tile inválidas."}), 400
        except rainviewer.RainViewerIndisponivel:
            return jsonify({"mensagem": "Tile RainViewer indisponível."}), 503

        resposta = app.response_class(conteudo, mimetype="image/png")
        resposta.headers["X-Content-Type-Options"] = "nosniff"
        if cache_control:
            resposta.headers["Cache-Control"] = cache_control
        return resposta

    @app.get(
        "/planos/<int:plano_id>/camadas/rainviewer/cobertura/<z>/<x>/<y>.png"
    )
    def cobertura_rainviewer(plano_id, z, x, y):
        piloto, resposta = exigir()
        if piloto is None:
            return resposta
        if do_piloto(g.db, piloto.id, plano_id) is None:
            return jsonify({"mensagem": MENSAGEM_RECUSA}), 404
        try:
            coordenadas = tuple(int(valor) for valor in (z, x, y))
            conteudo, cache_control = rainviewer.buscar_mascara(*coordenadas)
        except ValueError:
            return jsonify({"mensagem": "Coordenadas de tile inválidas."}), 400
        except rainviewer.RainViewerIndisponivel:
            return jsonify({"mensagem": "Cobertura RainViewer indisponível."}), 503

        resposta = app.response_class(conteudo, mimetype="image/png")
        resposta.headers["X-Content-Type-Options"] = "nosniff"
        if cache_control:
            resposta.headers["Cache-Control"] = cache_control
        return resposta

    @app.post("/planos/<int:plano_id>/apagar")
    def apagar_plano_formulario(plano_id):
        piloto, resposta = exigir()
        if piloto is None:
            return resposta
        confirmar = request.form.get("confirmar") in ("on", "true", "1")
        _ok, motivo = apagar(g.db, piloto, plano_id, confirmar)
        if motivo == "ausente":
            return render_template("recusa.html"), 404
        return redirect(url_for("painel"))

    @app.delete("/planos/<int:plano_id>")
    def apagar_plano(plano_id):
        piloto, resposta = exigir()
        if piloto is None:
            return resposta
        dados = request.get_json(silent=True) or request.form
        confirmar = dados.get("confirmar") in (True, "true", "1", "on")
        ok, motivo = apagar(g.db, piloto, plano_id, confirmar)
        if motivo == "ausente":
            return jsonify({"mensagem": MENSAGEM_RECUSA}), 404
        if motivo == "sem_confirmacao":
            return jsonify({"mensagem": "Confirme a exclusão."}), 400
        return jsonify({"ok": True})

    @app.post("/planos/<int:plano_id>/checklist/<int:item_id>")
    def checklist(plano_id, item_id):
        piloto, resposta = exigir()
        if piloto is None:
            return resposta
        dados = request.get_json(silent=True) or request.form
        marcado = dados.get("marcado") in (True, "true", "1", "on")
        item = marcar_item(g.db, piloto, plano_id, item_id, marcado)
        if item is None:
            return jsonify({"mensagem": MENSAGEM_RECUSA}), 404
        if quer_json():
            return jsonify({"id": item.id, "marcado": item.marcado})
        return redirect(url_for("ver_plano", plano_id=plano_id))

    @app.get("/planos/<int:plano_id>/pdf")
    def pdf(plano_id):
        piloto, resposta = exigir()
        if piloto is None:
            return resposta
        plano = do_piloto(g.db, piloto.id, plano_id)
        if plano is None:
            return jsonify({"mensagem": MENSAGEM_RECUSA}), 404
        completar_programacao_solar(g.db, plano)
        aerodromos_rota = {
            icao: g.db.get(Aerodromo, icao)
            for trecho in plano.trechos
            for icao in (trecho.origem_icao, trecho.destino_icao)
        }
        fontes_relatorio = construir_fontes_relatorio(
            plano, aerodromos_rota, plano.meteorologia
        )
        nome = nome_relatorio(plano)
        return (
            gerar_pdf(
                plano,
                piloto.nome_exibicao,
                aerodromos_rota,
                fontes_relatorio,
            ),
            200,
            {
                "Content-Type": "application/pdf",
                "Content-Disposition": f'inline; filename="{nome}.pdf"',
            },
        )

    @app.get("/aerodromos")
    def aerodromos():
        piloto, resposta = exigir()
        if piloto is None:
            return resposta
        estado, lista = aerodromos_oferecidos(g.db)
        if request.args.get("q") is not None:
            estado, lista = correspondencias(g.db, request.args.get("q"))
        return jsonify(
            {
                "estado": estado,
                "aerodromos": [
                    {"identificador": aero.icao, "nome": aero.nome, "fonte": aero.fonte}
                    for aero in lista
                ],
            }
        )

    @app.get("/aeronaves")
    def aeronaves():
        piloto, resposta = exigir()
        if piloto is None:
            return resposta
        estado, lista = modelos_visiveis(g.db)
        perfis = perfis_sinteticos_visiveis(g.db)
        modelos = []
        for aeronave in lista:
            item = {
                "id": aeronave.id,
                "nome": aeronave.nome,
                "frota": aeronave.frota,
                "manual_estado": aeronave.manual_estado,
            }
            item["fonte_manual"] = aeronave.fonte_manual
            item["dados_sinteticos"] = aeronave.dados_sinteticos
            item["procedencia"] = procedencia_aeronave(g.db, aeronave)
            item["estimativa_didatica"] = any(
                fonte and fonte["estimativa_didatica"]
                for fonte in item["procedencia"].values()
            )
            modelos.append(item)
        corpo = {
            "estado": estado,
            "modelos": modelos,
            "perfis_sinteticos": [
                {
                    "id": aeronave.id,
                    "nome": aeronave.nome,
                    "manual_estado": aeronave.manual_estado,
                    "dados_sinteticos": True,
                    "rotulo": (
                        "perfil sintético didático — valores não validados; "
                        "não representam dados do modelo associado"
                    ),
                    "modelo_alvo": aeronave.nome.partition(" — ")[2],
                    "procedencia": procedencia_aeronave(g.db, aeronave),
                    "estimativa_didatica": False,
                }
                for aeronave in perfis
            ],
        }
        if estado == "indisponivel":
            corpo["observacao"] = (
                "O registro nacional está indisponível. A seleção está vazia; a lista local não é usada como substituta."
            )
        return jsonify(corpo)

    return app


if __name__ == "__main__":
    criar_app().run(host="127.0.0.1", port=5000)
