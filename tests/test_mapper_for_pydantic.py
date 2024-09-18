"""Tests related to mapping from pydantic models

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


def test_pydantic_to_sqlalchemy():

    # Arrange
    master = PersonPydantic(name="Chief", age=99, gender=GenderPydantic.OTHER)
    person = PersonPydantic(name="John", age=25, gender=GenderPydantic.MALE)
    person2 = PersonPydantic(name="Jane", age=25, gender=GenderPydantic.FEMALE)
    pet1 = PetPydantic(name="Rex", age=5, species="Dog")
    pet2 = PetPydantic(name="Whiskers", age=3, species="Cat")
    pet3 = PetPydantic(name="Tweety", age=2, species="Bird")
    family = FamilyPydantic(
        members=[person, person2],
        name="Doe",
        pets={"dog": pet1, "cat": pet2, "bird": pet3},
        master=master,
    )

    # Act
    mapper = Mapper()
    mapped_members = mapper.map_list(family.members, PersonAlchemy)
    mapped_family = FamilyAlchemy(name=family.name, members=mapped_members)

    # Assert


def test_pydantic_to_dataclass():

    # Arrange
    master = PersonPydantic(name="Chief", age=99, gender=GenderPydantic.OTHER)
    person = PersonPydantic(name="John", age=25, gender=GenderPydantic.MALE)
    person2 = PersonPydantic(name="Jane", age=25, gender=GenderPydantic.FEMALE)
    pet1 = PetPydantic(name="Rex", age=5, species="Dog")
    pet2 = PetPydantic(name="Whiskers", age=3, species="Cat")
    pet3 = PetPydantic(name="Tweety", age=2, species="Bird")
    family = FamilyPydantic(
        members=[person, person2],
        name="Doe",
        pets={"dog": pet1, "cat": pet2, "bird": pet3},
        master=master,
    )
    clan = ClanPydantic(families=[family], name="Smith")

    # Act
    mapper = Mapper()
    mapper.add_custom_mapping(PersonPydantic, "gender", "genero")
    mapped_clan = mapper.map(clan, ClanDataclass)

    # Assert
    assert isinstance(mapped_clan, ClanDataclass)
    assert isinstance(mapped_clan.families[0], FamilyDataclass)
    assert isinstance(mapped_clan.families[0].members[0], PersonDataclass)
    assert isinstance(mapped_clan.families[0].members[0].genero, GenderDataclass)
    assert mapped_clan.families[0].members[0].genero == GenderDataclass.MALE
    assert isinstance(mapped_clan.families[0].pets["dog"], PetDataclass)


def test_pydantic_to_basic():

    # Arrange
    master = PersonPydantic(name="Chief", age=99, gender=GenderPydantic.OTHER)
    person = PersonPydantic(name="John", age=25, gender=GenderPydantic.MALE)
    person2 = PersonPydantic(name="Jane", age=25, gender=GenderPydantic.FEMALE)
    pet1 = PetPydantic(name="Rex", age=5, species="Dog")
    pet2 = PetPydantic(name="Whiskers", age=3, species="Cat")
    pet3 = PetPydantic(name="Tweety", age=2, species="Bird")
    family = FamilyPydantic(
        members=[person, person2],
        name="Doe",
        pets={"dog": pet1, "cat": pet2, "bird": pet3},
        master=master,
    )
    clan = ClanPydantic(families=[family], name="Smith")

    # Act
    mapper = Mapper()
    mapped_clan = mapper.map(clan, Clan)

    # Assert
    assert isinstance(mapped_clan, Clan)
    assert isinstance(mapped_clan.families[0], Family)
    assert isinstance(mapped_clan.families[0].members[0], Person)
    assert isinstance(mapped_clan.families[0].members[0].gender, Gender)
    assert mapped_clan.families[0].members[0].gender == Gender.MALE
    assert isinstance(mapped_clan.families[0].pets["dog"], Pet)
