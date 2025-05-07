from sqlalchemy.orm import Session
from datetime import datetime
from database import SessionLocal, StatusFisier, TipAlgoritm, TipCheie
from database.models.algoritmi import Algoritmi
from database.models.chei import Chei
from database.models.fisieragloritmcheie import FisierAlgorithmCheie
from database.models.fisiere import Fisiere

TEST_FAC_ID = "FAC-TEST-123"
TEST_FISIER_ID = "FIS-TEST-123"
TEST_ALG_ID = "ALG-TEST-123"
TEST_CHEIE_ID = "CHEIE-TEST-123"


def test_fac_crud():
    db: Session = SessionLocal()

    try:
        fisier = Fisiere(
            id_fisier=TEST_FISIER_ID,
            name_fisier="test.txt",
            dimensiune=100,
            locate_fisier="/test",
            hash="testhash",
            status=StatusFisier.necriptat
        )

        algoritm = Algoritmi(
            id_algoritm=TEST_ALG_ID,
            nume_algoritm="AES-256",
            tip_algoritm=TipAlgoritm.simetric
        )

        cheie = Chei(
            id_cheie=TEST_CHEIE_ID,
            id_algoritm=TEST_ALG_ID,
            cheie=b"testkey",
            tip_cheie=TipCheie.simetrica
        )

        db.add_all([fisier, algoritm, cheie])
        db.commit()

        fac = FisierAlgorithmCheie(
            id=TEST_FAC_ID,
            id_fisier=TEST_FISIER_ID,
            id_algorithm=TEST_ALG_ID,
            id_cheie=TEST_CHEIE_ID,
            data_criptare=datetime.now()
        )
        db.add(fac)
        db.commit()

        created = db.query(FisierAlgorithmCheie).get(TEST_FAC_ID)
        assert created is not None
        print("CREATE - succes")


        read = db.query(FisierAlgorithmCheie).get(TEST_FAC_ID)
        assert read.id_fisier == TEST_FISIER_ID

        assert read.fisiere.name_fisier == "test.txt"
        assert read.algoritm.nume_algoritm == "AES-256"
        assert read.cheie.tip_cheie == TipCheie.simetrica
        print("READ si relatii - succes")


        new_date = datetime(2023, 1, 1, 12, 0)
        read.data_decriptare = new_date
        db.commit()

        updated = db.query(FisierAlgorithmCheie).get(TEST_FAC_ID)
        assert updated.data_decriptare == new_date
        print("UPDATE - succes")


        db.delete(updated)
        db.commit()

        deleted = db.query(FisierAlgorithmCheie).get(TEST_FAC_ID)
        assert deleted is None
        print("DELETE - succes")

    except Exception as e:
        db.rollback()
        print(f"Eroare: {str(e)}")
        raise
    finally:
        db.query(FisierAlgorithmCheie).filter(FisierAlgorithmCheie.id == TEST_FAC_ID).delete()
        db.query(Chei).filter(Chei.id_cheie == TEST_CHEIE_ID).delete()
        db.query(Algoritmi).filter(Algoritmi.id_algoritm == TEST_ALG_ID).delete()
        db.query(Fisiere).filter(Fisiere.id_fisier == TEST_FISIER_ID).delete()
        db.commit()
        db.close()


if __name__ == "__main__":
    print("Teste CRUD pentru FisierAlgorithmCheie")
    test_fac_crud()
    print("Toate testele au trecut cu succes!")