import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from server import app, get_db_connection
import unittest

class FlashMessageTests(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Maak een testgebruiker aan
        conn = get_db_connection()
        conn.execute('DELETE FROM users WHERE username = ?', ('testuser',))
        conn.execute('INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)',
                     ('testuser', 'testpass', 'client', 'test@example.com'))
        conn.commit()
        conn.close()

    def tearDown(self):
        # Verwijder testgebruiker
        conn = get_db_connection()
        conn.execute('DELETE FROM users WHERE username = ?', ('testuser',))
        conn.commit()
        conn.close()

    def test_flash_message_on_failed_login(self):
        response = self.app.post('/login', data={'username': 'testuser', 'password': 'wrongpass'}, follow_redirects=True)
        self.assertIn(b'incorrect password', response.data.lower())

if __name__ == '__main__':
    unittest.main()
