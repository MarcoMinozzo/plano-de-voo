import os
from datetime import datetime, timedelta, timezone

from flask import Flask, g, jsonify, redirect, render_template, request, session, url_for

from servidor import carregar_env
from servidor.auth import (
    MENSAGEM_RECUSA,
    cadastrar,
    entrar,
    sessao_expirada,
)
from servidor.modelos import Aeronave, Aerodromo, Sessao, agora, configurar
from servidor.pdf_plano import gerar_pdf, ler_orientacao
from servidor.planos import apagar, do_piloto, listar, marcar_item, montar, para_json


def _visto(valor):
    if not valor:
        return None
    hora = datetime.fromisoformat(valor)
    if hora.tzinfo is None:
        hora = hora.replace(tzinfo=timezone.utc)
    return hora


def criar_app():
    carregar_env()
    app = Flask(__name__)
    app.secret_key = os.environ.get("SECRET_KEY", "dev")
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = os.environ.get("COOKIE_SECURE", "0") == "1"
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(hours=8)
    configurar(os.environ["DATABASE_URL"])

    @app.before_request
    def abrir_sessao_db():
        g.db = Sessao()

    @app.teardown_request
    def fechar_sessao_db(_exc):
        Sessao.remove()

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

    def entrar_sessao(piloto):
        session.clear()
        session.permanent = True
        session["piloto_id"] = piloto.id
        session["visto_em"] = agora().isoformat()

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
        piloto, erro = cadastrar(g.db, dados.get("identificacao"), dados.get("senha"))
        if erro:
            if quer_json():
                return jsonify({"mensagem": erro}), 400
            return render_template("cadastro.html", mensagem=erro), 400
        entrar_sessao(piloto)
        if quer_json():
            return jsonify({"ok": True, "id": piloto.id})
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
            aeronaves = g.db.query(Aeronave).order_by(Aeronave.nome).all()
            if quer_json():
                return jsonify({"mensagem": erro}), 400
            return render_template("plano_novo.html", mensagem=erro, aeronaves=aeronaves, orientacao=ler_orientacao()), 400
        if quer_json():
            return jsonify(para_json(plano)), 201
        return redirect(url_for("ver_plano", plano_id=plano.id))

    @app.get("/planos/novo")
    def novo_plano():
        piloto, resposta = exigir()
        if piloto is None:
            return resposta
        aeronaves = g.db.query(Aeronave).order_by(Aeronave.nome).all()
        return render_template("plano_novo.html", aeronaves=aeronaves, orientacao=ler_orientacao())

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
            plano, erro = montar(g.db, piloto, dados, plano)
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
        aeronave = g.db.get(Aeronave, plano.aeronave_id)
        origem = g.db.get(Aerodromo, plano.origem_icao)
        destino = g.db.get(Aerodromo, plano.destino_icao)
        if quer_json():
            return jsonify(para_json(plano))
        return render_template(
            "plano.html",
            plano=plano,
            aeronave=aeronave,
            origem=origem,
            destino=destino,
            orientacao=ler_orientacao(),
        )

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
        return gerar_pdf(plano), 200, {"Content-Type": "application/pdf"}

    @app.get("/aeronaves")
    def aeronaves():
        piloto, resposta = exigir()
        if piloto is None:
            return resposta
        lista = g.db.query(Aeronave).order_by(Aeronave.nome).all()
        return jsonify([
            {
                "id": a.id,
                "nome": a.nome,
                "fonte_manual": a.fonte_manual,
                "peso_max_decolagem_kg": a.peso_max_decolagem_kg,
            }
            for a in lista
        ])

    return app


if __name__ == "__main__":
    criar_app().run(host="127.0.0.1", port=5000)
