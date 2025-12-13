"""Coordinator Agent that manages the workflow and aggregates results from specialized agents."""

import asyncio
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from goc_guardian.agents.base import AgentResult
from goc_guardian.agents.abstract_analysis import AbstractAnalysisAgent
from goc_guardian.agents.content_evaluation import ContentEvaluationAgent
from goc_guardian.evaluators.oumi_evaluator import OumiEvaluator
from goc_guardian.utils.exceptions import EvaluationError, InvalidInputError


class AnalysisReport(BaseModel):
    """Complete analysis report aggregating results from all agents."""

    cfp_text: str
    agent_results: List[AgentResult]
    overall_risk_level: str
    summary: str
    recommendations: List[str]


class CoordinatorAgent:
    """Coordinator agent that orchestrates analysis across specialized agents."""

    def __init__(self, evaluator: Optional[OumiEvaluator] = None):
        """
        Initialize the Coordinator Agent.

        Args:
            evaluator: Optional shared Oumi evaluator instance
        """
        self.evaluator = evaluator or OumiEvaluator()
        self.abstract_agent = AbstractAnalysisAgent(self.evaluator)
        self.content_agent = ContentEvaluationAgent(self.evaluator)

    async def analyze_cfp(self, cfp_text: str) -> AnalysisReport:
        """
        Analyze CFP text using all specialized agents.

        Args:
            cfp_text: The CFP text to analyze

        Returns:
            AnalysisReport containing aggregated results from all agents

        Raises:
            InvalidInputError: If input validation fails
            EvaluationError: If analysis fails
        """
        # Validate input
        if not cfp_text or not isinstance(cfp_text, str):
            raise InvalidInputError("CFP text must be a non-empty string")
        if len(cfp_text.strip()) < 50:
            raise InvalidInputError("CFP text must be at least 50 characters long")

        try:
            # Run all agents concurrently for efficiency
            agent_results = await asyncio.gather(
                self.abstract_agent.analyze(cfp_text),
                self.content_agent.analyze(cfp_text),
                return_exceptions=True,
            )

            # Process results, handling any exceptions
            processed_results: List[AgentResult] = []
            for result in agent_results:
                if isinstance(result, Exception):
                    # Create error result for failed agent
                    error_result = AgentResult(
                        agent_name="Unknown",
                        confidence=0.0,
                        findings={"error": str(result)},
                        explanation=f"Analysis failed: {str(result)}",
                    )
                    processed_results.append(error_result)
                else:
                    processed_results.append(result)

            # Determine overall risk level
            overall_risk = self._calculate_overall_risk(processed_results)

            # Generate summary and recommendations
            summary = self._generate_summary(processed_results, overall_risk)
            recommendations = self._generate_recommendations(processed_results, overall_risk)

            return AnalysisReport(
                cfp_text=cfp_text[:200] + "..." if len(cfp_text) > 200 else cfp_text,
                agent_results=processed_results,
                overall_risk_level=overall_risk,
                summary=summary,
                recommendations=recommendations,
            )

        except (InvalidInputError, EvaluationError):
            raise
        except Exception as e:
            raise EvaluationError(f"Coordinated analysis failed: {str(e)}") from e

    def _calculate_overall_risk(self, agent_results: List[AgentResult]) -> str:
        """
        Calculate overall risk level from agent results.

        Args:
            agent_results: List of results from all agents

        Returns:
            Overall risk level: "low", "medium", or "high"
        """
        risk_scores = {"low": 0, "medium": 1, "high": 2}
        max_risk = "low"

        for result in agent_results:
            risk_level = result.findings.get("risk_level", "low")
            if risk_scores.get(risk_level, 0) > risk_scores.get(max_risk, 0):
                max_risk = risk_level

        return max_risk

    def _generate_summary(self, agent_results: List[AgentResult], overall_risk: str) -> str:
        """
        Generate a summary of the analysis.

        Args:
            agent_results: List of results from all agents
            overall_risk: Overall risk level

        Returns:
            Human-readable summary
        """
        summaries = []

        for result in agent_results:
            if "error" not in result.findings:
                summaries.append(f"{result.agent_name}: {result.explanation}")

        if not summaries:
            return "Analysis completed, but some services were unavailable. Please review manually."

        summary = f"Overall Risk Level: {overall_risk.upper()}\n\n"
        summary += "\n\n".join(summaries)

        return summary

    def _generate_recommendations(
        self, agent_results: List[AgentResult], overall_risk: str
    ) -> List[str]:
        """
        Generate reviewer recommendations based on analysis results.

        Args:
            agent_results: List of results from all agents
            overall_risk: Overall risk level

        Returns:
            List of recommendations for the reviewer
        """
        recommendations = []

        if overall_risk == "high":
            recommendations.append(
                "HIGH RISK: This CFP requires careful review. Check for copied content, "
                "AI generation, or lack of specificity."
            )
        elif overall_risk == "medium":
            recommendations.append(
                "MEDIUM RISK: This CFP may have some concerns. Review for originality and quality."
            )

        for result in agent_results:
            if "error" in result.findings:
                continue

            findings = result.findings

            # Recommendations based on abstract analysis
            if result.agent_name == "AbstractAnalysisAgent":
                if not findings.get("is_original", True):
                    recommendations.append(
                        "Check for copied or heavily derived content. Verify proper attribution if applicable."
                    )
                elif findings.get("originality_score", 1.0) < 0.7:
                    recommendations.append(
                        "Review for near-duplicate sections that may need revision."
                    )

            # Recommendations based on content evaluation
            elif result.agent_name == "ContentEvaluationAgent":
                if findings.get("is_ai_generated", False):
                    recommendations.append(
                        "Content appears AI-generated. Verify that it meets conference quality standards."
                    )
                if findings.get("is_overly_generic", False):
                    recommendations.append(
                        "Content is overly generic. Ensure it provides specific details about the conference."
                    )

        if not recommendations:
            recommendations.append(
                "No significant concerns detected. Standard review process recommended."
            )

        return recommendations

