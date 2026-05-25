###

1.Login Screen
    FIELDS
    --username
    --password
    button
    --log in
2.Homescreen
    --sidebar navigator
    --search
3.sidebar navigator
    --Dashboard
    --home
    --search
    --profile

4. Algorithm
- Continue watching
- Recommended For You
- Search Bar
- Suggested for you

5.Database
- Read database
- Arrange in the dashboard tab

###
- Homepage / Browse page   →  "Suggested for You"   ✅ recommendation system
- Search bar results       →  exact + fuzzy matches  ✅ search
- Below search results     →  "You might also like"  ✅ recommendation system
- Empty search state       →  "Popular right now"    ✅ light recommendation
    
    ### Dwight Ramos - search,view,read,ratings,favorites

- book favorites
- book reserved

Cover
catogery
title
description
book id
book shelf

## WORKFLOW 
- Folder Loader - done
- Display catalog - done
- user session - done 
- rating storage 
- activity tracker
- recommendation engine
- Homepage route
- suggested for you section
- wire up routes
- Test it

| Method | Purpose          |
| ------ | ---------------- |
| GET    | Get/show data    |
| POST   | Send/create data |
| PUT    | Update data      |
| DELETE | Delete data      |



import os    # Provides functions for interacting with the operating system (like managing paths and directories)
import json  # Allows parsing and formatting of JSON data storage files
import math  # Imports mathematical utilities (available for any complex scoring formulas if needed later)
import time  # Provides time-related capabilities (useful if logging historical interactions sequentially)

# Dictionary assigning raw algorithmic weights to different types of user behavior actions
ACTIONS_WEIGHT = {
    "view": 1.0,      # Giving a book a baseline view registers minor interest
    "search": 0.5,    # Finding a book via query logs a small touchpoint
    "read": 2.0,      # Opening a book to read flags deep interaction
    "rate": 3.0,      # Providing an un-scaled, implied star score adds solid points
    "favorite": 5.0   # Saving a book into a personal favorites list indicates maximum preference
}

# Constructs an absolute path pointing to the static image directory where book cover images are physically saved
BOOKS_DIR = os.path.join(os.path.dirname(__file__), 'static', 'Book_Covers')

SCORES_FILE = "data/user_ratings.json"  # Relative path pointing to the JSON database tracking all ongoing scoring values
ACTIVITY_LOG = "data/activity_log.json" # Unused placeholder path originally designated for sequential step-by-step history logs

# Defines a function to safely load user scoring data from the local storage file
def load_user_scores() -> dict:
    if not os.path.exists(SCORES_FILE):  # Checks if the user ratings file doesn't exist yet
        return {}                       # Returns a blank dictionary to initialize structural data gracefully
    with open(SCORES_FILE, "r") as f:    # Opens the file container in read-only text stream execution mode
        try:                             # Introduces a safety catch block to protect against potential corrupted file formats
            return json.load(f)          # Converts raw JSON string contents back into native Python dictionaries
        except json.JSONDecodeError:     # Triggers if the target data file has been wiped, broken, or improperly closed
            return {}                    # Drops a blank dictionary fallback to prevent the entire web engine from crashing

# Defines a function to overwrite the database with fresh updated records
def save_user_scores(scores: dict):
    os.makedirs(os.path.dirname(SCORES_FILE), exist_ok=True)  # Instantly creates missing directory pathways safely if missing
    with open(SCORES_FILE, "w") as f:                         # Opens the target tracking database in raw write-overwrite mode
        json.dump(scores, f, indent=4)                       # Saves Python memory arrays back to the disk formatting with nice indents

# Primary logic module used to mathematically calculate incoming activity data hooks from your web application routes
def track_activity(username: str, book_title: str, action: str, explicit_score: int = None):
    scores = load_user_scores()  # Grabs an active, live snapshot of all existing profile information data

    if username not in scores:       # Checks if this specific profile name is accessing your platform for the very first time
            scores[username] = {}    # Allocates a clean, blank sub-dictionary bound exclusively to their user session account
        
    if action == "rate" and explicit_score is not None:  # Evaluates if a concrete numeric score choice is actively being given
            scores[username][book_title] = explicit_score  # Directly overwrites any historical action points with the hard numeric evaluation
    else:                                                 # Executes if capturing standard background telemetry actions instead
            weight = ACTIONS_WEIGHT.get(action, 0)         # Pulls matching modifier point values from the configuration dict, dropping 0 if bad string

            current_score = scores[username].get(book_title, 0)    # Extracts historic interaction scores, defaulting to 0 for a first touchpoint
            scores[username][book_title] = current_score + weight  # Merges past scores together with your fresh context behavior points
            
    save_user_scores(scores)  # Commits the fresh, finalized evaluation weights back into structural permanent database files

# Small utility function designed to extract exclusive records belonging to an isolated user session context profile
def get_user_scores(username: str) -> dict:
     return load_user_scores().get(username, {})  # Isolates user sub-keys from global mappings, providing safety fallbacks if clear

