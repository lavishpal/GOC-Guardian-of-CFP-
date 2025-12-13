"""Conference detector for identifying conferences from CFP submissions."""

from typing import List, Optional
from src.models.corpus_manager import CFPSubmission


class ConferenceDetector:
    """Detects relevant conferences from CFP submissions."""

    def __init__(self):
        """Initialize conference detector."""
        # Common conference keywords
        self.conference_keywords = [
            "conference",
            "symposium",
            "workshop",
            "summit",
            "meetup",
            "forum",
        ]

    def detect_conferences(self, cfp: CFPSubmission) -> List[str]:
        """
        Detect potential conferences from CFP submission.

        Args:
            cfp: CFP submission to analyze

        Returns:
            List of potential conference names or identifiers
        """
        conferences = []
        full_text = cfp.get_full_text().lower()

        # Extract conference mentions
        # This is a simple heuristic - in production, use NLP or named entity recognition
        for keyword in self.conference_keywords:
            if keyword in full_text:
                # Try to extract conference name around the keyword
                # This is a placeholder - real implementation would use more sophisticated extraction
                conferences.append(f"detected_{keyword}")

        return conferences

    def extract_conference_info(self, cfp: CFPSubmission) -> dict:
        """
        Extract conference information from CFP.

        Args:
            cfp: CFP submission

        Returns:
            Dictionary with conference information
        """
        return {
            "potential_conferences": self.detect_conferences(cfp),
            "has_conference_mention": len(self.detect_conferences(cfp)) > 0,
        }

