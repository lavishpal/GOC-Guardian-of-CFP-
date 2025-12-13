"""Oumi Evaluation Agent for comprehensive content evaluation."""

from typing import Dict, Any, List, Optional
from src.models.corpus_manager import CFPSubmission, SimilarTalk
from src.evaluation.oumi_pipeline import OumiPipeline
from src.config.oumi_client import OumiConfig


class OumiEvaluationAgent:
    """
    Agent that uses Oumi to evaluate:
    - Semantic similarity
    - Paraphrase likelihood
    - AI-generated patterns
    
    Responsibilities:
    - Accept CFP text + similar talks
    - Use Oumi to evaluate similarity and paraphrasing
    - Produce numeric scores and explanations
    - Handle missing API keys gracefully
    """

    def __init__(
        self, pipeline: Optional[OumiPipeline] = None, config: Optional[OumiConfig] = None
    ):
        """
        Initialize Oumi evaluation agent.

        Args:
            pipeline: Optional Oumi pipeline instance
            config: Optional Oumi configuration
        """
        if pipeline is None:
            self.pipeline = OumiPipeline(config)
        else:
            self.pipeline = pipeline

    async def evaluate(
        self, cfp: CFPSubmission, similar_talks: List[SimilarTalk]
    ) -> Dict[str, Any]:
        """
        Accept CFP text + similar talks, use Oumi to evaluate similarity and paraphrasing.

        Args:
            cfp: CFP submission to evaluate
            similar_talks: List of similar talks for comparison

        Returns:
            Dictionary with structured evaluation metrics containing numeric scores and explanations:
            {
                "semantic_similarity": {
                    "scores": Dict[str, float],  # Numeric scores per talk
                    "explanations": Dict[str, str],  # Explanations per talk
                    "max_score": float  # Maximum similarity score
                },
                "paraphrase_likelihood": {
                    "score": float,  # Numeric score (0.0 to 1.0)
                    "explanation": str  # Human-readable explanation
                },
                "ai_generation_probability": {
                    "score": float,  # Numeric score (0.0 to 1.0)
                    "explanation": str  # Human-readable explanation
                },
                "originality_score": {
                    "score": float,  # Numeric score (0.0 to 1.0)
                    "explanation": str  # Human-readable explanation
                }
            }
            
        Note: All methods handle missing API keys gracefully by returning default values
        with appropriate explanations.
        """
        # Use Oumi pipeline for comprehensive evaluation
        # Pipeline handles missing API keys gracefully
        evaluation_result = await self.pipeline.evaluate_comprehensive(cfp, similar_talks)

        # Return structured metrics with numeric scores and explanations from Oumi
        return {
            "semantic_similarity": evaluation_result.get("semantic_similarity", {}),
            "paraphrase_likelihood": evaluation_result.get("paraphrase_likelihood", {}),
            "ai_generation_probability": evaluation_result.get("ai_generation_probability", {}),
            "originality_score": evaluation_result.get("originality_score", {}),
        }

    async def close(self):
        """Close pipeline connections."""
        await self.pipeline.close()

