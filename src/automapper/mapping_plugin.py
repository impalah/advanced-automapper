from abc import ABC, abstractmethod
from typing import Dict, Type

from automapper.types import TSource, TTarget


class MappingPlugin(ABC):
    """Defines the interface for a mapping plugin

    Args:
        ABC (_type_): _description_
    """

    @abstractmethod
    def can_handle(self, source: TSource, target: TTarget) -> bool:
        """Determines if the plugin can handle the mapping

        Args:
            source (TSource): type of the source object
            target (TTarget): type of the target object

        Returns:
            bool: _description_
        """
        pass

    @abstractmethod
    def get_source_fields(self, source: TSource) -> Dict[str, Type]:
        """Returns the fields of the source object

        Args:
            source (TSource): type of the source object

        Returns:
            Dict[str, Type]: _description_
        """
        pass
