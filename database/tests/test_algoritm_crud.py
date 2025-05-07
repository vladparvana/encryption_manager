from sqlalchemy.orm import Session
from database import SessionLocal, TipAlgoritm, TipCheie
from database.crud.chei_crud import create_cheie
from database.models.algoritmi import Algoritmi
from database.models.chei import Chei


def test_algoritmi_crud():
    db: Session = SessionLocal()

    try:

        algoritm_nou = Algoritmi(
            id_algoritm="AES-256",
            nume_algoritm="Advanced Encryption Standard",
            tip_algoritm=TipAlgoritm.simetric
        )
        db.add(algoritm_nou)
        db.commit()

        algoritm_creat = db.query(Algoritmi).filter(Algoritmi.id_algoritm == "AES-256").first()
        assert algoritm_creat is not None
        assert algoritm_creat.nume_algoritm == "Advanced Encryption Standard"
        print("CREATE testat cu succes!")


        algoritmi = db.query(Algoritmi).all()
        assert len(algoritmi) >= 1

        # Citire algoritm specific
        algoritm_citit = db.query(Algoritmi).get("AES-256")
        assert algoritm_citit.tip_algoritm == TipAlgoritm.simetric
        print("READ testat cu succes!")

        # =============================================
        # Test UPDATE
        # =============================================
        algoritm_citit.nume_algoritm = "AES-256 Improved"
        db.commit()

        # Verifică actualizarea
        algoritm_actualizat = db.query(Algoritmi).get("AES-256")
        assert algoritm_actualizat.nume_algoritm == "AES-256 Improved"
        print("UPDATE testat cu succes!")

        db.delete(algoritm_actualizat)
        db.commit()

        algoritm_sters = db.query(Algoritmi).get("AES-256")
        assert algoritm_sters is None
        print("DELETE testat cu succes!")

    except Exception as e:
        db.rollback()

    finally:
        db.close()


