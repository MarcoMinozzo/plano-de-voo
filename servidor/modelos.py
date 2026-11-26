from datetime import date, datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    create_engine,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, scoped_session, sessionmaker


class Base(DeclarativeBase):
    pass


Sessao = scoped_session(sessionmaker(expire_on_commit=False))


def configurar(url):
    engine = create_engine(url, future=True)
    Sessao.configure(bind=engine)
    return engine


def agora():
    return datetime.now(timezone.utc)


class Piloto(Base):
    __tablename__ = "piloto"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    identificacao: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nome_exibicao: Mapped[str] = mapped_column(String(160), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class TentativaEntrada(Base):
    __tablename__ = "tentativa_entrada"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    identificacao: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    instante: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class EmendaRotaer(Base):
    __tablename__ = "emenda_rotaer"
    __table_args__ = (
        Index(
            "uq_emenda_rotaer_uma_vigente",
            "vigente",
            unique=True,
            postgresql_where=text("vigente"),
            sqlite_where=text("vigente"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo_emenda: Mapped[str] = mapped_column(String(80), nullable=False)
    vigente: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    carregada_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False)


class ExtratoRab(Base):
    __tablename__ = "extrato_rab"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    referencia: Mapped[str] = mapped_column(String(160), nullable=False)
    carregado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False)


class Aeronave(Base):
    __tablename__ = "aeronave"
    __table_args__ = (
        CheckConstraint(
            "peso_max_decolagem_kg > peso_vazio_kg",
            name="ck_aeronave_mtow_maior_que_vazio",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(200), nullable=False)
    frota: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    manual_estado: Mapped[str] = mapped_column(String(20), nullable=False, default="gravado")
    extrato_id: Mapped[int | None] = mapped_column(ForeignKey("extrato_rab.id"), nullable=True)
    fonte_manual: Mapped[str | None] = mapped_column(Text, nullable=True)
    peso_vazio_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    peso_max_decolagem_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    bagagem_max_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    braco_bagagem_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    combustivel_valor: Mapped[float | None] = mapped_column(Float, nullable=True)
    combustivel_unidade: Mapped[str | None] = mapped_column(String(20), nullable=True)
    velocidade_valor: Mapped[float | None] = mapped_column(Float, nullable=True)
    velocidade_unidade: Mapped[str | None] = mapped_column(String(20), nullable=True)
    consumo_valor: Mapped[float | None] = mapped_column(Float, nullable=True)
    consumo_unidade: Mapped[str | None] = mapped_column(String(20), nullable=True)
    itens_manutencao: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    fontes_tecnicas: Mapped[list["FonteTecnicaAeronave"]] = relationship(
        cascade="all, delete-orphan",
        back_populates="aeronave",
        uselist=True,
    )

    @property
    def estimativa_didatica(self):
        return any(
            fonte.tipo_fonte in {"secundaria", "sintetica"}
            for fonte in self.fontes_tecnicas
            if fonte.selecionada
        )

    @property
    def dados_sinteticos(self):
        return any(
            fonte.tipo_fonte == "sintetica"
            for fonte in self.fontes_tecnicas
            if fonte.selecionada
        )


class FonteTecnicaAeronave(Base):
    __tablename__ = "fonte_tecnica_aeronave"
    __table_args__ = (
        Index(
            "uq_fonte_tecnica_um_selecionada_por_campo",
            "aeronave_id",
            "campo",
            unique=True,
            postgresql_where=text("selecionada"),
            sqlite_where=text("selecionada"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    aeronave_id: Mapped[int] = mapped_column(
        ForeignKey("aeronave.id", ondelete="CASCADE"), nullable=False, index=True
    )
    campo: Mapped[str] = mapped_column(String(80), nullable=False)
    valor: Mapped[float] = mapped_column(Float, nullable=False)
    unidade: Mapped[str] = mapped_column(String(20), nullable=False)
    tipo_fonte: Mapped[str] = mapped_column(String(20), nullable=False)
    publicador: Mapped[str] = mapped_column(String(200), nullable=False)
    referencia: Mapped[str] = mapped_column(Text, nullable=False)
    data_publicacao: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    data_consulta: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    modelo_variante: Mapped[str] = mapped_column(String(200), nullable=False)
    perfil: Mapped[str | None] = mapped_column(String(200), nullable=True)
    revisao_edicao: Mapped[str | None] = mapped_column(String(200), nullable=True)
    pagina_tabela: Mapped[str | None] = mapped_column(String(200), nullable=True)
    selecionada: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    divergencia: Mapped[str | None] = mapped_column(Text, nullable=True)
    limite_inferior: Mapped[float | None] = mapped_column(Float, nullable=True)
    limite_superior: Mapped[float | None] = mapped_column(Float, nullable=True)
    metodo_geracao: Mapped[str | None] = mapped_column(Text, nullable=True)
    versao_semente: Mapped[str | None] = mapped_column(String(64), nullable=True)
    incerteza: Mapped[str | None] = mapped_column(Text, nullable=True)
    justificativa_comparabilidade: Mapped[str | None] = mapped_column(Text, nullable=True)

    aeronave: Mapped["Aeronave"] = relationship(back_populates="fontes_tecnicas")


class Aerodromo(Base):
    __tablename__ = "aerodromo"

    icao: Mapped[str] = mapped_column(String(16), primary_key=True)
    nome: Mapped[str] = mapped_column(String(160), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False, default="aerodromo")
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    elev_m: Mapped[float] = mapped_column(Float, nullable=False)
    rotaer_versao_id: Mapped[str | None] = mapped_column(String(80), nullable=True)
    rotaer_atualizado_em: Mapped[date | None] = mapped_column(Date, nullable=True)
    telefone: Mapped[str | None] = mapped_column(Text, nullable=True)
    email: Mapped[str | None] = mapped_column(Text, nullable=True)
    contatos_rotaer_verificados: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    emenda_id: Mapped[int | None] = mapped_column(ForeignKey("emenda_rotaer.id"), nullable=True)
    fonte: Mapped[str] = mapped_column(Text, nullable=False)


class PlanoDeVoo(Base):
    __tablename__ = "plano_de_voo"
    __table_args__ = (
        CheckConstraint("origem_icao <> destino_icao", name="ck_plano_origem_destino"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    piloto_id: Mapped[int] = mapped_column(ForeignKey("piloto.id"), nullable=False, index=True)
    aeronave_id: Mapped[int] = mapped_column(ForeignKey("aeronave.id"), nullable=False)
    origem_icao: Mapped[str] = mapped_column(String(16), ForeignKey("aerodromo.icao"), nullable=False)
    destino_icao: Mapped[str] = mapped_column(String(16), ForeignKey("aerodromo.icao"), nullable=False)
    rota_estado: Mapped[str] = mapped_column(String(20), nullable=False, default="aceitavel")
    motivo: Mapped[str | None] = mapped_column(Text, nullable=True)
    hipotese_reabastecimento: Mapped[str | None] = mapped_column(Text, nullable=True)
    hora_partida: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    dados_particulares: Mapped[dict] = mapped_column(JSON, nullable=False)
    resultado: Mapped[dict] = mapped_column(JSON, nullable=False)
    meteorologia: Mapped[dict] = mapped_column(JSON, nullable=False)
    vento: Mapped[dict] = mapped_column(JSON, nullable=False)
    carta: Mapped[dict] = mapped_column(JSON, nullable=False)
    radar: Mapped[dict] = mapped_column(JSON, nullable=False)
    aviso: Mapped[str] = mapped_column(Text, nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    itens: Mapped[list["ItemChecklist"]] = relationship(
        cascade="all, delete-orphan",
        order_by="ItemChecklist.ordem",
        uselist=True,
    )
    trechos: Mapped[list["Trecho"]] = relationship(
        cascade="all, delete-orphan",
        order_by="Trecho.ordem",
        passive_deletes=True,
        uselist=True,
    )


class ItemChecklist(Base):
    __tablename__ = "item_checklist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plano_id: Mapped[int] = mapped_column(
        ForeignKey("plano_de_voo.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ordem: Mapped[int] = mapped_column(Integer, nullable=False)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    fonte: Mapped[str] = mapped_column(Text, nullable=False)
    marcado: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class Trecho(Base):
    __tablename__ = "trecho"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plano_id: Mapped[int] = mapped_column(
        ForeignKey("plano_de_voo.id", ondelete="CASCADE"), nullable=False, index=True
    )
    ordem: Mapped[int] = mapped_column(Integer, nullable=False)
    origem_icao: Mapped[str] = mapped_column(String(16), ForeignKey("aerodromo.icao"), nullable=False)
    destino_icao: Mapped[str] = mapped_column(String(16), ForeignKey("aerodromo.icao"), nullable=False)
    distancia_valor: Mapped[float] = mapped_column(Float, nullable=False)
    distancia_unidade: Mapped[str] = mapped_column(String(20), nullable=False)
    distancia_fonte: Mapped[str] = mapped_column(Text, nullable=False)
    proa_valor: Mapped[float] = mapped_column(Float, nullable=False)
    proa_unidade: Mapped[str] = mapped_column(String(20), nullable=False)
    proa_fonte: Mapped[str] = mapped_column(Text, nullable=False)
    tempo_valor: Mapped[float] = mapped_column(Float, nullable=False)
    tempo_unidade: Mapped[str] = mapped_column(String(20), nullable=False)
    tempo_fonte: Mapped[str] = mapped_column(Text, nullable=False)
    combustivel_valor: Mapped[float] = mapped_column(Float, nullable=False)
    combustivel_unidade: Mapped[str] = mapped_column(String(20), nullable=False)
    combustivel_fonte: Mapped[str] = mapped_column(Text, nullable=False)
    vento_estado: Mapped[str] = mapped_column(String(20), nullable=False)
    por_do_sol_estado: Mapped[str] = mapped_column(String(20), nullable=False)
    velocidade_solo_kt: Mapped[float] = mapped_column(Float, nullable=False)
