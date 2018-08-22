from abc import ABC, abstractmethod
from typing import Any, Dict, List, NamedTuple, Optional, Text, Union, cast, overload

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

    def unbind_doc_factory(self, factory: DocFactory) -> None:
        self._doc_factory = None

    def read_docset(self, key: DocKeyType) -> DocumentSet:
        if self._doc_factory is None:
            raise AttributeError("No document factory bound, call bind_doc_factory(factory) first.")

        return cast(DocumentSet, self.read_doc(key, self._doc_factory))

    @abstractmethod
    def update_doc(self, key: DocKeyType, val: DocValDict) -> List[DocKeyPair]:
        pass

    @abstractmethod
    def delete_doc(self, key: DocKeyType) -> int:
        pass
