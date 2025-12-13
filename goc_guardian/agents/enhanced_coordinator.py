"""Enhanced Coordinator Agent that integrates historical talks and semantic search."""

import asyncio
from typing import List, Optional
from pydantic import BaseModel
from goc_guardian.models import CFPSubmission, SimilarTalk, HistoricalTalk, EvaluationMetrics
from goc_guardian.agents.base import AgentResult
from goc_guardian.data_sources.sched_client import SchedClient
from goc_guardian.data_sources.sessionize_client import SessionizeClient
from goc_guardian.data_sources.semantic_search import SemanticSearch
from goc_guardian.evaluators.oumi_evaluator import OumiEvaluator
from goc_guardian.utils.exceptions import EvaluationError, InvalidInputError


class EnhancedAnalysisReport(BaseModel):
    """Complete analysis report with historical talks and similarity analysis."""

    cfp: CFPSubmission
    similar_talks: List[SimilarTalk]
    evaluation_metrics: EvaluationMetrics
    overall_risk_level: str
    summary: str
    recommendations: List[str]
    agent_results: List[AgentResult]


class EnhancedCoordinatorAgent:
    """Enhanced coordinator that fetches historical talks and performs comprehensive analysis."""

    def __init__(
        self,
        evaluator: Optional[OumiEvaluator] = None,
        sched_api_key: Optional[str] = None,
        sessionize_api_key: Optional[str] = None,
    ):
        """
        Initialize the Enhanced Coordinator Agent.

        Args:
            evaluator: Optional shared Oumi evaluator instance
            sched_api_key: Optional API key for Sched.com
            sessionize_api_key: Optional API key for Sessionize.com
        """
        self.evaluator = evaluator or OumiEvaluator()
        self.sched_client = SchedClient(api_key=sched_api_key)
        self.sessionize_client = SessionizeClient(api_key=sessionize_api_key)
        self.semantic_search = SemanticSearch()

    async def analyze_cfp(
        self,
        cfp: CFPSubmission,
        fetch_historical: bool = True,
        max_similar_talks: int = 10,
    ) -> EnhancedAnalysisReport:
        """
        Analyze CFP submission with historical talks and semantic search.

        Args:
            cfp: CFP submission to analyze
            fetch_historical: Whether to fetch historical talks
            max_similar_talks: Maximum number of similar talks to return

        Returns:
            EnhancedAnalysisReport with comprehensive analysis

        Raises:
            InvalidInputError: If input validation fails
            EvaluationError: If analysis fails
        """
        # Validate input
        if not cfp.title or len(cfp.title.strip()) < 10:
            raise InvalidInputError("CFP title must be at least 10 characters long")
        if not cfp.abstract or len(cfp.abstract.strip()) < 50:
            raise InvalidInputError("CFP abstract must be at least 50 characters long")

        try:
            # Step 1: Fetch historical talks (if enabled)
            historical_talks: List[HistoricalTalk] = []
            if fetch_historical:
                historical_talks = await self._fetch_historical_talks()

            # Step 2: Find semantically similar talks
            similar_talks = await self.semantic_search.find_similar_talks(
                cfp, historical_talks, top_k=max_similar_talks
            )

            # Step 3: Run comprehensive Oumi evaluation
            evaluation_result = await self.evaluator.evaluate_comprehensive(cfp, similar_talks)

            # Step 4: Build evaluation metrics
            metrics = self._build_evaluation_metrics(evaluation_result, similar_talks)

            # Step 5: Determine overall risk level
            overall_risk = self._calculate_overall_risk(metrics, similar_talks)

            # Step 6: Generate summary and recommendations
            summary = self._generate_summary(cfp, metrics, similar_talks, overall_risk)
            recommendations = self._generate_recommendations(metrics, similar_talks, overall_risk)

            # Step 7: Create agent results for compatibility
            agent_results = self._create_agent_results(evaluation_result)

            return EnhancedAnalysisReport(
                cfp=cfp,
                similar_talks=similar_talks,
                evaluation_metrics=metrics,
                overall_risk_level=overall_risk,
                summary=summary,
                recommendations=recommendations,
                agent_results=agent_results,
            )

        except (InvalidInputError, EvaluationError):
            raise
        except Exception as e:
            raise EvaluationError(f"Enhanced analysis failed: {str(e)}") from e

    async def _fetch_historical_talks(self) -> List[HistoricalTalk]:
        """
        Fetch historical talks from all sources.

        Returns:
            List of historical talks
        """
        try:
            # Fetch from both sources concurrently
            sched_talks, sessionize_talks = await asyncio.gather(
                self.sched_client.fetch_talks(limit=50),
                self.sessionize_client.fetch_talks(limit=50),
                return_exceptions=True,
            )

            all_talks = []
            if isinstance(sched_talks, list):
                all_talks.extend(sched_talks)
            if isinstance(sessionize_talks, list):
                all_talks.extend(sessionize_talks)

            return all_talks
        except Exception:
            # Fail gracefully - return empty list
            return []

    def _build_evaluation_metrics(
        self, evaluation_result: dict, similar_talks: List[SimilarTalk]
    ) -> EvaluationMetrics:
        """
        Build EvaluationMetrics from evaluation results.

        Args:
            evaluation_result: Raw evaluation results from Oumi
            similar_talks: List of similar talks

        Returns:
            EvaluationMetrics object
        """
        semantic_sim = evaluation_result.get("semantic_similarity", {})
        paraphrase = evaluation_result.get("paraphrase_likelihood", {})
        ai_gen = evaluation_result.get("ai_generation", {})
        originality = evaluation_result.get("originality", {})

        # Extract similarity scores
        similarity_scores = {}
        if isinstance(semantic_sim, dict):
            similarity_scores = semantic_sim.get("similarity_scores", {})

        # Extract paraphrase likelihood
        paraphrase_likelihood = 0.0
        if isinstance(paraphrase, dict):
            paraphrase_likelihood = paraphrase.get("paraphrase_likelihood", 0.0)

        # Extract AI probability
        ai_probability = 0.0
        if isinstance(ai_gen, dict):
            ai_probability = ai_gen.get("ai_probability", 0.0)

        # Extract originality score
        originality_score = 0.5
        if isinstance(originality, dict):
            originality_score = originality.get("originality_score", 0.5)

        return EvaluationMetrics(
            semantic_similarity=similarity_scores,
            paraphrase_likelihood=paraphrase_likelihood,
            ai_generation_probability=ai_probability,
            originality_score=originality_score,
        )

    def _calculate_overall_risk(
        self, metrics: EvaluationMetrics, similar_talks: List[SimilarTalk]
    ) -> str:
        """
        Calculate overall risk level.

        Args:
            metrics: Evaluation metrics
            similar_talks: List of similar talks

        Returns:
            Risk level: "low", "medium", or "high"
        """
        risk_factors = []

        # High similarity is a risk factor
        if metrics.semantic_similarity:
            max_sim = max(metrics.semantic_similarity.values()) if metrics.semantic_similarity.values() else 0.0
            if max_sim > 0.8:
                risk_factors.append("high")
            elif max_sim > 0.6:
                risk_factors.append("medium")

        # High paraphrase likelihood is a risk factor
        if metrics.paraphrase_likelihood > 0.7:
            risk_factors.append("high")
        elif metrics.paraphrase_likelihood > 0.5:
            risk_factors.append("medium")

        # High AI probability is a risk factor
        if metrics.ai_generation_probability > 0.7:
            risk_factors.append("high")
        elif metrics.ai_generation_probability > 0.5:
            risk_factors.append("medium")

        # Low originality is a risk factor
        if metrics.originality_score < 0.4:
            risk_factors.append("high")
        elif metrics.originality_score < 0.6:
            risk_factors.append("medium")

        # Determine overall risk
        if "high" in risk_factors or len(risk_factors) >= 3:
            return "high"
        elif "medium" in risk_factors or len(risk_factors) >= 2:
            return "medium"
        else:
            return "low"

    def _generate_summary(
        self,
        cfp: CFPSubmission,
        metrics: EvaluationMetrics,
        similar_talks: List[SimilarTalk],
        overall_risk: str,
    ) -> str:
        """Generate human-readable summary."""
        summary_parts = [f"Overall Risk Level: {overall_risk.upper()}\n"]

        summary_parts.append(f"Found {len(similar_talks)} similar historical talks.")

        if similar_talks:
            top_similar = similar_talks[0]
            summary_parts.append(
                f"Most similar talk: '{top_similar.talk.title}' "
                f"(similarity: {top_similar.similarity_score:.2f})"
            )

        summary_parts.append(f"\nOriginality Score: {metrics.originality_score:.2f}")
        summary_parts.append(f"Paraphrase Likelihood: {metrics.paraphrase_likelihood:.2f}")
        summary_parts.append(f"AI Generation Probability: {metrics.ai_generation_probability:.2f}")

        if metrics.semantic_similarity:
            max_sim = max(metrics.semantic_similarity.values()) if metrics.semantic_similarity.values() else 0.0
            summary_parts.append(f"Max Semantic Similarity: {max_sim:.2f}")

        return "\n".join(summary_parts)

    def _generate_recommendations(
        self, metrics: EvaluationMetrics, similar_talks: List[SimilarTalk], overall_risk: str
    ) -> List[str]:
        """Generate reviewer recommendations."""
        recommendations = []

        if overall_risk == "high":
            recommendations.append(
                "HIGH RISK: This CFP requires careful review. Multiple risk factors detected."
            )
        elif overall_risk == "medium":
            recommendations.append("MEDIUM RISK: Review for originality and quality.")

        if metrics.paraphrase_likelihood > 0.7:
            recommendations.append(
                f"High paraphrase likelihood ({metrics.paraphrase_likelihood:.2f}). "
                "Verify that content is not a paraphrase of existing talks."
            )

        if similar_talks and similar_talks[0].similarity_score > 0.8:
            top_talk = similar_talks[0]
            recommendations.append(
                f"Very similar to existing talk: '{top_talk.talk.title}'. "
                "Review for originality and proper attribution."
            )

        if metrics.ai_generation_probability > 0.6:
            recommendations.append(
                f"High AI generation probability ({metrics.ai_generation_probability:.2f}). "
                "Verify content quality and originality."
            )

        if metrics.originality_score < 0.5:
            recommendations.append(
                f"Low originality score ({metrics.originality_score:.2f}). "
                "Review for copied or heavily derived content."
            )

        if not recommendations:
            recommendations.append("No significant concerns detected. Standard review recommended.")

        return recommendations

    def _create_agent_results(self, evaluation_result: dict) -> List[AgentResult]:
        """Create agent results for compatibility."""
        results = []

        # Create result for semantic similarity
        semantic = evaluation_result.get("semantic_similarity", {})
        if isinstance(semantic, dict):
            results.append(
                AgentResult(
                    agent_name="SemanticSimilarityAgent",
                    confidence=semantic.get("max_similarity", 0.0),
                    findings=semantic,
                    explanation=f"Found {semantic.get('num_similar_talks', 0)} similar talks.",
                )
            )

        # Create result for paraphrase detection
        paraphrase = evaluation_result.get("paraphrase_likelihood", {})
        if isinstance(paraphrase, dict):
            results.append(
                AgentResult(
                    agent_name="ParaphraseDetectionAgent",
                    confidence=paraphrase.get("paraphrase_likelihood", 0.0),
                    findings=paraphrase,
                    explanation=f"Paraphrase likelihood: {paraphrase.get('paraphrase_likelihood', 0.0):.2f}",
                )
            )

        return results

    async def close(self):
        """Close all client connections."""
        await self.sched_client.close()
        await self.sessionize_client.close()

