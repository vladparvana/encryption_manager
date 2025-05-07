# test_fisiere_crud.py
from sqlalchemy.orm import Session
from datetime import datetime
from database import SessionLocal, StatusFisier
from database.crud.fisiere_crud import (
    create_fisier,
    get_fisier,
    get_toate_fisierele,
    get_fisiere_dupa_status,
    update_fisier,
    delete_fisier
)
from database.models.fisiere import Fisiere

TEST_ID = "TEST-123"
TEST_LOCATIE = "/test/path/file.txt"


def test_full_fisiere_crud():
    # Setup
    db: Session = SessionLocal()
    cleanup_test_data(db)

    try:
        fisier_nou, error = create_fisier(
            db=db,
            id_fisier=TEST_ID,
            name_fisier="test_file.txt",
            dimensiune=1024,
            locate_fisier=TEST_LOCATIE,
            hash="a1b2c3d4e5f6"
        )
        assert fisier_nou is not None
        assert error == ""
        assert fisier_nou.status == StatusFisier.necriptat
        print("CREATE valid - succes")

        fisier_duplicat, error_duplicat = create_fisier(
            db=db,
            id_fisier=TEST_ID,
            name_fisier="duplicate.txt",
            dimensiune=512,
            locate_fisier="/duplicate/path",
            hash="duphash"
        )
        assert fisier_duplicat is None
        assert "exista deja" in error_duplicat
        print("CREATE duplicate - succes")

        fisier = get_fisier(db, TEST_ID)
        assert fisier is not None
        assert fisier.name_fisier == "test_file.txt"

        toate_fisierele = get_toate_fisierele(db)
        assert len(toate_fisierele) >= 1

        fisiere_necriptate = get_fisiere_dupa_status(db, StatusFisier.necriptat)
        assert any(f.id_fisier == TEST_ID for f in fisiere_necriptate)
        print("READ operatii - succes")

        fisier_actualizat, error_update = update_fisier(
            db=db,
            id_fisier=TEST_ID,
            status=StatusFisier.criptat,
            dimensiune=2048
        )
        assert fisier_actualizat is not None
        assert fisier_actualizat.status == StatusFisier.criptat
        assert fisier_actualizat.dimensiune == 2048

        _, error_invalid = update_fisier(
            db=db,
            id_fisier=TEST_ID,
            dimensiune=-100
        )
        assert "negativa" in error_invalid
        print("UPDATE operatii - succes")

        success_delete, error_delete = delete_fisier(db, TEST_ID)
        assert success_delete is True
        assert error_delete == ""

        fisier_sters = get_fisier(db, TEST_ID)
        assert fisier_sters is None

        success_delete_fantoma, error_fantoma = delete_fisier(db, "ID_INEXISTENT")
        assert success_delete_fantoma is False
        assert "nu exist" in error_fantoma
        print("DELETE operații - succes")

    except Exception as e:
        db.rollback()
        print(f"Eroare : {str(e)}")
        raise
    finally:
        cleanup_test_data(db)
        db.close()


def cleanup_test_data(db: Session):
    db.query(Fisiere).filter(Fisiere.id_fisier == TEST_ID).delete()
    db.commit()


def test_cazuri_frontiera():
    db: Session = SessionLocal()

    try:
        fisier, error = create_fisier(
            db=db,
            id_fisier="TEST-EDGE-1",
            name_fisier="empty.txt",
            dimensiune=0,
            locate_fisier="/empty",
            hash="0" * 64
        )
        assert fisier is not None
        assert fisier.dimensiune == 0
        print("Dimensiune zero - succes")

        nume_lung = "a" * 255
        fisier, error = create_fisier(
            db=db,
            id_fisier="TEST-EDGE-2",
            name_fisier=nume_lung,
            dimensiune=100,
            locate_fisier="/long",
            hash="longhash"
        )
        assert fisier is not None
        assert len(fisier.name_fisier) == 255
        print("Nume lung - succes")

    finally:
        db.query(Fisiere).filter(Fisiere.id_fisier.in_(["TEST-EDGE-1", "TEST-EDGE-2"])).delete()
        db.commit()
        db.close()


if __name__ == "__main__":
    print("Starting Fisiere CRUD tests...")
    test_full_fisiere_crud_cycle()
    test_cazuri_frontiera()
    print("All Fisiere tests completed successfully!")