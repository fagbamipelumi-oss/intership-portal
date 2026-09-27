"""
Run this once to create the database tables and seed an admin account.

    python init_db.py

Safe to re-run: it won't duplicate tables or the admin user.
"""

import os

from app import create_app
from app.extensions import db, bcrypt
from app.models import User

app = create_app()

with app.app_context():
    db.create_all()
    print("Tables created (or already existed).")

    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            email="admin@internshipportal.local",
            password_hash=bcrypt.generate_password_hash(
                os.environ.get("ADMIN_PASSWORD", "changeme123")
            ).decode("utf-8"),
            role="admin",
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin account created — username: admin")
        print("The password is the ADMIN_PASSWORD environment variable.")
    else:
        print("Admin account already exists — skipping.")
