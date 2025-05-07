from datetime import datetime

from sqlalchemy import Column, String, BigInteger, DateTime, Enum
from sqlalchemy.orm import relationship

from database.base import Base
from database.enums import StatusFisier


class Fisiere(Base):
    __tablename__ = "fisiere"

    id_fisier = Column(String(36), primary_key=True)
    name_fisier = Column(String(255), nullable=False)
    dimensiune = Column(BigInteger, nullable=False)
    data_creare = Column(DateTime, default=datetime.now)
    status = Column(Enum(StatusFisier), nullable=False, default=StatusFisier.NECRIPTAT)
    locate_fisier = Column(String(500), nullable=False)
    hash = Column(String(64), nullable=False)

    operatii = relationship("FisierAlgorithmCheie", back_populates="fisiere", cascade="all, delete")