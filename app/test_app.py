import unittest
from app import app

class TestLogin(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_page_load(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
    
    
    def test_successful_login(self):
        response = self.app.post('/login', data=dict(username='user1', password='password1'), follow_redirects=True)
        self.assertIn(b'Login successful!', response.data)
    
    def test_unsuccessful_login(self):
        response = self.app.post('/login', data=dict(username='user1', password='asdf'), follow_redirects=True)
        self.assertIn(b'Login failed. Invalid username or password.', response.data)
    
    
    
