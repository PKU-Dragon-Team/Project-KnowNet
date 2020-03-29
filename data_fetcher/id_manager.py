# id_manager.py
# 爬虫爬到的每篇文献和每个作者需要一个在系统内唯一的id。
# IDManager的作用即完成全局唯一ID的管理工作。
# 索引表（即ID和关键码的对应关系）以json格式存储。key为ID，value为关键码

import hashlib
from abc import ABC
import typing as tg
from typing import Any, List, Text, NamedTuple
import os
import pymongo

from data_platform.datasource.mongodb import MongoDBDS
from data_platform.config import ConfigManager
from data_platform.datasource.abc.doc import DocKeyPair, DocKeyType, DocValDict

# (Colletcion, Key, Value)
class KeyValuePair(NamedTuple):
    docset_name: Text
    doc_key: Text
    doc_value: Any
    
    
class DocIdPair(NamedTuple):
    docset_name: Text
    id_: Any


class SpiderMongoDBDS(MongoDBDS):
    def __init__(self, config, *args, **kwargs):
        super().__init__(config, *args, **kwargs)
    
    
    def set_auto_increasement(self, key: KeyValuePair) -> None:
        '''在指定collection中，将一个指定key设置为自增变量。
        本函数只需在初始化id分配器时调用一次。
        该自增变量的初始值为int(doc_value)。
        之后可以通过get_next_value()获取自增后的结果。'''
        ds, d, init_v = key
        collection: pymongo.collection.Collection = self._mongodb[ds]
        doc = collection.insert_one({'_id': d, 'sequence_value': int(init_v)})
        return doc
    
    
    def get_next_value(self, key: DocKeyPair) -> int:
        '''key参数中的第一和第二个元素对应存储自增变量的collection和键。'''
        ds, d = key
        collection: pymongo.collection.Collection = self._mongodb[ds]
        ret = collection.find_one_and_update({'_id': d}, {'$inc': {'sequence_value': 1}})
        return ret['sequence_value']


    def get_id(self, key: KeyValuePair) -> int:
        '''查找docset中满足{key: value}的doc的_id。找不到则返回None'''
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
    
    
    def delete_collections(self, docsets: List) -> None:
        '''---删除数据库中指定的collection---'''
        collection_names = self._mongodb.list_collection_names()
        print('collections before cleaning:', collection_names)
        for collection_name in collection_names:
            if collection_name in docsets:
                db_collection = self._mongodb[collection_name]
                db_collection.drop()

        # 检查删除后的db是否为空
        print('collections remain:', self._mongodb.list_collection_names())

 
class IDManager(ABC):
    '''Abstract class for all id managers.'''        
    def __init__(self, 
                config: ConfigManager, 
                key_: DocKeyPair, 
                auto_inc: DocKeyPair) -> None:
        '''初始化IDManager。参数表：
        - config: 用于初始化MongoDBDS的配置文件，详见MongoDBDS类中的定义
        - key=(docset, doc): 分别表示存储id和name映射关系的collection和name在collection中的字段名
        - auto_inc=(docset, doc): 分别表示为了实现id的自增而需要的collection'''
        self._db = SpiderMongoDBDS(config)
        self._collection = key_[0]
        self._key = key_[1]
        
        self._auto_inc_docset = auto_inc[0]
        self._auto_inc_key = auto_inc[1]
        
        self._set_id_increasement(init_value=0)
        
    def _set_id_increasement(self, init_value: int) -> None:
        '''检查有没有初始化自增变量。如果以前初始化过，
        则会捕捉到DuplicateKeyError，就什么都不做。'''
        try:
            key_value_pair = KeyValuePair(self._auto_inc_docset, self._auto_inc_key, init_value)
            self._db.set_auto_increasement(key=key_value_pair)
        except pymongo.errors.DuplicateKeyError as e:
            pass
        return
    
            
    def check_id(self, name: Text) -> int:
        '''如果在数据库中查到了这个name对应的id（即查找条件为{key: name}），就返回id。
        如果没查到结果，为这个name分配一个新id，并加入到数据库中'''
        key_value_pair = KeyValuePair(self._collection, self._key, name)        
        result = self._db.get_id(key=key_value_pair)
        if result != None:
            # 如果在数据库中查到了这个name对应的id，就返回id。
            return result
        else:
            # 如果数据库中没查到结果，说明本name还没有录入到数据库。
            # 为这个name分配一个新id，并加入到数据库中
            nextv_doc_key_pair = DocKeyPair(self._auto_inc_docset, self._auto_inc_key)
            new_id = self._db.get_next_value(nextv_doc_key_pair)
            self._db.insert_one(id_=new_id, docset=self._collection, 
                            val={self._key: name})
            return new_id
    
    
    def check_name(self, id_: int) -> Text:
        '''根据doc的_id查找name。如果没找到返回None'''
        dip = DocIdPair(self._collection, id_)
        ret = self._db.get_doc_by_id(dip)
        if isinstance(ret, dict):
            return ret[self._key]
        return None


    def _get_db(self):
        '''获取本IDManager对应的mongodb database。仅用于debug'''
        return self._db._mongodb
    

class PaperIDManager(IDManager):
    def __init__(self, config: ConfigManager, 
                 key: DocKeyPair = DocKeyPair('paper_id', 'title'), 
                 auto_inc: DocKeyPair = DocKeyPair('id_inc', 'paper_id')):
        super().__init__(config, key, auto_inc)
    
    