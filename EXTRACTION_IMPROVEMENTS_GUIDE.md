# Extraction System Improvements Guide

## 🎯 Goal

Improve `extract_scenario_info()` to capture ALL context needed for:
- Dynamic persona generation
- Rich prompt creation
- Learn/Assess/Try mode prompts
- Coaching system
- Evaluation system

---

## 📊 Current Extraction vs What We Need

### Current Extraction (Simplified):
```python
template_data = {
    "general_info": {
        "domain": "Pharmaceutical Sales",
        "title": "IMPACT Sales Training"
    },
    "persona_definitions": {
        "assess_mode_ai_bot": {
            "name": "Dr. Archana Pandey",
            "age": 42,
            "role": "Gynecologist",
            "description": "..."
        }
    },
    "domain_knowledge": {
        "key_facts": [...],
        "dos": [...],
        "donts": [...]
    }
}
```

### What We Need (Enhanced):
```python
template_data = {
    "template_id": "uuid",
    "title": "IMPACT Sales Training for EO-Dine",
    "description": "FSO practices pitching to gynecologists",
    
    # ===== MODE DESCRIPTIONS (NEW) =====
    "learn_mode": {
        "what_happens": "Expert trainer teaches IMPACT methodology",
        "ai_bot_role": "Sales trainer teaching methodology",
        "learner_role": "FSO learning to pitch",
        "teaching_focus": "How to use IMPACT steps effectively",
        "methods": ["IMPACT"],  # Named methodologies
        "uses_vector_db": true  # Does it need supporting docs?
    },
    
    "assess_mode": {
        "what_happens": "FSO practices pitching EO-Dine to doctor",
        "learner_role": "FSO practicing pitch",
        "context": "Doctor's office, busy OPD",
        
        # ===== PERSONA TYPES (NEW - not instances) =====
        "persona_types": [
            {
                "type": "Experienced Gynecologist",
                "description": "Senior doctor, evidence-driven, time-conscious",
                "use_case": "Teaches FSO to handle experienced doctors",
                "key_characteristics": {
                    "specialty": "Gynecology - Endometriosis",
                    "decision_style": "Analytical, needs evidence",
                    "time_availability": "Limited, very busy",
                    "current_solution": "Uses Dienogest",
                    "pain_points": ["Irregular bleeding", "Bone loss"]
                }
            }
            # Could have multiple persona types for variations
        ]
    },
    
    "try_mode": {
        "same_as_assess": true,
        "coaching_enabled": true
    },
    
    # ===== DOMAIN KNOWLEDGE (ENHANCED) =====
    "domain_knowledge": {
        # Methodology
        "methodology": "IMPACT",  # Named methodology if exists
        "methodology_steps": [
            "Introduce yourself and establish rapport",
            "Motivate by identifying needs",
            "Present product with evidence",
            "Address objections with data",
            "Close with clear next steps",
            "Thank and schedule follow-up"
        ],
        
        # Product/Subject Matter
        "subject_matter": {
            "type": "pharmaceutical_product",  # or "policy", "service", etc.
            "name": "EO-Dine",
            "main_points": [...],
            "key_benefits": [...],
            "evidence": [...]
        },
        
        # Learning Content
        "key_facts": [...],  # Facts learner must know
        "dos": [...],
        "donts": [...],
        "conversation_topics": [...],
        
        # ===== EVALUATION CRITERIA (NEW) =====
        "evaluation_criteria": {
            "what_to_evaluate": [
                "Follows IMPACT steps in order",
                "Addresses objections with evidence",
                "Provides accurate product data",
                "Maintains professional tone"
            ],
            "scoring_weights": {
                "methodology_adherence": 30,
                "objection_handling": 20,
                "factual_accuracy": 25,
                "communication_skills": 25
            },
            "common_mistakes": [
                "Skips Motivate step",
                "Gives vague claims without data",
                "Doesn't handle time pressure"
            ]
        },
        
        # ===== COACHING RULES (NEW) =====
        "coaching_rules": {
            "when_coach_appears": [
                "After methodology violation",
                "After factual error",
                "After poor objection handling"
            ],
            "coaching_style": "Gentle and supportive",
            "what_to_catch": [
                "Methodology violations",
                "Factual inaccuracies",
                "Poor objection handling",
                "Inappropriate tone"
            ],
            "correction_patterns": {
                "skipped_step": "You need to {step_name} before moving forward",
                "vague_claim": "Provide specific evidence, not general claims",
                "wrong_fact": "That's incorrect. The correct information is {correct_fact}"
            }
        }
    },
    
    # ===== ARCHETYPE (existing, keep as-is) =====
    "archetype_classification": {
        "primary_archetype": "PERSUASION",
        "confidence_score": 0.85
    },
    
    # ===== CONTEXT OVERVIEW (existing, enhance) =====
    "context_overview": {
        "scenario_description": "...",
        "conversation_setting": "...",
        "goals": "..."
    }
}
```

