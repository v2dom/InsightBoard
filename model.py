from extensions import db
from datetime import datetime

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
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='posts')


