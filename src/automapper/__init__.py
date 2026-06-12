"""advanced-automapper — object mapper based on type hints.

Quick start
-----------
Create a ``Mapper`` instance **once** at application startup and reuse it:

.. code-block:: python

    from automapper import Mapper

    # Configure once — typically in a factory / DI container / lifespan hook
    def build_mapper() -> Mapper:
        m = Mapper()
        m.add_custom_mapping(PersonORM, "full_name", "name")
        return m

    app_mapper = build_mapper()

    # Use anywhere
    person = app_mapper.map(orm_person, PersonDomain)

FastAPI / lifespan example
--------------------------
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
        _mapper.add_custom_mapping(CourseORM, "created_by", "owner_id")
        yield
        _mapper = None

Testing
-------
Create a fresh ``Mapper`` per test to avoid mapping leakage:

.. code-block:: python

    def test_something():
        m = Mapper()
        m.add_custom_mapping(SomeSource, "old_field", "new_field")
        result = m.map(source_obj, TargetClass)
        assert result.new_field == source_obj.old_field
"""

from .default_mapper import DefaultMapper
from .mapper import Mapper
from .mapping_plugin import MappingPlugin
from .pynamodb_mapper import PynamoDBMapper
from .sql_alchemy_mapper import SqlAlchemyMapper

__all__ = [
    "Mapper",
    "MappingPlugin",
    "SqlAlchemyMapper",
    "PynamoDBMapper",
    "DefaultMapper",
]

