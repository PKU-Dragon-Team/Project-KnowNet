import os
import sys
import unittest as ut
from pathlib import Path

root_folder = Path(os.getcwd())
sys.path.append(str(root_folder))


class TestDataFetcher(ut.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def setUp(self):
        pass

    def test_fetch(self):
        pass

    def tearDown(self):
        pass
