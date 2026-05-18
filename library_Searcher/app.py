from flask import Flask, render_template, request ,redirect, url_for , flash

app = Flask(__name__)
app.secret_key = "Library_Secret_Key"

USERS_DB = {
    "admin": "password123"
}

@app.route('/')
def index():
    return render_template('login.html',login_success=False)

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if not username:
        return render_template('login.html', login_success=False, username_err="Username is required.")
    if not password:
        return render_template('login.html', login_success=False, username=username, password_err="Password is required.")
    
    if username not in USERS_DB:
        return render_template('login.html', login_success=False, username_err="Username not found.")
    if USERS_DB[username] != password:
        return render_template('login.html', login_success=False, username=username, password_err="Incorrect password.")


    if username in USERS_DB and USERS_DB[username] == password:
        flash('Login successful!', 'success')
        return render_template('dashboard.html', login_success=True , user=username,password=password , )

    return render_template('login.html', login_success=True, current_user=username)

@app.route('/dashboard')
def dashboard():
    username = request.args.get('username', 'Guest')
    return render_template('dashboard.html', current_user=username)

@app.route('/profile')
def profile():
    return render_template('profile.html')
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

