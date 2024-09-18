from enum import Enum
from typing import Dict, List


class Gender(Enum):
    MALE = 1
    FEMALE = 2
    FURRY = 3
    OTHER = 4


class Person:
    def __init__(self, name: str, age: int, gender: Gender):
        self.name = name
        self.age = age
        self.gender = gender

    name: str
    age: int
    gender: Gender

    def __repr__(self) -> str:
        return f"Person(name='{self.name}', age={self.age}, gender={self.gender})"


class Pet:
    def __init__(self, name: str, age: int, species: str):
        self.name = name
        self.age = age
        self.species = species

    name: str
    age: int
    species: str

    def __repr__(self) -> str:
        return f"Pet(name='{self.name}', age={self.age}, species='{self.species}')"


class Family:
    def __init__(
        self,
        members: List[Person],
        name: str,
        master: Person,
        pets: Dict[str, Pet] = {},
    ):
        self.members = members
        self.name = name
        self.pets = pets
        self.master = master

    master: Person
    members: List[Person]
    name: str
    pets: Dict[str, Pet]

    def __repr__(self) -> str:
        return f"Family(name='{self.name}', members={[member for member in self.members]}, pets={self.pets})"


class Clan:
    def __init__(self, families: List[Family], name: str):
        self.families = families
        self.name = name

    families: List[Family]
    name: str

    def __repr__(self) -> str:
        return (
            f"Clan(name='{self.name}', families={[family for family in self.families]})"
        )
