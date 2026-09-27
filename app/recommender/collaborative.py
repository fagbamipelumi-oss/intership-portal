"""
Collaborative filtering: finds students with similar interaction patterns
(viewed/saved/applied jobs) using K-Nearest Neighbors, then recommends jobs
that those similar students engaged with.

Returns an empty result for students with too little interaction history
to find meaningful neighbors — this "cold start" case is handled by the
hybrid module falling back to content-based scoring only.
"""

import numpy as np
from sklearn.neighbors import NearestNeighbors

from app.models import JobInteraction

INTERACTION_WEIGHTS = {"viewed": 1.0, "saved": 2.0, "applied": 3.0}


def _build_interaction_matrix():
    """
    Builds a dense student-job interaction matrix from JobInteraction
    records. Returns (matrix, student_ids, job_ids) where matrix[i][j] is
    the interaction weight between student_ids[i] and job_ids[j].
    """
    interactions = JobInteraction.query.all()
    if not interactions:
        return None, [], []

    student_ids = sorted({i.student_id for i in interactions})
    job_ids = sorted({i.job_id for i in interactions})
    student_index = {sid: idx for idx, sid in enumerate(student_ids)}
    job_index = {jid: idx for idx, jid in enumerate(job_ids)}

    matrix = np.zeros((len(student_ids), len(job_ids)))
    for i in interactions:
        weight = INTERACTION_WEIGHTS.get(i.interaction, 1.0)
        row, col = student_index[i.student_id], job_index[i.job_id]
        matrix[row, col] = max(matrix[row, col], weight)  # keep the strongest signal

    return matrix, student_ids, job_ids


def collaborative_scores(student_id, k=5):
    """
    Returns {job_id: score in [0, 1]} based on what similar students have
    engaged with. Returns {} if there isn't enough interaction data yet.
    """
    matrix, student_ids, job_ids = _build_interaction_matrix()
    if matrix is None or student_id not in student_ids:
        return {}

    n_students = len(student_ids)
    if n_students < 2:
        return {}

    n_neighbors = min(k + 1, n_students)  # +1: the student is their own nearest neighbor
    model = NearestNeighbors(metric="cosine", algorithm="brute", n_neighbors=n_neighbors)
    model.fit(matrix)

    target_row = student_ids.index(student_id)
    distances, indices = model.kneighbors(matrix[target_row : target_row + 1])

    scores = {}
    for dist, idx in zip(distances[0], indices[0]):
        neighbor_id = student_ids[idx]
        if neighbor_id == student_id:
            continue
        similarity = 1.0 - dist
        if similarity <= 0:
            continue
        for job_idx, weight in enumerate(matrix[idx]):
            if weight > 0:
                job_id = job_ids[job_idx]
                scores[job_id] = scores.get(job_id, 0.0) + similarity * weight

    if not scores:
        return {}

    max_score = max(scores.values())
    return {job_id: score / max_score for job_id, score in scores.items()}
