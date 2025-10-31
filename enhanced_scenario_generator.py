from typing import Dict, Any, List, Optional
import json
import re
from datetime import datetime
from uuid import uuid4
from openai import AsyncAzureOpenAI


class FlexibleScenarioGenerator:
    """
    Enhanced scenario generator with flexible extraction and dynamic template creation.
    Supports both document-based and prompt-based scenario generation.
    """
    
    def __init__(self, client: AsyncAzureOpenAI, model: str = "gpt-4o"):
        self.client = client
        self.model = model
    
    def _extract_raw_data(self, document_content: str) -> Dict[str, Any]:
        """Extract ALL raw data from document with comprehensive table parsing"""
        # Initialize storage for all possible document sections
        raw_data = {
            "project_basics": {},           # TABLE_0: Company, Course, Module, etc.
            "target_skills": [],           # TABLE_1: Learning objectives 1-5
            "learner_info": {},            # TABLE_2: Job roles, experience, challenges
            "ai_trainer": {},              # TABLE_3: AI trainer role and topics
            "ai_colleague": {},            # TABLE_4: AI colleague/stakeholder role
            "knowledge_accuracy": {},      # TABLE_5: What must be 100% accurate
            "common_situations": [],       # TABLE_6: Situations and correct responses
            "correction_preferences": {},  # TABLE_7: How AI should correct mistakes
            "success_metrics": [],         # TABLE_8: Success metrics and targets
            "common_mistakes": [],         # TABLE_9: Common mistakes to catch
            "conversation_examples": {},   # Scattered throughout document
            "all_paragraphs": []          # Capture everything for backup
        }
        
        lines = document_content.split('\n')
        current_table = None
        current_row_data = {}
        
        print(f"Starting extraction from {len(lines)} lines")
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Store all paragraphs for backup analysis
            if line.startswith('PARAGRAPH_') and ':' in line:
                paragraph_text = line.split(':', 1)[1].strip()
                if len(paragraph_text) > 10:  # Only meaningful paragraphs
                    raw_data["all_paragraphs"].append(paragraph_text)
            
            # 🏷️ IDENTIFY TABLE SECTIONS (0-9 mapping to document structure)
            if 'TABLE_0_START:' in line:
                current_table = "project_basics"
                print(f"Found TABLE_0: Project Basics")
            elif 'TABLE_1_START:' in line:
                current_table = "target_skills" 
                print(f"Found TABLE_1: Target Skills")
            elif 'TABLE_2_START:' in line:
                current_table = "learner_info"
                print(f"Found TABLE_2: Learner Info")
            elif 'TABLE_3_START:' in line:
                current_table = "ai_trainer"
                print(f"Found TABLE_3: AI Trainer")
            elif 'TABLE_4_START:' in line:
                current_table = "ai_colleague"
                print(f"Found TABLE_4: AI Colleague/Stakeholder")
            elif 'TABLE_5_START:' in line:
                current_table = "knowledge_accuracy"
                print(f"Found TABLE_5: Knowledge Accuracy Requirements")
            elif 'TABLE_6_START:' in line:
                current_table = "common_situations"
                print(f"Found TABLE_6: Common Situations")
            elif 'TABLE_7_START:' in line:
                current_table = "correction_preferences"
                print(f"Found TABLE_7: Correction Preferences")
            elif 'TABLE_8_START:' in line:
                current_table = "success_metrics"
                print(f"Found TABLE_8: Success Metrics")
            elif 'TABLE_9_START:' in line:
                current_table = "common_mistakes"
                print(f"Found TABLE_9: Common Mistakes")
            elif 'TABLE_' in line and '_END' in line:
                if current_table:
                    print(f"Finished extracting {current_table}")
                current_table = None
                current_row_data = {}
            
            # 📊 EXTRACT ROW DATA from current table
            elif line.startswith('ROW_') and 'CELL_' in line and current_table:
                try:
                    # Parse: "ROW_1: CELL_0: Field Name | CELL_1: Field Value"
                    if 'CELL_1:' in line:
                        parts = line.split('CELL_1:')
                        if len(parts) > 1:
                            # Extract field name from CELL_0
                            field_part = parts[0]
                            if 'CELL_0:' in field_part:
                                field = field_part.split('CELL_0:')[-1].strip(' |').strip()
                            else:
                                field = field_part.replace('ROW_', '').split(':')[1].strip(' |').strip()
                            
                            # Extract value from CELL_1
                            value = parts[1].strip()
                            
                            # 🎯 SMART DATA ORGANIZATION by table type
                            if current_table == "target_skills":
                                # Skills are numbered 1-5, store as list
                                if value and len(value) > 5:  # Meaningful skill description
                                    raw_data["target_skills"].append(value)
                                    print(f"  + Skill: {value[:50]}...")
                            
                            elif current_table in ["common_situations", "success_metrics", "common_mistakes"]:
                                # These have multiple rows with field-value pairs
                                if field and value and len(value) > 3:
                                    raw_data[current_table].append({
                                        "field": field, 
                                        "value": value,
                                        "row_number": len(raw_data[current_table]) + 1
                                    })
                                    print(f"  + {current_table}: {field} = {value[:30]}...")
                            
                            else:
                                # Simple key-value storage for other tables
                                if field and value:
                                    raw_data[current_table][field] = value
                                    print(f"  + {field}: {value[:50]}...")
                                    
                except Exception as e:
                    print(f"Error parsing row {i}: {str(e)}")
                    continue
            
            # 💬 EXTRACT CONVERSATION EXAMPLES (scattered throughout)
            elif 'Conversation Topic:' in line:
                topic = line.split(':', 1)[1].strip()
                raw_data["conversation_examples"]["topic"] = topic
                print(f"Found conversation topic: {topic}")
            
            elif any(keyword in line for keyword in ['AI Colleague:', 'AI Stakeholder:', 'AI Partner:', 'AI Character:', 'AI Bot:']):
                ai_line = line.split(':', 1)[1].strip().strip('"')
                raw_data["conversation_examples"]["ai_line"] = ai_line
                print(f"AI line: {ai_line[:50]}...")
            
            elif 'Correct Learner Response:' in line:
                correct = line.split(':', 1)[1].strip().strip('"')
                raw_data["conversation_examples"]["correct_response"] = correct
                print(f"Correct response: {correct[:50]}...")
            
            elif 'Incorrect Learner Response:' in line:
                incorrect = line.split(':', 1)[1].strip().strip('"')
                raw_data["conversation_examples"]["incorrect_response"] = incorrect
                print(f"Incorrect response: {incorrect[:50]}...")
        
        # 📈 EXTRACTION SUMMARY
        print(f"\nEXTRACTION SUMMARY:")
        print(f"  Project Basics: {len(raw_data['project_basics'])} fields")
        print(f"  Target Skills: {len(raw_data['target_skills'])} skills")
        print(f"  AI Trainer: {len(raw_data['ai_trainer'])} fields")
        print(f"  AI Colleague: {len(raw_data['ai_colleague'])} fields")
        print(f"  Common Situations: {len(raw_data['common_situations'])} situations")
        print(f"  Success Metrics: {len(raw_data['success_metrics'])} metrics")
        print(f"  Common Mistakes: {len(raw_data['common_mistakes'])} mistakes")
        print(f"  Conversation Examples: {len(raw_data['conversation_examples'])} elements")
        
        return raw_data
    
    async def flexible_extract_from_document(self, document_content: str) -> Dict[str, Any]:
        """
        Extract raw details from document - NO LLM, just show user what was filled
        """
        # 🔍 Step 1: Extract raw data from document structure
        raw_data = self._extract_raw_data(document_content)
        
        # 🏷️ Step 2: Build initial template from raw data (NO LLM)
        extracted_details = self._build_template_from_raw_data(raw_data)
        
        return extracted_details
    
    def _build_template_from_raw_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Build comprehensive template using ALL extracted data with clear source tracking"""
        
        # 📊 Extract all data sections
        project = raw_data.get("project_basics", {})
        skills = raw_data.get("target_skills", [])
        learner = raw_data.get("learner_info", {})
        trainer = raw_data.get("ai_trainer", {})
        colleague = raw_data.get("ai_colleague", {})
        accuracy = raw_data.get("knowledge_accuracy", {})
        situations = raw_data.get("common_situations", [])
        corrections = raw_data.get("correction_preferences", {})
        metrics = raw_data.get("success_metrics", [])
        mistakes = raw_data.get("common_mistakes", [])
        examples = raw_data.get("conversation_examples", {})
        
        print(f"\nBUILDING TEMPLATE FROM EXTRACTED DATA:")
        
        # 🎯 SCENARIO UNDERSTANDING - Core scenario info
        main_topic = f"{project.get('Course', '')} - {project.get('Scenario', '')}".strip(' -')
        if not main_topic or main_topic == " - ":
            main_topic = "Training Scenario"
        
        scenario_understanding = {
            "main_topic": main_topic,
            "learning_situation": learner.get("Current Challenges", "Professional development training"),
            "target_skills": skills[:5] if skills else ["Professional communication", "Problem-solving", "Critical thinking"],
            "key_challenges": learner.get("Current Challenges", "Developing practical skills"),
            "domain": project.get("Training Domain", "General Training"),
            "extraction_source": "FROM_DOCUMENT" if (skills and project.get('Course')) else "MIXED_CONTENT"
        }
        print(f"  Scenario: {main_topic} ({scenario_understanding['extraction_source']})")
        
        # 👥 PARTICIPANT ROLES - Who plays what (flexible role detection)
        expert_role = None
        practice_role = None
        
        # Find expert role dynamically
        for key, value in trainer.items():
            if any(keyword in key.lower() for keyword in ['trainer', 'expert', 'teacher', 'instructor']) and 'role' in key.lower():
                expert_role = value
                break
        
        # Find practice role dynamically  
        for key, value in colleague.items():
            if any(keyword in key.lower() for keyword in ['colleague', 'stakeholder', 'partner', 'character', 'bot']) and 'role' in key.lower():
                practice_role = value
                break
        
        participant_roles = {
            "expert_role": expert_role or "Expert Trainer",
            "practice_role": practice_role or "Practice Partner", 
            "learner_role": learner.get("Job Roles", "Trainee"),
            "extraction_source": "FROM_DOCUMENT" if expert_role else "GENERATED_CONTENT"
        }
        print(f"  Expert: {participant_roles['expert_role']}")
        print(f"  Practice: {participant_roles['practice_role']}")
        
        # 📚 KNOWLEDGE BASE - What learners need to know  
        # Filter out table headers and artifacts
        dos_from_doc = [item["value"] for item in situations if item.get("value") and len(item["value"]) > 10 and not any(header in item["value"] for header in ["Correct Response", "Source Document", "Common Situation", "CELL_"])]
        donts_from_doc = [item["value"] for item in mistakes if item.get("value") and len(item["value"]) > 10 and not any(header in item["value"] for header in ["Why It's Wrong", "Correct Information", "Common Mistake", "CELL_"])]
        
        knowledge_base = {
            "dos": dos_from_doc[:8] if dos_from_doc else ["Follow best practices", "Communicate clearly", "Listen actively"],
            "donts": donts_from_doc[:8] if donts_from_doc else ["Avoid assumptions", "Don't rush decisions", "Don't ignore concerns"],
            "key_facts": [item["field"] + ": " + item["value"] for item in situations if "fact" in item.get("field", "").lower()][:8] or ["Document-based knowledge", "Professional standards"],
            "conversation_topics": trainer.get("Training Topics", "Professional development topics").split(", ") if trainer.get("Training Topics") else ["Core concepts", "Practical application"],
            "extraction_source": "FROM_DOCUMENT" if (dos_from_doc or donts_from_doc) else "GENERATED_CONTENT"
        }
        print(f"  Knowledge: {len(knowledge_base['dos'])} dos, {len(knowledge_base['donts'])} donts ({knowledge_base['extraction_source']})")
        
        # 🔧 COACHING RULES - How to train and correct
        coaching_rules = {
            "process_requirements": {
                "mentioned_methodology": trainer.get("Teaching Style", "Interactive learning approach"),
                "required_steps": "Learn, practice, apply, reflect",
                "validation_criteria": "Demonstrate understanding and application"
            },
            "correction_preferences": {
                "preferred_tone": corrections.get("Tone", "Gentle coaching"),
                "feedback_timing": corrections.get("Timing", "Immediately"), 
                "correction_method": corrections.get("Method", "Explain and guide")
            },
            "document_specific_mistakes": [
                {
                    "mistake_pattern": item["field"],
                    "why_problematic": item["value"],
                    "correct_approach": "Address with empathy and clear guidance"
                } for item in mistakes[:5] if item.get("field") and item.get("value")
            ],
            "extraction_source": "FROM_DOCUMENT" if corrections else "MIXED_CONTENT"
        }
        
        # 📊 SUCCESS METRICS - How to measure success
        # Filter out table headers from metrics
        clean_metrics = [item["field"] + ": " + item["value"] for item in metrics if item.get("field") and item.get("value") and not any(header in item["field"] for header in ["Metric", "Target", "How to Measure", "CELL_"])]
        success_metrics = {
            "kpis_for_interaction": clean_metrics[:5] if clean_metrics else ["Understanding demonstrated", "Skills applied effectively"],
            "learning_objectives": learner.get("Current Challenges", "Apply knowledge effectively in realistic scenarios"),
            "evaluation_criteria": [item["field"] for item in metrics if "criteria" in item.get("field", "").lower()] or ["Accuracy", "Completeness", "Practical application"],
            "extraction_source": "FROM_DOCUMENT" if metrics else "GENERATED_CONTENT"
        }
        
        # 💬 CONVERSATION DYNAMICS - How interactions should flow (flexible detection)
        typical_concerns = ""
        
        # Find typical concerns dynamically
        for key, value in colleague.items():
            if any(keyword in key.lower() for keyword in ['concerns', 'questions', 'interactions', 'challenges']) and value:
                typical_concerns = value
                break
        
        conversation_dynamics = {
            "learn_mode_purpose": f"{expert_role or 'Expert'} teaches {project.get('Scenario', 'relevant topics')}",
            "practice_mode_purpose": f"{practice_role or 'Practice partner'} needs guidance and support",
            "typical_interactions": typical_concerns.split(", ") if typical_concerns else ["Seeking guidance", "Asking for clarification"],
            "success_looks_like": "Learner provides helpful, accurate guidance",
            "failure_patterns": [item["field"] for item in mistakes][:3] if mistakes else ["Generic responses", "Dismissive attitude"],
            "difficulty_level": colleague.get("Difficulty Level of the Interactions", "Mixed"),
            "extraction_source": "FROM_DOCUMENT" if typical_concerns else "MIXED_CONTENT"
        }
        
        # 📝 CONTENT SPECIFICS - Detailed knowledge areas
        content_specifics = {
            "key_knowledge": trainer.get("Training Topics", "Core concepts").split(", ") if trainer.get("Training Topics") else ["Professional knowledge"],
            "procedures_mentioned": [item["value"] for item in situations if "procedure" in item.get("field", "").lower()][:3] or ["Standard procedures"],
            "policies_referenced": [k for k, v in accuracy.items() if v and "yes" in str(v).lower()][:3] or ["Company policies"],
            "examples_given": [examples.get("topic", "Practical examples")] if examples.get("topic") else ["Scenario-based examples"],
            "extraction_source": "FROM_DOCUMENT" if trainer.get("Training Topics") else "MIXED_CONTENT"
        }
        
        # 💬 CONVERSATION EXAMPLES - Real dialogue samples
        dialogue_samples = []
        if examples.get("ai_line"): dialogue_samples.append(examples["ai_line"])
        if examples.get("correct_response"): dialogue_samples.append(f"Correct: {examples['correct_response']}")
        if examples.get("incorrect_response"): dialogue_samples.append(f"Incorrect: {examples['incorrect_response']}")
        
        conversation_examples = {
            "dialogue_samples": dialogue_samples if dialogue_samples else ["Interactive dialogue"],
            "question_patterns": ["How should I handle...", "What's the best approach...", "What would you recommend..."],
            "response_patterns": [examples.get("correct_response", "Helpful guidance")] if examples.get("correct_response") else ["Supportive guidance"],
            "incorrect_patterns": [examples.get("incorrect_response", "Unhelpful response")] if examples.get("incorrect_response") else ["Dismissive responses"],
            "extraction_source": "FROM_DOCUMENT" if dialogue_samples else "GENERATED_CONTENT"
        }
        
        # 🔄 FEEDBACK MECHANISM - Persona-based responses (will be enhanced by LLM)
        feedback_mechanism = {
            "positive_closing": "Thank you, that really helps me understand better",
            "negative_closing": "I'm still not sure about this situation", 
            "neutral_closing": "I'll think about what you've said",
            "persona_context": practice_role or "Practice Partner",
            "extraction_source": "NEEDS_PERSONA_ENHANCEMENT"  # Flag for LLM to make persona-specific
        }
        
        # 🎲 VARIATIONS & CHALLENGES
        variations_challenges = {
            "scenario_variations": ["Different experience levels", "Various contexts"],
            "edge_cases": [item["value"] for item in mistakes if "challenge" in item.get("field", "").lower()][:3] or ["Challenging situations"],
            "difficulty_levels": [colleague.get("Difficulty Level of the Interactions", "Mixed")],
            "extraction_source": "FROM_DOCUMENT" if colleague.get("Difficulty Level of the Interactions") else "GENERATED_CONTENT"
        }
        
        # 🔍 KNOWLEDGE BASE INTEGRATION
        knowledge_base_integration = {
            "requires_knowledge_base": "true" if any("yes" in str(v).lower() for v in accuracy.values()) else "false",
            "fact_checking_areas": [k for k, v in accuracy.items() if v and "yes" in str(v).lower()] or ["General accuracy"],
            "accuracy_requirements": "Must align with document specifications",
            "extraction_source": "FROM_DOCUMENT" if accuracy else "GENERATED_CONTENT"
        }
        
        # 🏷️ COMPILE FINAL TEMPLATE
        template = {
            "scenario_understanding": scenario_understanding,
            "participant_roles": participant_roles,
            "knowledge_base": knowledge_base,
            "coaching_rules": coaching_rules,
            "success_metrics": success_metrics,
            "conversation_dynamics": conversation_dynamics,
            "content_specifics": content_specifics,
            "conversation_examples": conversation_examples,
            "feedback_mechanism": feedback_mechanism,
            "variations_challenges": variations_challenges,
            "knowledge_base_integration": knowledge_base_integration
        }
        
        print(f"\nTEMPLATE BUILT SUCCESSFULLY with {len(template)} sections")
        return template
    
    async def flexible_extract_from_prompt(self, user_prompt: str) -> Dict[str, Any]:
        """
        Create scenario template from user's direct prompt/description
        """
        extraction_prompt = f"""
        You are an expert at creating training scenarios from descriptions.
        
        Based on this scenario request, create a comprehensive training template:
        
        USER REQUEST:
        {user_prompt}
        
        Generate training scenario data in this JSON format:
        {{
            "scenario_understanding": {{
                "main_topic": "Inferred main topic from request",
                "learning_situation": "What learning situation this addresses",
                "target_skills": ["skill1", "skill2", "skill3"],
                "key_challenges": "What challenges this training solves"
            }},
            "knowledge_base": {{
                "dos": ["Best practice 1", "Best practice 2", "Best practice 3"],
                "donts": ["What to avoid 1", "What to avoid 2", "What to avoid 3"],
                "key_facts": ["Important fact 1", "Important fact 2", "Important fact 3"],
                "conversation_topics": ["Topic 1", "Topic 2", "Topic 3"]
            }},
            "coaching_rules": {{
                "process_requirements": {{
                    "mentioned_methodology": "Relevant methodology for this scenario",
                    "required_steps": "Steps learners should follow",
                    "validation_criteria": "Success criteria"
                }},
                "correction_preferences": {{
                    "preferred_tone": "Appropriate tone for this scenario",
                    "feedback_timing": "When to give feedback",
                    "correction_method": "How to handle mistakes"
                }}
            }},
            "success_metrics": {{
                "kpis_for_interaction": ["Key performance indicators"],
                "learning_objectives": "What success looks like",
                "evaluation_criteria": ["How to measure success"]
            }},
            "variations_challenges": {{
                "scenario_variations": ["Different scenario types"],
                "edge_cases": ["Challenging situations"],
                "difficulty_levels": ["Progressive difficulty options"]
            }},
            "feedback_mechanism": {{
                "positive_closing": "Satisfied response",
                "negative_closing": "Unsatisfied response",
                "neutral_closing": "Neutral response"
            }},
            "participant_roles": {{
                "learner_role": "Who is being trained",
                "expert_role": "Who would teach this",
                "practice_role": "Who learner would practice with"
            }},
            "conversation_dynamics": {{
                "learn_mode_purpose": "Expert teaching learner",
                "practice_mode_purpose": "Learner practicing with practice_role",
                "typical_interactions": ["realistic interaction1", "realistic interaction2"],
                "success_looks_like": "Indicators of successful interaction",
                "failure_patterns": ["common mistake1", "common mistake2"]
            }},
            "content_specifics": {{
                "key_knowledge": ["important concept1", "important concept2"],
                "procedures_mentioned": ["relevant procedure1", "relevant procedure2"],
                "policies_referenced": ["relevant policy1", "relevant policy2"],
                "examples_given": ["realistic scenario1", "realistic scenario2"]
            }},
            "conversation_examples": {{
                "dialogue_samples": ["sample conversation that might happen"],
                "question_patterns": ["types of questions that arise"],
                "response_patterns": ["types of responses needed"]
            }},
            "knowledge_base_integration": {{
                "requires_knowledge_base": "Does this scenario need fact-checking?",
                "fact_checking_areas": ["Areas requiring accuracy"],
                "accuracy_requirements": "What must be verified?"
            }}
        }}
        
        Make content specific and realistic for the requested scenario.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You create detailed training scenarios from user requests."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.7,
                max_tokens=16000
            )
            
            response_text = response.choices[0].message.content
            return self._parse_json_response(response_text)
            
        except Exception as e:
            print(f"Error in prompt extraction: {str(e)}")
            return self._get_fallback_prompt_data(user_prompt)
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from LLM response"""
        try:
            # Try to extract JSON from code blocks
            json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Try to parse entire response as JSON
            return json.loads(response_text)
            
        except json.JSONDecodeError:
            # Return error structure
            return {"error": "Failed to parse JSON response", "raw_response": response_text}
    
    def _get_fallback_document_data(self, document_content: str) -> Dict[str, Any]:
        """Fallback data when extraction fails"""
        return {
            "scenario_understanding": {
                "main_topic": "Document Analysis",
                "learning_situation": "Training based on uploaded document",
                "target_skills": ["Document comprehension", "Practical application"],
                "key_challenges": "Understanding and applying document content",
                "extraction_source": "GENERATED_CONTENT"
            },
            "participant_roles": {
                "expert_role": "Subject Matter Expert",
                "practice_role": "Practice Partner",
                "extraction_source": "GENERATED_CONTENT"
            },
            "knowledge_base": {
                "dos": ["Follow document guidelines", "Apply best practices"],
                "donts": ["Ignore document content", "Make assumptions"],
                "key_facts": ["Document-based knowledge"],
                "conversation_topics": ["Document content", "Practical application"],
                "extraction_source": "GENERATED_CONTENT"
            },
            "coaching_rules": {
                "process_requirements": {
                    "mentioned_methodology": "Document-based learning",
                    "required_steps": "Read, understand, apply",
                    "validation_criteria": "Accuracy to document content"
                },
                "correction_preferences": {
                    "preferred_tone": "Supportive",
                    "feedback_timing": "Immediate",
                    "correction_method": "Explain and guide"
                },
                "extraction_source": "GENERATED_CONTENT"
            },
            "success_metrics": {
                "kpis_for_interaction": ["Document comprehension", "Application accuracy"],
                "learning_objectives": "Understand and apply document content",
                "evaluation_criteria": ["Accuracy", "Completeness"],
                "extraction_source": "GENERATED_CONTENT"
            },
            "conversation_dynamics": {
                "learn_mode_purpose": "Expert explains document content",
                "practice_mode_purpose": "Learner practices applying knowledge",
                "typical_interactions": ["Questions about content", "Clarification requests"],
                "success_looks_like": "Learner can apply document knowledge",
                "failure_patterns": ["Misunderstanding key concepts"],
                "extraction_source": "GENERATED_CONTENT"
            },
            "content_specifics": {
                "key_knowledge": ["Document-based knowledge"],
                "procedures_mentioned": ["Standard procedures"],
                "policies_referenced": ["Relevant policies"],
                "examples_given": ["Document examples"],
                "extraction_source": "GENERATED_CONTENT"
            },
            "conversation_examples": {
                "dialogue_samples": ["Sample conversations from document"],
                "question_patterns": ["Types of questions"],
                "response_patterns": ["Expected responses"],
                "extraction_source": "GENERATED_CONTENT"
            },
            "feedback_mechanism": {
                "positive_closing": "Thank you, that helps clarify things",
                "negative_closing": "I'm still not clear on this",
                "neutral_closing": "I'll think about it",
                "extraction_source": "GENERATED_CONTENT"
            },
            "variations_challenges": {
                "scenario_variations": ["Different skill levels"],
                "edge_cases": ["Complex situations"],
                "difficulty_levels": ["Basic", "Intermediate", "Advanced"],
                "extraction_source": "GENERATED_CONTENT"
            },
            "knowledge_base_integration": {
                "requires_knowledge_base": "true",
                "fact_checking_areas": ["Document accuracy"],
                "accuracy_requirements": "Must match document content",
                "extraction_source": "GENERATED_CONTENT"
            }
        }
    
    def _get_fallback_prompt_data(self, user_prompt: str) -> Dict[str, Any]:
        """Fallback data when prompt extraction fails"""
        return {
            "scenario_understanding": {
                "main_topic": "Custom Training Scenario",
                "learning_situation": f"Training based on: {user_prompt[:100]}...",
                "target_skills": ["Scenario-specific skills", "Communication", "Problem-solving"],
                "key_challenges": "Developing practical skills",
                "extraction_source": "GENERATED_CONTENT"
            },
            "participant_roles": {
                "expert_role": "Trainer",
                "practice_role": "Practice Partner",
                "extraction_source": "GENERATED_CONTENT"
            },
            "knowledge_base": {
                "dos": ["Follow best practices", "Communicate clearly"],
                "donts": ["Make assumptions", "Rush decisions"],
                "key_facts": ["Core concepts", "Best practices"],
                "conversation_topics": ["Key concepts", "Practical application"],
                "extraction_source": "GENERATED_CONTENT"
            },
            "coaching_rules": {
                "process_requirements": {
                    "mentioned_methodology": "Interactive learning",
                    "required_steps": "Learn, practice, apply",
                    "validation_criteria": "Effective demonstration"
                },
                "correction_preferences": {
                    "preferred_tone": "Supportive",
                    "feedback_timing": "Immediate",
                    "correction_method": "Guide and explain"
                },
                "extraction_source": "GENERATED_CONTENT"
            },
            "success_metrics": {
                "kpis_for_interaction": ["Skill demonstration", "Understanding"],
                "learning_objectives": "Develop practical skills",
                "evaluation_criteria": ["Effectiveness", "Accuracy"],
                "extraction_source": "GENERATED_CONTENT"
            },
            "conversation_dynamics": {
                "learn_mode_purpose": "Trainer teaches key concepts",
                "practice_mode_purpose": "Learner practices skills",
                "typical_interactions": ["Learning conversations", "Practice scenarios"],
                "success_looks_like": "Effective skill demonstration",
                "failure_patterns": ["Common learning mistakes"],
                "extraction_source": "GENERATED_CONTENT"
            },
            "content_specifics": {
                "key_knowledge": ["Core concepts", "Best practices"],
                "procedures_mentioned": ["Standard procedures"],
                "policies_referenced": ["Relevant guidelines"],
                "examples_given": ["Practical examples"],
                "extraction_source": "GENERATED_CONTENT"
            },
            "conversation_examples": {
                "dialogue_samples": ["Sample conversations"],
                "question_patterns": ["Common questions"],
                "response_patterns": ["Expected responses"],
                "extraction_source": "GENERATED_CONTENT"
            },
            "feedback_mechanism": {
                "positive_closing": "That makes sense, thank you",
                "negative_closing": "I need more clarification",
                "neutral_closing": "I'll consider that",
                "extraction_source": "GENERATED_CONTENT"
            },
            "variations_challenges": {
                "scenario_variations": ["Different contexts"],
                "edge_cases": ["Challenging situations"],
                "difficulty_levels": ["Basic", "Intermediate", "Advanced"],
                "extraction_source": "GENERATED_CONTENT"
            },
            "knowledge_base_integration": {
                "requires_knowledge_base": "false",
                "fact_checking_areas": ["General accuracy"],
                "accuracy_requirements": "Reasonable accuracy",
                "extraction_source": "GENERATED_CONTENT"
            }
        }
    
    async def _enhance_template_with_llm(self, initial_template: Dict[str, Any], document_content: str) -> Dict[str, Any]:
        """
        Use LLM to clean extracted data and create persona-specific enhancements
        """
        try:
            if self.client is None:
                print("No LLM client - returning template without enhancement")
                return initial_template
            
            # 🎯 Focus on areas that need LLM enhancement
            persona_context = initial_template.get("participant_roles", {}).get("practice_role", "Practice Partner")
            
            enhancement_prompt = f"""
            You are enhancing a training scenario template. Focus on:
            
            1. PERSONA-SPECIFIC FEEDBACK: The AI plays "{persona_context}"
            2. CLEAN EXTRACTED DATA: Organize and improve extracted content
            3. FILL GAPS: Add missing elements intelligently
            
            CURRENT TEMPLATE:
            {json.dumps(initial_template, indent=2)}
            
            ORIGINAL DOCUMENT EXCERPT:
            {document_content[:2000]}...
            
            Enhance this template by:
            
            1. **Persona-Specific Feedback**: Create closing responses that match "{persona_context}" character:
               - positive_closing: How this persona would respond when satisfied
               - negative_closing: How this persona would respond when unsatisfied  
               - neutral_closing: How this persona would respond neutrally
               - Make them sound natural for this character type
            
            2. **Clean Knowledge Base**: Improve dos/donts to be more specific and actionable
            
            3. **Fill Missing Elements**: Add content where extraction_source is "GENERATED_CONTENT"
            
            Return enhanced template in same JSON structure. Keep all extraction_source markers.
            Mark enhanced sections as "AI_ENHANCED".
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You enhance training templates by cleaning data and creating persona-specific content."},
                    {"role": "user", "content": enhancement_prompt}
                ],
                temperature=0.7,
                max_tokens=16000
            )
            
            response_text = response.choices[0].message.content
            enhanced_template = self._parse_json_response(response_text)
            
            # ✅ Validate enhancement worked
            if isinstance(enhanced_template, dict) and "scenario_understanding" in enhanced_template:
                print(f"LLM ENHANCEMENT SUCCESSFUL")
                print(f"  Persona: {persona_context}")
                print(f"  Feedback enhanced: {enhanced_template.get('feedback_mechanism', {}).get('extraction_source', 'Unknown')}")
                return enhanced_template
            else:
                print(f"LLM enhancement failed - using initial template")
                return initial_template
                
        except Exception as e:
            print(f"Error in LLM enhancement: {str(e)}")
            return initial_template
    
    def _clean_extracted_text_for_llm(self, document_content: str) -> str:
        """Clean extracted text to send better content to LLM"""
        lines = document_content.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and markers
            if not line or line.startswith('TABLE_') and ('_START:' in line or '_END' in line):
                continue
                
            # Clean paragraph markers
            if line.startswith('PARAGRAPH_') and ':' in line:
                content = line.split(':', 1)[1].strip()
                if len(content) > 10:  # Only meaningful content
                    cleaned_lines.append(content)
                    
            # Clean row/cell markers and extract meaningful content
            elif line.startswith('ROW_') and 'CELL_' in line:
                # Extract field-value pairs from table rows
                if 'CELL_1:' in line:
                    parts = line.split('CELL_1:')
                    if len(parts) > 1:
                        field_part = parts[0]
                        if 'CELL_0:' in field_part:
                            field = field_part.split('CELL_0:')[-1].strip(' |').strip()
                        else:
                            field = field_part.replace('ROW_', '').split(':')[1].strip(' |').strip()
                        
                        value = parts[1].strip()
                        
                        if field and value and len(value) > 3:
                            cleaned_lines.append(f"{field}: {value}")
            
            # Keep conversation examples and other meaningful content
            elif any(keyword in line for keyword in ['Conversation Topic:', 'AI Colleague:', 'AI Stakeholder:', 'Correct Learner Response:', 'Incorrect Learner Response:']):
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)

    async def enhance_template_with_llm(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        SINGLE LLM CALL: Enhance extracted template and fill missing details
        """
        try:
            if self.client is None:
                return self._get_basic_enhancements(extracted_data)
            
            enhancement_prompt = f"""
            You are enhancing a training scenario template extracted from a document.
            
            EXTRACTED DATA:
            {json.dumps(extracted_data, indent=2)}
            
            Your task:
            1. Fill missing or weak sections (marked as "GENERATED_CONTENT")
            2. Enhance persona-specific feedback to sound natural
            3. Improve knowledge base items to be more specific
            4. Add missing conversation examples if needed
            
            Return enhanced template in same JSON structure.
            Mark your enhancements with "extraction_source": "AI_ENHANCED"
            Keep document-extracted content unchanged.
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You enhance training templates by filling gaps and improving extracted content."},
                    {"role": "user", "content": enhancement_prompt}
                ],
                temperature=0.7,
                max_tokens=16000
            )
            
            enhanced_template = self._parse_json_response(response.choices[0].message.content)
            
            if isinstance(enhanced_template, dict) and "scenario_understanding" in enhanced_template:
                return {
                    "enhanced_template": enhanced_template,
                    "template_enhancements": {
                        "persona_suggestions": {
                            "expert_persona": enhanced_template.get("participant_roles", {}).get("expert_role", "Expert Trainer"),
                            "practice_persona": enhanced_template.get("participant_roles", {}).get("practice_role", "Practice Partner"),
                            "extraction_source": "AI_ENHANCED"
                        },
                        "conversation_flows": {
                            "learn_mode_flow": enhanced_template.get("conversation_dynamics", {}).get("learn_mode_purpose", "Expert teaches concepts"),
                            "practice_mode_flow": enhanced_template.get("conversation_dynamics", {}).get("practice_mode_purpose", "Learner practices skills"),
                            "extraction_source": "AI_ENHANCED"
                        },
                        "feedback_mechanisms": {
                            "positive_responses": [enhanced_template.get("feedback_mechanism", {}).get("positive_closing", "Thank you for the guidance")],
                            "negative_responses": [enhanced_template.get("feedback_mechanism", {}).get("negative_closing", "I need more help")],
                            "neutral_responses": [enhanced_template.get("feedback_mechanism", {}).get("neutral_closing", "I'll think about it")],
                            "extraction_source": "AI_ENHANCED"
                        },
                        "extraction_source": "AI_ENHANCED"
                    },
                    "validation_notes": {
                        "completeness_score": "95%",
                        "missing_elements": [],
                        "suggestions": ["Template enhanced with persona-specific feedback", "Conversation flows optimized"]
                    }
                }
            else:
                return self._get_basic_enhancements(extracted_data)
                
        except Exception as e:
            print(f"Error in LLM enhancement: {str(e)}")
            return self._get_basic_enhancements(extracted_data)
    
    def _identify_enhancements(self, original: Dict, enhanced: Dict) -> List[str]:
        """Identify what was enhanced by LLM"""
        enhancements = []
        
        for section, data in enhanced.items():
            if isinstance(data, dict) and data.get("extraction_source") == "AI_ENHANCED":
                enhancements.append(f"Enhanced {section}")
        
        return enhancements
    
    def _get_basic_enhancements(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback enhancements when LLM unavailable"""
        return {
            "validated_extraction": extracted_data,
            "template_enhancements": {
                "persona_suggestions": {
                    "expert_persona": extracted_data.get('participant_roles', {}).get('expert_role', 'Expert Trainer'),
                    "practice_persona": extracted_data.get('participant_roles', {}).get('practice_role', 'Practice Partner'),
                    "extraction_source": "FALLBACK_GENERATED"
                },
                "conversation_flows": {
                    "learn_mode_flow": extracted_data.get('conversation_dynamics', {}).get('learn_mode_purpose', 'Expert teaches learner'),
                    "practice_mode_flow": extracted_data.get('conversation_dynamics', {}).get('practice_mode_purpose', 'Learner practices with partner'),
                    "extraction_source": "FALLBACK_GENERATED"
                },
                "feedback_mechanisms": {
                    "positive_responses": [extracted_data.get('feedback_mechanism', {}).get('positive_closing', 'Thank you')],
                    "negative_responses": [extracted_data.get('feedback_mechanism', {}).get('negative_closing', 'I need more help')],
                    "neutral_responses": [extracted_data.get('feedback_mechanism', {}).get('neutral_closing', 'I\'ll think about it')],
                    "extraction_source": "FALLBACK_GENERATED"
                },
                "extraction_source": "FALLBACK_GENERATED"
            },
            "validation_notes": {
                "completeness_score": "75% (Fallback)",
                "missing_elements": ["LLM enhancement unavailable"],
                "suggestions": ["Template created with fallback data"]
            },
            "enhancements_made": ["Fallback validation completed"]
        }
    
    async def generate_dynamic_scenarios(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dynamic scenario prompts using LLM"""
        try:
            if self.client is None:
                return self._get_fallback_scenarios(template_data)
            
            scenario_prompt = f"""
            Create dynamic training scenario prompts and personas from this template:
            
            TEMPLATE DATA:
            {json.dumps(template_data, indent=2)}
            
            Generate:
            1. LEARN_MODE: Expert trainer teaching learner
            2. ASSESS_MODE: Learner practicing with feedback
            3. TRY_MODE: Learner practicing without feedback
            4. SCENARIO-SPECIFIC PERSONAS: Realistic characters for this scenario
            5. SAMPLE CONVERSATIONS: Example dialogues showing persona interactions
            
            Each prompt should:
            - Use [PERSONA_PLACEHOLDER] for dynamic persona insertion
            - Use [LANGUAGE_INSTRUCTIONS] for language settings
            - Be persona-aware and adaptive
            - Include [CORRECT] tags for assessment feedback
            - Include [FINISH] tags for conversation endings
            
            Return JSON format:
            {{
                "learn_mode": "Full learn mode prompt with placeholders",
                "assess_mode": "Full assess mode prompt with placeholders", 
                "try_mode": "Full try mode prompt with placeholders",
                "recommended_personas": {{
                    "learn_mode_personas": [
                        {{
                            "name": "Character Name",
                            "description": "Character description",
                            "persona_type": "Learner type",
                            "gender": "male/female",
                            "age": 30,
                            "character_goal": "What they want to achieve",
                            "location": "Where they work",
                            "persona_details": "Personality traits",
                            "situation": "Current situation",
                            "business_or_personal": "business",
                            "background_story": "Their background"
                        }}
                    ],
                    "practice_mode_personas": [
                        {{
                            "name": "Character Name",
                            "description": "Character description", 
                            "persona_type": "Practice partner type",
                            "gender": "male/female",
                            "age": 35,
                            "character_goal": "What they need help with",
                            "location": "Where they work",
                            "persona_details": "Personality traits",
                            "situation": "Current challenge",
                            "business_or_personal": "business",
                            "background_story": "Their background",
                            "sample_opener": "How they start conversation"
                        }}
                    ]
                }},
                "sample_conversations": [
                    {{
                        "persona_name": "Character name",
                        "mode": "assess_mode",
                        "conversation": "AI: Opening line\nLearner: Response\nAI: Follow-up"
                    }}
                ]
            }}
            
            Make personas and conversations specific to this scenario, not generic.
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You create dynamic training scenario prompts with persona placeholders."},
                    {"role": "user", "content": scenario_prompt}
                ],
                temperature=0.7,
                max_tokens=16000
            )
            
            result = self._parse_json_response(response.choices[0].message.content)
            
            if isinstance(result, dict) and "learn_mode" in result:
                # Add scenario metadata
                result["scenario_metadata"] = {
                    "title": template_data.get('scenario_understanding', {}).get('main_topic', 'Training Scenario'),
                    "domain": template_data.get('scenario_understanding', {}).get('domain', 'General'),
                    "difficulty": "Mixed"
                }
                return result
            else:
                return self._get_fallback_scenarios(template_data)
                
        except Exception as e:
            print(f"Error generating dynamic scenarios: {str(e)}")
            return self._get_fallback_scenarios(template_data)
    
    def _convert_to_existing_format(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert flexible template format to existing template format"""
        scenario = template_data.get('scenario_understanding', {})
        roles = template_data.get('participant_roles', {})
        knowledge = template_data.get('knowledge_base', {})
        feedback = template_data.get('feedback_mechanism', {})
        
        return {
            "general_info": {
                "domain": scenario.get('domain', 'General'),
                "purpose_of_ai_bot": "Trainer/Customer",
                "target_audience": "Trainees",
                "preferred_language": "English"
            },
            "context_overview": {
                "scenario_title": scenario.get('main_topic', 'Training Scenario'),
                "learn_mode_description": f"AI acts as {roles.get('expert_role', 'expert trainer')}",
                "assess_mode_description": f"AI acts as {roles.get('practice_role', 'practice partner')}",
                "try_mode_description": "Same as assess mode without feedback",
                "purpose_of_scenario": scenario.get('learning_situation', 'Training scenario')
            },
            "persona_definitions": {
                "learn_mode_ai_bot": {
                    "role": roles.get('expert_role', 'Expert Trainer'),
                    "behavioral_traits": "Professional, supportive",
                    "goal": "Educate learners"
                },
                "assess_mode_ai_bot": {
                    "role": roles.get('practice_role', 'Practice Partner'),
                    "behavioral_traits": "Natural, conversational",
                    "goal": "Engage with learner"
                }
            },
            "dialogue_flow": {
                "learn_mode_initial_prompt": "Welcome! I'm here to help you learn.",
                "assess_mode_initial_prompt": "Hello, I need some guidance."
            },
            "knowledge_base": {
                "dos": knowledge.get('dos', []),
                "donts": knowledge.get('donts', []),
                "key_facts": knowledge.get('key_facts', []),
                "conversation_topics": knowledge.get('conversation_topics', [])
            },
            "feedback_mechanism": {
                "positive_closing": feedback.get('positive_closing', 'Thank you for your help'),
                "negative_closing": feedback.get('negative_closing', 'I need more guidance'),
                "neutral_closing": feedback.get('neutral_closing', 'I\'ll think about it'),
                "profanity_closing": feedback.get('profanity_closing', 'Please keep it professional'),
                "disrespectful_closing": feedback.get('disrespectful_closing', 'I expect respectful communication'),
                "emphasis_point": feedback.get('emphasis_point', 'the importance of proper guidance'),
                "polite_repeat_example": feedback.get('polite_repeat_example', 'Could you clarify that?'),
                "negative_closing_example": feedback.get('negative_closing_example', 'I don\'t feel I got the help I needed')
            }
        }
    
    def _generate_dynamic_learn_mode(self, scenario: Dict, roles: Dict, knowledge: Dict, dynamics: Dict) -> str:
        """Generate dynamic learn mode with persona-aware conversation patterns"""
        return f"""# {scenario.get('main_topic', 'Training Scenario')} - Learn Mode

[LANGUAGE_INSTRUCTIONS]

## Core Character Rules

- You are an AI playing the role of a {roles.get('expert_role', 'Expert Trainer')}
- NEVER play the learner role - only respond as the {roles.get('expert_role', 'Expert Trainer')}
- Adapt your teaching style based on [PERSONA_PLACEHOLDER] characteristics
- Keep responses under 30 words unless explaining complex concepts

## Character Background

[PERSONA_PLACEHOLDER]

## Dynamic Teaching Approach

- **If persona is experienced**: Use advanced terminology and focus on nuanced applications
- **If persona is new**: Use simple language and provide step-by-step guidance  
- **If persona is skeptical**: Provide evidence and real-world examples
- **If persona is eager**: Offer additional resources and advanced challenges

## Knowledge Base on {scenario.get('domain', 'this topic')}

### Key Facts:
{chr(10).join(f"- {fact}" for fact in knowledge.get('key_facts', ['Professional standards apply'])[:5])}

### Do's:
{chr(10).join(f"- {do}" for do in knowledge.get('dos', ['Follow best practices'])[:5])}

### Don'ts:
{chr(10).join(f"- {dont}" for dont in knowledge.get('donts', ['Avoid assumptions'])[:5])}

## Conversation Patterns

- **Curious persona**: "That's interesting! Let me explain why..."
- **Practical persona**: "Here's how you'd apply this in real situations..."
- **Analytical persona**: "The key factors to consider are..."
- **Results-focused persona**: "This directly impacts your success by..."

## Conversation Closing

- When learner shows understanding: "Excellent! You've grasped the key concepts. [FINISH]"
- When learner needs more help: "Let's explore this further to ensure clarity. [FINISH]"
- When providing resources: "Here are some additional materials to deepen your knowledge. [FINISH]"""

    def _generate_dynamic_assess_mode(self, scenario: Dict, roles: Dict, knowledge: Dict, dynamics: Dict, feedback: Dict) -> str:
        """Generate dynamic assess mode with persona-driven conversations and feedback"""
        return f"""# {scenario.get('main_topic', 'Training Scenario')} - Assessment Mode

[LANGUAGE_INSTRUCTIONS]

## Core Character Rules

- You are an AI playing the role of a {roles.get('practice_role', 'Practice Partner')}
- NEVER play the trainer role - only respond as the {roles.get('practice_role', 'Practice Partner')}
- Adapt your behavior and concerns based on [PERSONA_PLACEHOLDER] characteristics
- Keep responses under 50 words unless explaining a complex situation

## Character Background

[PERSONA_PLACEHOLDER]

## Dynamic Persona Behaviors

- **If persona is anxious**: Express worries and seek reassurance frequently
- **If persona is confident**: Challenge suggestions and ask probing questions
- **If persona is inexperienced**: Ask basic questions and need step-by-step guidance
- **If persona is busy/stressed**: Want quick, practical solutions
- **If persona is detail-oriented**: Ask for specifics and clarifications

## Conversation Starters by Persona Type

- **Worried persona**: "I'm really concerned about {scenario.get('key_challenges', 'this situation')}. What should I do?"
- **Skeptical persona**: "I've tried similar approaches before and they didn't work. Why would this be different?"
- **Eager persona**: "I want to handle this perfectly. What's the best approach?"
- **Overwhelmed persona**: "There's so much to consider here. Where do I even start?"

## Areas to Explore

{chr(10).join(f"- {topic}" for topic in dynamics.get('typical_interactions', ['Seeking guidance', 'Asking for clarification'])[:4])}

## Fact-Checking Responses

Compare learner responses against:
{chr(10).join(f"- {fact}" for fact in knowledge.get('key_facts', ['Professional standards'])[:3])}

## Feedback System

When learner provides unhelpful response:
1. React naturally as your persona would
2. Add: "[CORRECT] {feedback.get('emphasis_point', 'I need better guidance')} [CORRECT]"

## Conversation Closing

- **Satisfied**: "{feedback.get('positive_closing', 'Thank you, that really helps!')} [FINISH]"
- **Still concerned**: "{feedback.get('negative_closing', 'I still need more guidance on this.')} [FINISH]"
- **Partially satisfied**: "{feedback.get('neutral_closing', 'Ill think about what youve said.')} [FINISH]"
- **If unhelpful**: "I don't feel I got the guidance I needed. [FINISH]"""

    def _generate_dynamic_try_mode(self, scenario: Dict, roles: Dict, knowledge: Dict, dynamics: Dict, feedback: Dict) -> str:
        """Generate dynamic try mode with natural persona interactions"""
        return f"""# {scenario.get('main_topic', 'Training Scenario')} - Try Mode

[LANGUAGE_INSTRUCTIONS]

## Core Character Rules

- You are an AI playing the role of a {roles.get('practice_role', 'Practice Partner')}
- NEVER play the trainer role - only respond as the {roles.get('practice_role', 'Practice Partner')}
- Adapt your personality and responses based on [PERSONA_PLACEHOLDER] characteristics
- Engage naturally without providing coaching feedback

## Character Background

[PERSONA_PLACEHOLDER]

## Dynamic Persona Responses

- **If persona is grateful**: Show appreciation and ask follow-up questions
- **If persona is resistant**: Push back gently and express doubts
- **If persona is collaborative**: Build on suggestions and offer additional context
- **If persona is independent**: Prefer to figure things out but appreciate input

## Natural Conversation Flow

- Start with persona-appropriate concern or question
- React authentically to learner's guidance
- Ask follow-up questions that match persona's style
- Show personality through word choice and tone

## Persona-Driven Reactions

- **Analytical persona**: "That makes sense logically, but how does it work in practice?"
- **Emotional persona**: "I feel better about this now, but what if it doesn't work?"
- **Practical persona**: "Okay, so the next step would be to..."
- **Cautious persona**: "I appreciate the advice, but I'm still worried about..."

## Conversation Closing

- **Satisfied**: "{feedback.get('positive_closing', 'Thank you, that really helps!')} [FINISH]"
- **Still uncertain**: "{feedback.get('negative_closing', 'I still have some concerns about this.')} [FINISH]"
- **Neutral**: "{feedback.get('neutral_closing', 'Ill consider what youve said.')} [FINISH]"""


    
    async def simulate_conversation(self, template_data: Dict[str, Any], persona_details: Dict[str, str], mode: str = "assess_mode") -> Dict[str, Any]:
        """Simulate a conversation with a specific persona to show scenario creators what to expect"""
        try:
            if self.client is None:
                return self._get_mock_conversation(template_data, persona_details, mode)
            
            scenario = template_data.get('scenario_understanding', {})
            roles = template_data.get('participant_roles', {})
            knowledge = template_data.get('knowledge_base', {})
            
            simulation_prompt = f"""
            Simulate a realistic conversation for this training scenario:
            
            SCENARIO: {scenario.get('main_topic', 'Training Scenario')}
            MODE: {mode}
            
            PERSONA PLAYING:
            Name: {persona_details.get('name', 'Character')}
            Age: {persona_details.get('age', 30)}
            Gender: {persona_details.get('gender', 'neutral')}
            Role: {persona_details.get('persona_type', 'Practice Partner')}
            Goal: {persona_details.get('character_goal', 'Get guidance')}
            Situation: {persona_details.get('situation', 'Needs help')}
            Background: {persona_details.get('background_story', 'Professional seeking guidance')}
            Personality: {persona_details.get('persona_details', 'Natural conversation')}
            
            CONVERSATION RULES:
            - AI plays: {roles.get('practice_role' if 'assess' in mode or 'try' in mode else 'expert_role', 'Character')}
            - Show 4-5 realistic exchanges
            - Demonstrate persona's personality, age, and background
            - Include natural reactions based on their situation and goals
            
            Generate conversation in this format:
            AI: [Character's opening line]
            Learner: [Realistic learner response]
            AI: [Character's reaction]
            Learner: [Another learner response]
            AI: [Character's follow-up]
            
            Make it feel natural and show the persona's unique characteristics, age, and professional context.
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You simulate realistic training conversations that demonstrate detailed persona characteristics."},
                    {"role": "user", "content": simulation_prompt}
                ],
                temperature=0.7,
                max_tokens=16000
            )
            
            conversation_text = response.choices[0].message.content
            
            return {
                "persona": persona_details,
                "mode": mode,
                "conversation": conversation_text,
                "scenario_title": scenario.get('main_topic', 'Training Scenario')
            }
            
        except Exception as e:
            print(f"Error simulating conversation: {str(e)}")
            return self._get_mock_conversation(template_data, persona_details, mode)
    
    def _get_mock_conversation(self, template_data: Dict[str, Any], persona_details: Dict[str, str], mode: str) -> Dict[str, Any]:
        """Generate mock conversation when LLM is unavailable"""
        scenario = template_data.get('scenario_understanding', {})
        persona_name = persona_details.get('name', 'Character')
        age = persona_details.get('age', 30)
        
        mock_conversation = f"""AI: {persona_details.get('sample_opener', 'Hello, I need some guidance on this situation.')}
Learner: I'd be happy to help, {persona_name}. Can you tell me more about what's concerning you?
AI: Well, given my background in {persona_details.get('situation', 'this area')}, I'm not sure if I'm handling this {scenario.get('domain', 'situation')} correctly.
Learner: What specific aspect would you like to focus on?
AI: {persona_details.get('persona_details', 'I just want to make sure I do the right thing')}. My goal is to {persona_details.get('character_goal', 'handle this properly')}."""
        
        return {
            "persona": persona_details,
            "mode": mode,
            "conversation": mock_conversation,
            "scenario_title": scenario.get('main_topic', 'Training Scenario')
        }

    async def generate_dynamic_scenarios(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate dynamic scenario prompts using LLM"""
        try:
            if self.client is None:
                return self._get_fallback_scenarios(template_data)
            
            scenario_prompt = f"""
            Create dynamic training scenario prompts and personas from this template:
            
            TEMPLATE DATA:
            {json.dumps(template_data, indent=2)}
            
            Generate:
            1. LEARN_MODE: Expert trainer teaching learner
            2. ASSESS_MODE: Learner practicing with feedback
            3. TRY_MODE: Learner practicing without feedback
            4. SCENARIO-SPECIFIC PERSONAS: Realistic characters for this scenario
            5. SAMPLE CONVERSATIONS: Example dialogues showing persona interactions
            
            Each prompt should:
            - Use [PERSONA_PLACEHOLDER] for dynamic persona insertion
            - Use [LANGUAGE_INSTRUCTIONS] for language settings
            - Be persona-aware and adaptive
            - Include [CORRECT] tags for assessment feedback
            - Include [FINISH] tags for conversation endings
            
            Return JSON format:
            {{
                "learn_mode": "Full learn mode prompt with placeholders",
                "assess_mode": "Full assess mode prompt with placeholders", 
                "try_mode": "Full try mode prompt with placeholders",
                "recommended_personas": {{
                    "learn_mode_personas": [
                        {{
                            "name": "Character Name",
                            "description": "Character description",
                            "persona_type": "Learner type",
                            "gender": "male/female",
                            "age": 30,
                            "character_goal": "What they want to achieve",
                            "location": "Where they work",
                            "persona_details": "Personality traits",
                            "situation": "Current situation",
                            "business_or_personal": "business",
                            "background_story": "Their background"
                        }}
                    ],
                    "practice_mode_personas": [
                        {{
                            "name": "Character Name",
                            "description": "Character description", 
                            "persona_type": "Practice partner type",
                            "gender": "male/female",
                            "age": 35,
                            "character_goal": "What they need help with",
                            "location": "Where they work",
                            "persona_details": "Personality traits",
                            "situation": "Current challenge",
                            "business_or_personal": "business",
                            "background_story": "Their background",
                            "sample_opener": "How they start conversation"
                        }}
                    ]
                }},
                "sample_conversations": [
                    {{
                        "persona_name": "Character name",
                        "mode": "assess_mode",
                        "conversation": "AI: Opening line\nLearner: Response\nAI: Follow-up"
                    }}
                ]
            }}
            
            Make personas and conversations specific to this scenario, not generic.
            """
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You create dynamic training scenario prompts with persona placeholders."},
                    {"role": "user", "content": scenario_prompt}
                ],
                temperature=0.7,
                max_tokens=16000
            )
            
            result = self._parse_json_response(response.choices[0].message.content)
            
            if isinstance(result, dict) and "learn_mode" in result:
                # Add scenario metadata
                result["scenario_metadata"] = {
                    "title": template_data.get('scenario_understanding', {}).get('main_topic', 'Training Scenario'),
                    "domain": template_data.get('scenario_understanding', {}).get('domain', 'General'),
                    "difficulty": "Mixed"
                }
                return result
            else:
                return self._get_fallback_scenarios(template_data)
                
        except Exception as e:
            print(f"Error generating dynamic scenarios: {str(e)}")
            return self._get_fallback_scenarios(template_data)

    def _get_fallback_scenarios(self, template_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback scenarios when generation fails"""
        scenario = template_data.get('scenario_understanding', {})
        roles = template_data.get('participant_roles', {})
        
        return {
            "learn_mode": "Fallback: LLM generation failed",
            "assess_mode": "Fallback: LLM generation failed", 
            "try_mode": "Fallback: LLM generation failed",
            "recommended_personas": {"learn_mode_personas": [], "practice_mode_personas": []},
            "scenario_metadata": {
                "title": scenario.get('main_topic', 'Training Scenario'),
                "domain": scenario.get('domain', 'General'),
                "difficulty": "Mixed"
            }
        }