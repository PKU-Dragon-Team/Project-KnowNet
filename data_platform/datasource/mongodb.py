from typing import List, Dict, List, Any, Text

from ..config import ConfigManager
from .abc.doc import DocDataSource, DocKeyPair, DocKeyType, DocValDict, DocKeyVal, DocIdPair
from .exception import NotSupportedError

try:
    import pymongo
    from pymongo import MongoClient
except ImportError:
    raise ImportError('This data source requires pymongo to be installed.')


class MongoDBDS(DocDataSource):
    '''MongoDB datasource class'''
    DEFAULT_DOC_KEY = DocKeyPair('_default', '_default')
    WILDCARD_DOC_KEY = DocKeyPair('@*', '@*')

    def __init__(self, config: ConfigManager, *args, **kwargs) -> None:
        '''参数表：
        - config: 用于初始化pymongo中MongoClient类。格式如下：
            config = {
                "init": {
                    "uri": [MongoClient要连接的地址。如果在本机上运行，写None即可。],
                    "database": [数据库名。如果在本机上运行，写任何一个字符串均可]
                }
            }
            详细说明见pymongo文档中关于MongoClient类的内容：
            https://api.mongodb.com/python/current/api/pymongo/mongo_client.html
        '''
        super().__init__(config, *args, **kwargs)

        self._uri: Text = config.check_get(["init", "uri"])
        self._database: Text = config.check_get(["init", "database"])

        self._client: MongoClient = MongoClient(self._uri)
        self._mongodb: pymongo.database.Database = self._client[self._database]

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
                    docsets = self._mongodb.list_collection_names()
                else:
                    docsets = [docset_name]

                for ds_name in docsets:
                    if is_doc_wildcard:
                        d_names = [d['_doc_name'] for d in self._mongodb[ds_name].find({}, ['_doc_name'])]
                        for d_name in d_names:
                            result.add(DocKeyPair(ds_name, d_name))
                    else:
                        result.add(DocKeyPair(ds_name, doc_name))
            else:
                result.add(DocKeyPair(docset_name, doc_name))

        return list(result)

    def clear(self):
        self._client.drop_database(self._mongodb)

    def flush(self):
        pass

    def reload(self):
        pass

    def create_doc(self, key: DocKeyType = DEFAULT_DOC_KEY, val: DocValDict = None) -> List[DocKeyPair]:
        if val is None:
            val = {}

        result: List[DocKeyPair] = []
        target = self._filter(key)

        for ds, d in target:
            collection: pymongo.collection.Collection = self._mongodb[ds]
            val_dup = {**val}
            val_dup['_doc_name'] = d
            if collection.insert_one(val_dup).inserted_id is not None:
                result.append(DocKeyPair(ds, d))

        return result

    def read_doc(self, key: DocKeyType = WILDCARD_DOC_KEY) -> Dict[DocKeyPair, DocValDict]:
        result: Dict[DocKeyPair, DocValDict] = {}
        target = self._filter(key)

        for ds, d in target:
            collection: pymongo.collection.Collection = self._mongodb[ds]
            doc = collection.find_one({'_doc_name': d})
            if doc is not None:
                del doc['_doc_name']
                del doc['_id']
                result[DocKeyPair(ds, d)] = doc

        return result

    def update_doc(self, key: DocKeyType = DEFAULT_DOC_KEY, val: DocValDict = None) -> List[DocKeyPair]:
        if val is None:
            val = {}

        result: List[DocKeyPair] = []
        target = self._filter(key)

        for ds, d in target:
            collection: pymongo.collection.Collection = self._mongodb[ds]
            update_result = collection.update_one({'_doc_name': d}, {'$set': val}, upsert=True)
            is_success = update_result.modified_count > 0 or update_result.upserted_id is not None
            if is_success:
                result.append(DocKeyPair(ds, d))

        return result

    def delete_doc(self, key: DocKeyType = DEFAULT_DOC_KEY) -> int:
        result = 0
        target = self._filter(key)

        for ds, d in target:
            collection: pymongo.collection.Collection = self._mongodb[ds]
            deleted_count = collection.delete_one({'_doc_name': d}).deleted_count
            result += deleted_count

        return result
    
    def query(self, docset, query: Dict) -> List[Dict]:
        '''在指定collection中根据query查找符合条件的所有文档'''
        collection: pymongo.collection.Collection = self._mongodb[docset]
        find_result = collection.find(query)
        ret = []
        for i in find_result:
            ret.append(i)
        return ret
    
    def set_auto_increasement(self, key: DocKeyVal) -> None:
        '''在指定collection中，将一个指定key设置为自增变量。
        该自增变量的初始值为int(value)。
        之后可以通过get_next_value(docset, key)获取自增后的结果。
        如果同名自增变量以前初始化过，则会捕获DuplicateKeyError，
        就什么都不做'''
        ds, d, init_v = key
        collection: pymongo.collection.Collection = self._mongodb[ds]
        try:
            doc = collection.insert_one({'_id': d, 'sequence_value': int(init_v)})
        except pymongo.errors.DuplicateKeyError as e:
            print('auto increasement value', d, 'already set.')
            pass

    def get_next_value(self, key: DocKeyPair) -> int:
        '''从指定的collection和key中获取一个自增变量的值并将其+1。
        常用于获取自增id的下一个值。'''
        ds, d = key
        collection: pymongo.collection.Collection = self._mongodb[ds]
        ret = collection.find_one_and_update({'_id': d}, {'$inc': {'sequence_value': 1}})
        return ret['sequence_value']

    def get_id(self, key: DocKeyVal) -> int:
        '''查找collection中第一个满足{key: value}的doc的_id。找不到则返回None'''
        ds, d, v = key
        collection: pymongo.collection.Collection = self._mongodb[ds]
        ret = collection.find_one({d: v})
        if isinstance(ret, dict):
            return ret['_id']
        return None
    
    def get_doc_by_id(self, key: DocIdPair) -> dict:
        '''查找docset中指定_id的doc'''
        ds, id_ = key
        collection: pymongo.collection.Collection = self._mongodb[ds]
        ret = collection.find_one({'_id': id_})
        return ret
    
    def insert_one(self, id_, docset: Text, val: DocValDict) -> int:
        '''在名为docset的collection中插入val文件，并将其_id设为id_。
        返回插入doc的_id'''
        collection: pymongo.collection.Collection = self._mongodb[docset]
        val_dup = {**val}
        val_dup['_id'] = id_
        ret = collection.insert_one(val_dup).inserted_id
        return ret
    
    def delete_collections(self, docsets: List[Text]) -> None:
        '''---删除数据库中指定的collection---'''
        collection_names = self._mongodb.list_collection_names()
        print('collections before cleaning:', collection_names)
        for collection_name in collection_names:
            if collection_name in docsets:
                db_collection = self._mongodb[collection_name]
                db_collection.drop()