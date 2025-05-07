# database/crud/fisiere_crud.py
from sqlalchemy.orm import Session
from datetime import datetime
from database.models.fisiere import Fisiere
from database import StatusFisier
from typing import Optional, List, Tuple


def create_fisier(db: Session, id_fisier: str, name_fisier: str, dimensiune: int,
                  locate_fisier: str, hash: str,
                  status: StatusFisier = StatusFisier.necriptat)-> Tuple[Optional[Fisiere], str]:
    try:
        existent = db.query(Fisiere).get(id_fisier)
        if existent:
            return None, f"Fisier cu ID {id_fisier} exista deja"

        fisier_nou = Fisiere(
            id_fisier=id_fisier,
            name_fisier=name_fisier,
            dimensiune=dimensiune,
            data_creare=datetime.now(),
            status=status,
            locate_fisier=locate_fisier,
            hash=hash
        )

        db.add(fisier_nou)
        db.commit()
        return fisier_nou, ""

    except Exception as e:
        db.rollback()
        return None, f"Eroare la creare fisier: {str(e)}"


def get_fisier(db: Session, id_fisier: str) -> Optional[Fisiere]:
    return db.query(Fisiere).get(id_fisier)


def get_toate_fisierele(db: Session) -> List[Fisiere]:
    return db.query(Fisiere).all()


def get_fisiere_dupa_status(db: Session, status: StatusFisier) -> List[Fisiere]:
    return db.query(Fisiere).filter(Fisiere.status == status).all()


def update_fisier(
        db: Session,
        id_fisier: str,
        name_fisier: Optional[str] = None,
        dimensiune: Optional[int] = None,
        status: Optional[StatusFisier] = None,
        locate_fisier: Optional[str] = None,
        hash: Optional[str] = None
) -> Tuple[Optional[Fisiere], str]:
    try:
        fisier = db.query(Fisiere).get(id_fisier)
        if not fisier:
            return None, "Fisierul nu exista"

        if name_fisier is not None:
            fisier.name_fisier = name_fisier
        if dimensiune is not None:
            if dimensiune < 0:
                return None, "Dimensiunea nu poate fi negativa"
            fisier.dimensiune = dimensiune
        if status is not None:
            fisier.status = status
        if locate_fisier is not None:
            fisier.locate_fisier = locate_fisier
        if hash is not None:
            fisier.hash = hash

        db.commit()
        return fisier, ""

    except Exception as e:
        db.rollback()
        return None, f"Eroare la actualizare: {str(e)}"


def delete_fisier(db: Session, id_fisier: str) -> Tuple[bool, str]:
    try:
        fisier = db.query(Fisiere).get(id_fisier)
        if not fisier:
            return False, "Fișierul nu exista"

        db.delete(fisier)
        db.commit()
        return True, ""

    except Exception as e:
        db.rollback()
        return False, f"Eroare la stergere: {str(e)}"