"""Main entry point for GOC: Guardians of CFP."""

import asyncio
import sys
from src.models.corpus_manager import CFPSubmission
from src.agents.conference_intelligence_agent import ConferenceIntelligenceAgent
from src.agents.similarity_detection_agent import SimilarityDetectionAgent
from src.agents.oumi_evaluation_agent import OumiEvaluationAgent
from src.agents.reviewer_decision_agent import ReviewerDecisionAgent


async def analyze_cfp_cli(title: str, abstract: str, description: str = None):
    """Analyze CFP from command line."""
    from src.models.corpus_manager import CorpusManager
    
    # Initialize shared corpus manager
    corpus_manager = CorpusManager()
    
    # Initialize agents with shared corpus manager
    conference_agent = ConferenceIntelligenceAgent(corpus_manager=corpus_manager)
    similarity_agent = SimilarityDetectionAgent(corpus_manager=corpus_manager)
    oumi_agent = OumiEvaluationAgent()
    decision_agent = ReviewerDecisionAgent()

    try:
        # Create CFP submission
        cfp = CFPSubmission(
            title=title,
            abstract=abstract,
            description=description,
        )

        print("Analyzing CFP...")
        print(f"Title: {cfp.title}\n")

        # Step 1: Conference intelligence - crawl and store talks
        print("Crawling and storing historical talks...")
        crawl_result = await conference_agent.crawl_and_store()
        print(f"Crawled {crawl_result['talks_fetched']} talks, stored {crawl_result['talks_stored']} in corpus\n")

        # Step 2: Similarity detection - retrieve from corpus (returns top 5)
        print("Detecting similar talks from corpus...")
        similar_talks = await similarity_agent.find_similar_talks(cfp)
        print(f"Found {len(similar_talks)} similar talks (top 5)\n")

        # Step 3: Oumi evaluation
        print("Running Oumi evaluation...")
        evaluation_metrics = await oumi_agent.evaluate(cfp, similar_talks)

        # Step 4: Generate report
        print("Generating report...\n")
        report = decision_agent.generate_report(cfp, similar_talks, evaluation_metrics)

        # Display results
        print("=" * 80)
        print("GOC: Guardians of CFP - ANALYSIS REPORT")
        print("=" * 80)
        print(f"\nRecommendation: {report.recommendation}")
        print(f"\n{report.explanation}")
        
        print(f"\nMetrics:")
        print(f"  Semantic Similarity: {report.semantic_similarity:.2%}")
        print(f"  Paraphrase Likelihood: {report.paraphrase_likelihood:.2%}")
        print(f"  AI Generation Confidence: {report.ai_generation_confidence:.2%}")
        print(f"  Originality Score: {report.originality_score:.2%}")

        if report.similar_talks:
            print(f"\nSimilar Talks ({len(report.similar_talks)}):")
            for st in report.similar_talks[:5]:
                title = st.get("title", "Unknown")
                similarity = st.get("similarity_score", 0.0)
                print(f"  - {title} (similarity: {similarity:.2%})")

        print("\n" + "=" * 80)

        await conference_agent.close()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        await conference_agent.close()
        sys.exit(1)


def main():
    """Main CLI entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--web":
        # Run web server
        from src.ui.reviewer_app import create_app
        import uvicorn
        app = create_app()
        uvicorn.run(app, host="0.0.0.0", port=8000)
    elif len(sys.argv) < 3:
        print("Usage:", file=sys.stderr)
        print("  python main.py --web                    # Start web server", file=sys.stderr)
        print("  python main.py <title> <abstract> [description]  # Analyze CFP", file=sys.stderr)
        sys.exit(1)
    else:
        title = sys.argv[1]
        abstract = sys.argv[2]
        description = sys.argv[3] if len(sys.argv) > 3 else None
        asyncio.run(analyze_cfp_cli(title, abstract, description))


if __name__ == "__main__":
    main()

