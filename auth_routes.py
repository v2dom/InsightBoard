from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from model import User
from extensions import db
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)

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
    user.failed_attempts = 0
    user.locked_until = None
    db.session.commit()

    if user.role == 'admin':
        return redirect(url_for('auth.admin_dashboard'))
    else:
        return redirect(url_for('auth.user_dashboard'))

# Show user dashboard
@auth_bp.route('/dashboard')
def user_dashboard():
    return render_template('dashboard.html', role='user')

# Show admin dashboard
@auth_bp.route('/admin')
def admin_dashboard():
    return render_template('dashboard.html', role='admin')

# Logout
@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login_page'))
