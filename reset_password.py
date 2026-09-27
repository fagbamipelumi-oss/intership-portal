"""
Reset a user's password directly — for local development use only.

Usage:
    python reset_password.py <username_or_email> <new_password>

Example:
    python reset_password.py acme_corp NewPassword123
"""

import sys
from app import create_app
from app.extensions import db, bcrypt
from app.models import User

if len(sys.argv) != 3:
    print("Usage: python reset_password.py <username_or_email> <new_password>")
    sys.exit(1)

identifier = sys.argv[1].strip().lower()
new_password = sys.argv[2]

if len(new_password) < 8:
    print("Password must be at least 8 characters.")
    sys.exit(1)

app = create_app()

with app.app_context():
    user = User.query.filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()

    if not user:
        print(f"No user found matching '{identifier}'.")
        sys.exit(1)

    user.password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
    db.session.commit()
    print(f"Password reset for {user.username} ({user.role}). New password: {new_password}")
