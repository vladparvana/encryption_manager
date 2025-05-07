from datetime import datetime

from sqlalchemy import String, Float, ForeignKey, DateTime, Column
from sqlalchemy.orm import relationship

from database.base import Base


class Performante(Base):
    __tablename__ = "performante"

    id_performanta = Column(String(50), primary_key=True)
    id_algoritm = Column(String(50), ForeignKey("algoritmi.id_algoritm", ondelete="CASCADE"), nullable=False)
    id_framework = Column(String(50), ForeignKey("frameworks.id_framework", ondelete="CASCADE"), nullable=False)
    timp_criptare = Column(Float, nullable=True)
    timp_decriptare = Column(Float, nullable=True)
    memorie_utilizata = Column(Float, nullable=False)
    data_test = Column(DateTime, default=datetime.now, nullable=False)

    algoritm = relationship("Algoritmi", back_populates="performante")
    framework = relationship("Frameworks", back_populates="performante")