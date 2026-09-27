"""
Hybrid recommendation engine combining content-based filtering (TF-IDF +
cosine similarity on skills/description) with collaborative filtering
(KNN over the student-job interaction matrix).

For students with no interaction history yet (the "cold start" problem —
every student starts here), collaborative scoring returns nothing, so the
hybrid falls back to pure content-based recommendations instead of letting
the missing signal drag every score down.
"""

from app.models import Job
from app.recommender.content_based import content_based_scores
from app.recommender.collaborative import collaborative_scores

CONTENT_WEIGHT = 0.6
COLLABORATIVE_WEIGHT = 0.4


def get_recommendations(student, top_n=10, exclude_job_ids=None):
    """
    Returns a ranked list of (Job, score) tuples for the given Student,
    highest score first, limited to open jobs.
    """
    exclude_job_ids = exclude_job_ids or set()
    open_jobs = [j for j in Job.query.filter_by(status="open").all() if j.id not in exclude_job_ids]
    if not open_jobs:
        return []

    content_scores = content_based_scores(student, open_jobs)
    collab_scores = collaborative_scores(student.id)

    has_collab_signal = bool(collab_scores)
    content_weight = CONTENT_WEIGHT if has_collab_signal else 1.0
    collab_weight = COLLABORATIVE_WEIGHT if has_collab_signal else 0.0

    ranked = []
    for job in open_jobs:
        c_score = content_scores.get(job.id, 0.0)
        k_score = collab_scores.get(job.id, 0.0)
        final_score = (c_score * content_weight) + (k_score * collab_weight)
        ranked.append((job, final_score))

    ranked.sort(key=lambda pair: pair[1], reverse=True)
    return ranked[:top_n]
