from abc import ABC
from typing import Text

from data_platform.datasource.mongodb import MongoDBDS
from data_platform.config import ConfigManager
from data_platform.datasource.abc.doc import DocKeyPair, DocKeyVal, DocIdPair


class IDManager(ABC):
    """IDManager的核心任务是使用mongodb分配和管理name: Text和id: int之间的映射关系。
    这里的name可以是文献名、作者名、期刊名等。"""
    def __init__(self, config: ConfigManager, key: DocKeyPair, auto_inc: DocKeyPair) -> None:
        '''初始化IDManager。
        参数表：
        - config: 用于初始化MongoDBDS的配置文件，详见MongoDBDS类中的定义
        - key=(docset, doc): 分别表示存储id和name映射关系的collection和name的字段名
        - auto_inc=(docset, doc): 分别表示为了实现id的自增而需要的collection和自增变量的字段名'''
        self._db = MongoDBDS(config)
        self._collection = key[0]
        self._key = key[1]

        self._auto_inc_docset = auto_inc[0]
        self._auto_inc_key = auto_inc[1]

        self._set_id_increasement(init_value=0)

    def _set_id_increasement(self, init_value: int) -> None:
        '''调用set_auto_increasement检查并初始化自增变量。'''
        key_value_pair = DocKeyVal(self._auto_inc_docset, self._auto_inc_key, init_value)
        self._db.set_auto_increasement(key=key_value_pair)

    def get_id(self, name: Text) -> int:
        '''如果在数据库中查到了这个name对应的id（即查找条件为{key: name}），就返回id。
        如果没查到结果，为这个name分配一个新id，并加入到数据库中'''
        key_value_pair = DocKeyVal(self._collection, self._key, name)
        result = self._db.get_id(key=key_value_pair)
        if result is not None:
            # 如果在数据库中查到了这个name对应的id，就返回id。
            return result
        # 如果数据库中没查到结果，说明本name还没有录入到数据库。
        # 为这个name分配一个新id，并加入到数据库中
        nextv_doc_key_pair = DocKeyPair(self._auto_inc_docset, self._auto_inc_key)
        new_id = self._db.get_next_value(nextv_doc_key_pair)
        self._db.insert_one(id_=new_id, docset=self._collection, val={self._key: name})
        return new_id

    def get_name(self, id_: int) -> Text:
        '''根据doc的_id查找name。如果没找到返回None'''
        dip = DocIdPair(self._collection, id_)
        ret = self._db.get_doc_by_id(dip)
        if isinstance(ret, dict):
            return ret[self._key]
        return None

    def _get_db(self):
        '''获取本IDManager对应的mongodb database。仅用于debug'''
        return self._db.get_db()
