from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
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
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class TentativaEntrada(Base):
    __tablename__ = "tentativa_entrada"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    identificacao: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    instante: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Aeronave(Base):
    __tablename__ = "aeronave"
    __table_args__ = (
        CheckConstraint(
            "peso_max_decolagem_kg > peso_vazio_kg",
            name="ck_aeronave_mtow_maior_que_vazio",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    fonte_manual: Mapped[str] = mapped_column(Text, nullable=False)
    peso_vazio_kg: Mapped[float] = mapped_column(Float, nullable=False)
    peso_max_decolagem_kg: Mapped[float] = mapped_column(Float, nullable=False)
    bagagem_max_kg: Mapped[float] = mapped_column(Float, nullable=False)
    braco_bagagem_m: Mapped[float] = mapped_column(Float, nullable=False)
    combustivel_valor: Mapped[float] = mapped_column(Float, nullable=False)
    combustivel_unidade: Mapped[str] = mapped_column(String(20), nullable=False)
    velocidade_valor: Mapped[float] = mapped_column(Float, nullable=False)
    velocidade_unidade: Mapped[str] = mapped_column(String(20), nullable=False)
    consumo_valor: Mapped[float] = mapped_column(Float, nullable=False)
    consumo_unidade: Mapped[str] = mapped_column(String(20), nullable=False)
    itens_manutencao: Mapped[list] = mapped_column(JSON, nullable=False)


class Aerodromo(Base):
    __tablename__ = "aerodromo"
    __table_args__ = (
        CheckConstraint("char_length(icao) = 4", name="ck_aerodromo_icao_quatro"),
    )

    icao: Mapped[str] = mapped_column(String(4), primary_key=True)
    nome: Mapped[str] = mapped_column(String(160), nullable=False)
    lat: Mapped[float] = mapped_column(Float, nullable=False)
    lon: Mapped[float] = mapped_column(Float, nullable=False)
    elev_m: Mapped[float] = mapped_column(Float, nullable=False)
    fonte: Mapped[str] = mapped_column(Text, nullable=False)


class PlanoDeVoo(Base):
    __tablename__ = "plano_de_voo"
    __table_args__ = (
        CheckConstraint("origem_icao <> destino_icao", name="ck_plano_origem_destino"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    piloto_id: Mapped[int] = mapped_column(ForeignKey("piloto.id"), nullable=False, index=True)
    aeronave_id: Mapped[int] = mapped_column(ForeignKey("aeronave.id"), nullable=False)
    origem_icao: Mapped[str] = mapped_column(ForeignKey("aerodromo.icao"), nullable=False)
    destino_icao: Mapped[str] = mapped_column(ForeignKey("aerodromo.icao"), nullable=False)
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
