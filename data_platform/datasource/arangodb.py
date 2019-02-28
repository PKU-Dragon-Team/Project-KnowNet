from typing import Any, Dict, List, Text

from .abc.doc import DocDataSource, DocKeyPair, DocKeyType, DocValDict
from .abc.graph import (EdgeKeyPair, EdgeKeyType, EdgeNamePair, EdgeValDict, GraphDataSource, GraphKeyType, GraphNameType, GraphType, GraphValType, NodeKeyPair,
                        NodeKeyType, NodeValDict)

# from .exception import NotSupportedError

try:
    import pyArango.connection
    import pyArango.database
    import pyArango.collection
    import pyArango.document
except ImportError:
    raise ImportError('This data source requires pyArango to be installed.')


class ArangoDBDS(DocDataSource, GraphDataSource):
    DEFAULT_DOC_KEY = DocKeyPair('default_', 'default_')
    WILDCARD_DOC_KEY = DocKeyPair('@*', '@*')

    DEFAULT_GRAPH_KEY = '_default'
    DEFAULT_NODE_KEY = NodeKeyPair('_default', 0)
    DEFAULT_EDGE_KEY = EdgeKeyPair('_default', EdgeNamePair(0, 1))
    DEFAULT_GRAPH_VAL = GraphValType(graph_type="Graph", attr={}, nodes=[], edges=[], node_attr={}, edge_attr={})

    def __init__(self, config, *args, **kwargs):
        super().__init__(config, *args, **kwargs)

        self._uri: Text = config.check_get(["init", "uri"])
        self._user: Text = config.check_get(["init", "user"])
        self._password: Text = config.check_get(["init", "password"])
        self._database: Text = config.check_get(["init", "database"])

        self._conn = pyArango.connection.Connection(self._uri, self._user, self._password)
        if not self._conn.hasDatabase(self._database):
            _db: pyArango.database.Database = self._conn.createDatabase(self._database)
        else:
            _db = self._conn[self._database]
        self._arangodb: pyArango.database.Database = _db

    def __del__(self):
        self._conn.disconnectSession()

    def _filter_doc(self, key: DocKeyType) -> List[DocKeyPair]:
        ds_d_c = self._format_doc_key(key)

        result = set()
        for docset_name, doc_name, _ in ds_d_c:
            is_docset_wildcard = docset_name.startswith('@*')
            is_doc_wildcard = doc_name.startswith('@*')
            has_wildcard = is_docset_wildcard or is_doc_wildcard
            if has_wildcard:
                # TODO: conditions
                if is_docset_wildcard:
                    docsets = list(self._arangodb.collections.keys())
                else:
                    docsets = [docset_name]

                for ds_name in docsets:
                    if is_doc_wildcard and self._arangodb.hasCollection(ds_name):
                        d_names = [d['doc_name_'] for d in self._arangodb[ds_name].fetchAll()]
                        for d_name in d_names:
                            result.add(DocKeyPair(ds_name, d_name))
                    else:
                        result.add(DocKeyPair(ds_name, doc_name))
            else:
                result.add(DocKeyPair(docset_name, doc_name))

        return list(result)

    def clear(self):
        self._arangodb.dropAllCollections()

    def flush(self):
        pass

    def reload(self):
        self._arangodb.reload()

    def create_doc(self, key: DocKeyType = DEFAULT_DOC_KEY, val: DocValDict = None) -> List[DocKeyPair]:
        if val is None:
            val = {}

        result: List[DocKeyPair] = []
        target = self._filter_doc(key)

        for ds, d in target:
            if not self._arangodb.hasCollection(ds):
                collection: pyArango.collection.Collection = self._arangodb.createCollection(name=ds)
            else:
                collection = self._arangodb[ds]

            val['doc_name_'] = d
            collection.createDocument(val)
            result.append(DocKeyPair(ds, d))

        return result

    def read_doc(self, key: DocKeyType = WILDCARD_DOC_KEY) -> Dict[DocKeyPair, DocValDict]:
        result: Dict[DocKeyPair, DocValDict] = {}
        target = self._filter_doc(key)

        for ds, d in target:
            if not self._arangodb.hasCollection(ds):
                continue

            collection: pyArango.collection.Collection = self._arangodb[ds]
            query = collection.fetchByExample({'doc_name_': d}, batchSize=10)
            for doc in query:  # type: pyArango.document.Document
                store = doc.getStore()
                del store['doc_name_']
                result[DocKeyPair(ds, d)] = store

        return result

    def update_doc(self, key: DocKeyType = DEFAULT_DOC_KEY, val: DocValDict = None) -> List[DocKeyPair]:
        if val is None:
            val = {}

        result: List[DocKeyPair] = []
        target = self._filter_doc(key)

        for ds, d in target:
            if not self._arangodb.hasCollection(ds):
                collection: pyArango.collection.Collection = self._arangodb.createCollection(name=ds)
            else:
                collection = self._arangodb[ds]

            query = collection.fetchByExample({'doc_name_': d}, batchSize=10, count=True)
            if query.count > 0:
                for doc in query:
                    doc.set(val)
                    doc.patch()
                result.append(DocKeyPair(ds, d))

        return result

    def delete_doc(self, key: DocKeyType = DEFAULT_DOC_KEY) -> int:
        result = 0
        target = self._filter_doc(key)

        for ds, d in target:
            if not self._arangodb.hasCollection(ds):
                continue
            collection: pyArango.collection.Collection = self._arangodb[ds]
            query = collection.fetchByExample({'doc_name_': d}, batchSize=10)
            for doc in query:
                doc.delete()
                result += 1

        return result

    def create_graph(self, key: GraphKeyType, val: GraphValType) -> List[GraphNameType]:
        pass

    def create_node(self, key: NodeKeyType, val: NodeValDict) -> List[NodeKeyPair]:
        pass

    def create_edge(self, key: EdgeKeyType, val: EdgeValDict) -> List[EdgeKeyPair]:
        pass

    def read_graph(self, key: GraphKeyType) -> GraphType:
        pass

    def read_node(self, key: NodeKeyType) -> Dict[NodeKeyPair, NodeValDict]:
        pass

    def read_edge(self, key: EdgeKeyType) -> Dict[EdgeKeyPair, EdgeValDict]:
        pass

    def update_graph(self, key: GraphKeyType, val: GraphValType) -> List[GraphNameType]:
        pass

    def update_node(self, key: NodeKeyType, val: NodeValDict) -> List[NodeKeyPair]:
        pass

    def update_edge(self, key: EdgeKeyType, val: EdgeValDict) -> List[EdgeKeyPair]:
        pass

    def delete_graph(self, key: GraphKeyType) -> int:
        pass

    def delete_node(self, key: NodeKeyType) -> int:
        pass

    def delete_edge(self, key: EdgeKeyType) -> int:
        pass

    def query(self, query: Text, *args, **kwargs) -> Any:
        """Run query on data source."""
        return self._arangodb.AQLQuery(query, *args, **kwargs)
