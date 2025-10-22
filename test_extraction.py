#!/usr/bin/env python3
"""
Test script to verify the enhanced document extraction system
"""

import asyncio
import json
from enhanced_scenario_generator import FlexibleScenarioGenerator

async def test_extraction():
    """Test the extraction system with the filled.md document"""
    
    # Read the DOCX document using the existing extraction function
    from scenario_generator import extract_text_from_docx
    
    with open("Leadership Fundamentals and Styles.docx", "rb") as f:
        docx_content = f.read()
    
    document_content = await extract_text_from_docx(docx_content)
    
    if not document_content:
        print("Failed to extract content from DOCX")
        return
    
    print("TESTING ENHANCED EXTRACTION SYSTEM")
    print("=" * 50)
    
    # Initialize generator (without client for testing)
    generator = FlexibleScenarioGenerator(client=None)
    
    # Test raw data extraction
    print("\nStep 1: Raw Data Extraction")
    raw_data = generator._extract_raw_data(document_content)
    
    # Test template building
    print("\nStep 2: Template Building")
    template = generator._build_template_from_raw_data(raw_data)
    
    # Test validation
    print("\nStep 3: Validation")
    validation_result = await generator.validate_and_enhance_template(template)
    
    # Print results
    print("\nEXTRACTION RESULTS:")
    print("=" * 30)
    
    print(f"Completeness Score: {validation_result['validation_notes']['completeness_score']}%")
    print(f"Missing Elements: {validation_result['validation_notes']['missing_elements']}")
    print(f"Suggestions: {validation_result['validation_notes']['suggestions']}")
    
    print("\nKEY EXTRACTED DATA:")
    print(f"  Course: {template.get('scenario_understanding', {}).get('main_topic', 'Not found')}")
    print(f"  Expert Role: {template.get('participant_roles', {}).get('expert_role', 'Not found')}")
    print(f"  Practice Role: {template.get('participant_roles', {}).get('practice_role', 'Not found')}")
    print(f"  Target Skills: {len(template.get('scenario_understanding', {}).get('target_skills', []))} skills")
    print(f"  Knowledge DOS: {len(template.get('knowledge_base', {}).get('dos', []))} items")
    print(f"  Knowledge DONTS: {len(template.get('knowledge_base', {}).get('donts', []))} items")
    print(f"  Success Metrics: {len(template.get('success_metrics', {}).get('kpis_for_interaction', []))} metrics")
    
    # Save results for inspection
    with open("extraction_test_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "raw_data": raw_data,
            "template": template,
            "validation": validation_result
        }, f, indent=2, ensure_ascii=False)
    
    print(f"\nFull results saved to: extraction_test_results.json")
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_extraction())