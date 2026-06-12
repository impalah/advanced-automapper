# advanced-automapper

Object automapper based on type hints.

## Installation

```bash
pip install advanced-automapper
# or with uv:
uv add advanced-automapper
```

## Instantiation pattern

Each `Mapper` instance owns its state independently (plugin list and custom
field renames). **Never share a `Mapper` across tests** — create a fresh
instance per test to prevent mapping leakage.

For production use, create and configure a **single instance at application
startup** and reuse it throughout:

```python
from automapper import Mapper

def build_mapper() -> Mapper:
    m = Mapper()
    m.add_custom_mapping(PersonORM, "full_name", "name")
    return m

app_mapper = build_mapper()  # configure once, reuse everywhere
```

### FastAPI / lifespan example

```python
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, Depends
from automapper import Mapper

_mapper: Mapper | None = None

def get_mapper() -> Mapper:
    assert _mapper is not None
    return _mapper

MapperDep = Annotated[Mapper, Depends(get_mapper)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _mapper
    _mapper = Mapper()
    _mapper.add_custom_mapping(CourseORM, "created_by", "owner_id")
    yield
    _mapper = None

app = FastAPI(lifespan=lifespan)
```

### Testing

```python
def test_mapping():
    m = Mapper()  # fresh instance — no shared state with other tests
    m.add_custom_mapping(PersonORM, "full_name", "name")
    result = m.map(orm_obj, PersonDomain)
    assert result.name == orm_obj.full_name
```

It is important to note that PyAutomapper requieres that both origin and destination classes have have type hints to define the type for every field.

Let's say you have a Pydantic model called Person, and you need to map it to a SqlAlchmey model to save it to a database:

```python

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship


class GenderPydantic(Enum):
    MALE = 1
    FEMALE = 2
    FURRY = 3
    OTHER = 4

class PersonPydantic(BaseModel):
    name: str
    age: int
    gender: GenderPydantic



Base = declarative_base()


class GenderAlchemy(Enum):
    MALE = 1
    FEMALE = 2
    FURRY = 3
    OTHER = 4

class PersonAlchemy(Base):
    __tablename__ = "persons"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[GenderAlchemy] = mapped_column(
        SqlEnum(GenderAlchemy), nullable=False
    )

    def __repr__(self):
        return f"<PersonAlchemy(name='{self.name}', age={self.age}, gender='{self.gender}')>"

# Create a person
person = PersonPydantic(name="John", age=25, gender=GenderPydantic.MALE)


```

To create a PersonAlchemy object:

```python
from automapper import mapper

mapped_person = mapper.map(person, PersonAlchemy)

print(mapped_person)

```

## Add custom mapping

PyAutomapper allows to map fields with different names between them using custom mapping.

Imagine that, in the previous SqlAlchemy class the gender field is called "genero":

```python

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship


class GenderPydantic(Enum):
    MALE = 1
    FEMALE = 2
    FURRY = 3
    OTHER = 4

class PersonPydantic(BaseModel):
    name: str
    age: int
    gender: GenderPydantic



Base = declarative_base()


class GenderAlchemy(Enum):
    MALE = 1
    FEMALE = 2
    FURRY = 3
    OTHER = 4

class PersonAlchemy(Base):
    __tablename__ = "persons"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    age: Mapped[int] = mapped_column(Integer)
    # Let's rename this field
    genero: Mapped[GenderAlchemy] = mapped_column(
        SqlEnum(GenderAlchemy), nullable=False
    )

    def __repr__(self):
        return f"<PersonAlchemy(name='{self.name}', age={self.age}, gender='{self.gender}')>"

# Create a person
person = PersonPydantic(name="John", age=25, gender=GenderPydantic.MALE)

```

The solution is to add a cutom mapping in the Mapper relating the field "gender", in the source class, with "genero" in the target.

```python

from automapper import mapper

mapper.add_custom_mapping(PersonPydantic, "gender", "genero")

mapped_person = mapper.map(person, PersonAlchemy)

print(mapped_person)

```

## More examples

The tests folder in the code repository contains examples of mapping between different python objects.
