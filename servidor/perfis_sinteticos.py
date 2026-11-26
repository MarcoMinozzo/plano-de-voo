from dataclasses import dataclass


@dataclass(frozen=True)
class PerfilSintetico:
    alvo_modelo: str
    nome_origem: str
    nome_exibicao: str


PERFIS_SINTETICOS = (
    PerfilSintetico(
        "CESSNA AIRCRAFT 152",
        "Aeronave DEMO 01",
        "CESSNA AIRCRAFT 152",
    ),
    PerfilSintetico(
        "CESSNA AIRCRAFT 172M",
        "Aeronave DEMO 02",
        "CESSNA AIRCRAFT 172M",
    ),
    PerfilSintetico(
        "CESSNA AIRCRAFT 172N",
        "Aeronave DEMO 03",
        "CESSNA AIRCRAFT 172N",
    ),
    PerfilSintetico(
        "CESSNA AIRCRAFT 172P",
        "Aeronave DEMO 04",
        "CESSNA AIRCRAFT 172P",
    ),
    PerfilSintetico(
        "CESSNA AIRCRAFT 182P",
        "Aeronave DEMO 05",
        "CESSNA AIRCRAFT 182P",
    ),
    PerfilSintetico(
        "CESSNA AIRCRAFT 182T",
        "Aeronave DEMO 06",
        "CESSNA AIRCRAFT 182T",
    ),
    PerfilSintetico(
        "CIRRUS DESIGN SR20",
        "Aeronave DEMO 07",
        "CIRRUS DESIGN SR20",
    ),
    PerfilSintetico(
        "CIRRUS DESIGN SR22",
        "Aeronave DEMO 08",
        "CIRRUS DESIGN SR22",
    ),
    PerfilSintetico(
        "CIRRUS DESIGN SR22T",
        "Aeronave DEMO 09",
        "CIRRUS DESIGN SR22T",
    ),
    PerfilSintetico(
        "PIPER AIRCRAFT PA-28-161",
        "Aeronave DEMO 10",
        "PIPER AIRCRAFT PA-28-161",
    ),
    PerfilSintetico(
        "PIPER AIRCRAFT PA-28-181",
        "Aeronave DEMO 11",
        "PIPER AIRCRAFT PA-28-181",
    ),
    PerfilSintetico(
        "PIPER AIRCRAFT PA-28R-201",
        "Aeronave DEMO 12",
        "PIPER AIRCRAFT PA-28R-201",
    ),
    PerfilSintetico(
        "PIPER AIRCRAFT PA-32-301",
        "Aeronave DEMO 13",
        "PIPER AIRCRAFT PA-32-301",
    ),
    PerfilSintetico(
        "PIPER AIRCRAFT PA-46-350P",
        "Aeronave DEMO 14",
        "PIPER AIRCRAFT PA-46-350P",
    ),
    PerfilSintetico(
        "PIPER AIRCRAFT PA-46R-350T",
        "Aeronave DEMO 15",
        "PIPER AIRCRAFT PA-46R-350T",
    ),
    PerfilSintetico(
        "NEIVA EMB-711C",
        "Aeronave DEMO 16",
        "NEIVA EMB-711C",
    ),
    PerfilSintetico(
        "NEIVA EMB-711ST",
        "Aeronave DEMO 17",
        "NEIVA EMB-711ST",
    ),
    PerfilSintetico(
        "NEIVA EMB-712",
        "Aeronave DEMO 18",
        "NEIVA EMB-712",
    ),
    PerfilSintetico(
        "NEIVA EMB-720D",
        "Aeronave DEMO 19",
        "NEIVA EMB-720D",
    ),
    PerfilSintetico(
        "BEECH AIRCRAFT A36",
        "Aeronave DEMO 20",
        "BEECH AIRCRAFT A36",
    ),
)
