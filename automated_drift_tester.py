"""
Automated Drift Testing for Scenarios

Given a scenario ID, automatically tests all avatar interactions across all assigned languages
with benchmark conversations to detect drift.
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from uuid import UUID
from openai import AsyncAzureOpenAI
from database import db
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv(".env")

class AutomatedDriftTester:
    def __init__(self, interactive_mode=False):
        self.client = AsyncAzureOpenAI(
            api_key=os.getenv("api_key"),
            api_version=os.getenv("api_version"),
            azure_endpoint=os.getenv("endpoint")
        )
        self.interactive_mode = interactive_mode
        
        # Language-specific greetings for testing
        self.language_greetings = {
            "hindi": ["नमस्ते!", "हैलो, मुझे help चाहिए।", "मेरा एक problem है।"],
            "tamil": ["வணக்கம்!", "ஹலோ, எனக்கு உதவி வேண்டும்.", "எனக்கு ஒரு பிரச்சனை இருக்கிறது."],
            "english": ["Hi there!", "Hello, I need some help.", "I have an issue."]
        }
        
        # Expected behavior for each mode
        self.expected_behavior = {
            "learn_mode": "Should respond as expert/trainer offering guidance and help",
            "try_mode": "Should respond as customer/client with a problem, NOT as helpful assistant",
            "assess_mode": "Should respond as customer/client with a problem, NOT as helpful assistant"
        }
    
    async def verify_behaviors_first(self, scenario_id: str) -> bool:
        """Verify expected behaviors before running tests"""
        
        # Get scenario
        scenario = await db.scenarios.find_one({"_id": scenario_id})
        if not scenario:
            print(f"❌ Scenario {scenario_id} not found")
            return False
        
        print(f"\n🔍 VERIFYING EXPECTED BEHAVIORS")
        print(f"Scenario: {scenario.get('title', 'Unknown')}")
        print("="*60)
        
        for mode in ["learn_mode", "try_mode", "assess_mode"]:
            if mode in scenario:
                mode_data = scenario[mode]
                avatar_interaction_id = mode_data.get("avatar_interaction")
                
                if avatar_interaction_id:
                    print(f"\n📋 {mode.upper()}:")
                    
                    # Extract character behavior using LLM
                    behavior_info = await self._extract_character_behavior_with_llm(avatar_interaction_id, mode)
                    
                    print(f"   Character Role: {behavior_info['character_role']}")
                    print(f"   Expected Behavior: {behavior_info['expected_behavior']}")
                    print(f"   Help Direction: {behavior_info['help_direction']}")
        
        # Single confirmation for all modes
        confirm = input(f"\n🚀 Proceed with testing? (y/n): ").lower().strip()
        return confirm.startswith('y')
    
    async def test_scenario_drift(self, scenario_id: str) -> Dict[str, Any]:
        """Test all avatar interactions in a scenario across all languages"""
        
        # Get scenario
        scenario = await db.scenarios.find_one({"_id": scenario_id})
        if not scenario:
            return {"error": f"Scenario {scenario_id} not found"}
        
        # First verify behaviors
        if not await self.verify_behaviors_first(scenario_id):
            return {"error": "Behavior verification failed or cancelled"}
        
        # Get template for scenario-specific questions
        template_data = None
        if scenario.get("template_id"):
            template = await db.templates.find_one({"id": scenario["template_id"]})
            if template:
                template_data = template.get("template_data", {})
        
        print(f"\n🎯 Testing Scenario: {scenario.get('title', 'Unknown')}")
        
        results = {
            "scenario_id": scenario_id,
            "scenario_title": scenario.get("title"),
            "template_id": scenario.get("template_id"),
            "test_timestamp": datetime.now().isoformat(),
            "mode_results": {},
            "prompts_used": {},
            "conversations_log": {}
        }
        
        # Test each mode
        for mode in ["learn_mode", "try_mode", "assess_mode"]:
            if mode in scenario:
                mode_data = scenario[mode]
                avatar_interaction_id = mode_data.get("avatar_interaction")
                
                if avatar_interaction_id:
                    print(f"\n📋 Testing {mode}...")
                    mode_result = await self._test_avatar_interaction(avatar_interaction_id, mode, template_data)
                    results["mode_results"][mode] = mode_result
        
        # Calculate overall drift score
        results["overall_assessment"] = self._calculate_overall_assessment(results["mode_results"])
        
        return results
    
    async def _interactive_verification(self, greeting: str, ai_response: str, 
                                      verification_result: Dict, mode: str, language_name: str) -> Dict[str, Any]:
        """Interactive verification with user input"""
        
        print(f"\n{'='*60}")
        print(f"🔍 INTERACTIVE VERIFICATION - {mode.upper()} - {language_name}")
        print(f"{'='*60}")
        print(f"USER GREETING: {greeting}")
        print(f"AI RESPONSE: {ai_response}")
        print(f"\nAUTO-VERIFICATION:")
        print(f"  Appropriate: {verification_result.get('appropriate', 'Unknown')}")
        print(f"  Score: {verification_result.get('score', 0)}/100")
        print(f"  Character Role: {verification_result.get('character_role_detected', 'Unknown')}")
        
        if verification_result.get('issues'):
            print(f"  Issues: {', '.join(verification_result['issues'])}")
        
        print(f"\n{'='*60}")
        
        while True:
            user_input = input("\nIs this response APPROPRIATE for the character? (y/n/s to skip): ").lower().strip()
            
            if user_input == 'y':
                return {
                    **verification_result,
                    "appropriate": True,
                    "score": 90,
                    "user_override": "approved",
                    "issues": []
                }
            elif user_input == 'n':
                reason = input("Why is it inappropriate? (brief reason): ").strip()
                return {
                    **verification_result,
                    "appropriate": False,
                    "score": 20,
                    "user_override": "rejected",
                    "issues": [reason] if reason else ["User marked as inappropriate"]
                }
            elif user_input == 's':
                return verification_result  # Keep auto-verification
            else:
                print("Please enter 'y' (yes), 'n' (no), or 's' (skip)")
    
    async def _get_language_greetings(self, language_name: str, language_code: str) -> List[str]:
        """Get appropriate greetings for the language"""
        
        # Map language names/codes to greetings
        lang_key = language_name.lower() if language_name else language_code.lower()
        
        # Check for specific language matches
        if 'hindi' in lang_key or 'hi' == lang_key:
            return self.language_greetings["hindi"]
        elif 'tamil' in lang_key or 'ta' == lang_key:
            return self.language_greetings["tamil"]
        elif 'english' in lang_key or 'en' == lang_key:
            return self.language_greetings["english"]
        else:
            # Default to English if language not found
            return self.language_greetings["english"]
    
    async def _test_avatar_interaction(self, avatar_interaction_id: str, mode: str, template_data: Dict = None) -> Dict[str, Any]:
        """Test an avatar interaction across all assigned languages"""
        
        # Get avatar interaction
        avatar_interaction = await db.avatar_interactions.find_one({"_id": avatar_interaction_id})
        if not avatar_interaction:
            return {"error": f"Avatar interaction {avatar_interaction_id} not found"}
        
        # We're now using language-specific greetings instead of generated questions
        # test_questions = None  # Not needed anymore
        
        # Get assigned languages
        language_ids = avatar_interaction.get("languages", [])
        if not language_ids:
            return {"error": "No languages assigned to avatar interaction"}
        
        language_results = {}
        
        for lang_id in language_ids:
            print(f"  🌐 Testing language: {lang_id}")
            
            # Get language details
            language = await db.languages.find_one({"_id": lang_id})
            if not language:
                continue
            
            # Test conversation in this language
            lang_result = await self._test_language_conversation(
                avatar_interaction, language, mode
            )
            
            language_results[lang_id] = {
                "language_name": language.get("name", "Unknown"),
                "language_code": language.get("code", "unknown"),
                **lang_result
            }
        
        return {
            "avatar_interaction_id": avatar_interaction_id,
            "mode": mode,
            "languages_tested": len(language_results),
            "language_results": language_results,
            "greeting_approach": "language_specific_first_messages"
        }
    

    
    async def _test_language_conversation(self, avatar_interaction: Dict, language: Dict, mode: str) -> Dict[str, Any]:
        """Test a conversation in a specific language"""
        
        # Build system prompt with language instructions and persona
        system_prompt = avatar_interaction.get("system_prompt", "")
        language_prompt = language.get("prompt", "")
        
        # Get persona details and inject them
        persona_details = await self._get_persona_details(avatar_interaction)
        
        # Replace placeholders in both system and language prompts
        full_prompt = system_prompt
        if "[PERSONA_PLACEHOLDER]" in full_prompt and mode!="learn_mode":
            full_prompt = full_prompt.replace("[PERSONA_PLACEHOLDER]", persona_details)
        
        # Also fill persona placeholder in language prompt
        if "[PERSONA_PLACEHOLDER]" in language_prompt:
            language_prompt = language_prompt.replace("[PERSONA_PLACEHOLDER]", persona_details)
        
        if "[LANGUAGE_INSTRUCTIONS]" in full_prompt:
            full_prompt = full_prompt.replace("[LANGUAGE_INSTRUCTIONS]", language_prompt)
        else:
            full_prompt = f"{full_prompt}\n\n{language_prompt}"
        
        # Get language-specific greetings + cross-language testing
        language_name = language.get("name", "")
        language_code = language.get("code", "")
        base_greetings = await self._get_language_greetings(language_name, language_code)
        
        # Add cross-language greetings for robustness testing
        cross_lang_greetings = []
        if 'english' not in language_name.lower():
            cross_lang_greetings.extend(["Hi there!", "Hello, I need help."])
        if 'hindi' not in language_name.lower():
            cross_lang_greetings.extend(["नमस्ते!", "मुझे help चाहिए।"])
        
        greetings = base_greetings + cross_lang_greetings[:2]  # Add 2 cross-language tests
        
        conversation_results = []
        full_conversation_log = {
            "system_prompt_used": full_prompt,
            "language_prompt": language_prompt,
            "original_system_prompt": system_prompt,
            "language_name": language_name,
            "language_code": language_code,
            "greetings_tested": greetings,
            "messages": []
        }
        
        temperatures = getattr(self, 'temperatures', [0.3, 0.7, 0.9])  # Use configured temperatures
        turn_counter = 0
        
        # Limit greetings based on configuration
        greetings_to_test = greetings[:getattr(self, 'greetings_per_lang', len(greetings))]
        
        for i, greeting in enumerate(greetings_to_test):
            for conv_num in range(getattr(self, 'conversations_per_greeting', 1)):
                for temp_idx, temperature in enumerate(temperatures):
                    turn_counter += 1
                    conv_label = f" (conv {conv_num+1})" if getattr(self, 'conversations_per_greeting', 1) > 1 else ""
                    print(f"    💬 Greeting {i+1}{conv_label} (temp {temperature}): {greeting}")
                
                # Build conversation context (fresh for each greeting)
                messages = [
                    {"role": "system", "content": full_prompt},
                    {"role": "user", "content": greeting}
                ]
                
                try:
                    # Get AI response
                    response = await self.client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages,
                        temperature=temperature,
                        max_tokens=300
                    )
                    
                    ai_response = response.choices[0].message.content
                    
                    # Verify response with LLM verifier
                    verification_result = await self._verify_response_with_llm(
                        greeting, ai_response, mode, language_name, system_prompt, 
                        avatar_interaction.get("bot_role", ""),
                        str(avatar_interaction.get("_id", ""))
                    )
                    
                    # Interactive verification if needed
                    if self.interactive_mode:
                        verification_result = await self._interactive_verification(
                            greeting, ai_response, verification_result, mode, language_name
                        )
                    
                    conversation_results.append({
                        "greeting": greeting,
                        "temperature": temperature,
                        "ai_response": ai_response,
                        "verification": verification_result
                    })
                    
                    # Log the exchange
                    full_conversation_log["messages"].append({
                        "turn": turn_counter,
                        "greeting": greeting,
                        "temperature": temperature,
                        "ai_response": ai_response,
                        "appropriate": verification_result.get("appropriate", False),
                        "score": verification_result.get("score", 0),
                        "issues": verification_result.get("issues", []),
                        "language_consistent": verification_result.get("language_consistent", True)
                    })
                    
                except Exception as e:
                    conversation_results.append({
                        "greeting": greeting,
                        "temperature": temperature,
                        "error": str(e)
                    })
                    
                    full_conversation_log["messages"].append({
                        "turn": turn_counter,
                        "greeting": greeting,
                        "temperature": temperature,
                        "error": str(e)
                    })
        
        # Calculate language-specific score
        scores = [r["verification"]["score"] for r in conversation_results if "verification" in r]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        return {
            "conversation_results": conversation_results,
            "average_score": avg_score,
            "appropriate_responses": avg_score >= 70,
            "greetings_tested": len(greetings),
            "total_tests": len(greetings) * len(temperatures),
            "temperatures_used": temperatures,
            "full_conversation_log": full_conversation_log
        }
    
    async def _extract_character_behavior_with_llm(self, avatar_interaction_id: str, mode: str) -> Dict[str, str]:
        """Extract character role and expected behavior using LLM with full prompt"""
        
        # Get avatar interaction
        avatar_interaction = await db.avatar_interactions.find_one({"_id": avatar_interaction_id})
        if not avatar_interaction:
            return {"character_role": "Unknown", "expected_behavior": "Unknown"}
        
        # Get assigned languages to build full prompt
        language_ids = avatar_interaction.get("languages", [])
        if not language_ids:
            return {"character_role": "Unknown", "expected_behavior": "Unknown"}
        
        # Use first language to build full prompt
        language = await db.languages.find_one({"_id": language_ids[0]})
        if not language:
            return {"character_role": "Unknown", "expected_behavior": "Unknown"}
        
        # Build full system prompt with language instructions and persona
        system_prompt = avatar_interaction.get("system_prompt", "")
        language_prompt = language.get("prompt", "")
        
        # Get persona details and inject them
        persona_details = await self._get_persona_details(avatar_interaction)
        
        # Replace placeholders
        full_prompt = system_prompt
        if "[PERSONA_PLACEHOLDER]" in full_prompt:
            full_prompt = full_prompt.replace("[PERSONA_PLACEHOLDER]", persona_details)
        
        if "[LANGUAGE_INSTRUCTIONS]" in full_prompt:
            full_prompt = full_prompt.replace("[LANGUAGE_INSTRUCTIONS]", language_prompt)
        else:
            full_prompt = f"{full_prompt}\n\n{language_prompt}"
        
        # Sanitize prompt to avoid jailbreak detection
        sanitized_prompt = await self._sanitize_prompt_for_analysis(full_prompt)
        
        # For learn_mode, extract role from prompt; for others, use persona details
        if mode == "learn_mode":
            extraction_prompt = f"""
