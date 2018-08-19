"""Packages for data source classes
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type, Union

import networkx as nx

from ..config import ConfigManager


class BaseDataSource(ABC):
    """abstract base class for all data sources.
    """

    def __init__(self, config: ConfigManager, *args, **kwargs) -> None:
        self._source = config
        self._init_args = args
        self._init_kwargs = kwargs

    @property
    def source(self) -> Any:
        """get the current data source
        """
        return self._source

    @abstractmethod
    def query(self, query: str, data: Dict) -> Any:
        pass


class DocDataSource(BaseDataSource):
    @abstractmethod
    def create_doc(self, key: Dict, val: Dict) -> List:
        pass

    @abstractmethod
    def read_doc(self, key: Dict) -> Dict:
        pass

    @abstractmethod
    def update_doc(self, key: Dict, val: Dict) -> List:
        pass

    @abstractmethod
    def delete_doc(self, key: Dict) -> int:
        pass


class GraphDataSource(BaseDataSource):
    @abstractmethod
    def create_graph(self, key: Dict, val: Dict) -> List:
        pass

    @abstractmethod
    def create_node(self, key: Dict, val: Dict) -> List:
        pass

    @abstractmethod
    def create_edge(self, key: Dict, val: Dict) -> List:
        pass

    @abstractmethod
    def read_graph(
            self, key: Dict
    ) -> Union[nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]:
        pass

    @abstractmethod
    def read_node(self, key: Dict) -> Dict:
        pass

    @abstractmethod
    def read_edge(self, key: Dict) -> Dict:
        pass

    @abstractmethod
    def update_graph(self, key: Dict, val: Dict) -> List:
        pass

    @abstractmethod
    def update_node(self, key: Dict, val: Dict) -> List:
        pass

    @abstractmethod
    def update_edge(self, key: Dict, val: Dict) -> List:
        pass

    @abstractmethod
    def delete_graph(self, key: Dict) -> int:
        pass

    @abstractmethod
    def delete_node(self, key: Dict) -> int:
        pass

    @abstractmethod
    def delete_edge(self, key: Dict) -> int:
        pass


class RowDataSource(BaseDataSource):
    @abstractmethod
    def create_row(self, key: Dict, val: Dict) -> List:
        pass

    @abstractmethod
    def read_row(self, key: Dict) -> Dict:
        pass

    @abstractmethod
    def update_row(self, key: Dict, val: Dict) -> List:
        pass

    @abstractmethod
    def delete_row(self, key: Dict) -> int:
        pass


class DataSourceFactory():
    _registered: Dict[str, Type[BaseDataSource]] = {}

    @staticmethod
    def register(type_: str, cls: Type[BaseDataSource]) -> None:
        DataSourceFactory._registered[type_] = cls

    @staticmethod
    def unregister(type_: str) -> None:
        if type_ in DataSourceFactory._registered:
            del DataSourceFactory._registered[type_]
        else:
            raise KeyError(f"{type_} is not registered.")

    @staticmethod
    def init(config: ConfigManager, *args, **kwargs) -> BaseDataSource:
        # may change type to some class in D-M4 config,
        # but dict APIs stay the same
        """build DataSource based on config
        """
        _pre_init = config.get("_pre_init")

        if _pre_init is None:
            raise ValueError("There is no _pre_init in config.")

        type_ = _pre_init.get("type")
        if type_:
            if type_ in DataSourceFactory._registered:
                return DataSourceFactory._registered[type_](config, *args,
                                                            **kwargs)
            else:
                raise TypeError(f"{type_} is not registered.")
        raise ValueError(f'"type" is not included in config.')


class NotSupportedError(Exception):
    """Indicate that the method is not supported in this data source.
    """
    pass
