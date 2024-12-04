import unittest
from app import app, get_db_connection, generate_password_hash
import init_database
from unittest.mock import patch
import sqlite3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# BASE_URL = "http://localhost:5000"
init_database.init_db()

class TestEndToEnd(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Initialize the database
        init_database.init_db()
        conn = get_db_connection()

        # Insert dummy data into the database
        try:
            conn.execute("DELETE FROM users")
            conn.execute("DELETE FROM bookings")
            conn.execute("DELETE FROM flights")
            conn.commit()

            passHash = generate_password_hash('Password1!')
            conn.execute('''
                INSERT INTO users (email, password, first_name, last_name, dob, gender, phone, address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', ('user1@gmail.com', passHash, "First", "Last", "2000-06-20", "male", "1234567890", "123 Random St"))
            conn.execute("INSERT INTO flights (flight_id, destination, departure, airline) VALUES (?, ?, ?, ?)",
                     (1, 'Toronto to Calgary', '2024-12-01 10:00:00', 'Air Canada'))
            conn.execute("INSERT INTO flights (flight_id, destination, departure, airline) VALUES (?, ?, ?, ?)",
                     (2, 'Calgary to Toronto', '2024-12-06 03:00:00', 'WestJet'))
            conn.execute("INSERT INTO bookings (booking_id, user_id, flight_id, status) VALUES (?, ?, ?, ?)",
                     (1, 1, 1, 'active'))
            conn.execute("INSERT INTO bookings (booking_id, user_id, flight_id, status) VALUES (?, ?, ?, ?)",
                     (2, 1, 2, 'active'))
            conn.commit()
        except:
            pass
        conn.close()

        # Set up the webdriver for Selenium to display the webpage being tested
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.get("http://127.0.0.1:5000/login")

        WebDriverWait(self.driver, 10).until(EC.title_is("Login Page"))

         # Log in as a test user
        #self.driver.find_element(By.ID, "username").send_keys("user1@gmail.com")
        #self.driver.find_element(By.ID, "password").send_keys("Password1!")
        #self.driver.find_element(By.ID, "submit").click()

        #WebDriverWait(self.driver, 10).until(EC.title_is("Booking Dashboard"))

    def tearDown(self):
        self.driver.quit()

    def test_login(self):
        # First check to make sure the right webpage is opened
        assert "Login Page" in self.driver.title

        input_email = self.driver.find_element(By.ID, "username")
        input_password = self.driver.find_element(By.ID, "password")
        submit_button = self.driver.find_element(By.ID, "submit")

        # Checks to confirm that all the necessary elements are displayed
        assert input_email.is_displayed()
        assert input_password.is_displayed()
        assert submit_button.is_displayed()

        input_email.send_keys("user1@gmail.com")
        input_password.send_keys("Password1!")
        input_password.send_keys(Keys.RETURN)

        self.driver.implicitly_wait(5)

        # Successful logins redirect back to the main page, so must check for that
        assert "QU Airlines" in self.driver.title
   
    # test that a user can register successfully with valid input.
    def test_successful_registration(self):
        self.driver.get("http://127.0.0.1:5000/register")
        WebDriverWait(self.driver, 10).until(EC.title_is("Register"))

        # fill out the registration form with valid input
        self.driver.find_element(By.NAME, "email").send_keys("testuser@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("P@ssw0rd1")
        self.driver.find_element(By.ID, "termsCheck").click()
        
        buttons = self.driver.find_elements(By.CSS_SELECTOR, ".btn-continue")
        buttons[0].click()

        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "first_name"))
        ).send_keys("First")
        self.driver.find_element(By.NAME, "last_name").send_keys("Name")
        self.driver.find_element(By.NAME, "dob").send_keys("2004-06-20")
        self.driver.find_element(By.NAME, "gender").send_keys("female")
        
        buttons = self.driver.find_elements(By.CSS_SELECTOR, ".btn-continue")
        buttons[1].click()
    
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.NAME, "phone"))
        ).send_keys("1234567890")
        self.driver.find_element(By.NAME, "address").send_keys("123 Street St")
        

        buttons = self.driver.find_elements(By.CSS_SELECTOR, ".btn-continue")
        buttons[2].click()

        # verify the success message is present on the redirected login page
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        page_text = self.driver.page_source
        self.assertIn("Email Address", page_text)

    def test_cancel_booking_e2e(self):
        # Navigate to the Cancel Booking page
        self.driver.get("http://127.0.0.1:5000/cancelBooking")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "bookingList")))

        # Find and click the cancel button for the first booking
        cancel_button = self.driver.find_element(By.CSS_SELECTOR, "button[data-booking-id='1']")
        cancel_button.click()

        # Confirm the cancellation (if there's a modal)
        WebDriverWait(self.driver, 10).until(EC.alert_is_present())
        alert = self.driver.switch_to.alert
        alert.accept()

        # Verify the cancellation success message
        success_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "alert-success"))
        )
        self.assertIn("Booking canceled successfully!", success_message.text)

        # Verify the canceled booking is no longer listed
        self.driver.get("http://127.0.0.1:5000/cancelBooking")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "bookingList")))
        booking_list = self.driver.find_element(By.ID, "bookingList").text
        self.assertNotIn("Toronto to Calgary", booking_list)

        
class TestIntegration(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Clear the database before each test
        conn = get_db_connection()
        conn.execute("DELETE FROM users")
        conn.commit()
    
    def test_registration_and_login(self):
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


        response = self.app.post('/login', data=dict(
            username='validemail@example.com',
            password='P@ssw0rd1'
        ), follow_redirects=True)

        with self.app.session_transaction() as session:
            self.assertEqual(session.get('user_email'), 'validemail@example.com') 
            self.assertEqual(session.get('logged_in'), True) 

        # Checks for the right page is redirected to and the status code of the response
        self.assertEqual(response.request.path, '/')  
        self.assertEqual(response.status_code, 200)

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
        conn.close()


    # Test for the page loading properly
    def test_page_load(self):
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
    
    # Testing for when a user successfully logs in, with their email and password in the dummy hashmap
    def test_successful_login(self):
        # Redirecting is false, as the check for the flash message should be done before the redirest
        response = self.app.post('/login', data=dict(username='user1@gmail.com', password='Password1!'), follow_redirects=True)

        with self.app.session_transaction() as session:
            self.assertEqual(session.get('user_email'), 'user1@gmail.com') 
            self.assertEqual(session.get('logged_in'), True) 


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
        
    # simulate a database error to test if the registration endpoint handles database exceptions properly
    def test_database_rollback_on_error(self):
        new_user = {
            'email': 'erroruser@example.com',
            'password': 'P@ssw0rd1',
            'first_name': 'Error',
            'last_name': 'User',
            'dob': '2000-01-01',
            'gender': 'male',
            'phone': '1234567890',
            'address': '123 Error St',
            'termsCheck': 'on'
        }

        with patch('app.get_db_connection', side_effect=sqlite3.DatabaseError('Simulated database error')):
            response = self.app.post('/register', data=new_user, follow_redirects=True)
            self.assertEqual(response.status_code, 500)
            self.assertIn(b'Registration failed, please try again later.', response.data)

        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE email = ?', ('erroruser@example.com',)).fetchone()
        conn.close()

        self.assertIsNone(user)

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

class TestCancelBookingIntegration(unittest.TestCase):
    def setUp(self):
        # Setup test client and enable testing mode
        self.app = app.test_client()
        self.conn = get_db_connection()

        # Clear and prepare the database for the test
        self.conn.execute("DELETE FROM bookings")
        self.conn.execute("DELETE FROM flights")
        self.conn.commit()

        # Insert test data
        self.conn.execute("INSERT INTO flights (destination, departure, airline) VALUES (?, ?, ?)",
                          ('Toronto to Calgary', '2024-12-01 10:00:00', 'Air Canada'))
        self.conn.execute("INSERT INTO flights (destination, departure, airline) VALUES (?, ?, ?)",
                          ('Calgary to Toronto', '2024-12-06 03:00:00', 'WestJet'))
        self.conn.execute("INSERT INTO bookings (booking_id, user_id, flight_id, status) VALUES (?, ?, ?, ?)",
                          (1, 1, 1, 'active'))
        self.conn.execute("INSERT INTO bookings (booking_id, user_id, flight_id, status) VALUES (?, ?, ?, ?)",
                          (2, 1, 2, 'active'))
        self.conn.commit()

    def tearDown(self):
        # Clean up the database after tests
        self.conn.execute("DELETE FROM bookings")
        self.conn.execute("DELETE FROM flights")
        self.conn.commit()
        self.conn.close()

    def test_cancel_booking_success(self):
        # Test successful cancellation of an existing booking
        response = self.app.post('/cancel_booking/1', follow_redirects=True)
        booking = self.conn.execute('SELECT status FROM bookings WHERE booking_id = 1').fetchone()
        self.assertEqual(booking['status'], 'canceled')  # Verify booking status updated
        self.assertIn(b'Booking canceled successfully!', response.data)  # Check flash message

    def test_cancel_nonexistent_booking(self):
        # Test trying to cancel a non-existent booking
        response = self.app.post('/cancel_booking/9999', follow_redirects=True)
        self.assertIn(b'Booking not found!', response.data)  # Check for "Booking not found" message

    def test_cancel_booking_when_list_is_empty(self):
        # Clear all bookings
        self.conn.execute("DELETE FROM bookings")
        self.conn.commit()

        # Attempt to cancel a booking when no bookings exist
        response = self.app.post('/cancel_booking/1', follow_redirects=True)
        self.assertIn(b'Booking not found!', response.data)  # Verify appropriate flash message

    def test_cancel_booking_and_check_page(self):
         
        # Step 1: Cancel the booking and follow the redirect to ensure flash message is consumed
        response = self.app.post('/cancel_booking/1', follow_redirects=True)

        # Step 2: Verify the flash message in the response of the redirect
        self.assertIn(b'Booking canceled successfully!', response.data)

        # Step 3: Fetch the cancelBooking page
        response = self.app.get('/cancelBooking')

        # Step 4: Confirm that the canceled booking is no longer listed
        self.assertNotIn(b'Toronto to Calgary', response.data)

if __name__ == '__main__':
    unittest.main()
    
