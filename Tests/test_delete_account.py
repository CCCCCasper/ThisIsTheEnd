import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from server import app
import unittest

class DeleteAccountTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_delete_account_requires_login(self):
        response = self.app.post('/delete_account', follow_redirects=True)
        self.assertIn(b'login', response.data.lower())

if __name__ == '__main__':
    unittest.main()
