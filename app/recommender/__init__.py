# Recommendation engine (Phase 4) lives here.
# content_based.py -> TF-IDF + cosine similarity on skills/description
# collaborative.py -> KNN over the student-job interaction matrix
# hybrid.py        -> combines both into a ranked recommendation list
#
# Wired into student.dashboard() via hybrid.get_recommendations().
