"""data source class for json as example of DocDataSource
"""

import json
from pathlib import Path
from typing import Dict, Iterable, List, NoReturn, Set, Tuple, Union

from . import base as _base
from ..config import ConfigManager

_DOC_KEY_T = Tuple[str, str]
_DOC_KEY_UT = Union[Dict[_DOC_KEY_T, Dict], List[_DOC_KEY_T], _DOC_KEY_T]


class JSONDS(_base.DocDataSource):
    """DocDataSource using JSON and in-memory dict as data storage

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
        self._data: Dict[str, Dict] = {}
        self._dirty_bits: Set[str] = set()

        self._load()

    def __del__(self) -> None:
        self.flush()

    def _dump(self) -> None:
        """dump in-memory data into local file
        """
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
        """load local file into memory
        """
        self._data.clear()
        self._dirty_bits.clear()

        for json_file in self._loc.glob('*.json'):  # type: Path
            with json_file.open('r') as f:
                self._data[json_file.stem] = json.load(f)

    def _filter(self, key: _DOC_KEY_UT) -> List[_DOC_KEY_T]:
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
        for docset_name, doc_name, conditions in ds_d_c:
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
                            result.add((ds_name, d_name))
                    else:
                        result.add((ds_name, doc_name))
            else:
                result.add((docset_name, doc_name))

        return list(result)

    def flush(self) -> None:
        """Write pending edit to disk files.
        """
        self._dump()

    def reload(self) -> None:
        """Force reload disk files into memory.
        """
        self.flush()
        self._load()

    def clear(self) -> None:
        """Clean in-memory and local files
        """
        self._dirty_bits.update(self._data.keys())
        self._data.clear()
        self.flush()

    def query(self, query: str, data: Dict) -> NoReturn:
        raise _base.NotSupportedError("JSON data source has no query method.")

    def create_doc(self, key: _DOC_KEY_UT = _default_doc_key, val: Dict = {}) -> List[_DOC_KEY_T]:
        """Create doc in data source
        """
        result = []
        target = self._filter(key)

        for ds, d in target:
            if ds not in self._data:
                self._data[ds] = {}
            self._data[ds][d] = val
            result.append((ds, d))
            self._dirty_bits.add(ds)

        return result

    def read_doc(self, key: _DOC_KEY_UT = _wildcard_doc_key) -> Dict[_DOC_KEY_T, Dict]:
        target = self._filter(key)
        result = {}
        for ds, d in target:
            if ds in self._data:
                if d in self._data[ds]:
                    result[(ds, d)] = self._data[ds][d]

        return result

    def update_doc(self, key: _DOC_KEY_UT = _default_doc_key, val: Dict = {}) -> List[_DOC_KEY_T]:
        result = []
        target = self._filter(key)

        for ds, d in target:
            if ds not in self._data:
                self._data[ds] = {}
            if d not in self._data[ds]:
                self._data[ds][d] = {}
            self._data[ds][d].update(val)
            result.append((ds, d))
            self._dirty_bits.add(ds)

        return result

    def delete_doc(self, key: _DOC_KEY_UT = _default_doc_key) -> int:
        result = 0
        target = self._filter(key)

        for ds, d in target:
            if ds in self._data:
                if d in self._data[ds]:
                    del self._data[ds][d]
                    result += 1
                    self._dirty_bits.add(ds)

        return result


_base.DataSourceFactory.register("json", JSONDS)
