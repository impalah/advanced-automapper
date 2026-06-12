from typing import Optional, Union, get_args, get_type_hints

from sqlalchemy.orm import Mapped


def get_inner_type(type_hint: type) -> type:
    """Get the inner type of a generic type

    Args:
        type_hint (Type): _description_

    Returns:
        Type: _description_
    """

    # TODO: specialize this method to handle sqlalchemy.orm.Mapped
    if (
        hasattr(type_hint, "__origin__")
        and type_hint.__origin__ == Mapped
        and len(type_hint.__args__) > 0
    ):
        return type_hint.__args__[0].__args__[-1]
    else:
        return type_hint.__args__[-1]


def is_generic_list(type_hint: type) -> bool:
    """Check if the type hint is a generic list

    Args:
        type_hint (Type): _description_

    Returns:
        bool: _description_
    """

    # TODO: specialize this method to handle sqlalchemy.orm.Mapped

    is_list = False

    if hasattr(type_hint, "__origin__"):
        is_origin_list = type_hint.__origin__ is list
        is_mapped_list = (
            type_hint.__origin__ is Mapped
            and len(type_hint.__args__) > 0
            and type_hint.__args__[0].__origin__ is list
        )
        is_list = is_origin_list or is_mapped_list

    return is_list


def is_generic_dict(type_hint: type) -> bool:
    """Check if the type hint is a generic dict

    Args:
        type_hint (Type): _description_

    Returns:
        bool: _description_
    """

    return hasattr(type_hint, "__origin__") and type_hint.__origin__ is dict


def get_fields_type(target_class: type) -> dict[str, type]:
    """Return the fields of a class with their types

    Args:
        target_class (Type): _description_

    Returns:
        Dict[str, Type]: _description_
    """

    target_fields = get_type_hints(target_class)
    for field, field_type in target_fields.items():
        # Return the inner type of Optional, Union, Mapped
        # TODO: improve the Optional detection, it's a shortcut for Union[T, None]
        if getattr(field_type, "__origin__", None) in (Optional, Union, Mapped):
            field_type = get_args(field_type)[0]
        target_fields[field] = field_type

    return target_fields


def is_pydantic(obj):
    """Returns True if obj is a pydantic model or an instance of a
    pydantic model."""
    cls = obj if isinstance(obj, type) else type(obj)
    return hasattr(cls, "model_fields")


def is_sqlalchemy(obj):
    """Returns True if obj is a sqlalchemy model or an instance of a
    sqlalchemy model."""
    cls = obj if isinstance(obj, type) else type(obj)
    return hasattr(cls, "__table__")


def is_pynamodb(obj: object) -> bool:
    """Returns True if *obj* is a PynamoDB Model class or instance.

    The check is done by walking the MRO looking for
    ``pynamodb.models.Model``.  If pynamodb is not installed, returns
    ``False`` without raising an error so that this helper is safe to call
    even when the optional ``pynamodb`` extra is not present.

    Args:
        obj: A class or an instance to test.

    Returns:
        True if *obj* is (or is an instance of) a PynamoDB Model.
    """
    try:
        from pynamodb.models import Model  # noqa: PLC0415
    except ImportError:
        return False
    cls = obj if isinstance(obj, type) else type(obj)
    return isinstance(cls, type) and issubclass(cls, Model)
