from typing import Dict, List

from .abc.doc import DocDataSource, DocKeyPair, DocKeyType, DocValDict


class MongoDBDS(DocDataSource):
    def create_doc(self, key: DocKeyType, val: DocValDict) -> List[DocKeyPair]:
        pass

    def read_doc(self, key: DocKeyType = DocKeyPair('@*', '@*')) -> Dict[DocKeyPair, DocValDict]:
        pass

    def update_doc(self, key: DocKeyType, val: DocValDict) -> List[DocKeyPair]:
        pass

    def delete_doc(self, key: DocKeyType) -> int:
        pass
