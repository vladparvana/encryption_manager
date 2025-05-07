from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Tuple, List

from database.models.algoritmi import Algoritmi
from database.models.chei import Chei
from database.models.fisieragloritmcheie import FisierAlgorithmCheie
from database.models.fisiere import Fisiere


def create_fac(
        db: Session,
        fac_id: str,
        id_fisier: str,
        id_algorithm: str,
        id_cheie: str,
        data_criptare: Optional[datetime] = None,
        data_decriptare: Optional[datetime] = None
) -> Tuple[Optional[FisierAlgorithmCheie], str]:
    try:
        fisier = db.query(Fisiere).get(id_fisier)
        algoritm = db.query(Algoritmi).get(id_algorithm)
        cheie = db.query(Chei).get(id_cheie)

        errors = []
        if not fisier:
            errors.append("Fisierul nu exista")
        if not algoritm:
            errors.append("Algoritmul nu exista")
        if not cheie:
            errors.append("Cheia nu exista")

        if errors:
            return None, ", ".join(errors)

        existent = db.query(FisierAlgorithmCheie).get(fac_id)
        if existent:
            return None, "Inregistrarea exista deja"

        fac = FisierAlgorithmCheie(
            id=fac_id,
            id_fisier=id_fisier,
            id_algorithm=id_algorithm,
            id_cheie=id_cheie,
            data_criptare=data_criptare,
            data_decriptare=data_decriptare
        )

        db.add(fac)
        db.commit()
        return fac, ""

    except Exception as e:
        db.rollback()
        return None, f"Eroare la creare: {str(e)}"


def get_fac(db: Session, fac_id: str) -> Optional[FisierAlgorithmCheie]:
    return db.query(FisierAlgorithmCheie).get(fac_id)


def get_all_fac(db: Session) -> List[FisierAlgorithmCheie]:
    return db.query(FisierAlgorithmCheie).all()


def update_fac_dates(
        db: Session,
        fac_id: str,
        data_criptare: Optional[datetime] = None,
        data_decriptare: Optional[datetime] = None
) -> Tuple[Optional[FisierAlgorithmCheie], str]:
    try:
        fac = db.query(FisierAlgorithmCheie).get(fac_id)
        if not fac:
            return None, "Inregistrare negasita"

        if data_criptare:
            fac.data_criptare = data_criptare
        if data_decriptare:
            fac.data_decriptare = data_decriptare

        db.commit()
        return fac, ""

    except Exception as e:
        db.rollback()
        return None, f"Eroare actualizare: {str(e)}"


def delete_fac(db: Session, fac_id: str) -> Tuple[bool, str]:
    try:
        fac = db.query(FisierAlgorithmCheie).get(fac_id)
        if not fac:
            return False, "Inregistrare negasita"

        db.delete(fac)
        db.commit()
        return True, ""

    except Exception as e:
        db.rollback()
        return False, f"Eroare stergere: {str(e)}"