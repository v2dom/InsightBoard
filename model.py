from extensions import db  # Import db from extensions.py

# You need a python class for each table in the database.
# You can hand chatgpt your ddl and ask it to generate python classes
# for each table in the database.

# EXAMPLE: User model representing the 'user' table in the database.
# Compare to your output from chatgpt
class User(db.Model):
    __tablename__ = 'user'  # Specifies the table name

    # Define the columns for the 'user' table
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Primary key
    email = db.Column(db.String(120), unique=True, nullable=False)  # Email field, unique and required
    name = db.Column(db.String(120), nullable=False)  # Name field, required
    password = db.Column(db.String(128), nullable=False)  # Password field, required (hashed)
    role = db.Column(db.String(50), default='user')  # 'user' or 'admin'
    failed_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime, nullable=True) # For account lockout feature

    # String representation of the User object for debugging
    def __repr__(self):
        return f'<User {self.name}>'
    


