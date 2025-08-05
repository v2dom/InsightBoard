from extensions import db
from datetime import datetime, timezone

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(50), default='user')
    failed_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f'<User {self.name}>'


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    category = db.Column(db.String(50))
    status = db.Column(db.String(20))
    created_at = db.Column(db.DateTime)
    approved_at = db.Column(db.DateTime, nullable=True)
    declined_at = db.Column(db.DateTime, nullable=True)
    submitted_at = db.Column(db.DateTime)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    review_msg = db.Column(db.String(200))
    
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)

    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='posts')
    
    # Track reports
    report_count = db.Column(db.Integer, default=0)
    reports = db.relationship('PostReport', backref='post', lazy='dynamic', cascade='all, delete-orphan')


class PostReport(db.Model):
    __tablename__ = 'post_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)
    reported_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reason = db.Column(db.String(200), nullable=False)
    reported_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Ensure one user can only report a post once
    __table_args__ = (db.UniqueConstraint('post_id', 'reported_by', name='unique_user_post_report'),)



