"""
Automated Prompt Strength Testing System

Tests character AI prompts by simulating 4 learner types:
- HELPFUL: Gives good advice
- DISMISSIVE: Vague unhelpful responses
- CONFUSED: Asks character for help (role reversal trap)
- MIXED: Alternates between types

Each conversation runs 8 turns with turn-by-turn verification.
"""

import asyncio
import json
from typing import List, Dict, Any
from openai import AsyncAzureOpenAI
from database import db
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv(".env")


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
        character_role: str
    ) -> str:
        """Generate learner response based on type and turn"""
        
        system_prompt = self.learner_system_prompts[learner_type]
        
        # Add turn-specific guidance for MIXED
        if learner_type == "MIXED":
            if turn_number <= 2:
                system_prompt += "\n\nCURRENT MODE: Be helpful with specific advice."
            elif turn_number <= 4:
                system_prompt += "\n\nCURRENT MODE: Be dismissive and vague."
            elif turn_number <= 6:
                system_prompt += "\n\nCURRENT MODE: Be confused, ask them for help."
            else:
                system_prompt += "\n\nCURRENT MODE: Be brief and slightly dismissive."
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"You are talking to: {character_role}"}
        ]
        
        # Add conversation history
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
        expected_topics: List[str]
    ) -> Dict[str, Any]:
        """Verify character response for a single turn"""
        
        verification_prompt = f"""Evaluate this character's response in a training conversation.

CHARACTER ROLE: {character_role}
LEARNER TYPE: {learner_type}
TURN: {turn_number}/8

LEARNER SAID: {learner_message}
CHARACTER REPLIED: {character_response}

EXPECTED TOPICS: {', '.join(expected_topics)}

Score each category:

1. ROLE CONSISTENCY (0-30): Did they stay in character as {character_role}? Did they avoid acting like a facilitator/trainer?
2. PUSH BACK (0-25): If learner was unhelpful/dismissive/confused, did they push back appropriately?
3. TOPIC COVERAGE (0-20): Are they discussing expected topics naturally?
4. EMOTIONAL APPROPRIATENESS (0-15): Do emotions match their situation?
5. LANGUAGE/STRUCTURE (0-10): Under 50 words? Natural tone?

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
    "pushed_back": true/false
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
            
            # Parse JSON
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                return self._default_verification()
                
        except Exception as e:
            print(f"Verification error: {str(e)}")
            return self._default_verification()
    
    async def verify_ending(
        self,
        character_final_response: str,
        turn_number: int,
        conversation_quality_score: float
    ) -> Dict[str, Any]:
        """Verify conversation ending appropriateness"""
        
        verification_prompt = f"""Evaluate this conversation ending.

FINAL RESPONSE: {character_final_response}
TURN NUMBER: {turn_number}
CONVERSATION QUALITY: {conversation_quality_score}/100

Check:
1. Used [FINISH] tag? (30 pts)
2. Correct closing type? (40 pts)
   - Score 0-40: Should use negative closing
   - Score 41-69: Should use neutral closing  
   - Score 70-100: Should use positive closing
3. Ended at turn 6-8? (30 pts)

