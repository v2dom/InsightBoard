from flask import flash,Blueprint, current_app, request, jsonify, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import decode_token
import jwt
from datetime import datetime, timezone
from extensions import db
from model import Post


routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/')
def home():
    return render_template('index.html')  # Your landing page

    
@routes_bp.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json()
    category = data.get("category")
    content = data.get("content")

    if not category or not content:
        return jsonify({"status": "error", "message": "Category and content required."}), 400

    new_post = Post(
        category=category,
        content=content,
        timestamp=datetime.now(timezone.utc),
        status="pending",
        upvotes=0
    )
    db.session.add(new_post)
    db.session.commit()

    return jsonify({"status": "success", "message": "Feedback received"})


@routes_bp.route("/feedback", methods=["GET"])
def serve_feedback_form():
    return render_template("feedback.html")


@routes_bp.route("/api/approved_posts", methods=["GET"])
def get_approved_posts():
    posts = Post.query.filter(Post.status.in_(["approved", "admin"]))\
                      .order_by(Post.upvotes.desc()).all()
    return jsonify([
        {
            "category": p.category,
            "content": p.content,
            "timestamp": p.timestamp.strftime("%m/%d/%Y %H:%M:%S"),
            "status": p.status,
            "upvotes": p.upvotes
        } for p in posts
    ])

@routes_bp.route("/feed", methods=["GET"])
def serve_feed():
    return render_template("feed.html")


@routes_bp.route("/admin/create-post", methods=["GET"])
def serve_create_post():
    if session.get('user_role') != 'admin':
        return redirect(url_for('auth.login_page'))
    return render_template("adminpost.html")

@routes_bp.route("/admin/create-post", methods=["POST"])
def handle_create_post():
    if session.get('user_role') != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    category = request.form.get("category")
    content = request.form.get("post")

    if not category or not content:
        return jsonify({"status": "error", "message": "Category and content required."}), 400

    new_post = Post(
        category=category,
        content=content,
        timestamp=datetime.now(timezone.utc),
        status="admin",
        upvotes=0
    )
    db.session.add(new_post)
    db.session.commit()

    return jsonify({"status": "success", "message": "Post submitted successfully!"})

@routes_bp.route("/admin/pending")
def admin_pending():
    posts = Post.query.filter_by(status="Pending").all()
    return render_template("pending.html", posts=posts)

@routes_bp.route("/admin/approve/<int:pid>", methods=["POST"])
def approve_post(pid):
    post = Post.query.get_or_404(pid)
    post.status = "Approved"
    post.reviewed_at = datetime.now(timezone.utc)
    post.review_msg = "Approved ✅"
    db.session.commit()
    return redirect(url_for('routes.admin_pending'))

@routes_bp.route("/admin/decline/<int:pid>", methods=["POST"])
def decline_post(pid):
    post = Post.query.get_or_404(pid)
    post.status = "Declined"
    post.reviewed_at = datetime.now(timezone.utc)
    post.review_msg = "Declined ❌"
    db.session.commit()
    return redirect(url_for('routes.admin_pending'))

@routes_bp.route("/admin/approved")
def admin_approved():
    posts = Post.query.filter_by(status="Approved").all()
    return render_template("approved.html", posts=posts)

@routes_bp.route("/admin/declined")
def admin_declined():
    posts = Post.query.filter_by(status="Declined").all()
    return render_template("declined.html", posts=posts)

@routes_bp.route("/admin/all")
def all_posts():
    posts = Post.query.all()
    return render_template("all_posts.html", posts=posts)

@routes_bp.route("/admin/submit", methods=["GET", "POST"])
def admin_submit_form():
    if request.method == "POST":
        content = request.form["content"]
        post = Post(content=content, status="Pending", submitted_at=datetime.now(timezone.utc))
        db.session.add(post)
        db.session.commit()
        flash("Post submitted for review.")
        return redirect(url_for('routes.admin_submit_form'))
    return render_template("submit.html")