---

## 🔍 What Extraction Needs to Do

### Task 1: Extract Mode Descriptions

**From document text, identify:**

1. **Learn Mode:**
   - What happens? (training, teaching, explaining)
   - Who is AI? (trainer, expert, instructor)
   - Who is learner? (FSO, employee, student)
   - What's being taught? (methodology, policy, skills)
   - Named methodology? (IMPACT, SPIN, KYC, etc.)

2. **Assess Mode:**
   - What happens? (practice conversation, simulation)
   - Who is AI? (customer, doctor, colleague)
   - Who is learner? (sales rep, employee, agent)
   - What's the context? (office, store, phone)

3. **Try Mode:**
   - Is it different from assess? (usually same)
   - Is coaching enabled? (yes/no)

**Example from pharma doc:**
```
"The FSO will learn the IMPACT methodology from an expert trainer..."
→ learn_mode: {
    "what_happens": "Expert trainer teaches IMPACT",
    "ai_bot_role": "Sales trainer",
    "methods": ["IMPACT"]
}

"Then practice pitching to Dr. Archana Pandey, a gynecologist..."
→ assess_mode: {
    "what_happens": "Practice pitch to gynecologist",
    "ai_bot_role": "Gynecologist being pitched to"
}
```

### Task 2: Extract Persona TYPES (not instances)

**Critical distinction:**

**Persona TYPE** (category):
- "Experienced Gynecologist" 
- "First-time Mother"
- "Bias Victim"

**Persona INSTANCE** (specific character):
- "Dr. Archana Pandey, 42, female, at Jawahar Medical"
- "Priya Sharma, 28, expecting first child"
- "Maya, team member who experienced exclusion"

**From document, extract:**

1. **What TYPE of character is this?**
   - Professional role/category
   - Life situation
   - Social role

2. **Key characteristics of this TYPE:**
   - Expertise level
   - Decision-making style
   - What they care about
   - What frustrates them

