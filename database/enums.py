from enum import Enum

class TipAlgoritm(Enum):
    SIMETRIC = "simetric"
    ASIMETRIC = "asimetric"

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
    PYCA = "pyca"
    CRYPTOGRAPHY = "cryptography"