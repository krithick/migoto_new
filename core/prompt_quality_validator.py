from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import asyncio

class ConversationTest(BaseModel):
    user_message: str
    expected_behavior: str
    test_type: str  # "knowledge", "persona_consistency", "archetype_behavior", "error_handling"

class ConversationTestResult(BaseModel):
    test_passed: bool
    ai_response: str
    evaluation: str
    score: float  # 0-1

class PromptQualityValidator:
    """Validates prompt quality by running actual test conversations"""
    
    def __init__(self, llm_client, model="gpt-4o"):
        self.client = llm_client
        self.model = model
    
    async def validate_prompt_with_conversations(
        self,
        system_prompt: str,
        persona: Dict[str, Any],
        template_data: Dict[str, Any],
        mode: str = "assess"
    ) -> Dict[str, Any]:
        """
        Validate prompt by running test conversations
        Returns quality score and detailed feedback
        """
        
        # Generate test scenarios based on template
        test_conversations = self._generate_test_scenarios(template_data, persona, mode)
        
        # Run each test conversation
        results = []
        for test in test_conversations:
            result = await self._run_conversation_test(system_prompt, test)
            results.append(result)
        
        # Analyze results
        analysis = self._analyze_test_results(results, template_data, persona)
        
        return {
            "overall_score": analysis["overall_score"],
            "test_results": results,
            "strengths": analysis["strengths"],
            "weaknesses": analysis["weaknesses"],
            "recommendations": analysis["recommendations"],
            "conversation_examples": [
                {
                    "user": r.test.user_message,
                    "ai": r.ai_response,
                    "passed": r.test_passed,
                    "evaluation": r.evaluation
                }
                for r in results[:3]  # Show top 3 examples
            ]
        }
    
    def _generate_test_scenarios(
        self,
        template_data: Dict[str, Any],
        persona: Dict[str, Any],
        mode: str
    ) -> List[ConversationTest]:
        """Generate test scenarios based on template content"""
        
        tests = []
        knowledge_base = template_data.get("knowledge_base", {})
        archetype = template_data.get("archetype_classification", {})
        
        # Test 1: Knowledge accuracy
        topics = knowledge_base.get("conversation_topics", [])
        if topics:
            tests.append(ConversationTest(
                user_message=f"Can you tell me about {topics[0]}?",
                expected_behavior="Should provide accurate information from knowledge base",
                test_type="knowledge"
            ))
        
        # Test 2: Persona consistency
        if persona.get("role"):
            tests.append(ConversationTest(
                user_message="Who are you and what's your situation?",
                expected_behavior=f"Should respond as {persona.get('role')} with consistent background",
                test_type="persona_consistency"
            ))
        
        # Test 3: Archetype-specific behavior
        if archetype.get("archetype") == "PERSUASION":
            tests.append(ConversationTest(
                user_message="I'm not sure about this, can you help me decide?",
                expected_behavior="Should use objection handling from objection_library",
                test_type="archetype_behavior"
            ))
        elif archetype.get("archetype") == "CONFRONTATION":
            tests.append(ConversationTest(
                user_message="I think there's been a misunderstanding here.",
                expected_behavior="Should show defensive mechanisms or emotional state",
                test_type="archetype_behavior"
            ))
        
        # Test 4: Error handling
        tests.append(ConversationTest(
            user_message="xyz random nonsense 123",
            expected_behavior="Should handle unclear input gracefully while staying in character",
            test_type="error_handling"
        ))
        
        # Test 5: Inappropriate response handling
        tests.append(ConversationTest(
            user_message="You're stupid and this is a waste of time",
            expected_behavior="Should respond professionally to disrespect",
            test_type="error_handling"
        ))
        
        return tests
    
    async def _run_conversation_test(
        self,
        system_prompt: str,
        test: ConversationTest
    ) -> ConversationTestResult:
        """Run a single conversation test"""
        
        try:
            # Get AI response
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": test.user_message}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            ai_response = response.choices[0].message.content
            
            # Evaluate response quality
            evaluation_result = await self._evaluate_response(
                test.user_message,
                ai_response,
                test.expected_behavior,
                test.test_type
            )
            
            return ConversationTestResult(
                test_passed=evaluation_result["passed"],
                ai_response=ai_response,
                evaluation=evaluation_result["evaluation"],
                score=evaluation_result["score"]
            )
            
        except Exception as e:
            return ConversationTestResult(
                test_passed=False,
                ai_response="",
                evaluation=f"Test failed: {str(e)}",
                score=0.0
            )
    
    async def _evaluate_response(
        self,
        user_message: str,
        ai_response: str,
        expected_behavior: str,
        test_type: str
    ) -> Dict[str, Any]:
        """Evaluate if AI response meets expected behavior"""
        
        evaluation_prompt = f"""
Evaluate this AI training bot response:

USER MESSAGE: {user_message}
AI RESPONSE: {ai_response}
EXPECTED BEHAVIOR: {expected_behavior}
TEST TYPE: {test_type}

Evaluate on these criteria:
1. Does the response match expected behavior?
2. Is the response appropriate and professional?
3. Does it stay in character?
4. Is it helpful and clear?

Return JSON:
{{
    "passed": true/false,
    "score": 0.0-1.0,
    "evaluation": "Brief explanation of why it passed/failed",
    "specific_issues": ["issue1", "issue2"] or []
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at evaluating AI training bot responses."},
                    {"role": "user", "content": evaluation_prompt}
                ],
                temperature=0.2,
                max_tokens=300
            )
            
            import json
            import re
            result_text = response.choices[0].message.content
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            return json.loads(result_text)
            
        except Exception as e:
            return {
                "passed": False,
                "score": 0.0,
                "evaluation": f"Evaluation failed: {str(e)}",
                "specific_issues": []
            }
    
    def _analyze_test_results(
        self,
        results: List[ConversationTestResult],
        template_data: Dict[str, Any],
        persona: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze all test results and provide feedback"""
        
        total_score = sum(r.score for r in results) / len(results) if results else 0
        passed_count = sum(1 for r in results if r.test_passed)
        
        strengths = []
        weaknesses = []
        recommendations = []
        
        # Analyze by test type
        test_types = {}
        for result in results:
            test_type = result.test.test_type
            if test_type not in test_types:
                test_types[test_type] = []
            test_types[test_type].append(result)
        
        for test_type, type_results in test_types.items():
            type_score = sum(r.score for r in type_results) / len(type_results)
            
            if type_score >= 0.8:
                strengths.append(f"Strong {test_type} handling (score: {type_score:.2f})")
            elif type_score < 0.5:
                weaknesses.append(f"Weak {test_type} handling (score: {type_score:.2f})")
                recommendations.append(f"Improve {test_type} by reviewing prompt instructions")
        
        # Check persona consistency
        persona_tests = [r for r in results if r.test.test_type == "persona_consistency"]
        if persona_tests and all(r.test_passed for r in persona_tests):
            strengths.append("Consistent persona behavior")
        elif persona_tests:
            weaknesses.append("Inconsistent persona behavior")
            recommendations.append("Clarify persona details in system prompt")
        
        # Check archetype behavior
        archetype_tests = [r for r in results if r.test.test_type == "archetype_behavior"]
        if archetype_tests and all(r.test_passed for r in archetype_tests):
            strengths.append("Proper archetype-specific behavior")
        elif archetype_tests:
            weaknesses.append("Archetype behavior not evident")
            recommendations.append("Ensure archetype-specific fields are included in persona")
        
        return {
            "overall_score": total_score,
            "passed_tests": passed_count,
            "total_tests": len(results),
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations
        }


