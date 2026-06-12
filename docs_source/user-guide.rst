================
User Guide
================

Object automapper based on type hints.

Installation
============

.. code-block:: bash

   pip install advanced-automapper
   # or with uv:
   uv add advanced-automapper

PynamoDB support requires the optional extra:

.. code-block:: bash

   pip install "advanced-automapper[pynamodb]"
   # or with uv:
   uv add "advanced-automapper[pynamodb]"

Get started
===========

Both origin and destination classes must expose their fields via Python type
hints.  Create a single ``Mapper`` instance at application startup and reuse
it throughout:

.. code-block:: python

   from automapper import Mapper

   def build_mapper() -> Mapper:
       m = Mapper()
       m.add_custom_mapping(PersonORM, "full_name", "name")
       return m

   # Create once, reuse everywhere
   mapper = build_mapper()

Map a Pydantic model to a SQLAlchemy model:

.. code-block:: python

   mapped_person = mapper.map(person_pydantic, PersonAlchemy)
   print(mapped_person)

Add custom mapping
==================

PyAutomapper allows mapping fields with different names using
``add_custom_mapping``.  If the SQLAlchemy model has ``genero`` instead of
``gender``:

.. code-block:: python

   from automapper import Mapper

   mapper = Mapper()
   mapper.add_custom_mapping(PersonPydantic, "gender", "genero")

   mapped_person = mapper.map(person, PersonAlchemy)
   print(mapped_person)

PynamoDB support
================

``advanced-automapper`` ships with built-in support for mapping from and to
`PynamoDB <https://pynamodb.readthedocs.io/>`_ models.  Install the optional
extra first (see *Installation* above).

Define your PynamoDB model with Python type annotations alongside the
attribute declarations.  The annotations allow the mapper to use the model as
a *target* (bidirectional mapping):

.. code-block:: python

   from pynamodb.models import Model
   from pynamodb.attributes import UnicodeAttribute, NumberAttribute, BooleanAttribute

   class PersonModel(Model):
       class Meta:
           table_name = "persons"
           region = "us-east-1"

       # Python type annotations enable bidirectional mapping
       email: str = UnicodeAttribute(hash_key=True)
       name: str = UnicodeAttribute(null=True)
       age: float = NumberAttribute(null=True)
       active: bool = BooleanAttribute(null=True)

Map **from** a PynamoDB instance to a domain dataclass:

.. code-block:: python

   import dataclasses
   from automapper import Mapper

   @dataclasses.dataclass
   class PersonDomain:
       email: str = ""
       name: str = ""
       age: float = 0.0
       active: bool = False

   mapper = Mapper()
   # Read item from DynamoDB, then convert to domain object
   db_item = PersonModel.get("john@example.com")
   domain_obj = mapper.map(db_item, PersonDomain)

Map **to** a PynamoDB model (useful when writing to DynamoDB from a domain
object):

.. code-block:: python

   domain_obj = PersonDomain(
       email="alice@example.com",
       name="Alice",
       age=28.0,
       active=True,
   )
   db_item = mapper.map(domain_obj, PersonModel)
   db_item.save()

Field introspection for PynamoDB sources uses ``Model.get_attributes()``,
which returns only the DynamoDB attributes declared on the model class.
PynamoDB's internal bookkeeping fields are automatically excluded.

FastAPI / lifespan example
==========================

Create and configure the mapper once during application startup so it is
effectively immutable during request handling:

.. code-block:: python

   from contextlib import asynccontextmanager
   from typing import Annotated
   from fastapi import FastAPI, Depends
   from automapper import Mapper

   _mapper: Mapper | None = None

   def get_mapper() -> Mapper:
       assert _mapper is not None, "Mapper not initialised"
       return _mapper

   MapperDep = Annotated[Mapper, Depends(get_mapper)]

   @asynccontextmanager
   async def lifespan(app: FastAPI):
       global _mapper
       _mapper = Mapper()
       _mapper.add_custom_mapping(PersonModel, "email", "user_id")
       yield
       _mapper = None

   app = FastAPI(lifespan=lifespan)

   @app.get("/persons/{email}")
   async def get_person(email: str, mapper: MapperDep) -> PersonDomain:
       db_item = PersonModel.get(email)
       return mapper.map(db_item, PersonDomain)

Testing
=======

Create a fresh ``Mapper`` per test to prevent mapping state from leaking
between tests:

.. code-block:: python

   def test_map_person():
       m = Mapper()  # fresh instance — no shared state
       m.add_custom_mapping(PersonModel, "email", "username")
       db_item = PersonModel(email="test@example.com", name="Test")
       result = m.map(db_item, PersonDomain)
       assert result.email == "test@example.com"

More examples
=============

The ``tests/`` folder in the repository contains mapping examples for all
supported types: Pydantic, dataclasses, plain Python classes, SQLAlchemy ORM
models, and PynamoDB models.
