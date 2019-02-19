import os
import sys
import tempfile
from itertools import chain
from pathlib import Path

from .base import BaseTestDataSource

root_folder = Path(os.getcwd())
sys.path.append(str(root_folder))

SAMPLE_TABLE1 = {
    ('table1', "row1"): {
        "col1": 1,
        "col2": 2,
        "col3": 3,
        "col4": 4,
        "col5": 5
    },
    ('table1', "row2"): {
        "col2": 2,
        "col3": 3,
        "col4": 4,
        "col5": 5,
        "col6": 6,
        'foo': 'baz'
    },
    ('table1', "go_user1"): {
        'name': 'player',
        'nickname': 'boo',
        'from': 'pa',
        'li': ['unique', 'foo']
    },
    ('table1', "matrix1"): {
        'content': [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    }
}

SAMPLE_TABLE2 = {
    ('table2', "1"): {
        "col1": 1,
        "col2": 2,
        "col3": 3,
        "col4": 4,
        "col5": 5
    },
    ('table2', "22"): {
        "col2": 2,
        "col3": 3,
        "col4": 4,
        "col5": 5,
        "col6": 6,
        'foo': 'baz'
    },
    ('table2', "333"): {
        'name': 'player',
        'nickname': 'boo',
        'from': 'pa',
        'li': ['unique', 'foo']
    },
    ('table2', "4444"): {
        'content': [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    }
}


class TestRowDataSource(BaseTestDataSource):
    def test_all(self):
        from data_platform.datasource.abc.row import RowKeyPair

        with tempfile.TemporaryDirectory(prefix='test_', suffix='_rowds') as tmpdir:
            ds = self.get_test_instance(tmpdir)
            ds.create_table('table1')
            ds.create_table('table2')

            for row_key, row_data in chain(SAMPLE_TABLE1.items(), SAMPLE_TABLE2.items()):
                self.assertEqual(ds.create_row(row_key, row_data), [RowKeyPair(table_name=row_key[0], row_name=row_key[1])])

            self.assertEqual(
                ds.read_row(), {
                    RowKeyPair(table_name='table2', row_name='1'): {
                        'col1': 1,
                        'col2': 2,
                        'col3': 3,
                        'col4': 4,
                        'col5': 5
                    },
                    RowKeyPair(table_name='table2', row_name='22'): {
                        'col2': 2,
                        'col3': 3,
                        'col4': 4,
                        'col5': 5,
                        'col6': 6,
                        'foo': 'baz'
                    },
                    RowKeyPair(table_name='table2', row_name='333'): {
                        'name': 'player',
                        'nickname': 'boo',
                        'from': 'pa',
                        'li': ['unique', 'foo']
                    },
                    RowKeyPair(table_name='table2', row_name='4444'): {
                        'content': [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
                    },
                    RowKeyPair(table_name='table1', row_name='row1'): {
                        'col1': 1,
                        'col2': 2,
                        'col3': 3,
                        'col4': 4,
                        'col5': 5
                    },
                    RowKeyPair(table_name='table1', row_name='row2'): {
                        'col2': 2,
                        'col3': 3,
                        'col4': 4,
                        'col5': 5,
                        'col6': 6,
                        'foo': 'baz'
                    },
                    RowKeyPair(table_name='table1', row_name='go_user1'): {
                        'name': 'player',
                        'nickname': 'boo',
                        'from': 'pa',
                        'li': ['unique', 'foo']
                    },
                    RowKeyPair(table_name='table1', row_name='matrix1'): {
                        'content': [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
                    }
                })
            self.assertCountEqual(
                ds.update_row(('@*', 'row1'), {'new_column': 1}),
                [RowKeyPair(table_name='table2', row_name='row1'),
                 RowKeyPair(table_name='table1', row_name='row1')])
            self.assertEqual(
                ds.read_row(('table1', 'row1')),
                {
                    RowKeyPair(table_name='table1', row_name='row1'): {
                        'col1': 1,
                        'col2': 2,
                        'col3': 3,
                        'col4': 4,
                        'col5': 5,
                        'new_column': 1
                    }
                })
            self.assertEqual(ds.delete_row(('table1', '@*')), 4)
            self.assertEqual(
                ds.read_row(), {
                    RowKeyPair(table_name='table2', row_name='1'): {
                        'col1': 1,
                        'col2': 2,
                        'col3': 3,
                        'col4': 4,
                        'col5': 5
                    },
                    RowKeyPair(table_name='table2', row_name='22'): {
                        'col2': 2,
                        'col3': 3,
                        'col4': 4,
                        'col5': 5,
                        'col6': 6,
                        'foo': 'baz'
                    },
                    RowKeyPair(table_name='table2', row_name='333'): {
                        'name': 'player',
                        'nickname': 'boo',
                        'from': 'pa',
                        'li': ['unique', 'foo']
                    },
                    RowKeyPair(table_name='table2', row_name='4444'): {
                        'content': [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
                    },
                    RowKeyPair(table_name='table2', row_name='row1'): {
                        'new_column': 1
                    }
                })
            ds.delete_table('table1')
            ds.delete_table('table2')


class TestSQLiteDS(TestRowDataSource):
    @classmethod
    def get_test_class(cls):
        from data_platform.datasource import SQLiteDS

        return SQLiteDS

    def get_test_instance(self, temp_location):
        from data_platform.config import ConfigManager
        from data_platform.datasource import SQLiteDS

        config = ConfigManager({"init": {"location": os.path.join(temp_location, 'data.db')}})
        ds = SQLiteDS(config)
        return ds
