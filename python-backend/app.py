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

# Anonymous Feedback
@app.route("/create-feedback", methods=["GET"])
def serve_feedback_form():
    if not is_logged_in:
        return "Please log in to submit feedback.", 403
    return send_file("feedback.html")

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
        "approved": False
    }

    file = "pending_approval.json"
    feedback_list = []

    if os.path.exists(file):
        with open(file, "r") as f:
            feedback_list = json.load(f)

    feedback_list.append(feedback_entry)

    with open(file, "w") as f:
        json.dump(feedback_list, f, indent=4)

    return jsonify({"status": "success", "message": "Feedback received"}), 200

# Admin Post
@app.route("/create-post", methods=["GET"])
def serve_create_post():
    if not (is_logged_in and is_admin):
        return "Access denied. Admins only.", 403
    return send_file("adminpost.html")

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
        "approved": True
    }

    file = "admin_posts.json"
    posts = []

    if os.path.exists(file):
        with open(file, "r") as f:
            posts = json.load(f)

    posts.append(post_entry)

    with open(file, "w") as f:
        json.dump(posts, f, indent=4)

    return jsonify({"status": "success", "message": "Post submitted successfully!"})

@app.route("/")
def home():
    return "Flask is running!"

if __name__ == "__main__":
    app.run(port=5001, debug=True)
