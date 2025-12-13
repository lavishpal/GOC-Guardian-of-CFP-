"""Content Evaluation Agent for detecting AI-generated and overly generic CFP content."""

from typing import Dict, Any, Optional
from goc_guardian.agents.base import BaseAgent, AgentResult
from goc_guardian.evaluators.oumi_evaluator import OumiEvaluator
from goc_guardian.utils.exceptions import APIUnavailableError, EvaluationError


class ContentEvaluationAgent(BaseAgent):
    """Agent specialized in detecting AI-generated and overly generic CFP content."""

    def __init__(self, evaluator: Optional[OumiEvaluator] = None):
        """
        Initialize the Content Evaluation Agent.

        Args:
            evaluator: Optional Oumi evaluator instance
        """
        super().__init__("ContentEvaluationAgent")
        self.evaluator = evaluator or OumiEvaluator()

    async def analyze(self, cfp_text: str) -> AgentResult:
        """
        Analyze CFP text for AI-generated or overly generic content.

        Args:
            cfp_text: The CFP text to analyze

        Returns:
            AgentResult with findings about AI generation and genericness

        Raises:
            EvaluationError: If analysis fails
        """
        self._validate_input(cfp_text)

        try:
            # Use Oumi to evaluate AI generation
            ai_evaluation = await self.evaluator.evaluate_ai_generation(cfp_text)

            ai_probability = ai_evaluation.get("ai_probability", 0.5)
            is_ai_generated = ai_evaluation.get("is_ai_generated", False)
            genericness_score = ai_evaluation.get("genericness_score", 0.5)
            is_overly_generic = ai_evaluation.get("is_overly_generic", False)

            # Calculate confidence based on AI probability and genericness
            confidence = max(ai_probability, genericness_score)

            # Build findings
            findings: Dict[str, Any] = {
                "ai_probability": ai_probability,
                "is_ai_generated": is_ai_generated,
                "genericness_score": genericness_score,
                "is_overly_generic": is_overly_generic,
                "risk_level": self._determine_risk_level(ai_probability, genericness_score),
            }

            # Generate reviewer-friendly explanation
            explanation = self._generate_explanation(
                ai_probability, is_ai_generated, genericness_score, is_overly_generic
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
                    "ai_probability": None,
                    "is_ai_generated": None,
                    "genericness_score": None,
                },
                explanation="Unable to analyze content quality: evaluation service is currently unavailable. Please try again later.",
            )
        except Exception as e:
            raise EvaluationError(f"Content evaluation failed: {str(e)}") from e

    def _determine_risk_level(
        self, ai_probability: float, genericness_score: float
    ) -> str:
        """
        Determine the risk level based on AI probability and genericness.

        Args:
            ai_probability: Probability that content is AI-generated
            genericness_score: Score indicating how generic the content is

        Returns:
            Risk level: "low", "medium", or "high"
        """
        if ai_probability > 0.7 or genericness_score > 0.8:
            return "high"
        elif ai_probability > 0.5 or genericness_score > 0.6:
            return "medium"
        else:
            return "low"

    def _generate_explanation(
        self,
        ai_probability: float,
        is_ai_generated: bool,
        genericness_score: float,
        is_overly_generic: bool,
    ) -> str:
        """
        Generate a reviewer-friendly explanation of the findings.

        Args:
            ai_probability: Probability that content is AI-generated
            is_ai_generated: Whether content appears AI-generated
            genericness_score: Score indicating how generic the content is
            is_overly_generic: Whether content is overly generic

        Returns:
            Human-readable explanation
        """
        explanations = []

        if is_ai_generated:
            explanations.append(
                f"This CFP shows characteristics consistent with AI-generated content "
                f"(probability: {ai_probability:.2f}). "
                "Reviewer should verify that the content is original and thoughtfully crafted."
            )
        elif ai_probability > 0.5:
            explanations.append(
                f"This CFP may contain some AI-generated elements "
                f"(probability: {ai_probability:.2f}). "
                "Reviewer should assess content quality and originality."
            )

        if is_overly_generic:
            explanations.append(
                f"This CFP appears overly generic and lacks specific details "
                f"(genericness score: {genericness_score:.2f}). "
                "Reviewer should check for sufficient specificity and concrete information."
            )
        elif genericness_score > 0.6:
            explanations.append(
                f"This CFP may be somewhat generic "
                f"(genericness score: {genericness_score:.2f}). "
                "Reviewer should verify that it provides sufficient detail."
            )

        if not explanations:
            return (
                f"This CFP appears to be human-written and specific. "
                f"AI probability: {ai_probability:.2f}, Genericness: {genericness_score:.2f}. "
                "No significant concerns detected."
            )

        return " ".join(explanations)

