from enum import Enum
from typing import List

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

from .base_model import Base


class PetAlchemy(Base):
    __tablename__ = "pets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    age: Mapped[int] = mapped_column(Integer)
    species: Mapped[str] = mapped_column(String(50), nullable=True)

    def __repr__(self):
        return f"<PetAlchemy(name='{self.name}', age={self.age}, species='{self.species}')>"
