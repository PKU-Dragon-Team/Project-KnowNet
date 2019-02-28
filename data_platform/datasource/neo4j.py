from typing import Dict, List

from .abc.graph import (EdgeKeyPair, EdgeKeyType, EdgeNamePair, EdgeValDict, GraphDataSource, GraphKeyType, GraphNameType, GraphType, GraphValType, NodeKeyPair,
                        NodeKeyType, NodeValDict)


class Neo4jDS(GraphDataSource):
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

    pass
