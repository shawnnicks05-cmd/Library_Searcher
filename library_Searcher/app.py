from flask import Flask, render_template, request, redirect, url_for, flash, session
import os


app = Flask(__name__)
app.secret_key = "Library_Secret_Key"

USERS_DB = {
    "admin": "admin",
    "DwightRamos": "ginger",
    "EthanMathhew": "Piang",
    "Shawnnicks05": "Bading"
}


BOOKS_DIR = os.path.join(app.root_path, 'static', 'Book_Covers')

def get_Books():
    catalog = {}
    if not os.path.exists(BOOKS_DIR):
        return catalog

    for category in os.listdir(BOOKS_DIR):
        category_path = os.path.join(BOOKS_DIR, category)
        
        if(os.path.isdir(category_path)):
            catalog[category] = []

            for filename in os.listdir(category_path):
                if filename.lower().endswith(('.png')):

                            
                    book_title = os.path.splitext(filename)[0].title()
                    catalog[category].append({
                        'title': book_title,
                        'category': category,
                        'cover_image': filename
                    })

    return catalog

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
    book_catalog = get_Books()
    return render_template(
        'dashboard.html',
        current_user=session['username'],
        username=session.get("username"),
        catalog=book_catalog
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