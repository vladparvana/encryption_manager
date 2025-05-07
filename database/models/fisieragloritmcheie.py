from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base

class FisierAlgorithmCheie(Base):
    __tablename__ = "fisier_algorithm_cheie"

    id = Column(String(36), primary_key=True)
    id_fisier = Column(String(36), ForeignKey("fisiere.id_fisier",ondelete="CASCADE"), nullable=False)
    id_algorithm = Column(String(50), ForeignKey("algoritmi.id_algoritm",ondelete="CASCADE"), nullable=False)
    id_cheie = Column(String(50), ForeignKey("chei.id_cheie",ondelete="CASCADE"), nullable=False)
    data_criptare = Column(DateTime)
    data_decriptare = Column(DateTime)
    output_path = Column(String, nullable=True)
    id_performanta = Column(String(50), ForeignKey("performante.id_performanta"), nullable=True)

    fisiere = relationship("Fisiere", back_populates="operatii")
    algoritm = relationship("Algoritmi", back_populates="operatii")
    cheie = relationship("Chei", back_populates="operatii")