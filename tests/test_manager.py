import os
import random
import unittest
from minipassword.box import PasswordManager


class TestPasswordManager(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(TestPasswordManager, self).__init__(*args, **kwargs)
        self.password_manager = PasswordManager()

    def test_add_password(self):
        result = self.password_manager.add_password(f'mypassword{random.randint(1, 1000)}', 'mypassword', 'mypassword')
        print('Add Password done!')
        self.assertIsNone(result)

    def test_get_password(self):
        result = self.password_manager.get_password('test')
        print('Get Password:')
        print(result)
        self.assertIsNotNone(result)

    def test_get_all_password(self):
        result = self.password_manager.get_all_passwords()
        print('Get All Passwords:')
        print(result)
        self.assertIsNotNone(result)

    def test_update_password(self):
        try:
            self.password_manager.update_password(1, 'updatedpassword', 'updatedpassword', 'updatedpassword')
            result = self.password_manager.get_password('updatedpassword')
            print('Update Password done!')
            print(result)
            self.assertTrue(True)
        except Exception as e:
            print(e)
            self.assertTrue(False)

    def test_delete_password(self):
        try:
            self.password_manager.delete_password(1)
            result = self.password_manager.get_all_passwords()
            print('Delete Password done!')
            print(result)
            self.assertTrue(True)
        except Exception as e:
            print(e)
            self.assertTrue(False)


if __name__ == '__main__':
    unittest.main()
