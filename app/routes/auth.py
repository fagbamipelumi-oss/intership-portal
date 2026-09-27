from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db, bcrypt
from app.models import User, Student, Employer
from app.validators import validate_registration_fields

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register/student", methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        errors = validate_registration_fields(
            request.form, ["username", "email", "password", "first_name", "last_name"]
        )
        if errors:
            for error in errors:
                flash(error, "danger")
            return redirect(url_for("auth.register_student"))

        username = request.form["username"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        first_name = request.form["first_name"].strip()
        last_name = request.form["last_name"].strip()

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already registered.", "danger")
            return redirect(url_for("auth.register_student"))

        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(username=username, email=email, password_hash=pw_hash, role="student")
        db.session.add(user)
        db.session.flush()  # get user.id before commit

        student = Student(user_id=user.id, first_name=first_name, last_name=last_name, skills=[])
        db.session.add(student)
        db.session.commit()

        flash("Account created. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register_student.html")


@auth_bp.route("/register/employer", methods=["GET", "POST"])
def register_employer():
    if request.method == "POST":
        errors = validate_registration_fields(
            request.form, ["username", "email", "password", "company_name"]
        )
        if errors:
            for error in errors:
                flash(error, "danger")
            return redirect(url_for("auth.register_employer"))

        username = request.form["username"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        company_name = request.form["company_name"].strip()

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already registered.", "danger")
            return redirect(url_for("auth.register_employer"))

        pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(username=username, email=email, password_hash=pw_hash, role="employer")
        db.session.add(user)
        db.session.flush()

        employer = Employer(user_id=user.id, company_name=company_name)
        db.session.add(employer)
        db.session.commit()

        flash("Account created. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register_employer.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form["identifier"].strip().lower()
        password = request.form["password"]

        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            if user.role == "student":
                return redirect(url_for("student.dashboard"))
            elif user.role == "employer":
                return redirect(url_for("employer.dashboard"))
            else:
                return redirect(url_for("admin.dashboard"))

        flash("Invalid username/email or password.", "danger")
        return redirect(url_for("auth.login"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You've been logged out.", "info")
    return redirect(url_for("auth.login"))
