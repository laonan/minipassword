import os
import unittest
from minipassword.box import ConfUtils


class TestConfig(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestConfig, self).__init__(*args, **kwargs)

    def test_create_database_file(self):
        util = ConfUtils()
        util.create_database_file()
        if os.path.isfile(util.config_file) and os.path.isfile(util.get('db', 'database_file')):
            self.assertTrue(True)
        else:
            self.assertTrue(False)


if __name__ == '__main__':
    unittest.main()
