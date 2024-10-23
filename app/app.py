from flask import Flask, render_template, request, redirect, url_for, flash 
import re
from datetime import datetime

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = "asdf"

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


dummy = {
    'user1@gmail.com': 'Password1!',
    'user2@gmail.com': 'Password2!',
    'user3@gmail.com': 'Password3!'
}
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if username exists and password matches
        if username in dummy and dummy[username] == password:
            flash('Login successful!', 'success')  # Flash success message
            return redirect(url_for('index'))  # Redirect to the main page
        else:
            flash('Login failed. Invalid username or password.', 'danger')  # Flash failure message
            return redirect(url_for('login'))  # Redirect to prevent form resubmission

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password'].strip()
        terms_accepted = 'termsCheck' in request.form

        errors = {}

        if not re.match(email_regex, email):
            errors['email_error'] = 'Invalid email address.'
        if not re.match(password_regex, password):
            errors['password_error'] = 'Password must be at least 8 characters long, include a special character, and mix of uppercase/lowercase.'
        if not terms_accepted:
            errors['terms_error'] = 'You must accept the Terms and Conditions to continue.'

        first_name = request.form['first_name'].strip()
        last_name = request.form['last_name'].strip()
        dob = request.form['dob'].strip()
        gender = request.form['gender']

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

        phone = request.form['phone'].strip()
        address = request.form['address'].strip()

        if not re.match(phone_regex, phone):
            errors['phone_error'] = 'Invalid phone number. Must be at least 10 digits.'
        if not re.match(address_regex, address):
            errors['address_error'] = 'Invalid address. Please enter a valid address (at least 8 characters).'

        # returns form with errors if any are found
        if errors:
            return render_template('register.html', errors=errors, form_data=request.form)
        
        return redirect(url_for('login'))

    return render_template('register.html', errors={}, form_data={})
    
bookings = [
    {"id": 1, "departure": "Toronto to Calgary", "date": "Tuesday, October 8th, 2024", "time": "08:00 - 12:24", "airline": "WestJet"},
    {"id": 2, "departure": "Calgary to Toronto", "date": "Friday, October 18th, 2024", "time": "1:49 - 6:32", "airline": "Air Canada"}
]

@app.route('/cancelBooking')
def cancelBooking ():
    return render_template('cancelBooking.html', bookings=bookings)

@app.route('/cancel/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    global bookings
    booking_to_cancel = next((b for b in bookings if b['id'] == booking_id), None)

    if booking_to_cancel:
        bookings.remove(booking_to_cancel)
        flash('Your booking has been canceled successfully.')
        
    else:
        flash('Booking not found.')

    return redirect(url_for('cancelBooking'))  

if __name__ == '__main__':
    app.run(debug=True)
