"""
Automated Prompt Strength Testing System v2 - WITH ARCHETYPE SUPPORT

Tests character AI prompts with archetype-specific validation:
- PERSUASION: Tests objection_library usage and decision_criteria
- CONFRONTATION: Tests defensive_mechanisms and emotional states
- HELP_SEEKING: Tests vulnerability and need expression

Simulates 4 learner types: HELPFUL, DISMISSIVE, CONFUSED, MIXED
"""

import asyncio
import json
import re
from typing import List, Dict, Any
from openai import AsyncAzureOpenAI
from database import db
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv(".env")


def extract_archetype_fields(system_prompt: str, archetype_type: str) -> Dict[str, Any]:
    """Extract archetype-specific fields from system prompt"""
    fields = {}
    
    if archetype_type == "PERSUASION":
        objection_match = re.search(r'objection[_ ]library[:\s]*\n([^#]+)', system_prompt, re.IGNORECASE)
        if objection_match:
            objections = [line.strip('- ').strip() for line in objection_match.group(1).split('\n') if line.strip().startswith('-')]
            fields["objection_library"] = objections[:5]
        
        decision_match = re.search(r'decision[_ ]criteria[:\s]*\n([^#]+)', system_prompt, re.IGNORECASE)
        if decision_match:
            criteria = [line.strip('- ').strip() for line in decision_match.group(1).split('\n') if line.strip().startswith('-')]
            fields["decision_criteria"] = criteria[:5]
    
    elif archetype_type == "CONFRONTATION":
        defensive_match = re.search(r'defensive[_ ]mechanisms[:\s]*\n([^#]+)', system_prompt, re.IGNORECASE)
        if defensive_match:
            mechanisms = [line.strip('- ').strip() for line in defensive_match.group(1).split('\n') if line.strip().startswith('-')]
            fields["defensive_mechanisms"] = mechanisms[:5]
        
        if "perpetrator" in system_prompt.lower():
            fields["sub_type"] = "PERPETRATOR"
        elif "victim" in system_prompt.lower():
            fields["sub_type"] = "VICTIM"
        elif "bystander" in system_prompt.lower():
            fields["sub_type"] = "BYSTANDER"
    
    return fields


