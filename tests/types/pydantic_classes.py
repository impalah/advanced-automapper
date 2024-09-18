from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel


class GenderPydantic(Enum):
    MALE = 1
    FEMALE = 2
    FURRY = 3
    OTHER = 4


class PersonPydantic(BaseModel):
    name: str
    age: int
    gender: GenderPydantic


class PetPydantic(BaseModel):
    name: str
    age: int
    species: str


class FamilyPydantic(BaseModel):
    master: PersonPydantic
    members: List[PersonPydantic]
    name: str
    pets: Optional[Dict[str, PetPydantic]] = {}


class ClanPydantic(BaseModel):
    families: List[FamilyPydantic]
    name: str
