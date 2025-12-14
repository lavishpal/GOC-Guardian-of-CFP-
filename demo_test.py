"""Demo test scenarios for CFP Guardian."""

import asyncio
from goc_guardian.models import CFPSubmission
from goc_guardian.agents.enhanced_coordinator import EnhancedCoordinatorAgent


# Test Scenarios
SCENARIOS = {
    "generic": {
        "title": "Introduction to Machine Learning",
        "abstract": """This presentation will cover the fundamentals of machine learning, 
including supervised and unsupervised learning algorithms. We will explore 
various techniques and applications of ML in different domains. Attendees 
will gain insights into the latest trends and best practices in the field.""",
        "expected": "HIGH risk - Generic, buzzword-heavy content",
    },
    "specific": {
        "title": "Optimizing PostgreSQL Query Performance in High-Throughput Systems",
        "abstract": """Based on our experience scaling a fintech platform to 50M daily 
transactions, this talk presents specific techniques for PostgreSQL optimization. 
We'll cover: partition pruning strategies that reduced query time by 80%, 
effective use of materialized views with incremental refresh, and our custom 
connection pooling solution that eliminated timeout errors. Real production 
metrics and pgBadger analysis will be shared.""",
        "expected": "LOW risk - Specific technical content with metrics",
    },
    "ai_generated": {
        "title": "Leveraging Cutting-Edge Technologies for Digital Transformation",
        "abstract": """In today's rapidly evolving landscape, it is imperative to harness 
innovative solutions that drive organizational excellence. This session will 
delve into transformative strategies, exploring how emerging technologies can 
revolutionize business processes. Furthermore, we will examine best practices 
and actionable insights to empower stakeholders in their journey towards 
digital maturity.""",
        "expected": "HIGH risk - AI-generated patterns, vague buzzwords",
    },
    "duplicate": {
        "title": "Getting Started with Docker Containers",
        "abstract": """Docker has revolutionized application deployment. This talk covers 
Docker basics, containers vs VMs, creating Dockerfiles, and deploying 
containerized applications. Perfect for beginners wanting to learn Docker.""",
        "expected": "MEDIUM-HIGH risk - Common topic, likely similar talks exist",
    },
}


async def run_scenario(coordinator: EnhancedCoordinatorAgent, scenario_name: str, scenario_data: dict):
    """Run a single test scenario."""
    print("\n" + "=" * 80)
    print(f"SCENARIO: {scenario_name.upper()}")
    print("=" * 80)
    print(f"Title: {scenario_data['title']}")
    print(f"\nAbstract:\n{scenario_data['abstract']}")
    print(f"\nExpected: {scenario_data['expected']}")
    print("\n" + "-" * 80)
    print("ANALYZING...")
    print("-" * 80)
    
    try:
        cfp = CFPSubmission(
            title=scenario_data["title"],
            abstract=scenario_data["abstract"],
        )
        
        report = await coordinator.analyze_cfp(cfp, fetch_historical=True)
        
        print(f"\nRESULTS:")
        print(f"Risk Level: {report.overall_risk_level.upper()}")
        print(f"Confidence: {report.confidence:.2f}")
        
        if hasattr(report, 'evaluation_metrics'):
            print(f"\nMetrics:")
            print(f"  - Originality: {report.evaluation_metrics.originality_score:.2f}")
            print(f"  - AI Generation: {report.evaluation_metrics.ai_generation_score:.2f}")
            print(f"  - Semantic Similarity: {report.evaluation_metrics.semantic_similarity_score:.2f}")
        
        print(f"\nSimilar Talks Found: {len(report.similar_talks)}")
        
        if report.similar_talks:
            print("\nTop Similar Talks:")
            for i, talk in enumerate(report.similar_talks[:3], 1):
                print(f"  {i}. {talk.title} (similarity: {talk.similarity_score:.2f})")
        
        print(f"\nSummary:\n{report.summary}")
        
        if report.recommendations:
            print(f"\nRecommendations:")
            for i, rec in enumerate(report.recommendations, 1):
                print(f"  {i}. {rec}")
        
        return True
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        print(f"Error Type: {type(e).__name__}")
        return False


async def run_all_scenarios():
    """Run all demo scenarios."""
    print("\nCFP GUARDIAN - DEMO TEST SCENARIOS")
    print("=" * 80)
    
    coordinator = EnhancedCoordinatorAgent()
    
    try:
        results = {}
        for scenario_name, scenario_data in SCENARIOS.items():
            success = await run_scenario(coordinator, scenario_name, scenario_data)
            results[scenario_name] = success
            
            # Pause between scenarios
            if scenario_name != list(SCENARIOS.keys())[-1]:
                print("\n" + "=" * 80)
                await asyncio.sleep(2)  # Give time to read results
        
        # Summary
        print("\n" + "=" * 80)
        print("DEMO SUMMARY")
        print("=" * 80)
        for scenario_name, success in results.items():
            status = "PASSED" if success else "FAILED"
            print(f"{scenario_name.ljust(20)}: {status}")
        
        total = len(results)
        passed = sum(results.values())
        print(f"\nTotal: {passed}/{total} scenarios completed successfully")
        
    finally:
        await coordinator.close()


async def run_single_scenario(scenario_name: str):
    """Run a single scenario by name."""
    if scenario_name not in SCENARIOS:
        print(f"Unknown scenario: {scenario_name}")
        print(f"Available scenarios: {', '.join(SCENARIOS.keys())}")
        return
    
    coordinator = EnhancedCoordinatorAgent()
    
    try:
        await run_scenario(coordinator, scenario_name, SCENARIOS[scenario_name])
    finally:
        await coordinator.close()


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) > 1:
        # Run specific scenario
        scenario_name = sys.argv[1].lower()
        print(f"\nRunning scenario: {scenario_name}")
        asyncio.run(run_single_scenario(scenario_name))
    else:
        # Run all scenarios
        print("\nRunning all scenarios (use 'python demo_test.py <scenario_name>' for specific scenario)")
        print(f"Available scenarios: {', '.join(SCENARIOS.keys())}")
        asyncio.run(run_all_scenarios())


if __name__ == "__main__":
    main()
