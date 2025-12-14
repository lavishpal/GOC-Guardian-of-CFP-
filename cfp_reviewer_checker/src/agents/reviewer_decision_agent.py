"""Reviewer Decision Agent for generating final recommendations."""

from typing import List, Dict, Any
from src.models.corpus_manager import CFPSubmission, SimilarTalk, NormalizedTalk
from src.models.reviewer_report import ReviewerReport, SimilarTalkEntry


class ReviewerDecisionAgent:
    """Agent that generates final reviewer recommendations."""

    def __init__(self):
        """Initialize reviewer decision agent."""
        pass

    def generate_report(
        self,
        cfp: CFPSubmission,
        similar_talks: List[SimilarTalk],
        evaluation_metrics: Dict[str, Any],
    ) -> ReviewerReport:
        """
        Generate comprehensive reviewer report.

        Args:
            cfp: CFP submission
            similar_talks: List of similar talks
            evaluation_metrics: Evaluation metrics from Oumi

        Returns:
            ReviewerReport matching the standard structure
        """
        # Extract numeric scores from Oumi evaluation metrics
        semantic_sim_data = evaluation_metrics.get("semantic_similarity", {})
        semantic_similarity = (
            semantic_sim_data.get("max_score", 0.0)
            if isinstance(semantic_sim_data, dict)
            else 0.0
        )

        paraphrase_data = evaluation_metrics.get("paraphrase_likelihood", {})
        paraphrase_likelihood = (
            paraphrase_data.get("score", 0.0)
            if isinstance(paraphrase_data, dict)
            else 0.0
        )

        ai_gen_data = evaluation_metrics.get("ai_generation_probability", {})
        ai_generation_confidence = (
            ai_gen_data.get("score", 0.0) if isinstance(ai_gen_data, dict) else 0.0
        )

        originality_data = evaluation_metrics.get("originality_score", {})
        originality_score = (
            originality_data.get("score", 0.5)
            if isinstance(originality_data, dict)
            else 0.5
        )

        # Convert similar talks to normalized format
        similar_talk_entries = [
            SimilarTalkEntry(
                talk=st.talk.to_normalized(),
                similarity_score=st.similarity_score,
                paraphrase_likelihood=st.paraphrase_likelihood,
            )
            for st in similar_talks
        ]

        # Generate recommendation and explanation
        recommendation = self._generate_recommendation(
            semantic_similarity, paraphrase_likelihood, ai_generation_confidence, originality_score
        )
        explanation = self._generate_explanation(
            cfp,
            semantic_similarity,
            paraphrase_likelihood,
            ai_generation_confidence,
            originality_score,
            similar_talks,
            evaluation_metrics,
        )

        return ReviewerReport.from_analysis(
            semantic_similarity=semantic_similarity,
            paraphrase_likelihood=paraphrase_likelihood,
            ai_generation_confidence=ai_generation_confidence,
            originality_score=originality_score,
            similar_talks=similar_talk_entries,
            recommendation=recommendation,
            explanation=explanation,
        )


    def _generate_recommendation(
        self,
        semantic_similarity: float,
        paraphrase_likelihood: float,
        ai_generation_confidence: float,
        originality_score: float,
    ) -> str:
        """
        Generate reviewer recommendation.
        
        Note: This agent never makes accept/reject decisions.
        It only provides guidance and flags for reviewer attention.
        """
        concerns = []

        # Identify concerns without making decisions
        if semantic_similarity > 0.8:
            concerns.append("HIGH semantic similarity with historical talks")
        elif semantic_similarity > 0.6:
            concerns.append("MODERATE semantic similarity detected")

        if paraphrase_likelihood > 0.7:
            concerns.append("HIGH paraphrase likelihood")
        elif paraphrase_likelihood > 0.5:
            concerns.append("MODERATE paraphrase likelihood")

        if ai_generation_confidence > 0.7:
            concerns.append("HIGH AI generation confidence")
        elif ai_generation_confidence > 0.5:
            concerns.append("MODERATE AI generation confidence")

        if originality_score < 0.4:
            concerns.append("LOW originality score")
        elif originality_score < 0.6:
            concerns.append("MODERATE originality score")

        # Generate guidance without accept/reject decision
        if len(concerns) >= 3 or any("HIGH" in c for c in concerns):
            return "REVIEWER ATTENTION REQUIRED - Multiple high-risk factors detected. Please review carefully for originality, duplication, and content quality."
        elif len(concerns) >= 2:
            return "REVIEWER ATTENTION RECOMMENDED - Some concerns detected. Please verify originality and content quality."
        else:
            return "STANDARD REVIEW - No significant concerns detected. Proceed with normal review process."

    def _generate_explanation(
        self,
        cfp: CFPSubmission,
        semantic_similarity: float,
        paraphrase_likelihood: float,
        ai_generation_confidence: float,
        originality_score: float,
        similar_talks: List[SimilarTalk],
        evaluation_metrics: Dict[str, Any],
    ) -> str:
        """Generate detailed explanation using Oumi evaluation results."""
        parts = []

        # Overall assessment
        parts.append(f"Analysis of CFP submission '{cfp.title}' using Oumi evaluation engine:")

        # Get Oumi explanations
        semantic_sim_data = evaluation_metrics.get("semantic_similarity", {})
        paraphrase_data = evaluation_metrics.get("paraphrase_likelihood", {})
        ai_gen_data = evaluation_metrics.get("ai_generation_probability", {})
        originality_data = evaluation_metrics.get("originality_score", {})

        # Semantic similarity with Oumi explanation
        parts.append(f"\nSemantic Similarity: {semantic_similarity:.2%}")
        if isinstance(semantic_sim_data, dict) and semantic_sim_data.get("explanations"):
            # Include Oumi explanation if available
            explanations = semantic_sim_data.get("explanations", {})
            if explanations:
                first_explanation = list(explanations.values())[0]
                parts.append(f"   Oumi: {first_explanation}")
        if semantic_similarity > 0.8:
            parts.append("   HIGH similarity detected with historical talks.")
        elif semantic_similarity > 0.6:
            parts.append("   MODERATE similarity detected.")

        # Paraphrase likelihood with Oumi explanation
        parts.append(f"\nParaphrase Likelihood: {paraphrase_likelihood:.2%}")
        if isinstance(paraphrase_data, dict) and paraphrase_data.get("explanation"):
            parts.append(f"   Oumi: {paraphrase_data['explanation']}")
        if paraphrase_likelihood > 0.7:
            parts.append("   HIGH likelihood of paraphrased content.")
        elif paraphrase_likelihood > 0.5:
            parts.append("   MODERATE likelihood of paraphrased content.")

        # AI generation with Oumi explanation
        parts.append(f"\nAI Generation Confidence: {ai_generation_confidence:.2%}")
        if isinstance(ai_gen_data, dict) and ai_gen_data.get("explanation"):
            parts.append(f"   Oumi: {ai_gen_data['explanation']}")
        if ai_generation_confidence > 0.7:
            parts.append("   HIGH confidence in AI-generated patterns.")
        elif ai_generation_confidence > 0.5:
            parts.append("   MODERATE confidence in AI-generated patterns.")

        # Originality with Oumi explanation
        parts.append(f"\nOriginality Score: {originality_score:.2%}")
        if isinstance(originality_data, dict) and originality_data.get("explanation"):
            parts.append(f"   Oumi: {originality_data['explanation']}")
        if originality_score < 0.4:
            parts.append("   LOW originality - content may be copied or heavily derived.")
        elif originality_score < 0.6:
            parts.append("   MODERATE originality - review for near-duplicates.")

        # Similar talks
        if similar_talks:
            parts.append(f"\nFound {len(similar_talks)} similar historical talk(s):")
            for st in similar_talks[:3]:  # Show top 3
                parts.append(
                    f"   - '{st.talk.title}' ({st.talk.conference or 'Unknown'}, {st.talk.year or 'Unknown'}) "
                    f"- Similarity: {st.similarity_score:.2%}, Paraphrase: {st.paraphrase_likelihood:.2%}"
                )

        return "\n".join(parts)

