import re
from typing import List, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from backend.app.domain.models.incident import Incident


class DuplicateIncidentDetector:
    """
    Intelligent Duplicate Incident Detection using a composite scoring mechanism:
    - TF-IDF Cosine Similarity (Semantic & Term weighting)
    - Jaccard Token Overlap
    - Domain Service Context Boost
    """
    def __init__(self, similarity_threshold: float = 0.35):
        self.similarity_threshold = similarity_threshold

    def find_potential_duplicates(
        self,
        target_incident: Incident,
        candidate_incidents: List[Incident]
    ) -> List[Tuple[Incident, float]]:
        """
        Returns a list of (Incident, similarity_score) sorted descending by similarity,
        where composite similarity exceeds the threshold.
        """
        # Exclude same incident and already verified/closed incidents
        pool = [
            inc for inc in candidate_incidents
            if inc.id != target_incident.id and inc.status.value not in ("CLOSED", "VERIFIED")
        ]
        if not pool:
            return []

        target_text = f"{target_incident.title} {target_incident.description}"
        pool_texts = [f"{inc.title} {inc.description}" for inc in pool]
        all_texts = [target_text] + pool_texts

        vectorizer = TfidfVectorizer(stop_words='english')
        try:
            tfidf_matrix = vectorizer.fit_transform(all_texts)
            sim_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
        except ValueError:
            sim_scores = [0.0] * len(pool)

        target_tokens = set(re.findall(r'\b\w{3,}\b', target_text.lower()))

        matches = []
        for inc, cosine_score in zip(pool, sim_scores):
            inc_tokens = set(re.findall(r'\b\w{3,}\b', f"{inc.title} {inc.description}".lower()))
            jaccard = (
                len(target_tokens & inc_tokens) / len(target_tokens | inc_tokens)
                if (target_tokens | inc_tokens) else 0.0
            )

            # Composite: 60% TF-IDF Cosine + 40% Token Overlap
            composite = (0.60 * float(cosine_score)) + (0.40 * jaccard)

            # Boost if same service or same category
            if target_incident.service.id == inc.service.id:
                composite = min(1.0, composite * 1.30)
            if target_incident.category and inc.category and target_incident.category.lower() == inc.category.lower():
                composite = min(1.0, composite * 1.10)

            if composite >= self.similarity_threshold:
                matches.append((inc, round(composite, 3)))

        matches.sort(key=lambda x: x[1], reverse=True)
        return matches
