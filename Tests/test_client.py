import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from server import app
import unittest

class ClientTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_clients_page_loads(self):
        response = self.app.get('/clients')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'client', response.data.lower())

    # Voeg hier meer tests toe voor client functionaliteit, edge cases, etc.

if __name__ == '__main__':
    unittest.main()
