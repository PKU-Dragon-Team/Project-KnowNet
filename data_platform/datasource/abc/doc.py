from abc import ABC, abstractmethod
from typing import Any, Dict, List, NamedTuple, Optional, Text, Tuple, Union

from . import BaseDataSource, ConditionDict
from ...config import ConfigManager
from ...document import Document, DocumentSet


# Type Definitions for Doc
class DocKeyPair(NamedTuple):
    docset_name: Text
    doc_name: Text


DocKeyList = List[DocKeyPair]
DocKeyDict = Dict[DocKeyPair, ConditionDict]
DocKeyType = Union[DocKeyPair, DocKeyList, DocKeyDict]
DocValDict = Dict[Text, Any]


class DocFactory(ABC):
    @classmethod
    @abstractmethod
    def pack(cls, doc_dict: DocValDict) -> Document:
        pass

    @classmethod
    @abstractmethod
    def unpack(cls, doc: Document) -> DocValDict:
        pass


class DocDataSource(BaseDataSource):
    """Interface of doc-based data sources."""

    def __init__(self, config: ConfigManager, *args, **kwargs) -> None:
        super().__init__(config, *args, **kwargs)

        self._doc_factory: Optional[DocFactory] = None

    @staticmethod
    def _format_doc_key(key: DocKeyType) -> List[Tuple]:
        ds_d_c: List[Tuple] = []
        if isinstance(key, tuple):
            ds_d_c.append((key[0], key[1], None))

        if isinstance(key, list):
            for ds, d in key:
                ds_d_c.append((ds, d, None))

        if isinstance(key, dict):
            for (ds, d), c in key.items():
                ds_d_c.append((ds, d, c))
        return ds_d_c

    @abstractmethod
    def create_doc(self, key: DocKeyType, val: DocValDict) -> List[DocKeyPair]:
        pass

    # Both pylint and flake8 won't recognise @overload for now, so turn-off method redefined checking manually
    # pylint: disable=function-redefined
    # flake8: noqa: F811

    # @overload
    # @abstractmethod
    # def read_doc(self, key: DocKeyType) -> Dict[DocKeyPair, DocValDict]:
    #     ...

    # @overload
    # @abstractmethod
    # def read_doc(self, key: DocKeyType, doc_factory: DocFactory) -> DocumentSet:
    #     ...

    # above is completely commented out at last because pylint will misunderstand the signature of the actual method

    @abstractmethod
    def read_doc(self, key: DocKeyType, doc_factory: Optional[DocFactory] = None) -> Union[Dict[DocKeyPair, DocValDict], DocumentSet]:
        pass

    def bind_doc_factory(self, factory: DocFactory) -> None:
        self._doc_factory = factory

    def unbind_doc_factory(self) -> None:
        self._doc_factory = None

    @abstractmethod
    def update_doc(self, key: DocKeyType, val: DocValDict) -> List[DocKeyPair]:
        pass

    @abstractmethod
    def delete_doc(self, key: DocKeyType) -> int:
        pass
