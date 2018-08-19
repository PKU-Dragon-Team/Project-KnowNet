"""data source class for graph storage with NetworkX
"""

from pathlib import Path
from typing import Any, Dict, Hashable, List, NoReturn, Set, Tuple, Union, cast

import networkx as nx

from . import base as _base
from ..config import ConfigManager

_Graph = Union[nx.Graph, nx.DiGraph]

_GRAPH_T = str
_NODE_T = Hashable
_EDGE_T = Tuple[_NODE_T, _NODE_T]

_GRAPH_KEY_T = _GRAPH_T
_NODE_KEY_T = Tuple[_GRAPH_T, _NODE_T]
_EDGE_KEY_T = Tuple[_GRAPH_T, _EDGE_T]

_GRAPH_KEY_UT = Union[Dict[_GRAPH_KEY_T, Any], List[_GRAPH_KEY_T], _GRAPH_KEY_T]
_NODE_KEY_UT = Union[Dict[_NODE_KEY_T, Any], List[_NODE_KEY_T], _NODE_KEY_T]
_EDGE_KEY_UT = Union[Dict[_EDGE_KEY_T, Any], List[_EDGE_KEY_T], _EDGE_KEY_T]

GRAPH_MAPPING = {"Graph": nx.Graph, "DiGraph": nx.DiGraph}

FILE_MAPPING = {
    "edge-list": ('txt', nx.read_edgelist, nx.write_edgelist),
    "weighted-edge-list": ('txt', nx.read_weighted_edgelist, nx.write_weighted_edgelist),
    "graphml": ('graphml', nx.read_graphml, nx.write_graphml),
    "pickle": ('bin', nx.read_gpickle, nx.write_gpickle)
}