class InteractivePromptTester:
    """Interactive testing facility for prompts with different personas"""
    
    def __init__(self, llm_client, model="gpt-4o"):
        self.client = llm_client
        self.model = model
        self.conversation_history = []
    
    async def start_test_conversation(
        self,
        system_prompt: str,
        persona: Dict[str, Any],
        initial_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Start a test conversation with a persona"""
        
        self.conversation_history = []
        
        if initial_message:
            response = await self._send_message(system_prompt, initial_message)
            return {
                "conversation_id": "test_" + str(hash(system_prompt))[:8],
                "persona": persona.get("name", "Test Persona"),
                "initial_response": response,
                "message": "Conversation started. Use continue_test_conversation to continue."
            }
        
        return {
            "conversation_id": "test_" + str(hash(system_prompt))[:8],
            "persona": persona.get("name", "Test Persona"),
            "message": "Conversation ready. Send first message."
        }
    
    async def continue_test_conversation(
        self,
        system_prompt: str,
        user_message: str
    ) -> Dict[str, Any]:
        """Continue test conversation"""
        
        response = await self._send_message(system_prompt, user_message)
        
        return {
            "user_message": user_message,
            "ai_response": response,
            "turn_number": len(self.conversation_history) // 2,
            "conversation_history": self.conversation_history
        }
    
    async def _send_message(self, system_prompt: str, user_message: str) -> str:
        """Send message and get response"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in self.conversation_history:
            messages.append(msg)
        
        # Add new user message
        messages.append({"role": "user", "content": user_message})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=200
        )
        
        ai_response = response.choices[0].message.content
        
        # Update history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": ai_response})
        
        return ai_response
    
    async def evaluate_conversation(
        self,
        template_data: Dict[str, Any],
        persona: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate the full conversation"""
        
        evaluation_prompt = f"""
Evaluate this test conversation with an AI training bot:

CONVERSATION HISTORY:
{self._format_conversation_history()}

EXPECTED PERSONA: {persona.get('name')} - {persona.get('role')}
SCENARIO: {template_data.get('context_overview', {}).get('scenario_title')}

Evaluate:
1. Persona consistency throughout conversation
2. Knowledge accuracy
3. Appropriate responses
4. Archetype-specific behavior (if applicable)
5. Professional tone

Return JSON:
{{
    "overall_score": 0.0-1.0,
    "persona_consistency": 0.0-1.0,
    "knowledge_accuracy": 0.0-1.0,
    "response_quality": 0.0-1.0,
    "strengths": ["strength1", "strength2"],
    "issues": ["issue1", "issue2"],
    "recommendations": ["rec1", "rec2"]
}}
"""
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert at evaluating AI training conversations."},
                {"role": "user", "content": evaluation_prompt}
            ],
            temperature=0.2,
            max_tokens=500
        )
        
        import json
        import re
        result_text = response.choices[0].message.content
        json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(1))
        return json.loads(result_text)
    
    def _format_conversation_history(self) -> str:
        """Format conversation history for evaluation"""
        formatted = []
        for msg in self.conversation_history:
            role = "USER" if msg["role"] == "user" else "AI"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted)
