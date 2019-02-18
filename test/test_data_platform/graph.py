import os
import sys
import tempfile
from pathlib import Path

from . import _constant
from .base import BaseTestDataSource

root_folder = Path(os.getcwd())
sys.path.append(str(root_folder))


class TestGraphDataSource(BaseTestDataSource):
    def test_all(self):
        with tempfile.TemporaryDirectory(prefix='test_', suffix='_rowds') as tmpdir:
            ds = self.get_test_instance(tmpdir)
            # create
            self.assertEqual(ds.create_graph(val=_constant.SAMPLE_GRAPH1), ['_default'])
            self.assertCountEqual(ds.create_graph(key=['graph2', 'graph3', 'graph4'], val=_constant.SAMPLE_GRAPH2), ['graph2', 'graph3', 'graph4'])
            self.assertEqual(ds.create_graph(key='foo'), ['foo'])
            self.assertEqual(ds.create_node(_constant.SAMPLE_NODE, val={'blah': True}), [('foo', 0)])
            self.assertEqual(ds.create_edge(_constant.SAMPLE_EDGE, {'baz': False}), [('foo', (0, 2))])

            # read
            self.assertSetEqual(set(ds.read_graph().keys()), set(('_default', 'graph2', 'graph3', 'graph4', 'foo')))
            self.assertEqual(ds.read_graph('_default')['_default'].graph, {'graph_name': 'Sample Graph 1'})
            self.assertEqual(ds.read_node(), _constant.EXPECTED_NODES)
            self.assertEqual(ds.read_node(('@*', 0)), _constant.EXPECTED_NODES_FILTERED)
            self.assertEqual(ds.read_edge(), _constant.EXPECTED_EDGES)
            self.assertEqual(ds.read_edge(('@*', ('@*', 0))), _constant.EXPECTED_EDGES_FILTERED)

            # update
            self.assertEqual(ds.update_graph(val=_constant.UPDATE_GRAPH_VAL), ['_default'])
            self.assertEqual(ds.read_graph('_default')['_default'].graph, {'graph_name': 'Sample Graph 1', 'graph_title': 'A New Graph'})
            self.assertEqual(ds.update_node(('foo', 0), {'build': 'yes'}), _constant.UPDATE_NODE_RESULT)
            self.assertEqual(ds.read_node(('foo', 0)), _constant.UPDATE_NODE_READ)
            self.assertEqual(ds.update_edge(('foo', (0, 2)), {'hello': 'world'}), _constant.UPDATE_EDGE_RESULT)
            self.assertEqual(ds.read_edge(('foo', (0, 2))), _constant.UPDATE_EDGE_READ)

            # delete
            self.assertEqual(ds.delete_graph('foo'), 1)
            self.assertSetEqual(set(ds.read_graph().keys()), set(['_default', 'graph2', 'graph3', 'graph4']))
            self.assertEqual(ds.delete_graph(), 1)
            self.assertSetEqual(set(ds.read_graph().keys()), set(['graph2', 'graph3', 'graph4']))
            self.assertEqual(ds.delete_node(('@*', 0)), 3)
            self.assertEqual(ds.read_node(), _constant.DELETE_NODE_READ)
            self.assertEqual(ds.delete_edge(('@*', (2, '@*'))), 3)
            self.assertEqual(ds.read_edge(), _constant.DELETE_EDGE_READ)

            ds.flush()
            ds.clear()
            ds.reload()

            del ds


class TestNetworkXDS(TestGraphDataSource):
    @classmethod
    def get_test_class(cls):
        from data_platform.datasource import NetworkXDS

        return NetworkXDS

    def get_test_instance(self, temp_location):
        from data_platform.config import ConfigManager
        from data_platform.datasource import NetworkXDS

        config = ConfigManager({"init": {"location": temp_location}})
        ds = NetworkXDS(config)
        return ds
