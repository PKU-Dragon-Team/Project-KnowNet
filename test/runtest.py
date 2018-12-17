import unittest as ut

from test_data_platform import TestJSONDS

TEST_CASES = [TestJSONDS]

if __name__ == '__main__':
    suite = ut.TestSuite(ut.defaultTestLoader.loadTestsFromTestCase(case) for case in TEST_CASES)

    runner = ut.TextTestRunner()
    runner.run(suite)
