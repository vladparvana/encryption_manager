from typing import Optional, List

from sqlalchemy.orm import session

from database import TipAlgoritm
from database.models.algoritmi import Algoritmi


def create_algoritm(id_algo: str, nume: str, tip: TipAlgoritm) -> Algoritmi:
    if session.query(Algoritmi).filter(Algoritmi.id_algoritm == id_algo).first():
        raise ValueError(f"Algoritmul {id_algo} exista deja!")

    if not isinstance(tip, TipAlgoritm):
        raise TypeError("Tip algoritm invalid. Alegeti dintre TipAlgoritm.simetric/asimetric")

    algoritm = Algoritmi(
        id_algoritm=id_algo,
        nume_algoritm=nume,
        tip_algoritm=tip
    )

    session.add(algoritm)
    session.commit()
    return algoritm

def get_algoritm(id_algo: str) -> Optional[Algoritmi]:
    return session.query(Algoritmi).filter(Algoritmi.id_algoritm == id_algo).first()

def get_all_algoritmi() -> List[Algoritmi]:
    return session.query(Algoritmi).order_by(Algoritmi.id_algoritm).all()


def update_algoritm(id_algo: str, **kwargs) -> bool:
    algoritm = get_algoritm(id_algo)
    if not algoritm:
        return False

    allowed_fields = {'nume_algoritm', 'tip_algoritm'}
    for key, value in kwargs.items():
        if key not in allowed_fields:
            raise KeyError(f"Camp invalid pentru actualizare: {key}")

        if key == 'tip_algoritm' and not isinstance(value, TipAlgoritm):
            raise TypeError("Tip algoritm invalid")

        setattr(algoritm, key, value)

    session.commit()
    return True


def delete_algoritm(id_algo: str) -> bool:
    algoritm = get_algoritm(id_algo)
    if not algoritm:
        return False

    session.delete(algoritm)
    session.commit()
    return True