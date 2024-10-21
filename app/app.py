from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = "asdf"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['user_input']
        return render_template('index.html', user_input=user_input)
    return render_template('index.html', user_input=None)


dummy = {
    'user1': 'password1',
    'user2': 'password2',
    'user3': 'password3'
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
            return redirect(url_for('index'))  # Redirect to prevent form resubmission
        else:
            flash('Login failed. Invalid username or password.', 'danger')  # Flash failure message
            return redirect(url_for('login'))  # Redirect to prevent form resubmission

    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)