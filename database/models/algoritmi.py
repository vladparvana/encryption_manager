from sqlalchemy import Column, String, Enum
from sqlalchemy.orm import relationship
from database.base import Base, SessionLocal
from database.enums import TipAlgoritm
import uuid

class Algoritmi(Base):
    __tablename__ = "algoritmi"

    id_algoritm = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nume_algoritm = Column(String(100), nullable=False)
    tip_algoritm = Column(Enum(TipAlgoritm), nullable=False)

    chei = relationship("Chei", back_populates="algoritm", cascade="all, delete")
    operatii = relationship("FisierAlgorithmCheie", back_populates="algoritm", cascade="all, delete")
    performante = relationship("Performante", back_populates="algoritm",cascade="all, delete")

    @classmethod
    def get_by_name(cls, name):
        session = SessionLocal()
        try:
            return session.query(cls).filter(cls.nume_algoritm == name).first()
        finally:
            session.close()
