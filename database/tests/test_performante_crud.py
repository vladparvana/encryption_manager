from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from database import SessionLocal, TipAlgoritm
from database.models.algoritmi import Algoritmi
from database.models.performante import Performante


def test_performante_crud():
    # Setup
    db: Session = SessionLocal()

    # ID-uri de test
    TEST_ALGORITM_ID = "AES-256-TEST"
    TEST_PERFORMANTA_ID = "PERF-TEST-123"

    try:
        # Test CREATE
        algoritm_test = Algoritmi(
            id_algoritm=TEST_ALGORITM_ID,
            nume_algoritm="Test Algoritm",
            tip_algoritm=TipAlgoritm.simetric
        )
        db.add(algoritm_test)
        db.commit()

        # Test CREATE

        performanta_noua = Performante(
            id_performanta=TEST_PERFORMANTA_ID,
            id_algoritm=TEST_ALGORITM_ID,
            timp_criptare=2.5,
            timp_decriptare=3.1,
            memorie_utilizata=150.0,
            data_test=datetime.now()
        )
        db.add(performanta_noua)
        db.commit()

        # Verificare
        perf_creata = db.query(Performante).get(TEST_PERFORMANTA_ID)
        assert perf_creata is not None
        assert perf_creata.memorie_utilizata == 150.0
        print("CREATE Performanta - succes")

        # Test READ
        perf_citita = db.query(Performante).get(TEST_PERFORMANTA_ID)
        assert perf_citita.timp_criptare == 2.5

        toate_perf = db.query(Performante).all()
        assert len(toate_perf) >= 1

        perf_algoritm = db.query(Performante).filter(
            Performante.id_algoritm == TEST_ALGORITM_ID
        ).all()
        assert len(perf_algoritm) == 1
        print("READ Performanta - succes")

        # Test UPDATE

        perf_citita.memorie_utilizata = 160.0
        db.commit()

        perf_actualizata = db.query(Performante).get(TEST_PERFORMANTA_ID)
        assert perf_actualizata.memorie_utilizata == 160.0
        print("UPDATE Performanta - succes")

        # =============================================
        # Test DELETE
        # =============================================
        db.delete(perf_actualizata)
        db.commit()

        perf_stearsa = db.query(Performante).get(TEST_PERFORMANTA_ID)
        assert perf_stearsa is None
        print("DELETE - succes")

    except Exception as e:
        db.rollback()
        print(f"Eroare: {str(e)}")
        raise
    finally:
        # Curățare
        db.query(Performante).filter(Performante.id_performanta == TEST_PERFORMANTA_ID).delete()
        db.query(Algoritmi).filter(Algoritmi.id_algoritm == TEST_ALGORITM_ID).delete()
        db.commit()
        db.close()


def test_scenarii_performante_invalide():
    db: Session = SessionLocal()
    TEST_ALGORITM_ID = "AES-256-TEST"

    try:
        # Setup algoritm de test
        algoritm_test = Algoritmi(
            id_algoritm=TEST_ALGORITM_ID,
            nume_algoritm="Test Algoritm",
            tip_algoritm=TipAlgoritm.simetric
        )
        db.add(algoritm_test)
        db.commit()

        # Test 1: Algoritm inexistent
        try:
            perf_invalida = Performante(
                id_performanta="PERF-INVALID-1",
                id_algoritm="ID_INEXISTENT",
                memorie_utilizata=100.0
            )
            db.add(perf_invalida)
            db.commit()
            assert False, "Ar fi trebuit sa esueze"
        except Exception as e:
            db.rollback()
            print("Test algoritm inexistent - succes")

        # Test 2: Memorie negativă
        try:
            perf_invalida = Performante(
                id_performanta="PERF-INVALID-2",
                id_algoritm=TEST_ALGORITM_ID,
                memorie_utilizata=-10.0
            )
            db.add(perf_invalida)
            db.commit()
            assert False, "Ar fi trebuit sa esueze"
        except Exception as e:
            db.rollback()
            print("Test memorie negativa - succes")

    finally:
        # Curățare
        db.query(Performante).filter(Performante.id_performanta.in_(["PERF-INVALID-1", "PERF-INVALID-2"])).delete()
        db.query(Algoritmi).filter(Algoritmi.id_algoritm == TEST_ALGORITM_ID).delete()
        db.commit()
        db.close()


if __name__ == "__main__":
    print("Pornire teste Performante CRUD")
    test_performante_crud()
    test_scenarii_performante_invalide()
    print("Toate testele completate")