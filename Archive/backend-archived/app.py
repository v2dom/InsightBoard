from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from datetime import datetime
import pytz
import json
import os

app = Flask(__name__)
CORS(app)

# Test Auth
is_logged_in = True
is_admin = True

# Arizona Time Zone
az = pytz.timezone("US/Arizona")

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