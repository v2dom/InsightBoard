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
    return render_template('index.html')

    
@routes_bp.route("/submit-feedback", methods=["POST"])
def submit_feedback():
    if not session.get("user_id"):
        return jsonify({"status": "error", "message": "You must be logged in to submit feedback."}), 401

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
    
    if session.get('user_role') == 'admin':
        flash("Admin users cannot submit anonymous feedback.", "error")
        return redirect(url_for('auth.user_dashboard'))
    
    return render_template("submit.html")


@routes_bp.route("/api/approved_posts", methods=["GET"])
def get_approved_posts():
    posts = Post.query.filter(Post.status.in_(["Approved", "admin"]))\
                      .order_by(Post.upvotes.desc()).all()
    
    for post in posts:
        if post.created_at and post.created_at.tzinfo is None:
            post.created_at = post.created_at.replace(tzinfo=timezone.utc)
    
    user_id = session.get("user_id")
    user_role = session.get("user_role")
    reported_posts = []
    
    if user_id:
        reported_posts = [r.post_id for r in PostReport.query.filter_by(reported_by=user_id).all()]
    
    return jsonify([
        {
            "id": p.id,
            "category": p.category,
            "content": p.content,
            "timestamp": p.created_at.isoformat() if p.created_at else "",
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
        created_by=session.get("user_id") or 1
    )

    db.session.add(new_post)
    db.session.commit()

    return jsonify({"status": "success", "message": "Post submitted successfully!"})

@routes_bp.route("/admin/pending")
def admin_pending():
    try:
        pending_posts = Post.query.filter_by(status="Pending").all()
        flagged_posts = Post.query.filter(Post.report_count > 0, Post.status == "Approved").all()

        for post in pending_posts:
            if post.submitted_at and post.submitted_at.tzinfo is None:
                post.submitted_at = post.submitted_at.replace(tzinfo=timezone.utc)
        
        for post in flagged_posts:
            if post.submitted_at and post.submitted_at.tzinfo is None:
                post.submitted_at = post.submitted_at.replace(tzinfo=timezone.utc)
            if post.reviewed_at and post.reviewed_at.tzinfo is None:
                post.reviewed_at = post.reviewed_at.replace(tzinfo=timezone.utc)

        flagged_posts_with_reports = []
        for post in flagged_posts:
            reports = PostReport.query.filter_by(post_id=post.id).all()
            for report in reports:
                if report.reported_at and report.reported_at.tzinfo is None:
                    report.reported_at = report.reported_at.replace(tzinfo=timezone.utc)
            flagged_posts_with_reports.append({
                'post': post,
                'reports': reports
            })
        
        return render_template("pending.html", 
                             pending_posts=pending_posts, 
                             flagged_posts_with_reports=flagged_posts_with_reports)
    except Exception as e:
        flash(f"Database error: {str(e)}", "error")
        return render_template("pending.html", pending_posts=[], flagged_posts_with_reports=[])

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

@routes_bp.route("/admin/approve-flagged/<int:pid>", methods=["POST"])
def approve_flagged_post(pid):
    post = Post.query.get_or_404(pid)
    post.report_count = 0
    PostReport.query.filter_by(post_id=pid).delete()
    post.reviewed_at = datetime.now(timezone.utc)
    post.review_msg = "Re-approved after flag review ✅"
    db.session.commit()
    return redirect(url_for('routes.admin_pending'))

@routes_bp.route("/admin/decline-flagged/<int:pid>", methods=["POST"])
def decline_flagged_post(pid):
    post = Post.query.get_or_404(pid)
    post.status = "Declined"
    post.reviewed_at = datetime.now(timezone.utc)
    post.review_msg = "Declined after flag review ❌"
    PostReport.query.filter_by(post_id=pid).delete()
    db.session.commit()
    return redirect(url_for('routes.admin_pending'))

@routes_bp.route("/admin")
def admin_dashboard():
    if session.get('user_role') != 'admin':
        return redirect(url_for('auth.login_page'))
    
    posts = Post.query.filter(Post.status.in_(["Approved", "admin"])).order_by(Post.upvotes.desc()).all()
    
    for post in posts:
        if post.submitted_at and post.submitted_at.tzinfo is None:
            post.submitted_at = post.submitted_at.replace(tzinfo=timezone.utc)
        if post.reviewed_at and post.reviewed_at.tzinfo is None:
            post.reviewed_at = post.reviewed_at.replace(tzinfo=timezone.utc)
    
    user_id = session.get("user_id")
    user_role = session.get("user_role")
    reported_posts = []
    
    if user_id:
        reported_posts = [r.post_id for r in PostReport.query.filter_by(reported_by=user_id).all()]
    
    return render_template("admin_dashboard.html", posts=posts, reported_ids=reported_posts, show_report_count=(user_role == "admin"))

@routes_bp.route("/admin/approved")
def admin_approved():
    posts = Post.query.filter_by(status="Approved").all()
    
    for post in posts:
        if post.submitted_at and post.submitted_at.tzinfo is None:
            post.submitted_at = post.submitted_at.replace(tzinfo=timezone.utc)
        if post.reviewed_at and post.reviewed_at.tzinfo is None:
            post.reviewed_at = post.reviewed_at.replace(tzinfo=timezone.utc)
    
    user_id = session.get("user_id")
    user_role = session.get("user_role")
    reported_posts = []
    
    if user_id:
        reported_posts = [r.post_id for r in PostReport.query.filter_by(reported_by=user_id).all()]
    
    return render_template("approved.html", posts=posts, reported_ids=reported_posts, show_report_count=(user_role == "admin"))

@routes_bp.route("/admin/declined")
def admin_declined():
    posts = Post.query.filter_by(status="Declined").all()

    for post in posts:
        if post.submitted_at and post.submitted_at.tzinfo is None:
            post.submitted_at = post.submitted_at.replace(tzinfo=timezone.utc)
        if post.reviewed_at and post.reviewed_at.tzinfo is None:
            post.reviewed_at = post.reviewed_at.replace(tzinfo=timezone.utc)
    
    return render_template("declined.html", posts=posts)

@routes_bp.route("/admin/all")
@routes_bp.route("/admin/all/<status>")
def all_posts(status=None):
    if status == "Flagged":
        posts = Post.query.filter(Post.report_count > 0, Post.status == "Approved").all()
    elif status:
        posts = Post.query.filter_by(status=status).all()
    else:
        posts = Post.query.all()
    
    for post in posts:
        if post.submitted_at and post.submitted_at.tzinfo is None:
            post.submitted_at = post.submitted_at.replace(tzinfo=timezone.utc)
        if post.reviewed_at and post.reviewed_at.tzinfo is None:
            post.reviewed_at = post.reviewed_at.replace(tzinfo=timezone.utc)
    
    return render_template("all_posts.html", posts=posts, current_status=status)

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




def flash_message(msg):
    flash(msg)

def badge(post):
    return f'<span class="badge badge-{post.status.lower()}">{post.status}</span>'


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
    
    for post in posts:
        if post.submitted_at and post.submitted_at.tzinfo is None:
            post.submitted_at = post.submitted_at.replace(tzinfo=timezone.utc)
        if post.reviewed_at and post.reviewed_at.tzinfo is None:
            post.reviewed_at = post.reviewed_at.replace(tzinfo=timezone.utc)
    
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
    
    for post in posts:
        if post.submitted_at and post.submitted_at.tzinfo is None:
            post.submitted_at = post.submitted_at.replace(tzinfo=timezone.utc)
        if post.reviewed_at and post.reviewed_at.tzinfo is None:
            post.reviewed_at = post.reviewed_at.replace(tzinfo=timezone.utc)
    
    reported = session.setdefault("reported_ids", [])
    return render_template("approved.html", posts=posts, reported_ids=reported)

@routes_bp.route("/admin-declined")
def declined():
    posts = Post.query.filter_by(status="Declined").all()
    
    for post in posts:
        if post.submitted_at and post.submitted_at.tzinfo is None:
            post.submitted_at = post.submitted_at.replace(tzinfo=timezone.utc)
        if post.reviewed_at and post.reviewed_at.tzinfo is None:
            post.reviewed_at = post.reviewed_at.replace(tzinfo=timezone.utc)
    
    return render_template("declined.html", posts=posts)

@routes_bp.route("/admin-all")
@routes_bp.route("/admin-all/<status>")
def all_posts_new(status=None):
    posts = Post.query.filter_by(status=status).all() if status else Post.query.all()
    
    for post in posts:
        if post.submitted_at and post.submitted_at.tzinfo is None:
            post.submitted_at = post.submitted_at.replace(tzinfo=timezone.utc)
        if post.reviewed_at and post.reviewed_at.tzinfo is None:
            post.reviewed_at = post.reviewed_at.replace(tzinfo=timezone.utc)
    
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

@routes_bp.route("/badges")
def badges():
    if not session.get("user_id"):
        return redirect(url_for('auth.login_page'))
    return render_template("badges.html")

@routes_bp.route("/report/<int:pid>", methods=["GET", "POST"])
def report(pid):
    if not session.get("user_id"):
        flash("You must be logged in to report posts.", "error")
        return redirect(url_for('auth.login_page'))
    
    post = Post.query.get_or_404(pid)
    user_id = session.get("user_id")
    
    existing_report = PostReport.query.filter_by(post_id=pid, reported_by=user_id).first()
    
    if request.method == "POST" and not existing_report:
        try:
            report = PostReport(
                post_id=pid,
                reported_by=user_id,
                reason=request.form["reason"][:200]
            )
            db.session.add(report)
            
            post.report_count += 1
            
            if post.report_count >= 3:
                post.status = "Declined"
                post.reviewed_at = datetime.now(timezone.utc)
                post.review_msg = f"Auto-declined due to {post.report_count} reports"
                flash(f"Post has been reported {post.report_count} times and has been automatically declined.", "warning")
            else:
                post.status = "Approved"
                flash(f"Report submitted. Post has {post.report_count} report(s) and will be reviewed by admin.", "success")
            
            db.session.commit()
            if session.get("user_role") == "admin":
                return redirect(url_for("routes.admin_approved"))
            else:
                return redirect(url_for("auth.user_dashboard"))
            
        except Exception as e:
            db.session.rollback()
            flash("Error submitting report. You may have already reported this post.", "error")
            if session.get("user_role") == "admin":
                return redirect(url_for("routes.admin_approved"))
            else:
                return redirect(url_for("auth.user_dashboard"))
    
    return render_template("report.html", already=existing_report is not None, post=post)

@routes_bp.route("/admin/search-filter", methods=["GET"])
def admin_search_filter():
    if session.get("user_role") != "admin":
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    keyword = request.args.get("q", "").strip().lower()
    selected_categories = request.args.getlist("category")
    selected_statuses = request.args.getlist("status")

    query = Post.query

    if keyword:
        query = query.filter(Post.content.ilike(f"%{keyword}%"))

    if selected_categories:
        query = query.filter(Post.category.in_(selected_categories))

    if selected_statuses:
        if "All" in selected_statuses:
            pass
        else:
            query = query.filter(Post.status.in_(selected_statuses))

    posts = query.order_by(Post.submitted_at.desc()).all()

    return render_template(
        "all_posts.html",
        posts=posts,
        selected_statuses=selected_statuses,
        selected_categories=selected_categories,
        current_status="Filtered"
    )

        


