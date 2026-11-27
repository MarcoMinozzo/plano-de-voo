"""Fotos ilustrativas dos modelos, com licença livre e crédito visível.

As imagens vêm do Wikimedia Commons. Não são fotos do site do fabricante
nem representam uma aeronave específica da frota.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class FotoAeronave:
    arquivo: str
    autor: str
    licenca: str
    licenca_url: str
    fonte: str


def _foto(arquivo, autor, licenca, licenca_url, pagina):
    return FotoAeronave(arquivo, autor, licenca, licenca_url, pagina)


CC_BY = "https://creativecommons.org/licenses/by/4.0"
CC_BY_3 = "https://creativecommons.org/licenses/by/3.0"
CC_BY_SA_4 = "https://creativecommons.org/licenses/by-sa/4.0"
CC_BY_SA_3 = "https://creativecommons.org/licenses/by-sa/3.0"
CC_BY_SA_2 = "https://creativecommons.org/licenses/by-sa/2.0"
GFDL_12 = "http://www.gnu.org/licenses/old-licenses/fdl-1.2.html"
GFDL = "http://www.gnu.org/copyleft/fdl.html"

CESSNA_152 = _foto(
    "cessna-152.jpg",
    "Md Shaifuzzaman Ayon",
    "CC BY-SA 4.0",
    CC_BY_SA_4,
    "https://commons.wikimedia.org/wiki/File:S2-AEY_Cessna_152_II_Arirang_Aviation_15285847_VGHS,_Bangladesh.jpg",
)
CESSNA_172 = _foto(
    "cessna-172.jpg",
    "TRTPUWU",
    "CC BY 4.0",
    CC_BY,
    "https://commons.wikimedia.org/wiki/File:CC-STA_(Cessna_172_of_the_Temuco_Air_club).jpg",
)
CESSNA_182 = _foto(
    "cessna-182.jpg",
    "Felix König",
    "CC BY 3.0",
    CC_BY_3,
    "https://commons.wikimedia.org/wiki/File:Cessna_182N_Skylane.JPG",
)
CIRRUS_SR20 = _foto(
    "cirrus-sr20.jpg",
    "Peter Bakema",
    "GFDL 1.2",
    GFDL_12,
    "https://commons.wikimedia.org/wiki/File:Cirrus_SR20-G2,_Private_JP5979582.jpg",
)
CIRRUS_SR22 = _foto(
    "cirrus-sr22.jpg",
    "Matti Blume",
    "CC BY-SA 4.0",
    CC_BY_SA_4,
    "https://commons.wikimedia.org/wiki/File:Cirrus_SR22,_Trebbin_(_1090102).jpg",
)
CIRRUS_SR22T = _foto(
    "cirrus-sr22t.jpg",
    "Acroterion",
    "CC BY-SA 4.0",
    CC_BY_SA_4,
    "https://commons.wikimedia.org/wiki/File:Cirrus_SR22T_N671MV_FDK_MD1.jpg",
)
PIPER_161 = _foto(
    "piper-pa28-161.jpg",
    "ZLEA",
    "CC BY-SA 4.0",
    CC_BY_SA_4,
    "https://commons.wikimedia.org/wiki/File:Piper_PA-28-161_Warrior_II_(N2107D,_cn_28-7916142)_(11-8-2025).jpg",
)
PIPER_181 = _foto(
    "piper-pa28-181.jpg",
    "kallerna",
    "CC BY-SA 4.0",
    CC_BY_SA_4,
    "https://commons.wikimedia.org/wiki/File:Piper_PA-28-181_Archer_III_Vampula.jpg",
)
PIPER_ARROW = _foto(
    "piper-pa28r.jpg",
    "Anthony Noble",
    "GFDL 1.2",
    GFDL_12,
    "https://commons.wikimedia.org/wiki/File:Piper_PA-28R-180_Cherokee_Arrow_AN1860431.jpg",
)
PIPER_32 = _foto(
    "piper-pa32.jpg",
    "Aldo Bidini",
    "GFDL 1.2",
    GFDL_12,
    "https://commons.wikimedia.org/wiki/File:Piper_PA-32-301_Saratoga,_Private_JP6683284.jpg",
)
PIPER_MIRAGE = _foto(
    "piper-pa46-350p.jpg",
    "Rob Hodgkins",
    "CC BY-SA 2.0",
    CC_BY_SA_2,
    "https://commons.wikimedia.org/wiki/File:N350NM_Piper_Pa46-350P_Malibu_Mirage_Cvt_25-07-17_(36088534361).jpg",
)
PIPER_MATRIX = _foto(
    "piper-pa46r.jpg",
    "Robert Frola",
    "GFDL",
    GFDL,
    "https://commons.wikimedia.org/wiki/File:VH-SJM_Piper_PA-46R-350T_Malibu_Matrix_(6486114703).jpg",
)
NEIVA_711 = _foto(
    "neiva-711.jpg",
    "Aeroprints.com",
    "CC BY-SA 3.0",
    CC_BY_SA_3,
    "https://commons.wikimedia.org/wiki/File:PT-VCP_Embraer_Emb.711_Corisco_(8181526261).jpg",
)
NEIVA_712 = _foto(
    "neiva-712.jpg",
    "Renato Spilimbergo Carvalho",
    "GFDL 1.2",
    GFDL_12,
    "https://commons.wikimedia.org/wiki/File:Embraer_EMB-712_Tupi_AN0828598.jpg",
)
NEIVA_720 = _foto(
    "neiva-720.jpg",
    "Renato Spilimbergo Carvalho",
    "GFDL 1.2",
    GFDL_12,
    "https://commons.wikimedia.org/wiki/File:Embraer_EMB-720D_Minuano_AN1402922.jpg",
)
BEECH_A36 = _foto(
    "beech-a36.jpg",
    "ZLEA",
    "CC BY-SA 4.0",
    CC_BY_SA_4,
    "https://commons.wikimedia.org/wiki/File:Beechcraft_A36_Bonanza_(N66722,_cn_E-2081)_(4-13-2024).jpg",
)

# A regra mais específica vem primeiro. Variantes do mesmo desenho compartilham a foto.
REGRAS = (
    (("SR22T",), CIRRUS_SR22T),
    (("SR22",), CIRRUS_SR22),
    (("SR20",), CIRRUS_SR20),
    (("PA-46R", "PA-46-350T", "MATRIX"), PIPER_MATRIX),
    (("PA-46", "MIRAGE"), PIPER_MIRAGE),
    (("PA-32", "SARATOGA"), PIPER_32),
    (("PA-28R", "ARROW"), PIPER_ARROW),
    (("PA-28-161", "WARRIOR"), PIPER_161),
    (("PA-28-181", "ARCHER", "PA-28"), PIPER_181),
    (("EMB-720", "MINUANO"), NEIVA_720),
    (("EMB-712", "TUPI"), NEIVA_712),
    (("EMB-711", "CORISCO"), NEIVA_711),
    (("A36", "BONANZA"), BEECH_A36),
    (("182",), CESSNA_182),
    (("172",), CESSNA_172),
    (("152",), CESSNA_152),
)


def imagem_da_aeronave(nome):
    if not nome:
        return None
    texto = " ".join(str(nome).upper().split())
    for marcas, foto in REGRAS:
        if any(marca in texto for marca in marcas):
            return foto
    return None
