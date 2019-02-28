import unittest as ut

from test.test_data_platform.doc import TestJSONDS, TestMongoDBDS
from test.test_data_platform.graph import TestNetworkXDS
from test.test_data_platform.row import TestSQLiteDS
from test.test_data_platform.config import TestConfig

from data_platform.config import get_global_config

TEST_CASES = [TestJSONDS, TestSQLiteDS, TestNetworkXDS, TestConfig]

global_config = get_global_config()

if global_config.check_node(['test', 'mongodb']):
    TEST_CASES.append(TestMongoDBDS)

if __name__ == '__main__':
    suite = ut.TestSuite(ut.defaultTestLoader.loadTestsFromTestCase(case) for case in TEST_CASES)

    runner = ut.TextTestRunner()
    runner.run(suite)