class NetworkXDS(_base.GraphDataSource):
    """GraphDataSource using NetworkX Graph as data storage.
    """

    _default_graph_key = '_default'
    _default_node_key = ('_default', 0)
    _default_edge_key = ('_default', (0, 1))

    _wildcard_graph_key = '@*'
    _wildcard_node_key = ('@*', '@*')
    _wildcard_edge_key = ('@*', ('@*', '@*'))

    def __init__(self, config: ConfigManager, *args, **kwargs) -> None:
        super().__init__(config, *args, **kwargs)

        self._file_format = config.get('file_format', 'edge-list')
        self._file_ext, self._reader, self._writer = FILE_MAPPING[self._file_format]

        _loc = config.check_get(["init", "location"])
        path_loc = Path(_loc)

        if path_loc.is_dir():
            self._loc = path_loc
        else:
            self._loc = path_loc.parent

        self._config = config
        self._data: Dict[_GRAPH_KEY_T, _Graph] = {}
        self._dirty_bits: Set[_GRAPH_KEY_T] = set()

        self._load()

    def __del__(self) -> None:
        self.flush()

    def _dump(self) -> None:
        """dump in-memory data into local file
        """
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
        """load local file into memory
        """
        self._data.clear()
        self._dirty_bits.clear()

        for graph_file in self._loc.glob('*.' + self._file_ext):  # type: Path
            with graph_file.open('rb') as f:
                self._data[graph_file.stem] = self._reader(f)

    def flush(self):
        """Write pending edit to disk files.
        """
        self._dump()

    def reload(self):
        """Force reload disk files into memory.
        """
        self.flush()
        self._load()

    def clear(self) -> None:
        """Clean in-memory and local files
        """
        self._dirty_bits.update(self._data.keys())
        self._data.clear()
        self.flush()

    def query(self, query: str, data: Dict) -> NoReturn:
        raise _base.NotSupportedError("NetworkX data source has no query method.")

    def _filter_graph(self, key: _GRAPH_KEY_UT) -> List[_GRAPH_KEY_T]:
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
        for graph_name, conditions in graph_cond:
            if graph_name.startswith('@*'):
                for g_n in self._data:
                    result.append(g_n)
                    # TODO: wildcards and filters
            else:
                result.append(graph_name)

        return result

    def _filter_node(self, key: _NODE_KEY_UT) -> List[_NODE_KEY_T]:
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
        for graph_name, node_name, conditions in graph_node_cond:
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
                            result.append((g_n, n_n))
                        # TODO: node filter
                    else:
                        result.append((g_n, node_name))

            else:
                result.append((graph_name, node_name))

        return result

    def _filter_edge(self, key: _EDGE_KEY_UT) -> List[_EDGE_KEY_T]:
        graph_edge_cond: List[Tuple] = []

        if isinstance(key, tuple):
            graph_edge_cond.append((key[0], key[1], None))

        if isinstance(key, list):
            for g_n, e_p in key:
                graph_edge_cond.append((g_n, e_p, None))

        if isinstance(key, dict):
            for (g_n, e_p), cond in key.items():
                graph_edge_cond.append((g_n, e_p, cond))

        result = []
        for graph_name, (node1, node2), conditions in graph_edge_cond:
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
                                result.append((g_n, e_p))
                        elif is_node1_wildcard:  # node2's in_edges
                            if g.has_node(node2):
                                if is_directional:
                                    for e_p in g.in_edges(node2):
                                        result.append((g_n, e_p))
                                else:
                                    # TODO: Warning: graph is not directional, use edges instead
                                    for e_p in g.edges(node2):
                                        result.append((g_n, e_p))
                        elif is_node2_wildcard:  # node1's out_edges
                            if g.has_node(node1):
                                if is_directional:
                                    for e_p in g.out_edges(node1):
                                        result.append((g_n, e_p))
                                else:
                                    for e_p in g.edges(node1):
                                        result.append((g_n, e_p))
                        # TODO: edge filter
                    else:
                        result.append((g_n, (node1, node2)))

            else:
                result.append((graph_name, (node1, node2)))

        return result

    @staticmethod
    def _create_one_graph(val: Dict) -> _Graph:
        type_ = val.get("graph_type", "Graph")
        kwargs = val.get("kwargs", {})
        nodes = val.get("nodes", [])
        edges = val.get("edges", [])

        node_kwargs = val.get("node_kwargs", {})
        edge_kwargs = val.get("edge_kwargs", {})

        graph_init = GRAPH_MAPPING[cast(str, type_)]

        g = graph_init(**cast(dict, kwargs))
        g.add_nodes_from(nodes, **node_kwargs)
        g.add_edges_from(edges, **edge_kwargs)

        return g

    def _update_one_graph(self, graph_name: _GRAPH_T, val: Dict) -> None:
        kwargs = val.get("kwargs", {})
        nodes = val.get("nodes", [])
        edges = val.get("edges", [])

        node_kwargs = val.get("node_kwargs", {})
        edge_kwargs = val.get("edge_kwargs", {})

        self._data[graph_name].graph.update(kwargs)
        self._data[graph_name].add_nodes_from(nodes, **node_kwargs)
        self._data[graph_name].add_edges_from(edges, **edge_kwargs)

    def create_graph(self, key: _GRAPH_KEY_UT = _default_graph_key, val: Dict = {}) -> List[_GRAPH_KEY_T]:
        target = self._filter_graph(key)

        results: List = []
        for graph_name in target:
            self._data[graph_name] = self._create_one_graph(val)
            results.append(graph_name)
            self._dirty_bits.add(graph_name)

        return results

    def create_node(self, key: _NODE_KEY_UT = _default_node_key, val: Dict = {}) -> List[_NODE_KEY_T]:
        target = self._filter_node(key)

        results: List = []
        for graph_name, node_name in target:
            self._data[graph_name].add_node(node_name, **val)
            results.append((graph_name, node_name))
            self._dirty_bits.add(graph_name)

        return results

    def create_edge(self, key: _EDGE_KEY_UT = _default_edge_key, val: Dict = {}) -> List[_EDGE_KEY_T]:
        target = self._filter_edge(key)

        results: List = []
        for graph_name, (node1, node2) in target:
            self._data[graph_name].add_edge(node1, node2, **val)
            results.append((graph_name, (node1, node2)))
            self._dirty_bits.add(graph_name)

        return results

    def read_graph(self, key: _GRAPH_KEY_UT = _wildcard_graph_key) -> Dict[_GRAPH_KEY_T, _Graph]:
        target = self._filter_graph(key)

        result = {}
        for graph_name in target:
            if graph_name in self._data:
                result[graph_name] = self._data[graph_name]

        return result

    def read_node(self, key: _NODE_KEY_UT = _wildcard_node_key) -> Dict[_NODE_KEY_T, Dict]:
        target = self._filter_node(key)

        result = {}
        for g_name, n_name in target:
            if g_name in self._data:
                g = self._data[g_name]
                if g.has_node(n_name):
                    result[(g_name, n_name)] = g.nodes[n_name]

        return result

    def read_edge(self, key: _EDGE_KEY_UT = _wildcard_edge_key) -> Dict[_EDGE_KEY_T, Dict]:
        target = self._filter_edge(key)

        result = {}
        for g_name, (n1_name, n2_name) in target:
            if g_name in self._data:
                g = self._data[g_name]
                if g.has_edge(n1_name, n2_name):
                    result[(g_name, (n1_name, n2_name))] = g.edges[n1_name, n2_name]

        return result

    def update_graph(self, key: _GRAPH_KEY_UT = _default_graph_key, val: Dict = {}) -> List:
        target = self._filter_graph(key)
        result = []
        for graph_name in target:
            self._update_one_graph(graph_name, val)
            result.append(graph_name)
            self._dirty_bits.add(graph_name)

        return result

    def update_node(self, key: _NODE_KEY_UT = _default_node_key, val: Dict = {}) -> List:
        target = self._filter_node(key)
        result = []
        for graph_name, node_name in target:
            self._data[graph_name].nodes[node_name].update(val)
            result.append((graph_name, node_name))
            self._dirty_bits.add(graph_name)

        return result

    def update_edge(self, key: _EDGE_KEY_UT = _default_edge_key, val: Dict = {}) -> List:
        target = self._filter_edge(key)
        result = []
        for graph_name, (node1_name, node2_name) in target:
            self._data[graph_name].edges[node1_name, node2_name].update(val)
            result.append((graph_name, (node1_name, node2_name)))
            self._dirty_bits.add(graph_name)

        return result

    def delete_graph(self, key: _GRAPH_KEY_UT = _default_graph_key) -> int:
        target = self._filter_graph(key)
        result = 0
        for graph_name in target:
            if graph_name in self._data:
                del self._data[graph_name]
                result += 1
                self._dirty_bits.add(graph_name)

        return result

    def delete_node(self, key: _NODE_KEY_UT = _default_node_key) -> int:
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

    def delete_edge(self, key: _EDGE_KEY_UT = _default_edge_key) -> int:
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
