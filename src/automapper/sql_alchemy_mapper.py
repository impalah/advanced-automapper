from typing import Any, Dict, Type, get_type_hints

from sqlalchemy.orm import class_mapper

from automapper.functions import is_sqlalchemy
from automapper.mapping_plugin import MappingPlugin
from automapper.types import TSource, TTarget


class SqlAlchemyMapper(MappingPlugin):
    """SqlAlchemy plugin for the mapping

    Args:
        MappingPlugin (_type_): _description_
    """

    def get_parent_classes(self, cls):
        parents = []
        for base in cls.__bases__:
            parents.append(base)
            parents.extend(self.get_parent_classes(base))
        return parents

    def can_handle(self, source: TSource, target: TTarget) -> bool:

        return is_sqlalchemy(source)

        # return isinstance(source, DeclarativeMeta)

    def get_source_fields(self, source: Any) -> Dict[str, Type]:

        return get_type_hints(type(source))
        # return {key: value for key, value in source.__mapper__.c.items()}
