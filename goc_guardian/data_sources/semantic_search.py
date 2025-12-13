"""Semantic search for finding similar talks."""

from typing import List
from goc_guardian.models import HistoricalTalk, SimilarTalk, CFPSubmission


class SemanticSearch:
    """Semantic search engine for finding similar talks."""

    def __init__(self):
        """Initialize semantic search."""
        # In production, this would use embeddings (e.g., sentence-transformers, OpenAI embeddings)
        # For now, we'll use a simple text similarity approach
        pass

    async def find_similar_talks(
        self, cfp: CFPSubmission, historical_talks: List[HistoricalTalk], top_k: int = 10
    ) -> List[SimilarTalk]:
        """
        Find semantically similar talks to the CFP submission.

        Args:
            cfp: CFP submission to find similar talks for
            historical_talks: List of historical talks to search
            top_k: Number of top similar talks to return

        Returns:
            List of SimilarTalk objects sorted by similarity
        """
        if not historical_talks:
            return []

        cfp_text = cfp.get_full_text().lower()
        cfp_words = set(cfp_text.split())

        similar_talks = []

        for talk in historical_talks:
            talk_text = talk.get_full_text().lower()
            talk_words = set(talk_text.split())

            # Calculate semantic similarity (using word overlap as heuristic)
            # In production, this would use proper embeddings and cosine similarity
            similarity = self._calculate_semantic_similarity(cfp_text, talk_text, cfp_words, talk_words)
            paraphrase_likelihood = self._calculate_paraphrase_likelihood(cfp_text, talk_text)

            if similarity > 0.1:  # Only include talks with some similarity
                similar_talks.append(
                    SimilarTalk(
                        talk=talk,
                        similarity_score=similarity,
                        paraphrase_likelihood=paraphrase_likelihood,
                    )
                )

        # Sort by similarity score and return top_k
        similar_talks.sort(key=lambda x: x.similarity_score, reverse=True)
        return similar_talks[:top_k]

    def _calculate_semantic_similarity(
        self, text1: str, text2: str, words1: set, words2: set
    ) -> float:
        """
        Calculate semantic similarity between two texts.

        Args:
            text1: First text
            text2: Second text
            words1: Set of words from first text
            words2: Set of words from second text

        Returns:
            Similarity score between 0.0 and 1.0
        """
        if not words1 or not words2:
            return 0.0

        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        jaccard = intersection / union if union > 0 else 0.0

        # Title similarity (weighted higher)
        # In production, use proper embeddings for semantic similarity
        title_similarity = self._title_similarity(text1, text2)

        # Combined score
        return (jaccard * 0.6 + title_similarity * 0.4)

    def _title_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate title similarity (heuristic).

        Args:
            text1: First text
            text2: Second text

        Returns:
            Title similarity score
        """
        # Extract first sentence as title (heuristic)
        title1 = text1.split(".")[0].lower() if "." in text1 else text1.lower()
        title2 = text2.split(".")[0].lower() if "." in text2 else text2.lower()

        words1 = set(title1.split())
        words2 = set(title2.split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0.0

    def _calculate_paraphrase_likelihood(self, text1: str, text2: str) -> float:
        """
        Calculate paraphrase likelihood between two texts.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Paraphrase likelihood between 0.0 and 1.0
        """
        # Heuristic: check for similar structure and key phrases
        # In production, use Oumi or a paraphrase detection model

        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        # High word overlap suggests paraphrase
        overlap = len(words1 & words2)
        avg_length = (len(words1) + len(words2)) / 2
        paraphrase_score = min(1.0, (overlap / avg_length) * 1.5) if avg_length > 0 else 0.0

        return paraphrase_score

