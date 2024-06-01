from enum import Enum

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

Base = declarative_base()


class GenderAlchemy(Enum):
    MALE = 1
    FEMALE = 2
    FURRY = 3
    OTHER = 4


class FamilyAlchemy(Base):
    __tablename__ = "families"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    # pets: Dict[str, PetAlchemy]
    members: Mapped[list["PersonAlchemy"]] = relationship(
        "PersonAlchemy", back_populates="family"
    )

    def __repr__(self):
        return f"<FamilyAlchemy(name='{self.name}', members={[member for member in self.members]})>"


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

    def __repr__(self):
        return f"<PersonAlchemy(name='{self.name}', age={self.age}, gender='{self.gender}')>"


class PetAlchemy(Base):
    __tablename__ = "pets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    age: Mapped[int] = mapped_column(Integer)
    species: Mapped[str] = mapped_column(String(50), nullable=True)

    def __repr__(self):
        return f"<PetAlchemy(name='{self.name}', age={self.age}, species='{self.species}')>"
