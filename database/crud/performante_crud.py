from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from typing import Optional, Tuple
from database.models.performante import Performante
from database.models.algoritmi import Algoritmi


def create_performanta(
        db: Session,
        id_performanta: str,
        id_algoritm: str,
        timp_criptare: Optional[float],
        timp_decriptare: Optional[float],
        memorie_utilizata: float,
        data_test: datetime = datetime.utcnow()
) -> Tuple[Optional[Performante], Optional[str]]:
    try:
        algoritm = db.query(Algoritmi).filter(Algoritmi.id_algoritm == id_algoritm).first()
        if not algoritm:
            return None, f"Algoritmul cu ID {id_algoritm} nu exista"

        if memorie_utilizata <= 0:
            return None, "Memoria utilizata trebuie sa fie mai mare decat 0"

        performanta = Performante(
            id_performanta=id_performanta,
            id_algoritm=id_algoritm,
            timp_criptare=timp_criptare,
            timp_decriptare=timp_decriptare,
            memorie_utilizata=memorie_utilizata,
            data_test=data_test
        )

        db.add(performanta)
        db.commit()
        db.refresh(performanta)
        return performanta, None

    except IntegrityError as e:
        db.rollback()
        return None, f"Eroare integritate: Cheie duplicata" if "UNIQUE" in str(e) else f"Eroare integritate: {str(e)}"

    except Exception as e:
        db.rollback()
        return None, f"Eroare neasteptata: {str(e)}"


def get_performanta(db: Session, id_performanta: str) -> Optional[Performante]:
    return db.query(Performante).filter(Performante.id_performanta == id_performanta).first()


def get_toate_performantele(db: Session, skip: int = 0, limit: int = 100) -> list[Performante]:
    return db.query(Performante).offset(skip).limit(limit).all()


def get_performante_dupa_algoritm(db: Session, id_algoritm: str) -> list[Performante]:
    return db.query(Performante).filter(Performante.id_algoritm == id_algoritm).all()


def update_performanta(
        db: Session,
        id_performanta: str,
        timp_criptare: Optional[float] = None,
        timp_decriptare: Optional[float] = None,
        memorie_utilizata: Optional[float] = None
) -> Tuple[Optional[Performante], Optional[str]]:
    try:
        performanta = get_performanta(db, id_performanta)
        if not performanta:
            return None, "Performanta nu exista"

        if timp_criptare is not None:
            performanta.timp_criptare = timp_criptare
        if timp_decriptare is not None:
            performanta.timp_decriptare = timp_decriptare
        if memorie_utilizata is not None:
            if memorie_utilizata <= 0:
                return None, "Memoria trebuie să fie pozitiva"
            performanta.memorie_utilizata = memorie_utilizata

        db.commit()
        db.refresh(performanta)
        return performanta, None

    except Exception as e:
        db.rollback()
        return None, f"Eroare actualizare: {str(e)}"


def delete_performanta(db: Session, id_performanta: str) -> Tuple[bool, Optional[str]]:
    performanta = get_performanta(db, id_performanta)
    if not performanta:
        return False, "Performanta nu exista"

    try:
        db.delete(performanta)
        db.commit()
        return True, None
    except Exception as e:
        db.rollback()
        return False, f"Eroare stergere: {str(e)}"