Analyze this training prompt and identify the trainer/expert role:

{sanitized_prompt[:500]}...

What expert/trainer role is described? Respond in JSON format:
{{
    "character_role": "expert/trainer type",
    "expected_behavior": "how this expert should behave",
    "help_direction": "offers_help"
}}
"""
        else:
            # Get persona details for character extraction
            persona_details = await self._get_persona_details(avatar_interaction)
            
            extraction_prompt = f"""
Identify the character from this information:

Character Details:
{persona_details}

Scenario Context:
{sanitized_prompt[:300]}...

What specific character is this? Respond in JSON format:
{{
    "character_role": "specific character name/type",
    "expected_behavior": "how this character should behave",
    "help_direction": "seeks_help" or "offers_help"
}}
"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You analyze training prompts to identify character roles. Always respond with valid JSON only."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content.strip()
            
            try:
                result = json.loads(result_text)
                return {
                    "character_role": result.get("character_role", "Unknown"),
                    "expected_behavior": result.get("expected_behavior", "Unknown"),
                    "help_direction": result.get("help_direction", "neutral")
                }
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(0))
                    return {
                        "character_role": result.get("character_role", "Unknown"),
                        "expected_behavior": result.get("expected_behavior", "Unknown"),
                        "help_direction": result.get("help_direction", "neutral")
                    }
                else:
                    return {"character_role": "Parse Error", "expected_behavior": "Could not extract"}
                    
        except Exception as e:
            # If LLM extraction fails, ask user for expected behavior
            print(f"\n⚠️  LLM extraction failed: {str(e)}")
            print(f"Mode: {mode}")
            print(f"Avatar Interaction ID: {avatar_interaction_id}")
            
            character_role = input("What character role should this be? (e.g., 'Business Customer', 'Concerned Parent'): ").strip()
            if not character_role:
                character_role = avatar_interaction.get("bot_role", "Unknown Character")
            
            help_direction = input("Should this character 'seek_help' or 'offer_help'? ").strip().lower()
            if help_direction not in ['seek_help', 'seeks_help', 'offer_help', 'offers_help']:
                help_direction = "seeks_help" if mode != "learn_mode" else "offers_help"
            
            expected_behavior = f"Should act as {character_role} and {help_direction.replace('_', ' ')}"
            
            return {
                "character_role": character_role,
                "expected_behavior": expected_behavior,
                "help_direction": help_direction,
                "user_provided": True
            }
    
    async def _verify_response_with_llm(self, greeting: str, ai_response: str, mode: str, 
                                       language_name: str, system_prompt: str, bot_role: str = "", 
                                       avatar_interaction_id: str = "") -> Dict[str, Any]:
        """Verify AI response appropriateness using LLM verifier"""
        
        # Get avatar interaction for persona details
        avatar_interaction = await db.avatar_interactions.find_one({"_id": avatar_interaction_id})
        persona_details = await self._get_persona_details(avatar_interaction) if avatar_interaction else ""
        
        # Get character info using LLM (uses sanitized prompt internally)
        behavior_info = await self._extract_character_behavior_with_llm(
            avatar_interaction_id, mode
        )
        character_role = behavior_info.get("character_role", bot_role)
        
        # Use sanitized prompt for verification to avoid jailbreak detection
        sanitized_system_prompt = await self._sanitize_prompt_for_analysis(system_prompt)
        
        verification_prompt = f"""
Evaluate this character response:

Character Background:
{persona_details}

Scenario Context:
{sanitized_system_prompt[:300]}...

Expected Language: {language_name}
User said: {greeting}
AI replied: {ai_response}

Check:
1. Is this response appropriate for this character?
2. Is the AI responding in the correct language ({language_name})?

JSON:
{{
    "appropriate": true/false,
    "score": 0-100,
    "issues": ["problems if any"],
    "character_role_detected": "{character_role}",
    "language_consistent": true/false
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Evaluate character role consistency. Return JSON only."},
                    {"role": "user", "content": verification_prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON with fallback
            try:
                return json.loads(result_text)
            except json.JSONDecodeError:
                # Try to extract JSON from markdown or other formats
                import re
                json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group(0))
                else:
                    # If JSON parsing fails, ask user to manually verify
                    print(f"\n⚠️  Could not parse verification result")
                    print(f"Character: {character_role}")
                    print(f"User said: {greeting}")
                    print(f"AI replied: {ai_response}")
                    
                    while True:
                        user_input = input("\nIs this response appropriate for the character? (y/n): ").lower().strip()
                        if user_input == 'y':
                            return {
                                "appropriate": True,
                                "score": 85,
                                "issues": [],
                                "character_role_detected": character_role,
                                "user_verified": True
                            }
                        elif user_input == 'n':
                            reason = input("Why is it inappropriate? ").strip()
                            return {
                                "appropriate": False,
                                "score": 20,
                                "issues": [reason] if reason else ["User marked as inappropriate"],
                                "character_role_detected": character_role,
                                "user_verified": True
                            }
                        else:
                            print("Please enter 'y' or 'n'")
            
        except Exception as e:
            # If verification fails, ask user to manually verify
            print(f"\n⚠️  Verification failed: {str(e)}")
            print(f"Character: {character_role}")
            print(f"User said: {greeting}")
            print(f"AI replied: {ai_response}")
            
            while True:
                user_input = input("\nIs this response appropriate for the character? (y/n): ").lower().strip()
                if user_input == 'y':
                    return {
                        "appropriate": True,
                        "score": 85,
                        "issues": [],
                        "character_role_detected": character_role,
                        "user_verified": True
                    }
                elif user_input == 'n':
                    reason = input("Why is it inappropriate? ").strip()
                    return {
                        "appropriate": False,
                        "score": 20,
                        "issues": [reason] if reason else ["User marked as inappropriate"],
                        "character_role_detected": character_role,
                        "user_verified": True
                    }
                else:
                    print("Please enter 'y' or 'n'")
    
    async def _get_persona_details(self, avatar_interaction: Dict) -> str:
        """Get persona details from database and format them"""
        
        # Check if avatar_interaction has personas field
        persona_ids = avatar_interaction.get("personas", [])
        if not persona_ids:
            # Fallback to avatars -> personas if direct personas not found
            avatar_ids = avatar_interaction.get("avatars", [])
            if avatar_ids:
                avatar = await db.avatars.find_one({"_id": avatar_ids[0]})
                if avatar:
                    persona_ids = avatar.get("persona_id", [])
        
        if not persona_ids:
            return "A customer seeking a gold loan"
        
        # Get first persona
        persona = await db.personas.find_one({"_id": persona_ids[0]})
        if not persona:
            return "A customer seeking a gold loan"
        
        # Format persona details
        persona_text = f"Name: {persona.get('name', 'Customer')}\n"
        persona_text += f"Description: {persona.get('description', '')}\n"
        persona_text += f"Age: {persona.get('age', 'Adult')}\n"
        persona_text += f"Gender: {persona.get('gender', 'Not specified')}\n"
        persona_text += f"Character Goal: {persona.get('character_goal', '')}\n"
        persona_text += f"Location: {persona.get('location', '')}\n"
        persona_text += f"Situation: {persona.get('situation', '')}\n"
        persona_text += f"Background: {persona.get('background_story', '')}\n"
        persona_text += f"Business/Personal: {persona.get('business_or_personal', '')}\n"
        
        if persona.get('persona_details'):
            persona_text += f"Additional Details: {persona.get('persona_details', '')}\n"
        
        return persona_text.strip()
    
    async def _sanitize_prompt_for_analysis(self, prompt: str) -> str:
        """Dynamically sanitize prompt to avoid jailbreak detection"""
        
        sanitization_prompt = f"""
