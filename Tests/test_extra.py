import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from server import app
import unittest

class ExtraOptionTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_extra_options_page_loads(self):
        response = self.app.get('/extra')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'extra', response.data.lower())

if __name__ == '__main__':
    unittest.main()
