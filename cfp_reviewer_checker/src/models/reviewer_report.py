"""Reviewer Report model matching the standard structure."""

from pydantic import BaseModel, Field
from typing import List, Dict, Any
from src.models.corpus_manager import NormalizedTalk


class SimilarTalkEntry(BaseModel):
    """Entry for similar talk in reviewer report."""

    talk: NormalizedTalk
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    paraphrase_likelihood: float = Field(..., ge=0.0, le=1.0)


class ReviewerReport(BaseModel):
    """Reviewer report matching the standard structure."""

    semantic_similarity: float = Field(..., ge=0.0, le=1.0, description="Overall semantic similarity score")
    paraphrase_likelihood: float = Field(..., ge=0.0, le=1.0, description="Overall paraphrase likelihood")
    ai_generation_confidence: float = Field(..., ge=0.0, le=1.0, description="AI generation confidence")
    originality_score: float = Field(..., ge=0.0, le=1.0, description="Originality score")
    similar_talks: List[Dict[str, Any]] = Field(default_factory=list, description="List of similar talks")
    recommendation: str = Field(..., description="Reviewer recommendation")
    explanation: str = Field(..., description="Detailed explanation")

    @classmethod
    def from_analysis(
        cls,
        semantic_similarity: float,
        paraphrase_likelihood: float,
        ai_generation_confidence: float,
        originality_score: float,
        similar_talks: List[SimilarTalkEntry],
        recommendation: str,
        explanation: str,
    ) -> "ReviewerReport":
        """
        Create ReviewerReport from analysis results.

        Args:
            semantic_similarity: Overall semantic similarity score
            paraphrase_likelihood: Overall paraphrase likelihood
            ai_generation_confidence: AI generation confidence
            originality_score: Originality score
            similar_talks: List of similar talk entries
            recommendation: Reviewer recommendation
            explanation: Detailed explanation

        Returns:
            ReviewerReport instance
        """
        # Convert similar talks to dict format
        similar_talks_dict = [
            {
                "id": st.talk.id,
                "title": st.talk.title,
                "abstract": st.talk.abstract,
                "description": st.talk.description,
                "conference": st.talk.conference,
                "year": st.talk.year,
                "url": st.talk.url,
                "similarity_score": st.similarity_score,
                "paraphrase_likelihood": st.paraphrase_likelihood,
            }
            for st in similar_talks
        ]

        return cls(
            semantic_similarity=semantic_similarity,
            paraphrase_likelihood=paraphrase_likelihood,
            ai_generation_confidence=ai_generation_confidence,
            originality_score=originality_score,
            similar_talks=similar_talks_dict,
            recommendation=recommendation,
            explanation=explanation,
        )

