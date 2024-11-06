import unittest
from app import app, get_db_connection, generate_password_hash
import init_database


BASE_URL = "http://localhost:5000"
init_database.init_db()

class TestLogin(unittest.TestCase):
    
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Connect to database and clear any data before each test
        conn = get_db_connection()
        conn.execute("DELETE FROM users")
        conn.commit()


        # Insert dummy data into the database
        try:
            passHash = generate_password_hash('Password1!')
            conn.execute('''
                INSERT INTO users (email, password, first_name, last_name, dob, gender, phone, address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', ('user1@gmail.com', passHash, "First", "Last", "2000-06-20", "male", "1234567890", "123 Random St"))
            conn.commit()
        except:
            pass

    # Test for the page loading properly
    def test_page_load(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
    
    # Testing for when a user successfully logs in, with their email and password in the dummy hashmap
    def test_successful_login(self):
        # Redirecting is false, as the check for the flash message should be done before the redirest
        response = self.app.post('/login', data=dict(username='user1@gmail.com', password='Password1!'), follow_redirects=False)
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

class TestRegistration(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # clear the database before each test
        with get_db_connection() as conn:
            conn.execute("DELETE FROM users")
            conn.commit()
    
    # test for the page loading properly
    def test_page_load(self):
        response = self.app.get('/register')
        self.assertEqual(response.status_code, 200)
    
    # test for when a user successfully registers
    def test_successful_registration(self):
        response = self.app.post('/register', data=dict(
            email='validemail@example.com',
            password='P@ssw0rd1',
            first_name='First',
            last_name='Last',
            dob='2000-06-20',
            gender='male',
            phone='1234567890',
            address='123 Random St',
            termsCheck='on'
        ), follow_redirects=True)
       
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email Address', response.data)

        with get_db_connection() as conn:
            user = conn.execute("SELECT * FROM users WHERE email = ?", ('validemail@example.com',)).fetchone()
            self.assertIsNotNone(user)

    # test for when the same email is registered twice
    def test_duplicate_email_registration(self):
        # register a user for the first time
        self.app.post('/register', data=dict(
            email='duplicate@example.com',
            password='P@ssw0rd1',
            first_name='First',
            last_name='Last',
            dob='2000-06-20',
            gender='male',
            phone='1234567890',
            address='123 Random St',
            termsCheck='on'
        ), follow_redirects=True)

        # attempt to register with the same email again
        response = self.app.post('/register', data=dict(
            email='duplicate@example.com',
            password='P@ssw0rd!2',
            first_name='FirstAgain',
            last_name='LastAgain',
            dob='1999-08-19',
            gender='male',
            phone='3233213223',
            address='456 Another St',
            termsCheck='on'
        ), follow_redirects=True)

        # verify duplicate email error
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email already registered.', response.data)
        
    # test for when a user enters an invalid email
    def test_invalid_email(self):
        response = self.app.post('/register', data=dict(
            email='@example.com',
            password='P@ssw0rd1',
            first_name='First',
            last_name='Last',
            dob='2000-06-20',
            gender='male',
            phone='1234567890',
            address='123 Random St',
            termsCheck='on'
        ), follow_redirects=True)
        self.assertIn(b'Invalid email address.', response.data)
    
    # test for when a user enters an invalid password
    def test_invalid_password(self):
        response = self.app.post('/register', data=dict(
            email='validemail@example.com',
            password='password',
            first_name='First',
            last_name='Last',
            dob='2000-06-20',
            gender='male',
            phone='1234567890',
            address='123 Random St',
            termsCheck='on'
        ), follow_redirects=True)
        self.assertIn(b'Password must be at least 8 characters long, include a special character, and mix of uppercase/lowercase.', response.data)

    # test for when a user doesn't check off the terms and conditions box
    def test_terms_unchecked(self):
        response = self.app.post('/register', data=dict(
            email='validemail@example.com',
            password='P@ssw0rd1',
            first_name='First',
            last_name='Last',
            dob='2000-06-20',
            gender='male',
            phone='1234567890',
            address='123 Random St'
        ), follow_redirects=True)
        self.assertIn(b'You must accept the Terms and Conditions to continue.', response.data)

    # test for when a user enters an invalid first name
    def test_invalid_first_name(self):
        response = self.app.post('/register', data=dict(
            email='validemail@example.com',
            password='P@ssw0rd1',
            first_name='1',
            last_name='Last',
            dob='2000-06-20',
            gender='male',
            phone='1234567890',
            address='123 Random St',
            termsCheck='on'
        ), follow_redirects=True)
        self.assertIn(b'First name can only contain letters', response.data)

    # test for when a user enters an invalid last name
    def test_invalid_last_name(self):
        response = self.app.post('/register', data=dict(
            email='validemail@example.com',
            password='P@ssw0rd1',
            first_name='First',
            last_name='1',
            dob='2000-06-20',
            gender='male',
            phone='1234567890',
            address='123 Random St',
            termsCheck='on'
        ), follow_redirects=True)
        self.assertIn(b'Last name can only contain letters', response.data)

    # test for when a user enters an invalid DOB
    def test_invalid_dob(self):
        response = self.app.post('/register', data=dict(
            email='validemail@example.com',
            password='P@ssw0rd1',
            first_name='First',
            last_name='Last',
            dob='2018-06-20',
            gender='male',
            phone='1234567890',
            address='123 Random St',
            termsCheck='on'
            ), follow_redirects=True)
        self.assertIn(b'Invalid date of birth. You must be at least 18 years of age and enter in YYYY-MM-DD format.', response.data)

    # test for when a user doesn't select a gender
    def test_invalid_gender(self):
        response = self.app.post('/register', data=dict(
            email='validemail@example.com',
            password='P@ssw0rd1',
            first_name='First',
            last_name='Last',
            dob='2000-06-20',
            gender='',
            phone='1234567890',
            address='123 Random St',
            termsCheck='on'
        ), follow_redirects=True)
        self.assertIn(b'Please select a gender option', response.data)

    # test for when a user enters an invalid phone number
    def test_invalid_phone(self):
        response = self.app.post('/register', data=dict(
            email='validemail@example.com',
            password='P@ssw0rd1',
            first_name='First',
            last_name='Last',
            dob='2000-06-20',
            gender='male',
            phone='1234',
            address='123 Random St',
            termsCheck='on'
        ), follow_redirects=True)
        self.assertIn(b'Invalid phone number. Must be at least 10 digits.', response.data)

    # test for when a user enters an invalid address
    def test_invalid_address(self):
        response = self.app.post('/register', data=dict(
            email='validemail@example.com',
            password='P@ssw0rd1',
            first_name='First',
            last_name='Last',
            dob='2000-06-20',
            gender='male',
            phone='1234567890',
            address='Short',
            termsCheck='on'
        ), follow_redirects=True)
        self.assertIn(b'Invalid address. Please enter a valid address (at least 8 characters).', response.data)

class CancelBookingTestCase(unittest.TestCase):

    def setUp(self):
        # Setup test client and enable testing mode
        self.app = app.test_client()
        self.conn = get_db_connection()
        self.conn.execute('DELETE FROM bookings')  # Clear bookings table before each test
        self.conn.execute('INSERT INTO bookings (booking_id, user_id, flight_id, status) VALUES (1, 1, 1, "active")')
        self.conn.commit()

    def tearDown(self):
        # Close connection and reset database after each test
        self.conn.execute('DELETE FROM bookings')
        self.conn.commit()
        self.conn.close()

    def test_cancel_booking_success(self):
        # Test successful cancellation of an existing booking
        response = self.app.post('/cancel_booking/1', follow_redirects=True)
        booking = self.conn.execute('SELECT status FROM bookings WHERE booking_id = 1').fetchone()
        self.assertEqual(booking['status'], 'canceled')  # Verify the booking status is updated
        self.assertIn(b'Booking canceled successfully!', response.data)  # Check for success message in redirected response
       

    def test_cancel_nonexistent_booking(self):
        # Test trying to cancel a non-existent booking
        response = self.app.post('/cancel_booking/9999', follow_redirects=True)
        self.assertIn(b'Booking not found!', response.data)  # Check for "Booking not found" message

    def test_cancel_booking_when_list_is_empty(self):
        # Clear the bookings table directly
        self.conn.execute('DELETE FROM bookings')
        self.conn.commit()
        
        # Attempt to cancel a booking when no bookings are available
        response = self.app.post('/cancel_booking/1', follow_redirects=True)
        self.assertIn(b'Booking not found!', response.data)  # Check for message in empty state

if __name__ == '__main__':
    unittest.main()
    
