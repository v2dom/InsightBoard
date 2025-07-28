# <<<<<<< HEAD (<<< had to comment this, errors show -Khanh)
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
# import pytz (<<< this import isn't working on my end -Khanh)
import json
import os

app = Flask(__name__)
CORS(app)

# Test Auth
is_logged_in = True
is_admin = True

# Arizona Time Zone
# az = pytz.timezone("US/Arizona") (<<< get the datetime function for this -Khanh)

# Path Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
POSTS_FILE = os.path.join(BASE_DIR, "posts.json")

# Anonymous Feedback
@app.route("/create-feedback", methods=["GET"])
def serve_feedback_form():
    if not is_logged_in:
        return "Please log in to submit feedback.", 403
    return send_file(os.path.join(FRONTEND_DIR, "feedback.html"))

@app.route("/submit-feedback", methods=["POST", "OPTIONS"])
def submit_feedback():
    if request.method == "OPTIONS":
        return jsonify({"status": "ok"}), 200

    if not is_logged_in:
        return jsonify({"status": "error", "message": "You must be logged in to submit feedback."}), 401

    data = request.get_json()
    feedback_entry = {
        "category": data.get("category"),
        "content": data.get("content"),
        "timestamp": datetime.now(az).strftime("%m/%d/%Y %H:%M:%S"),
        "status": "pending",
        "upvotes": 0
    }

    posts = []
    if os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, "r") as f:
            posts = json.load(f)

    posts.append(feedback_entry)

    with open(POSTS_FILE, "w") as f:
        json.dump(posts, f, indent=4)

    return jsonify({"status": "success", "message": "Feedback received"}), 200

# Admin Post
@app.route("/create-post", methods=["GET"])
def serve_create_post():
    if not (is_logged_in and is_admin):
        return "Access denied. Admins only.", 403
    return send_file(os.path.join(FRONTEND_DIR, "adminpost.html"))

@app.route("/create-post", methods=["POST"])
def handle_create_post():
    if not (is_logged_in and is_admin):
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    category = request.form.get("category")
    content = request.form.get("post")

    post_entry = {
        "category": category,
        "content": content,
        "timestamp": datetime.now(az).strftime("%m/%d/%Y %H:%M:%S"),
        "status": "admin",
        "upvotes": 0
    }

    posts = []
    if os.path.exists(POSTS_FILE):
        with open(POSTS_FILE, "r") as f:
            posts = json.load(f)

    posts.append(post_entry)

    with open(POSTS_FILE, "w") as f:
        json.dump(posts, f, indent=4)

    return jsonify({"status": "success", "message": "Post submitted successfully!"})

# View Posts
@app.route("/api/approved_posts", methods=["GET"])
def get_approved_posts():
    if not os.path.exists(POSTS_FILE):
        return jsonify([])

    with open(POSTS_FILE, "r") as f:
        all_posts = json.load(f)

    visible_posts = [
        p for p in all_posts if p.get("status") in ("approved", "admin")
    ]
    visible_posts.sort(key=lambda x: x.get("upvotes", 0), reverse=True)

    return jsonify(visible_posts)

@app.route("/feed", methods=["GET"])
def serve_feed():
    if not is_logged_in:
        return "Access denied. Please log in to view the feed.", 403
    return send_file(os.path.join(FRONTEND_DIR, "feed.html"))

@app.route("/")
def home():
    return "Flask is running!"

if __name__ == "__main__":
    app.run(port=5001, debug=True)
# =======
from flask import Flask, request, jsonify
import os, json, uuid, random, string
from flask import send_from_directory

app = Flask(__name__, static_folder="../admin_frontend", static_url_path="")
app.secret_key = "supersecret123"

USER_FILE = "backend/users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        with open(USER_FILE, "w") as f:
            json.dump([], f)
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

def generate_password(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "admindash.html")

@app.route("/create-account", methods=["POST"])
def create_account():
    first = request.form["first_name"]
    last = request.form["last_name"]
    email = request.form["email"]
    role = request.form["role"]
    password = generate_password()
    account_id = str(uuid.uuid4())

    users = load_users()

    if any(user["email"] == email for user in users):
        return jsonify({"status": "error", "message": "Email already exists."})

    new_user = {
        "id": account_id,
        "first_name": first,
        "last_name": last,
        "email": email,
        "role": role,
        "password": password
    }

    users.append(new_user)
    save_users(users)

    return jsonify({"status": "success", "message": f"Account for {email} created! Temporary password: {password}"})

if __name__ == "__main__":
    app.run(debug=True)
# >>>>>>> 1a17e33 (Add backend folder) (<<< had to comment this, errors show -Khanh)
