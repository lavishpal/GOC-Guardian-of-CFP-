"""Prompts for reviewer-friendly explanations."""

from typing import List
from src.models.corpus_manager import SimilarTalk


def generate_risk_explanation(risk_level: str) -> str:
    """
    Generate explanation for risk level.

    Args:
        risk_level: Risk level (low, medium, high)

    Returns:
        Human-readable explanation
    """
    explanations = {
        "low": "This CFP appears to be original with low risk of duplication or AI generation.",
        "medium": "This CFP shows some concerns that warrant review for originality and quality.",
        "high": "This CFP requires careful review due to multiple risk factors detected.",
    }
    return explanations.get(risk_level, "Risk level could not be determined.")


def generate_similarity_explanation(similar_talks: List[SimilarTalk]) -> str:
    """
    Generate explanation for similar talks.

    Args:
        similar_talks: List of similar talks

    Returns:
        Human-readable explanation
    """
    if not similar_talks:
        return "No similar historical talks found."

    top = similar_talks[0]
    explanation = f"Found {len(similar_talks)} similar talk(s). "
    explanation += f"Most similar: '{top.talk.title}' "
    explanation += f"(similarity: {top.similarity_score:.1%})"

    if top.paraphrase_likelihood > 0.7:
        explanation += f" High paraphrase likelihood ({top.paraphrase_likelihood:.1%})."

    return explanation


def generate_ai_explanation(ai_probability: float) -> str:
    """
    Generate explanation for AI generation probability.

    Args:
        ai_probability: AI generation probability (0.0 to 1.0)

    Returns:
        Human-readable explanation
    """
    if ai_probability > 0.7:
        return f"High AI generation probability ({ai_probability:.1%}). Verify content quality."
    elif ai_probability > 0.5:
        return f"Moderate AI generation probability ({ai_probability:.1%}). Review for quality."
    else:
        return f"Low AI generation probability ({ai_probability:.1%})."


def generate_originality_explanation(originality_score: float) -> str:
    """
    Generate explanation for originality score.

    Args:
        originality_score: Originality score (0.0 to 1.0)

    Returns:
        Human-readable explanation
    """
    if originality_score < 0.4:
        return f"Low originality score ({originality_score:.1%}). Review for copied content."
    elif originality_score < 0.7:
        return f"Moderate originality score ({originality_score:.1%}). Check for near-duplicates."
    else:
        return f"High originality score ({originality_score:.1%}). Content appears original."


def generate_recommendation_summary(recommendations: List[str]) -> str:
    """
    Generate summary of recommendations.

    Args:
        recommendations: List of recommendations

    Returns:
        Formatted recommendation summary
    """
    if not recommendations:
        return "No specific recommendations."

    return "\n".join(f"• {rec}" for rec in recommendations)

