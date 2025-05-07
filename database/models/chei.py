from datetime import datetime
from sqlalchemy import Column, String, ForeignKey, LargeBinary, DateTime, Enum
from sqlalchemy.orm import relationship
from database.base import Base, SessionLocal
from database.enums import TipCheie
import uuid

class Chei(Base):
    __tablename__ = "chei"

    id_cheie = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    id_algoritm = Column(String, ForeignKey("algoritmi.id_algoritm",ondelete="CASCADE"), nullable=False)
    nume = Column(String(100), nullable=False)
    cheie = Column(LargeBinary, nullable=False)
    data_creare = Column(DateTime, default=datetime.now)
    expirare = Column(DateTime, nullable=True)
    tip_cheie = Column(Enum(TipCheie), nullable=False)

    algoritm = relationship("Algoritmi", back_populates="chei")
    operatii = relationship("FisierAlgorithmCheie", back_populates="cheie",cascade="all, delete")

    @classmethod
    def get_by_name(cls, name):
        session = SessionLocal()
        try:
            return session.query(cls).filter(cls.nume == name).first()
        finally:
            session.close()