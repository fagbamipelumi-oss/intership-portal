from datetime import datetime
from flask_login import UserMixin
from app.extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum("student", "employer", "admin", name="user_role"), nullable=False)
    is_active_flag = db.Column("is_active", db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship("Student", backref="user", uselist=False, cascade="all, delete-orphan")
    employer = db.relationship("Employer", backref="user", uselist=False, cascade="all, delete-orphan")

    # Flask-Login uses .is_active; map it to our column without clashing
    @property
    def is_active(self):
        return self.is_active_flag


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    course = db.Column(db.String(120))
    cgpa = db.Column(db.Numeric(3, 2))
    skills = db.Column(db.JSON, default=list)  # e.g. ["Python", "SQL"]
    qualifications = db.Column(db.Text)  # certifications, degrees, achievements
    experience = db.Column(db.Text)  # prior work/internship experience
    interests = db.Column(db.Text)  # career interests, e.g. "Web Development"
    bio = db.Column(db.Text)
    cv_file_path = db.Column(db.String(255))
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    applications = db.relationship("Application", backref="student", cascade="all, delete-orphan")


class Employer(db.Model):
    __tablename__ = "employers"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    company_name = db.Column(db.String(150), nullable=False)
    industry = db.Column(db.String(100))
    location = db.Column(db.String(150))
    description = db.Column(db.Text)

    jobs = db.relationship("Job", backref="employer", cascade="all, delete-orphan")


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey("employers.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.JSON, default=list)
    qualifications = db.Column(db.Text)
    location = db.Column(db.String(150))
    job_type = db.Column(db.Enum("internship", "full-time", "part-time", name="job_type"), default="internship")
    min_cgpa = db.Column(db.Numeric(3, 2), default=0)
    status = db.Column(db.Enum("open", "closed", "flagged", name="job_status"), default="open")
    deadline = db.Column(db.Date)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship("Application", backref="job", cascade="all, delete-orphan")


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    status = db.Column(
        db.Enum("pending", "reviewed", "shortlisted", "rejected", name="application_status"),
        default="pending",
    )
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint("student_id", "job_id", name="unique_application"),)


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    subject = db.Column(db.String(150))
    message_body = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)


class JobInteraction(db.Model):
    """Implicit signal table (viewed/applied/saved) used by the
    collaborative-filtering half of the recommender (Phase 4)."""

    __tablename__ = "job_interactions"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    interaction = db.Column(db.Enum("viewed", "applied", "saved", name="interaction_type"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
