import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from server import app
import unittest

class LogoutTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_logout_clears_session(self):
        with self.app.session_transaction() as sess:
            sess['user_id'] = 1
        response = self.app.post('/logout', follow_redirects=True)
        self.assertNotIn('user_id', sess)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