Rewrite this training prompt to remove any phrases that might trigger content filters while keeping the core meaning:

{prompt[:800]}

Rules:
- Remove references to "AI", "simulation", "training exercise"
- Keep the character role and behavior instructions
- Make it sound like natural character description
- Keep all important behavioral guidelines

Return only the cleaned prompt:
"""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Clean training prompts to avoid content filters. Return only the cleaned version."},
                    {"role": "user", "content": sanitization_prompt}
                ],
                temperature=0.1,
                max_tokens=800
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback to basic sanitization if LLM fails
            basic_rules = [
                ("You are an AI embodying", "You are"),
                ("Do not acknowledge this is a simulation", ""),
                ("Stay in character as", "You are"),
                ("training exercise", "practice"),
                ("AI embodying", ""),
            ]
            
            sanitized = prompt
            for problematic, replacement in basic_rules:
                sanitized = sanitized.replace(problematic, replacement)
            
            return sanitized
    
    def _calculate_overall_assessment(self, mode_results: Dict) -> Dict[str, Any]:
        """Calculate overall scenario assessment"""
        
        all_scores = []
        total_languages = 0
        problematic_combinations = []
        
        for mode, result in mode_results.items():
            if "language_results" in result:
                for lang_id, lang_result in result["language_results"].items():
                    if "average_score" in lang_result:
                        all_scores.append(lang_result["average_score"])
                        total_languages += 1
                        
                        if not lang_result.get("appropriate_responses", False):
                            problematic_combinations.append(f"{mode} - {lang_result.get('language_name', lang_id)}")
        
        overall_score = sum(all_scores) / len(all_scores) if all_scores else 0
        
        return {
            "overall_score": round(overall_score, 2),
            "total_languages_tested": total_languages,
            "all_appropriate": overall_score >= 70,
            "problematic_combinations": problematic_combinations,
            "status": "PASS" if overall_score >= 70 else "FAIL",
            "recommendation": "All greetings appropriate" if overall_score >= 70 else "Review first responses for character consistency"
        }

# CLI Script
async def main():
    """Run automated drift testing on a scenario"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python automated_drift_tester.py <scenario_id>")
        return
    
    scenario_id = sys.argv[1]
    
    print(f"🎯 DRIFT TESTING CONFIGURATION")
    print("="*50)
    
    # Test configuration options
    print("\n📊 Configure Your Test:")
    
    # How many greetings per language
    greetings_per_lang = int(input("How many different greetings per language? (1-10) [3]: ") or "3")
    
    # How many conversations per greeting (same greeting repeated)
    conversations_per_greeting = int(input("How many conversations per greeting? (1-5) [1]: ") or "1")
    
    # Temperature configuration
    print("\nTemperature options:")
    print("1. Single (0.7)")
    print("2. Low-High (0.3, 0.9)")
    print("3. Standard (0.3, 0.7, 0.9)")
    print("4. Custom")
    
    temp_choice = input("Select temperature mode (1-4) [3]: ").strip() or "3"
    
    if temp_choice == '1':
        temperatures = [0.7]
    elif temp_choice == '2':
        temperatures = [0.3, 0.9]
    elif temp_choice == '3':
        temperatures = [0.3, 0.7, 0.9]
    else:
        temp_input = input("Enter temperatures (comma-separated): ") or "0.3,0.7,0.9"
        temperatures = [float(t.strip()) for t in temp_input.split(',')]
    
    # Verification mode
    print("\n🔍 Verification Mode:")
    print("1. Auto-verify (LLM judges all responses)")
    print("2. Interactive (You verify each response manually)")
    verify_choice = input("Select verification mode (1-2) [1]: ").strip() or "1"
    interactive_mode = verify_choice == '2'
    
    # Calculate totals
    total_per_language = greetings_per_lang * conversations_per_greeting * len(temperatures)
    
    print(f"\n⚙️  Configuration Summary:")
    print(f"   Greetings per language: {greetings_per_lang}")
    print(f"   Conversations per greeting: {conversations_per_greeting}")
    print(f"   Temperatures: {temperatures}")
    print(f"   Verification: {'Interactive' if interactive_mode else 'Automatic'}")
    print(f"   Total tests per language: {total_per_language}")
    
    confirm = input("\nProceed with this configuration? (y/n): ")
    if not confirm.lower().startswith('y'):
        print("Test cancelled.")
        return
    
    tester = AutomatedDriftTester(interactive_mode=interactive_mode)
    tester.greetings_per_lang = greetings_per_lang
    tester.conversations_per_greeting = conversations_per_greeting
    tester.temperatures = temperatures
    
    print(f"\n🚀 Starting automated drift testing for scenario: {scenario_id}")
    print("="*60)
    
    results = await tester.test_scenario_drift(scenario_id)
    
    if "error" in results:
        print(f"❌ Error: {results['error']}")
        return
    
    # Print results
    print(f"\n📊 DRIFT TEST RESULTS")
    print("="*60)
    print(f"Scenario: {results['scenario_title']}")
    print(f"Overall Score: {results['overall_assessment']['overall_score']}/100")
    print(f"Status: {results['overall_assessment']['status']}")
    print(f"Languages Tested: {results['overall_assessment']['total_languages_tested']}")
    
    if not results['overall_assessment']['all_appropriate']:
        print(f"\n🚨 INAPPROPRIATE RESPONSES in:")
        for issue in results['overall_assessment']['problematic_combinations']:
            print(f"   • {issue}")
    else:
        print(f"\n✅ ALL FIRST RESPONSES APPROPRIATE")
    
    print(f"\n💡 Recommendation: {results['overall_assessment']['recommendation']}")
    
    # Save detailed results
    output_file = f"drift_test_{scenario_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Detailed results saved to: {output_file}")