3. **NOT the specific name/age/gender** (that's generated later)

**Example from pharma doc:**
```
"Dr. Archana Pandey is an experienced gynecologist who treats 
endometriosis patients. She currently uses Dienogest but has 
concerns about irregular bleeding and bone loss..."

→ Extract as PERSONA TYPE:
{
    "type": "Experienced Gynecologist",
    "description": "Senior doctor specializing in endometriosis",
    "key_characteristics": {
        "specialty": "Gynecology - Endometriosis",
        "decision_style": "Evidence-based, analytical",
        "current_solution": "Uses Dienogest",
        "pain_points": ["Irregular bleeding", "Bone loss"],
        "time_constraints": "Very busy, limited time"
    }
}

NOTE: Name "Dr. Archana Pandey" becomes part of the TYPE description,
but we can generate "Dr. Rajesh Kumar" or "Dr. Meera Shah" 
with same characteristics later!
```

### Task 3: Extract Domain Knowledge Structure

**From document, identify and structure:**

1. **Named Methodology?**
   - IMPACT, SPIN, KYC, Socratic method, etc.
   - If yes → Extract steps/stages

2. **Subject Matter:**
   - Product (EO-Dine)
   - Policy (DEI policy)
   - Service (maternity package)
   - Process (complaint handling)

3. **Learning Content:**
   - Key facts (what learner must know)
   - Dos and Don'ts
   - Topics to cover

4. **Evaluation Criteria:**
   - What makes a good conversation?
   - What are common mistakes?
   - How to score?

5. **Coaching Rules:**
   - When should coach intervene?
   - What should coach say?
   - What mistakes to catch?

**Example extraction:**

```
Document says:
"The FSO should follow IMPACT: Introduce, Motivate, Present, 
Address, Close, Thank. They must provide evidence-based data, 
not vague claims. Common mistakes include skipping the Motivate 
step and giving generic statements."

→ Extract:
{
    "methodology": "IMPACT",
    "methodology_steps": ["Introduce", "Motivate", "Present", ...],
    "dos": ["Provide evidence-based data", "Be specific"],
    "donts": ["Make vague claims", "Give generic statements"],
    "common_mistakes": ["Skipping Motivate step", "Generic statements"],
    "coaching_rules": {
        "what_to_catch": ["Skipped methodology steps", "Vague claims"]
    }
}
```

### Task 4: Identify Detail Category Hints

**OPTIONAL but helpful:**

From document context, suggest which detail categories might be relevant.

**Example:**
```
Document mentions:
- "Dr. Archana has a surgery scheduled" → time_constraints
- "She's seen this FSO before" → past_experiences / sales_rep_history
- "She treats endometriosis patients" → professional_context
- "Family considerations important" → family_context

→ Extract hint:
{
    "suggested_detail_categories": [
        "professional_context",
        "time_constraints", 
        "sales_rep_history"
    ]
}
```

**Note:** LLM will still make final decision, but this helps!

---

## 🛠️ Implementation Strategy

### Approach: Multi-Pass LLM Extraction

Instead of one big prompt, do **multiple focused extractions**:

```python
async def extract_scenario_info_v2(document_text, client):
    """
    Enhanced extraction with multiple passes
    """
    
    # Pass 1: Basic info + mode identification
    basic_info = await extract_basic_info_and_modes(document_text, client)
    
    # Pass 2: Persona type extraction (for assess mode)
    persona_types = await extract_persona_types(document_text, client)
    
    # Pass 3: Domain knowledge extraction
    domain_knowledge = await extract_domain_knowledge(document_text, client)
    
    # Pass 4: Coaching & evaluation extraction
    coaching_eval = await extract_coaching_and_evaluation(document_text, client)
    
    # Pass 5: Archetype classification (existing)
    archetype = await classify_archetype(document_text, client)
    
    # Combine all
    template_data = {
        **basic_info,
        "assess_mode": {
            **basic_info.get("assess_mode", {}),
            "persona_types": persona_types
        },
        "domain_knowledge": {
            **domain_knowledge,
            **coaching_eval
        },
        "archetype_classification": archetype
    }
    
    return template_data
```

**Why multiple passes?**
- ✅ Each pass focuses on ONE thing (better quality)
- ✅ Can run in parallel (faster)
- ✅ Easier to debug (know which pass failed)
- ✅ Can cache/reuse parts

---

## 📝 Implementation Details

### Pass 1: Basic Info + Modes

**Purpose:** Extract title, description, and what happens in each mode

**Prompt:**

```python
extraction_prompt = f"""
Analyze this training scenario document and extract structured information.

**Document:**
{document_text}

**Task:** Extract the following information:

1. **General Info:**
   - Title (short, descriptive)
   - Description (1-2 sentences)
   - Domain (e.g., "Pharmaceutical Sales", "DEI Training", "Customer Service")

2. **Learn Mode:**
   - What happens? (what is being taught/learned)
   - AI bot role (who is teaching - trainer, expert, instructor)
   - Learner role (who is learning - FSO, employee, student)
   - Teaching focus (what's the main learning objective)
   - Named methodology? (e.g., IMPACT, SPIN, KYC) - if mentioned
   - Uses vector DB? (does it reference supporting documents)

3. **Assess Mode:**
   - What happens? (what is being practiced/simulated)
   - AI bot role (who is the AI playing - customer, doctor, colleague)
   - Learner role (who is the learner playing)
   - Context (where/when does this happen - office, phone, etc.)

4. **Try Mode:**
   - Same as assess mode? (yes/no)
   - Coaching enabled? (yes/no)

**Output Format:** Return ONLY valid JSON:
{{
    "title": "...",
    "description": "...",
    "general_info": {{
        "domain": "..."
    }},
    "learn_mode": {{
        "what_happens": "...",
        "ai_bot_role": "...",
        "learner_role": "...",
        "teaching_focus": "...",
        "methods": ["..."],  // List of named methodologies, if any
        "uses_vector_db": true/false
    }},
    "assess_mode": {{
        "what_happens": "...",
        "ai_bot_role": "...",
        "learner_role": "...",
        "context": "..."
    }},
    "try_mode": {{
        "same_as_assess": true/false,
        "coaching_enabled": true/false
    }}
}}
"""
```

### Pass 2: Persona Types

**Purpose:** Extract persona TYPE(s) for assess mode - NOT specific instances

**Prompt:**

```python
persona_extraction_prompt = f"""
Analyze this training scenario and extract PERSONA TYPE(S) for the assess mode.

**CRITICAL:** Extract the TYPE/CATEGORY of persona, NOT specific details like name/age.

**Document:**
{document_text}

**Task:** Identify the type(s) of characters the AI could play in assess mode.

**Example of TYPE vs INSTANCE:**
- TYPE: "Experienced Gynecologist" ✅
- INSTANCE: "Dr. Archana Pandey, 42 years old" ❌

**For each persona TYPE, extract:**
1. **Type name** (professional/social category)
2. **Description** (brief overview)
3. **Use case** (why this type is good for training)
4. **Key characteristics** (what defines this type):
   - Expertise/specialty area
   - Decision-making style
   - Current situation/approach
   - Pain points/concerns
   - Time availability
   - Any other defining traits

**Output Format:** Return ONLY valid JSON array:
[
    {{
        "type": "Experienced Gynecologist",
        "description": "Senior doctor specializing in endometriosis treatment",
        "use_case": "Teaches FSO to handle experienced, evidence-driven doctors",
        "key_characteristics": {{
            "specialty": "Gynecology - Endometriosis",
            "decision_style": "Analytical, evidence-based",
            "time_availability": "Limited, very busy",
            "current_solution": "Uses Dienogest",
            "pain_points": ["Irregular bleeding with Dienogest", "Bone loss concerns"],
            "decision_factors": ["Clinical evidence", "Safety profile", "Patient outcomes"]
        }}
    }}
]

**If document mentions multiple persona types (e.g., victim, perpetrator, bystander), extract ALL of them.**

**If document only describes one specific person, generalize to a type.**
"""
```

### Pass 3: Domain Knowledge

**Purpose:** Extract structured domain knowledge including methodology, facts, dos/donts

**Prompt:**

```python
domain_knowledge_prompt = f"""
Extract comprehensive domain knowledge from this training scenario.

**Document:**
{document_text}

**Task:** Extract the following:

1. **Named Methodology** (if exists):
   - Name (e.g., IMPACT, SPIN, KYC)
   - Steps/stages in order
   - Description of each step

2. **Subject Matter:**
   - Type (product, policy, service, process, concept)
   - Name
   - Main points to cover
   - Key benefits/features
   - Supporting evidence

3. **Learning Content:**
   - Key facts (what learner must know)
   - Dos (what to do)
   - Don'ts (what to avoid)
   - Conversation topics (what to discuss)

4. **Common Mistakes:**
   - What errors do learners typically make?
   - What should be avoided?

**Output Format:** Return ONLY valid JSON:
{{
    "methodology": "IMPACT" or null,
    "methodology_steps": [
        {{
            "step": "Introduce",
            "description": "Introduce yourself and establish rapport",
            "what_to_do": "Greet professionally, state purpose",
            "what_to_avoid": "Being too casual or overly formal"
        }},
        // ... more steps
    ],
    "subject_matter": {{
        "type": "pharmaceutical_product",
        "name": "EO-Dine",
        "main_points": ["...", "..."],
        "key_benefits": ["...", "..."],
        "evidence": ["...", "..."]
    }},
    "key_facts": ["...", "...", "..."],
    "dos": ["...", "...", "..."],
    "donts": ["...", "...", "..."],
    "conversation_topics": ["...", "..."],
    "common_mistakes": ["...", "...", "..."]
}}
"""
```

### Pass 4: Coaching & Evaluation

**Purpose:** Extract coaching rules and evaluation criteria

**Prompt:**

```python
coaching_eval_prompt = f"""
Extract coaching and evaluation information from this training scenario.

**Document:**
{document_text}

**Task 1 - Coaching Rules:**

Identify:
1. **When should coach appear?**
   - After what actions/mistakes?
   - Timing/triggers

2. **What should coach say?**
   - Correction patterns for common mistakes
   - Coaching style (gentle, direct, supportive, etc.)

3. **What mistakes should coach catch?**
   - Methodology violations
   - Factual errors
   - Communication issues

**Task 2 - Evaluation Criteria:**

Identify:
1. **What to evaluate:**
   - Specific behaviors/skills to assess

2. **Scoring weights:**
   - How important is each criterion (%)

3. **Success indicators:**
   - What makes a good performance

4. **Failure indicators:**
   - What makes a poor performance

**Output Format:** Return ONLY valid JSON:
{{
    "coaching_rules": {{
        "when_coach_appears": [
            "After methodology step is skipped",
            "After factual error is made",
            "After poor objection handling"
        ],
        "coaching_style": "Gentle and supportive",
        "what_to_catch": [
            "Methodology violations",
            "Factual inaccuracies",
            "Poor communication"
        ],
        "correction_patterns": {{
            "skipped_step": "You need to {{step_name}} before moving forward",
            "vague_claim": "Provide specific evidence, not general claims",
            "wrong_fact": "That's incorrect. The correct information is {{correct_fact}}"
        }}
    }},
    "evaluation_criteria": {{
        "what_to_evaluate": [
            "Follows methodology steps",
            "Provides accurate information",
            "Handles objections well"
        ],
        "scoring_weights": {{
            "methodology_adherence": 30,
            "factual_accuracy": 25,
            "objection_handling": 20,
            "communication_skills": 25
        }},
        "success_indicators": [
            "All methodology steps followed in order",
            "Strong evidence provided for claims",
            "Objections addressed with data"
        ],
        "failure_indicators": [
            "Skipped methodology steps",
            "Vague or incorrect information",
            "Unable to handle objections"
        ],
        "common_mistakes": [
            "Skipping Motivate step",
            "Making claims without evidence",
            "Getting defensive with objections"
        ]
    }}
}}
"""
```

---

## 🔧 Code Implementation

**File:** Create `core/scenario_extractor_v2.py` (don't replace existing!)

```python
"""
Enhanced Scenario Extractor V2
Multi-pass extraction for comprehensive scenario understanding
"""

import json
from typing import Dict, Any, List


class ScenarioExtractorV2:
    """
    Enhanced extraction that captures all context needed for:
    - Dynamic persona generation
    - Mode-specific prompts
    - Coaching system
    - Evaluation system
    """
    
    def __init__(self, client, model="gpt-4o"):
        self.client = client
        self.model = model
    
    async def extract_scenario_info(self, document_text: str) -> Dict[str, Any]:
        """
        Main extraction method - orchestrates multiple passes
        """
        import asyncio
        
        print("[EXTRACTION] Starting multi-pass extraction...")
        
        # Run all extraction passes in parallel for speed
        basic_info_task = self._extract_basic_info_and_modes(document_text)
        persona_types_task = self._extract_persona_types(document_text)
        domain_knowledge_task = self._extract_domain_knowledge(document_text)
        coaching_eval_task = self._extract_coaching_and_evaluation(document_text)
        
        # Wait for all to complete
        basic_info, persona_types, domain_knowledge, coaching_eval = await asyncio.gather(
            basic_info_task,
            persona_types_task,
            domain_knowledge_task,
            coaching_eval_task
        )
        
        print("[EXTRACTION] All passes complete, combining results...")
        
        # Combine results
        template_data = {
            **basic_info,
            "assess_mode": {
                **basic_info.get("assess_mode", {}),
                "persona_types": persona_types
            },
            "domain_knowledge": {
                **domain_knowledge,
                **coaching_eval
            }
        }
        
        # Add archetype classification (if not already present)
        if "archetype_classification" not in template_data:
            archetype = await self._classify_archetype(document_text)
            template_data["archetype_classification"] = archetype
        
        return template_data
    
    async def _extract_basic_info_and_modes(self, document_text: str) -> Dict[str, Any]:
        """Pass 1: Extract basic info and mode descriptions"""
        
        prompt = f"""
Analyze this training scenario document and extract structured information.

**Document:**
{document_text}

**Task:** Extract the following information:

1. **General Info:**
   - Title (short, descriptive)
   - Description (1-2 sentences)
   - Domain (e.g., "Pharmaceutical Sales", "DEI Training", "Customer Service")

2. **Learn Mode:**
   - What happens? (what is being taught/learned)
   - AI bot role (who is teaching - trainer, expert, instructor)
   - Learner role (who is learning - FSO, employee, student)
   - Teaching focus (what's the main learning objective)
   - Named methodology? (e.g., IMPACT, SPIN, KYC) - if mentioned
   - Uses vector DB? (does it reference supporting documents)

3. **Assess Mode:**
   - What happens? (what is being practiced/simulated)
   - AI bot role (who is the AI playing - customer, doctor, colleague)
   - Learner role (who is the learner playing)
   - Context (where/when does this happen - office, phone, etc.)

4. **Try Mode:**
   - Same as assess mode? (yes/no)
   - Coaching enabled? (yes/no)

**Output Format:** Return ONLY valid JSON:
{{
    "title": "...",
    "description": "...",
    "general_info": {{
        "domain": "..."
    }},
    "learn_mode": {{
        "what_happens": "...",
        "ai_bot_role": "...",
        "learner_role": "...",
        "teaching_focus": "...",
        "methods": ["..."],
        "uses_vector_db": true/false
    }},
    "assess_mode": {{
        "what_happens": "...",
        "ai_bot_role": "...",
        "learner_role": "...",
        "context": "..."
    }},
    "try_mode": {{
        "same_as_assess": true/false,
        "coaching_enabled": true/false
    }}
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You extract structured information from training scenario documents."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            result = self._parse_json_response(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"[ERROR] Basic info extraction failed: {e}")
            return self._get_fallback_basic_info()
    
    async def _extract_persona_types(self, document_text: str) -> List[Dict[str, Any]]:
        """Pass 2: Extract persona TYPE(s) - not specific instances"""
        
        prompt = f"""
Analyze this training scenario and extract PERSONA TYPE(S) for the assess mode.

**CRITICAL:** Extract the TYPE/CATEGORY of persona, NOT specific details like name/age.

**Document:**
{document_text}

**Task:** Identify the type(s) of characters the AI could play in assess mode.

**Example of TYPE vs INSTANCE:**
- TYPE: "Experienced Gynecologist" ✅
- INSTANCE: "Dr. Archana Pandey, 42 years old" ❌

**For each persona TYPE, extract:**
1. **Type name** (professional/social category)
2. **Description** (brief overview)
3. **Use case** (why this type is good for training)
4. **Key characteristics** (what defines this type):
   - Expertise/specialty area
   - Decision-making style
   - Current situation/approach
   - Pain points/concerns
   - Time availability
   - Any other defining traits

**Output Format:** Return ONLY valid JSON array:
[
    {{
        "type": "Experienced Gynecologist",
        "description": "Senior doctor specializing in endometriosis treatment",
        "use_case": "Teaches FSO to handle experienced, evidence-driven doctors",
        "key_characteristics": {{
            "specialty": "Gynecology - Endometriosis",
            "decision_style": "Analytical, evidence-based",
            "time_availability": "Limited, very busy",
            "current_solution": "Uses Dienogest",
            "pain_points": ["Irregular bleeding with Dienogest", "Bone loss concerns"],
            "decision_factors": ["Clinical evidence", "Safety profile", "Patient outcomes"]
        }}
    }}
]

**If document mentions multiple persona types (e.g., victim, perpetrator, bystander), extract ALL of them.**
**If document only describes one specific person, generalize to a type.**
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You extract persona types from training scenarios."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            result = self._parse_json_response(response.choices[0].message.content)
            
            # Ensure it's a list
            if isinstance(result, dict):
                result = [result]
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Persona type extraction failed: {e}")
            return []
    
    async def _extract_domain_knowledge(self, document_text: str) -> Dict[str, Any]:
        """Pass 3: Extract domain knowledge structure"""
        
        prompt = f"""
Extract comprehensive domain knowledge from this training scenario.

**Document:**
{document_text}

**Task:** Extract the following:

1. **Named Methodology** (if exists):
   - Name (e.g., IMPACT, SPIN, KYC)
   - Steps/stages in order
   - Description of each step

2. **Subject Matter:**
   - Type (product, policy, service, process, concept)
   - Name
   - Main points to cover
   - Key benefits/features
   - Supporting evidence

3. **Learning Content:**
   - Key facts (what learner must know)
   - Dos (what to do)
   - Don'ts (what to avoid)
   - Conversation topics (what to discuss)

4. **Common Mistakes:**
   - What errors do learners typically make?
   - What should be avoided?

**Output Format:** Return ONLY valid JSON:
{{
    "methodology": "IMPACT" or null,
    "methodology_steps": [
        {{
            "step": "Introduce",
            "description": "Introduce yourself and establish rapport",
            "what_to_do": "Greet professionally, state purpose",
            "what_to_avoid": "Being too casual or overly formal"
        }}
    ],
    "subject_matter": {{
        "type": "pharmaceutical_product",
        "name": "EO-Dine",
        "main_points": [],
        "key_benefits": [],
        "evidence": []
    }},
    "key_facts": [],
    "dos": [],
    "donts": [],
    "conversation_topics": [],
    "common_mistakes": []
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You extract domain knowledge from training documents."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            result = self._parse_json_response(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"[ERROR] Domain knowledge extraction failed: {e}")
            return {}
    
    async def _extract_coaching_and_evaluation(self, document_text: str) -> Dict[str, Any]:
        """Pass 4: Extract coaching rules and evaluation criteria"""
        
        prompt = f"""
Extract coaching and evaluation information from this training scenario.

**Document:**
{document_text}

**Task 1 - Coaching Rules:**
1. When should coach appear?
2. What should coach say?
3. What mistakes should coach catch?

**Task 2 - Evaluation Criteria:**
1. What to evaluate
2. Scoring weights
3. Success/failure indicators

**Output Format:** Return ONLY valid JSON:
{{
    "coaching_rules": {{
        "when_coach_appears": [],
        "coaching_style": "Gentle and supportive",
        "what_to_catch": [],
        "correction_patterns": {{}}
    }},
    "evaluation_criteria": {{
        "what_to_evaluate": [],
        "scoring_weights": {{}},
        "success_indicators": [],
        "failure_indicators": [],
        "common_mistakes": []
    }}
}}
"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You extract coaching and evaluation criteria."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            result = self._parse_json_response(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"[ERROR] Coaching/eval extraction failed: {e}")
            return {"coaching_rules": {}, "evaluation_criteria": {}}
    
    async def _classify_archetype(self, document_text: str) -> Dict[str, Any]:
        """Classify conversation archetype (existing logic)"""
        # Use existing archetype classification
        # This should already exist in your codebase
        return {
            "primary_archetype": "PERSUASION",
            "confidence_score": 0.8
        }
    
    def _parse_json_response(self, response_text: str) -> Any:
        """Parse JSON from LLM response"""
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(response_text)
        except Exception as e:
            print(f"[ERROR] JSON parsing failed: {e}")
            print(f"[DEBUG] Response was: {response_text[:500]}")
            return {}
    
    def _get_fallback_basic_info(self) -> Dict[str, Any]:
        """Fallback if extraction fails"""
        return {
            "title": "Training Scenario",
            "description": "Practice scenario",
            "general_info": {"domain": "general"},
            "learn_mode": {},
            "assess_mode": {},
            "try_mode": {}
        }
```

---

## ✅ Integration with Existing System

**Don't replace existing extraction! Add alongside:**

```python
# In your existing service file

# EXISTING (keep as-is)
async def extract_scenario_info(self, document_text):
    """Original extraction - keep for backwards compatibility"""
    # ... existing code ...
    pass

# NEW V2 (add this)
async def extract_scenario_info_v2(self, document_text):
    """Enhanced extraction with persona types, coaching, evaluation"""
    from core.scenario_extractor_v2 import ScenarioExtractorV2
    
    try:
        extractor = ScenarioExtractorV2(self.client, self.model)
        template_data = await extractor.extract_scenario_info(document_text)
        return template_data
    except Exception as e:
        print(f"[WARN] V2 extraction failed: {e}")
        print("[INFO] Falling back to V1 extraction")
        return await self.extract_scenario_info(document_text)
```

---

## 🧪 Testing

**Test with your pharma scenario:**

```python
# Test extraction
extractor = ScenarioExtractorV2(client)
result = await extractor.extract_scenario_info(pharma_document)

# Check results
print("Title:", result["title"])
print("Learn mode:", result["learn_mode"])
print("Assess mode:", result["assess_mode"])
print("Persona types:", result["assess_mode"]["persona_types"])
print("Domain knowledge:", result["domain_knowledge"])
print("Coaching rules:", result["domain_knowledge"]["coaching_rules"])
print("Evaluation:", result["domain_knowledge"]["evaluation_criteria"])
```

---

## 📋 Next Steps

1. ✅ Create `scenario_extractor_v2.py`
2. ✅ Test with existing scenarios
3. ✅ Verify persona types are extracted correctly
4. ✅ Check domain knowledge structure
5. ✅ Validate coaching/eval extraction

**Then:** Connect with persona generation system! 🎯
