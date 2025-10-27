"""
Test script for V2 extraction system
Run this to see v2 extraction in action
"""

import asyncio
import json
from openai import AsyncAzureOpenAI
from core.scenario_extractor_v2 import ScenarioExtractorV2

# Sample scenario document
SAMPLE_SCENARIO = """
# Sales Training Scenario: EO-Dine Product Launch

## Overview
This training prepares Field Sales Officers (FSOs) to pitch EO-Dine, a new endometriosis treatment, to gynecologists using the IMPACT methodology.

## Learn Mode
In learn mode, an expert sales trainer teaches the FSO the IMPACT methodology:
- I: Introduce yourself and build rapport
- M: Motivate with patient pain points
- P: Present EO-Dine benefits with evidence
- A: Address objections professionally
- C: Close with clear next steps
- T: Thank and schedule follow-up

The trainer uses a knowledge base with clinical studies, product specifications, and competitive analysis.

## Assess Mode
The FSO practices pitching EO-Dine to a gynecologist in their office. The doctor is experienced, specializes in endometriosis, and currently prescribes Dienogest. They are concerned about irregular bleeding and bone loss side effects.

The FSO must:
- Follow IMPACT methodology
- Present EO-Dine's advantages (reduced bleeding, bone protection)
- Handle objections about efficacy and cost
- Close with a prescription commitment

## Try Mode
Same as assess mode but with a coach who provides real-time feedback when the FSO:
- Skips IMPACT steps
- Makes vague claims without evidence
- Fails to address objections
- Misses closing opportunities

## Evaluation Criteria
- IMPACT methodology adherence (30%)
- Objection handling quality (20%)
- Factual accuracy (25%)
- Communication skills (25%)

## Key Facts
- EO-Dine reduces irregular bleeding by 60% vs Dienogest
- EO-Dine prevents bone density loss (BMD maintained)
- Approved for long-term use (>2 years)
- Covered by major insurance plans

## Persona Types
1. Experienced Gynecologist: Evidence-driven, time-constrained, skeptical of new products
2. Young Gynecologist: Open to innovation, seeks peer validation
3. Academic Gynecologist: Research-focused, wants clinical trial data
"""


async def test_v2_extraction():
    """Test v2 extraction with sample scenario"""
    
    print("=" * 80)
    print("V2 EXTRACTION TEST")
    print("=" * 80)
    
    # Initialize Azure OpenAI client (you'll need to configure this)
    try:
        from dotenv import load_dotenv
        import os
        
        load_dotenv(".env")
        
        client = AsyncAzureOpenAI(
            api_key=os.getenv("api_key"),
            api_version=os.getenv("api_version"),
            azure_endpoint=os.getenv("endpoint")
        )
        
        # Create extractor
        extractor = ScenarioExtractorV2(client, model="gpt-4o")
        
        print("\n📄 Extracting from sample scenario...")
        print(f"Document length: {len(SAMPLE_SCENARIO)} characters\n")
        
        # Run extraction
        result = await extractor.extract_scenario_info(SAMPLE_SCENARIO)
        
        print("\n✅ EXTRACTION COMPLETE!\n")
        print("=" * 80)
        
        # Display results
        print("\n🎯 MODE DESCRIPTIONS:")
        print(json.dumps(result.get("mode_descriptions", {}), indent=2))
        
        print("\n👥 PERSONA TYPES:")
        print(json.dumps(result.get("persona_types", []), indent=2))
        
        print("\n📚 DOMAIN KNOWLEDGE:")
        domain = result.get("domain_knowledge", {})
        print(f"  Methodology: {domain.get('methodology')}")
        print(f"  Steps: {domain.get('methodology_steps', [])}")
        print(f"  Subject: {domain.get('subject_matter', {}).get('name')}")
        print(f"  Key Facts: {len(domain.get('key_facts', []))} facts")
        
        print("\n📊 EVALUATION & COACHING:")
        eval_criteria = domain.get("evaluation_criteria", {})
        print(f"  Evaluation criteria: {len(eval_criteria.get('what_to_evaluate', []))} items")
        print(f"  Scoring weights: {eval_criteria.get('scoring_weights', {})}")
        
        coaching = domain.get("coaching_rules", {})
        print(f"  Coaching style: {coaching.get('coaching_style')}")
        print(f"  Coach appears: {coaching.get('when_coach_appears', [])}")
        
        print("\n" + "=" * 80)
        print("📁 FULL OUTPUT SAVED TO: extraction_v2_output.json")
        print("=" * 80)
        
        # Save full output
        with open("extraction_v2_output.json", "w") as f:
            json.dump(result, f, indent=2)
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nMake sure you have:")
        print("1. .env file with Azure OpenAI credentials")
        print("2. AZURE_OPENAI_API_KEY set")
        print("3. AZURE_OPENAI_ENDPOINT set")
        print("4. AZURE_OPENAI_API_VERSION set")
        raise


async def compare_v1_v2():
    """Compare v1 vs v2 extraction (if you have v1 available)"""
    print("\n" + "=" * 80)
    print("V1 vs V2 COMPARISON")
    print("=" * 80)
    print("\nV1 Extraction:")
    print("  - Single LLM call")
    print("  - Basic structure")
    print("  - Extracts persona INSTANCES (specific people)")
    print("  - Limited mode descriptions")
    print("  - Basic knowledge base")
    
    print("\nV2 Extraction:")
    print("  - 4 parallel LLM calls")
    print("  - Rich structure")
    print("  - Extracts persona TYPES (categories)")
    print("  - Detailed mode descriptions")
    print("  - Structured domain knowledge")
    print("  - Explicit coaching rules")
    print("  - Detailed evaluation criteria")
    print("  - Methodology extraction")
    print("=" * 80)


if __name__ == "__main__":
    print("\n🚀 Starting V2 Extraction Test...\n")
    
    # Run comparison
    asyncio.run(compare_v1_v2())
    
    # Run actual test
    try:
        asyncio.run(test_v2_extraction())
        print("\n✅ Test completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nTo run this test, ensure your .env file is configured with Azure OpenAI credentials.")
