from typing import Dict, Optional, Type, Union, get_args, get_type_hints

from sqlalchemy.orm import Mapped


def get_inner_type(type_hint: Type) -> Type:
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


def is_generic_list(type_hint: Type) -> bool:
    """Check if the type hint is a generic list

    Args:
        type_hint (Type): _description_

    Returns:
        bool: _description_
    """

    # TODO: specialize this method to handle sqlalchemy.orm.Mapped

    is_list = False

    if hasattr(type_hint, "__origin__"):
        is_origin_list = type_hint.__origin__ == list
        is_mapped_list = (
            type_hint.__origin__ == Mapped
            and len(type_hint.__args__) > 0
            and type_hint.__args__[0].__origin__ == list
        )
        is_list = is_origin_list or is_mapped_list

    return is_list


def is_generic_dict(type_hint: Type) -> bool:
    """Check if the type hint is a generic dict

    Args:
        type_hint (Type): _description_

    Returns:
        bool: _description_
    """

    return hasattr(type_hint, "__origin__") and type_hint.__origin__ == dict


def get_fields_type(target_class: Type) -> Dict[str, Type]:
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
