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
        Dynamic calculation for originality score.

        Args:
            text: The text to analyze
            reference_texts: Optional reference texts

        Returns:
            Originality score between 0.0 and 1.0
        """
        text_lower = text.lower()
        
        # Start with high originality, subtract for generic/problematic patterns
        originality = 1.0
        
        # 1. Check for template-like phrases (big penalty)
        template_phrases = [
            "we are pleased to announce", "call for papers",
            "we invite submissions", "topics of interest include",
            "we welcome papers on", "submissions are invited",
            "please submit your", "deadline for submission"
        ]
        template_count = sum(1 for phrase in template_phrases if phrase in text_lower)
        originality -= min(0.40, template_count * 0.15)
        
        # 2. Penalize generic/buzzword content
        generic_score = self._calculate_genericness(text)
        originality -= (generic_score * 0.30)  # Up to 30% penalty for genericness
        
        # 3. Penalize AI-like patterns
        ai_score = self._calculate_ai_heuristic(text)
        originality -= (ai_score * 0.20)  # Up to 20% penalty for AI patterns
        
        # 4. Reward specific, concrete content
        specific_indicators = [
            "we reduced", "we increased", "we built", "we discovered",
            "our team", "our experience", "our production", "at our company",
            "when we", "after we", "case study", "real example"
        ]
        specific_count = sum(1 for phrase in specific_indicators if phrase in text_lower)
        originality += min(0.15, specific_count * 0.05)  # Bonus for specificity
        
        # 5. Check for numbers/metrics (indicates real experience)
        has_percentages = '%' in text or 'percent' in text_lower
        has_numbers = any(char.isdigit() for char in text)
        has_metrics = any(word in text_lower for word in ['million', 'thousand', 'ms', 'seconds', 'users', 'requests'])
        
        if has_percentages:
            originality += 0.10
        if has_numbers and has_metrics:
            originality += 0.10
        
        # 6. If we have reference texts, check overlap
        if reference_texts:
            max_overlap = 0.0
            text_words = set(text_lower.split())
            for ref_text in reference_texts:
                ref_words = set(ref_text.lower().split())
                if len(text_words) > 0 and len(ref_words) > 0:
                    overlap = len(text_words & ref_words) / len(text_words)
                    max_overlap = max(max_overlap, overlap)
            # High overlap with existing content = lower originality
            originality -= (max_overlap * 0.30)
        
        return max(0.0, min(1.0, originality))

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
        Heuristic for AI generation detection with dynamic scoring.

        Args:
            text: The text to analyze

        Returns:
            AI probability score between 0.0 and 1.0
        """
        text_lower = text.lower()
        score = 0.0
        
        # 1. Check for AI-style transition words (very common in ChatGPT)
        ai_transitions = [
            "furthermore", "moreover", "additionally", "in conclusion",
            "it is important to note", "it is worth noting", "notably",
            "in today's", "in this talk", "in this presentation",
            "we will explore", "we will delve into", "we will examine",
            "this talk will", "this presentation will", "this session will"
        ]
        transition_count = sum(1 for phrase in ai_transitions if phrase in text_lower)
        score += min(0.35, transition_count * 0.08)
        
        # 2. Check for vague, buzzword-heavy language
        buzzwords = [
            "cutting-edge", "state-of-the-art", "revolutionary", "innovative",
            "transformative", "paradigm", "leverage", "synergy", "robust",
            "comprehensive overview", "deep dive", "best practices",
            "real-world", "hands-on", "actionable insights"
        ]
        buzzword_count = sum(1 for word in buzzwords if word in text_lower)
        score += min(0.25, buzzword_count * 0.06)
        
        # 3. Check for overly structured/formulaic language
        formulaic_phrases = [
            "we are pleased to", "we invite you to", "participants will learn",
            "attendees will gain", "this session aims to", "the goal of this",
            "by the end of this", "upon completion"
        ]
        formulaic_count = sum(1 for phrase in formulaic_phrases if phrase in text_lower)
        score += min(0.20, formulaic_count * 0.1)
        
        # 4. Check for lack of specifics (AI often uses vague language)
        specific_indicators = [
            "we reduced", "we increased", "we built", "we discovered",
            "our team", "our experience", "our production", "at our company",
            "when we", "after we", "% improvement", "x faster", "million"
        ]
        specific_count = sum(1 for phrase in specific_indicators if phrase in text_lower)
        # Fewer specifics = more likely AI
        if specific_count == 0:
            score += 0.15
        elif specific_count == 1:
            score += 0.05
        
        # 5. Check sentence structure uniformity (AI tends to be very uniform)
        sentences = text.split('.')
        if len(sentences) > 2:
            avg_length = sum(len(s.split()) for s in sentences) / len(sentences)
            # Very uniform sentence length suggests AI
            if 15 <= avg_length <= 25:  # AI sweet spot
                score += 0.10
        
        return min(1.0, score)

    def _calculate_genericness(self, text: str) -> float:
        """
        Calculate how generic the text appears with dynamic scoring.

        Args:
            text: The text to analyze

        Returns:
            Genericness score between 0.0 and 1.0
        """
        text_lower = text.lower()
        score = 0.0
        
        # 1. Vague quantifiers (very generic)
        vague_quantifiers = [
            "various", "numerous", "many", "several", "multiple",
            "wide range", "diverse", "extensive", "comprehensive"
        ]
        quantifier_count = sum(1 for term in vague_quantifiers if term in text_lower)
        score += min(0.30, quantifier_count * 0.08)
        
        # 2. Generic topics without specificity
        generic_topics = [
            "topics include", "areas such as", "domains including",
            "aspects of", "fundamentals of", "introduction to",
            "overview of", "basics of", "getting started"
        ]
        topic_count = sum(1 for phrase in generic_topics if phrase in text_lower)
        score += min(0.25, topic_count * 0.12)
        
        # 3. Lack of concrete details
        has_numbers = any(char.isdigit() for char in text)
        has_metrics = any(word in text_lower for word in ['%', 'percent', 'million', 'thousand', 'seconds', 'ms'])
        has_tools = any(word in text_lower for word in ['python', 'java', 'docker', 'kubernetes', 'aws', 'postgres', 'redis'])
        
        specificity_score = sum([has_numbers, has_metrics, has_tools])
        if specificity_score == 0:
            score += 0.25  # Very generic
        elif specificity_score == 1:
            score += 0.10  # Somewhat generic
        # else: specific, no penalty
        
        # 4. Filler words and phrases
        filler_phrases = [
            "it is important", "it is essential", "it is critical",
            "we will discuss", "we will cover", "we will explore",
            "allows you to", "enables you to", "helps you"
        ]
        filler_count = sum(1 for phrase in filler_phrases if phrase in text_lower)
        score += min(0.20, filler_count * 0.10)
        
        return min(1.0, score)

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

