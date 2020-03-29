# id_manager.py
# 爬虫爬到的每篇文献和每个作者需要一个在系统内唯一的id。
# IDManager的作用即完成全局唯一ID的管理工作。
# 索引表（即ID和关键码的对应关系）以json格式存储。key为ID，value为关键码

# 注意：目前的IDManager在多线程下是不安全的。请不要同时创建两个以上相同的IDManager子类。

import hashlib
from abc import ABC
import typing as tg
import os
import json

 
class IDManager(ABC):
    '''Abstract class for all id managers.'''        
    def __init__(self) -> None:
        self._MAX_NUMBER = 1000000  # hash表的大小
        self._hash_method = hashlib.md5
        self._json_address = None
        self._table = None
    
    def __del__(self) -> None:
        # 对象消亡时，将修改写入json文件中
        self._dump()
    
    def _dump(self):
        with open(self._json_address, 'w', encoding='utf-8') as f:
            json.dump(self._table, f)
    
    def get_max_number(self) -> int:
        return self._MAX_NUMBER

    def get_id(self, key: str) -> int:
        key_encoded = key.encode('utf-8')
        # 根据关键码查找对应的id
        hashed_int = int(self._hash_method(key_encoded).hexdigest(), base=16)
        id_ =  hashed_int % self._MAX_NUMBER
        
        # 检查这个id是否在记录中存在。
        while True:
            try:
                key_in_table = self._table[str(id_)]
            except KeyError as e:
                # 出现KeyError，说明当前id还没有对应的key，因此分配给这个新key
                break
            if key_in_table == key: # 说明当前id对应的就是这个新key
                break
            id_ = (id_ + 1) % self._MAX_NUMBER
            
        self._table[str(id_)] = key
        return str(id_)
    
    def get_key(self, id_:int) -> str:
        # 根据id查找对应的关键码
        try:
            key = self._table[id_]
        except KeyError as e:
            return None
        return 
    
    def print_table(self):
        for k in self._table:
            print(k, '\t', self._table[k])
    
class PaperIDManager(IDManager):
    def __init__(self):
        super().__init__()
        self._json_address = './data_fetcher/paper_id.json'
        if os.path.exists(self._json_address):  
            # 如果这个json文件已经被创建了，就读取它作为table
            with open(self._json_address, 'r', encoding='utf-8') as f:    
                self._table = json.load(f)
        else:   # 如果还没创建，将table设为空dict
            self._table = dict()
            print('Initialized PaperID storage json.')
        
    def __del__(self):
        super().__del__()
    