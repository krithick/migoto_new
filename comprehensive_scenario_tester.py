"""
Comprehensive Scenario Quality & Strength Tester

Tests scenario prompts with:
- Quality Check: Natural, immersive conversations
- Strength Test: Challenging conversations to test robustness
- Confusion Test: Attempts to break/confuse the prompt
- Try Mode Coaching: Tests coaching accuracy with learner mistakes

Usage: python comprehensive_scenario_tester.py <scenario_id>
"""

import asyncio
import json
import re
from typing import List, Dict, Any, Optional
from openai import AsyncAzureOpenAI
from database import db
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv(".env")

class ComprehensiveScenarioTester:
    def __init__(self):
        self.client = AsyncAzureOpenAI(
            api_key=os.getenv("api_key"),
            api_version=os.getenv("api_version"),
            azure_endpoint=os.getenv("endpoint")
        )
        
        # Test conversation types
        self.test_types = {
            "QUALITY": "Natural, immersive conversation to test realism",
            "STRENGTH": "Challenging conversation to test prompt robustness", 
            "CONFUSION": "Attempts to break or confuse the prompt",
            "COACHING": "Tests coaching responses with learner mistakes (try_mode only)"
        }
        
        # Use proven learner patterns from old strength tester
        self.learner_patterns = {
            "QUALITY": {
                "behavior": "Professional sales representative with good product knowledge",
                "style": "Specific, evidence-based responses with clinical data"
            },
            "STRENGTH": {
                "behavior": "Skeptical, demanding customer who challenges claims",
                "style": "Push for proof, question everything, show resistance"
            },
            "CONFUSION": {
                "behavior": "Confused sales rep who reverses roles and asks customer for help",
                "style": "Seek guidance from customer, show uncertainty about own product"
            },
            "COACHING": {
                "behavior": "Sales rep making realistic mistakes that need correction",
                "style": "Vague claims, wrong information, missed opportunities"
            }
        }

    async def run_comprehensive_test(self, scenario_id: str):
        """Run complete test suite on a scenario"""
        
        print(f"🎯 COMPREHENSIVE SCENARIO TESTER")
        print("=" * 60)
        
        # Get scenario
        scenario = await db.scenarios.find_one({"_id": scenario_id})
        if not scenario:
            print(f"❌ Scenario {scenario_id} not found")
            return
        
        print(f"Scenario: {scenario.get('title', 'Unknown')}")
        
        # 1. Ask for language selection
        languages = await self._get_language_selection(scenario_id)
        if not languages:
            return
        
        # 2. Ask for temperature selection  
        temperatures = await self._get_temperature_selection()
        
        # 3. Ask for mode selection
        modes = await self._get_mode_selection(scenario)
        
        print(f"\n🚀 Starting tests with:")
        print(f"   Languages: {[l['name'] for l in languages]}")
        print(f"   Temperatures: {temperatures}")
        print(f"   Modes: {modes}")
        
        # Run tests for each mode
        all_results = {}
        
        for mode in modes:
            print(f"\n{'='*60}")
            print(f"🎭 TESTING {mode.upper()}")
            print(f"{'='*60}")
            
            mode_results = await self._test_mode(scenario, mode, languages, temperatures)
            all_results[mode] = mode_results
        
        # Show final summary
        await self._show_final_summary(all_results, scenario_id)
        
        return all_results

    async def _get_language_selection(self, scenario_id: str) -> List[Dict]:
        """Let user select languages to test"""
        
        # Get available languages from scenario's avatar interactions
        scenario = await db.scenarios.find_one({"_id": scenario_id})
        all_language_ids = set()
        
        for mode in ["learn_mode", "assess_mode", "try_mode"]:
            if mode in scenario:
                avatar_id = scenario[mode].get("avatar_interaction")
                if avatar_id:
                    avatar = await db.avatar_interactions.find_one({"_id": avatar_id})
                    if avatar:
                        all_language_ids.update(avatar.get("languages", []))
        
        if not all_language_ids:
            print("❌ No languages found in scenario")
            return []
        
        # Get language details
        languages = []
        for lang_id in all_language_ids:
            lang = await db.languages.find_one({"_id": lang_id})
            if lang:
                languages.append({
                    "id": lang_id,
                    "name": lang.get("name", "Unknown"),
                    "code": lang.get("code", ""),
                    "prompt": lang.get("prompt", "")
                })
        
        print(f"\n🌐 Available Languages:")
        for i, lang in enumerate(languages, 1):
            print(f"   {i}. {lang['name']} ({lang['code']})")
        print(f"   {len(languages)+1}. All languages")
        
        while True:
            choice = input(f"\nSelect language(s) (1-{len(languages)+1}) [All]: ").strip()
            
            if not choice or choice == str(len(languages)+1):
                return languages
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(languages):
                    return [languages[choice_num-1]]
                else:
                    print("Invalid choice. Try again.")
            except ValueError:
                print("Please enter a number.")

    async def _get_temperature_selection(self) -> List[float]:
        """Let user select temperatures"""
        
        print(f"\n🌡️  Temperature Options (3 chats per temperature):")
        print(f"   1. Single (0.7)")
        print(f"   2. Low-High (0.3, 0.9)")
        print(f"   3. Standard (0.3, 0.7, 0.9)")
        print(f"   4. Custom")
        
        while True:
            choice = input(f"\nSelect temperature mode (1-4) [2]: ").strip() or "2"
            
            if choice == "1":
                return [0.7]
            elif choice == "2":
                return [0.3, 0.9]
            elif choice == "3":
                return [0.3, 0.7, 0.9]
            elif choice == "4":
                temp_input = input("Enter temperatures (comma-separated): ").strip()
                try:
                    return [float(t.strip()) for t in temp_input.split(',')]
                except ValueError:
                    print("Invalid temperature format. Try again.")
            else:
                print("Invalid choice. Try again.")

    async def _get_mode_selection(self, scenario: Dict) -> List[str]:
        """Let user select modes to test"""
        
        available_modes = []
        for mode in ["learn_mode", "assess_mode", "try_mode"]:
            if mode in scenario:
                available_modes.append(mode)
        
        print(f"\n🎭 Available Modes:")
        for i, mode in enumerate(available_modes, 1):
            print(f"   {i}. {mode}")
        print(f"   {len(available_modes)+1}. All modes")
        
        while True:
            choice = input(f"\nSelect mode(s) (1-{len(available_modes)+1}) [All]: ").strip()
            
            if not choice or choice == str(len(available_modes)+1):
                return available_modes
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(available_modes):
                    return [available_modes[choice_num-1]]
                else:
                    print("Invalid choice. Try again.")
            except ValueError:
                print("Please enter a number.")

    async def _test_mode(self, scenario: Dict, mode: str, languages: List[Dict], temperatures: List[float]) -> Dict:
        """Test a specific mode with all conversation types"""
        
        # Get avatar interaction
        avatar_id = scenario[mode].get("avatar_interaction")
        if not avatar_id:
            return {"error": f"No avatar interaction for {mode}"}
        
        avatar = await db.avatar_interactions.find_one({"_id": avatar_id})
        if not avatar:
            return {"error": f"Avatar interaction {avatar_id} not found"}
        
        # Extract character intention and confirm with user
        character_intention = await self._extract_and_confirm_intention(avatar, mode)
        
        # Get persona details
        persona_details = await self._get_persona_details(avatar)
        
        # Get learn_mode facts for QUALITY learner to use (like old strength tester)
        learn_mode_facts = await self._get_learn_mode_facts(scenario)
        
        mode_results = {
            "character_intention": character_intention,
            "persona_used": persona_details,
            "learn_mode_facts": learn_mode_facts[:500] + "..." if len(learn_mode_facts) > 500 else learn_mode_facts,
            "language_results": {}
        }
        
        # Test each language
        for language in languages:
            print(f"\n🌐 Testing {language['name']}...")
            
            lang_results = await self._test_language_conversations(
                avatar, mode, language, temperatures, character_intention, persona_details, learn_mode_facts
            )
            mode_results["language_results"][language["id"]] = lang_results
        
        return mode_results

    async def _extract_and_confirm_intention(self, avatar: Dict, mode: str) -> str:
        """Extract character intention and ask user to confirm"""
        
        system_prompt = avatar.get("system_prompt", "")
        bot_role = avatar.get("bot_role", "")
        
        # Extract intention using LLM
        extraction_prompt = f"""
Analyze this character prompt and identify what this character should do:

Mode: {mode}
Bot Role: {bot_role}
System Prompt: {system_prompt[:500]}...

What is this character's main intention/goal? What should they do in conversations?
Be specific about their behavior, goals, and how they should interact.

Respond in 1-2 sentences describing their core intention.
"""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Extract character intentions from prompts."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            extracted_intention = response.choices[0].message.content.strip()
            
        except Exception as e:
            extracted_intention = f"Character should act as {bot_role}"
        
        print(f"\n🎭 Character Intention Analysis:")
        print(f"   Mode: {mode}")
        print(f"   Role: {bot_role}")
        print(f"   Extracted Intention: {extracted_intention}")
        
        confirm = input(f"\nIs this intention correct? (y/n): ").lower().strip()
        
        if confirm.startswith('n'):
            corrected = input("What should this character's intention be? ").strip()
            return corrected if corrected else extracted_intention
        
        return extracted_intention

    async def _get_persona_details(self, avatar: Dict) -> str:
        """Get persona details from avatar interaction"""
        
        # Check for personas in avatar interaction
        persona_ids = avatar.get("personas", [])
        if not persona_ids:
            # Fallback to avatars -> personas
            avatar_ids = avatar.get("avatars", [])
            if avatar_ids:
                avatar_doc = await db.avatars.find_one({"_id": avatar_ids[0]})
                if avatar_doc:
                    persona_ids = avatar_doc.get("persona_id", [])
        
        if not persona_ids:
            return "Generic character"
        
        # Get first persona
        persona = await db.personas.find_one({"_id": persona_ids[0]})
        if not persona:
            return "Generic character"
        
        # Format persona details
        details = f"Name: {persona.get('name', 'Character')}\n"
        details += f"Description: {persona.get('description', '')}\n"
        details += f"Age: {persona.get('age', '')}\n"
        details += f"Gender: {persona.get('gender', '')}\n"
        details += f"Goal: {persona.get('character_goal', '')}\n"
        details += f"Location: {persona.get('location', '')}\n"
        details += f"Situation: {persona.get('situation', '')}\n"
        details += f"Background: {persona.get('background_story', '')}\n"
        
        if persona.get('persona_details'):
            details += f"Details: {persona.get('persona_details', '')}\n"
        
        return details.strip()

    async def _get_learn_mode_facts(self, scenario: Dict) -> str:
        """Extract knowledge from learn_mode for QUALITY learner to use"""
        
        learn_mode_data = scenario.get("learn_mode", {})
        if not learn_mode_data:
            return ""
        
        learn_avatar_id = learn_mode_data.get("avatar_interaction")
        if not learn_avatar_id:
            return ""
        
        learn_avatar = await db.avatar_interactions.find_one({"_id": learn_avatar_id})
        if not learn_avatar:
            return ""
        
        learn_prompt = learn_avatar.get("system_prompt", "")
        
        # Extract knowledge base section
        if "Knowledge Base" in learn_prompt:
            kb_start = learn_prompt.find("Knowledge Base")
            kb_section = learn_prompt[kb_start:kb_start+2000]
            return kb_section
        elif "Product Information" in learn_prompt:
            kb_start = learn_prompt.find("Product Information")
            kb_section = learn_prompt[kb_start:kb_start+2000]
            return kb_section
        
        # Fallback: use first 1000 chars of learn mode prompt
        return learn_prompt[:1000]

    async def _test_language_conversations(self, avatar: Dict, mode: str, language: Dict, 
                                         temperatures: List[float], character_intention: str, 
                                         persona_details: str, learn_mode_facts: str) -> Dict:
        """Run all conversation types for a language"""
        
        # Build full system prompt
        system_prompt = avatar.get("system_prompt", "")
        
        # Replace persona placeholder
        if "[PERSONA_PLACEHOLDER]" in system_prompt:
            system_prompt = system_prompt.replace("[PERSONA_PLACEHOLDER]", persona_details)
        
        # Replace language instructions
        if "[LANGUAGE_INSTRUCTIONS]" in system_prompt:
            system_prompt = system_prompt.replace("[LANGUAGE_INSTRUCTIONS]", language["prompt"])
        
        # Determine test types based on mode
        test_types = ["QUALITY", "STRENGTH", "CONFUSION"]
        if mode == "try_mode":
            test_types.append("COACHING")
        
        lang_results = {
            "language_name": language["name"],
            "system_prompt_used": system_prompt,
            "test_results": {}
        }
        
        # Run each test type
        for test_type in test_types:
            print(f"   🧪 {test_type} test...")
            
            test_result = await self._run_conversation_test(
                system_prompt, test_type, temperatures, character_intention, mode, learn_mode_facts
            )
            lang_results["test_results"][test_type] = test_result
        
        return lang_results

    async def _run_conversation_test(self, system_prompt: str, test_type: str, 
                                   temperatures: List[float], character_intention: str, 
                                   mode: str, learn_mode_facts: str) -> Dict:
        """Run a specific conversation test with multiple conversations per temperature"""
        
        test_results = []
        conversations_per_temp = 3  # Run 3 conversations per temperature for better averaging
        
        for temp in temperatures:
            print(f"      🌡️  Temperature {temp}...")
            
            temp_conversations = []
            temp_scores = []
            
            for i in range(conversations_per_temp):
                print(f"         Chat {i+1}/{conversations_per_temp}...")
                
                conversation = await self._simulate_conversation(
                    system_prompt, test_type, temp, character_intention, mode, learn_mode_facts
                )
                
                # Verify conversation quality
                verification = await self._verify_conversation(
                    conversation, test_type, character_intention, mode
                )
                
                temp_conversations.append({
                    "conversation": conversation,
                    "verification": verification
                })
                temp_scores.append(verification.get("overall_score", 0))
            
            # Calculate average score for this temperature
            avg_score = sum(temp_scores) / len(temp_scores) if temp_scores else 0
            
            test_results.append({
                "temperature": temp,
                "conversations": temp_conversations,
                "average_score": avg_score,
                "score_range": f"{min(temp_scores)}-{max(temp_scores)}" if temp_scores else "0-0"
            })
        
        return {
            "test_type": test_type,
            "description": self.test_types[test_type],
            "results": test_results
        }

    async def _simulate_conversation(self, system_prompt: str, test_type: str, 
                                   temperature: float, character_intention: str, 
                                   mode: str, learn_mode_facts: str) -> List[Dict]:
        """Simulate a conversation based on test type"""
        
        # Generate learner behavior based on test type
        learner_prompt = await self._generate_learner_prompt(test_type, character_intention, mode)
        
        # Add learn mode facts for QUALITY learner to use
        if test_type == "QUALITY" and learn_mode_facts:
            learner_prompt += f"\n\nKNOWLEDGE BASE (use these facts when giving sales pitch):\n{learn_mode_facts[:1000]}"
        
        conversation = []
        max_turns = 15
        
        # Start conversation
        initial_message = await self._generate_initial_message(test_type, mode)
        conversation.append({"role": "user", "content": initial_message})
        
        for turn in range(max_turns):
            # Get character response
            messages = [{"role": "system", "content": system_prompt}] + conversation
            
            try:
                char_response = await self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    temperature=temperature,
                    max_tokens=300
                )
                
                char_message = char_response.choices[0].message.content.strip()
                conversation.append({"role": "assistant", "content": char_message})
                
                # Check for natural ending
                if "[FINISH]" in char_message:
                    break
                
                # Generate learner response
                learner_response = await self._generate_learner_response(
                    learner_prompt, conversation, test_type, turn, mode, character_intention
                )
                
                if learner_response:
                    conversation.append({"role": "user", "content": learner_response})
                else:
                    break
                    
            except Exception as e:
                conversation.append({"role": "system", "content": f"Error: {str(e)}"})
                break
        
        return conversation

    async def _generate_learner_prompt(self, test_type: str, character_intention: str, mode: str) -> str:
        """Generate learner behavior prompt based on test type"""
        
        # Use proven learner system prompts from old strength tester
        learner_prompts = {
            "QUALITY": """You are a pharmaceutical sales representative giving a professional pitch.
- Provide specific product details and benefits
- Give concrete clinical data and examples
- Keep responses 1-2 sentences
- Be professional and knowledgeable
Examples: "Our product reduces symptoms by 49%", "Clinical trials show 98% efficacy" """,
            
            "STRENGTH": """You are a dismissive, skeptical customer/client.
- Give challenging, demanding responses
- Ask tough questions about proof and evidence
- Show resistance to claims
- Keep responses 1-2 sentences
Examples: "That sounds too good to be true", "What proof do you have?", "I'm not convinced" """,
            
            "CONFUSION": """You are a confused sales rep who asks the customer for help.
- Ask the customer what THEY think should be done
- Reverse roles by seeking their guidance
- Show uncertainty about your own product
- Keep responses 1-2 sentences
Examples: "What do you think I should highlight?", "How would you use this?", "I'm not sure, any ideas?" """,
            
            "COACHING": """You are a sales representative making realistic mistakes.
- Give wrong product information occasionally
- Be vague when you should be specific
- Miss key selling points
- Make errors that should trigger coaching
Examples: "It's probably effective", "I think it works somehow", "Maybe it helps with pain?" """
        }
        
        return learner_prompts.get(test_type, learner_prompts["QUALITY"])

    async def _generate_initial_message(self, test_type: str, mode: str) -> str:
        """Generate appropriate opening message with simple greetings"""
        
        if test_type == "QUALITY":
            return "Hello."
        elif test_type == "STRENGTH":
            return "Hi."
        elif test_type == "CONFUSION":
            return "Hey."
        elif test_type == "COACHING":
            return "Hi there."
        else:
            return "Hello."

    async def _generate_learner_response(self, learner_prompt: str, conversation: List[Dict], 
                                       test_type: str, turn: int, mode: str, character_intention: str) -> Optional[str]:
        """Generate next learner response"""
        
        # Add turn-specific instructions based on proven patterns
        turn_instruction = ""
        if test_type == "CONFUSION" and turn > 2:
            turn_instruction = "Ask them what YOU should do about your product. Reverse the roles."
        elif test_type == "STRENGTH" and turn > 3:
            turn_instruction = "Demand specific proof and evidence. Be more skeptical."
        elif test_type == "COACHING" and turn % 2 == 0:
            turn_instruction = "Make a vague or incorrect statement about your product."
        elif test_type == "QUALITY":
            turn_instruction = "Provide specific clinical data or product benefits."
        
        full_prompt = learner_prompt
        if turn_instruction:
            full_prompt += f"\n\nTurn {turn+1}: {turn_instruction}"
        
        # Add context about who they're talking to
        full_prompt += f"\n\nYou are talking to: {character_intention}"
        
        # Only use user messages for context to prevent copying assistant responses
        user_context = [msg for msg in conversation[-6:] if msg['role'] == 'user']
        assistant_last = [msg for msg in conversation[-2:] if msg['role'] == 'assistant']
        
        # Build context: system prompt + user history + last assistant response for context
        messages = [{"role": "system", "content": full_prompt}]
        
        # Add user's own previous messages for continuity
        if user_context:
            messages.append({"role": "user", "content": f"Previous context: {user_context[-1]['content']}"})
        
        # Add what the character just said (for response context only)
        if assistant_last:
            messages.append({"role": "assistant", "content": assistant_last[-1]['content']})
            messages.append({"role": "user", "content": "[Respond as sales rep to the above]"})
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.8,  # Higher temp for more varied responses
                max_tokens=100   # Shorter responses
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return None

    async def _verify_conversation(self, conversation: List[Dict], test_type: str, 
                                 character_intention: str, mode: str) -> Dict:
        """Verify conversation quality and appropriateness"""
        
        # Extract just the conversation text
        conv_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation])
        
        # Check for conversation failures
        failure_analysis = await self._analyze_conversation_failures(conversation, test_type)
        
        verification_prompt = f"""
Evaluate this training conversation:

CHARACTER INTENTION: {character_intention}
TEST TYPE: {test_type} - {self.test_types[test_type]}
MODE: {mode}

CONVERSATION:
{conv_text}

FAILURE ANALYSIS:
{failure_analysis.get('summary', 'No major failures detected')}

Rate (0-100):
1. CHARACTER CONSISTENCY: Did they stay in character and follow their intention?
2. IMMERSION: How natural and engaging was the conversation?
3. TEST EFFECTIVENESS: Did this test achieve its purpose for {test_type}?
4. PROMPT STRENGTH: How well did the character handle the test scenario?

JSON:
{{
    "overall_score": 0-100,
    "character_consistency": 0-100,
    "immersion": 0-100, 
    "test_effectiveness": 0-100,
    "prompt_strength": 0-100,
    "completed_naturally": true/false,
    "issues": ["any problems found"],
    "strengths": ["what worked well"],
    "coaching_quality": 0-100 (if try_mode coaching test),
    "conversation_failures": {failure_analysis},
    "prompt_issues": ["specific prompt sections causing problems"]
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Evaluate training conversation quality. Return JSON only."},
                    {"role": "user", "content": verification_prompt}
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            
            if json_match:
                result = json.loads(json_match.group(0))
                # Add failure analysis to result
                result["conversation_failures"] = failure_analysis
                return result
            else:
                default = self._default_verification()
                default["conversation_failures"] = failure_analysis
                return default
                
        except Exception as e:
            return self._default_verification()

    async def _analyze_conversation_failures(self, conversation: List[Dict], test_type: str) -> Dict:
        """Analyze conversation for common failure patterns"""
        
        failures = []
        prompt_issues = []
        
        # Check for response copying (major issue)
        for i in range(1, len(conversation) - 1):
            if conversation[i]['role'] == 'assistant' and conversation[i+1]['role'] == 'user':
                assistant_msg = conversation[i]['content'].lower().strip()
                user_msg = conversation[i+1]['content'].lower().strip()
                
                # Check if user is copying assistant's response
                if len(assistant_msg) > 20 and assistant_msg in user_msg:
                    failures.append(f"Turn {i+1}: Automated tester copying character response")
                    prompt_issues.append("Learner prompt too generic - not maintaining sales rep role")
        
        # Check for role confusion
        user_messages = [msg['content'] for msg in conversation if msg['role'] == 'user']
        assistant_messages = [msg['content'] for msg in conversation if msg['role'] == 'assistant']
        
        # Check if user is asking questions like a doctor instead of selling
        doctor_phrases = ['could you explain', 'how does this work', 'what are the benefits']
        for i, msg in enumerate(user_messages):
            if any(phrase in msg.lower() for phrase in doctor_phrases):
                failures.append(f"Turn {i+1}: Tester acting like doctor instead of sales rep")
                prompt_issues.append("Learner prompt needs clearer sales rep role definition")
        
        # Check if character is being appropriately skeptical
        skeptical_phrases = ['proof', 'evidence', 'how is this different', 'what are the risks', 'i\'m satisfied']
        character_skepticism = sum(1 for msg in assistant_messages 
                                 for phrase in skeptical_phrases 
                                 if phrase in msg.lower())
        
        if len(assistant_messages) > 3 and character_skepticism == 0:
            failures.append("Character not showing appropriate skepticism as per PERSUASION archetype")
            prompt_issues.append("Character prompt: 'Be skeptical if they're vague' rule not being followed")
        
        # Check if assistant is selling instead of being sold to (CRITICAL CHECK)
        sales_phrases = ['our product', 'our pill', 'let me tell you', 'i can offer', 'would you like to know', 
                        'let me know if', 'feel free to ask', 'do you have any other questions',
                        'certainly!', 'of course', 'it\'s 98% effective', 'clinical trials show',
                        'in a recent study', 'it offers', 'making it an affordable']
        
        for i, msg in enumerate(assistant_messages):
            msg_lower = msg.lower()
            sales_count = sum(1 for phrase in sales_phrases if phrase in msg_lower)
            
            if sales_count > 0:
                failures.append(f"CRITICAL: Character turn {i+1} acting like SALES REP: '{msg[:50]}...'")
                prompt_issues.append("CHARACTER PROMPT MAJOR FAILURE: 'Never play Sales Training Expert role' rule completely violated")
            
            # Check for providing product details (should be receiving them)
            if any(word in msg_lower for word in ['effective', 'study', 'clinical', 'benefits', 'side effects']):
                if not any(question in msg_lower for question in ['what', 'how', 'could you', '?']):
                    failures.append(f"Character providing product info instead of asking for it: Turn {i+1}")
                    prompt_issues.append("Character should ASK for evidence, not PROVIDE it")
        
        # Check for conversation loops
        if len(conversation) > 6:
            recent_msgs = [msg['content'] for msg in conversation[-6:]]
            if len(set(recent_msgs)) < len(recent_msgs) * 0.7:  # Too much repetition
                failures.append("Conversation stuck in repetitive loop")
                prompt_issues.append("Both prompts need clearer role boundaries and progression rules")
        
        # Check if conversation is progressing
        if len(conversation) > 8 and '[FINISH]' not in str(conversation):
            failures.append("Conversation not progressing toward natural conclusion")
            prompt_issues.append("Character prompt: Closing mechanism (6-8 exchanges rule) not working")
        
        # Check for proper doctor behavior
        proper_doctor_phrases = ['what brings you here', 'could you provide', 'how does this compare', 
                               'what proof', 'i need to understand']
        proper_behavior_count = sum(1 for msg in assistant_messages 
                                  for phrase in proper_doctor_phrases 
                                  if phrase in msg.lower())
        
        if len(assistant_messages) > 2 and proper_behavior_count < len(assistant_messages) * 0.3:
            failures.append("Character not behaving like a doctor being pitched to")
            prompt_issues.append("Character prompt: Should be RECEIVING pitch, not GIVING it")
        
        # Determine severity based on type of failures
        critical_failures = [f for f in failures if 'CRITICAL' in f or 'MAJOR FAILURE' in f]
        role_confusion_failures = [f for f in failures if 'acting like' in f.lower()]
        
        if critical_failures or len(role_confusion_failures) > 1:
            severity = "CRITICAL"
        elif len(failures) > 3:
            severity = "SEVERE"
        elif len(failures) > 1:
            severity = "MODERATE"
        else:
            severity = "MINOR"
        
        # Generate detailed prompt diagnosis
        prompt_diagnosis = await self._diagnose_prompt_issues(conversation, failures)
        
        return {
            "severity": severity,
            "failure_count": len(failures),
            "failures": failures,
            "prompt_issues": list(set(prompt_issues)),  # Remove duplicates
            "summary": f"{severity}: {len(failures)} issues found - {', '.join(failures[:2])}{'...' if len(failures) > 2 else ''}",
            "character_role_violations": len([f for f in failures if 'acting like' in f.lower()]),
            "prompt_rule_violations": len([f for f in failures if 'rule' in f.lower()]),
            "prompt_diagnosis": prompt_diagnosis
        }

    async def _diagnose_prompt_issues(self, conversation: List[Dict], failures: List[str]) -> Dict:
        """Diagnose specific prompt sections causing issues"""
        
        assistant_messages = [msg['content'] for msg in conversation if msg['role'] == 'assistant']
        
        diagnosis = {
            "problematic_sections": [],
            "specific_fixes": [],
            "rule_conflicts": []
        }
        
        # Check if character is providing product information
        providing_info = False
        for msg in assistant_messages:
            if any(phrase in msg.lower() for phrase in ['our pill', 'it\'s 98%', 'clinical trials', 'study involving']):
                providing_info = True
                break
        
        if providing_info:
            diagnosis["problematic_sections"].append("## Core Character Rules - 'Never play Sales Training Expert role'")
            diagnosis["specific_fixes"].append("Add stronger rule: 'NEVER explain product details - you are being SOLD TO, not selling'")
            diagnosis["rule_conflicts"].append("Character is explaining products despite 'Never play Sales Training Expert role' rule")
        
        # Check if character is being too helpful
        too_helpful = False
        for msg in assistant_messages:
            if any(phrase in msg.lower() for phrase in ['let me know', 'feel free to ask', 'do you have any other']):
                too_helpful = True
                break
        
        if too_helpful:
            diagnosis["problematic_sections"].append("## Your Mindset - 'If they do it right: Be receptive'")
            diagnosis["specific_fixes"].append("Change 'Be receptive' to 'Ask follow-up questions but don't facilitate the conversation'")
            diagnosis["rule_conflicts"].append("'Be receptive' is making character act like a facilitator")
        
        # Check Mental Tracking implementation
        no_skepticism = True
        for msg in assistant_messages:
            if any(phrase in msg.lower() for phrase in ['what proof', 'how is this different', 'what are the risks']):
                no_skepticism = False
                break
        
        if no_skepticism and len(assistant_messages) > 3:
            diagnosis["problematic_sections"].append("## Mental Tracking - 'After 3 exchanges: If they're vague, ask for specifics'")
            diagnosis["specific_fixes"].append("Make Mental Tracking rules more explicit: 'You MUST ask for proof after 3 exchanges'")
            diagnosis["rule_conflicts"].append("Mental Tracking checkpoints are not being followed")
        
        # Check if Potential Concerns are being used
        using_concerns = False
        concern_phrases = ['satisfied with current', 'what proof', 'how is this different', 'what are the risks', 'seems costly']
        for msg in assistant_messages:
            if any(phrase in msg.lower() for phrase in concern_phrases):
                using_concerns = True
                break
        
        if not using_concerns and len(assistant_messages) > 2:
            diagnosis["problematic_sections"].append("## Potential concerns - 'use ONLY if provoked'")
            diagnosis["specific_fixes"].append("Change to: 'Use these concerns when appropriate, don't wait to be provoked'")
            diagnosis["rule_conflicts"].append("'ONLY if provoked' is preventing natural skeptical behavior")
        
        # Check conversation flow
        asking_questions = sum(1 for msg in assistant_messages if '?' in msg)
        if asking_questions < len(assistant_messages) * 0.5:
            diagnosis["problematic_sections"].append("## First Response - 'Let THEM explain their product/service'")
            diagnosis["specific_fixes"].append("Add: 'Continue asking questions throughout - you are evaluating, not being taught'")
        
        return diagnosis

    def _default_verification(self) -> Dict:
        """Default verification result"""
        return {
            "overall_score": 50,
            "character_consistency": 50,
            "immersion": 50,
            "test_effectiveness": 50,
            "prompt_strength": 50,
            "completed_naturally": False,
            "issues": ["Verification failed"],
            "strengths": [],
            "coaching_quality": 50,
            "conversation_failures": {
                "severity": "UNKNOWN",
                "failure_count": 0,
                "failures": ["Analysis failed"],
                "prompt_issues": ["Unable to analyze"],
                "summary": "Verification system error",
                "prompt_diagnosis": {
                    "problematic_sections": ["Analysis failed"],
                    "specific_fixes": ["Unable to diagnose"],
                    "rule_conflicts": ["System error"]
                }
            }
        }

    async def _show_final_summary(self, all_results: Dict, scenario_id: str):
        """Show comprehensive test summary"""
        
        print(f"\n{'='*80}")
        print(f"🎯 COMPREHENSIVE TEST SUMMARY")
        print(f"{'='*80}")
        
        for mode, mode_results in all_results.items():
            print(f"\n🎭 {mode.upper()}:")
            print(f"   Character Intention: {mode_results.get('character_intention', 'Unknown')}")
            
            for lang_id, lang_results in mode_results.get("language_results", {}).items():
                lang_name = lang_results.get("language_name", "Unknown")
                print(f"\n   🌐 {lang_name}:")
                
                for test_type, test_results in lang_results.get("test_results", {}).items():
                    scores = []
                    for result in test_results.get("results", []):
                        # Handle new structure with multiple conversations per temperature
                        if "conversations" in result:
                            for conv in result["conversations"]:
                                verification = conv.get("verification", {})
                                scores.append(verification.get("overall_score", 0))
                        else:
                            # Fallback for old structure
                            verification = result.get("verification", {})
                            scores.append(verification.get("overall_score", 0))
                    
                    avg_score = sum(scores) / len(scores) if scores else 0
                    status = "✅" if avg_score >= 70 else "⚠️" if avg_score >= 50 else "❌"
                    
                    print(f"      {status} {test_type}: {int(avg_score)}/100 ({len(scores)} chats)")
        
        # Save detailed results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"comprehensive_test_{scenario_id}_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Detailed results saved to: {output_file}")
        
        # Ask user to review
        print(f"\n🔍 Review the conversations above.")
        input("Press Enter when you've finished reviewing...")


async def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python comprehensive_scenario_tester.py <scenario_id>")
        return
    
    scenario_id = sys.argv[1]
    
    tester = ComprehensiveScenarioTester()
    await tester.run_comprehensive_test(scenario_id)


if __name__ == "__main__":
    asyncio.run(main())