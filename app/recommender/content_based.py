"""
Content-based filtering: matches a student's profile (skills, course, bio)
against open job postings (title, description, required skills,
qualifications) using TF-IDF vectorization and cosine similarity.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _student_document(student):
    """Flatten a student's profile into one text blob for vectorization."""
    parts = []
    if student.skills:
        # Repeat skills so they carry more weight than free-text prose
        parts.append((" ".join(student.skills) + " ") * 3)
    if student.course:
        parts.append(student.course)
    if getattr(student, "interests", None):
        parts.append((student.interests + " ") * 2)
    if getattr(student, "qualifications", None):
        parts.append(student.qualifications)
    if getattr(student, "experience", None):
        parts.append(student.experience)
    if student.bio:
        parts.append(student.bio)
    return " ".join(parts)


def _job_document(job):
    """Flatten a job posting into one text blob for vectorization."""
    parts = [job.title or "", job.description or ""]
    if job.required_skills:
        parts.append((" ".join(job.required_skills) + " ") * 3)
    if job.qualifications:
        parts.append(job.qualifications)
    return " ".join(p for p in parts if p)


def content_based_scores(student, jobs):
    """
    Returns {job_id: similarity_score in [0, 1]} for the given student
    against the given list of open Job objects.
    """
    if not jobs:
        return {}

    student_doc = _student_document(student)
    if not student_doc.strip():
        # Nothing in the student's profile to match on yet
        return {job.id: 0.0 for job in jobs}

    job_docs = [_job_document(job) for job in jobs]
    corpus = [student_doc] + job_docs

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf_matrix = vectorizer.fit_transform(corpus)
    except ValueError:
        # Empty vocabulary after stop-word removal — no usable signal
        return {job.id: 0.0 for job in jobs}

    student_vector = tfidf_matrix[0:1]
    job_vectors = tfidf_matrix[1:]
    similarities = cosine_similarity(student_vector, job_vectors)[0]

    return {job.id: float(score) for job, score in zip(jobs, similarities)}
