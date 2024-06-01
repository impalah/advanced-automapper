# advanced-automapper

Object automapper based on type hints.


## Installation

Using pip:

```bash
pip install advanced-automapper
```

Using poetry

```bash
poetry advanced-automapper
```


## Get started

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
from automapper import Mapper

mapper = Mapper()
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

from automapper import Mapper

mapper = Mapper()
mapper.add_custom_mapping(PersonPydantic, "gender", "genero")

mapped_person = mapper.map(person, PersonAlchemy)

print(mapped_person)

```

## More examples

The tests folder in the code repository contains examples of mapping between different python objects.