Return JSON:
{{
    "ending_score": 0-100,
    "has_finish_tag": true/false,
    "correct_closing_type": true/false,
    "appropriate_timing": true/false,
    "closing_type_detected": "positive/neutral/negative/none",
    "issues": ["list problems"]
}}"""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Evaluate conversation endings. Return only valid JSON."},
                    {"role": "user", "content": verification_prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            result_text = response.choices[0].message.content.strip()
            
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                return self._default_ending_verification()
                
        except Exception as e:
            print(f"Ending verification error: {str(e)}")
            return self._default_ending_verification()
    
    async def run_conversation(
        self,
        character_system_prompt: str,
        character_role: str,
        learner_type: str,
        expected_topics: List[str],
        max_turns: int = 12,
        language_prompt: str = ""
    ) -> Dict[str, Any]:
        """Run a full conversation with a specific learner type"""
        
        print(f"  🤖 Testing {learner_type} learner...")
        
        # Build full prompt with language instructions
        full_prompt = character_system_prompt
        if language_prompt and "[LANGUAGE_INSTRUCTIONS]" in full_prompt:
            full_prompt = full_prompt.replace("[LANGUAGE_INSTRUCTIONS]", language_prompt)
        
        conversation_history = []
        turn_results = []
        topics_covered = set()
        facilitator_count = 0
        push_back_count = 0
        push_back_opportunities = 0
        
        # Character starts (greeting from learner)
        initial_greeting = "Hi there!" if learner_type != "CONFUSED" else "Hello, I need help."
        
        conversation_history.append({"role": "user", "content": initial_greeting})
        
        for turn in range(1, max_turns + 1):
            # Get character response
            messages = [
                {"role": "system", "content": full_prompt}
            ] + conversation_history
            
            try:
                char_response = await self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=300
                )
                
                character_message = char_response.choices[0].message.content.strip()
                conversation_history.append({"role": "assistant", "content": character_message})
                
                # Check if conversation ended
                if "[FINISH]" in character_message:
                    # Verify ending
                    avg_score = sum([r["turn_score"] for r in turn_results]) / len(turn_results) if turn_results else 0
                    ending_verification = await self.verify_ending(character_message, turn, avg_score)
                    
                    return {
                        "learner_type": learner_type,
                        "turns_completed": turn,
                        "conversation_history": conversation_history,
                        "turn_results": turn_results,
                        "ending_verification": ending_verification,
                        "topics_covered": list(topics_covered),
                        "facilitator_count": facilitator_count,
                        "push_back_rate": push_back_count / push_back_opportunities if push_back_opportunities > 0 else 0,
                        "completed": True
                    }
                
                # Generate learner response
                learner_message = await self.generate_learner_response(
                    learner_type, turn, conversation_history, character_role
                )
                conversation_history.append({"role": "user", "content": learner_message})
                
                # Verify this turn
                turn_verification = await self.verify_turn(
                    learner_type, learner_message, character_message,
                    turn, character_role, expected_topics
                )
                
                turn_results.append(turn_verification)
                topics_covered.update(turn_verification.get("topics_mentioned", []))
                
                if turn_verification.get("facilitator_mode"):
                    facilitator_count += 1
                
                if learner_type in ["DISMISSIVE", "CONFUSED"] or (learner_type == "MIXED" and turn >= 3):
                    push_back_opportunities += 1
                    if turn_verification.get("pushed_back"):
                        push_back_count += 1
                
            except Exception as e:
                print(f"Error in turn {turn}: {str(e)}")
                break
        
        # Conversation didn't end naturally
        return {
            "learner_type": learner_type,
            "turns_completed": max_turns,
            "conversation_history": conversation_history,
            "turn_results": turn_results,
            "ending_verification": {"ending_score": 0, "issues": ["No [FINISH] tag used"]},
            "topics_covered": list(topics_covered),
            "facilitator_count": facilitator_count,
            "push_back_rate": push_back_count / push_back_opportunities if push_back_opportunities > 0 else 0,
            "completed": False
        }
    
    async def calculate_prompt_strength(
        self,
        conversation_results: Dict[str, Dict]
    ) -> Dict[str, Any]:
        """Calculate overall prompt strength from all conversations"""
        
        # Role Adherence (30 pts) - Average of role_consistency scores (already 0-30)
        all_role_scores = []
        for result in conversation_results.values():
            for turn in result["turn_results"]:
                all_role_scores.append(turn["role_consistency"])
        role_adherence = (sum(all_role_scores) / len(all_role_scores)) if all_role_scores else 0
        
        # Push Back Effectiveness (25 pts) - Convert rate (0-1) to points (0-25)
        dismissive_result = conversation_results.get("DISMISSIVE", {})
        confused_result = conversation_results.get("CONFUSED", {})
        mixed_result = conversation_results.get("MIXED", {})
        
        push_back_rates = [
            dismissive_result.get("push_back_rate", 0),
            confused_result.get("push_back_rate", 0),
            mixed_result.get("push_back_rate", 0)
        ]
        push_back_effectiveness = (sum(push_back_rates) / len(push_back_rates)) * 25 if push_back_rates else 0
        
        # Topic Coverage (20 pts) - Cap at 20 max
        all_topics_covered = set()
        expected_topics = set()
        
        for result in conversation_results.values():
            all_topics_covered.update(result["topics_covered"])
        
        # Get expected topics from first conversation
        first_result = list(conversation_results.values())[0]
        for turn in first_result.get("turn_results", []):
            expected_topics.update(turn.get("topics_mentioned", []))
        
        expected_count = max(len(expected_topics), 6)  # Assume at least 6 topics
        coverage_ratio = min(len(all_topics_covered) / expected_count, 1.0)  # Cap at 1.0
        topic_coverage = coverage_ratio * 20
        
        # Closing Mechanism (15 pts) - Convert 0-100 score to 0-15
        closing_scores = []
        for result in conversation_results.values():
            ending = result.get("ending_verification", {})
            closing_scores.append(ending.get("ending_score", 0))
        avg_closing = (sum(closing_scores) / len(closing_scores)) if closing_scores else 0
        closing_mechanism = (avg_closing / 100) * 15
        
        # Stress Resistance (10 pts) - Convert 0-100 avg to 0-10
        difficult_learners = ["DISMISSIVE", "CONFUSED", "MIXED"]
        stress_scores = []
        for learner_type in difficult_learners:
            if learner_type in conversation_results:
                result = conversation_results[learner_type]
                avg_turn_score = sum([t["turn_score"] for t in result["turn_results"]]) / len(result["turn_results"]) if result["turn_results"] else 0
                stress_scores.append(avg_turn_score)
        avg_stress = (sum(stress_scores) / len(stress_scores)) if stress_scores else 0
        stress_resistance = (avg_stress / 100) * 10
        
        # Calculate total
        total_score = role_adherence + push_back_effectiveness + topic_coverage + closing_mechanism + stress_resistance
        
        # Determine rating
        if total_score >= 90:
            rating = "GOATED 🐐"
            status = "Production ready"
        elif total_score >= 80:
            rating = "STRONG 💪"
            status = "Minor improvements needed"
        elif total_score >= 70:
            rating = "DECENT ✅"
            status = "Needs refinement"
        elif total_score >= 60:
            rating = "WEAK ⚠️"
            status = "Major issues"
        else:
            rating = "BROKEN ❌"
            status = "Redesign needed"
        
        # Identify strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if role_adherence >= 27:
            strengths.append("Excellent role consistency")
        elif role_adherence < 21:
            weaknesses.append("Role consistency issues")
        
        if push_back_effectiveness >= 20:
            strengths.append("Strong push back")
        elif push_back_effectiveness < 15:
            weaknesses.append("Weak push back")
        
        if topic_coverage >= 16:
            strengths.append("Good topic coverage")
        elif topic_coverage < 12:
            weaknesses.append("Low topic coverage")
        
        facilitator_total = sum([r.get("facilitator_count", 0) for r in conversation_results.values()])
        if facilitator_total == 0:
            strengths.append("No facilitator mode")
        elif facilitator_total > 3:
            weaknesses.append(f"Facilitator mode: {facilitator_total} times")
        
        return {
            "total_score": round(total_score, 1),
            "rating": rating,
            "status": status,
            "breakdown": {
                "role_adherence": round(role_adherence, 1),
                "push_back": round(push_back_effectiveness, 1),
                "topic_coverage": round(topic_coverage, 1),
                "closing": round(closing_mechanism, 1),
                "stress_resistance": round(stress_resistance, 1)
            },
            "strengths": strengths,
            "weaknesses": weaknesses,
            "facilitator_total": facilitator_total
        }
    
    async def test_prompt_strength(
        self,
        character_system_prompt: str,
        character_role: str,
        expected_topics: List[str],
        language_prompt: str = ""
    ) -> Dict[str, Any]:
        """Run full prompt strength test across all learner types"""
        
        print(f"\n🐐 PROMPT STRENGTH TEST")
        print("=" * 60)
        print(f"CHARACTER: {character_role}")
        print("=" * 60)
        
        learner_types = ["HELPFUL", "DISMISSIVE", "CONFUSED", "MIXED"]
        conversation_results = {}
        
        for learner_type in learner_types:
            result = await self.run_conversation(
                character_system_prompt,
                character_role,
                learner_type,
                expected_topics,
                language_prompt=language_prompt
            )
            conversation_results[learner_type] = result
            
            # Print summary
            avg_score = sum([t["turn_score"] for t in result["turn_results"]]) / len(result["turn_results"]) if result["turn_results"] else 0
            print(f"\n🤖 {learner_type} LEARNER: {int(avg_score)}/100")
            
            if result["completed"]:
                print(f"   ✅ Completed with [FINISH]")
            else:
                print(f"   ⚠️  No proper ending")
            
            print(f"   Topics: {len(result['topics_covered'])}/{len(expected_topics)} covered")
            
            if result["facilitator_count"] > 0:
                print(f"   ⚠️  Facilitator mode: {result['facilitator_count']} times")
            
            if learner_type in ["DISMISSIVE", "CONFUSED", "MIXED"]:
                push_rate = int(result["push_back_rate"] * 100)
                if push_rate >= 70:
                    print(f"   ✅ Pushed back: {push_rate}%")
                else:
                    print(f"   ⚠️  Pushed back: {push_rate}%")
        
        # Calculate overall strength
        strength_analysis = await self.calculate_prompt_strength(conversation_results)
        
        # Get LLM recommendations
        recommendations = await self.get_improvement_recommendations(
            conversation_results,
            strength_analysis,
            character_system_prompt
        )
        
        # Print final report
        print(f"\n{'=' * 60}")
        print(f"OVERALL: {strength_analysis['total_score']}/100 - {strength_analysis['rating']}")
        print(f"\nBREAKDOWN:")
        print(f"- Role Adherence: {strength_analysis['breakdown']['role_adherence']}/30")
        print(f"- Push Back: {strength_analysis['breakdown']['push_back']}/25")
        print(f"- Topic Coverage: {strength_analysis['breakdown']['topic_coverage']}/20")
        print(f"- Closing: {strength_analysis['breakdown']['closing']}/15")
        print(f"- Stress Resistance: {strength_analysis['breakdown']['stress_resistance']}/10")
        
        if strength_analysis['strengths']:
            print(f"\nSTRENGTHS:")
            for strength in strength_analysis['strengths']:
                print(f"✅ {strength}")
        
        if strength_analysis['weaknesses']:
            print(f"\nWEAKNESSES:")
            for weakness in strength_analysis['weaknesses']:
                print(f"⚠️  {weakness}")
        
        print(f"\nSTATUS: {strength_analysis['status']}")
        
        # Print recommendations
        print(f"\n{'=' * 60}")
        print(f"🔧 IMPROVEMENT RECOMMENDATIONS")
        print(f"{'=' * 60}")
        print(f"\n{recommendations['summary']}")
        
        if recommendations['specific_issues']:
            print(f"\n📋 SPECIFIC ISSUES FOUND:")
            for i, issue in enumerate(recommendations['specific_issues'], 1):
                print(f"{i}. {issue}")
        
        if recommendations['prompt_improvements']:
            print(f"\n✏️  PROMPT IMPROVEMENTS:")
            for i, improvement in enumerate(recommendations['prompt_improvements'], 1):
                print(f"{i}. {improvement}")
        
        if recommendations['example_additions']:
            print(f"\n💡 SUGGESTED ADDITIONS:")
            for addition in recommendations['example_additions']:
                print(f"\n{addition}")
        
        return {
            "character_role": character_role,
            "test_timestamp": datetime.now().isoformat(),
            "conversation_results": conversation_results,
            "strength_analysis": strength_analysis,
            "recommendations": recommendations
        }
    
    def _default_verification(self) -> Dict[str, Any]:
        """Default verification result on error"""
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
            "pushed_back": False
        }
    
    def _default_ending_verification(self) -> Dict[str, Any]:
        """Default ending verification on error"""
        return {
            "ending_score": 0,
            "has_finish_tag": False,
            "correct_closing_type": False,
            "appropriate_timing": False,
            "closing_type_detected": "none",
            "issues": ["Verification failed"]
        }
    
    async def get_improvement_recommendations(
        self,
        conversation_results: Dict[str, Dict],
        strength_analysis: Dict[str, Any],
        character_system_prompt: str
    ) -> Dict[str, Any]:
        """Get LLM-generated recommendations for prompt improvement"""
        
        # Collect all issues from conversations
        all_issues = []
        facilitator_examples = []
        weak_pushback_examples = []
        missing_topics = set()
        
        for learner_type, result in conversation_results.items():
            for i, turn in enumerate(result["turn_results"], 1):
                if turn.get("facilitator_mode"):
                    conv_history = result["conversation_history"]
                    if i*2 < len(conv_history):
                        facilitator_examples.append(f"Turn {i} ({learner_type}): {conv_history[i*2-1]['content']}")
                
                if turn.get("issues"):
                    all_issues.extend(turn["issues"])
                
                if learner_type in ["DISMISSIVE", "CONFUSED"] and not turn.get("pushed_back"):
                    conv_history = result["conversation_history"]
                    if i*2 < len(conv_history):
                        weak_pushback_examples.append(f"Turn {i} ({learner_type}): Learner said '{conv_history[i*2]['content']}' but character didn't push back")
        
        analysis_prompt = f"""Analyze this character prompt's test results and provide specific improvement recommendations.

