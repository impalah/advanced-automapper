from typing import Any, Dict, Type

from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import DeclarativeMeta

from automapper.mapping_plugin import MappingPlugin
from automapper.types import TSource, TTarget


class SqlAlchemyMapper(MappingPlugin):
    """SqlAlchemy plugin for the mapping

    Args:
        MappingPlugin (_type_): _description_
    """

    def can_handle(self, source: TSource, target: TTarget) -> bool:
        return isinstance(source, DeclarativeMeta)

    def get_source_fields(self, source: Any) -> Dict[str, Type]:
        return {key: value for key, value in source.__mapper__.c.items()}
