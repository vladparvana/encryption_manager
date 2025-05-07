from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Tuple, List
import uuid

from database.models.algoritmi import Algoritmi
from database.models.chei import Chei
from database.models.fisiere import Fisiere
from database.models.performante import Performante
from database.models.frameworks import Frameworks
from database.models.fisieragloritmcheie import FisierAlgorithmCheie
from database.enums import TipFramework, StatusFisier, TipAlgoritm, TipCheie

def create_file_operation(
    db: Session,
    file_id: str,
    algorithm_id: str,
    key_id: str,
    operation_type: str,
    performance_data: dict,
    output_path: str = None,
    framework_id: str = None
) -> Tuple[Optional[FisierAlgorithmCheie], str]:
    try:
        # Verify all entities exist
        file = db.query(Fisiere).get(file_id)
        algorithm = db.query(Algoritmi).get(algorithm_id)
        key = db.query(Chei).get(key_id)

        errors = []
        if not file:
            errors.append("Fișierul nu există")
        if not algorithm:
            errors.append("Algoritmul nu există")
        if not key:
            errors.append("Cheia nu există")

        if errors:
            return None, ", ".join(errors)

        # Generate a unique id for performance
        perf_id = str(uuid.uuid4())

        # Create performance record first
        if framework_id:
            framework = db.query(Frameworks).get(framework_id)
        else:
            framework = db.query(Frameworks).filter(Frameworks.nume_framework == 'OpenSSL').first()
            if not framework:
                # Use algorithm's encrypt/decrypt commands if available
                encrypt_cmd = getattr(algorithm, 'comanda_criptare', None)
                decrypt_cmd = getattr(algorithm, 'comanda_decriptare', None)
                if not encrypt_cmd or not decrypt_cmd:
                    if hasattr(algorithm, 'encrypt_cmd') and hasattr(algorithm, 'decrypt_cmd'):
                        encrypt_cmd = algorithm.encrypt_cmd
                        decrypt_cmd = algorithm.decrypt_cmd
                    else:
                        encrypt_cmd = 'openssl enc -aes-256-cbc -salt -in "{input}" -out "{output}" -pass pass:{key}'
                        decrypt_cmd = 'openssl enc -aes-256-cbc -d -salt -in "{input}" -out "{output}" -pass pass:{key}'
                framework = Frameworks(
                    id_framework=str(uuid.uuid4()),
                    nume_framework='OpenSSL',
                    tip_framework='OPENSSL',
                    versiune='1.1.1',
                    comanda_criptare=encrypt_cmd,
                    comanda_decriptare=decrypt_cmd
                )
                db.add(framework)
                db.commit()

        performance = Performante(
            id_performanta=perf_id,
            id_algoritm=algorithm_id,
            id_framework=framework.id_framework,
            timp_criptare=performance_data.get('encrypt_time'),
            timp_decriptare=performance_data.get('decrypt_time'),
            memorie_utilizata=performance_data.get('memory_used', 0),
            data_test=datetime.now()
        )
        db.add(performance)
        db.flush()  # Ensure id_performanta is available

        # Create file-algorithm-key relationship and link to performance
        fac = FisierAlgorithmCheie(
            id=str(uuid.uuid4()),
            id_fisier=file_id,
            id_algorithm=algorithm_id,
            id_cheie=key_id,
            data_criptare=datetime.now() if operation_type == "Encrypt" else None,
            data_decriptare=datetime.now() if operation_type == "Decrypt" else None,
            output_path=output_path,
            id_performanta=perf_id
        )

        # Update file status
        file.status = StatusFisier.CRIPTAT if operation_type == "Encrypt" else StatusFisier.DECRIPTAT

        # Save all changes
        db.add(fac)
        db.commit()
        print(f"[DEBUG] Saved operation: fac.id={fac.id}, fac.id_performanta={fac.id_performanta}, performance.id_performanta={performance.id_performanta}")

        return fac, ""

    except Exception as e:
        db.rollback()
        return None, f"Eroare la creare operație: {str(e)}"

def get_file_operations(db: Session, file_id: str) -> List[FisierAlgorithmCheie]:
    return db.query(FisierAlgorithmCheie).filter(FisierAlgorithmCheie.id_fisier == file_id).all()

def get_algorithm_operations(db: Session, algorithm_id: str) -> List[FisierAlgorithmCheie]:
    return db.query(FisierAlgorithmCheie).filter(FisierAlgorithmCheie.id_algorithm == algorithm_id).all()

def get_key_operations(db: Session, key_id: str) -> List[FisierAlgorithmCheie]:
    return db.query(FisierAlgorithmCheie).filter(FisierAlgorithmCheie.id_cheie == key_id).all()

def delete_file_operation(db: Session, operation_id: str) -> Tuple[bool, str]:
    try:
        operation = db.query(FisierAlgorithmCheie).get(operation_id)
        if not operation:
            return False, "Operația nu există"

        db.delete(operation)
        db.commit()
        return True, ""

    except Exception as e:
        db.rollback()
        return False, f"Eroare la ștergere operație: {str(e)}" 