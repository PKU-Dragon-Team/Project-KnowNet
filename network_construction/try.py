# encoding:utf-8
from data_platform.config import ConfigManager
from data_platform.datasource.networkx import NetworkXDS, GraphValType
from pathlib import Path
import os


def init():
    current_location = Path(os.getcwd())
    data_location = current_location / 'data'
    graph_location = data_location / 'graph'
    config = ConfigManager({
        "init": {
            "location": graph_location
        },
        'file_format': 'graphml'
    })
    return NetworkXDS(config)

nxds = init()
sample_graph1 = GraphValType(
    graph_type="Graph",
    attr={
        "graph_name": "Sample Graph 1"
    },
    nodes=[
        0,
        1,
        2,
        3,
        'foo',
        'baz'
    ],
    edges=[
        (0, 1),
        (1, 2),
        (2, 3),
        (1, 'foo'),
        (0, 'baz')
    ],
    node_attr={
        'color': 'red',
        'page_rank': 5
    },
    edge_attr={
        'weight': 0.5
    }
)

sample_graph2 = GraphValType(
    graph_type="DiGraph",
    attr={
        "graph_name": "Sample Graph 2"
    },
    nodes=[
        0,
        1,
        2,
        3,
        'foo',
        'baz'
    ],
    edges=[
        (0, 1),
        (1, 2),
        (2, 0),
        (2, 3),
        (3, 2),
        (1, 'foo'),
        (0, 'baz')
    ],
    node_attr={
        'color': 'green',
        'page_rank': 3
    },
    edge_attr={
        'weight': 0.1
    }
)

sample_node = ('foo', 0)
sample_edge = ('foo', (0, 2))
nxds.create_graph(val=sample_graph1)
nxds.create_graph(key=['graph2', 'graph3', 'graph4'], val=sample_graph2)
nxds.create_graph(key='foo')
nxds.create_node(sample_node, val={'blah': True})
print(nxds.read_node(sample_node))
