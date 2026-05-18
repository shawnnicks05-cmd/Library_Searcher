from flask import Flask, render_template, request ,redirect, url_for , flash

app = Flask(__name__)
app.secret_key = "LOVE LOVE"

USERS_DB = {
    "admin": "password123"
}

@app.route('/')
def index():
    return render_template('index.html',login_success=False)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if not username or not password:
        flash('Please enter both username and password.', 'warning')
        return render_template('index.html', login_success=False)

    if username not in USERS_DB:
        flash('Username not found. Please sign up.', 'warning')
        return render_template('index.html', login_success=False)

    
    if USERS_DB[username] != password:
        flash('Incorrect password. Please try again.', 'danger')
        return render_template('index.html', login_success=False)


    if username in USERS_DB and USERS_DB[username] == password:
        flash('Login successful!', 'success')
        return render_template('index.html', login_success=False)

    else:
        flash('Invalid username or password.', 'danger')
        return render_template('index.html', login_success=False)


    flash('Login successful!', 'success')
    return render_template('index.html', login_success=True, user=username)


"""
@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    if username in USERS_DB:
        flash('Username already exists.', 'danger')
        return render_template('index.html', login_success=False)
    
    USERS_DB[username] = password

    return render_template('index.html', login_success=True, user=username)
"""
if __name__ == '__main__':
    app.run(debug=True)

