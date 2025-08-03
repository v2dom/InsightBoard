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
    if not session.get("user_id"):
        return jsonify({"status": "error", "message": "You must be logged in to submit feedback."}), 401
    
    # Admins cannot submit feedback
    if session.get('user_role') == 'admin':
        return jsonify({"status": "error", "message": "Admin users cannot submit anonymous feedback."}), 403
    
    data = request.get_json()
    category = data.get("category")
    content = data.get("content")

    if not category or not content:
        return jsonify({"status": "error", "message": "Category and content required."}), 400

    new_post = Post(
        category=category,
        content=content,
        submitted_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        status="pending",
        upvotes=0,
        created_by = session.get("user_id") or 1
    )

    db.session.add(new_post)
    db.session.commit()

    return jsonify({"status": "success", "message": "Thank you for your feedback! It has been submitted and is now pending approval."})


@routes_bp.route("/feedback", methods=["GET"])
def serve_feedback_form():
    if not session.get("user_id"):
        flash("You must be logged in to submit feedback.", "error")
        return redirect(url_for('auth.login_page'))
    
    # Block admin users from submitting anonymous feedback
    if session.get('user_role') == 'admin':
        flash("Admin users cannot submit anonymous feedback.", "error")
        return redirect(url_for('auth.user_dashboard'))
    
    return render_template("submit.html")


@routes_bp.route("/api/approved_posts", methods=["GET"])
def get_approved_posts():
    posts = Post.query.filter(Post.status.in_(["approved", "admin"]))\
                      .order_by(Post.upvotes.desc()).all()
    return jsonify([
        {
            "category": p.category,
            "content": p.content,
            "timestamp": p.created_at.strftime("%m/%d/%Y %H:%M:%S") if p.created_at else "",
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
        created_at=datetime.now(timezone.utc),
        submitted_at=datetime.now(timezone.utc),
        status="admin",
        upvotes=0,
        created_by=session.get("user_id") or 1  # Use actual user ID if available
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

# User Dashboard
@routes_bp.route("/userdash")
def user_dashboard():
    if not session.get("user_id"):
        return redirect(url_for('auth.login_page'))
    
    user_id = session["user_id"]
    
    approved_posts = Post.query.filter_by(created_by=user_id, status="Approved").order_by(Post.submitted_at.desc()).all()
    pending_posts = Post.query.filter_by(created_by=user_id, status="Pending").order_by(Post.submitted_at.desc()).all()
    declined_posts = Post.query.filter_by(created_by=user_id, status="Declined").order_by(Post.submitted_at.desc()).all()
    
    return render_template("userdash.html", 
                         approved_posts=approved_posts,
                         pending_posts=pending_posts,
                         declined_posts=declined_posts)