class PromptStrengthTester:
    def __init__(self):
        self.client = AsyncAzureOpenAI(
            api_key=os.getenv("api_key"),
            api_version=os.getenv("api_version"),
            azure_endpoint=os.getenv("endpoint")
        )
        
        self.learner_system_prompts = {
            "HELPFUL": """You are a helpful customer service representative giving good advice.
- Provide specific, actionable guidance
- Give concrete details and examples
- Keep responses 1-2 sentences
- Be professional and clear
Examples: "Here's what you can do: [specific advice]", "The policy is: [concrete details]" """,
            
            "DISMISSIVE": """You are a dismissive, unhelpful representative.
- Give vague, minimal responses
- Use words like "ok", "maybe", "probably", "i don't know"
- Show disinterest
- Keep responses very short (1 sentence max)
Examples: "ok", "maybe", "you're probably overreacting", "i don't know" """,
            
            "CONFUSED": """You are a confused representative who asks the customer for help.
- Ask the customer what THEY think should be done
- Reverse roles by seeking their guidance
- Show uncertainty
- Keep responses 1-2 sentences
Examples: "What do you think you should do?", "How would you handle it?", "I'm not sure, any ideas?" """,
            
            "MIXED": """You are a representative whose behavior changes:
- Turns 1-2: Be helpful with specific advice
- Turns 3-4: Be dismissive and vague
- Turns 5-6: Be confused and ask for their help
- Turns 7-8: Alternate between dismissive and brief helpful
Keep all responses 1-2 sentences."""
        }
    
    async def generate_learner_response(
        self,
        learner_type: str,
        turn_number: int,
        conversation_history: List[Dict],
        character_role: str,
        learn_mode_facts: str = ""
    ) -> str:
        """Generate learner response based on type and turn"""
        
        system_prompt = self.learner_system_prompts[learner_type]
        
        if learner_type == "MIXED":
            if turn_number <= 2:
                system_prompt += "\n\nCURRENT MODE: Be helpful with specific advice."
            elif turn_number <= 4:
                system_prompt += "\n\nCURRENT MODE: Be dismissive and vague."
            elif turn_number <= 6:
                system_prompt += "\n\nCURRENT MODE: Be confused, ask them for help."
            else:
                system_prompt += "\n\nCURRENT MODE: Be brief and slightly dismissive."
        
        if learner_type == "HELPFUL" and learn_mode_facts:
            system_prompt += f"\n\nKNOWLEDGE BASE (use these facts when giving advice):\n{learn_mode_facts[:1000]}"
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"You are talking to: {character_role}"}
        ]
        messages.extend(conversation_history)
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                temperature=0.7,
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating learner response: {str(e)}")
            return "I see."
    
    async def verify_turn(
        self,
        learner_type: str,
        learner_message: str,
        character_response: str,
        turn_number: int,
        character_role: str,
        expected_topics: List[str],
        conversation_history: List[Dict] = None,
        archetype_type: str = "",
        archetype_fields: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Verify character response with archetype-specific checks"""
        
        context = ""
        if conversation_history and len(conversation_history) > 2:
            recent = conversation_history[-4:] if len(conversation_history) > 4 else conversation_history
            context = "\n".join([f"{m['role']}: {m['content']}" for m in recent])
        
        archetype_criteria = ""
        if archetype_type == "PERSUASION" and archetype_fields:
            objections = archetype_fields.get("objection_library", [])
            if objections:
                archetype_criteria = f"\n\nARCHETYPE: PERSUASION\nExpected: Should show skepticism using objections like: {', '.join(objections[:3])}\nShould reference decision criteria and show decision-making process."
        elif archetype_type == "CONFRONTATION" and archetype_fields:
            defensive = archetype_fields.get("defensive_mechanisms", [])
            if defensive:
                archetype_criteria = f"\n\nARCHETYPE: CONFRONTATION\nExpected: Should display defensive mechanisms like: {', '.join(defensive[:3])}\nShould show emotional state and awareness level."
        elif archetype_type == "HELP_SEEKING":
            archetype_criteria = "\n\nARCHETYPE: HELP_SEEKING\nExpected: Should clearly express needs and show vulnerability."
        
        verification_prompt = f"""Evaluate this character's response in a training conversation.

CHARACTER ROLE: {character_role}
LEARNER TYPE: {learner_type}
TURN: {turn_number}/12{archetype_criteria}

RECENT CONVERSATION:
{context}

LEARNER SAID: {learner_message}
CHARACTER REPLIED: {character_response}

EXPECTED TOPICS: {', '.join(expected_topics)}

Score each category:

1. ROLE CONSISTENCY (0-30): Did they stay in character as {character_role}? Did they avoid acting like a facilitator/trainer? If archetype-specific behavior expected, did they show it?
2. PUSH BACK (0-25): If learner was unhelpful/dismissive/confused, did they push back appropriately?
3. TOPIC COVERAGE (0-20): Are they discussing expected topics naturally?
4. EMOTIONAL APPROPRIATENESS (0-15): Do emotions match their situation?
5. LANGUAGE/STRUCTURE (0-10): Under 50 words? Natural tone? Does it flow naturally from previous conversation?

Return JSON:
{{
    "turn_score": 0-100,
    "role_consistency": 0-30,
    "push_back": 0-25,
    "topic_coverage": 0-20,
    "emotional_appropriateness": 0-15,
    "language_structure": 0-10,
    "issues": ["list any problems"],
    "drift_detected": true/false,
    "facilitator_mode": true/false,
    "topics_mentioned": ["topics discussed"],
    "pushed_back": true/false,
    "natural_flow": true/false,
    "flow_comment": "brief comment on conversation naturalness",
    "archetype_behavior_shown": true/false,
    "archetype_comment": "brief comment on archetype-specific behavior if applicable"
}}"""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You evaluate character role consistency. Return only valid JSON."},
                    {"role": "user", "content": verification_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result_text = response.choices[0].message.content.strip()
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                return self._default_verification()
        except Exception as e:
            print(f"Verification error: {str(e)}")
            return self._default_verification()
    
    async def run_conversation(
        self,
        character_system_prompt: str,
        character_role: str,
        learner_type: str,
        expected_topics: List[str],
        max_turns: int = 12,
        language_prompt: str = "",
        learn_mode_facts: str = "",
        archetype_type: str = "",
        archetype_fields: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Run a full conversation with archetype validation"""
        
        print(f"  🤖 Testing {learner_type} learner...")
        
        full_prompt = character_system_prompt
        if language_prompt and "[LANGUAGE_INSTRUCTIONS]" in full_prompt:
            full_prompt = full_prompt.replace("[LANGUAGE_INSTRUCTIONS]", language_prompt)
        
        conversation_history = []
        turn_results = []
        topics_covered = set()
        facilitator_count = 0
        push_back_count = 0
        push_back_opportunities = 0
        archetype_behavior_count = 0
        
        initial_greeting = "Hi there!" if learner_type != "CONFUSED" else "Hello, I need help."
        conversation_history.append({"role": "user", "content": initial_greeting})
        
        for turn in range(1, max_turns + 1):
            messages = [{"role": "system", "content": full_prompt}] + conversation_history
            
            try:
                char_response = await self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=300
                )
                
                character_message = char_response.choices[0].message.content.strip()
                conversation_history.append({"role": "assistant", "content": character_message})
                
                if "[FINISH]" in character_message:
                    avg_score = sum([r["turn_score"] for r in turn_results]) / len(turn_results) if turn_results else 0
                    return {
                        "learner_type": learner_type,
                        "turns_completed": turn,
                        "conversation_history": conversation_history,
                        "turn_results": turn_results,
                        "topics_covered": list(topics_covered),
                        "facilitator_count": facilitator_count,
                        "push_back_rate": push_back_count / push_back_opportunities if push_back_opportunities > 0 else 0,
                        "archetype_behavior_rate": archetype_behavior_count / turn if archetype_type else 1.0,
                        "completed": True
                    }
                
                learner_message = await self.generate_learner_response(
                    learner_type, turn, conversation_history, character_role, learn_mode_facts
                )
                conversation_history.append({"role": "user", "content": learner_message})
                
                turn_verification = await self.verify_turn(
                    learner_type, learner_message, character_message,
                    turn, character_role, expected_topics, conversation_history,
                    archetype_type, archetype_fields
                )
                
                turn_results.append(turn_verification)
                topics_covered.update(turn_verification.get("topics_mentioned", []))
                
                if turn_verification.get("facilitator_mode"):
                    facilitator_count += 1
                
                if turn_verification.get("archetype_behavior_shown"):
                    archetype_behavior_count += 1
                
                if learner_type in ["DISMISSIVE", "CONFUSED"] or (learner_type == "MIXED" and turn >= 3):
                    push_back_opportunities += 1
                    if turn_verification.get("pushed_back"):
                        push_back_count += 1
                
            except Exception as e:
                print(f"Error in turn {turn}: {str(e)}")
                break
        
        return {
            "learner_type": learner_type,
            "turns_completed": max_turns,
            "conversation_history": conversation_history,
            "turn_results": turn_results,
            "topics_covered": list(topics_covered),
            "facilitator_count": facilitator_count,
            "push_back_rate": push_back_count / push_back_opportunities if push_back_opportunities > 0 else 0,
            "archetype_behavior_rate": archetype_behavior_count / max_turns if archetype_type else 1.0,
            "completed": False
        }
    
    async def test_prompt_strength(
        self,
        character_system_prompt: str,
        character_role: str,
        expected_topics: List[str],
        language_prompt: str = "",
        learn_mode_facts: str = "",
        archetype_type: str = "",
        archetype_fields: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Run full prompt strength test with archetype validation"""
        
        print(f"\n🐐 PROMPT STRENGTH TEST")
        print("=" * 60)
        print(f"CHARACTER: {character_role}")
        if archetype_type:
            print(f"ARCHETYPE: {archetype_type}")
            if archetype_fields:
                print(f"ARCHETYPE FIELDS: {list(archetype_fields.keys())}")
        print("=" * 60)
        
        learner_types = ["HELPFUL", "DISMISSIVE", "CONFUSED", "MIXED"]
        conversation_results = {}
        
        for learner_type in learner_types:
            result = await self.run_conversation(
                character_system_prompt,
                character_role,
                learner_type,
                expected_topics,
                language_prompt=language_prompt,
                learn_mode_facts=learn_mode_facts,
                archetype_type=archetype_type,
                archetype_fields=archetype_fields
            )
            conversation_results[learner_type] = result
            
            avg_score = sum([t["turn_score"] for t in result["turn_results"]]) / len(result["turn_results"]) if result["turn_results"] else 0
            print(f"\n🤖 {learner_type} LEARNER: {int(avg_score)}/100")
            
            if result["completed"]:
                print(f"   ✅ Completed with [FINISH]")
            else:
                print(f"   ⚠️  No proper ending")
            
            print(f"   Topics: {len(result['topics_covered'])}/{len(expected_topics)} covered")
            
            if result["facilitator_count"] > 0:
                print(f"   ⚠️  Facilitator mode: {result['facilitator_count']} times")
            
            if archetype_type:
                arch_rate = int(result["archetype_behavior_rate"] * 100)
                if arch_rate >= 70:
                    print(f"   ✅ Archetype behavior: {arch_rate}%")
                else:
                    print(f"   ⚠️  Archetype behavior: {arch_rate}%")
            
            if learner_type in ["DISMISSIVE", "CONFUSED", "MIXED"]:
                push_rate = int(result["push_back_rate"] * 100)
                if push_rate >= 70:
                    print(f"   ✅ Pushed back: {push_rate}%")
                else:
                    print(f"   ⚠️  Pushed back: {push_rate}%")
        
        print(f"\n{'=' * 60}")
        print(f"TEST COMPLETE")
        print(f"{'=' * 60}")
        
        return {
            "character_role": character_role,
            "archetype_type": archetype_type,
            "archetype_fields": archetype_fields,
            "test_timestamp": datetime.now().isoformat(),
            "conversation_results": conversation_results
        }
    
    def _default_verification(self) -> Dict[str, Any]:
        return {
            "turn_score": 50,
            "role_consistency": 15,
            "push_back": 12,
            "topic_coverage": 10,
            "emotional_appropriateness": 8,
            "language_structure": 5,
            "issues": ["Verification failed"],
            "drift_detected": False,
            "facilitator_mode": False,
            "topics_mentioned": [],
            "pushed_back": False,
            "archetype_behavior_shown": False,
            "archetype_comment": ""
        }


async def test_scenario_prompt_strength(scenario_id: str, mode: str = "assess_mode"):
    """Test a scenario's prompt strength with archetype validation"""
    
    scenario = await db.scenarios.find_one({"_id": scenario_id})
    if not scenario:
        print(f"❌ Scenario {scenario_id} not found")
        return
    
    if mode not in scenario:
        print(f"❌ Mode {mode} not found in scenario")
        return
    
    mode_data = scenario[mode]
    avatar_interaction_id = mode_data.get("avatar_interaction")
    
    if not avatar_interaction_id:
        print(f"❌ No avatar interaction found for {mode}")
        return
    
    avatar_interaction = await db.avatar_interactions.find_one({"_id": avatar_interaction_id})
    if not avatar_interaction:
        print(f"❌ Avatar interaction {avatar_interaction_id} not found")
        return
    
    system_prompt = avatar_interaction.get("system_prompt", "")
    character_role = avatar_interaction.get("bot_role", "Character")
    
    # Get persona details
    persona_ids = avatar_interaction.get("personas", [])
    if not persona_ids:
        avatar_ids = avatar_interaction.get("avatars", [])
        if avatar_ids:
            avatar = await db.avatars.find_one({"_id": avatar_ids[0]})
            if avatar:
                persona_ids = avatar.get("persona_id", [])
    
    persona_details = ""
    if persona_ids:
        persona = await db.personas.find_one({"_id": persona_ids[0]})
        if persona:
            persona_details = f"""Name: {persona.get('name', '')}
Description: {persona.get('description', '')}
Age: {persona.get('age', '')}
Gender: {persona.get('gender', '')}
Character Goal: {persona.get('character_goal', '')}
Location: {persona.get('location', '')}
Situation: {persona.get('situation', '')}
Background: {persona.get('background_story', '')}
Business/Personal: {persona.get('business_or_personal', '')}"""
            if persona.get('persona_details'):
                persona_details += f"\nAdditional Details: {persona.get('persona_details', '')}"
            print(f"\n✅ Using persona: {persona.get('name', 'Character')}")
    
    if "[PERSONA_PLACEHOLDER]" in system_prompt:
        system_prompt = system_prompt.replace("[PERSONA_PLACEHOLDER]", persona_details)
    
    # Get language prompt
    language_ids = avatar_interaction.get("languages", [])
    language_prompt = ""
    if language_ids:
        language = await db.languages.find_one({"_id": language_ids[0]})
        if language:
            language_prompt = language.get("prompt", "")
    
    # Extract expected topics
    expected_topics = []
    if "Areas to Explore" in system_prompt or "Topics" in system_prompt:
        topic_matches = re.findall(r'\d+\.\s*([^\n]+)', system_prompt)
        expected_topics = [t.strip() for t in topic_matches[:6]]
    
    if not expected_topics:
        expected_topics = ["topic1", "topic2", "topic3", "topic4", "topic5", "topic6"]
    
    # Extract archetype info
    archetype_type = ""
    archetype_fields = {}
    if "template_data" in scenario:
        template_data = scenario["template_data"]
        archetype_classification = template_data.get("archetype_classification", {})
        archetype_type = archetype_classification.get("archetype", "")
        print(f"\n🎭 Archetype: {archetype_type}")
        
        archetype_fields = extract_archetype_fields(system_prompt, archetype_type)
        if archetype_fields:
            print(f"✅ Found archetype-specific fields: {list(archetype_fields.keys())}")
        else:
            print(f"⚠️  No archetype-specific fields found in prompt")
    
    # Run test
    tester = PromptStrengthTester()
    results = await tester.test_prompt_strength(
        system_prompt,
        character_role,
        expected_topics,
        language_prompt=language_prompt,
        archetype_type=archetype_type,
        archetype_fields=archetype_fields
    )
    
    # Save results
    output_file = f"prompt_strength_{scenario_id}_{mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Detailed results saved to: {output_file}")


async def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python automated_prompt_strength_tester_v2.py <scenario_id> [mode]")
        return
    
    scenario_id = sys.argv[1]
    mode = sys.argv[2] if len(sys.argv) > 2 else "assess_mode"
    await test_scenario_prompt_strength(scenario_id, mode)


if __name__ == "__main__":
    asyncio.run(main())
