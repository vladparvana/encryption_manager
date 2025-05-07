from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from database.models.algoritmi import Algoritmi
from database.models.chei import Chei
from database.enums import TipCheie
from datetime import datetime


def create_cheie(
        db: Session,
        id_cheie: str,
        id_algoritm: str,
        cheie_data: bytes,
        tip_cheie: TipCheie,
        expirare: datetime = None
) -> tuple[Chei | None, str | None]:
    try:
        algoritm = db.query(Algoritmi).filter(Algoritmi.id_algoritm == id_algoritm).first()
        if not algoritm:
            return None, f"Algoritmul cu ID {id_algoritm} nu exista"

        existing_cheie = db.query(Chei).filter(Chei.id_cheie == id_cheie).first()
        if existing_cheie:
            return None, f"Cheia cu ID {id_cheie} exista deja"

        cheie = Chei(
            id_cheie=id_cheie,
            id_algoritm=id_algoritm,
            cheie=cheie_data,
            tip_cheie=tip_cheie,
            expirare=expirare
        )

        db.add(cheie)
        db.commit()
        db.refresh(cheie)
        return cheie, None

    except IntegrityError as e:
        db.rollback()
        return None, f"Eroare de integritate: {str(e)}"

    except Exception as e:
        db.rollback()
        return None, f"Eroare neasteptata: {str(e)}"


def get_cheie(db: Session, id_cheie: str) -> Chei:
    return db.query(Chei).filter(Chei.id_cheie == id_cheie).first()


def get_toate_cheile(db: Session, skip: int = 0, limit: int = 100) -> list[Chei]:
    return db.query(Chei).offset(skip).limit(limit).all()


def get_chei_dupa_algoritm(db: Session, id_algoritm: str) -> list[Chei]:
    return db.query(Chei).filter(Chei.id_algoritm == id_algoritm).all()


def update_cheie(
        db: Session,
        id_cheie: str,
        cheie_data: bytes = None,
        expirare: datetime = None
) -> Chei:
    cheie = get_cheie(db, id_cheie)
    if not cheie:
        return None

    if cheie_data:
        cheie.cheie = cheie_data
    if expirare:
        cheie.expirare = expirare

    db.commit()
    db.refresh(cheie)
    return cheie


def delete_cheie(db: Session, id_cheie: str) -> bool:
    cheie = get_cheie(db, id_cheie)
    if not cheie:
        return False

    db.delete(cheie)
    db.commit()
    return True