"""
ADD THIS METHOD TO EnhancedScenarioGenerator CLASS in scenario_generator.py
Add after _get_mock_template_data() method (around line 1400)
"""

async def extract_scenario_info_v2(self, scenario_document: str) -> Dict[str, Any]:
    """
    V2 EXTRACTION: Enhanced multi-pass extraction system.
    Safe to call - has fallback to v1 if fails.
    """
    try:
        from core.scenario_extractor_v2 import ScenarioExtractorV2
        
        print("[V2 EXTRACTION] Starting enhanced extraction...")
        
        # Try V2 extraction
        extractor_v2 = ScenarioExtractorV2(self.client, self.model)
        template_data = await extractor_v2.extract_scenario_info(scenario_document)
        
        # Still run archetype classification (keep existing system)
        try:
            archetype_result = await self.archetype_classifier.classify_scenario(scenario_document, template_data)
            
            primary_archetype_str = str(archetype_result.primary_archetype).split(".")[-1] if archetype_result.primary_archetype else "HELP_SEEKING"
            
            template_data["archetype_classification"] = {
                "primary_archetype": primary_archetype_str,
                "confidence_score": archetype_result.confidence_score,
                "alternative_archetypes": archetype_result.alternative_archetypes,
                "reasoning": archetype_result.reasoning,
                "sub_type": archetype_result.sub_type
            }
            print(f"[V2] Classified as: {primary_archetype_str}")
        except Exception as e:
            print(f"[WARN] Archetype classification failed: {e}")
            template_data["archetype_classification"] = {
                "primary_archetype": "HELP_SEEKING",
                "confidence_score": 0.5,
                "alternative_archetypes": [],
                "reasoning": f"Classification failed: {str(e)}",
                "sub_type": None
            }
        
        # Inject archetype fields (keep existing system)
        self._inject_archetype_fields(template_data)
        
        print("[V2 EXTRACTION] Completed successfully")
        return template_data
        
    except Exception as e:
        print(f"[WARN] V2 extraction failed: {e}")
        print("[INFO] Falling back to V1 extraction")
        
        # Fallback to existing v1 method
        return await self.extract_scenario_info(scenario_document)
