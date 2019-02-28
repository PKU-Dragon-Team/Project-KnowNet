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
    DEFAULT_DOC_KEY = DocKeyPair('_default', '_default')
    WILDCARD_DOC_KEY = DocKeyPair('@*', '@*')

    def __init__(self, config: ConfigManager, *args, **kwargs) -> None:
        super().__init__(config, *args, **kwargs)

        self._factory: Optional[DocFactory] = None

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

    @abstractmethod
    def read_doc(self, key: DocKeyType = DocKeyPair('@*', '@*')) -> Dict[DocKeyPair, DocValDict]:
        pass

    def bind_doc_factory(self, factory: DocFactory) -> None:
        self._factory = factory

    def unbind_doc_factory(self) -> None:
        self._factory = None

    def read_docset(self, key: DocKeyType = DocKeyPair('@*', '@*'), factory: Optional[DocFactory] = None) -> DocumentSet:
        if factory is not None:
            return DocumentSet({d_k: factory.pack(d) for d_k, d in self.read_doc(key).items()})
        if self._factory is not None:
            return DocumentSet({d_k: self._factory.pack(d) for d_k, d in self.read_doc(key).items()})
        raise AttributeError('There is no factory to form document set!')

    @abstractmethod
    def update_doc(self, key: DocKeyType, val: DocValDict) -> List[DocKeyPair]:
        pass

    @abstractmethod
    def delete_doc(self, key: DocKeyType) -> int:
        pass