# Core mapping routine that checks structural storage directories to automatically organize asset indexes
def get_Books():
    catalog = {}  # Instantiates a clean structure to accumulate files discovered across system scans
    print(f"DEBUG: Python is searching for your book covers here: {BOOKS_DIR}")  # Diagnostic console report print tracker
    if not os.path.exists(BOOKS_DIR):  # Evaluates whether asset directories are physically absent from local drive targets
        return catalog                 # Returns empty sets immediately if directories are missing to stave off crashes

    for category in os.listdir(BOOKS_DIR):                # Steps sequentially through high-level subdirectory folders inside your main covers folder
        category_path = os.path.join(BOOKS_DIR, category)  # Constructs a clean, absolute computer directory path targeting the individual category subfolder
        
        if(os.path.isdir(category_path)):  # Validates that the targeted loop element is a true sub-folder block rather than stray metadata files
            catalog[category] = []         # Initializes an empty catalog book tray under this genre's text key inside the dictionary

            for filename in os.listdir(category_path):         # Iterates over every isolated file entity within this active genre folder
                if filename.lower().endswith(('.png')):        # Verifies the item is a valid PNG image format, preventing indexing bugs

                    book_title = os.path.splitext(filename)[0].title()  # Drops image extensions, changing "file_name" to title-cased words
                    catalog[category].append({                          # Commits a newly registered dictionary profile index tracking object
                        'title': book_title,                            # Sets the dynamic readable metadata title field value
                        'category': category,                          # Stores categorical reference points for image path mapping
                        'cover_image': filename                         # Links to the asset file identifier to render covers in templates
                    })

    return catalog  # Returns the fully assembled multi-tier dictionary containing every discovered book image item

# Algorithmic engine that returns books sorted by category, dropping rows completely if a user lacks history there
def get_recommended_catalog(username: str) -> dict:
     
     all_books = get_Books()  # Runs directory scans to establish complete raw baselines of your library items

     user_scores = get_user_scores(username)  # Loads specific past performance profiling numbers for calculations

     if not user_scores:       # Checks whether an incoming guest session lacks any historical analytics information profiles
          return all_books     # Defaults back to exposing comprehensive standard directory loops so they can build up an initial baseline

     recommended_catalog = {}  # Prepares a final storage container to hold only the dynamic filtered outputs

     for category, books in all_books.items():  # Loops line-by-line down categorical genre groupings to run filters
          category_has_activity = False         # Deploys tracking flags to record whether any internal interaction took place inside a category

          scored_books = []    # Dynamic list assigned to organize files the user has interacted with
          unscored_books = []  # Dynamic list assigned to organize completely untouched, hidden title files
          
          for book in books:                 # Evaluates every individual library module registered within this active directory track
              book_title = book['title']     # Grabs text values to verify tracking matches across index registers

              if book_title in user_scores and user_scores[book_title] > 0:  # Matches title keys against real positive tracking counts
                   category_has_activity = True                             # Triggers context flag indicating active engagement with this genre
                   book['score'] = user_scores[book_title]                  # Explicitly appends current telemetry tracking weights directly to objects
                   scored_books.append(book)                                # Relocates processed items straight into active interaction arrays
              else:                                                         # Direct fallback routing path for any pristine unviewed files
                   book['score'] = 0                                        # Assigns fixed baseline numbers to normalize sorting calculations
                   unscored_books.append(book)                              # Groups raw unviewed files into separate arrays
        
          if category_has_activity:  # Checks if this genre has been validated for showing on user dashboards
               scored_books.sort(key=lambda x: x['score'], reverse=True)  # Sorts engaging items relative to high score ranks

               recommended_catalog[category] = scored_books + unscored_books  # Combines top items in front of untouched ones inside the container
     if not recommended_catalog:   # Safety override checking if the tracking logs didn't line up with folder naming conventions
          return all_books         # Re-exposes baseline folders to keep the frontend running smoothly
     return recommended_catalog    # Returns modified, sorted, and category-filtered data objects back to route calls

# Single-row algorithmic routine that destroys sorting walls to create seamless recommendation queues
def get_flat_recommendations(username: str) -> list:
    all_books_catalog = get_Books()          # Grabs raw folder assets grouped under their respective nested folder titles
    user_scores = get_user_scores(username)  # Extracts targeted scoring data specific to this user account
    
    flat_book_list = []  # Prepares a clean, flat list array to receive books out of their original folder groupings
    
    # 1. Break the books out of their category walls
    for category, books in all_books_catalog.items():  # Steps cleanly through structural folder divisions
        for book in books:                             # Steps inside isolated data dictionaries for individual books
            book['category'] = category                # Binds a category property to the item so HTML paths don't lose its folder
            book['score'] = user_scores.get(book['title'], 0)  # Applies past score tracking numbers or defaults to a clean zero value
            flat_book_list.append(book)                # Feeds data records into one single combined list array
            
    # 2. Sort the entire master list by score (highest scores first)
    # If the user has history, things they interact with float to the top
    flat_book_list.sort(key=lambda x: x['score'], reverse=True)  # Rearranges the flat list using user interaction scores as the priority metric
    
    # 3. Filter rule: If they have tracking data, let's ONLY show books 
    # they have actually interacted with (score > 0)
    has_history = any(b['score'] > 0 for b in flat_book_list)  # Scans list objects via inline boolean generators to look for engagement history
    if has_history:                                            # Checks if the profile has generated any telemetry history markers
        flat_book_list = [b for b in flat_book_list if b['score'] > 0]  # Completely slices off unviewed items to hide untracked suggestions
        
    return flat_book_list  # Hands back a flattened, prioritized queue ready to feed directly into a single horizontal webpage slider row