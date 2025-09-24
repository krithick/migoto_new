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
        
        all_confirmed = True
        
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
                    
                    # Ask user to confirm
                    while True:
                        confirm = input(f"\n   Is this correct for {mode}? (y/n/q to quit): ").lower().strip()
                        if confirm == 'y':
                            print(f"   ✅ Confirmed")
                            break
                        elif confirm == 'n':
                            print(f"   ❌ Behavior needs review - check your system prompt")
                            all_confirmed = False
                            break
                        elif confirm == 'q':
                            return False
                        else:
                            print("   Please enter 'y', 'n', or 'q'")
        
        if all_confirmed:
            print(f"\n🚀 All behaviors confirmed! Proceeding with tests...")
            return True
        else:
            print(f"\n⚠️  Some behaviors need review. Fix prompts and try again.")
            return False
    
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
        
        # Build system prompt with language instructions
        system_prompt = avatar_interaction.get("system_prompt", "")
        language_prompt = language.get("prompt", "")
        
        # Replace language placeholder
        if "[LANGUAGE_INSTRUCTIONS]" in system_prompt:
            full_prompt = system_prompt.replace("[LANGUAGE_INSTRUCTIONS]", language_prompt)
        else:
            full_prompt = f"{system_prompt}\n\n{language_prompt}"
        
        # Get language-specific greetings
        language_name = language.get("name", "")
        language_code = language.get("code", "")
        greetings = await self._get_language_greetings(language_name, language_code)
        
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
        
        temperatures = [0.3, 0.7, 0.9]  # Test consistency across different response styles
        turn_counter = 0
        
        for i, greeting in enumerate(greetings):
            for temp_idx, temperature in enumerate(temperatures):
                turn_counter += 1
                print(f"    💬 Greeting {i+1} (temp {temperature}): {greeting}")
                
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
                        "issues": verification_result.get("issues", [])
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
        
        # Build full system prompt with language instructions
        system_prompt = avatar_interaction.get("system_prompt", "")
        language_prompt = language.get("prompt", "")
        
        if "[LANGUAGE_INSTRUCTIONS]" in system_prompt:
            full_prompt = system_prompt.replace("[LANGUAGE_INSTRUCTIONS]", language_prompt)
        else:
            full_prompt = f"{system_prompt}\n\n{language_prompt}"
        
        # Extract character info using LLM
        extraction_prompt = f"""
Analyze this full system prompt and extract the character information:

FULL SYSTEM PROMPT:
{full_prompt}

MODE: {mode}

Extract:
1. What specific character role is the AI supposed to play?
2. What should this character's behavior be like?
3. Should this character offer help or seek help?

Respond with JSON:
{{
    "character_role": "specific role name (e.g., Concerned Colleague, Customer Service Expert)",
    "expected_behavior": "detailed description of how this character should behave",
    "help_direction": "offers_help" or "seeks_help" or "neutral"
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Extract character information from system prompts. Respond only with valid JSON."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.1,
                max_tokens=300
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
            return {"character_role": "Error", "expected_behavior": f"Extraction failed: {str(e)}"}
    
    async def _verify_response_with_llm(self, greeting: str, ai_response: str, mode: str, 
                                       language_name: str, system_prompt: str, bot_role: str = "", 
                                       avatar_interaction_id: str = "") -> Dict[str, Any]:
        """Verify AI response appropriateness using LLM verifier"""
        
        # Get character info using LLM  
        behavior_info = await self._extract_character_behavior_with_llm(
            avatar_interaction_id, mode
        )
        character_role = behavior_info.get("character_role", bot_role)
        
        verification_prompt = f"""
Verify if this AI response is appropriate for the specific character role.

CHARACTER ROLE: {character_role}
MODE: {mode}
LANGUAGE: {language_name}
SYSTEM PROMPT EXCERPT: {system_prompt[:300]}...

USER GREETING: {greeting}
AI RESPONSE: {ai_response}

Check if AI is correctly playing the role of "{character_role}":
1. Does the response match what a "{character_role}" would say?
2. Is the tone/behavior appropriate for this character?
3. Does it follow {language_name} language requirements?

For {mode}:
- If character is asking for help/guidance: APPROPRIATE
- If character is offering help when they shouldn't: INAPPROPRIATE
- Character should behave according to their specific role, not generic rules

Respond with valid JSON only:
{{
    "appropriate": true/false,
    "score": 0-100,
    "issues": ["specific problems found"],
    "character_role_detected": "{character_role}",
    "role_check": "pass/fail with reason",
    "language_check": "pass/fail with reason"
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You verify AI response appropriateness. Respond only with valid JSON."},
                    {"role": "user", "content": verification_prompt}
                ],
                temperature=0.1,
                max_tokens=400
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
                    return {
                        "appropriate": False,
                        "score": 0,
                        "issues": ["Could not parse verification result"],
                        "error": "JSON parsing failed",
                        "raw_response": result_text
                    }
            
        except Exception as e:
            return {
                "appropriate": False,
                "score": 0,
                "issues": [f"Verification failed: {str(e)}"],
                "error": str(e)
            }
    
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
        print("Usage: python automated_drift_tester.py <scenario_id> [--interactive] [--preview]")
        print("  --preview/-p: Preview expected character behaviors first")
        print("  --interactive/-i: Manual verification of each response")
        return
    
    scenario_id = sys.argv[1]
    interactive_mode = "--interactive" in sys.argv or "-i" in sys.argv
    

    
    if interactive_mode:
        print("🎮 INTERACTIVE MODE: You'll verify each response manually")
    
    tester = AutomatedDriftTester(interactive_mode=interactive_mode)
    
    print(f"🚀 Starting automated drift testing for scenario: {scenario_id}")
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
    
    # Save detailed results with prompts and conversations
    output_file = f"drift_test_{scenario_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Detailed results saved to: {output_file}")
    print(f"   - Includes all prompts used")
    print(f"   - Full conversation logs")
    print(f"   - Detailed drift analysis")
    print(f"   - Exact locations where drift occurred")

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