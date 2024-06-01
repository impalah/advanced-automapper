"""Tests related to mapping from sqlalchmey models

Returns:
    _type_: _description_
"""

from automapper import Mapper

from .types.classes import Clan, Family, Gender, Person, Pet
from .types.dataclasses import (
    ClanDataclass,
    FamilyDataclass,
    GenderDataclass,
    PersonDataclass,
    PetDataclass,
)
from .types.pydantic_classes import (
    ClanPydantic,
    FamilyPydantic,
    GenderPydantic,
    PersonPydantic,
    PetPydantic,
)
from .types.sqlalchemy_models import FamilyAlchemy, GenderAlchemy, PersonAlchemy


def test_sqlalchemy_to_dataclass():

    # Arrange
    person = PersonAlchemy(name="John", age=25, gender=GenderAlchemy.MALE)
    person2 = PersonAlchemy(name="Jane", age=25, gender=GenderAlchemy.FEMALE)
    family = FamilyAlchemy(
        members=[person, person2],
        name="Doe",
    )

    # Act
    mapper = Mapper()
    mapper.add_custom_mapping(PersonAlchemy, "gender", "genero")
    mapped_family = mapper.map(family, FamilyDataclass)

    # Assert
    assert isinstance(mapped_family, FamilyDataclass)
    assert isinstance(mapped_family.members[0], PersonDataclass)
    assert isinstance(mapped_family.members[0].genero, GenderDataclass)
    assert mapped_family.members[0].genero == GenderDataclass.MALE


def test_sqlalchemy_to_basic():

    # Arrange
    person = PersonAlchemy(name="John", age=25, gender=GenderAlchemy.MALE)
    person2 = PersonAlchemy(name="Jane", age=25, gender=GenderAlchemy.FEMALE)
    family = FamilyAlchemy(
        members=[person, person2],
        name="Doe",
    )

    # Act
    mapper = Mapper()
    mapped_family = mapper.map(family, Family)

    # Assert
    assert isinstance(mapped_family, Family)
    assert isinstance(mapped_family.members[0], Person)
    assert isinstance(mapped_family.members[0].gender, Gender)
    assert mapped_family.members[0].gender == Gender.MALE


def test_sqlalchemy_to_pydantic():

    # Arrange
    person = PersonAlchemy(name="John", age=25, gender=GenderAlchemy.MALE)
    person2 = PersonAlchemy(name="Jane", age=25, gender=GenderAlchemy.FEMALE)
    family = FamilyAlchemy(
        members=[person, person2],
        name="Doe",
    )

    # Act
    mapper = Mapper()
    mapped_family = mapper.map(family, FamilyPydantic)

    # Assert
    assert isinstance(mapped_family, FamilyPydantic)
    assert isinstance(mapped_family.members[0], PersonPydantic)
    assert isinstance(mapped_family.members[0].gender, GenderPydantic)
    assert mapped_family.members[0].gender == GenderPydantic.MALE
