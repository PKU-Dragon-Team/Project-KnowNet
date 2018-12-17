import unittest as ut

from test.test_data_platform.doc import TestJSONDS
from test.test_data_platform.graph import TestNetworkXDS
from test.test_data_platform.row import TestSQLiteDS

TEST_CASES = [TestJSONDS, TestSQLiteDS, TestNetworkXDS]

if __name__ == '__main__':
    suite = ut.TestSuite(ut.defaultTestLoader.loadTestsFromTestCase(case) for case in TEST_CASES)

    runner = ut.TextTestRunner()
    runner.run(suite)
