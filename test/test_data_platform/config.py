import unittest as ut


class TestConfig(ut.TestCase):
    def test_global_config(self):
        from data_platform.config import get_global_config, ConfigDicts

        site_wise = {
            'a': 0,
            'b': 0,
            'c': 0
        }
        user = {
            'b': 1,
            'c': 1,
            'd': 1
        }
        local = {
            'c': 2,
            'e': 2
        }
        config_dicts = ConfigDicts(site_wise, user, local)

        result = {
            'a': 0,
            'b': 1,
            'c': 2,
            'd': 1,
            'e': 2
        }

        self.assertEqual(get_global_config(config_dicts), result)
