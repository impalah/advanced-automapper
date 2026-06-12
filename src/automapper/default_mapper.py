from typing import get_type_hints

from automapper.mapping_plugin import MappingPlugin
from automapper.types import TSource, TTarget


class DefaultMapper(MappingPlugin):
    """Default plugin for the mapping

    Args:
        MappingPlugin (_type_): _description_
    """

    def can_handle(self, source: TSource, target: TTarget) -> bool:
        return True

    def get_source_fields(self, source: TSource) -> dict[str, type]:
        return get_type_hints(type(source))
