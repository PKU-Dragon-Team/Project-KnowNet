from abc import abstractmethod
from typing import Any, Dict, List, NamedTuple, Text, Union

import networkx as nx

from . import BaseDataSource, ConditionDict

# Type definitions for Graph
GraphNameType = Text
GraphKeyList = List[GraphNameType]
GraphKeyDict = Dict[GraphNameType, ConditionDict]
GraphKeyType = Union[GraphNameType, GraphKeyList, GraphKeyDict]
GraphType = Union[nx.Graph, nx.DiGraph, nx.MultiGraph, nx.MultiDiGraph]
GraphAttrDict = Dict[Text, Any]

# Type definitions for Node
NodeNameType = Union[int, Text]


class NodeKeyPair(NamedTuple):
    graph_name: GraphNameType
    node_name: NodeNameType


NodeKeyList = List[NodeKeyPair]
NodeKeyDict = Dict[NodeKeyPair, ConditionDict]
NodeKeyType = Union[NodeKeyPair, NodeKeyList, NodeKeyDict]
NodeValDict = Dict[Text, Any]


# Type Definitions for Edge
class EdgeNamePair(NamedTuple):
    node1: NodeNameType
    node2: NodeNameType


class EdgeKeyPair(NamedTuple):
    graph_name: GraphNameType
    edge_name: EdgeNamePair


EdgeKeyList = List[EdgeKeyPair]
EdgeKeyDict = Dict[EdgeKeyPair, ConditionDict]
EdgeKeyType = Union[EdgeKeyPair, EdgeKeyList, EdgeKeyDict]
EdgeValDict = Dict[Text, Any]


class GraphValType(NamedTuple):
    graph_type: Text = ''
    attr: GraphAttrDict = {}
    nodes: List[NodeNameType] = []
    edges: List[EdgeNamePair] = []
    node_attr: NodeValDict = {}
    edge_attr: EdgeValDict = {}


class GraphDataSource(BaseDataSource):
    @abstractmethod
    def create_graph(self, key: GraphKeyType, val: GraphValType) -> List[GraphNameType]:
        pass

    @abstractmethod
    def create_node(self, key: NodeKeyType, val: NodeValDict) -> List[NodeKeyPair]:
        pass

    @abstractmethod
    def create_edge(self, key: EdgeKeyType, val: EdgeValDict) -> List[EdgeKeyPair]:
        pass

    @abstractmethod
    def read_graph(self, key: GraphKeyType) -> GraphType:
        pass

    @abstractmethod
    def read_node(self, key: NodeKeyType) -> Dict[NodeKeyPair, NodeValDict]:
        pass

    @abstractmethod
    def read_edge(self, key: EdgeKeyType) -> Dict[EdgeKeyPair, EdgeValDict]:
        pass

    @abstractmethod
    def update_graph(self, key: GraphKeyType, val: GraphValType) -> List[GraphNameType]:
        pass

    @abstractmethod
    def update_node(self, key: NodeKeyType, val: NodeValDict) -> List[NodeKeyPair]:
        pass

    @abstractmethod
    def update_edge(self, key: EdgeKeyType, val: EdgeValDict) -> List[EdgeKeyPair]:
        pass

    @abstractmethod
    def delete_graph(self, key: GraphKeyType) -> int:
        pass

    @abstractmethod
    def delete_node(self, key: NodeKeyType) -> int:
        pass

    @abstractmethod
    def delete_edge(self, key: EdgeKeyType) -> int:
        pass