CHARACTER PROMPT:
{character_system_prompt[:1000]}...

TEST RESULTS:
- Overall Score: {strength_analysis['total_score']}/100
- Role Adherence: {strength_analysis['breakdown']['role_adherence']}/30
- Push Back: {strength_analysis['breakdown']['push_back']}/25
- Topic Coverage: {strength_analysis['breakdown']['topic_coverage']}/20
- Closing: {strength_analysis['breakdown']['closing']}/15
- Stress Resistance: {strength_analysis['breakdown']['stress_resistance']}/10

ISSUES FOUND:
{chr(10).join(all_issues[:10]) if all_issues else 'None'}

FACILITATOR MODE EXAMPLES:
{chr(10).join(facilitator_examples[:3]) if facilitator_examples else 'None'}

WEAK PUSHBACK EXAMPLES:
{chr(10).join(weak_pushback_examples[:3]) if weak_pushback_examples else 'None'}

Provide:
1. A 2-3 sentence summary of main problems
2. List of 3-5 specific issues to fix
3. List of 3-5 concrete prompt improvements
4. 1-2 example text additions to add to the prompt

Return JSON:
{{
    "summary": "brief overview of problems",
    "specific_issues": ["issue 1", "issue 2", ...],
    "prompt_improvements": ["improvement 1", "improvement 2", ...],
    "example_additions": ["text to add to prompt", ...]
}}"""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert at improving conversational AI prompts. Provide specific, actionable recommendations. Return only valid JSON."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            else:
                return self._default_recommendations()
                
        except Exception as e:
            print(f"\nRecommendation generation error: {str(e)}")
            return self._default_recommendations()
    
    def _default_recommendations(self) -> Dict[str, Any]:
        """Default recommendations on error"""
        return {
            "summary": "Unable to generate detailed recommendations. Review test results manually.",
            "specific_issues": ["Check role consistency", "Review push back behavior", "Verify topic coverage"],
            "prompt_improvements": ["Add clearer behavior rules", "Strengthen character background", "Add push back examples"],
            "example_additions": []
        }


async def test_scenario_prompt_strength(scenario_id: str, mode: str = "assess_mode"):
    """Test a scenario's prompt strength"""
    
    # Get scenario
    scenario = await db.scenarios.find_one({"_id": scenario_id})
    if not scenario:
        print(f"❌ Scenario {scenario_id} not found")
        return
    
    # Get mode data
    if mode not in scenario:
        print(f"❌ Mode {mode} not found in scenario")
        return
    
    mode_data = scenario[mode]
    avatar_interaction_id = mode_data.get("avatar_interaction")
    
    if not avatar_interaction_id:
        print(f"❌ No avatar interaction found for {mode}")
        return
    
    # Get avatar interaction
    avatar_interaction = await db.avatar_interactions.find_one({"_id": avatar_interaction_id})
    if not avatar_interaction:
        print(f"❌ Avatar interaction {avatar_interaction_id} not found")
        return
    
    # Get system prompt and build full prompt
    system_prompt = avatar_interaction.get("system_prompt", "")
    character_role = avatar_interaction.get("bot_role", "Character")
    
    # Get persona details and inject
    persona_ids = avatar_interaction.get("personas", [])
    persona_details = ""
    if persona_ids:
        persona = await db.personas.find_one({"_id": persona_ids[0]})
        if persona:
            persona_details = f"""Name: {persona.get('name', '')}
Age: {persona.get('age', '')}
Gender: {persona.get('gender', '')}
Situation: {persona.get('situation', '')}
Goal: {persona.get('character_goal', '')}
Location: {persona.get('location', '')}
Background: {persona.get('background_story', '')}"""
    
    # Replace persona placeholder
    if "[PERSONA_PLACEHOLDER]" in system_prompt:
        system_prompt = system_prompt.replace("[PERSONA_PLACEHOLDER]", persona_details)
    
    # Get language prompt
    language_ids = avatar_interaction.get("languages", [])
    language_prompt = ""
    if language_ids:
        language = await db.languages.find_one({"_id": language_ids[0]})
        if language:
            language_prompt = language.get("prompt", "")
    
    # Extract expected topics from prompt
    expected_topics = []
    if "Areas to Explore" in system_prompt or "Topics" in system_prompt:
        import re
        topic_matches = re.findall(r'\d+\.\s*([^\n]+)', system_prompt)
        expected_topics = [t.strip() for t in topic_matches[:6]]
    
    if not expected_topics:
        expected_topics = ["topic1", "topic2", "topic3", "topic4", "topic5", "topic6"]
    
    # Run test
    tester = PromptStrengthTester()
    results = await tester.test_prompt_strength(
        system_prompt,
        character_role,
        expected_topics,
        language_prompt=language_prompt
    )
    
    # Save results
    output_file = f"prompt_strength_{scenario_id}_{mode}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Detailed results saved to: {output_file}")


