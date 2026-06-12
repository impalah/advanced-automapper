"""PynamoDB model fixtures used in mapping tests.

These models are intentionally minimal: they carry Python type annotations
alongside the PynamoDB attribute declarations so that the automapper can also
use them as *targets* (bidirectional mapping).

The ``Meta.host`` is set to a non-existent local address so that accidental
network calls raise immediately instead of hanging; no DynamoDB connection is
needed to instantiate or read attribute values on a model object.
"""

from enum import Enum

from pynamodb.attributes import (
    BooleanAttribute,
    ListAttribute,
    NumberAttribute,
    UnicodeAttribute,
)
from pynamodb.models import Model


class GenderPynamoDB(Enum):
    MALE = 1
    FEMALE = 2
    FURRY = 3
    OTHER = 4


class PersonPynamoDB(Model):
    """Flat PynamoDB model representing a person.

    Fields intentionally mirror those of the plain-Python and dataclass
    fixtures so that cross-type mapping tests are straightforward.
    """

    class Meta:
        table_name = "persons"
        region = "us-east-1"
        host = "http://localhost:18000"  # local-only; no real DynamoDB needed

    # Python type annotations allow the automapper to use this model as a
    # mapping TARGET via get_type_hints().
    email: str = UnicodeAttribute(hash_key=True)
    name: str = UnicodeAttribute(null=True)
    age: float = NumberAttribute(null=True)
    active: bool = BooleanAttribute(null=True)


class FamilyPynamoDB(Model):
    """Flat PynamoDB model representing a family.

    DynamoDB does not support foreign-key relationships, so member details
    are stored as a list of string names rather than nested objects.
    """

    class Meta:
        table_name = "families"
        region = "us-east-1"
        host = "http://localhost:18000"

    family_id: str = UnicodeAttribute(hash_key=True)
    name: str = UnicodeAttribute(null=True)
    member_count: float = NumberAttribute(null=True)
    member_names: list = ListAttribute(null=True)
