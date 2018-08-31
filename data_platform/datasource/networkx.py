"""data source class for graph storage with NetworkX."""

from pathlib import Path
from typing import Dict, List, NoReturn, Set, Tuple

import networkx as nx

from ..config import ConfigManager
from .abc.base import ConditionDict
from .abc.graph import EdgeKeyPair, EdgeKeyType, EdgeNamePair, EdgeValDict
from .abc.graph import GraphDataSource, GraphKeyType, GraphNameType, GraphType, GraphValType
from .abc.graph import NodeKeyPair, NodeKeyType, NodeValDict
from .exception import NotSupportedError


class NetworkXDS(GraphDataSource):
    """GraphDataSource using NetworkX Graph as data storage."""

    GRAPH_MAPPING = {"Graph": nx.Graph, "DiGraph": nx.DiGraph}

    FILE_MAPPING = {
        "edge-list": ('txt', nx.read_edgelist, nx.write_edgelist),
        "weighted-edge-list": ('txt', nx.read_weighted_edgelist, nx.write_weighted_edgelist),
        "graphml": ('graphml', nx.read_graphml, nx.write_graphml),
        "pickle": ('bin', nx.read_gpickle, nx.write_gpickle)
    }

    DEFAULT_GRAPH_KEY = '_default'
    DEFAULT_NODE_KEY = NodeKeyPair('_default', 0)
    DEFAULT_EDGE_KEY = EdgeKeyPair('_default', EdgeNamePair(0, 1))
    DEFAULT_GRAPH_VAL = GraphValType(graph_type="Graph", attr={}, nodes=[], edges=[], node_attr={}, edge_attr={})

    def __init__(self, config: ConfigManager, *args, **kwargs) -> None:
        super().__init__(config, *args, **kwargs)

        self._file_format = config.get('file_format', 'edge-list')
        self._file_ext, self._reader, self._writer = self.FILE_MAPPING[self._file_format]

        _loc = config.check_get(["init", "location"])
        path_loc = Path(_loc)

        if path_loc.is_dir():
            self._loc = path_loc
        else:
            self._loc = path_loc.parent

        self._config = config
        self._data: Dict[GraphNameType, GraphType] = {}
        self._dirty_bits: Set[GraphNameType] = set()

        self._load()

    def __del__(self) -> None:
        self.flush()

    def _dump(self) -> None:
        """Dump in-memory data into local file."""
        for graph_name in self._dirty_bits.copy():
            graph_file = self._loc / (graph_name + '.' + self._file_ext)

            if graph_name not in self._data:
                if graph_file.exists():
                    graph_file.unlink()
            else:
                with graph_file.open('wb') as f:
                    self._writer(self._data[graph_name], f)

            self._dirty_bits.remove(graph_name)

    def _load(self) -> None:
        """Load local file into memory."""
        self._data.clear()
        self._dirty_bits.clear()

        for graph_file in self._loc.glob('*.' + self._file_ext):  # type: Path
            with graph_file.open('rb') as f:
                self._data[graph_file.stem] = self._reader(f)

    def flush(self):
        """Write pending edit to disk files."""
        self._dump()

    def reload(self):
        """Force reload disk files into memory."""
        self.flush()
        self._load()

    def clear(self) -> None:
        """Clean in-memory and local files."""
        self._dirty_bits.update(self._data.keys())
        self._data.clear()
        self.flush()

    def query(self, query: str, *args, **kwargs) -> NoReturn:
        raise NotSupportedError("NetworkX data source has no query method.")

    def _filter_graph(self, key: GraphKeyType) -> List[GraphNameType]:
        graph_cond: List[Tuple] = []

        if isinstance(key, str):
            graph_cond.append((key, None))

        if isinstance(key, list):
            for g_n in key:
                graph_cond.append((g_n, None))

        if isinstance(key, dict):
            for g_n, c in key.items():
                graph_cond.append((g_n, c))

        result = []
        for graph_name, _ in graph_cond:
            if graph_name.startswith('@*'):
                for g_n in self._data:
                    result.append(g_n)
                    # TODO: wildcards and filters
            else:
                result.append(graph_name)

        return result

    def _filter_node(self, key: NodeKeyType) -> List[NodeKeyPair]:
        graph_node_cond: List[Tuple] = []
        if isinstance(key, tuple):
            graph_node_cond.append((key[0], key[1], None))

        if isinstance(key, list):
            for g_n, n_n in key:
                graph_node_cond.append((g_n, n_n, None))

        if isinstance(key, dict):
            for (g_n, n_n), cond in key.items():
                graph_node_cond.append((g_n, n_n, cond))
        result = []
        for graph_name, node_name, _ in graph_node_cond:
            is_graph_wildcard = graph_name.startswith('@*')
            is_node_wildcard = isinstance(node_name, str) and node_name.startswith('@*')
            is_wildcard = is_graph_wildcard or is_node_wildcard

            if is_wildcard:
                if is_graph_wildcard:
                    target_graph_names = list(self._data.keys())
                    # TODO: graph filter
                else:
                    target_graph_names = [graph_name]

                for g_n in target_graph_names:
                    if is_node_wildcard:
                        for n_n in self._data[g_n]:
                            result.append(NodeKeyPair(g_n, n_n))
                        # TODO: node filter
                    else:
                        result.append(NodeKeyPair(g_n, node_name))

            else:
                result.append(NodeKeyPair(graph_name, node_name))

        return result

    def _filter_edge(self, key: EdgeKeyType) -> List[EdgeKeyPair]:
        graph_edge_cond: List[Tuple[GraphNameType, EdgeNamePair, ConditionDict]] = []

        if isinstance(key, tuple):
            graph_edge_cond.append((key[0], key[1], {}))

        if isinstance(key, list):
            for g_n, e_p in key:
                graph_edge_cond.append((g_n, e_p, {}))

        if isinstance(key, dict):
            for (g_n, e_p), cond in key.items():
                graph_edge_cond.append((g_n, e_p, cond))

        result = []
        for graph_name, (node1, node2), _ in graph_edge_cond:
            is_graph_wildcard = graph_name.startswith('@*')
            is_node1_wildcard = isinstance(node1, str) and node1.startswith('@*')
            is_node2_wildcard = isinstance(node2, str) and node2.startswith('@*')
            is_edge_wildcard = is_node1_wildcard or is_node2_wildcard
            is_wildcard = is_graph_wildcard or is_edge_wildcard

            if is_wildcard:
                if is_graph_wildcard:
                    target_graph_names = list(self._data.keys())
                    # TODO: graph filter
                else:
                    target_graph_names = [graph_name]

                for g_n in target_graph_names:
                    g = self._data[g_n]
                    is_directional = g.is_directed()
                    if is_edge_wildcard:
                        if is_node1_wildcard and is_node2_wildcard:  # all-edges
                            for e_p in g.edges():
                                result.append(EdgeKeyPair(g_n, e_p))
                        elif is_node1_wildcard:  # node2's in_edges
                            if g.has_node(node2):
                                if is_directional:
                                    for e_p in g.in_edges(node2):
                                        result.append(EdgeKeyPair(g_n, e_p))
                                else:
                                    # TODO: Warning: graph is not directional, use edges instead
                                    for e_p in g.edges(node2):
                                        result.append(EdgeKeyPair(g_n, e_p))
                        elif is_node2_wildcard:  # node1's out_edges
                            if g.has_node(node1):
                                if is_directional:
                                    for e_p in g.out_edges(node1):
                                        result.append(EdgeKeyPair(g_n, e_p))
                                else:
                                    for e_p in g.edges(node1):
                                        result.append(EdgeKeyPair(g_n, e_p))
                        # TODO: edge filter
                    else:
                        result.append(EdgeKeyPair(g_n, EdgeNamePair(node1, node2)))

            else:
                result.append(EdgeKeyPair(graph_name, EdgeNamePair(node1, node2)))

        return result

    @classmethod
    def _create_one_graph(cls, val: GraphValType) -> GraphType:
        graph_type = val.graph_type
        attr = val.attr
        nodes = val.nodes
        edges = val.edges
        node_attr = val.node_attr
        edge_attr = val.edge_attr

        graph_init = cls.GRAPH_MAPPING[graph_type]

        g = graph_init(**attr)
        g.add_nodes_from(nodes, **node_attr)
        g.add_edges_from(edges, **edge_attr)

        return g

    def _update_one_graph(self, graph_name: GraphNameType, val: GraphValType) -> None:
        attr = val.attr
        nodes = val.nodes
        edges = val.edges

        node_attr = val.node_attr
        edge_attr = val.edge_attr

        self._data[graph_name].graph.update(attr)
        self._data[graph_name].add_nodes_from(nodes)
        self._data[graph_name].add_edges_from(edges)
        for node in nodes:
            self._data[graph_name].nodes[node].update(node_attr)
        for edge in edges:
            self._data[graph_name].edges[edge].update(edge_attr)

    def create_graph(self, key: GraphKeyType = DEFAULT_GRAPH_KEY, val: GraphValType = DEFAULT_GRAPH_VAL) -> List[GraphNameType]:
        target = self._filter_graph(key)

        results: List = []
        for graph_name in target:
            self._data[graph_name] = self._create_one_graph(val)
            results.append(graph_name)
            self._dirty_bits.add(graph_name)

        return results

    def create_node(self, key: NodeKeyType = DEFAULT_NODE_KEY, val: NodeValDict = {}) -> List[NodeKeyPair]:
        target = self._filter_node(key)

        results: List = []
        for graph_name, node_name in target:
            self._data[graph_name].add_node(node_name, **val)
            results.append((graph_name, node_name))
            self._dirty_bits.add(graph_name)

        return results

    def create_edge(self, key: EdgeKeyType = DEFAULT_EDGE_KEY, val: EdgeValDict = {}) -> List[EdgeKeyPair]:
        target = self._filter_edge(key)

        results: List = []
        for graph_name, (node1, node2) in target:
            self._data[graph_name].add_edge(node1, node2, **val)
            results.append((graph_name, (node1, node2)))
            self._dirty_bits.add(graph_name)

        return results

    def read_graph(self, key: GraphKeyType = "@*") -> Dict[GraphNameType, GraphType]:
        target = self._filter_graph(key)

        result = {}
        for graph_name in target:
            if graph_name in self._data:
                result[graph_name] = self._data[graph_name]

        return result

    def read_node(self, key: NodeKeyType = NodeKeyPair('@*', '@*')) -> Dict[NodeKeyPair, NodeValDict]:
        target = self._filter_node(key)

        result = {}
        for g_name, n_name in target:
            if g_name in self._data:
                g = self._data[g_name]
                if g.has_node(n_name):
                    result[NodeKeyPair(g_name, n_name)] = g.nodes[n_name]

        return result

    def read_edge(self, key: EdgeKeyType = EdgeKeyPair('@*', EdgeNamePair('@*', '@*'))) -> Dict[EdgeKeyPair, EdgeValDict]:
        target = self._filter_edge(key)

        result = {}
        for g_name, (n1_name, n2_name) in target:
            if g_name in self._data:
                g = self._data[g_name]
                if g.has_edge(n1_name, n2_name):
                    result[EdgeKeyPair(g_name, EdgeNamePair(n1_name, n2_name))] = g.edges[n1_name, n2_name]

        return result

    def update_graph(self, key: GraphKeyType = DEFAULT_GRAPH_KEY, val: GraphValType = DEFAULT_GRAPH_VAL) -> List[GraphNameType]:
        target = self._filter_graph(key)
        result = []
        for graph_name in target:
            self._update_one_graph(graph_name, val)
            result.append(graph_name)
            self._dirty_bits.add(graph_name)

        return result

    def update_node(self, key: NodeKeyType = DEFAULT_NODE_KEY, val: NodeValDict = {}) -> List[NodeKeyPair]:
        target = self._filter_node(key)
        result = []
        for graph_name, node_name in target:
            self._data[graph_name].nodes[node_name].update(val)
            result.append(NodeKeyPair(graph_name, node_name))
            self._dirty_bits.add(graph_name)

        return result

    def update_edge(self, key: EdgeKeyType = DEFAULT_EDGE_KEY, val: EdgeValDict = {}) -> List[EdgeKeyPair]:
        target = self._filter_edge(key)
        result = []
        for graph_name, (node1_name, node2_name) in target:
            self._data[graph_name].edges[node1_name, node2_name].update(val)
            result.append(EdgeKeyPair(graph_name, EdgeNamePair(node1_name, node2_name)))
            self._dirty_bits.add(graph_name)

        return result

    def delete_graph(self, key: GraphKeyType = DEFAULT_GRAPH_KEY) -> int:
        target = self._filter_graph(key)
        result = 0
        for graph_name in target:
            if graph_name in self._data:
                del self._data[graph_name]
                result += 1
                self._dirty_bits.add(graph_name)

        return result

    def delete_node(self, key: NodeKeyType = DEFAULT_NODE_KEY) -> int:
        target = self._filter_node(key)
        result = 0
        for graph_name, node_name in target:
            if graph_name in self._data:
                g = self._data[graph_name]
                if g.has_node(node_name):
                    g.remove_node(node_name)
                    result += 1
                    self._dirty_bits.add(graph_name)

        return result

    def delete_edge(self, key: EdgeKeyType = DEFAULT_EDGE_KEY) -> int:
        target = self._filter_edge(key)
        result = 0
        for graph_name, (node1_name, node2_name) in target:
            if graph_name in self._data:
                g = self._data[graph_name]
                if g.has_edge(node1_name, node2_name):
                    g.remove_edge(node1_name, node2_name)
                    result += 1
                    self._dirty_bits.add(graph_name)

        return result
