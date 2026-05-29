import os
import json
import math
import time

ACTIONS_WEIGHT = {
    "view": 1.0,
    "search": 0.5,
    "read": 2.0,
    "rate": 3.0,    
    "favorite": 5.0
}

# 🟢 FIXED: Changed paths to absolute so Flask's watchdog doesn't lose your data files
HISTORY_FILE = os.path.join(os.path.dirname(__file__), 'data', 'history.json')
SCORES_FILE = os.path.join(os.path.dirname(__file__), 'data', 'user_ratings.json')
ACTIVITY_LOG = os.path.join(os.path.dirname(__file__), 'data', 'activity_log.json')
BOOKS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'Book_Covers')

# --- Chronological History Storage Helpers ---
def load_history():
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}
    
def save_history(data):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# --- Original Score Storage Helpers ---
def load_user_scores() -> dict:
    if not os.path.exists(SCORES_FILE):
        return {}
    with open(SCORES_FILE, "r", encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_user_scores(scores: dict):
    os.makedirs(os.path.dirname(SCORES_FILE), exist_ok=True)
    with open(SCORES_FILE, "w", encoding='utf-8') as f:
        json.dump(scores, f, indent = 4)

# --- Track Activity ---
def track_activity(username: str, book_title: str, action: str, explicit_score: int = None):
    scores = load_user_scores()

    if username not in scores:
        scores[username] = {}
        
    if action == "rate" and explicit_score is not None:
        scores[username][book_title] = explicit_score
    else: 
        weight = ACTIONS_WEIGHT.get(action, 0)
        current_score = scores[username].get(book_title, 0)
        scores[username][book_title] = current_score + weight
            
    save_user_scores(scores)

    # 🕒 SEPARATE PROGRESS TRACKER: Appends directly to history.json without affecting scores
    if action == "read":
        history_data = load_history()
        
        if username not in history_data:
            history_data[username] = []
            
        user_history = history_data[username]
        
        if book_title in user_history:
            user_history.remove(book_title)
            
        user_history.insert(0, book_title)
        history_data[username] = user_history[:5]
        
        save_history(history_data)

# --- Smart Score Retrieval ---
def get_user_scores(username: str) -> dict:
    user_data = load_user_scores().get(username, {})
    
    # 🟢 ADAPTER: If user profile contains a nested "ratings" block, use it!
    # Otherwise, fall back to the root dictionary. This reads BOTH formats perfectly.
    if "ratings" in user_data:
        return user_data["ratings"]
    return user_data

# --- Original System Engines (Completely Untouched) ---
def get_Books():
    catalog = {}
    print(f"DEBUG: Python is searching for your book covers here: {BOOKS_DIR}")
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

def get_recommended_catalog(username: str) -> dict:
     all_books = get_Books()
     user_scores = get_user_scores(username)

     if not user_scores:
          return all_books
    
     recommended_catalog = {}

     for category, books in all_books.items():
          category_has_activity = False
          scored_books = []
          unscored_books = []
          
          for book in books:
               book_title = book['title']

               if book_title in user_scores and user_scores[book_title] > 0:
                    category_has_activity = True
                    book['score'] = user_scores[book_title]
                    scored_books.append(book)
               else:
                    book['score'] = 0
                    unscored_books.append(book)
        
          if category_has_activity:
               scored_books.sort(key=lambda x: x['score'], reverse=True)
               recommended_catalog[category] = scored_books + unscored_books

     if not recommended_catalog:
          return all_books
     return recommended_catalog

def get_flat_recommendations(username: str) -> list:
    all_books_catalog = get_Books()  
    user_scores = get_user_scores(username)
    
    flat_book_list = []
    
    for category, books in all_books_catalog.items():
        for book in books:
            book['category'] = category
            book['score'] = user_scores.get(book['title'], 0)
            flat_book_list.append(book)
            
    flat_book_list.sort(key=lambda x: x['score'], reverse=True)
    
    has_history = any(b['score'] > 0 for b in flat_book_list)
    if has_history:
        flat_book_list = [b for b in flat_book_list if b['score'] > 0]
        
    return flat_book_list