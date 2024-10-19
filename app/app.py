from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

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
        username = request.form['username']
        password = request.form['password']
        if username in dummy and dummy[username] == password:
            flash("Login successful, welcome {username}")
            return redirect(url_for('index'))
        else:
            flash("Username or password is incorrect")
            return redirect(url_for('login'))
            
    return render_template('login.html')

if __name__ == '__main__':
    app.run(debug=True)