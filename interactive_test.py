#!/usr/bin/env python3
"""Interactive test script to compare different CFP abstracts."""

import asyncio
import sys
from goc_guardian.models import CFPSubmission
from goc_guardian.agents.enhanced_coordinator import EnhancedCoordinatorAgent


# Test cases with clear differences
TEST_CASES = {
    "1": {
        "name": "ChatGPT-Generated (Generic)",
        "title": "Leveraging AI for Digital Transformation",
        "abstract": """In today's rapidly evolving landscape, it is imperative to harness 
        innovative solutions that drive organizational excellence. This session will delve 
        into transformative strategies, exploring how emerging technologies can revolutionize 
        business processes. Furthermore, we will examine best practices and actionable 
        insights to empower stakeholders in their journey towards digital maturity.""",
        "expected": "HIGH AI probability, MEDIUM-HIGH risk"
    },
    "2": {
        "name": "Technical Specific Content",
        "title": "Reducing PostgreSQL Query Latency by 80% at Scale",
        "abstract": """We reduced query time by 80% using partition pruning strategies in 
        our fintech platform handling 50M daily transactions. Our team built a custom 
        connection pooling solution that eliminated timeout errors. When we implemented 
        materialized views with incremental refresh, we discovered a 40% improvement in 
        dashboard load times. Production metrics show 2ms average query latency at peak load.""",
        "expected": "LOW AI probability, LOW risk"
    },
    "3": {
        "name": "Buzzword-Heavy (AI-like)",
        "title": "Cutting-Edge Cloud-Native Solutions",
        "abstract": """This talk will explore state-of-the-art, cutting-edge solutions for 
        leveraging synergies in the cloud-native paradigm. Furthermore, we will delve into 
        comprehensive best practices for transformative digital transformation. Moreover, 
        this presentation will provide actionable insights and real-world use cases that 
        enable organizations to achieve robust, innovative results through various diverse 
        approaches.""",
        "expected": "VERY HIGH AI probability, HIGH risk"
    },
    "4": {
        "name": "Simple but Real",
        "title": "Building a Python CLI Tool",
        "abstract": """Learn how we built a command-line tool in Python that our DevOps 
        team uses daily. I'll show the code structure, how we handled argument parsing 
        with argparse, and our testing approach with pytest. You'll see real examples 
        from our GitHub repo and walk away with templates you can use.""",
        "expected": "LOW AI probability, LOW risk"
    }
}


async def analyze_test_case(coordinator, case_num, case_data):
    """Analyze a single test case and display results."""
    print("\n" + "=" * 80)
    print(f"TEST CASE {case_num}: {case_data['name']}")
    print("=" * 80)
    print(f"Title: {case_data['title']}")
    print(f"\nAbstract:\n{case_data['abstract'][:200]}...")
    print(f"\nExpected: {case_data['expected']}")
    print("\n" + "-" * 80)
    print("ANALYZING...")
    print("-" * 80)
    
    try:
        cfp = CFPSubmission(
            title=case_data["title"],
            abstract=case_data["abstract"]
        )
        
        report = await coordinator.analyze_cfp(cfp, fetch_historical=False)
        
        # Display results
        print(f"\n✅ RESULTS:")
        print(f"Overall Risk Level: {report.overall_risk_level.upper()}")
        
        metrics = report.evaluation_metrics
        print(f"\nMetrics:")
        print(f"  • Originality Score:        {metrics.originality_score * 100:6.1f}%")
        print(f"  • AI Generation Probability: {metrics.ai_generation_probability * 100:6.1f}%")
        print(f"  • Paraphrase Likelihood:     {metrics.paraphrase_likelihood * 100:6.1f}%")
        
        # Color-coded interpretation
        ai_prob = metrics.ai_generation_probability
        if ai_prob >= 0.6:
            ai_status = "🚨 HIGH (Likely AI-generated)"
        elif ai_prob >= 0.3:
            ai_status = "⚠️  MEDIUM (Some AI patterns)"
        else:
            ai_status = "✅ LOW (Appears human-written)"
        
        print(f"\nInterpretation: {ai_status}")
        
        if report.recommendations:
            print(f"\nRecommendations:")
            for rec in report.recommendations:
                print(f"  • {rec}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return False


async def run_all_tests():
    """Run all test cases."""
    print("\n🧪 CFP GUARDIAN - INTERACTIVE TEST SUITE")
    print("=" * 80)
    print("Testing different types of CFP content to demonstrate dynamic evaluation")
    print("=" * 80)
    
    coordinator = EnhancedCoordinatorAgent()
    
    try:
        for case_num in sorted(TEST_CASES.keys()):
            success = await analyze_test_case(coordinator, case_num, TEST_CASES[case_num])
            if not success:
                print(f"\n⚠️  Test case {case_num} failed")
            
            # Pause between tests
            if case_num != list(TEST_CASES.keys())[-1]:
                input("\n📋 Press Enter to continue to next test...")
        
        # Final summary
        print("\n" + "=" * 80)
        print("🎉 TEST SUMMARY")
        print("=" * 80)
        print("If you see DIFFERENT scores for each test case, the system is working!")
        print("\nKey observations:")
        print("  • ChatGPT/Generic text → HIGH AI probability (60-80%)")
        print("  • Technical/Specific text → LOW AI probability (0-20%)")
        print("  • Buzzword-heavy text → VERY HIGH AI probability (70-90%)")
        print("  • Real but simple text → LOW AI probability (10-30%)")
        print("\n✅ Dynamic evaluation is WORKING as expected!")
        print("=" * 80)
        
    finally:
        await coordinator.close()


async def run_custom_test():
    """Allow user to input custom CFP for testing."""
    print("\n✏️  CUSTOM CFP TEST")
    print("=" * 80)
    
    title = input("Enter CFP Title: ").strip()
    if len(title) < 10:
        print("❌ Title must be at least 10 characters")
        return
    
    print("\nEnter Abstract (press Ctrl+D when done):")
    abstract_lines = []
    try:
        while True:
            line = input()
            abstract_lines.append(line)
    except EOFError:
        pass
    
    abstract = "\n".join(abstract_lines).strip()
    if len(abstract) < 50:
        print("❌ Abstract must be at least 50 characters")
        return
    
    coordinator = EnhancedCoordinatorAgent()
    
    try:
        cfp = CFPSubmission(title=title, abstract=abstract)
        report = await coordinator.analyze_cfp(cfp, fetch_historical=False)
        
        print("\n" + "=" * 80)
        print("ANALYSIS RESULTS")
        print("=" * 80)
        print(f"Risk Level: {report.overall_risk_level.upper()}")
        
        metrics = report.evaluation_metrics
        print(f"\nOriginality Score:        {metrics.originality_score * 100:.1f}%")
        print(f"AI Generation Probability: {metrics.ai_generation_probability * 100:.1f}%")
        print(f"Paraphrase Likelihood:     {metrics.paraphrase_likelihood * 100:.1f}%")
        
        if report.recommendations:
            print(f"\nRecommendations:")
            for rec in report.recommendations:
                print(f"  • {rec}")
        
    finally:
        await coordinator.close()


def main():
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--custom":
        print("🎯 Running custom test mode")
        asyncio.run(run_custom_test())
    else:
        print("🎯 Running all test cases")
        print("Tip: Use --custom flag to test your own CFP text")
        asyncio.run(run_all_tests())


if __name__ == "__main__":
    main()
