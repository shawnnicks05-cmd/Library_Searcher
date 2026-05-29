from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import os
import json

import datetime
# 🟢 Import the recommendation engine functions
from Logic import load_history, track_activity, load_user_scores,get_flat_recommendations,get_Books, get_user_scores

app = Flask(__name__)
app.secret_key = "Library_Secret_Key"

USERS_DB = {
    "admin": "admin",
    "DwightRamos": "ginger",
    "EthanMathhew": "Piang",
    "Shawnnicks05": "Bading"
}

BOOKS_DIR = os.path.join(app.root_path, 'static', 'Book_Covers')



# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html', login_success=False)


@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    if not username:
        return render_template('login.html', login_success=False,
                               username_err="Username is required.")

    if not password:
        return render_template('login.html', login_success=False,
                               username=username,
                               password_err="Password is required.")

    if username not in USERS_DB:
        return render_template('login.html', login_success=False,
                               username_err="Username not found.")

    if USERS_DB[username] != password:
        return render_template('login.html', login_success=False,
                               username=username,
                               password_err="Incorrect password.")

    session['username'] = username
    flash('Login successful!', 'success')
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('index'))

    user = session['username']

    # 1. Load recommendations (Using the corrected dictionary loader)
    book_catalog = get_flat_recommendations(user) 

    # 2. Extract reading logs from history.json
    history_data = load_history()
    recent_titles = history_data.get(user, []) # e.g. ["Complexity", "101 Things..."]

    # 3. Flatten your catalog dictionary data into a list for fast scanning
    catalog_dict = get_Books() 
    flat_catalog = []
    for category, books in catalog_dict.items():
        for b in books:
            flat_catalog.append(b)

    recent_books = []

    # 4. Match historical titles to their category folders to load covers
    for title in recent_titles:
        clean_target = title.strip().lower()
        for book in flat_catalog:
            if book['title'].strip().lower() == clean_target:
                recent_books.append({
                    'title': book['title'],
                    'category': book['category']
                })
                break

    return render_template('dashboard.html',
                           current_user=user,
                           username=user,
                           recommendations=book_catalog,   
                           recent_books=recent_books)

@app.route('/profile')
def profile():
    if 'username' not in session:
        return redirect(url_for('index'))

    return render_template('profile.html',
                           current_user=session['username'],
                           username=session.get('username'))


@app.route('/search')
def search():
    if 'username' not in session:
        return redirect(url_for('index'))

    query = request.args.get('q', '').strip().lower()
    results = []

    if query:
        book_catalog = get_Books()
        for category, books in book_catalog.items():
            for book in books:
                if (query in book['title'].lower() or
                        query in book['category'].lower()):
                    results.append(book)
                    # 🟢 Track search weight for any matched query books found
                    track_activity(session['username'], book['title'], "search")

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

BOOKS_CONTENT_DIR = os.path.join(app.root_path, 'static', 'Book_Covers')

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

    # 🟢 Track page view action
    track_activity(session['username'], title, "view")

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

    # 🟢 Track book text file read activation action
    track_activity(session['username'], book_title=title, action="read")
    
    # Find matching .txt file (case-insensitive)
    content = "No content available for this book yet."
    content_category_path = os.path.join(app.static_folder, 'Book_Covers', category)
    clean_target_name = title.lower().replace('_', ' ').replace('-', ' ').strip()


    if os.path.exists(content_category_path):
        for filename in os.listdir(content_category_path):
            if filename.endswith('.txt'):
                clean_filename = os.path.splitext(filename)[0].lower().replace('_', ' ').replace('-', ' ').strip()
                if clean_filename == clean_target_name:
                    with open(os.path.join(content_category_path, filename), 'r', encoding='utf-8') as f:
                        content = f.read()
                    break

    return render_template('book_read.html',
                           username=session.get('username'),
                           current_user=session['username'],
                           title=title,
                           category=category,
                           content=content)


LIKES_FILE = os.path.join(app.root_path, 'data/likes.json')

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
    else:
        likes[key].append(username)
        liked = True
        # 🟢 Track action score calculation only if they successfully toggle "Like On"
        track_activity(username, title, "favorite")

    save_likes(likes)
    return jsonify({'liked': liked, 'count': len(likes[key])})


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully!', 'info')
    return redirect(url_for('index'))


# ──────────────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    app.run(debug=True)