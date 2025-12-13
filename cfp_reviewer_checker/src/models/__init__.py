"""Models package for CFP Reviewer Checker."""

from .corpus_manager import (
    CorpusManager,
    HistoricalTalk,
    NormalizedTalk,
    CFPSubmission,
    SimilarTalk,
)
from .reviewer_report import ReviewerReport, SimilarTalkEntry

__all__ = [
    "CorpusManager",
    "HistoricalTalk",
    "NormalizedTalk",
    "CFPSubmission",
    "SimilarTalk",
    "ReviewerReport",
    "SimilarTalkEntry",
]

