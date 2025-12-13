"""Oumi-based evaluator for CFP content analysis."""

import asyncio
from typing import Dict, Any, Optional, List
from goc_guardian.models import SimilarTalk, CFPSubmission
from goc_guardian.utils.exceptions import APIUnavailableError, EvaluationError


class OumiEvaluator:
    """Evaluator using Oumi framework for content analysis."""

    def __init__(self):
        """Initialize the Oumi evaluator."""
        self._available = True

    async def evaluate_originality(
        self, text: str, reference_texts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate the originality of CFP text using Oumi.

        Args:
            text: The CFP text to evaluate
            reference_texts: Optional list of reference texts for comparison

        Returns:
            Dictionary containing originality metrics

        Raises:
            APIUnavailableError: If Oumi API is unavailable
            EvaluationError: If evaluation fails
        """
        if not self._available:
            raise APIUnavailableError("Oumi evaluator is currently unavailable")

        try:
            # Simulate async evaluation with Oumi
            # In production, this would use actual Oumi API calls
            await asyncio.sleep(0.1)  # Simulate API call

            # Placeholder for Oumi integration
            # Actual implementation would use: from oumi import evaluate
            # result = await evaluate(text, metrics=["originality", "similarity"])

            # For now, return a structured result that mimics Oumi output
            originality_score = self._calculate_originality_heuristic(text, reference_texts)

            return {
                "originality_score": originality_score,
                "is_original": originality_score > 0.7,
                "similarity_scores": self._calculate_similarity(text, reference_texts or []),
            }
        except Exception as e:
            if isinstance(e, (APIUnavailableError, EvaluationError)):
                raise
            raise EvaluationError(f"Evaluation failed: {str(e)}") from e

    async def evaluate_ai_generation(self, text: str) -> Dict[str, Any]:
        """
        Evaluate if text appears to be AI-generated using Oumi.

        Args:
            text: The CFP text to evaluate

        Returns:
            Dictionary containing AI generation detection metrics

        Raises:
            APIUnavailableError: If Oumi API is unavailable
            EvaluationError: If evaluation fails
        """
        if not self._available:
            raise APIUnavailableError("Oumi evaluator is currently unavailable")

        try:
            await asyncio.sleep(0.1)  # Simulate API call

            # Placeholder for Oumi AI detection
            # Actual: result = await evaluate(text, metrics=["ai_detection", "genericness"])

            ai_score = self._calculate_ai_heuristic(text)
            generic_score = self._calculate_genericness(text)

            return {
                "ai_probability": ai_score,
                "is_ai_generated": ai_score > 0.6,
                "genericness_score": generic_score,
                "is_overly_generic": generic_score > 0.7,
            }
        except Exception as e:
            if isinstance(e, (APIUnavailableError, EvaluationError)):
                raise
            raise EvaluationError(f"AI evaluation failed: {str(e)}") from e

    def _calculate_originality_heuristic(
        self, text: str, reference_texts: Optional[List[str]] = None
    ) -> float:
        """
        Heuristic calculation for originality (placeholder until Oumi is fully integrated).

        Args:
            text: The text to analyze
            reference_texts: Optional reference texts

        Returns:
            Originality score between 0.0 and 1.0
        """
        # Simple heuristic: check for common generic phrases
        generic_phrases = [
            "we are pleased to announce",
            "call for papers",
            "we invite submissions",
            "topics of interest include",
        ]
        text_lower = text.lower()
        generic_count = sum(1 for phrase in generic_phrases if phrase in text_lower)

        # More generic phrases = lower originality
        base_score = 0.8
        penalty = min(0.3, generic_count * 0.1)
        return max(0.0, base_score - penalty)

    def _calculate_similarity(self, text: str, reference_texts: List[str]) -> Dict[str, float]:
        """
        Calculate similarity scores with reference texts.

        Args:
            text: The text to analyze
            reference_texts: List of reference texts

        Returns:
            Dictionary mapping reference indices to similarity scores
        """
        if not reference_texts:
            return {}

        # Simple word overlap heuristic
        text_words = set(text.lower().split())
        similarities = {}

        for idx, ref_text in enumerate(reference_texts):
            ref_words = set(ref_text.lower().split())
            if len(text_words) == 0 or len(ref_words) == 0:
                similarities[f"ref_{idx}"] = 0.0
            else:
                overlap = len(text_words & ref_words)
                union = len(text_words | ref_words)
                similarity = overlap / union if union > 0 else 0.0
                similarities[f"ref_{idx}"] = similarity

        return similarities

    def _calculate_ai_heuristic(self, text: str) -> float:
        """
        Heuristic for AI generation detection (placeholder).

        Args:
            text: The text to analyze

        Returns:
            AI probability score between 0.0 and 1.0
        """
        # Check for overly formal, generic language patterns
        ai_indicators = [
            "furthermore",
            "moreover",
            "in conclusion",
            "it is important to note",
            "we would like to",
        ]
        text_lower = text.lower()
        indicator_count = sum(1 for indicator in ai_indicators if indicator in text_lower)

        # More indicators = higher AI probability
        base_score = 0.3
        increase = min(0.4, indicator_count * 0.1)
        return min(1.0, base_score + increase)

    def _calculate_genericness(self, text: str) -> float:
        """
        Calculate how generic the text appears.

        Args:
            text: The text to analyze

        Returns:
            Genericness score between 0.0 and 1.0
        """
        # Check for vague, generic terms
        generic_terms = [
            "various",
            "numerous",
            "wide range",
            "diverse",
            "comprehensive",
            "extensive",
        ]
        text_lower = text.lower()
        term_count = sum(1 for term in generic_terms if term in text_lower)

        base_score = 0.4
        increase = min(0.4, term_count * 0.1)
        return min(1.0, base_score + increase)

    async def evaluate_semantic_similarity(
        self, cfp: CFPSubmission, similar_talks: List[SimilarTalk]
    ) -> Dict[str, Any]:
        """
        Evaluate semantic similarity using Oumi.

        Args:
            cfp: CFP submission to evaluate
            similar_talks: List of similar talks with similarity scores

        Returns:
            Dictionary containing semantic similarity metrics

        Raises:
            APIUnavailableError: If Oumi API is unavailable
            EvaluationError: If evaluation fails
        """
        if not self._available:
            raise APIUnavailableError("Oumi evaluator is currently unavailable")

        try:
            await asyncio.sleep(0.1)  # Simulate API call

            # Placeholder for Oumi semantic similarity evaluation
            # Actual: result = await evaluate(cfp.get_full_text(), similar_talks, metrics=["semantic_similarity"])

            similarity_scores = {}
            max_similarity = 0.0

            for idx, similar_talk in enumerate(similar_talks):
                score = similar_talk.similarity_score
                similarity_scores[f"talk_{idx}"] = score
                max_similarity = max(max_similarity, score)

            return {
                "similarity_scores": similarity_scores,
                "max_similarity": max_similarity,
                "num_similar_talks": len(similar_talks),
                "high_risk": max_similarity > 0.8,
            }
        except Exception as e:
            if isinstance(e, (APIUnavailableError, EvaluationError)):
                raise
            raise EvaluationError(f"Semantic similarity evaluation failed: {str(e)}") from e

    async def evaluate_paraphrase_likelihood(
        self, cfp: CFPSubmission, similar_talks: List[SimilarTalk]
    ) -> Dict[str, Any]:
        """
        Evaluate paraphrase likelihood using Oumi.

        Args:
            cfp: CFP submission to evaluate
            similar_talks: List of similar talks

        Returns:
            Dictionary containing paraphrase likelihood metrics

        Raises:
            APIUnavailableError: If Oumi API is unavailable
            EvaluationError: If evaluation fails
        """
        if not self._available:
            raise APIUnavailableError("Oumi evaluator is currently unavailable")

        try:
            await asyncio.sleep(0.1)  # Simulate API call

            # Placeholder for Oumi paraphrase detection
            # Actual: result = await evaluate(cfp.get_full_text(), similar_talks, metrics=["paraphrase"])

            if not similar_talks:
                return {
                    "paraphrase_likelihood": 0.0,
                    "is_paraphrase": False,
                    "max_paraphrase_score": 0.0,
                }

            max_paraphrase = max(talk.paraphrase_likelihood for talk in similar_talks)
            avg_paraphrase = sum(talk.paraphrase_likelihood for talk in similar_talks) / len(similar_talks)

            return {
                "paraphrase_likelihood": avg_paraphrase,
                "max_paraphrase_score": max_paraphrase,
                "is_paraphrase": max_paraphrase > 0.7,
                "num_high_paraphrase": sum(1 for talk in similar_talks if talk.paraphrase_likelihood > 0.7),
            }
        except Exception as e:
            if isinstance(e, (APIUnavailableError, EvaluationError)):
                raise
            raise EvaluationError(f"Paraphrase evaluation failed: {str(e)}") from e

    async def evaluate_comprehensive(
        self, cfp: CFPSubmission, similar_talks: List[SimilarTalk]
    ) -> Dict[str, Any]:
        """
        Comprehensive evaluation using all Oumi metrics.

        Args:
            cfp: CFP submission to evaluate
            similar_talks: List of similar talks

        Returns:
            Dictionary containing all evaluation metrics

        Raises:
            APIUnavailableError: If Oumi API is unavailable
            EvaluationError: If evaluation fails
        """
        if not self._available:
            raise APIUnavailableError("Oumi evaluator is currently unavailable")

        try:
            # Run all evaluations concurrently
            cfp_text = cfp.get_full_text()
            reference_texts = [talk.talk.get_full_text() for talk in similar_talks]

            semantic_result, paraphrase_result, ai_result, originality_result = await asyncio.gather(
                self.evaluate_semantic_similarity(cfp, similar_talks),
                self.evaluate_paraphrase_likelihood(cfp, similar_talks),
                self.evaluate_ai_generation(cfp_text),
                self.evaluate_originality(cfp_text, reference_texts),
                return_exceptions=True,
            )

            # Combine results
            result = {
                "semantic_similarity": semantic_result if not isinstance(semantic_result, Exception) else {},
                "paraphrase_likelihood": paraphrase_result if not isinstance(paraphrase_result, Exception) else {},
                "ai_generation": ai_result if not isinstance(ai_result, Exception) else {},
                "originality": originality_result if not isinstance(originality_result, Exception) else {},
            }

            return result
        except Exception as e:
            if isinstance(e, (APIUnavailableError, EvaluationError)):
                raise
            raise EvaluationError(f"Comprehensive evaluation failed: {str(e)}") from e

    def set_available(self, available: bool) -> None:
        """
        Set the availability status of the evaluator.

        Args:
            available: Whether the evaluator is available
        """
        self._available = available

