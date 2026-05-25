"""
Confidence Scorer — Computes a composite confidence score for RAG responses
based on retrieval similarity, query-context coverage, and source diversity.
"""

import re
from typing import List, Tuple

import config


def compute_confidence(
    query: str,
    retrieved_results: List[Tuple[str, dict, float]],
    strategy: str = "hybrid",
) -> dict:
    """
    Compute a composite confidence score for a RAG response.

    The score is a weighted combination of:
    1. Retrieval similarity (avg cosine similarity of top-K chunks)
    2. Context coverage (fraction of query terms found in retrieved context)
    3. Source diversity (bonus for multi-document answers)

    Args:
        query: The user's original question.
        retrieved_results: List of (text, metadata, similarity_score) tuples.
        strategy: The search strategy used ('hybrid', 'semantic', 'keyword').

    Returns:
        Dict with keys: 'score' (0-100), 'label', 'icon', 'breakdown'
    """
    if not retrieved_results:
        return {
            "score": 0,
            "label": "No Data",
            "icon": "🔴",
            "breakdown": {
                "retrieval_similarity": 0.0,
                "context_coverage": 0.0,
                "source_diversity": 0.0,
            },
        }

    # ── 1. Retrieval Similarity ──────────────────────────────────────────
    similarities = [score for _, _, score in retrieved_results]
    avg_similarity = sum(similarities) / len(similarities) if similarities else 0
    
    if strategy == "hybrid":
        # Normalize: RRF max score per query is ~0.0327 (1/61 + 1/61). We normalize it to 100.
        retrieval_score = min((avg_similarity / 0.033) * 100, 100.0)
    elif strategy == "semantic":
        # FAISS inner product (cosine) usually falls in 0.0 - 1.0
        retrieval_score = min(avg_similarity * 100, 100.0)
    elif strategy == "keyword":
        # BM25 scores can be large depending on length, 15 is a typical good match threshold
        retrieval_score = min((avg_similarity / 15.0) * 100, 100.0)
    else:
        retrieval_score = min((avg_similarity / 0.033) * 100, 100.0)

    # ── 2. Context Coverage ──────────────────────────────────────────────
    # Tokenize query into meaningful terms (remove stopwords-like short terms)
    query_terms = set(
        word.lower()
        for word in re.findall(r'\b\w+\b', query)
        if len(word) > 2  # Skip very short words
    )

    if query_terms:
        combined_context = " ".join(text.lower() for text, _, _ in retrieved_results)
        matched_terms = sum(1 for term in query_terms if term in combined_context)
        coverage_score = (matched_terms / len(query_terms)) * 100
    else:
        coverage_score = 50.0  # Neutral if query is very short

    # ── 3. Source Diversity ──────────────────────────────────────────────
    unique_sources = set(meta.get("source_file", "") for _, meta, _ in retrieved_results)
    num_sources = len(unique_sources)
    # 1 source = 40%, 2 sources = 70%, 3+ sources = 100%
    diversity_map = {1: 40.0, 2: 70.0}
    diversity_score = diversity_map.get(num_sources, 100.0)

    # ── Composite Score ──────────────────────────────────────────────────
    weights = config.CONFIDENCE_WEIGHTS
    composite = (
        weights["retrieval_similarity"] * retrieval_score
        + weights["context_coverage"] * coverage_score
        + weights["source_diversity"] * diversity_score
    )
    composite = round(min(composite, 100.0), 1)

    # ── Label ────────────────────────────────────────────────────────────
    label, icon = "Low", "🔴"
    for (low, high), (lbl, icn) in config.CONFIDENCE_LABELS.items():
        if low <= composite < high:
            label, icon = lbl, icn
            break

    return {
        "score": composite,
        "label": label,
        "icon": icon,
        "breakdown": {
            "retrieval_similarity": round(retrieval_score, 1),
            "context_coverage": round(coverage_score, 1),
            "source_diversity": round(diversity_score, 1),
        },
    }
