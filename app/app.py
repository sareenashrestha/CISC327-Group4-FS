from flask import Flask, render_template, request, redirect, url_for, flash, session
import re
import sqlite3
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, jsonify
from init_database import init_db, get_db_connection

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

init_db()

# Validation regex patterns
email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
password_regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*]).{8,}$'
name_regex = r'^[A-Za-z]+$'
dob_regex = r'^\d{4}-\d{2}-\d{2}$' 
phone_regex = r'^\+?[0-9\s\-()]{10,}$'
address_regex = r'^[a-zA-Z0-9\s,.\'-]{8,}$'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['user_input']
        return render_template('index.html', user_input=user_input)
    return render_template('index.html', user_input=None)

@app.route('/check_email', methods=['POST'])
def check_email():
    email = request.form.get('email')
    conn = get_db_connection()
    cursor = conn.cursor()
    user = cursor.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
    conn.close()
    return jsonify({"exists": bool(user)})

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        email = request.form.get('username')
        password = request.form.get('password')

        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute query to select the stored password from the users table where the email matches the input email
        cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
        res = cursor.fetchone() # Fetch one is used because there should be only one email based on the defined table (unique not null constraint)
        conn.close()  # Close the connection

        # Conditions are if the query result is empty (input email doesn't exist in db)
        # or the input password doesn't match the stored password for that email
        if not res or not check_password_hash(res[0], password):
            flash('Login failed. Invalid username or password.', 'danger')
            return redirect(url_for('login'))  # Redirect to prevent form resubmission
        
        # Else in this case is if the email exists and the password matches, aka successful login
        else:
            flash('Login successful!', 'success')
            return redirect(url_for('index'))  # Redirect to the main page

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', errors={}, form_data={})
    
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = generate_password_hash(request.form['password'].strip()) # hash the pasword from the form input for secure storage
        terms_accepted = 'termsCheck' in request.form
        first_name = request.form['first_name'].strip()
        last_name = request.form['last_name'].strip()
        dob = request.form['dob'].strip()
        gender = request.form['gender']
        phone = request.form['phone'].strip()
        address = request.form['address'].strip()

        errors = {}

        conn = get_db_connection()
        cursor = conn.cursor()
        existing_user = cursor.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

        if existing_user:
            errors['email_error'] = "Email already registered."  # check for duplicate email before inserting the user into the db
        if not re.match(email_regex, email):
            errors['email_error'] = 'Invalid email address.'
        if not re.match(password_regex, request.form['password']):
            errors['password_error'] = 'Password must be at least 8 characters long, include a special character, and mix of uppercase/lowercase.'
        if not terms_accepted:
            errors['terms_error'] = 'You must accept the Terms and Conditions to continue.'
        if not re.match(name_regex, first_name):
            errors['first_name_error'] = 'First name can only contain letters.'
        if not re.match(name_regex, last_name):
            errors['last_name_error'] = 'Last name can only contain letters.'
        if not re.match(dob_regex, dob):
            errors['dob_error'] = 'Invalid date of birth. You must be at least 18 years of age and enter in YYYY-MM-DD format.'
        else:
            birth_date = datetime.strptime(dob, '%Y-%m-%d')
            today = datetime.today()
            eighteen_years_ago = datetime(today.year - 18, today.month, today.day)
            if birth_date > eighteen_years_ago:
                errors['dob_error'] = 'Invalid date of birth. You must be at least 18 years of age and enter in YYYY-MM-DD format.'
        if not gender:
            errors['gender_error'] = 'Please select a gender option.'
        if not re.match(phone_regex, phone):
            errors['phone_error'] = 'Invalid phone number. Must be at least 10 digits.'
        if not re.match(address_regex, address):
            errors['address_error'] = 'Invalid address. Please enter a valid address (at least 8 characters).'

        # returns form with errors if any are found
        if errors:
            return render_template('register.html', errors=errors, form_data=request.form)
        
        try:
            # insert into database if there are no errors
            cursor.execute('''
                INSERT INTO users (email, password, first_name, last_name, dob, gender, phone, address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (email, password, first_name, last_name, dob, gender, phone, address))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            # return error if the email is already registered
            errors['email_error'] = "Email already registered."
            return render_template('register.html', errors=errors, form_data=request.form)


# Database connection function
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home route - User's page displaying bookings
@app.route('/cancelBooking')
def cancelBooking():
    conn = get_db_connection()

    query = '''
    SELECT bookings.booking_id, flights.destination, flights.departure, flights.airline
    FROM bookings
    JOIN flights ON bookings.flight_id = flights.flight_id
    WHERE bookings.status = "active";
    '''

    bookings = conn.execute(query).fetchall()
    conn.close()

    #print("Flash messages before rendering:", session.get('_flashes'))  # Debug session flashes
    return render_template('cancelBooking.html', bookings=bookings, firstName="John")



# Cancel booking route
@app.route('/cancel_booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    conn = get_db_connection()
    booking = conn.execute('SELECT * FROM bookings WHERE booking_id = ?', (booking_id,)).fetchone()

    if booking is None:
        flash('Booking not found!', 'error')
        return redirect(url_for('cancelBooking'))

    # Update booking status
    conn.execute('UPDATE bookings SET status = ? WHERE booking_id = ?', ('canceled', booking_id))
    conn.commit()
    conn.close()

    # Redirect with a persistent success message
    flash('Booking canceled successfully!', 'success')
    return redirect(url_for('cancelBooking'))


if __name__ == '__main__':
    app.run(debug=True)
