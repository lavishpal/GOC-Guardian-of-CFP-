"""Example usage of the CFP Reviewer Checker."""

import asyncio
from goc_guardian.agents.coordinator import CoordinatorAgent


async def example():
    """Example of using the CFP Reviewer Checker."""
    # Sample CFP text
    cfp_text = """
    We are pleased to announce the Call for Papers for the International Conference on 
    Artificial Intelligence and Machine Learning. We invite submissions on various topics 
    including deep learning, natural language processing, computer vision, and more. 
    Furthermore, we welcome papers on numerous applications of AI in diverse domains. 
    It is important to note that submissions should be original and not previously published.
    """

    coordinator = CoordinatorAgent()
    report = await coordinator.analyze_cfp(cfp_text)

    print("Example Analysis Results:")
    print(f"Overall Risk: {report.overall_risk_level}")
    print(f"\nSummary:\n{report.summary}")
    print(f"\nRecommendations:")
    for rec in report.recommendations:
        print(f"  - {rec}")


if __name__ == "__main__":
    asyncio.run(example())

