from servidor.imagens_aeronave import imagem_da_aeronave

MODELOS = {
    "CESSNA AIRCRAFT 152": "cessna-152.jpg",
    "CESSNA AIRCRAFT 172M": "cessna-172.jpg",
    "CESSNA AIRCRAFT 172N": "cessna-172.jpg",
    "CESSNA AIRCRAFT 172P": "cessna-172.jpg",
    "CESSNA AIRCRAFT 182P": "cessna-182.jpg",
    "CESSNA AIRCRAFT 182T": "cessna-182.jpg",
    "CIRRUS DESIGN SR20": "cirrus-sr20.jpg",
    "CIRRUS DESIGN SR22": "cirrus-sr22.jpg",
    "CIRRUS DESIGN SR22T": "cirrus-sr22t.jpg",
    "PIPER AIRCRAFT PA-28-161": "piper-pa28-161.jpg",
    "PIPER AIRCRAFT PA-28-181": "piper-pa28-181.jpg",
    "PIPER AIRCRAFT PA-28R-201": "piper-pa28r.jpg",
    "PIPER AIRCRAFT PA-32-301": "piper-pa32.jpg",
    "PIPER AIRCRAFT PA-46-350P": "piper-pa46-350p.jpg",
    "PIPER AIRCRAFT PA-46R-350T": "piper-pa46r.jpg",
    "NEIVA EMB-711C": "neiva-711.jpg",
    "NEIVA EMB-711ST": "neiva-711.jpg",
    "NEIVA EMB-712": "neiva-712.jpg",
    "NEIVA EMB-720D": "neiva-720.jpg",
    "BEECH AIRCRAFT A36": "beech-a36.jpg",
}


def test_cada_modelo_listado_tem_a_foto_da_familia():
    for nome, arquivo in MODELOS.items():
        foto = imagem_da_aeronave(nome)
        assert foto is not None, nome
        assert foto.arquivo == arquivo
        assert foto.autor
        assert foto.licenca
        assert foto.fonte.startswith("https://commons.wikimedia.org/")


def test_modelo_sem_foto_conhecida_nao_recebe_imagem_de_outro():
    assert imagem_da_aeronave("Modelo Base") is None
    assert imagem_da_aeronave("Cessna 140") is None
    assert imagem_da_aeronave("") is None
