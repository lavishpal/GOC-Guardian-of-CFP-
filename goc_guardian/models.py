"""Data models for CFP Reviewer Checker."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict


class CFPSubmission(BaseModel):
    """Model for CFP submission with title, abstract, and description."""

    title: str = Field(..., min_length=10, description="CFP title")
    abstract: str = Field(..., min_length=50, description="CFP abstract")
    description: Optional[str] = Field(None, description="CFP description (optional)")

    def get_full_text(self) -> str:
        """Get combined text of all fields."""
        parts = [self.title, self.abstract]
        if self.description:
            parts.append(self.description)
        return " ".join(parts)


class HistoricalTalk(BaseModel):
    """Model for historical talk from conference platforms."""

    title: str
    abstract: Optional[str] = None
    description: Optional[str] = None
    speaker: Optional[str] = None
    conference: Optional[str] = None
    year: Optional[int] = None
    source: str  # "sched" or "sessionize"
    url: Optional[str] = None

    def get_full_text(self) -> str:
        """Get combined text of all fields."""
        parts = [self.title]
        if self.abstract:
            parts.append(self.abstract)
        if self.description:
            parts.append(self.description)
        return " ".join(parts)


class SimilarTalk(BaseModel):
    """Model for semantically similar talk with similarity score."""

    talk: HistoricalTalk
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Semantic similarity score")
    paraphrase_likelihood: float = Field(..., ge=0.0, le=1.0, description="Paraphrase likelihood")


class EvaluationMetrics(BaseModel):
    """Model for Oumi evaluation metrics."""

    semantic_similarity: Dict[str, float] = Field(default_factory=dict)
    paraphrase_likelihood: float = Field(..., ge=0.0, le=1.0)
    ai_generation_probability: float = Field(..., ge=0.0, le=1.0)
    originality_score: float = Field(..., ge=0.0, le=1.0)

