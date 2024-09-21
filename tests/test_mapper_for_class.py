"""Tests related to mapping from basic python classes

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
from .types.sqlalchemy.family_alchemy import FamilyAlchemy
from .types.sqlalchemy.person_alchemy import GenderAlchemy, PersonAlchemy
from .types.sqlalchemy.pet_alchemy import PetAlchemy


def test_basic_to_dataclass():

    # Arrange
    master = Person(name="Chief", age=99, gender=Gender.OTHER)
    person = Person(name="John", age=25, gender=Gender.MALE)
    person2 = Person(name="Jane", age=25, gender=Gender.FEMALE)
    pet1 = Pet(name="Rex", age=5, species="Dog")
    pet2 = Pet(name="Whiskers", age=3, species="Cat")
    pet3 = Pet(name="Tweety", age=2, species="Bird")
    family = Family(
        members=[person, person2],
        name="Doe",
        pets={"dog": pet1, "cat": pet2, "bird": pet3},
        master=master,
    )
    clan = Clan(families=[family], name="Smith")

    # Act
    mapper = Mapper()
    mapper.add_custom_mapping(Person, "gender", "genero")

    mapped_clan = mapper.map(clan, ClanDataclass)

    # Assert
    assert isinstance(mapped_clan, ClanDataclass)
    assert isinstance(mapped_clan.families[0], FamilyDataclass)
    assert isinstance(mapped_clan.families[0].members[0], PersonDataclass)
    assert isinstance(mapped_clan.families[0].members[0].genero, GenderDataclass)
    assert mapped_clan.families[0].members[0].genero == GenderDataclass.MALE
    assert isinstance(mapped_clan.families[0].pets["dog"], PetDataclass)


def test_basic_family_to_pydantic():

    # Arrange
    master = Person(name="Chief", age=99, gender=Gender.OTHER)
    person = Person(name="John", age=25, gender=Gender.MALE)
    person2 = Person(name="Jane", age=25, gender=Gender.FEMALE)
    pet1 = Pet(name="Rex", age=5, species="Dog")
    pet2 = Pet(name="Whiskers", age=3, species="Cat")
    pet3 = Pet(name="Tweety", age=2, species="Bird")
    family = Family(
        members=[person, person2],
        name="Doe",
        pets={"dog": pet1, "cat": pet2, "bird": pet3},
        master=master,
    )

    # Act
    mapper = Mapper()
    mapped_family = mapper.map(family, FamilyPydantic)

    # Assert
    assert isinstance(mapped_family, FamilyPydantic)
    assert isinstance(mapped_family.master, PersonPydantic)
    assert isinstance(mapped_family.members[0], PersonPydantic)
    assert isinstance(mapped_family.members[0].gender, GenderPydantic)
    assert mapped_family.members[0].gender == GenderPydantic.MALE
    assert isinstance(mapped_family.pets["dog"], PetPydantic)


def test_basic_to_pydantic():

    # Arrange
    master = Person(name="Chief", age=99, gender=Gender.OTHER)
    person = Person(name="John", age=25, gender=Gender.MALE)
    person2 = Person(name="Jane", age=25, gender=Gender.FEMALE)
    pet1 = Pet(name="Rex", age=5, species="Dog")
    pet2 = Pet(name="Whiskers", age=3, species="Cat")
    pet3 = Pet(name="Tweety", age=2, species="Bird")
    family = Family(
        members=[person, person2],
        name="Doe",
        pets={"dog": pet1, "cat": pet2, "bird": pet3},
        master=master,
    )
    clan = Clan(families=[family], name="Smith")

    # Act
    mapper = Mapper()
    mapped_clan = mapper.map(clan, ClanPydantic)

    # Assert
    assert isinstance(mapped_clan, ClanPydantic)
    assert isinstance(mapped_clan.families[0], FamilyPydantic)
    assert isinstance(mapped_clan.families[0].members[0], PersonPydantic)
    assert isinstance(mapped_clan.families[0].members[0].gender, GenderPydantic)
    assert mapped_clan.families[0].members[0].gender == GenderPydantic.MALE
    assert isinstance(mapped_clan.families[0].pets["dog"], PetPydantic)
