from abc import ABC, abstractmethod
from typing import Any, Dict, Text

from ...config import ConfigManager

ConditionDict = Dict[Text, Any]


class BaseDataSource(ABC):
    """Abstract base class for all data sources."""

    def __init__(self, config: ConfigManager, *args, **kwargs) -> None:
        self._config = config
        self._init_args = args
        self._init_kwargs = kwargs

    @property
    def config(self) -> ConfigManager:
        """Get the current config manager."""
        return self._config

    @abstractmethod
    def query(self, query: Text, *args, **kwargs) -> Any:
        """Run query on data source."""
        pass
