from enum import Enum

class TipAlgoritm(Enum):
    SIMETRIC = "simetric"
    ASIMETRIC = "asimetric"
    SIMETRIC_LIBRE = "simetric_libre"
    ASIMETRIC_LIBRE = "asimetric_libre"

class TipCheie(Enum):
    PUBLICA = "publica"
    PRIVATA = "privata"
    SECRETA = "secreta"

class StatusFisier(Enum):
    NECRIPTAT = "necriptat"
    CRIPTAT = "criptat"
    DECRIPTAT = "decriptat"

class TipFramework(Enum):
    OPENSSL = "openssl"
    LIBRESSL = "libressl"
    LIBRE_WRAPPER = "libre_wrapper"