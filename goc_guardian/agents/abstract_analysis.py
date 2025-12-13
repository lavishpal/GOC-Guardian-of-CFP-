"""Abstract Analysis Agent for detecting copied and near-duplicate CFP abstracts."""

from typing import Dict, Any, Optional
from goc_guardian.agents.base import BaseAgent, AgentResult
from goc_guardian.evaluators.oumi_evaluator import OumiEvaluator
from goc_guardian.utils.exceptions import APIUnavailableError, EvaluationError


class AbstractAnalysisAgent(BaseAgent):
    """Agent specialized in detecting copied and near-duplicate CFP abstracts."""

    def __init__(self, evaluator: Optional[OumiEvaluator] = None):
        """
        Initialize the Abstract Analysis Agent.

        Args:
            evaluator: Optional Oumi evaluator instance
        """
        super().__init__("AbstractAnalysisAgent")
        self.evaluator = evaluator or OumiEvaluator()

    async def analyze(self, cfp_text: str) -> AgentResult:
        """
        Analyze CFP text for copied or near-duplicate content.

        Args:
            cfp_text: The CFP text to analyze

        Returns:
            AgentResult with findings about copied/duplicate content

        Raises:
            EvaluationError: If analysis fails
        """
        self._validate_input(cfp_text)

        try:
            # Use Oumi to evaluate originality
            evaluation_result = await self.evaluator.evaluate_originality(cfp_text)

            # Determine if content appears copied or duplicated
            originality_score = evaluation_result.get("originality_score", 0.5)
            is_original = evaluation_result.get("is_original", True)
            similarity_scores = evaluation_result.get("similarity_scores", {})

            # Calculate confidence based on originality score
            confidence = 1.0 - originality_score if not is_original else originality_score

            # Build findings
            findings: Dict[str, Any] = {
                "originality_score": originality_score,
                "is_original": is_original,
                "similarity_scores": similarity_scores,
                "risk_level": self._determine_risk_level(originality_score, similarity_scores),
            }

            # Generate reviewer-friendly explanation
            explanation = self._generate_explanation(
                originality_score, is_original, similarity_scores
            )

            return AgentResult(
                agent_name=self.name,
                confidence=confidence,
                findings=findings,
                explanation=explanation,
            )

        except APIUnavailableError:
            # Fail gracefully - return a neutral result
            return AgentResult(
                agent_name=self.name,
                confidence=0.5,
                findings={
                    "error": "Evaluation service unavailable",
                    "originality_score": None,
                    "is_original": None,
                },
                explanation="Unable to analyze originality: evaluation service is currently unavailable. Please try again later.",
            )
        except Exception as e:
            raise EvaluationError(f"Abstract analysis failed: {str(e)}") from e

    def _determine_risk_level(
        self, originality_score: float, similarity_scores: Dict[str, float]
    ) -> str:
        """
        Determine the risk level based on originality and similarity scores.

        Args:
            originality_score: Originality score from evaluation
            similarity_scores: Similarity scores with reference texts

        Returns:
            Risk level: "low", "medium", or "high"
        """
        if originality_score < 0.4:
            return "high"
        elif originality_score < 0.7:
            return "medium"
        elif any(score > 0.8 for score in similarity_scores.values()):
            return "medium"
        else:
            return "low"

    def _generate_explanation(
        self,
        originality_score: float,
        is_original: bool,
        similarity_scores: Dict[str, float],
    ) -> str:
        """
        Generate a reviewer-friendly explanation of the findings.

        Args:
            originality_score: Originality score from evaluation
            is_original: Whether content appears original
            similarity_scores: Similarity scores with reference texts

        Returns:
            Human-readable explanation
        """
        if not is_original or originality_score < 0.5:
            explanation = (
                f"This CFP shows signs of being copied or heavily derived from existing content. "
                f"Originality score: {originality_score:.2f}. "
            )
            if similarity_scores:
                max_similarity = max(similarity_scores.values())
                explanation += (
                    f"High similarity detected with reference texts (max: {max_similarity:.2f}). "
                )
            explanation += "Reviewer should verify originality and check for proper attribution."
        elif originality_score < 0.7:
            explanation = (
                f"This CFP may contain some duplicated content. "
                f"Originality score: {originality_score:.2f}. "
                "Reviewer should review for near-duplicate sections."
            )
        else:
            explanation = (
                f"This CFP appears to be original. "
                f"Originality score: {originality_score:.2f}. "
                "No significant duplication detected."
            )

        return explanation

