from data_platform.datasource.abc.graph import EdgeNamePair, EdgeKeyPair, GraphValType, NodeKeyPair

SAMPLE_GRAPH1 = GraphValType(
    graph_type="Graph",
    attr={"graph_name": "Sample Graph 1"},
    nodes=[0, 1, 2, 3, 'foo', 'baz'],
    edges=[EdgeNamePair(0, 1), EdgeNamePair(1, 2), EdgeNamePair(2, 3),
           EdgeNamePair(1, 'foo'), EdgeNamePair(0, 'baz')],
    node_attr={
        'color': 'red',
        'page_rank': 5
    },
    edge_attr={'weight': 0.5})

SAMPLE_GRAPH2 = GraphValType(
    graph_type="DiGraph",
    attr={"graph_name": "Sample Graph 2"},
    nodes=[0, 1, 2, 3, 'foo', 'baz'],
    edges=[EdgeNamePair(0, 1),
           EdgeNamePair(1, 2),
           EdgeNamePair(2, 0),
           EdgeNamePair(2, 3),
           EdgeNamePair(3, 2),
           EdgeNamePair(1, 'foo'),
           EdgeNamePair(0, 'baz')],
    node_attr={
        'color': 'green',
        'page_rank': 3
    },
    edge_attr={'weight': 0.1})

SAMPLE_NODE = NodeKeyPair('foo', 0)
SAMPLE_EDGE = EdgeKeyPair('foo', EdgeNamePair(0, 2))

EXPECTED_NODES = {
    NodeKeyPair(graph_name='_default', node_name=0): {
        'color': 'red',
        'page_rank': 5
    },
    NodeKeyPair(graph_name='_default', node_name=1): {
        'color': 'red',
        'page_rank': 5
    },
    NodeKeyPair(graph_name='_default', node_name=2): {
        'color': 'red',
        'page_rank': 5
    },
    NodeKeyPair(graph_name='_default', node_name=3): {
        'color': 'red',
        'page_rank': 5
    },
    NodeKeyPair(graph_name='_default', node_name='foo'): {
        'color': 'red',
        'page_rank': 5
    },
    NodeKeyPair(graph_name='_default', node_name='baz'): {
        'color': 'red',
        'page_rank': 5
    },
    NodeKeyPair(graph_name='graph2', node_name=0): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph2', node_name=1): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph2', node_name=2): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph2', node_name=3): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph2', node_name='foo'): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph2', node_name='baz'): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph3', node_name=0): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph3', node_name=1): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph3', node_name=2): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph3', node_name=3): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph3', node_name='foo'): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph3', node_name='baz'): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph4', node_name=0): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph4', node_name=1): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph4', node_name=2): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph4', node_name=3): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph4', node_name='foo'): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph4', node_name='baz'): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='foo', node_name=0): {
        'blah': True
    },
    NodeKeyPair(graph_name='foo', node_name=2): {}
}

EXPECTED_NODES_FILTERED = {
    NodeKeyPair(graph_name='_default', node_name=0): {
        'color': 'red',
        'page_rank': 5
    },
    NodeKeyPair(graph_name='graph2', node_name=0): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph3', node_name=0): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph4', node_name=0): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='foo', node_name=0): {
        'blah': True
    }
}

