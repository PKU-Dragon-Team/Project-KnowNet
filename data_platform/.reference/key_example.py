"""Example of acceptable key.

# naming style:

- name and content: "docset"
- hidden property and metadata: "$title"
- operator and other magics: "@any"
"""

doc_key0 = ('_default', '_default')
doc_key1 = [('pep', 'pep001'), ('pep', 'pep484'), ('foo', 'baz')]
doc_key = {  # type: ignore
    ("docset1", "doc1"): {},  # identical key
    ("docset2", "@*"): {  # @* means wildcards, good for filtering the whole set, only wildcards can contain filtering conditions
        "$title": {}  # empty dict means check for property existance
    },
    ("docset3", "@*"): {
        "$sections": {
            "$section": {
                "$section_title": {}  # nested conditon to check deeper path
            }
        }
    },
    ("@*", "@*"): {  # docset can also use wildcards
        "$author": "Taylor Swift",  # plain condition will use equal(`==`) to compare  # yapf: disable
        "$title": {
            "@re": "*Blank Space*"  # @re will consider as regular expressions
        },
        "$publish_year": {
            "@range": [2011, 2018]  # @range take a list of two arguments, left is included but right is exclued
        },
        "$length": {
            "@range": [10, '']  # use empty value (`__bool__() == False`) to not check this end
        }
    }
}

graph_key0 = ('graph0')
graph_key1 = [('graph1'), ('graph2'), ('graphfoo')]
graph_key = {  # type: ignore
    "graph1": {},  # only name
    "@*": {
        "$node_count": {
            "@range": [100, 5000]
        }
    },
    "@*foo": {
        "$edge_list": {
            "@sum": {  # @sum to collect a bunch of data
                "@foreach": {  # @foreach to compute everyone
                    "@function": lambda edge: edge.weight
                }
            }
        }
    }
}

node_key0 = ('graph1', '@*')
node_key1 = [('graph1', 'node7'), ('graph2', 'node5'), ('graphfoo', 'nodebaz')]
node_key = {  # type: ignore
    ("graph1", "node1"): {},
    ("graph2", "@*"): {
        "$degree": {
            "@range": [10, None]
        }
    },
    ("graph3", "@*"): {
        "$neighbors": {
            "@any": {  # @any to combine multiple conditions, similar one is @all
                "@foreach": {  # @foreach to check inside a container
                    "@function": lambda neighbor: neighbor.PageRank > 1
                }
            }
        }
    }
}

edge_key0 = ('graph0', ('node1', 'node2'))
edge_key1 = [('graph1', ('node2', 'node5')), ('graph4', ('node1', '@*')), ('graphfoo', ('@*', 'nodebaz'))]
edge_key = {  # type: ignore
    ("graph1", ("node1", "node2")): {},  # edge is found by pair of nodes
    ("graph2", ("@*", "@*")): {  # wildcards also works for edges
        "@function": lambda edge: edge.weight > 1
    },
    ("graph3", ("@*", "node1")): {},  # edges go into node1
    ("graph4", ("node2", "@*")): {}  # edges go out from node2
}

row_key0 = ('table1', 'row1')
row_key1 = [('tablepep', 'pep001'), ('tablepep', 'pep484'), ('tablefoo', 'rowbaz')]
row_key = {  # type: ignore
    ("table1", "row1"): {},  # row key
    ("talbe2", "@*"): {  # wildcards
        "$docset": "docset1",  # column name starts with $
        "$length": {
            "@function": lambda len: len > 10 and len < 200 and len % 3 == 0
        }
    }
}
