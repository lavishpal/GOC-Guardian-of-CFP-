"""Similarity Detection Agent for finding semantically similar talks."""

from typing import List, Optional
import math
from src.models.corpus_manager import CFPSubmission, HistoricalTalk, SimilarTalk, CorpusManager


class SimilarityDetectionAgent:
    """
    Agent that accepts CFP submission text,
    queries corpus_manager for similar talks,
    and returns top 5 similar entries.
    
    Responsibilities:
    - Accept CFP submission text
    - Query corpus_manager for similar talks
    - Return top 5 similar entries
    - If vector search fails, fallback to keyword matching
    """

    def __init__(self, corpus_manager: Optional[CorpusManager] = None):
        """
        Initialize similarity detection agent.

        Args:
            corpus_manager: Optional corpus manager instance
        """
        self.corpus_manager = corpus_manager or CorpusManager()
        self._embeddings_cache = {}  # Cache for embeddings

    async def find_similar_talks(self, cfp: CFPSubmission) -> List[SimilarTalk]:
        """
        Accept CFP submission text, query corpus for similar talks, return top 5.

        Args:
            cfp: CFP submission to find similar talks for

        Returns:
            List of top 5 similarity candidates sorted by similarity score
        """
        # Query corpus_manager for all talks
        historical_talks = self.corpus_manager.get_all_talks()

        if not historical_talks:
            return []

        cfp_text = cfp.get_full_text()

        # Try vector search first
        try:
            similar_talks = await self._vector_search(cfp_text, historical_talks)
            if similar_talks:
                # Return top 5
                return similar_talks[:5]
        except Exception:
            # Vector search failed, fallback to keyword matching
            pass

        # Fallback to keyword matching
        similar_talks = self._keyword_matching(cfp_text, historical_talks)
        return similar_talks[:5]

    async def _vector_search(
        self, cfp_text: str, historical_talks: List[HistoricalTalk]
    ) -> List[SimilarTalk]:
        """
        Perform vector search using embeddings.

        Args:
            cfp_text: CFP submission text
            historical_talks: List of historical talks to search

        Returns:
            List of similar talks sorted by similarity score

        Raises:
            Exception: If vector search fails (e.g., embeddings unavailable)
        """
        # Get embedding for CFP text
        cfp_embedding = await self._get_embedding(cfp_text)

        similarity_scores = []

        # Calculate similarity for each talk
        for talk in historical_talks:
            talk_text = talk.get_full_text()
            talk_embedding = await self._get_embedding(talk_text)

            # Calculate cosine similarity
            similarity = self._cosine_similarity(cfp_embedding, talk_embedding)

            # Calculate paraphrase likelihood (simplified - based on similarity)
            paraphrase_likelihood = similarity * 0.8  # Paraphrase is typically high similarity

            similarity_scores.append(
                SimilarTalk(
                    talk=talk,
                    similarity_score=similarity,
                    paraphrase_likelihood=paraphrase_likelihood,
                )
            )

        # Sort by similarity score (descending)
        similarity_scores.sort(key=lambda x: x.similarity_score, reverse=True)
        return similarity_scores

    async def _get_embedding(self, text: str) -> List[float]:
        """
        Get embedding vector for text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector as list of floats

        Raises:
            Exception: If embeddings are unavailable
        """
        # Check cache first
        if text in self._embeddings_cache:
            return self._embeddings_cache[text]

        # Try to use sentence transformers if available
        try:
            from sentence_transformers import SentenceTransformer

            if not hasattr(self, "_model"):
                # Initialize model (use a lightweight model)
                self._model = SentenceTransformer("all-MiniLM-L6-v2")

            embedding = self._model.encode(text, convert_to_numpy=True).tolist()
            self._embeddings_cache[text] = embedding
            return embedding

        except ImportError:
            # Fallback: use simple TF-IDF-like embedding
            # This is a basic fallback that will work but isn't true vector search
            raise Exception("Vector search unavailable: sentence-transformers not installed")

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors.

        Args:
            vec1: First vector
            vec2: Second vector

        Returns:
            Cosine similarity score between 0.0 and 1.0
        """
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(a * a for a in vec2))

        if magnitude1 == 0.0 or magnitude2 == 0.0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    def _keyword_matching(
        self, cfp_text: str, historical_talks: List[HistoricalTalk]
    ) -> List[SimilarTalk]:
        """
        Fallback keyword matching when vector search fails.

        Args:
            cfp_text: CFP submission text
            historical_talks: List of historical talks to search

        Returns:
            List of similar talks sorted by keyword match score
        """
        cfp_text_lower = cfp_text.lower()
        cfp_words = set(cfp_text_lower.split())

        similarity_scores = []

        for talk in historical_talks:
            talk_text = talk.get_full_text().lower()
            talk_words = set(talk_text.split())

            # Calculate keyword overlap
            if not cfp_words or not talk_words:
                continue

            # Jaccard similarity
            intersection = len(cfp_words & talk_words)
            union = len(cfp_words | talk_words)
            jaccard_similarity = intersection / union if union > 0 else 0.0

            # Title similarity (weighted higher)
            cfp_title_words = set(cfp_text_lower.split()[:10])  # First 10 words as title
            talk_title_words = set(talk_text.split()[:10])
            title_intersection = len(cfp_title_words & talk_title_words)
            title_union = len(cfp_title_words | talk_title_words)
            title_similarity = (
                title_intersection / title_union if title_union > 0 else 0.0
            )

            # Combined similarity score
            similarity = jaccard_similarity * 0.6 + title_similarity * 0.4

            # Paraphrase likelihood (simplified)
            paraphrase_likelihood = min(1.0, similarity * 1.2)

            if similarity > 0.1:  # Minimum threshold
                similarity_scores.append(
                    SimilarTalk(
                        talk=talk,
                        similarity_score=similarity,
                        paraphrase_likelihood=paraphrase_likelihood,
                    )
                )

        # Sort by similarity score (descending)
        similarity_scores.sort(key=lambda x: x.similarity_score, reverse=True)
        return similarity_scores

