from flask import Flask, render_template, request, redirect, url_for, flash, session,jsonify
from recommender import get_Books, track_activity, get_user_scores, get_recommended_catalog,get_flat_recommendations
from functools import wraps
import json
import os

app = Flask(__name__)
app.secret_key = "Library_Secret_Key"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):

        if 'username' not in session:
            flash("Please log in to access this page.","error")
            return redirect(url_for('index'))
        return f(*args,**kwargs)
    return decorated_function

def load_users() -> dict:
    with open("data/users.json", "r") as f:
        return json.load(f)

<<<<<<< HEAD
=======
    for category in os.listdir(BOOKS_DIR):
        category_path = os.path.join(BOOKS_DIR, category)

        if os.path.isdir(category_path):
            catalog[category] = []

            for filename in os.listdir(category_path):
                if filename.lower().endswith('.png'):
                    book_title = os.path.splitext(filename)[0].title()
                    catalog[category].append({
                        'title': book_title,
                        'category': category,
                        'cover_image': filename
                    })

    return catalog



>>>>>>> 611d268 (Push)

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    if not username:
        return render_template('login.html', username_err="Username is required.")

    if not password:
        return render_template('login.html', username=username, password_err="Password is required.")

    users = load_users()

    if username not in users:
        return render_template('login.html', username_err="Username not found.")

    if users[username] != password:
        return render_template('login.html', username=username, password_err="Incorrect password.")

    session['username'] = username
    flash('Login successful!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))

    user    = session.get('username')
    recommendations = get_flat_recommendations(user)
    catalog_books = get_Books()
    if not recommendations:
        fallback_books = []
        category_seen = set()
        for book in catalog_books:
            category = book.get('category')
            if category not in  category_seen:
             fallback_books.append(book)
             category_seen.add(category)
    
        recommendations = fallback_books

    if len(recommendations) > 5:
        recommendations = recommendations[:5]
    

    return render_template('dashboard.html', user=user, recommendations=recommendations,catalog_books=catalog_books)

@app.route("/view/<title>")
@login_required
def view_book(title):
    user = session.get("username")
    track_activity(user, title, "view")
    
    flash(f"You viewed {title}!", "info")
    return redirect(url_for('dashboard'))
 # Redirects back instead of loading a missing HTML file


@app.route("/read/<title>")
@login_required
def read_book(title):
    user = session.get("username")
    track_activity(user,title,"read")

    flash(f"reading {title}!", "info")
    return redirect(url_for('dashboard'))

@app.route("/favorite", methods=["POST"])
@login_required
def favorite():
    user = session.get("username")
    title = request.form.get("title")
    track_activity(user, title , "favorite")

    return redirect(url_for('dashboard'))

@app.route("/scores", methods=["POST"])
def scores():
    user = session.get("username")
    title = request.form.get("title")
    scores = int(request.form.get("scores"))
    
    track_activity(user,title,"rate",explicit_score=scores)

    return redirect(url_for('dashboard'))



@app.route('/api/suggested-books')
def api_suggested_books():
    user = session.get('username')
    if not user:
        return jsonify([])
    
    user_scores_dict = get_user_scores(user) or {}

    book_titles = list(user_scores_dict.keys())

    return jsonify(book_titles) 

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('index'))

    return render_template('profile.html', user=session.get('username'))


@app.route('/search')
def search():
    user = session.get("username")
    query = request.args.get('q','').strip().lower()

    if 'username' not in session:
        return redirect(url_for('index'))

    all_suggestions = get_flat_recommendations(user)

    if query:

<<<<<<< HEAD
        books_to_show = [b for b in all_suggestions 
                         if query in b['title'].lower() or query in b['category'].lower()]
=======
        # Save recent searches in session
        recent = session.get('recent_searches', [])
        if query not in recent:
            recent.insert(0, query)
            session['recent_searches'] = recent[:5]
            session.modified = True

    return render_template('search.html',
                           current_user=session['username'],
                           username=session.get('username'),
                           results=results,
                           query=query)


