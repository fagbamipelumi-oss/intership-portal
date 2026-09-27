from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_file
from flask_login import login_required, current_user
import os

from app.extensions import db
from app.models import Job, Application, Student
from app.utils import role_required

employer_bp = Blueprint("employer", __name__, url_prefix="/employer")


@employer_bp.route("/dashboard")
@login_required
@role_required("employer")
def dashboard():
    employer = current_user.employer
    jobs = Job.query.filter_by(employer_id=employer.id).order_by(Job.posted_at.desc()).all()
    return render_template("employer/dashboard.html", employer=employer, jobs=jobs)


@employer_bp.route("/profile", methods=["GET", "POST"])
@login_required
@role_required("employer")
def profile():
    employer = current_user.employer
    if request.method == "POST":
        employer.company_name = request.form.get("company_name", employer.company_name).strip()
        employer.industry = request.form.get("industry", "").strip()
        employer.location = request.form.get("location", "").strip()
        employer.description = request.form.get("description", "").strip()
        db.session.commit()
        flash("Company profile updated.", "success")
        return redirect(url_for("employer.profile"))

    return render_template("employer/profile.html", employer=employer)


@employer_bp.route("/jobs/new", methods=["GET", "POST"])
@login_required
@role_required("employer")
def post_job():
    if request.method == "POST":
        skills_raw = request.form.get("required_skills", "")
        job = Job(
            employer_id=current_user.employer.id,
            title=request.form["title"].strip(),
            description=request.form["description"].strip(),
            required_skills=[s.strip() for s in skills_raw.split(",") if s.strip()],
            qualifications=request.form.get("qualifications", "").strip(),
            location=request.form.get("location", "").strip(),
            job_type=request.form.get("job_type", "internship"),
            min_cgpa=float(request.form.get("min_cgpa") or 0),
            deadline=request.form.get("deadline") or None,
        )
        db.session.add(job)
        db.session.commit()
        flash("Job posted.", "success")
        return redirect(url_for("employer.dashboard"))

    return render_template("employer/post_job.html")


@employer_bp.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("employer")
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.employer_id != current_user.employer.id:
        flash("Not authorized to edit this job.", "danger")
        return redirect(url_for("employer.dashboard"))

    if request.method == "POST":
        skills_raw = request.form.get("required_skills", "")
        job.title = request.form["title"].strip()
        job.description = request.form["description"].strip()
        job.required_skills = [s.strip() for s in skills_raw.split(",") if s.strip()]
        job.qualifications = request.form.get("qualifications", "").strip()
        job.location = request.form.get("location", "").strip()
        job.job_type = request.form.get("job_type", "internship")
        job.min_cgpa = float(request.form.get("min_cgpa") or 0)
        job.deadline = request.form.get("deadline") or None
        db.session.commit()
        flash("Job updated.", "success")
        return redirect(url_for("employer.dashboard"))

    return render_template("employer/post_job.html", job=job)


@employer_bp.route("/jobs/<int:job_id>/delete", methods=["POST"])
@login_required
@role_required("employer")
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    if job.employer_id != current_user.employer.id:
        flash("Not authorized to delete this job.", "danger")
        return redirect(url_for("employer.dashboard"))

    db.session.delete(job)
    db.session.commit()
    flash("Job deleted.", "success")
    return redirect(url_for("employer.dashboard"))


@employer_bp.route("/jobs/<int:job_id>/applicants")
@login_required
@role_required("employer")
def applicants(job_id):
    job = Job.query.get_or_404(job_id)
    if job.employer_id != current_user.employer.id:
        flash("Not authorized to view this job's applicants.", "danger")
        return redirect(url_for("employer.dashboard"))

    apps = Application.query.filter_by(job_id=job.id).all()
    return render_template("employer/applicants.html", job=job, applications=apps)


@employer_bp.route("/applications/<int:application_id>/status", methods=["POST"])
@login_required
@role_required("employer")
def update_application_status(application_id):
    application = Application.query.get_or_404(application_id)
    if application.job.employer_id != current_user.employer.id:
        flash("Not authorized.", "danger")
        return redirect(url_for("employer.dashboard"))

    new_status = request.form.get("status")
    if new_status in ("pending", "reviewed", "shortlisted", "rejected"):
        application.status = new_status
        db.session.commit()
        flash("Application status updated.", "success")

    return redirect(url_for("employer.applicants", job_id=application.job_id))


@employer_bp.route("/students/<int:student_id>/cv")
@login_required
@role_required("employer")
def download_cv(student_id):
    student = Student.query.get_or_404(student_id)

    # Only allow the download if this student actually applied to one of
    # this employer's jobs — an employer has no business seeing a CV
    # otherwise.
    applied_to_this_employer = (
        Application.query.join(Job)
        .filter(Application.student_id == student_id, Job.employer_id == current_user.employer.id)
        .first()
    )
    if not applied_to_this_employer:
        flash("Not authorized to view this candidate's CV.", "danger")
        return redirect(url_for("employer.dashboard"))

    if not student.cv_file_path or not os.path.exists(student.cv_file_path):
        flash("This student hasn't uploaded a CV.", "warning")
        return redirect(request.referrer or url_for("employer.dashboard"))

    return send_file(student.cv_file_path, as_attachment=True)
