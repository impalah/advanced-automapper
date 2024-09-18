import dataclasses
from enum import Enum
from typing import Dict, List, Optional


class GenderDataclass(Enum):
    MALE = 1
    FEMALE = 2
    FURRY = 3
    OTHER = 4


@dataclasses.dataclass
class PersonDataclass:
    name: str
    age: int
    genero: GenderDataclass


@dataclasses.dataclass
class PetDataclass:
    name: str
    age: int
    species: str


@dataclasses.dataclass
class FamilyDataclass:
    master: PersonDataclass
    members: List[PersonDataclass]
    name: str
    pets: Optional[Dict[str, PetDataclass]] = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class ClanDataclass:
    families: List[FamilyDataclass]
    name: str
