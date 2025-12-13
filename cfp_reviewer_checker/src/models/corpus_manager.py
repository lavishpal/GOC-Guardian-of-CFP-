"""Corpus manager for storing and managing historical talks and CFP submissions."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import json


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


class NormalizedTalk(BaseModel):
    """Normalized talk model matching the standard structure."""

    id: str
    title: str
    abstract: str
    description: str
    conference: str
    year: int
    url: str

    def get_full_text(self) -> str:
        """Get combined text of all fields."""
        return f"{self.title} {self.abstract} {self.description}".strip()


class HistoricalTalk(BaseModel):
    """Model for historical talk from conference platforms (internal use)."""

    id: Optional[str] = None
    title: str
    abstract: Optional[str] = None
    description: Optional[str] = None
    speaker: Optional[str] = None
    conference: Optional[str] = None
    year: Optional[int] = None
    source: str  # "sched", "sessionize", or other
    url: Optional[str] = None
    scraped_at: Optional[datetime] = None

    def get_full_text(self) -> str:
        """Get combined text of all fields."""
        parts = [self.title]
        if self.abstract:
            parts.append(self.abstract)
        if self.description:
            parts.append(self.description)
        return " ".join(parts)

    def to_normalized(self) -> NormalizedTalk:
        """Convert to normalized talk format."""
        import uuid
        return NormalizedTalk(
            id=self.id or str(uuid.uuid4()),
            title=self.title or "",
            abstract=self.abstract or "",
            description=self.description or "",
            conference=self.conference or "",
            year=self.year or 0,
            url=self.url or "",
        )

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "title": self.title,
            "abstract": self.abstract,
            "description": self.description,
            "speaker": self.speaker,
            "conference": self.conference,
            "year": self.year,
            "source": self.source,
            "url": self.url,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "HistoricalTalk":
        """Create from dictionary."""
        if data.get("scraped_at"):
            try:
                from dateutil.parser import parse
                data["scraped_at"] = parse(data["scraped_at"])
            except ImportError:
                # Fallback if dateutil not available
                from datetime import datetime
                data["scraped_at"] = datetime.fromisoformat(data["scraped_at"])
        return cls(**data)


class SimilarTalk(BaseModel):
    """Model for semantically similar talk with similarity score."""

    talk: HistoricalTalk
    similarity_score: float = Field(..., ge=0.0, le=1.0, description="Semantic similarity score")
    paraphrase_likelihood: float = Field(..., ge=0.0, le=1.0, description="Paraphrase likelihood")


class CorpusManager:
    """Manages the corpus of historical talks."""

    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize corpus manager.

        Args:
            storage_path: Optional path to JSON file for persistent storage
        """
        self.storage_path = storage_path
        self.talks: List[HistoricalTalk] = []
        self._load_from_storage()

    def add_talk(self, talk: HistoricalTalk) -> None:
        """
        Add a talk to the corpus.

        Args:
            talk: Historical talk to add
        """
        # Check for duplicates based on title and URL
        if not any(
            t.title.lower() == talk.title.lower() and t.url == talk.url
            for t in self.talks
        ):
            self.talks.append(talk)
            self._save_to_storage()

    def add_talks(self, talks: List[HistoricalTalk]) -> None:
        """
        Add multiple talks to the corpus.

        Args:
            talks: List of historical talks to add
        """
        for talk in talks:
            self.add_talk(talk)

    def get_all_talks(self) -> List[HistoricalTalk]:
        """
        Get all talks in the corpus.

        Returns:
            List of all historical talks
        """
        return self.talks.copy()

    def get_talks_by_conference(self, conference: str) -> List[HistoricalTalk]:
        """
        Get talks filtered by conference name.

        Args:
            conference: Conference name to filter by

        Returns:
            List of talks from the specified conference
        """
        return [talk for talk in self.talks if talk.conference and conference.lower() in talk.conference.lower()]

    def get_talks_by_source(self, source: str) -> List[HistoricalTalk]:
        """
        Get talks filtered by source.

        Args:
            source: Source to filter by (e.g., "sched", "sessionize")

        Returns:
            List of talks from the specified source
        """
        return [talk for talk in self.talks if talk.source == source]

    def search_talks(self, query: str) -> List[HistoricalTalk]:
        """
        Search talks by query string.

        Args:
            query: Search query

        Returns:
            List of matching talks
        """
        query_lower = query.lower()
        return [
            talk
            for talk in self.talks
            if query_lower in talk.title.lower()
            or (talk.abstract and query_lower in talk.abstract.lower())
            or (talk.description and query_lower in talk.description.lower())
        ]

    def get_corpus_size(self) -> int:
        """
        Get the total number of talks in the corpus.

        Returns:
            Number of talks
        """
        return len(self.talks)

    def clear(self) -> None:
        """Clear all talks from the corpus."""
        self.talks = []
        self._save_to_storage()

    def _load_from_storage(self) -> None:
        """Load talks from persistent storage."""
        if not self.storage_path:
            return

        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.talks = [HistoricalTalk.from_dict(talk_data) for talk_data in data]
        except FileNotFoundError:
            # File doesn't exist yet, start with empty corpus
            pass
        except Exception:
            # Error loading, start with empty corpus
            pass

    def _save_to_storage(self) -> None:
        """Save talks to persistent storage."""
        if not self.storage_path:
            return

        try:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump([talk.to_dict() for talk in self.talks], f, indent=2, ensure_ascii=False)
        except Exception:
            # Error saving, continue without persistence
            pass

