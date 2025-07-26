from flask import (
    Flask, request, redirect, url_for, render_template, flash  # Changed from render_template_string
)
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///posts.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "demo-secret"
db = SQLAlchemy(app)

is_logged_in = True
is_admin = True


# ------------- Database model -------------
class Post(db.Model):
    id           = db.Column(db.Integer, primary_key=True)
    content      = db.Column(db.Text,  nullable=False)
    status       = db.Column(db.String(10), default="Pending")   # Pending | Approved | Declined
    submitted_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    reviewed_at  = db.Column(db.DateTime)
    review_msg   = db.Column(db.String(200))

# ------------- Helper -------------
def review(pid, new_status, msg):
    post = Post.query.get_or_404(pid)
    post.status, post.reviewed_at, post.review_msg = new_status, datetime.now(timezone.utc), msg
    db.session.commit()
    flash(msg)

# ------------- Routes -------------
# Initialize the database at startup
with app.app_context():
    db.create_all()

@app.route("/seed")
def seed():
    if not Post.query.first():
        db.session.add_all([
            Post(content="First pending post"),
            Post(content="Another suggestion awaiting review")
        ])
        db.session.commit()
    return "Seeded!"

# Admin queue
@app.route("/")
def pending():
    posts = Post.query.filter_by(status="Pending").all()
    return render_template('pending.html', title="Pending", posts=posts)

# Approve / Decline actions
@app.post("/approve/<int:pid>")
def approve(pid):
    review(pid, "Approved", "Post approved ✅ - The post is now visible to all users.")
    return redirect(url_for('pending'))

@app.post("/decline/<int:pid>")
def decline(pid):
    review(pid, "Declined", "Post declined ❌ - The post will not be shown to users.")
    return redirect(url_for('pending'))

# Public feed
@app.route("/approved")
def approved():
    posts = Post.query.filter_by(status="Approved").all()
    return render_template('approved.html', title="Approved", posts=posts)

# Declined posts view
@app.route("/declined")
def declined():
    posts = Post.query.filter_by(status="Declined").all()
    return render_template('declined.html', title="Declined", posts=posts)

# All posts view with optional status filter
@app.route("/all")
@app.route("/all/<status>")
def all_posts(status=None):
    if status:
        posts = Post.query.filter_by(status=status).all()
    else:
        posts = Post.query.all()
    return render_template('all_posts.html', title="All Posts", posts=posts)

# Simple form to create new pending posts
@app.route("/submit", methods=["GET", "POST"])
def submit_form():
    if request.method == "POST":
        db.session.add(Post(content=request.form["content"]))
        db.session.commit()
        flash("Post submitted for review.")
        return redirect(url_for('submit_form'))
    return render_template('submit.html', title="Submit")

if __name__ == "__main__":
    app.run(debug=True)