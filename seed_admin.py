from extensions import db
from model import User
from werkzeug.security import generate_password_hash, check_password_hash
from app import create_app

app = create_app()

with app.app_context():
    admin_email = "admin1@example.com"
    plain_password = "abc"
    hashed_password = generate_password_hash(plain_password, method='pbkdf2:sha256')

    print("📌 Generated hash:", hashed_password)
    print("📌 Password matches hash?", check_password_hash(hashed_password, plain_password))

    user = User.query.filter_by(email=admin_email).first()

    if user:
        print("⚠️ Admin already exists. Updating password...")
        user.password = hashed_password
        user.name = "Admin"
        user.role = "admin"
    else:
        user = User(
            email=admin_email,
            name="Admin",
            password=hashed_password,
            role="admin"
        )
        db.session.add(user)

    db.session.commit()

    # Pull fresh from DB and test again
    fresh_user = User.query.filter_by(email=admin_email).first()
    print("✅ Pulled from DB:", fresh_user.email)
    print("🔍 Stored hash in DB:", fresh_user.password)
    print("🔐 Password check (should be True):", check_password_hash(fresh_user.password, plain_password))
