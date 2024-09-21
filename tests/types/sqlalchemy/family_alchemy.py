from enum import Enum
from typing import ForwardRef, List

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

from .base_model import Base

"""
To avoid the issue of circular references and continue using get_type_hints, you can use deferred type annotations with ForwardRef from the typing module.
This allows type annotations to be resolved at runtime, thus avoiding circular import problems.

Explanation: When you have two classes that reference each other, importing them directly can lead to circular import issues.
By using ForwardRef, you can defer the resolution of the type annotations until runtime.
This means that the types are not immediately evaluated when the module is imported, which helps to avoid circular dependencies.

"""

# Use ForwardRef to resolve circular imports
PersonAlchemy = ForwardRef("PersonAlchemy")


class FamilyAlchemy(Base):
    __tablename__ = "families"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    master: Mapped["PersonAlchemy"] = relationship(
        "PersonAlchemy", back_populates="families"
    )

    # pets: Dict[str, PetAlchemy]
    members: Mapped[list["PersonAlchemy"]] = relationship(
        "PersonAlchemy", back_populates="family"
    )

    def __repr__(self):
        return f"<FamilyAlchemy(name='{self.name}', members={[member for member in self.members]})>"


# Now we can resolve the circular import
from .person_alchemy import PersonAlchemy

# Update the annotations
FamilyAlchemy.__annotations__["master"] = PersonAlchemy
FamilyAlchemy.__annotations__["members"] = list[PersonAlchemy]
