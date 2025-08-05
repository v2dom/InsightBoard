from flask import Blueprint, request, render_template, redirect, url_for, flash, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from model import User, Post, PostReport
from extensions import db
from datetime import datetime, timedelta, timezone
import random
import string

def generate_password(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

auth_bp = Blueprint('auth', __name__)

# Create New User
@auth_bp.route('/admin/create-account', methods=['GET', 'POST'])
def create_account():
    if session.get('user_role') != 'admin':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    if request.method == 'GET':
        return render_template('create_account.html')
    
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    role = request.form.get('role')
    password = request.form.get('password')
    if not password:
        return jsonify({"status": "error", "message": "Password is required"}), 400


    # Check for duplicate email
    if User.query.filter_by(email=email).first():
        return jsonify({"status": "error", "message": "Email already exists."}), 400

    new_user = User(
        name=f"{first_name} {last_name}",  
        email=email,
        password=generate_password_hash(password, method='pbkdf2:sha256'),
        role=role
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": f"Account for {email} created! Temporary password: {password}"
    })

# Show login form
@auth_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

# Process login
@auth_bp.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()

    if not user:
        flash('Invalid credentials', 'danger')
        return redirect(url_for('auth.login_page'))

    if user.locked_until and user.locked_until > datetime.utcnow():
        flash('Account locked. Try again later.', 'danger')
        return redirect(url_for('auth.login_page'))

    if not check_password_hash(user.password, password):
        if user.failed_attempts is None:
            user.failed_attempts = 0
        user.failed_attempts += 1
        if user.failed_attempts >= 3:
            user.locked_until = datetime.utcnow() + timedelta(minutes=5)
            flash('Too many failed attempts. Locked for 5 minutes.', 'danger')
        else:
            flash('Invalid password', 'danger')
        db.session.commit()
        return redirect(url_for('auth.login_page'))


    # Successful login
    session['user_id'] = user.id
    session['user_role'] = user.role

    name_parts = user.name.split(' ', 1)
    session['first_name'] = name_parts[0] if name_parts else 'User'
    session['last_name'] = name_parts[1] if len(name_parts) > 1 else ''
    
    user.failed_attempts = 0
    user.locked_until = None
    db.session.commit()

    if user.role == 'admin':
        return redirect(url_for('routes.admin_dashboard'))
    else:
        return redirect(url_for('auth.user_dashboard'))

# Show user dashboard
@auth_bp.route('/dashboard')
def user_dashboard():
    if not session.get("user_id"):
        return redirect(url_for('auth.login_page'))
    
    user_id = session["user_id"]
    user_role = session.get("user_role")
    
    # Get all approved posts for the feed (not just user's own)
    feed_posts = Post.query.filter(Post.status.in_(["Approved", "admin"]))\
                          .order_by(Post.upvotes.desc()).all()
    
    for post in feed_posts:
        if post.submitted_at and post.submitted_at.tzinfo is None:
            post.submitted_at = post.submitted_at.replace(tzinfo=timezone.utc)
        if post.reviewed_at and post.reviewed_at.tzinfo is None:
            post.reviewed_at = post.reviewed_at.replace(tzinfo=timezone.utc)
    
    # Get posts this user has reported
    reported_posts = []
    if user_id:
        reported_posts = [r.post_id for r in PostReport.query.filter_by(reported_by=user_id).all()]
    
    return render_template("userdash.html", 
                         feed_posts=feed_posts,
                         reported_ids=reported_posts,
                         show_report_count=(user_role == "admin"))

# Show feedback form
@auth_bp.route('/dashboard/feedback')
def dashboard_feedback():
    if not session.get("user_id"):
        return redirect(url_for('auth.login_page'))
    return render_template("submit.html")

# Show user's posts
@auth_bp.route('/dashboard/my-posts')
def my_posts():
    if not session.get("user_id"):
        return redirect(url_for('auth.login_page'))
    
    user_id = session["user_id"]
    
    user_approved_posts = Post.query.filter_by(created_by=user_id, status="Approved").order_by(Post.submitted_at.desc()).all()
    pending_posts = Post.query.filter_by(created_by=user_id, status="Pending").order_by(Post.submitted_at.desc()).all()
    declined_posts = Post.query.filter_by(created_by=user_id, status="Declined").order_by(Post.submitted_at.desc()).all()

    for post in user_approved_posts + pending_posts + declined_posts:
        if post.submitted_at and post.submitted_at.tzinfo is None:
            post.submitted_at = post.submitted_at.replace(tzinfo=timezone.utc)
        if post.reviewed_at and post.reviewed_at.tzinfo is None:
            post.reviewed_at = post.reviewed_at.replace(tzinfo=timezone.utc)
    
    return render_template("my_posts.html", 
                         approved_posts=user_approved_posts,
                         pending_posts=pending_posts,
                         declined_posts=declined_posts)


# Logout
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login_page'))