EXPECTED_EDGES = {
    EdgeKeyPair(graph_name='_default', edge_name=EdgeNamePair(node1=0, node2=1)): {
        'weight': 0.5
    },
    EdgeKeyPair(graph_name='_default', edge_name=EdgeNamePair(node1=0, node2='baz')): {
        'weight': 0.5
    },
    EdgeKeyPair(graph_name='_default', edge_name=EdgeNamePair(node1=1, node2=2)): {
        'weight': 0.5
    },
    EdgeKeyPair(graph_name='_default', edge_name=EdgeNamePair(node1=1, node2='foo')): {
        'weight': 0.5
    },
    EdgeKeyPair(graph_name='_default', edge_name=EdgeNamePair(node1=2, node2=3)): {
        'weight': 0.5
    },
    EdgeKeyPair(graph_name='graph2', edge_name=EdgeNamePair(node1=0, node2=1)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph2', edge_name=EdgeNamePair(node1=0, node2='baz')): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph2', edge_name=EdgeNamePair(node1=1, node2=2)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph2', edge_name=EdgeNamePair(node1=1, node2='foo')): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph2', edge_name=EdgeNamePair(node1=2, node2=0)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph2', edge_name=EdgeNamePair(node1=2, node2=3)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph2', edge_name=EdgeNamePair(node1=3, node2=2)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph3', edge_name=EdgeNamePair(node1=0, node2=1)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph3', edge_name=EdgeNamePair(node1=0, node2='baz')): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph3', edge_name=EdgeNamePair(node1=1, node2=2)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph3', edge_name=EdgeNamePair(node1=1, node2='foo')): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph3', edge_name=EdgeNamePair(node1=2, node2=0)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph3', edge_name=EdgeNamePair(node1=2, node2=3)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph3', edge_name=EdgeNamePair(node1=3, node2=2)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph4', edge_name=EdgeNamePair(node1=0, node2=1)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph4', edge_name=EdgeNamePair(node1=0, node2='baz')): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph4', edge_name=EdgeNamePair(node1=1, node2=2)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph4', edge_name=EdgeNamePair(node1=1, node2='foo')): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph4', edge_name=EdgeNamePair(node1=2, node2=0)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph4', edge_name=EdgeNamePair(node1=2, node2=3)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph4', edge_name=EdgeNamePair(node1=3, node2=2)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='foo', edge_name=EdgeNamePair(node1=0, node2=2)): {
        'baz': False
    }
}

EXPECTED_EDGES_FILTERED = {
    EdgeKeyPair(graph_name='_default', edge_name=EdgeNamePair(node1=0, node2=1)): {
        'weight': 0.5
    },
    EdgeKeyPair(graph_name='_default', edge_name=EdgeNamePair(node1=0, node2='baz')): {
        'weight': 0.5
    },
    EdgeKeyPair(graph_name='graph2', edge_name=EdgeNamePair(node1=2, node2=0)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph3', edge_name=EdgeNamePair(node1=2, node2=0)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph4', edge_name=EdgeNamePair(node1=2, node2=0)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='foo', edge_name=EdgeNamePair(node1=0, node2=2)): {
        'baz': False
    }
}

UPDATE_GRAPH_VAL = GraphValType(
    attr={'graph_title': 'A New Graph'},
    nodes=[7, 8, 9],
    edges=[EdgeNamePair(7, 8), EdgeNamePair(9, 7)],
    node_attr={'role': 'follower'},
    edge_attr={'create_date': '2018-01-20'})

UPDATE_NODE_RESULT = [NodeKeyPair(graph_name='foo', node_name=0)]
UPDATE_NODE_READ = {NodeKeyPair(graph_name='foo', node_name=0): {'blah': True, 'build': 'yes'}}
UPDATE_EDGE_RESULT = [EdgeKeyPair(graph_name='foo', edge_name=EdgeNamePair(node1=0, node2=2))]
UPDATE_EDGE_READ = {EdgeKeyPair(graph_name='foo', edge_name=EdgeNamePair(node1=0, node2=2)): {'baz': False, 'hello': 'world'}}

DELETE_NODE_READ = {
    NodeKeyPair(graph_name='graph2', node_name=1): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph2', node_name=2): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph2', node_name=3): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph2', node_name='foo'): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph2', node_name='baz'): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph3', node_name=1): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph3', node_name=2): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph3', node_name=3): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph3', node_name='foo'): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph3', node_name='baz'): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph4', node_name=1): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph4', node_name=2): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph4', node_name=3): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph4', node_name='foo'): {
        'color': 'green',
        'page_rank': 3
    },
    NodeKeyPair(graph_name='graph4', node_name='baz'): {
        'color': 'green',
        'page_rank': 3
    }
}
DELETE_EDGE_READ = {
    EdgeKeyPair(graph_name='graph2', edge_name=EdgeNamePair(node1=1, node2=2)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph2', edge_name=EdgeNamePair(node1=1, node2='foo')): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph2', edge_name=EdgeNamePair(node1=3, node2=2)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph3', edge_name=EdgeNamePair(node1=1, node2=2)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph3', edge_name=EdgeNamePair(node1=1, node2='foo')): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph3', edge_name=EdgeNamePair(node1=3, node2=2)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph4', edge_name=EdgeNamePair(node1=1, node2=2)): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph4', edge_name=EdgeNamePair(node1=1, node2='foo')): {
        'weight': 0.1
    },
    EdgeKeyPair(graph_name='graph4', edge_name=EdgeNamePair(node1=3, node2=2)): {
        'weight': 0.1
    }
}
