"""Oumi evaluation pipeline for comprehensive content analysis."""

import asyncio
from typing import Dict, Any, List, Optional
from src.models.corpus_manager import CFPSubmission, SimilarTalk
from src.config.oumi_client import OumiClient, OumiConfig
from src.utils.exceptions import APIUnavailableError, EvaluationError


class OumiPipeline:
    """
    Pipeline for Oumi-based evaluation.
    
    Accepts CFP text + similar talks, uses Oumi to evaluate similarity and paraphrasing,
    and produces numeric scores and explanations.
    Handles missing API keys gracefully by returning default values.
    """

    def __init__(self, config: Optional[OumiConfig] = None):
        """
        Initialize Oumi pipeline.

        Args:
            config: Optional Oumi configuration
        """
        self.client = OumiClient(config)
        self._has_api_key = bool(self.client.config.api_key)

    async def evaluate_comprehensive(
        self, cfp: CFPSubmission, similar_talks: List[SimilarTalk]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive evaluation using Oumi.

        Args:
            cfp: CFP submission
            similar_talks: List of similar talks

        Returns:
            Dictionary with all evaluation metrics and explanations:
            {
                "semantic_similarity": {
                    "scores": Dict[str, float],
                    "explanations": Dict[str, str],
                    "max_score": float
                },
                "paraphrase_likelihood": {
                    "score": float,
                    "explanation": str
                },
                "ai_generation_probability": {
                    "score": float,
                    "explanation": str
                },
                "originality_score": {
                    "score": float,
                    "explanation": str
                }
            }
        """
        cfp_text = cfp.get_full_text()
        reference_texts = [st.talk.get_full_text() for st in similar_talks]

        # Run evaluations concurrently using Oumi
        results = await asyncio.gather(
            self._evaluate_semantic_similarity(cfp, similar_talks),
            self._evaluate_paraphrase(cfp, similar_talks),
            self._evaluate_ai_generation(cfp_text),
            self._evaluate_originality(cfp_text, reference_texts),
            return_exceptions=True,
        )

        semantic, paraphrase, ai_gen, originality = results

        # Handle exceptions gracefully
        semantic_result = (
            semantic
            if not isinstance(semantic, Exception)
            else {"scores": {}, "explanations": {}, "max_score": 0.0}
        )
        paraphrase_result = (
            paraphrase
            if not isinstance(paraphrase, Exception)
            else {"score": 0.0, "explanation": "Evaluation unavailable"}
        )
        ai_gen_result = (
            ai_gen
            if not isinstance(ai_gen, Exception)
            else {"score": 0.0, "explanation": "Evaluation unavailable"}
        )
        originality_result = (
            originality
            if not isinstance(originality, Exception)
            else {"score": 0.5, "explanation": "Evaluation unavailable"}
        )

        return {
            "semantic_similarity": semantic_result,
            "paraphrase_likelihood": paraphrase_result,
            "ai_generation_probability": ai_gen_result,
            "originality_score": originality_result,
        }

    async def _evaluate_semantic_similarity(
        self, cfp: CFPSubmission, similar_talks: List[SimilarTalk]
    ) -> Dict[str, Any]:
        """
        Evaluate semantic similarity using Oumi.

        Args:
            cfp: CFP submission
            similar_talks: List of similar talks

        Returns:
            Dictionary with scores, explanations, and max score.
            Handles missing API keys gracefully.
        """
        # Check if API key is available
        if not self._has_api_key:
            return {
                "scores": {},
                "explanations": {
                    "error": "Oumi API key not configured. Semantic similarity evaluation unavailable."
                },
                "max_score": 0.0,
            }

        cfp_text = cfp.get_full_text()
        similarity_scores = {}
        explanations = {}

        # Use Oumi to compare CFP vs each historical talk
        for idx, st in enumerate(similar_talks):
            try:
                result = await self.client.evaluate_semantic_similarity(
                    cfp_text, st.talk.get_full_text()
                )
                similarity_scores[f"talk_{idx}"] = result["score"]
                explanations[f"talk_{idx}"] = result["explanation"]
            except APIUnavailableError as e:
                # Missing API key or API unavailable - return default with explanation
                similarity_scores[f"talk_{idx}"] = 0.0
                explanations[f"talk_{idx}"] = f"Oumi API unavailable: {str(e)}"
            except EvaluationError as e:
                # Evaluation error - return default with explanation
                similarity_scores[f"talk_{idx}"] = 0.0
                explanations[f"talk_{idx}"] = f"Evaluation error: {str(e)}"
            except Exception as e:
                # Unexpected error - return default with explanation
                similarity_scores[f"talk_{idx}"] = 0.0
                explanations[f"talk_{idx}"] = f"Unexpected error: {str(e)}"

        max_score = max(similarity_scores.values()) if similarity_scores else 0.0

        return {
            "scores": similarity_scores,
            "explanations": explanations,
            "max_score": max_score,
        }

    async def _evaluate_paraphrase(
        self, cfp: CFPSubmission, similar_talks: List[SimilarTalk]
    ) -> Dict[str, Any]:
        """
        Evaluate paraphrase likelihood using Oumi.

        Args:
            cfp: CFP submission
            similar_talks: List of similar talks

        Returns:
            Dictionary with numeric score and explanation.
            Handles missing API keys gracefully.
        """
        if not similar_talks:
            return {
                "score": 0.0,
                "explanation": "No similar talks to compare for paraphrase detection.",
            }

        # Check if API key is available
        if not self._has_api_key:
            return {
                "score": 0.0,
                "explanation": "Oumi API key not configured. Paraphrase evaluation unavailable.",
            }

        cfp_text = cfp.get_full_text()
        scores = []
        explanations = []

        # Use Oumi to detect paraphrased content
        for st in similar_talks:
            try:
                result = await self.client.evaluate_paraphrase(
                    cfp_text, st.talk.get_full_text()
                )
                scores.append(result["score"])
                explanations.append(result["explanation"])
            except APIUnavailableError as e:
                # Missing API key or API unavailable
                scores.append(0.0)
                explanations.append(f"Oumi API unavailable: {str(e)}")
            except EvaluationError as e:
                # Evaluation error
                scores.append(0.0)
                explanations.append(f"Evaluation error: {str(e)}")
            except Exception as e:
                # Unexpected error
                scores.append(0.0)
                explanations.append(f"Unexpected error: {str(e)}")

        # Calculate average score (numeric)
        avg_score = sum(scores) / len(scores) if scores else 0.0

        # Combine explanations
        if explanations:
            combined_explanation = (
                f"Paraphrase detection across {len(similar_talks)} similar talks. "
                f"Average likelihood: {avg_score:.2%}. "
                + explanations[0]  # Include first explanation
            )
        else:
            combined_explanation = f"Paraphrase detection unavailable for {len(similar_talks)} talks."

        return {
            "score": avg_score,
            "explanation": combined_explanation,
        }

    async def _evaluate_ai_generation(self, text: str) -> Dict[str, Any]:
        """
        Evaluate AI generation probability using Oumi.

        Args:
            text: Text to evaluate

        Returns:
            Dictionary with numeric score and explanation.
            Handles missing API keys gracefully.
        """
        # Check if API key is available
        if not self._has_api_key:
            return {
                "score": 0.0,
                "explanation": "Oumi API key not configured. AI generation evaluation unavailable.",
            }

        try:
            result = await self.client.evaluate_ai_generation(text)
            return result
        except APIUnavailableError as e:
            return {
                "score": 0.0,
                "explanation": f"Oumi API unavailable: {str(e)}",
            }
        except EvaluationError as e:
            return {
                "score": 0.0,
                "explanation": f"Evaluation error: {str(e)}",
            }
        except Exception as e:
            return {
                "score": 0.0,
                "explanation": f"Unexpected error: {str(e)}",
            }

    async def _evaluate_originality(
        self, text: str, reference_texts: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluate originality score using Oumi.

        Args:
            text: Text to evaluate
            reference_texts: List of reference texts

        Returns:
            Dictionary with numeric score and explanation.
            Handles missing API keys gracefully.
        """
        # Check if API key is available
        if not self._has_api_key:
            return {
                "score": 0.5,
                "explanation": "Oumi API key not configured. Originality evaluation unavailable.",
            }

        try:
            result = await self.client.evaluate_originality(text, reference_texts)
            return result
        except APIUnavailableError as e:
            return {
                "score": 0.5,
                "explanation": f"Oumi API unavailable: {str(e)}",
            }
        except EvaluationError as e:
            return {
                "score": 0.5,
                "explanation": f"Evaluation error: {str(e)}",
            }
        except Exception as e:
            return {
                "score": 0.5,
                "explanation": f"Unexpected error: {str(e)}",
            }

    async def close(self):
        """Close Oumi client connection."""
        await self.client.close()

