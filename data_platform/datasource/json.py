"""data source class for json as example of DocDataSource."""

import json
from pathlib import Path
from typing import Dict, Iterable, List, NoReturn, Optional, Set, Text, Tuple, Union, overload

from ..config import ConfigManager
from ..document import Document, DocumentSet
from .abc.doc import DocDataSource, DocFactory, DocKeyPair, DocKeyType, DocValDict
from .exception import NotSupportedError


class JSONDS(DocDataSource):
    """DocDataSource using JSON and in-memory dict as data storage.

    support multi-docsets (specify "docset_id" in key)
    """

    _default_doc_key = ('_default', '_default')
    _wildcard_doc_key = ('@*', '@*')

    def __init__(self, config: ConfigManager, *args, **kwargs) -> None:
        super().__init__(config, *args, **kwargs)

        _loc = config.check_get(["init", "location"])
        path_loc = Path(_loc)

        if path_loc.is_dir():
            self._loc = path_loc
        else:
            self._loc = path_loc.parent

        self._config = config
        self._data: Dict[Text, Dict] = {}
        self._dirty_bits: Set[Text] = set()

        self._load()

    def __del__(self) -> None:
        self.flush()

    def _dump(self) -> None:
        """Dump in-memory data into local file."""
        for docset in self._dirty_bits.copy():
            jsonfile = self._loc / (docset + '.json')
            if docset not in self._data:
                if jsonfile.exists():
                    jsonfile.unlink()
            else:
                with jsonfile.open('w') as f:
                    json.dump(self._data[docset], f)

            self._dirty_bits.remove(docset)

    def _load(self) -> None:
        """Load local file into memory."""
        self._data.clear()
        self._dirty_bits.clear()

        for json_file in self._loc.glob('*.json'):  # type: Path
            with json_file.open('r') as f:
                self._data[json_file.stem] = json.load(f)

    def _filter(self, key: DocKeyType) -> List[DocKeyPair]:
        ds_d_c: List[Tuple] = []

        if isinstance(key, tuple):
            ds_d_c.append((key[0], key[1], None))

        if isinstance(key, list):
            for ds, d in key:
                ds_d_c.append((ds, d, None))

        if isinstance(key, dict):
            for (ds, d), c in key.items():
                ds_d_c.append((ds, d, c))

        result = set()
        for docset_name, doc_name, _ in ds_d_c:
            is_docset_wildcard = docset_name.startswith('@*')
            is_doc_wildcard = doc_name.startswith('@*')
            has_wildcard = is_docset_wildcard or is_doc_wildcard
            if has_wildcard:
                docsets: Iterable
                if is_docset_wildcard:
                    docsets = self._data.keys()
                    # TODO: docset wildcards and filters
                else:
                    docsets = [docset_name]

                for ds_name in docsets:
                    if is_doc_wildcard:
                        for d_name in self._data[ds_name]:
                            # TODO: doc wildcards and filters
                            result.add(DocKeyPair(ds_name, d_name))
                    else:
                        result.add(DocKeyPair(ds_name, doc_name))
            else:
                result.add(DocKeyPair(docset_name, doc_name))

        return list(result)

    def flush(self) -> None:
        """Write pending edit to disk files."""
        self._dump()

    def reload(self) -> None:
        """Force reload disk files into memory."""
        self.flush()
        self._load()

    def clear(self) -> None:
        """Clean in-memory and local files."""
        self._dirty_bits.update(self._data.keys())
        self._data.clear()
        self.flush()

    def query(self, query: str, *args, **kwargs) -> NoReturn:
        raise NotSupportedError("JSON data source has no query method.")

    def create_doc(self, key: DocKeyType = ('_default', '_default'), val: DocValDict = {}) -> List[DocKeyPair]:
        """Create doc in data source."""
        result = []
        target = self._filter(key)

        for ds, d in target:
            if ds not in self._data:
                self._data[ds] = {}
            self._data[ds][d] = val
            result.append(DocKeyPair(ds, d))
            self._dirty_bits.add(ds)

        return result

    # pylint: disable=function-redefined
    # flake8: noqa: F811
    @overload
    def read_doc(self, key: DocKeyType) -> Dict[DocKeyPair, DocValDict]:
        ...

    @overload
    def read_doc(self, key: DocKeyType, doc_factory: DocFactory) -> DocumentSet:
        ...

    def read_doc(self, key: DocKeyType = ('@*', '@*'), doc_factory: Optional[DocFactory] = None) -> Union[Dict[DocKeyPair, DocValDict], DocumentSet]:
        target = self._filter(key)
        result: Dict[DocKeyPair, DocValDict] = {}
        for ds, d in target:
            if ds in self._data:
                if d in self._data[ds]:
                    result[DocKeyPair(ds, d)] = self._data[ds][d]

        if doc_factory is not None:
            return DocumentSet({kp: doc_factory.pack(d) for kp, d in result.items()})

        return result

    def update_doc(self, key: DocKeyType = ('_default', '_default'), val: DocValDict = {}) -> List[DocKeyPair]:
        result = []
        target = self._filter(key)

        for ds, d in target:
            if ds not in self._data:
                self._data[ds] = {}
            if d not in self._data[ds]:
                self._data[ds][d] = {}
            self._data[ds][d].update(val)
            result.append(DocKeyPair(ds, d))
            self._dirty_bits.add(ds)

        return result

    def delete_doc(self, key: DocKeyType = ('_default', '_default')) -> int:
        result = 0
        target = self._filter(key)

        for ds, d in target:
            if ds in self._data:
                if d in self._data[ds]:
                    del self._data[ds][d]
                    result += 1
                    self._dirty_bits.add(ds)

        return result
