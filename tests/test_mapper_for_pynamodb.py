"""Tests for mapping from/to PynamoDB models.

Covers:
- PynamoDB instance as source → dataclass target
- PynamoDB instance as source → Pydantic target
- PynamoDB instance as source → plain-class target
- Dataclass as source → PynamoDB target
- Custom field rename (add_custom_mapping) with PynamoDB source
- is_pynamodb helper
- PynamoDBMapper.can_handle / get_source_fields contract

All tests instantiate models in-memory without a DynamoDB connection.
"""

import dataclasses

import pytest
from pydantic import BaseModel

pynamodb = pytest.importorskip(
    "pynamodb", reason="pynamodb not installed; skipping PynamoDB mapper tests"
)

from automapper import Mapper  # noqa: E402
from automapper.functions import is_pynamodb  # noqa: E402
from automapper.pynamodb_mapper import PynamoDBMapper  # noqa: E402

from .types.pynamodb.person_pynamodb import (  # noqa: E402
    FamilyPynamoDB,
    GenderPynamoDB,
    PersonPynamoDB,
)

# ---------------------------------------------------------------------------
# Auxiliary flat types aligned to PersonPynamoDB
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class PersonFlat:
    email: str = ""
    name: str = ""
    age: float = 0.0
    active: bool = False


@dataclasses.dataclass
class PersonFlatRenamed:
    """Target with 'username' instead of 'email' to test custom mapping."""

    username: str = ""
    name: str = ""
    age: float = 0.0
    active: bool = False


@dataclasses.dataclass
class FamilyFlat:
    family_id: str = ""
    name: str = ""
    member_count: float = 0.0


class PersonPydanticFlat(BaseModel):
    """Pydantic model whose fields match PersonPynamoDB exactly."""

    email: str = ""
    name: str = ""
    age: float = 0.0
    active: bool = False


# ---------------------------------------------------------------------------
# Helper / detection tests
# ---------------------------------------------------------------------------


def test_is_pynamodb_with_instance():
    person = PersonPynamoDB(email="test@example.com", name="Test", age=1.0, active=True)
    assert is_pynamodb(person) is True


def test_is_pynamodb_with_class():
    assert is_pynamodb(PersonPynamoDB) is True


def test_is_pynamodb_with_non_pynamodb_instance():
    assert is_pynamodb(PersonFlat()) is False


def test_is_pynamodb_with_plain_dict():
    assert is_pynamodb({}) is False


def test_pynamodb_mapper_can_handle():
    plugin = PynamoDBMapper()
    person = PersonPynamoDB(email="a@b.com", name="A", age=1.0, active=False)
    assert plugin.can_handle(person, None) is True


def test_pynamodb_mapper_cannot_handle_dataclass():
    plugin = PynamoDBMapper()
    assert plugin.can_handle(PersonFlat(), None) is False


def test_pynamodb_mapper_get_source_fields():
    plugin = PynamoDBMapper()
    person = PersonPynamoDB(email="a@b.com", name="A", age=1.0, active=True)
    fields = plugin.get_source_fields(person)
    assert set(fields.keys()) == {"email", "name", "age", "active"}


# ---------------------------------------------------------------------------
# FROM PynamoDB → various targets
# ---------------------------------------------------------------------------


def test_pynamodb_to_dataclass():
    """Map a PynamoDB instance to a dataclass."""
    person = PersonPynamoDB(email="john@example.com", name="John", age=25.0, active=True)

    mapper = Mapper()
    result = mapper.map(person, PersonFlat)

    assert isinstance(result, PersonFlat)
    assert result.email == "john@example.com"
    assert result.name == "John"
    assert result.age == 25.0
    assert result.active is True


def test_pynamodb_to_dataclass_partial_fields():
    """Fields present only in source are dropped; target defaults are kept."""
    family = FamilyPynamoDB(
        family_id="fam-001",
        name="Doe",
        member_count=3.0,
        member_names=["John", "Jane", "Bob"],
    )

    mapper = Mapper()
    result = mapper.map(family, FamilyFlat)

    assert isinstance(result, FamilyFlat)
    assert result.family_id == "fam-001"
    assert result.name == "Doe"
    assert result.member_count == 3.0
    # member_names is not in FamilyFlat — it is silently ignored


def test_pynamodb_to_pydantic():
    """Map a PynamoDB instance to a Pydantic model with matching fields."""
    person = PersonPynamoDB(
        email="jane@example.com", name="Jane", age=30.0, active=False
    )

    mapper = Mapper()
    result = mapper.map(person, PersonPydanticFlat)

    assert isinstance(result, PersonPydanticFlat)
    assert result.email == "jane@example.com"
    assert result.name == "Jane"
    assert result.age == 30.0
    assert result.active is False


def test_pynamodb_to_dataclass_custom_mapping():
    """Custom field rename: PynamoDB 'email' → dataclass 'username'."""
    person = PersonPynamoDB(
        email="alice@example.com", name="Alice", age=28.0, active=True
    )

    mapper = Mapper()
    mapper.add_custom_mapping(PersonPynamoDB, "email", "username")
    result = mapper.map(person, PersonFlatRenamed)

    assert isinstance(result, PersonFlatRenamed)
    assert result.username == "alice@example.com"
    assert result.name == "Alice"


def test_pynamodb_to_dataclass_none_source():
    """Mapping None source returns None without raising."""
    mapper = Mapper()
    result = mapper.map(None, PersonFlat)
    assert result is None


# ---------------------------------------------------------------------------
# TO PynamoDB (PynamoDB as target)
# ---------------------------------------------------------------------------


def test_dataclass_to_pynamodb():
    """Map a dataclass to a PynamoDB model (bidirectional)."""
    flat = PersonFlat(email="bob@example.com", name="Bob", age=40.0, active=True)

    mapper = Mapper()
    result = mapper.map(flat, PersonPynamoDB)

    assert isinstance(result, PersonPynamoDB)
    assert result.email == "bob@example.com"
    assert result.name == "Bob"
    assert result.age == 40.0
    assert result.active is True


def test_pynamodb_roundtrip():
    """Mapping PynamoDB → dataclass → PynamoDB preserves field values."""
    original = PersonPynamoDB(
        email="carol@example.com", name="Carol", age=22.0, active=False
    )

    mapper = Mapper()
    intermediate = mapper.map(original, PersonFlat)
    restored = mapper.map(intermediate, PersonPynamoDB)

    assert restored.email == original.email
    assert restored.name == original.name
    assert restored.age == original.age
    assert restored.active == original.active
