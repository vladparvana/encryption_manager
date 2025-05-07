from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship
from database.base import Base, SessionLocal
from database.enums import TipFramework
import uuid

class Frameworks(Base):
    __tablename__ = "frameworks"

    id_framework = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nume_framework = Column(String(100), nullable=False)
    tip_framework = Column(Enum(TipFramework), nullable=False)
    versiune = Column(String(20), nullable=False)
    comanda_criptare = Column(String(500), nullable=False)
    comanda_decriptare = Column(String(500), nullable=False)

    performante = relationship("Performante", back_populates="framework", cascade="all, delete")

    @classmethod
    def get_by_type(cls, framework_type):
        session = SessionLocal()
        try:
            return session.query(cls).filter(cls.tip_framework == framework_type).first()
        finally:
            session.close() 