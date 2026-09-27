# Internship & Recruitment Portal

A Flask + MySQL web app matching students to internships/jobs, with (planned)
hybrid recommendation and resume-parsing components.

## Status

**Phase 1 (Database) and Phase 2/3 (Backend + Frontend skeleton) are done.**
This gets you: registration/login for students, employers, and admin;
student profile + CV upload (parsing not wired in yet); job posting and
browsing; applying; application status tracking; basic admin analytics
and moderation.

**Not yet built:** Phase 4 (recommendation engine), Phase 5 (resume
parsing with NLTK), Phase 6 (tests). `app/recommender/` is scaffolded
but empty — student dashboards currently show the 5 most recent open
jobs instead of a personalized ranking.

## Setup (SQLite — default, no database install needed)

1. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv venv
   source venv/bin/activate      # Windows: venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and set a real `SECRET_KEY`. Leave `DATABASE_URL`
   commented out — the app defaults to a local SQLite file
   (`internship_portal.db`), created automatically.

3. **Create the database tables and seed an admin account**
   ```bash
   python init_db.py
   ```
   This creates `internship_portal.db` and an admin login:
   username `admin`, password `changeme123`. **Change that password**
   after your first login — there's no UI for it yet, so for now it
   means updating the `password_hash` column directly, or just use a
   registered student/employer account to try the app out.

4. **Run the app**
   ```bash
   python run.py
   ```
   Visit `http://localhost:5000`.

## Hosting on Render

This repository includes `render.yaml` for a Render web service and a
PostgreSQL database.

1. Push the `internship_portal` folder to a GitHub repository.
2. In Render, choose **New > Blueprint**, connect the repository, and deploy
   the blueprint. Render will install dependencies, create the database, and
   start the app with Gunicorn.
3. Open the web service's **Environment** page and copy the generated
   `ADMIN_PASSWORD` value. Use username `admin` to sign in.
4. Set `MAIL_USERNAME` and `MAIL_PASSWORD` in Render if email verification is
   enabled for your deployment.

The Render free database is persistent, but the local `uploads/` directory is
not. Uploaded CVs can disappear when the service is redeployed, so use an
object-storage service for production file persistence.

## Switching to MySQL later

The schema is also available as raw SQL in `database/schema.sql` for
when you're ready to move off SQLite (e.g. for deployment). To switch:
1. Install MySQL Server and run `mysql -u root -p < database/schema.sql`.
2. In `.env`, uncomment and fill in `DATABASE_URL=mysql+pymysql://...`.
3. Delete `internship_portal.db` (or just start fresh) and remove/skip
   `init_db.py`'s `db.create_all()` step, since the schema is already
   in MySQL — you'll still want to seed an admin user via the app or
   a quick script.

## Project structure

```
internship_portal/
├── app/
│   ├── models/          SQLAlchemy models (users, students, employers, jobs, applications, messages, job_interactions)
│   ├── routes/          Blueprints: auth, student, employer, admin
│   ├── recommender/     Phase 4 — hybrid recommendation engine (not yet implemented)
│   ├── templates/        Jinja2 + Bootstrap templates
│   ├── static/           CSS/JS
│   └── extensions.py     db, login_manager, bcrypt instances
├── database/
│   └── schema.sql        Full MySQL schema
├── uploads/               CV uploads land here
├── config.py
├── requirements.txt
└── run.py
```

## Next steps (suggested order)

1. **Phase 4 — Recommendation engine**: build `content_based.py`
   (TF-IDF over student skills vs. job required_skills, cosine
   similarity), `collaborative.py` (KNN over the `job_interactions`
   table), and `hybrid.py` to blend them; wire the result into
   `student.dashboard()`.
2. **Phase 5 — Resume parsing**: extract text from uploaded PDFs/DOCX
   (PyPDF2 / python-docx), tokenize with NLTK, and auto-populate
   `Student.skills` on upload.
3. **Phase 6 — Testing**: unit tests for routes and the recommender,
   plus a manual UAT pass through the full student and employer
   journeys.
