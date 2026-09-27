import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import Student, Job, Application, JobInteraction
from app.recommender.hybrid import get_recommendations
from app.utils import role_required, allowed_cv_file

student_bp = Blueprint("student", __name__, url_prefix="/student")


@student_bp.route("/dashboard")
@login_required
@role_required("student")
def dashboard():
    student = current_user.student
    my_applications = Application.query.filter_by(student_id=student.id).all()

    if not student.cv_file_path:
        return render_template(
            "student/dashboard.html",
            student=student,
            recommended_jobs=[],
            applications=my_applications,
            cv_required=True,
        )

    already_applied = {a.job_id for a in student.applications}
    ranked = get_recommendations(student, top_n=5, exclude_job_ids=already_applied)
    recommended_jobs = [(job, round(score * 100)) for job, score in ranked]
    return render_template(
        "student/dashboard.html",
        student=student,
        recommended_jobs=recommended_jobs,
        applications=my_applications,
        cv_required=False,
    )


@student_bp.route("/profile", methods=["GET", "POST"])
@login_required
@role_required("student")
def profile():
    student = current_user.student
    if request.method == "POST":
        student.first_name = request.form.get("first_name", student.first_name)
        student.last_name = request.form.get("last_name", student.last_name)
        student.course = request.form.get("course", student.course)
        cgpa = request.form.get("cgpa")
        student.cgpa = float(cgpa) if cgpa else student.cgpa
        student.qualifications = request.form.get("qualifications", student.qualifications)
        student.experience = request.form.get("experience", student.experience)
        student.interests = request.form.get("interests", student.interests)
        student.bio = request.form.get("bio", student.bio)
        skills_raw = request.form.get("skills", "")
        student.skills = [s.strip() for s in skills_raw.split(",") if s.strip()]

        cv_file = request.files.get("cv")
        if cv_file and cv_file.filename:
            if allowed_cv_file(cv_file.filename, current_app.config["ALLOWED_CV_EXTENSIONS"]):
                filename = secure_filename(f"student_{student.id}_{cv_file.filename}")
                path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                cv_file.save(path)
                student.cv_file_path = path
                # TODO Phase 5: trigger resume parsing here to auto-populate skills/education
            else:
                flash("CV must be a PDF or DOCX file.", "danger")

        db.session.commit()
        flash("Profile updated.", "success")
        return redirect(url_for("student.profile"))

    return render_template("student/profile.html", student=student)


@student_bp.route("/jobs")
@login_required
@role_required("student")
def browse_jobs():
    student = current_user.student
    if not student.cv_file_path:
        flash("Upload your CV on your profile before browsing jobs.", "warning")
        return redirect(url_for("student.profile"))

    query = Job.query.filter_by(status="open")
    keyword = request.args.get("q")
    location = request.args.get("location")
    job_type = request.args.get("job_type")

    if keyword:
        query = query.filter(Job.title.ilike(f"%{keyword}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    if job_type:
        query = query.filter_by(job_type=job_type)

    jobs = query.order_by(Job.posted_at.desc()).all()
    return render_template("student/browse_jobs.html", jobs=jobs)


@student_bp.route("/jobs/<int:job_id>", methods=["GET", "POST"])
@login_required
@role_required("student")
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    student = current_user.student

    if not student.cv_file_path:
        flash("Upload your CV on your profile before viewing or applying to jobs.", "warning")
        return redirect(url_for("student.profile"))

    # Log a "viewed" interaction for the collaborative-filtering signal
    db.session.add(JobInteraction(student_id=student.id, job_id=job.id, interaction="viewed"))
    db.session.commit()

    if request.method == "POST":
        existing = Application.query.filter_by(student_id=student.id, job_id=job.id).first()
        if existing:
            flash("You've already applied to this job.", "warning")
        else:
            db.session.add(Application(student_id=student.id, job_id=job.id))
            db.session.add(JobInteraction(student_id=student.id, job_id=job.id, interaction="applied"))
            db.session.commit()
            flash("Application submitted!", "success")
        return redirect(url_for("student.job_detail", job_id=job.id))

    return render_template("student/job_detail.html", job=job)
