"""Data source for row storage using sqlite3.

Support multiple tables (datasets)
"""

import json
import sqlite3
from typing import Dict, List, Set, Text, Tuple, Generator
from contextlib import contextmanager

from ..config import ConfigManager
from .abc.row import RowDataSource, RowKeyPair, RowKeyType, RowValDict


class SQLiteDS(RowDataSource):
    """Class of SQLite Data Source."""

    CONFIG_SCHEMA = {"init": {"location": {}}}

    def __init__(self, config: ConfigManager, *args, **kwargs) -> None:
        """Initialize the data source.

        `config` schema:
        - 'init': initialize parameters
            - 'location': "the location of db file"."

        """
        super().__init__(config, *args, **kwargs)

        config.check_schema(SQLiteDS.CONFIG_SCHEMA)
        loc = config.check_get(['init', 'location'])
        self._loc = loc
        self._tables: Set = set()

    @contextmanager
    def connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self._loc)
        try:
            yield conn
        finally:
            conn.close()

    def create_table(self, table_name: Text) -> None:
        with self.connect() as conn:
            if table_name not in self._tables:
                conn.execute(f"CREATE TABLE IF NOT EXISTS {table_name}(row_key TEXT UNIQUE, json TEXT)")
                self._tables.add(table_name)
            conn.commit()

    def delete_table(self, table_name: Text) -> None:
        with self.connect() as conn:
            if table_name in self._tables:
                conn.execute(f"DROP TABLE {table_name}")
                self._tables.remove(table_name)
            conn.commit()

    def _filter(self, key: RowKeyType) -> List[RowKeyPair]:
        table_row_con: List[Tuple[Text, Text, Dict]] = []
        if isinstance(key, tuple):
            table_row_con.append((key[0], key[1], {}))
        elif isinstance(key, list):
            table_row_con.extend((k[0], k[1], {}) for k in key)
        elif isinstance(key, dict):
            table_row_con.extend((k[0], k[1], con) for k, con in key.items())

        result = []
        for table_name, row_name, _ in table_row_con:
            if table_name.startswith('@*'):
                # TODO: table filters
                target_tables = list(self._tables)
            else:
                if table_name not in self._tables:
                    raise KeyError(f'No table named {table_name}')
                else:
                    target_tables = [table_name]

            for target_table in target_tables:
                with self.connect() as conn:
                    if isinstance(row_name, str) and row_name.startswith('@*'):
                        rows = conn.execute(f'SELECT row_key, json FROM {target_table}').fetchall()
                        # TODO: row wildcard filters
                        result.extend(RowKeyPair(target_table, row[0]) for row in rows)
                    else:
                        result.append(RowKeyPair(target_table, row_name))

        return result

    def create_row(self, key: RowKeyType, val: RowValDict) -> List[RowKeyPair]:
        result = []
        target = self._filter(key)
        with self.connect() as conn:
            for table_name, row_key in target:
                conn.execute(f"REPLACE INTO {table_name} VALUES (?,?)", (row_key, json.dumps(val)))
                result.append(RowKeyPair(table_name, row_key))
            conn.commit()
        return result

    def read_row(self, key: RowKeyType = ('@*', '@*')) -> Dict[RowKeyPair, RowValDict]:
        result = {}
        target = self._filter(key)
        with self.connect() as conn:
            for table_name, row_key in target:
                target_row = conn.execute(f'SELECT json FROM {table_name} WHERE row_key = ?', (row_key, )).fetchone()
                if target_row is not None:
                    raw_json = target_row[0]
                    parsed_json = json.loads(raw_json)
                    result[RowKeyPair(table_name, row_key)] = parsed_json
        return result

    def update_row(self, key: RowKeyType, val: RowValDict) -> List[RowKeyPair]:
        result = []
        target = self._filter(key)
        with self.connect() as conn:
            for table_name, row_key in target:
                target_row = conn.execute(f'SELECT json FROM {table_name} WHERE row_key = ?', (row_key, )).fetchone()
                if target_row is not None:
                    raw_json = target_row[0]
                    parsed_json = json.loads(raw_json)
                    parsed_json.update(val)
                else:
                    parsed_json = val
                conn.execute(f"REPLACE INTO {table_name} VALUES (?,?)", (row_key, json.dumps(parsed_json)))
                result.append(RowKeyPair(table_name, row_key))
            conn.commit()
        return result

    def delete_row(self, key: RowKeyType) -> int:
        result = 0
        target = self._filter(key)
        with self.connect() as conn:
            for table_name, row_key in target:
                conn.execute(f'DELETE FROM {table_name} WHERE row_key = ?', (row_key, ))
                result += 1
            conn.commit()
        return result

    def query(self, query: str, *args, **kwargs) -> List:
        with self.connect() as conn:
            result = conn.executescript(query).fetchall()
        return result
