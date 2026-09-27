from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app.extensions import db
from app.models import User, Job, Application, Employer
from app.utils import role_required

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    stats = {
        "total_users": User.query.count(),
        "total_students": User.query.filter_by(role="student").count(),
        "total_employers": User.query.filter_by(role="employer").count(),
        "total_jobs": Job.query.count(),
        "total_applications": Application.query.count(),
        "shortlisted": Application.query.filter_by(status="shortlisted").count(),
    }
    return render_template("admin/dashboard.html", stats=stats)


@admin_bp.route("/users")
@login_required
@role_required("admin")
def manage_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/users.html", users=users)


@admin_bp.route("/users/<int:user_id>/toggle-active", methods=["POST"])
@login_required
@role_required("admin")
def toggle_user_active(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You can't deactivate your own account.", "danger")
        return redirect(url_for("admin.manage_users"))

    user.is_active_flag = not user.is_active_flag
    db.session.commit()
    flash(f"{user.username} is now {'active' if user.is_active_flag else 'inactive'}.", "success")
    return redirect(url_for("admin.manage_users"))


@admin_bp.route("/employers")
@login_required
@role_required("admin")
def manage_employers():
    employers = Employer.query.join(User).order_by(User.created_at.desc()).all()
    return render_template("admin/employers.html", employers=employers)


@admin_bp.route("/jobs")
@login_required
@role_required("admin")
def moderate_jobs():
    jobs = Job.query.order_by(Job.posted_at.desc()).all()
    return render_template("admin/jobs.html", jobs=jobs)


@admin_bp.route("/jobs/<int:job_id>/flag", methods=["POST"])
@login_required
@role_required("admin")
def flag_job(job_id):
    job = Job.query.get_or_404(job_id)
    job.status = "flagged" if job.status != "flagged" else "open"
    db.session.commit()
    flash("Job status updated.", "success")
    return redirect(url_for("admin.moderate_jobs"))
