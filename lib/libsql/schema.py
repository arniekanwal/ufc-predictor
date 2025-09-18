from sqlalchemy import String, DateTime, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base

class Fighter(Base):
    __tablename__ = "fighters"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fighter: Mapped[str] = mapped_column(String(35), nullable=False)
    
    # One-to-Many relationship to weightclasses
    weight_classes: Mapped[list["WeightClass"]] = relationship(back_populates="fighter", cascade="all, delete-orphan")

    date = mapped_column(DateTime)
    gender: Mapped[str] = mapped_column(String(6))
    expectedvalue: Mapped[float] = mapped_column(Float)
    currentlosestreak: Mapped[int] = mapped_column(Integer)
    currentwinstreak: Mapped[int] = mapped_column(Integer)
    draws: Mapped[int] = mapped_column(Integer)
    avgsigstrlanded: Mapped[float] = mapped_column(Float)
    avgsigstrpct: Mapped[float] = mapped_column(Float)
    avgsubatt: Mapped[float] = mapped_column(Float)
    avgtdlanded: Mapped[float] = mapped_column(Float)
    avgtdpct: Mapped[float] = mapped_column(Float)
    losses: Mapped[int] = mapped_column(Integer)
    totalroundsfought: Mapped[int] = mapped_column(Integer)
    totaltitlebouts: Mapped[int] = mapped_column(Integer)
    winsbysubmission: Mapped[int] = mapped_column(Integer)
    wins: Mapped[int] = mapped_column(Integer)
    stance: Mapped[str] = mapped_column(String(10), nullable=True)
    heightcms: Mapped[float] = mapped_column(Float)
    reachcms: Mapped[float] = mapped_column(Float)
    weightlbs: Mapped[int] = mapped_column(Integer)
    age: Mapped[int] = mapped_column(Integer)
    winsbydecision: Mapped[int] = mapped_column(Integer)
    winsbykotko: Mapped[int] = mapped_column(Integer)
    ufc_debut: Mapped[int] = mapped_column(Integer)
    dayssincelastfight: Mapped[int] = mapped_column(Integer)
    currelo: Mapped[float] = mapped_column(Float)

    def __repr__(self) -> str:
        return f"<Fighter(id={self.id}, name='{self.fighter}')"
    
class WeightClass(Base):
    __tablename__ = "weight_classes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Establish Foreign Key to link to Fighter table
    fighter_id: Mapped[int] = mapped_column(ForeignKey('fighters.id'), nullable=False)
    # Back reference to the fighter (create relationship)
    fighter: Mapped["Fighter"] = relationship("Fighter", back_populates="weight_classes")
    
    weightclass: Mapped[str] = mapped_column(String(30), nullable=False)

    def __repr__(self):
        return f"<WeightClass(id={self.id}, fighter_id={self.fighter_id}, weight_class='{self.weight_class}')>"