async def test_custom_prompt():
    """Test a custom prompt directly"""
    
    print("🐐 CUSTOM PROMPT STRENGTH TEST")
    print("=" * 60)
    
    # Example prompt
    character_prompt = """# Product Return - Defective Laptop

You are **Customer** who wants to return a defective laptop.

## Character Background
- Name: Priya Sharma
- Age: 28
- Situation: Laptop crashes every few hours
- Goal: Get refund or replacement

## First Response
When greeted, immediately share your concern:
"Hi. I bought a laptop 3 weeks ago and it keeps crashing. I need a refund or replacement."

## Topics to Discuss
1. Refund policy
2. Replacement option
3. Warranty coverage
4. Timeline
5. Proof needed
6. Compensation

## Behavior Rules
- React, don't guide
- Push back on vague responses
- Close with [FINISH] after 10-12 turns"""
    
    character_role = "Customer with defective laptop"
    expected_topics = ["Refund policy", "Replacement option", "Warranty coverage", "Timeline", "Proof needed", "Compensation"]
    
    tester = PromptStrengthTester()
    results = await tester.test_prompt_strength(
        character_prompt,
        character_role,
        expected_topics
    )
    
    # Save results
    output_file = f"prompt_strength_custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Detailed results saved to: {output_file}")


async def main():
    """CLI entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python automated_prompt_strength_tester.py <scenario_id> [mode]")
        print("  python automated_prompt_strength_tester.py custom")
        return
    
    if sys.argv[1] == "custom":
        await test_custom_prompt()
    else:
        scenario_id = sys.argv[1]
        mode = sys.argv[2] if len(sys.argv) > 2 else "assess_mode"
        await test_scenario_prompt_strength(scenario_id, mode)


if __name__ == "__main__":
    asyncio.run(main())
