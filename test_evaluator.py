"""Test script to verify dynamic evaluation is working."""

import asyncio
from goc_guardian.models import CFPSubmission
from goc_guardian.evaluators.oumi_evaluator import OumiEvaluator


async def test_evaluator():
    """Test the improved evaluator with different inputs."""
    
    evaluator = OumiEvaluator()
    
    # Test 1: ChatGPT-style generic text
    print("=" * 80)
    print("TEST 1: ChatGPT-Style Generic Text")
    print("=" * 80)
    chatgpt_text = """
    In today's rapidly evolving landscape, it is imperative to harness innovative 
    solutions that drive organizational excellence. This session will delve into 
    transformative strategies, exploring how emerging technologies can revolutionize 
    business processes. Furthermore, we will examine best practices and actionable 
    insights to empower stakeholders in their journey towards digital maturity.
    """
    
    ai_result = await evaluator.evaluate_ai_generation(chatgpt_text)
    orig_result = await evaluator.evaluate_originality(chatgpt_text)
    
    print(f"Text: {chatgpt_text[:100]}...")
    print(f"AI Probability: {ai_result['ai_probability']:.2f}")
    print(f"Genericness: {ai_result['genericness_score']:.2f}")
    print(f"Originality: {orig_result['originality_score']:.2f}")
    print()
    
    # Test 2: Specific technical text
    print("=" * 80)
    print("TEST 2: Specific Technical Text")
    print("=" * 80)
    technical_text = """
    We reduced PostgreSQL query time by 80% using partition pruning strategies 
    in our fintech platform handling 50M daily transactions. Our team built a 
    custom connection pooling solution that eliminated timeout errors. When we 
    implemented materialized views with incremental refresh, we discovered a 
    40% improvement in dashboard load times. Production metrics show 2ms average 
    query latency at peak load.
    """
    
    ai_result = await evaluator.evaluate_ai_generation(technical_text)
    orig_result = await evaluator.evaluate_originality(technical_text)
    
    print(f"Text: {technical_text[:100]}...")
    print(f"AI Probability: {ai_result['ai_probability']:.2f}")
    print(f"Genericness: {ai_result['genericness_score']:.2f}")
    print(f"Originality: {orig_result['originality_score']:.2f}")
    print()
    
    # Test 3: Buzzword-heavy text
    print("=" * 80)
    print("TEST 3: Buzzword-Heavy Text")
    print("=" * 80)
    buzzword_text = """
    This talk will explore cutting-edge, state-of-the-art solutions for leveraging 
    synergies in the cloud-native paradigm. Furthermore, we will delve into 
    comprehensive best practices for transformative digital transformation. 
    Moreover, this presentation will provide actionable insights and real-world 
    use cases that enable organizations to achieve robust, innovative results.
    """
    
    ai_result = await evaluator.evaluate_ai_generation(buzzword_text)
    orig_result = await evaluator.evaluate_originality(buzzword_text)
    
    print(f"Text: {buzzword_text[:100]}...")
    print(f"AI Probability: {ai_result['ai_probability']:.2f}")
    print(f"Genericness: {ai_result['genericness_score']:.2f}")
    print(f"Originality: {orig_result['originality_score']:.2f}")
    print()
    
    # Test 4: Simple introduction text
    print("=" * 80)
    print("TEST 4: Simple Introduction")
    print("=" * 80)
    simple_text = """
    An introduction to Python programming for beginners. This talk covers 
    variables, functions, and basic control flow.
    """
    
    ai_result = await evaluator.evaluate_ai_generation(simple_text)
    orig_result = await evaluator.evaluate_originality(simple_text)
    
    print(f"Text: {simple_text[:100]}...")
    print(f"AI Probability: {ai_result['ai_probability']:.2f}")
    print(f"Genericness: {ai_result['genericness_score']:.2f}")
    print(f"Originality: {orig_result['originality_score']:.2f}")
    print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print("If you see DIFFERENT scores for each test, the evaluator is working!")
    print("If all scores are the same, there's still an issue.")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_evaluator())
