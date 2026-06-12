from collections.abc import Callable
from dataclasses import is_dataclass
from enum import Enum
from typing import Any

from sqlalchemy.orm import Mapped

from automapper.default_mapper import DefaultMapper
from automapper.functions import (
    get_fields_type,
    get_inner_type,
    is_generic_dict,
    is_generic_list,
    is_pydantic,
    is_pynamodb,
    is_sqlalchemy,
)
from automapper.mapping_plugin import MappingPlugin
from automapper.pynamodb_mapper import PynamoDBMapper
from automapper.sql_alchemy_mapper import SqlAlchemyMapper
from automapper.types import TMapTarget, TSource, TSourceValue


class Mapper:
    """Maps objects from one class to another based on type hints.

    Each ``Mapper`` instance is fully independent: its plugin list and custom
    field mappings are owned by that instance and never shared with others.
    This makes it safe to create multiple instances (e.g. one per test) and to
    configure a single application-wide instance during startup without risk of
    cross-contamination between tests or concurrent workers.

    Typical usage — create once at application startup and reuse:

    .. code-block:: python

        from automapper import Mapper

        # Build and configure once (e.g. in FastAPI lifespan or a DI factory)
        mapper = Mapper()
        mapper.add_custom_mapping(PersonORM, "full_name", "name")

        # Reuse everywhere
        person = mapper.map(orm_obj, PersonDomain)

    For testing, create a fresh instance per test so mappings do not leak:

    .. code-block:: python

        def test_something():
            m = Mapper()
            m.add_custom_mapping(SomeSource, "old_field", "new_field")
            result = m.map(source_obj, TargetClass)
            assert result.new_field == source_obj.old_field
    """

    def __init__(
        self,
        plugins: list[MappingPlugin] | None = None,
    ) -> None:
        """Initialise a new, independent Mapper instance.

        Args:
            plugins: Optional list of :class:`MappingPlugin` instances to use
                for source-field introspection.  When *None* the default plugin
                stack ``[SqlAlchemyMapper(), PynamoDBMapper(), DefaultMapper()]``
                is used.  The ``DefaultMapper`` **must** always be last because
                it acts as a catch-all.
        """
        # Instance-owned plugin list — never shared with other Mapper instances.
        self.mappers: list[MappingPlugin] = (
            plugins
            if plugins is not None
            else [SqlAlchemyMapper(), PynamoDBMapper(), DefaultMapper()]
        )
        # Instance-owned custom field renames — never shared with other instances.
        self.custom_mappings: dict[type, dict[str, str]] = {}

    # ------------------------------------------------------------------
    # Configuration API
    # ------------------------------------------------------------------

    def add_custom_mapping(
        self, source_class: type, source_field: str, target_field: str
    ) -> None:
        """Register a field rename from *source_field* to *target_field*.

        Must be called **before** the first :meth:`map` call for the affected
        source class.  All registrations should happen at application startup
        (e.g. in a ``build_mapper()`` factory) so the instance is effectively
        immutable during request handling.

        Args:
            source_class: The class whose field is being renamed.
            source_field: Name of the field on *source_class*.
            target_field: Name of the corresponding field on the target class.
        """
        if source_class not in self.custom_mappings:
            self.custom_mappings[source_class] = {}
        self.custom_mappings[source_class][source_field] = target_field

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------

    def get_source_fields(self, source: TSource) -> dict[str, type] | None:
        """Return a ``{field_name: type}`` mapping for *source*.

        Iterates the plugin list in order and delegates to the first plugin
        that declares it can handle *source*.

        Args:
            source: An object instance to inspect.

        Returns:
            A dictionary of field names to their resolved types, or ``None``
            if no plugin can handle the source.
        """
        for mapper in self.mappers:
            if mapper.can_handle(source, None):
                return mapper.get_source_fields(source)
        return None

    # ------------------------------------------------------------------
    # Mapping API
    # ------------------------------------------------------------------

    def map(self, source: TSource, target_class: type[TMapTarget]) -> TMapTarget:
        """Map *source* to a new instance of *target_class*.

        Fields present in both *source* and *target_class* are copied by name
        (after applying any registered custom renames).  Fields that exist only
        in *source* are silently dropped; fields that exist only in
        *target_class* keep their default values.

        The mapping is applied recursively: nested dataclasses, Pydantic
        models, SQLAlchemy ORM objects, lists and dicts are all traversed.

        Args:
            source: The source object instance.
            target_class: The class to instantiate with the mapped values.

        Returns:
            A new instance of *target_class* populated with values from *source*.
        """
        if source is None:
            return None  # type: ignore[return-value]

        source_fields: dict[str, type] | None = self.get_source_fields(source)
        if source_fields is None:
            source_fields = {}
        target_fields: dict[str, type] = get_fields_type(target_class)

        target_kwargs: dict[str, Any] = {}

        for field_name, _field_type in source_fields.items():
            target_field_name = self.custom_mappings.get(type(source), {}).get(
                field_name, field_name
            )

            if target_field_name not in target_fields:
                continue

            source_value = getattr(source, field_name, None)
            target_field_type = target_fields[target_field_name]
            target_kwargs[target_field_name] = self._map_field(
                source_value, target_field_type
            )

        return target_class(**target_kwargs)

    def _map_field(self, source_value: TSourceValue, target_field_type: type) -> Any:
        """Return *source_value* converted to *target_field_type*.

        Args:
            source_value: The raw value from the source object.
            target_field_type: The expected type on the target class.

        Returns:
            The converted value, or *source_value* unchanged when no
            conversion is needed.
        """
        type_mapping: dict[Callable[[type], bool], Callable[[Any, type], Any]] = {
            is_generic_list: lambda val, typ: self.map_list(val, get_inner_type(typ)),
            is_generic_dict: lambda val, typ: self.map_dict(val, get_inner_type(typ)),
            lambda t: is_dataclass(t): self.map,
            lambda t: is_pydantic(t): self.map,
            lambda t: is_sqlalchemy(t): self.map,
            lambda t: is_pynamodb(t): self.map,
            lambda _: isinstance(source_value, Enum): self.map_enum,
        }

        for check, func in type_mapping.items():
            if check(target_field_type):
                return func(source_value, target_field_type)

        return source_value

    def map_enum(self, source_value: Enum, target_field_type: type) -> Any:
        """Map an Enum member to the equivalent member of *target_field_type*.

        Matching is done by member **name** so the two Enum classes do not need
        to share the same base type or numeric values.

        Args:
            source_value: The source Enum member.
            target_field_type: The target Enum class (or a ``Mapped[EnumClass]``
                SQLAlchemy annotation).

        Returns:
            The matching target Enum member, or *source_value* unchanged if no
            match is found.
        """
        target_enum_type = self._find_matching_enum(target_field_type, source_value)
        if target_enum_type:
            return getattr(target_enum_type, source_value.name)
        return source_value

    def map_list(self, source_list: list, target_inner_type: type) -> list | None:
        """Map each element of *source_list* to *target_inner_type*.

        Args:
            source_list: A list of source objects.
            target_inner_type: The element type of the target list.

        Returns:
            A new list with each element mapped, or ``None`` if *source_list*
            is ``None``.
        """
        if source_list is None:
            return None
        return [self.map(item, target_inner_type) for item in source_list]

    def map_dict(self, source_dict: dict, target_inner_type: type) -> dict | None:
        """Map each value of *source_dict* to *target_inner_type*.

        Keys are preserved as-is; only values are recursively mapped.

        Args:
            source_dict: A dict whose values are source objects.
            target_inner_type: The value type of the target dict.

        Returns:
            A new dict with mapped values, or ``None`` if *source_dict* is
            ``None``.
        """
        if source_dict is None:
            return None
        return {k: self.map(v, target_inner_type) for k, v in source_dict.items()}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _find_matching_enum(
        self, target_field_type: type, source_value: Enum
    ) -> type[Enum] | None:
        """Return the Enum class that contains *source_value.name*, or ``None``."""
        # Unwrap SQLAlchemy Mapped[EnumClass] if needed
        if (
            hasattr(target_field_type, "__origin__")
            and target_field_type.__origin__ is Mapped
        ):
            target_field_type = target_field_type.__args__[0]
        if isinstance(target_field_type, type) and issubclass(target_field_type, Enum):
            if source_value.name in target_field_type.__members__:
                return target_field_type
        return None

