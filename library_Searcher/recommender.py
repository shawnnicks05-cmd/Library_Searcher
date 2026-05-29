import os
import json
import math
import time


ACTIONS_WEIGHT = {
    "view": 1.0,
    "search": 0.5,
    "read": 2.0,
    "rate": 3.0,    
    "favorite":5.0
}

BOOKS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'Book_Covers')

SCORES_FILE = "data/user_ratings.json"
ACTIVITY_LOG = "data/activity_log.json"

def load_user_scores() -> dict:
    if not os.path.exists(SCORES_FILE):
        return {}
    with open(SCORES_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_user_scores(scores: dict):
    os.makedirs(os.path.dirname(SCORES_FILE), exist_ok=True)
    with open(SCORES_FILE, "w") as f:
        json.dump(scores, f, indent = 4)

def track_activity(username: str, book_title: str, action: str, explicit_score: int = None):
    scores = load_user_scores()

    if username not in scores:
            scores[username] = {}
        
    if action == "rate" and explicit_score is not None:
            scores[username][book_title] = explicit_score
    else: 
            weight = ACTIONS_WEIGHT.get(action,0)
    
            current_score = scores[username].get(book_title,0)
            scores[username][book_title] = current_score + weight
            
    save_user_scores(scores)

def get_user_scores(username: str) -> dict:
     return load_user_scores().get(username,{})


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
    all_books_catalog = get_Books()  # Gets the categorized dict
    user_scores = get_user_scores(username)
    
    flat_book_list = []
    
    # 1. Break the books out of their category walls
    for category, books in all_books_catalog.items():
        for book in books:
            # Attach the category name directly to the book object for your HTML image path
            book['category'] = category
            # Grab the score or default to 0
            book['score'] = user_scores.get(book['title'], 0)
            flat_book_list.append(book)
            
    # 2. Sort the entire master list by score (highest scores first)
    # If the user has history, things they interact with float to the top
    flat_book_list.sort(key=lambda x: x['score'], reverse=True)
    
    # 3. Filter rule: If they have tracking data, let's ONLY show books 
    # they have actually interacted with (score > 0)
    has_history = any(b['score'] > 0 for b in flat_book_list)
    if has_history:
        flat_book_list = [b for b in flat_book_list if b['score'] > 0]
        
    return flat_book_list