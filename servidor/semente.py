from servidor import carregar_env
from servidor.modelos import Aerodromo, Aeronave, Sessao, configurar

FONTE_AERODROMOS = "DECEA, coordenada de referência do aeródromo"
FONTE_MANUAL = (
    "Números de estudo do Cessna 140: vazio 404 kg, máximo de decolagem 658 kg, "
    "bagagem 36 kg, braço da bagagem 2,03 m"
)

AERODROMOS = (
    ("SBJD", "Comandante Rolim Adolfo Amaro", -23.18167, -46.94361, 753),
    ("SBAU", "Araçatuba", -21.14417, -50.42639, 415),
    ("SBBU", "Bauru", -22.34500, -49.05389, 617),
    ("SBML", "Frank Miloye Milenkovich", -22.19694, -49.92639, 650),
    ("SBDN", "Presidente Prudente", -22.17500, -51.42444, 452),
    ("SBKP", "Viracopos", -23.0074, -47.1345, 661),
    ("SBRP", "Leite Lopes", -21.1361, -47.7767, 549),
)


def semear(db):
    if db.query(Aeronave).filter_by(nome="Cessna 140").first() is None:
        db.add(
            Aeronave(
                nome="Cessna 140",
                fonte_manual=FONTE_MANUAL,
                peso_vazio_kg=404.0,
                peso_max_decolagem_kg=658.0,
                bagagem_max_kg=36.0,
                braco_bagagem_m=2.03,
                combustivel_valor=22.0,
                combustivel_unidade="gal",
                velocidade_valor=91.0,
                velocidade_unidade="kt",
                consumo_valor=5.0,
                consumo_unidade="gal/h",
                itens_manutencao=[
                    {"texto": "Documentos a bordo conferidos", "fonte": FONTE_MANUAL},
                    {"texto": "Tampas de combustível travadas", "fonte": FONTE_MANUAL},
                    {"texto": "Comandos livres", "fonte": FONTE_MANUAL},
                    {
                        "texto": "Meteorologia e alternativa revistas para voo visual",
                        "fonte": "preparação de voo visual",
                    },
                ],
            )
        )
    for icao, nome, lat, lon, elev in AERODROMOS:
        if db.get(Aerodromo, icao) is None:
            db.add(
                Aerodromo(
                    icao=icao,
                    nome=nome,
                    lat=lat,
                    lon=lon,
                    elev_m=elev,
                    fonte=FONTE_AERODROMOS,
                )
            )
    db.commit()


def main():
    carregar_env()
    import os

    configurar(os.environ["DATABASE_URL"])
    db = Sessao()
    try:
        semear(db)
    finally:
        Sessao.remove()


if __name__ == "__main__":
    main()