@app.route('/api/search-suggestions')
def search_suggestions():
    if 'username' not in session:
        return jsonify([])

    query = request.args.get('q', '').strip().lower()
    suggestions = {"books": [], "categories": []}

    if len(query) >= 2:
        book_catalog = get_Books()
        seen_categories = set()

        for category, books in book_catalog.items():
            for book in books:
                if query in book['title'].lower():
                    suggestions["books"].append(book['title'])

                if query in category.lower() and category not in seen_categories:
                    suggestions["categories"].append(category)
                    seen_categories.add(category)

    return jsonify(suggestions)


@app.route('/api/recent-searches')
def get_recent_searches():
    if 'username' not in session:
        return jsonify([])

    return jsonify(session.get('recent_searches', []))

BOOKS_CONTENT_DIR = os.path.join(app.root_path, 'static', 'Book_Content')

# Fake author/description data per book (add more as needed)
BOOK_META = {
    "default": {
        "author": "Unknown Author",
        "year": "2024",
        "description": "A captivating story that takes readers on an unforgettable journey through vivid worlds and compelling characters."
    }
}

def get_book_meta(title):
    return BOOK_META.get(title, BOOK_META["default"])

@app.route('/book/<category>/<title>')
def book_detail(category, title):
    if 'username' not in session:
        return redirect(url_for('index'))

    meta = get_book_meta(title)
    cover_image = None
    category_path = os.path.join(BOOKS_DIR, category)
    if os.path.exists(category_path):
        for filename in os.listdir(category_path):
            if os.path.splitext(filename)[0].title() == title:
                cover_image = filename
                break

    like_count = get_like_count(category, title)
    user_liked = has_user_liked(category, title, session['username'])

    return render_template('book_detail.html',
                           username=session.get('username'),
                           current_user=session['username'],
                           title=title,
                           category=category,
                           cover_image=cover_image,
                           meta=meta,
                           like_count=like_count,
                           user_liked=user_liked)


@app.route('/book/<category>/<title>/read')
def book_read(category, title):
    if 'username' not in session:
        return redirect(url_for('index'))

    content = "No content available for this book yet."
    content_category_path = os.path.join(BOOKS_CONTENT_DIR, category)

    if os.path.exists(content_category_path):
        for filename in os.listdir(content_category_path):
            if os.path.splitext(filename)[0].title() == title and filename.endswith('.txt'):
                filepath = os.path.join(content_category_path, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                break

    return render_template('book_read.html',
                           username=session.get('username'),
                           current_user=session['username'],
                           title=title,
                           category=category,
                           content=content)


LIKES_FILE = os.path.join(app.root_path, 'likes.json')

def load_likes():
    if not os.path.exists(LIKES_FILE):
        return {}
    with open(LIKES_FILE, 'r') as f:
        return json.load(f)

def save_likes(likes):
    with open(LIKES_FILE, 'w') as f:
        json.dump(likes, f)

def get_like_count(category, title):
    likes = load_likes()
    key = f"{category}::{title}"
    return len(likes.get(key, []))

def has_user_liked(category, title, username):
    likes = load_likes()
    key = f"{category}::{title}"
    return username in likes.get(key, [])


@app.route('/api/like/<category>/<title>', methods=['POST'])
def toggle_like(category, title):
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    username = session['username']
    likes = load_likes()
    key = f"{category}::{title}"

    if key not in likes:
        likes[key] = []

    if username in likes[key]:
        likes[key].remove(username)
        liked = False
>>>>>>> 611d268 (Push)
    else:

        books_to_show = all_suggestions


    return render_template('search.html',user=user,books_to_show=books_to_show)


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully!', 'info')
    return redirect(url_for('index'))


<<<<<<< HEAD
=======

>>>>>>> 611d268 (Push)
if __name__ == '__main__':
    app.run(debug=True)