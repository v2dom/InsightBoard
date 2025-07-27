from __future__ import annotations

import datetime as dt
import logging
import os
from functools import wraps
from typing import Optional, List

from flask import (
    Flask,
    abort,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


instance_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
try:
    os.makedirs(instance_path, exist_ok=True)
    logger.info(f"Instance directory created/verified at: {instance_path}")
except Exception as e:
    logger.error(f"Error creating instance directory: {e}")
    raise

# Database configuration
db_path = os.path.join(instance_path, 'posts.db')
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key'),  # Better secret key handling
    SQLALCHEMY_DATABASE_URI=f"sqlite:///{db_path}",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

db = SQLAlchemy(app)

class Post(db.Model):
    """Database model for blog posts."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    body = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=dt.datetime.utcnow)
    created_by = db.Column(db.String(80), default="anonymous")

    def __repr__(self) -> str:
        return f"<Post {self.id} {self.title!r} {self.status}>"

    @property
    def excerpt(self) -> str:
        """Return truncated body text."""
        max_length = 60
        return f"{self.body[:max_length]}..." if len(self.body) > max_length else self.body

def init_db() -> None:
    """Initialize database with sample data if empty."""
    try:
        with app.app_context():
            db.create_all()
            if not Post.query.count():
                sample_posts = [
                    Post(
                        title=f"Sample Post {i}",
                        body="Testing.",
                        status="pending",
                        created_at=dt.datetime.utcnow() - dt.timedelta(minutes=10 * i),
                    )
                    for i in range(1, 6)
                ]
                db.session.add_all(sample_posts)
                db.session.commit()
                logger.info("Database initialized successfully!")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

def admin_required(f):
    """Decorator to check if user has admin role."""
    @wraps(f)
    def wrapped(*args, **kwargs):
        role = session.get("role")
        if role != "admin":
            logger.warning(f"Unauthorized access attempt with role: {role}")
            abort(403 if role else 401)
        return f(*args, **kwargs)
    return wrapped

@app.route("/")
def index():
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        role = request.form.get("role") or "user"
        session["role"] = role
        logger.info(f"User logged in with role: {role}")
        return redirect(url_for("admin_pending"))
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/admin/posts/pending")
@admin_required
def admin_pending():
    posts: List[Post] = (
        Post.query.filter_by(status="pending")
        .order_by(Post.created_at.asc())
        .all()
    )
    return render_template("pending_posts.html", posts=posts)

@app.route("/admin/reset", methods=["POST"])
@admin_required
def reset_db():
    """Reset database with fresh sample data."""
    try:
        with app.app_context():
            # Drop all tables
            db.drop_all()
            # Create all tables
            db.create_all()
            # Add new sample posts
            sample_posts = [
                Post(
                    title=f"Sample Post {i}",
                    body="Testing.",
                    status="pending",
                    created_at=dt.datetime.utcnow() - dt.timedelta(minutes=10 * i),
                )
                for i in range(1, 6)
            ]
            db.session.add_all(sample_posts)
            db.session.commit()
            logger.info("Database reset successfully!")
        return redirect(url_for("admin_pending"))
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        return f"Error resetting database: {e}", 500

def reset_db() -> None:
    """Reset database with fresh sample data."""
    try:
        with app.app_context():
            # Drop all tables
            db.drop_all()
            # Create all tables
            db.create_all()
            # Add new sample posts
            sample_posts = [
                Post(
                    title=f"Sample Post {i}",
                    body="Testing.",
                    status="pending",
                    created_at=dt.datetime.utcnow() - dt.timedelta(minutes=10 * i),
                )
                for i in range(1, 6)
            ]
            db.session.add_all(sample_posts)
            db.session.commit()
            logger.info("Database reset successfully!")
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        raise

# Add a new route to trigger the reset
@app.route("/admin/reset-db")
@admin_required
def reset_database():
    try:
        reset_db()
        return redirect(url_for("admin_pending"))
    except Exception as e:
        return f"Error resetting database: {e}", 500

if __name__ == "__main__":
    logger.info("Initializing database...")
    init_db()
    logger.info("Starting Flask application...")
    app.run(debug=True)