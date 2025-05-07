from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import SessionLocal, TipAlgoritm, TipCheie, StatusFisier
from database.models.algoritmi import Algoritmi
from database.models.chei import Chei
from database.models.fisieragloritmcheie import FisierAlgorithmCheie
from database.models.fisiere import Fisiere
from database.models.performante import Performante

def create():
    db = SessionLocal()

    TEST_ALG_ID = "ALG-TEST-123"
    TEST_CHEIE_ID = "CHEIE-TEST-123"
    TEST_FISIER_ID = "FIS-TEST-123"
    TEST_FAC_ID = "FAC-TEST-123"
    TEST_PERF_ID = "PERF-TEST-123"

    try:
        print("Creare entitati")
        algoritm = Algoritmi(
            id_algoritm=TEST_ALG_ID,
            nume_algoritm="AES-256",
            tip_algoritm=TipAlgoritm.simetric
        )
        db.add(algoritm)

        cheie = Chei(
            id_cheie=TEST_CHEIE_ID,
            id_algoritm=TEST_ALG_ID,
            cheie=b"test-key",
            tip_cheie=TipCheie.simetrica
        )
        db.add(cheie)

        fisier = Fisiere(
            id_fisier=TEST_FISIER_ID,
            name_fisier="test.txt",
            dimensiune=1024,
            locate_fisier="/test",
            hash="test-hash",
            status=StatusFisier.necriptat
        )
        db.add(fisier)

        fac = FisierAlgorithmCheie(
            id=TEST_FAC_ID,
            id_fisier=TEST_FISIER_ID,
            id_algorithm=TEST_ALG_ID,
            id_cheie=TEST_CHEIE_ID,
            data_criptare=datetime.now()
        )
        db.add(fac)

        performanta = Performante(
            id_performanta=TEST_PERF_ID,
            id_algoritm=TEST_ALG_ID,
            timp_criptare=2.5,
            timp_decriptare=3.1,
            memorie_utilizata=150.0
        )
        db.add(performanta)

        db.commit()
        print("Creare entitati - success")

    except Exception as e:
        db.rollback()
        print(f"Test failed: {str(e)}")
        raise

def get():
    db = SessionLocal()

    TEST_ALG_ID = "ALG-TEST-123"
    TEST_CHEIE_ID = "CHEIE-TEST-123"
    TEST_FISIER_ID = "FIS-TEST-123"
    TEST_FAC_ID = "FAC-TEST-123"
    TEST_PERF_ID = "PERF-TEST-123"

    try:
        print("Test get")
        alg = db.query(Algoritmi).get(TEST_ALG_ID)
        ch = db.query(Chei).get(TEST_CHEIE_ID)
        fis = db.query(Fisiere).get(TEST_FISIER_ID)
        fac_obj = db.query(FisierAlgorithmCheie).get(TEST_FAC_ID)
        perf = db.query(Performante).get(TEST_PERF_ID)


        assert all([alg, ch, fis, fac_obj, perf]), "Test get - fail"
        print(alg.__dict__)
        print(ch.__dict__)
        print(fis.__dict__)
        print(fac_obj.__dict__)
        print(perf.__dict__)
        print("Test get - success")
    except Exception as e:
        db.rollback()
        print(f"Test failed: {str(e)}")
        raise

def update():
    db = SessionLocal()

    TEST_ALG_ID = "ALG-TEST-123"
    TEST_CHEIE_ID = "CHEIE-TEST-123"
    TEST_FISIER_ID = "FIS-TEST-123"
    TEST_FAC_ID = "FAC-TEST-123"
    TEST_PERF_ID = "PERF-TEST-123"

    try:
        alg = db.query(Algoritmi).get(TEST_ALG_ID)
        ch = db.query(Chei).get(TEST_CHEIE_ID)
        fis = db.query(Fisiere).get(TEST_FISIER_ID)
        fac_obj = db.query(FisierAlgorithmCheie).get(TEST_FAC_ID)
        perf = db.query(Performante).get(TEST_PERF_ID)

        print("Test update")
        alg.nume_algoritm = "AES-256-Updated"
        db.commit()
        assert db.query(Algoritmi).get(TEST_ALG_ID).nume_algoritm == "AES-256-Updated"
        print("Update Algoritmi - success")

        ch.cheie = b"new-test-key"
        db.commit()
        assert db.query(Chei).get(TEST_CHEIE_ID).cheie == b"new-test-key"
        print("Update Chei - success")

        fis.status = StatusFisier.criptat
        db.commit()
        assert db.query(Fisiere).get(TEST_FISIER_ID).status == StatusFisier.criptat
        print("Update Fisiere - success")

        new_decriptare = datetime.now() + timedelta(hours=1)
        fac_obj.data_decriptare = new_decriptare
        db.commit()
        assert db.query(FisierAlgorithmCheie).get(TEST_FAC_ID).data_decriptare == new_decriptare
        print("Update FAC - success")

        perf.timp_criptare = 3.0
        perf.memorie_utilizata = 160.0
        db.commit()
        updated_perf = db.query(Performante).get(TEST_PERF_ID)
        assert updated_perf.timp_criptare == 3.0 and updated_perf.memorie_utilizata == 160.0
        print("Update Performante - success")
    except Exception as e:
        db.rollback()
        print(f"Test failed: {str(e)}")
        raise


def delete():
    db = SessionLocal()

    TEST_ALG_ID = "ALG-TEST-123"
    TEST_CHEIE_ID = "CHEIE-TEST-123"
    TEST_FISIER_ID = "FIS-TEST-123"
    TEST_FAC_ID = "FAC-TEST-123"
    TEST_PERF_ID = "PERF-TEST-123"

    try:

        alg = db.query(Algoritmi).get(TEST_ALG_ID)
        ch = db.query(Chei).get(TEST_CHEIE_ID)
        fis = db.query(Fisiere).get(TEST_FISIER_ID)
        fac_obj = db.query(FisierAlgorithmCheie).get(TEST_FAC_ID)
        perf = db.query(Performante).get(TEST_PERF_ID)
        print("Delete")
        db.delete(alg)
        db.commit()

        assert not db.query(Algoritmi).get(TEST_ALG_ID), "Algoritm not deleted"
        assert not db.query(Chei).get(TEST_CHEIE_ID), "Cheie not deleted"
        assert not db.query(FisierAlgorithmCheie).get(TEST_FAC_ID), "FAC not deleted"
        assert not db.query(Performante).get(TEST_PERF_ID), "Performanta not deleted"
        assert db.query(Fisiere).get(TEST_FISIER_ID), "Fisiere deleted incorrectly"
        print("Delete - success")

    except Exception as e:
        db.rollback()
        print(f"Test failed: {str(e)}")
        raise


