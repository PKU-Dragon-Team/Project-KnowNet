"""data source for row storage using sqlite
"""

import sqlite3
from typing import Dict, List

from . import base as _base


class SQLiteDS(_base.RowDataSource):
    def create_row(self, key: Dict, val: Dict) -> List:
        pass

    def read_row(self, key: Dict) -> Dict:
        pass

    def update_row(self, key: Dict, val: Dict) -> List:
        pass

    def delete_row(self, key: Dict) -> int:
        pass
