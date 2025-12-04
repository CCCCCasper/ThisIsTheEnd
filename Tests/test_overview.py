import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from server import app
import unittest

class OverviewTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_reservations_overview_loads(self):
        response = self.app.get('/reservations')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'reservation', response.data.lower())

if __name__ == '__main__':
    unittest.main()
