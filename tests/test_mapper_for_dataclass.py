"""Tests related to mapping from dataclasses

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


def test_dataclass_to_pydantic():

    # Arrange
    master = PersonDataclass(name="Chief", age=99, genero=GenderDataclass.OTHER)
    person = PersonDataclass(name="John", age=25, genero=GenderDataclass.MALE)
    person2 = PersonDataclass(name="Jane", age=25, genero=GenderDataclass.FEMALE)
    pet1 = PetDataclass(name="Rex", age=5, species="Dog")
    pet2 = PetDataclass(name="Whiskers", age=3, species="Cat")
    pet3 = PetDataclass(name="Tweety", age=2, species="Bird")
    family = FamilyDataclass(
        members=[person, person2],
        name="Doe",
        pets={"dog": pet1, "cat": pet2, "bird": pet3},
        master=master,
    )
    clan = ClanDataclass(families=[family], name="Smith")

    # Act
    mapper = Mapper()
    mapper.add_custom_mapping(PersonDataclass, "genero", "gender")
    mapped_clan = mapper.map(clan, ClanPydantic)

    # Assert
    assert isinstance(mapped_clan, ClanPydantic)
    assert isinstance(mapped_clan.families[0], FamilyPydantic)
    assert isinstance(mapped_clan.families[0].members[0], PersonPydantic)
    assert isinstance(mapped_clan.families[0].members[0].gender, GenderPydantic)
    assert mapped_clan.families[0].members[0].gender == GenderPydantic.MALE
    assert isinstance(mapped_clan.families[0].pets["dog"], PetPydantic)


def test_dataclass_to_sqlalchemy():

    # Arrange
    master = PersonDataclass(name="Chief", age=99, genero=GenderDataclass.OTHER)
    person = PersonDataclass(name="John", age=25, genero=GenderDataclass.MALE)
    person2 = PersonDataclass(name="Jane", age=25, genero=GenderDataclass.FEMALE)
    pet1 = PetDataclass(name="Rex", age=5, species="Dog")
    pet2 = PetDataclass(name="Whiskers", age=3, species="Cat")
    pet3 = PetDataclass(name="Tweety", age=2, species="Bird")
    family = FamilyDataclass(
        members=[person, person2],
        name="Doe",
        pets={"dog": pet1, "cat": pet2, "bird": pet3},
        master=master,
    )

    # Act
    mapper = Mapper()
    mapper.add_custom_mapping(PersonDataclass, "genero", "gender")
    mapped_family = mapper.map(family, FamilyAlchemy)

    # Assert


def dataclass_to_sqlalchemy_simple():

    # Arrange
    person = PersonDataclass(name="John", age=25, genero=GenderDataclass.MALE)

    # Act
    mapper = Mapper()
    mapper.add_custom_mapping(PersonDataclass, "genero", "gender")
    mapped_person = mapper.map(person, PersonAlchemy)

    # Assert


def test_dataclass_to_basic():

    # Arrange
    master = PersonDataclass(name="Chief", age=99, genero=GenderDataclass.OTHER)
    person = PersonDataclass(name="John", age=25, genero=GenderDataclass.MALE)
    person2 = PersonDataclass(name="Jane", age=25, genero=GenderDataclass.FEMALE)
    pet1 = PetDataclass(name="Rex", age=5, species="Dog")
    pet2 = PetDataclass(name="Whiskers", age=3, species="Cat")
    pet3 = PetDataclass(name="Tweety", age=2, species="Bird")
    family = FamilyDataclass(
        members=[person, person2],
        name="Doe",
        pets={"dog": pet1, "cat": pet2, "bird": pet3},
        master=master,
    )
    clan = ClanDataclass(families=[family], name="Smith")

    # Act
    mapper = Mapper()
    mapper.add_custom_mapping(PersonDataclass, "genero", "gender")
    mapped_clan = mapper.map(clan, Clan)

    # Assert
    assert isinstance(mapped_clan, Clan)
    assert isinstance(mapped_clan.families[0], Family)
    assert isinstance(mapped_clan.families[0].members[0], Person)
    assert isinstance(mapped_clan.families[0].members[0].gender, Gender)
    assert mapped_clan.families[0].members[0].gender == Gender.MALE
    assert isinstance(mapped_clan.families[0].pets["dog"], Pet)
