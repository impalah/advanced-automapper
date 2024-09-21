from enum import Enum
from typing import List

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

from .base_model import Base
from .family_alchemy import FamilyAlchemy


class GenderAlchemy(Enum):
    MALE = 1
    FEMALE = 2
    FURRY = 3
    OTHER = 4


class PersonAlchemy(Base):
    __tablename__ = "persons"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[GenderAlchemy] = mapped_column(
        SqlEnum(GenderAlchemy), nullable=False
    )

    family_id: Mapped[int] = mapped_column(Integer, ForeignKey("families.id"))
    family: Mapped[FamilyAlchemy] = relationship(
        "FamilyAlchemy", back_populates="members"
    )

    families: Mapped[List["FamilyAlchemy"]] = relationship(
        "FamilyAlchemy", back_populates="master"
    )

    def __repr__(self):
        return f"<PersonAlchemy(name='{self.name}', age={self.age}, gender='{self.gender}')>"
