from flask import flash,Blueprint, current_app, request, jsonify, render_template, session, redirect, url_for, Response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import decode_token
import jwt
import pathlib
import html
from datetime import datetime, timezone
from extensions import db
from model import Post, PostReport


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
    posts = Post.query.filter(Post.status.in_(["Approved", "admin"]))\
                      .order_by(Post.upvotes.desc()).all()
    
    user_id = session.get("user_id")
    user_role = session.get("user_role")
    reported_posts = []
    
    if user_id:
        # Get posts this user has reported
        reported_posts = [r.post_id for r in PostReport.query.filter_by(reported_by=user_id).all()]
    
    return jsonify([
        {
            "id": p.id,
            "category": p.category,
            "content": p.content,
            "timestamp": p.created_at.strftime("%m/%d/%Y %H:%M:%S") if p.created_at else "",
            "status": p.status,
            "upvotes": p.upvotes,
            "reported": p.id in reported_posts,
            "report_count": p.report_count if user_role == "admin" else None
        } for p in posts
    ])




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
    try:
        posts = Post.query.filter_by(status="Pending").all()
        return render_template("pending.html", posts=posts)
    except Exception as e:
        flash(f"Database error: {str(e)}", "error")
        return render_template("pending.html", posts=[])

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
    
    user_id = session.get("user_id")
    user_role = session.get("user_role")
    reported_posts = []
    
    if user_id:
        # Get posts this user has reported
        reported_posts = [r.post_id for r in PostReport.query.filter_by(reported_by=user_id).all()]
    
    return render_template("approved.html", posts=posts, reported_ids=reported_posts, show_report_count=(user_role == "admin"))

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




# ---------- New Admin Interface Helpers ----------
def flash_message(msg):
    flash(msg)

def badge(post):
    return f'<span class="badge badge-{post.status.lower()}">{post.status}</span>'


# ---------- New Admin Interface Routes ----------
@routes_bp.route("/seed")
def seed():
    if not Post.query.first():
        db.session.add_all([
            Post(content="First pending post", status="Pending", submitted_at=datetime.now(timezone.utc), created_by=1),
            Post(content="Another suggestion awaiting review", status="Pending", submitted_at=datetime.now(timezone.utc), created_by=1)
        ])
        db.session.commit()
    return "Seeded!"

@routes_bp.route("/admin-queue")
def admin_queue():
    posts = Post.query.filter(Post.status.in_(["Pending", "Flagged"])).all()
    return render_template("pending.html", posts=posts)

@routes_bp.route("/admin-approve/<int:pid>", methods=["POST"])
def approve(pid):
    _review(pid, "Approved", "Post approved ✅")
    return redirect(url_for("routes.admin_queue"))

@routes_bp.route("/admin-decline/<int:pid>", methods=["POST"])
def decline(pid):
    _review(pid, "Declined", "Post declined ❌")
    return redirect(url_for("routes.admin_queue"))

def _review(pid, new_status, msg):
    p = Post.query.get_or_404(pid)
    p.status = new_status
    p.reviewed_at = datetime.now(timezone.utc)
    p.review_msg = msg
    db.session.commit()
    flash_message(msg)

@routes_bp.route("/admin-approved")
def approved():
    posts = Post.query.filter_by(status="Approved").all()
    reported = session.setdefault("reported_ids", [])
    return render_template("approved.html", posts=posts, reported_ids=reported)

@routes_bp.route("/admin-declined")
def declined():
    posts = Post.query.filter_by(status="Declined").all()
    return render_template("declined.html", posts=posts)

@routes_bp.route("/admin-all")
@routes_bp.route("/admin-all/<status>")
def all_posts_new(status=None):
    posts = Post.query.filter_by(status=status).all() if status else Post.query.all()
    reported = session.setdefault("reported_ids", [])
    return render_template("all_posts.html", posts=posts, reported_ids=reported, current_status=status)

@routes_bp.route("/admin-submit", methods=["GET", "POST"])
def submit():
    if request.method == "POST":
        db.session.add(Post(content=request.form["content"], status="Pending", submitted_at=datetime.now(timezone.utc), created_by=1))
        db.session.commit()
        flash_message("Post submitted for review.")
        return redirect(url_for("routes.submit"))
    return render_template("submit.html")

@routes_bp.route("/report/<int:pid>", methods=["GET", "POST"])
def report(pid):
    if not session.get("user_id"):
        flash("You must be logged in to report posts.", "error")
        return redirect(url_for('auth.login_page'))
    
    post = Post.query.get_or_404(pid)
    user_id = session.get("user_id")
    
    # Check if user already reported this post
    existing_report = PostReport.query.filter_by(post_id=pid, reported_by=user_id).first()
    
    if request.method == "POST" and not existing_report:
        try:
            # Create the report
            report = PostReport(
                post_id=pid,
                reported_by=user_id,
                reason=request.form["reason"][:200]
            )
            db.session.add(report)
            
            # Increment report count
            post.report_count += 1
            
            # If post gets 2 or more reports, move it to declined
            if post.report_count >= 2:
                post.status = "Declined"
                post.reviewed_at = datetime.now(timezone.utc)
                post.review_msg = f"Auto-declined due to {post.report_count} reports"
                flash(f"Post has been reported {post.report_count} times and has been automatically declined.", "warning")
            else:
                flash(f"Report submitted. Post has {post.report_count} report(s).", "success")
            
            db.session.commit()
            # Redirect based on user role - admins go to admin approved, users go to dashboard
            if session.get("user_role") == "admin":
                return redirect(url_for("routes.admin_approved"))
            else:
                return redirect(url_for("auth.user_dashboard"))
            
        except Exception as e:
            db.session.rollback()
            flash("Error submitting report. You may have already reported this post.", "error")
            # Redirect based on user role
            if session.get("user_role") == "admin":
                return redirect(url_for("routes.admin_approved"))
            else:
                return redirect(url_for("auth.user_dashboard"))
    
    return render_template("report.html", already=existing_report is not None, post=post)






