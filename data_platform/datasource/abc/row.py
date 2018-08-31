from abc import abstractmethod
from typing import Any, Dict, List, NamedTuple, Text, Union

from . import BaseDataSource, ConditionDict


class RowKeyPair(NamedTuple):
    table_name: Text
    row_name: Text


RowKeyList = List[RowKeyPair]
RowKeyDict = Dict[RowKeyPair, ConditionDict]
RowKeyType = Union[RowKeyPair, RowKeyList, RowKeyDict]
RowValDict = Dict[Text, Any]


class RowDataSource(BaseDataSource):
    @abstractmethod
    def create_row(self, key: RowKeyType, val: RowValDict) -> List[RowKeyPair]:
        pass

    @abstractmethod
    def read_row(self, key: RowKeyType) -> Dict[RowKeyPair, RowValDict]:
        pass

    @abstractmethod
    def update_row(self, key: RowKeyType, val: RowValDict) -> List[RowKeyPair]:
        pass

    @abstractmethod
    def delete_row(self, key: RowKeyType) -> int:
        pass
