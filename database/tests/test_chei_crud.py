from sqlalchemy.orm import Session

from database import SessionLocal, TipCheie, TipAlgoritm
from database.crud.chei_crud import create_cheie
from database.models.algoritmi import Algoritmi
from database.models.chei import Chei


def test_create_cheie_scenarii():
    db: Session = SessionLocal()

    try:
        result, error = create_cheie(
            db=db,
            id_cheie="cheie-test-1",
            id_algoritm="NONEXISTENT-ALGO",
            cheie_data=b"test",
            tip_cheie=TipCheie.simetrica
        )
        assert result is None
        assert "nu exista" in error
        print("Test algoritm inexistent reusit!")

        algoritm_temp = Algoritmi(
            id_algoritm="TEMP-ALGO",
            nume_algoritm="TEMP",
            tip_algoritm=TipAlgoritm.simetric
        )
        db.add(algoritm_temp)
        db.commit()

        create_cheie(
            db=db,
            id_cheie="cheie-test-2",
            id_algoritm="TEMP-ALGO",
            cheie_data=b"test",
            tip_cheie=TipCheie.simetrica
        )

        result, error = create_cheie(
            db=db,
            id_cheie="cheie-test-2",
            id_algoritm="TEMP-ALGO",
            cheie_data=b"test",
            tip_cheie=TipCheie.simetrica
        )
        assert result is None
        assert "există deja" in error
        print("Test cheie duplicata reusit!")

    finally:
        db.query(Chei).filter(Chei.id_cheie.in_(["cheie-test-1", "cheie-test-2"])).delete()
        db.query(Algoritmi).filter(Algoritmi.id_algoritm == "TEMP-ALGO").delete()
        db.commit()
        db.close()