from typing import Dict, List, Any, Text

from ..config import ConfigManager
from .abc.doc import DocDataSource, DocKeyPair, DocKeyType, DocValDict
from .exception import NotSupportedError

try:
    import pymongo
    from pymongo import MongoClient
except ImportError:
    raise ImportError('This data source requires pymongo to be installed.')


class MongoDBDS(DocDataSource):
    _default_doc_key = DocKeyPair('_default', '_default')
    _wildcard_doc_key = DocKeyPair('@*', '@*')

    def __init__(self, config: ConfigManager, *args, **kwargs) -> None:
        super().__init__(config, *args, **kwargs)

        self._uri: Text = config.check_get(["init", "uri"])
        self._database: Text = config.check_get(["init", "database"])

        self._client: MongoClient = MongoClient(self._uri)
        self._db: pymongo.database.Database = self._client[self._database]

    def __del__(self):
        self._client.close()

    def _filter(self, key: DocKeyType) -> List[DocKeyPair]:
        ds_d_c = self._format_doc_key(key)

        result = set()
        for docset_name, doc_name, _ in ds_d_c:
            is_docset_wildcard = docset_name.startswith('@*')
            is_doc_wildcard = doc_name.startswith('@*')
            has_wildcard = is_docset_wildcard or is_doc_wildcard
            if has_wildcard:
                # TODO: conditions
                if is_docset_wildcard:
                    docsets = self._db.list_collection_names()
                else:
                    docsets = [docset_name]

                for ds_name in docsets:
                    if is_doc_wildcard:
                        d_names = [d['_doc_name'] for d in self._db[ds_name].find({}, ['_doc_name'])]
                        for d_name in d_names:
                            result.add(DocKeyPair(ds_name, d_name))
                    else:
                        result.add(DocKeyPair(ds_name, doc_name))
            else:
                result.add(DocKeyPair(docset_name, doc_name))

        return list(result)

    def clear(self):
        self._client.drop_database(self._db)

    def flush(self):
        pass

    def reload(self):
        pass

    def create_doc(self, key: DocKeyType = _default_doc_key, val: DocValDict = None) -> List[DocKeyPair]:
        if val is None:
            val = {}

        result: List[DocKeyPair] = []
        target = self._filter(key)

        for ds, d in target:
            collection: pymongo.collection.Collection = self._db[ds]
            val_dup = {**val}
            val_dup['_doc_name'] = d
            if collection.insert_one(val_dup).inserted_id is not None:
                result.append(DocKeyPair(ds, d))

        return result

    def read_doc(self, key: DocKeyType = _wildcard_doc_key) -> Dict[DocKeyPair, DocValDict]:
        result: Dict[DocKeyPair, DocValDict] = {}
        target = self._filter(key)

        for ds, d in target:
            collection: pymongo.collection.Collection = self._db[ds]
            doc = collection.find_one({'_doc_name': d})
            if doc is not None:
                del doc['_doc_name']
                del doc['_id']
                result[DocKeyPair(ds, d)] = doc

        return result

    def update_doc(self, key: DocKeyType = _default_doc_key, val: DocValDict = None) -> List[DocKeyPair]:
        if val is None:
            val = {}

        result: List[DocKeyPair] = []
        target = self._filter(key)

        for ds, d in target:
            collection: pymongo.collection.Collection = self._db[ds]
            update_result = collection.update_one({'_doc_name': d}, {'$set': val}, upsert=True)
            is_success = update_result.modified_count > 0 or update_result.upserted_id is not None
            if is_success:
                result.append(DocKeyPair(ds, d))

        return result

    def delete_doc(self, key: DocKeyType = _default_doc_key) -> int:
        result = 0
        target = self._filter(key)

        for ds, d in target:
            collection: pymongo.collection.Collection = self._db[ds]
            deleted_count = collection.delete_one({'_doc_name': d}).deleted_count
            result += deleted_count

        return result

    def query(self, query: Text, *args, **kwargs) -> Any:
        """Run query on data source."""
        raise NotSupportedError
