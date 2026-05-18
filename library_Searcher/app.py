from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = "Library_Secret_Key"

USERS_DB = {
    "admin": "password123"
}


@app.route('/')
def index():

    # If already logged in
    if 'username' in session:
        return redirect(url_for('dashboard'))

    return render_template(
        'login.html',
        login_success=False
    )


@app.route('/login', methods=['POST'])
def login():

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    # Validation
    if not username:
        return render_template(
            'login.html',
            login_success=False,
            username_err="Username is required."
        )

    if not password:
        return render_template(
            'login.html',
            login_success=False,
            username=username,
            password_err="Password is required."
        )

    # Username check
    if username not in USERS_DB:
        return render_template(
            'login.html',
            login_success=False,
            username_err="Username not found."
        )

    # Password check
    if USERS_DB[username] != password:
        return render_template(
            'login.html',
            login_success=False,
            username=username,
            password_err="Incorrect password."
        )

    # Save login session
    session['username'] = username

    flash('Login successful!', 'success')

    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():

    # Prevent access if not logged in
    if 'username' not in session:
        return redirect(url_for('index'))

    return render_template(
        'dashboard.html',
        current_user=session['username']
    )


@app.route('/profile')
def profile():

    # Prevent access if not logged in
    if 'username' not in session:
        return redirect(url_for('index'))

    return render_template(
        'profile.html',
        current_user=session['username']
    )

@app.route('/search')
def search():

    # Prevent access if not logged in
    if 'username' not in session:
        return redirect(url_for('index'))

    return render_template(
        'search.html',
        current_user=session['username']
    )


@app.route('/logout')
def logout():

    session.pop('username', None)

    flash('Logged out successfully!', 'info')

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)