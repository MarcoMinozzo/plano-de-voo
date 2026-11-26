from datetime import timedelta

from werkzeug.security import check_password_hash, generate_password_hash

from servidor.modelos import Piloto, TentativaEntrada, agora

MENSAGEM_RECUSA = "Acesso recusado."
MENSAGEM_SENHA_CURTA = "A senha precisa ter no mínimo 8 caracteres."
MENSAGEM_JA_USADA = "Identificação já usada."
MENSAGEM_NOME_EXIBICAO = "Informe um nome de exibição com até 160 caracteres."
JANELA = timedelta(minutes=15)
LIMITE_FALHAS = 5
OCIOSIDADE = timedelta(hours=8)


def senha_curta(senha):
    return senha is None or len(senha) < 8


def normalizar_nome_exibicao(nome):
    if not isinstance(nome, str):
        return None
    nome = nome.strip()
    if not nome or len(nome) > 160:
        return None
    return nome


def em_bloqueio(db, identificacao, momento=None):
    momento = momento or agora()
    inicio = momento - JANELA
    falhas = (
        db.query(TentativaEntrada)
        .filter(
            TentativaEntrada.identificacao == identificacao,
            TentativaEntrada.instante >= inicio,
        )
        .count()
    )
    return falhas >= LIMITE_FALHAS


def _falha(db, identificacao, momento):
    db.add(TentativaEntrada(identificacao=identificacao, instante=momento))
    db.commit()
    return MENSAGEM_RECUSA


def cadastrar(db, identificacao, senha, nome_exibicao):
    identificacao = (identificacao or "").strip()
    nome_exibicao = normalizar_nome_exibicao(nome_exibicao)
    if senha_curta(senha):
        return None, MENSAGEM_SENHA_CURTA
    if not identificacao:
        return None, MENSAGEM_SENHA_CURTA
    if nome_exibicao is None:
        return None, MENSAGEM_NOME_EXIBICAO
    if db.query(Piloto).filter_by(identificacao=identificacao).first():
        return None, MENSAGEM_JA_USADA
    piloto = Piloto(
        identificacao=identificacao,
        senha_hash=generate_password_hash(senha),
        nome_exibicao=nome_exibicao,
        criado_em=agora(),
    )
    db.add(piloto)
    db.commit()
    return piloto, None


def entrar(db, identificacao, senha, momento=None):
    momento = momento or agora()
    identificacao = (identificacao or "").strip()
    if em_bloqueio(db, identificacao, momento):
        return None, MENSAGEM_RECUSA
    piloto = db.query(Piloto).filter_by(identificacao=identificacao).first()
    if piloto is None or not check_password_hash(piloto.senha_hash, senha or ""):
        return None, _falha(db, identificacao, momento)
    return piloto, None


def sessao_expirada(visto_em, momento=None):
    if visto_em is None:
        return True
    momento = momento or agora()
    if visto_em.tzinfo is None:
        visto_em = visto_em.replace(tzinfo=momento.tzinfo)
    return momento - visto_em > OCIOSIDADE
