import os
from datetime import datetime
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash

# Try loading environment variables from local .env file (useful for Windows/local runs)
try:
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    key, val = line.strip().split("=", 1)
                    os.environ[key.strip()] = val.strip()
except Exception:
    pass

# Fetch Mongo URI from environment variable, fallback to local host connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/paper_scraper_db")

# Initialize Client
# We use a try-except block so that even if MongoDB is not reachable immediately, the app doesn't crash on start
try:
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client.get_default_database()
    # Ping database to verify connection
    client.server_info()
    print("Successfully connected to MongoDB.")
except Exception as e:
    print(f"Warning: Could not connect to MongoDB at {MONGO_URI}. Details: {e}")
    # Fallback mock setup if DB is offline during development/build
    client = None
    db = None

# Helper collections
def get_papers_col():
    return db["papers"] if db is not None else None

def get_users_col():
    return db["users"] if db is not None else None


# --- Paper Caching Methods ---

def get_cached_paper(article_number):
    """Retrieve paper metadata from MongoDB cache if it exists."""
    col = get_papers_col()
    if col is None:
        return None
    try:
        doc = col.find_one({"_id": str(article_number)})
        if doc:
            # Convert _id back to articleNumber for frontend mapping
            doc["articleNumber"] = doc["_id"]
            return doc
    except Exception as e:
        print(f"Error reading paper cache for {article_number}: {e}")
    return None

def cache_paper(paper_data, email=None):
    """Save paper metadata to MongoDB cache."""
    col = get_papers_col()
    if col is None or not paper_data or not paper_data.get("articleNumber"):
        return False
    try:
        doc = dict(paper_data)
        doc["_id"] = str(paper_data["articleNumber"])
        doc["scraped_by"] = email
        doc["scraped_at"] = datetime.utcnow()
        
        # Upsert: update if exists, insert if new
        col.replace_one({"_id": doc["_id"]}, doc, upsert=True)
        print(f"Cached paper in MongoDB: {doc['_id']} (\"{doc.get('title')}\")")
        return True
    except Exception as e:
        print(f"Error saving paper to cache: {e}")
    return False


# --- User Authentication Methods ---

def register_user(email, password):
    """Register a new user with hashed password."""
    col = get_users_col()
    if col is None:
        return False, "Database connection not available."
    
    email = email.strip().lower()
    if not email or not password:
        return False, "Email and password are required."
        
    try:
        # Check if user already exists
        if col.find_one({"_id": email}):
            return False, "User with this email already exists."
            
        password_hash = generate_password_hash(password)
        col.insert_one({
            "_id": email,
            "password_hash": password_hash,
            "created_at": datetime.utcnow(),
            "last_login": datetime.utcnow()
        })
        print(f"Successfully registered user: {email}")
        return True, "Registration successful."
    except Exception as e:
        print(f"Error registering user {email}: {e}")
        return False, f"Database error: {str(e)}"

def authenticate_user(email, password):
    """Authenticate a user and update their last login time."""
    col = get_users_col()
    if col is None:
        return False, "Database connection not available."
        
    email = email.strip().lower()
    if not email or not password:
        return False, "Email and password are required."
        
    try:
        user = col.find_one({"_id": email})
        if not user:
            return False, "Invalid email or password."
            
        if check_password_hash(user["password_hash"], password):
            # Update last login time
            col.update_one({"_id": email}, {"$set": {"last_login": datetime.utcnow()}})
            return True, "Authentication successful."
            
        return False, "Invalid email or password."
    except Exception as e:
        print(f"Error authenticating user {email}: {e}")
        return False, f"Database error: {str(e)}"