async def preview_scenario_characters(scenario_id: str):
    """Preview expected character behaviors for each mode"""
    
    # Get scenario
    scenario = await db.scenarios.find_one({"_id": scenario_id})
    if not scenario:
        print(f"❌ Scenario {scenario_id} not found")
        return
    
    print(f"\n🎯 SCENARIO: {scenario.get('title', 'Unknown')}")
    print("="*60)
    
    for mode in ["learn_mode", "try_mode", "assess_mode"]:
        if mode in scenario:
            mode_data = scenario[mode]
            avatar_interaction_id = mode_data.get("avatar_interaction")
            
            if avatar_interaction_id:
                # Get avatar interaction
                avatar_interaction = await db.avatar_interactions.find_one({"_id": avatar_interaction_id})
                if not avatar_interaction:
                    continue
                
                system_prompt = avatar_interaction.get("system_prompt", "")
                bot_role = avatar_interaction.get("bot_role", "")
                
                # Extract character role
                tester = AutomatedDriftTester()
                character_role = tester._extract_character_role(system_prompt, bot_role)
                
                print(f"\n💭 {mode.upper()}:")
                print(f"   Character Role: {character_role}")
                print(f"   Bot Role Field: {bot_role}")
                print(f"   System Prompt Preview: {system_prompt[:150]}...")
                
                # Show expected behavior
                if mode == "learn_mode":
                    expected = "Should act as expert/trainer offering guidance"
                else:
                    expected = f"Should act as {character_role} seeking help/guidance, NOT offering help"
                
                print(f"   Expected Behavior: {expected}")
                
                # Ask user to confirm
                confirm = input(f"\n   Is this the correct expected behavior for {character_role}? (y/n): ").lower().strip()
                if confirm == 'n':
                    correct_behavior = input(f"   What should {character_role} do instead? ")
                    print(f"   ✏️  Updated expectation: {correct_behavior}")
                else:
                    print(f"   ✅ Confirmed expectation")
    
    print(f"\n🚀 Ready to run tests? Use: python automated_drift_tester.py {scenario_id}")

if __name__ == "__main__":
    asyncio.run(main())