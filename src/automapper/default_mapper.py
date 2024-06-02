from typing import Dict, Type, get_type_hints

from automapper.mapping_plugin import MappingPlugin
from automapper.types import TSource, TTarget


class DefaultMapper(MappingPlugin):
    """Default plugin for the mapping

    Args:
        MappingPlugin (_type_): _description_
    """

    def can_handle(self, source: TSource, target: TTarget) -> bool:
        return True

    def get_source_fields(self, source: TSource) -> Dict[str, Type]:
        return get_type_hints(type(source))
