import os
import sys
import unittest as ut
from pathlib import Path

root_folder = Path(os.getcwd())
sys.path.append(str(root_folder))


class TestJSONDS(ut.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.jsds = None

    def setUp(self):
        pass

    def test_import(self):
        import data_platform.datasource

        self.jsds = data_platform.datasource.JSONDS

    def test_init(self):
        pass

    def tearDown(self):
        pass


if __name__ == '__main__':
    ut.main()
