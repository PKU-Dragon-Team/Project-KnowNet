import unittest as ut
import tempfile


class BaseTestDataSource(ut.TestCase):
    @classmethod
    def get_test_class(cls):
        """Import and return the test class"""

        raise NotImplementedError

    def get_test_instance(self, temp_location):
        """Initialize and return the test class.
        Use temp_location as storage if necessary"""

        raise NotImplementedError

    def setUp(self):
        """Optional initalizations."""

    def test_import(self):
        self.assertIsNotNone(self.get_test_class())

    def test_init(self):
        with tempfile.TemporaryDirectory(prefix='test_', suffix='_ds') as tmpdir:
            self.assertIsNotNone(self.get_test_instance(tmpdir))

    def tearDown(self):
        """Optional finalizations."""
