"""Mapping plugin for PynamoDB models.

This module is safe to import even when pynamodb is not installed: all
pynamodb imports are deferred to method bodies and guarded with
``try/except ImportError``.

Install the optional extra to use this plugin::

    pip install advanced-automapper[pynamodb]
    # or
    uv add "advanced-automapper[pynamodb]"
"""

from datetime import datetime
from decimal import Decimal
from typing import Any

from automapper.functions import is_pynamodb
from automapper.mapping_plugin import MappingPlugin
from automapper.types import TSource, TTarget


def _pynamodb_attr_to_python_type(attr: Any) -> type:
    """Return the closest Python native type for a PynamoDB Attribute instance.

    The mapping covers the most common attribute types.  Unknown attribute
    types fall back to ``object``.

    Args:
        attr: A ``pynamodb.attributes.Attribute`` instance.

    Returns:
        A Python built-in or stdlib type that best represents *attr*.
    """
    try:
        from pynamodb.attributes import (  # noqa: PLC0415
            BinaryAttribute,
            BooleanAttribute,
            ListAttribute,
            MapAttribute,
            NumberAttribute,
            NumberSetAttribute,
            UnicodeAttribute,
            UnicodeSetAttribute,
            UTCDateTimeAttribute,
        )
    except ImportError:
        return object

    _type_map: list[tuple[type, type]] = [
        (UnicodeAttribute, str),
        (NumberAttribute, Decimal),
        (BooleanAttribute, bool),
        (UTCDateTimeAttribute, datetime),
        (ListAttribute, list),
        (MapAttribute, dict),
        (UnicodeSetAttribute, set),
        (NumberSetAttribute, set),
        (BinaryAttribute, bytes),
    ]
    for attr_cls, python_type in _type_map:
        if isinstance(attr, attr_cls):
            return python_type
    return object


class PynamoDBMapper(MappingPlugin):
    """Mapping plugin that handles PynamoDB ``Model`` instances as source.

    Field introspection is performed via ``Model.get_attributes()``, which
    returns only the DynamoDB attributes explicitly declared on the model
    class (partition key, sort key and all non-key attributes).  This
    avoids picking up PynamoDB's internal bookkeeping attributes that appear
    in ``get_type_hints()``.

    The plugin is registered in the default ``Mapper`` plugin stack
    automatically.  If pynamodb is not installed, :meth:`can_handle` always
    returns ``False`` so the plugin is silently bypassed by the next plugin
    in the chain (``DefaultMapper``).

    Example — mapping FROM a PynamoDB model:

    .. code-block:: python

        from automapper import Mapper

        mapper = Mapper()
        domain_obj = mapper.map(dynamodb_item, CourseRead)

    Example — mapping TO a PynamoDB model (target must have Python type
    annotations on its attributes):

    .. code-block:: python

        from automapper import Mapper

        mapper = Mapper()
        item = mapper.map(domain_obj, CourseModel)

    Custom field renames work identically to every other plugin:

    .. code-block:: python

        mapper.add_custom_mapping(CourseModel, "pk", "course_id")
        domain_obj = mapper.map(dynamodb_item, CourseRead)

    Requires the ``pynamodb`` optional extra::

        pip install advanced-automapper[pynamodb]
    """

    def can_handle(self, source: TSource, target: TTarget) -> bool:
        """Return ``True`` if *source* is a PynamoDB Model instance.

        Args:
            source: The source object to inspect.
            target: Unused; present to satisfy the :class:`MappingPlugin`
                interface.

        Returns:
            ``True`` when pynamodb is installed and *source* is an instance
            of ``pynamodb.models.Model``.  ``False`` otherwise (including
            when pynamodb is not installed).
        """
        return is_pynamodb(source)

    def get_source_fields(self, source: Any) -> dict[str, type]:
        """Return ``{field_name: python_type}`` for all DynamoDB attributes.

        Uses ``Model.get_attributes()`` rather than ``get_type_hints`` so
        that PynamoDB's own internal bookkeeping fields are excluded.

        Args:
            source: A PynamoDB ``Model`` instance.

        Returns:
            A dictionary mapping each attribute name to its corresponding
            Python type.
        """
        attributes: dict[str, Any] = type(source).get_attributes()
        return {
            name: _pynamodb_attr_to_python_type(attr)
            for name, attr in attributes.items()
        }
