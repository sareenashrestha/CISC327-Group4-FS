import unittest
from app import app

class TestLogin(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    # Test for the page loading properly
    def test_page_load(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
    
    # Testing for when a user successfully logs in, with their email and password in the dummy hashmap
    def test_successful_login(self):
        # Redirecting is false, as the check for the flash message should be done before the redirest
        response = self.app.post('/login', data=dict(username='user1@gmail.com', password='password1'), follow_redirects=False)
        self.assertEqual(response.status_code, 302) # 302 is the status code for redirect

        # This will grab the session data, which will include the flash message, then check if the right flash message is in the session data
        with self.app.session_transaction() as session:
            flashed_messages = dict(session['_flashes'])
            self.assertIn('Login successful!', flashed_messages.values())
        response = self.app.get('/', follow_redirects=True) # Now can follow the redirext

        # Checks for the right page is redirected to and the status code of the response
        self.assertEqual(response.request.path, '/')  
        self.assertEqual(response.status_code, 200)
    
    # Testing for when a user unsuccessfully logs in, with their email and password not in the dummy hashmap
    def test_unsuccessful_login(self):
        # Can follow redirect now because we going back to the login page
        response = self.app.post('/login', data=dict(username='user17@gmail.com', password='asdf'), follow_redirects=True)
        self.assertIn(b'Login failed. Invalid username or password.', response.data)
        self.assertEqual(response.request.path, '/login')
        self.assertEqual(response.status_code, 200)
    
    
    
