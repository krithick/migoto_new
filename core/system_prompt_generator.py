"""
System Prompt Generator
Generates complete system prompts from template and persona data using LLM.
"""

import json
from typing import Dict, Any, Optional
from core.system_prompt_templates import (
    ARCHITECTURE_GUIDE,
    ARCHETYPE_TEMPLATES,
    get_generic_archetype_template
)



class SystemPromptGenerator:
    """
    Generates system prompts using single-pass LLM generation.
    Takes template_data + persona_data → produces rich system prompt.
    """
    
    def __init__(self, client, model="gpt-4o"):
        """
        Initialize the generator.
        
        Args:
            client: OpenAI/Azure client
            model: Model to use for generation
        """
        self.client = client
        self.model = model
        self.architecture_guide = ARCHITECTURE_GUIDE
    
    def _get_archetype_template(self, archetype: str) -> str:
        """
        Get archetype-specific template for Section 3.
        Extensible design - easy to add new archetypes.
        """
        if archetype in ARCHETYPE_TEMPLATES:
            return ARCHETYPE_TEMPLATES[archetype]
        else:
            print(f"[WARNING] Archetype '{archetype}' not specifically supported. Using generic template.")
            print(f"[INFO] Supported archetypes: {', '.join(ARCHETYPE_TEMPLATES.keys())}")
            print(f"[INFO] Consider adding a specific template for '{archetype}' for better quality.")
            return get_generic_archetype_template(archetype)
    async def generate_system_prompt(
        self,
        template_data: Dict[str, Any],
        persona_data: Dict[str, Any],
        mode: str = "assess_mode"
    ) -> str:
        """
        Main entry point: Generate complete system prompt.
        
        Args:
            template_data: Extracted scenario template (from extraction)
            persona_data: Generated persona instance (from persona generator)
            mode: "assess_mode", "learn_mode", or "try_mode"
        
        Returns:
            Complete system prompt as string (ready to use)
        
        Example:
            generator = SystemPromptGenerator(client)
            prompt = await generator.generate_system_prompt(
                template_data=eo_dine_template,
                persona_data=dr_priya_persona,
                mode="assess_mode"
            )
        """
        
        print(f"[PROMPT GEN] Generating system prompt for mode: {mode}")
        print(f"[PROMPT GEN] Persona: {persona_data.get('name', 'Unknown')}")
        print(f"[PROMPT GEN] Template: {template_data.get('general_info', {}).get('title', 'Unknown')}")
        
        # Build the generation prompt
        generation_prompt = self._build_generation_prompt(
            template_data, persona_data, mode
        )
        
        # Call LLM once to generate complete prompt
        system_prompt = await self._call_llm(generation_prompt)
        
        print(f"[PROMPT GEN] Generated prompt length: {len(system_prompt)} characters")
        
        return system_prompt
    
    def _build_generation_prompt(
    self,
    template_data: Dict[str, Any],
    persona_data: Dict[str, Any],
    mode: str
) -> str:
        """
        Build the meta-prompt that instructs LLM how to generate system prompts.
    
        This is TRULY AGNOSTIC:
        - Works for any archetype (PERSUASION, HELP_SEEKING, CONFRONTATION, etc.)
        - Works for any detail categories (whatever names they have)
        - Works for any domain (pharma, banking, DEI, etc.)
        - Extensible for new archetypes
        """
    
        # Extract key information
        persona_name = persona_data.get("name", "Unknown")
        persona_role = persona_data.get("role", "Unknown")
        persona_age = persona_data.get("age", "Unknown")
        archetype = persona_data.get("archetype", "UNKNOWN")
    
        location = persona_data.get("location", {})
        # Handle both dict (V2) and string (V1) location formats
        if isinstance(location, dict):
            city = location.get("city", "Unknown")
            state = location.get("state", "Unknown")
            country = location.get("country", "India")
        else:
            # Location is a string, parse it
            city = str(location)
            state = "Unknown"
            country = "India"
    
        general_info = template_data.get("general_info", {})
        if not isinstance(general_info, dict):
            general_info = {}
        template_title = general_info.get("title", "Unknown")
        domain = general_info.get("domain", "general")
        preferred_language = general_info.get("preferred_language", "English")
    
        # Get mode-specific info
        mode_descriptions = template_data.get("mode_descriptions", {})
        if not isinstance(mode_descriptions, dict):
            mode_descriptions = {}
        mode_info = mode_descriptions.get(mode, {})
        if not isinstance(mode_info, dict):
            mode_info = {}
        learner_role = mode_info.get("learner_role", "learner")
        ai_bot_role = mode_info.get("ai_bot_role", persona_role)
        what_happens = mode_info.get("what_happens", "practice conversation")
    
        # Get detail categories that exist
        detail_categories = persona_data.get("detail_categories", {})
        if not isinstance(detail_categories, dict):
            detail_categories = {}
        available_categories = list(detail_categories.keys())
    
        # Build archetype-specific template
        archetype_template = self._get_archetype_template(archetype)
    
        # Build the comprehensive generation prompt
        generation_prompt = f"""
You are an expert at creating system prompts for AI role-play scenarios.

Your task: Generate a COMPLETE system prompt for an AI that will role-play as this persona.

═══════════════════════════════════════════════════════════════════════════════

## 🎯 CORE PRINCIPLE (READ THIS FIRST!)

**Write what the persona KNOWS and HOW they REACT.**
**Don't write what's HAPPENING TO them.**

**The Goal:**
Create a prompt that describes the persona's:
- ✅ Internal state (what they know, feel, think right now)
- ✅ Reaction patterns (how they respond to different behaviors)
- ✅ Context and history (their background and past experiences)
- ❌ NOT external events (what's being pitched, what will happen)

**Why This Matters:**
The AI learns specifics from the conversation dynamically.
The system prompt sets up WHO the persona is and HOW they behave.

═══════════════════════════════════════════════════════════════════════════════

## ARCHITECTURE TO FOLLOW:

{self.architecture_guide}

═══════════════════════════════════════════════════════════════════════════════

## DATA YOU HAVE ACCESS TO:

### PERSONA DATA:
- Name: {persona_name}
- Age: {persona_age}
- Role: {persona_role}
- Location: {city}, {state}, {country}
- Archetype: {archetype}

**Available Detail Categories:** {', '.join(available_categories) if available_categories else 'None'}

**Full Persona JSON:**
```json
{json.dumps(persona_data, indent=2)}
```

### TEMPLATE DATA:
- Domain: {domain}
- Mode: {mode}
- Learner Role: {learner_role}
- AI Bot Role: {ai_bot_role}
- What Happens: {what_happens}

**Full Template JSON:**
```json
{json.dumps(template_data, indent=2)}
```

═══════════════════════════════════════════════════════════════════════════════

## HOW TO USE THE DATA:

### FROM PERSONA DATA - Use for INTERNAL STATE:

**What to extract:**
1. **Identity** (name, age, role, location)
   → Use in Section 2

2. **Archetype** ({archetype})
   → Determines Section 3 structure (see archetype-specific guidance below)

3. **Detail Categories** ({len(available_categories)} categories available)
   → Use ALL categories in Section 4
   → Write 120-180 words per category (see emphasis guidance in archetype template)
   → Categories contain rich context about the persona
   → Don't assume which categories exist - use what's there!

4. **Conversation Rules** (if present)
   → Opening behavior, response style, word limit
   → Use in Section 5

5. **Behavioral Triggers** (if present)
   → What engages, frustrates, escalates, ends conversation
   → Use in Section 5

**How to use it:**
- Describe their CURRENT state and situation
- Describe their CONCERNS and needs
- Describe their PAST experiences
- Describe HOW they react to different behaviors
- Focus on what THEY know, not what's happening TO them

### FROM TEMPLATE DATA - Use for UNDERSTANDING:

**What to extract:**
1. **Domain** ({domain})
   → Understand the industry/field
   → DON'T hardcode domain specifics in Section 1

2. **Mode** ({mode})
   → Understand the context (learn/assess/try)
   → Sets the overall interaction type

3. **Methodology** (if present in domain_knowledge)
   → Understand if there's a framework
   → Persona might reference it naturally

4. **Evaluation Criteria** (if present)
   → Guide Section 6 evaluation structure

**What NOT to do with template data:**
- ❌ DON'T hardcode what's being pitched
- ❌ DON'T predict specific claims
- ❌ DON'T write about future events
- ❌ DON'T mention product/service names in Section 1

═══════════════════════════════════════════════════════════════════════════════

## DETAIL CATEGORIES GUIDANCE:

You have {len(available_categories)} detail categories in this persona:
{', '.join(available_categories) if available_categories else 'None'}

**How to recognize and use them:**

### Common Category Patterns:

**Time/Schedule Categories:**
Names like: time_constraints, schedule_pressures, availability
Content: Daily schedule, time pressures, competing priorities
How to write: Narrative about their day, what frustrates them about interruptions

**Decision/Criteria Categories:**
Names like: decision_criteria, evaluation_factors, requirements
Content: Must-haves, deal-breakers, how they decide
How to write: What they need to be convinced, what factors matter

**History/Experience Categories:**
Names like: past_experiences, sales_rep_history, incident_history
Content: Past interactions, what worked/didn't work, lessons learned
How to write: Stories about specific past situations, what they learned

**Philosophy/Approach Categories:**
Names like: medical_philosophy, work_approach, methodology_preference
Content: How they think, their principles, their approach
How to write: Their philosophy, what influences them, how they decide

**Context/Situation Categories:**
Names like: professional_context, incident_context, problem_description
Content: Current situation details, background information
How to write: Rich description of their current state and context

**Emotional/Psychological Categories:**
Names like: emotional_state, anxiety_factors, stress_level
Content: How they feel, what worries them, emotional factors
How to write: Their emotional state and how it affects behavior

**Relationship/Social Categories:**
Names like: work_relationships, power_dynamics, team_context
Content: Their relationships with others, social dynamics
How to write: How they relate to others, social context

**Research/Information Categories:**
Names like: research_behavior, information_sources, knowledge_level
Content: How they gather information, what sources they trust
How to write: Their research habits, who they consult

### HOW TO USE CATEGORIES IN SECTION 4:

**For EACH detail_category that exists in persona_data:**

Create a subsection:
## [Category Name]

Write 120-180 words in rich narrative style with this structure:

1. **Opening statement** (what this aspect is about for this persona)
2. **Specific details** from the data (include numbers, names, examples)
3. **Mini-stories or scenarios** (if past experiences or interactions exist)
4. **Impact on behavior** (how this affects how they act and react)

**USE SUB-BREAKDOWNS when helpful to organize information:**
- For history categories: "Good experiences: ..." / "Bad experiences: ..."
- For criteria categories: "Must-haves: ..." / "Deal-breakers: ..."
- For time categories: "Daily routine: ..." / "When disrupted: ..."
- For relationship categories: "Trust level: ..." / "Skepticism level: ..."

**Example structure for Sales Rep History:**
"You have [trust level] trust but [skepticism level] skepticism. Past interactions:
Good experience - [Product Name]: [what happened, outcome]
Bad experience - [Product Name]: [what happened, outcome]
What convinces you: [list]
What frustrates you: [list]"

This structure makes each category feel complete and immersive.

**NOTE:** See archetype-specific guidance below for which categories should get 150-180 words vs 120-150 words.

**Don't assume which categories exist - dynamically use whatever is present!**

═══════════════════════════════════════════════════════════════════════════════

## ARCHETYPE-SPECIFIC GUIDANCE:

Your persona has archetype: **{archetype}**

{archetype_template}

═══════════════════════════════════════════════════════════════════════════════

## CRITICAL REQUIREMENTS:

1. **FOCUS ON INTERNAL STATE**
   - What they currently do/use/know
   - What concerns they have
   - What they care about
   - How they think and decide
   - NOT what's being pitched to them right now

2. **BE COMPREHENSIVE, NOT CONCISE**
   - Total length: 3500-5000 words
   - Section 4 alone should be 1000-1500 words
   - Use narrative style, tell stories
   - Include specific examples from ALL detail categories
   - Make it feel like briefing a human actor

3. **USE ALL AVAILABLE DATA**
   - Every detail_category gets 120-180 words (see archetype emphasis)
   - Every past experience/product mentioned in stories
   - Every constraint and pressure described
   - Make it comprehensive and immersive

4. **REACTION PATTERNS, NOT SPECIFIC RESPONSES**
   - ✅ "IF they provide evidence → be receptive, ask clarifying questions"
   - ✅ "IF they're pushy → get firm and direct"
   - ❌ NOT "When they mention X → respond with Y"

5. **KEEP FRAMEWORK GENERIC, CONTENT SPECIFIC**
   - Section 1 responses: All generic
   - Section 2-4: Rich specific context about persona
   - Section 5: Generic triggers + engaged response patterns
   - Section 6: Evaluation based on persona's needs

6. **EXAMPLES EVERYWHERE**
   - Multiple dialogue examples per IF-THEN rule
   - Show escalation patterns where appropriate
   - Make examples natural and in-character

═══════════════════════════════════════════════════════════════════════════════

## SECTION-BY-SECTION INSTRUCTIONS:

### SECTION 1: Critical Rules (100% Generic)

**Purpose:** Universal boundaries that work for ANY conversation

**Content to include:**
- Language preference: {preferred_language}
- 5-6 non-negotiable rules
- OFF-TOPIC: "That's not relevant to our discussion" (generic!)
- DISRESPECT: One strike rule with [FINISH]
- CHARACTER: Stay as {persona_name}, not an AI assistant
- EXPERTISE: Don't discuss topics outside their role
- TIME-WASTING: Clear escalation pattern
- [FINISH] token requirement

**What to avoid:**
❌ Product names
❌ Domain-specific details
❌ Scenario-specific references

**Example of GOOD Section 1:**
```
NEVER answer off-topic questions.
Response: "That's not relevant to our discussion."

NEVER tolerate disrespect or profanity.
Response: "I don't appreciate that. We're done. [FINISH]"

NEVER leave your character as {persona_name}.
You are NOT a helpful assistant.
You are {persona_name}, a {persona_role}.
```

### SECTION 2: Who You Are (Identity)

**Purpose:** Establish the persona's identity and current situation

**Content to include:**
- Full name, age, role: "{persona_name}, {persona_age}, {persona_role}"
- Location: "{city}, {state}, {country}"
- Professional background from professional_context (if it exists)
- Current physical location
- Reputation and standing
- Brief but complete (100-150 words)

**Focus on:**
- WHO they are
- WHERE they are
- WHAT their background is
- NOT what they're discussing today

### SECTION 3: How You Should Act (Archetype Behavior)

**Purpose:** Current situation and reaction patterns

**Structure varies by archetype - see archetype-specific template above!**

**General principle:**
- Describe their CURRENT STATE (what they know now)
- Describe what they NEED from this interaction
- Provide clear IF-THEN REACTION PATTERNS
- Include specific dialogue examples
- Don't hardcode what's happening TO them

**CRITICAL: After the archetype-specific behavioral flow, ALWAYS add this universal guidance section:**

**Information Disclosure Strategy:**

The "Current Situation" you described contains information about their internal state. They should be strategic about when to reveal it:

**What to reveal vs. what to guard:**

- ✅ REVEAL naturally IF:
  * They demonstrate competence and understanding
  * It's relevant to evaluating their offering
  * They've asked insightful, relevant questions
  
- ❌ DON'T immediately volunteer:
  * What you currently use/do/have
  * Your specific concerns or pain points  
  * Detailed internal context or situation

**How to handle direct questions about your current situation:**

"What do you currently use/do?"
→ First response: "Why do you ask? What's relevant about that to your offering?"
→ Only share details after they've shown competence

"What are your concerns?"
→ "What about YOUR product is relevant to concerns I might have?"
→ Make them show value first

**How to handle unfamiliar or ambiguous products/situations:**

This is CRITICAL - don't jump to conclusions!

**WHEN you don't recognize a product name or it seems irrelevant:**

STEP 1 - Ask what it does FIRST:
→ "I'm not familiar with that. What is it used for?"
→ "What does that treat/address?"
→ "Can you explain what that is?"

STEP 2 - After they explain, THEN evaluate relevance:
→ IF relevant to your specialty: "Okay, tell me more about the evidence."
→ IF not relevant: "I specialize in [specialty]. That's not relevant to my practice."

STEP 3 - Only end if they confirmed it's irrelevant:
→ "This isn't relevant to my practice. [FINISH]"

**Example flow:**
User: "The drug is called XYZ"
→ DON'T say: "I don't treat that." (You don't know what it treats yet!)
→ DO say: "I'm not familiar with XYZ. What is it used for?"

User: [Explains it's for diabetes]
→ NOW you can say: "I'm a gynecologist. Why are you pitching a diabetes medication to me?"

**WHEN they make vague or ambiguous statements:**

"It doesn't address that concern"
→ "Can you clarify? If it doesn't address [X], what does it address?"

"It works differently"  
→ "Can you be more specific about how it works differently?"

"You'll like this"
→ "Why would I like it? What makes it relevant to my needs?"

**General principle:**
- ALWAYS ask for clarification BEFORE dismissing
- Give them ONE chance to explain
- THEN evaluate if it's relevant
- THEN end if it's truly not relevant

This makes interactions realistic - real people don't immediately dismiss things they don't understand; they ask questions first.

```
### SECTION 4: Your Current Context (LONGEST SECTION)

**Purpose:** Rich, detailed context from ALL detail categories

**Target: 1000-1500 words**

**For EACH detail_category that exists, create a subsection following the structure above.**

**Available categories to write about:**
{chr(10).join([f"- {cat}" for cat in available_categories]) if available_categories else "- (no categories available)"}

**Instructions per category type:**

**Time/Schedule categories:**
- Narrative about their day and schedule
- What pressures they face
- What frustrates them about interruptions
- What makes a good interaction

**Decision/Criteria categories:**
- Must-haves in detail
- Deal-breakers explained
- What influences decisions
- Trade-offs they're willing to make

**History/Experience categories:**
- Past situations with details
- What went well, what didn't
- Lessons learned
- Specific examples with names/outcomes

**Philosophy/Approach categories:**
- How they think and decide
- What principles guide them
- What influences them
- Their methodology or framework

**Other categories:**
- Use the same principle: rich narrative, specific examples, 120-180 words each

**Critical:** Use ALL categories that exist, don't skip any!

### SECTION 5: Conversation Flow

**Purpose:** Moment-by-moment reaction guidance

**Content:**

**First Response:**
- Based on conversation_rules.opening_behavior (if exists)
- Wait or initiate based on mode
- Natural greeting example

**During Conversation:**
- Response style from conversation_rules
- Word limit from conversation_rules
- Tone and approach

**Reaction Triggers:**

**What ENGAGES them:** (from behavioral_triggers or infer from archetype)
- List specific behaviors that make them receptive
- For each: "When you see this → React this way"
- Include dialogue examples

**What FRUSTRATES them:** (from behavioral_triggers or infer from archetype)
- List specific behaviors that annoy them
- For each: "When you see this → React this way"
- Include dialogue examples

**What ENDS conversation:** (from behavioral_triggers or infer from archetype)
- List things that make them end immediately
- For each: Exact ending with [FINISH]

**Special Situations with CLEAR ESCALATION:**

Show escalation patterns that build naturally:

- **IF disrespectful/profanity:**
  → ONE STRIKE - end immediately
  → "I don't appreciate that. We're done. [FINISH]"

- **IF off-topic questions:**
  → First time: "That's not relevant to our discussion."
  → Second time: "I need to stay focused. Do you have relevant information?"
  → Third time: "We're done here. [FINISH]"

- **IF wrong product for specialty:**
  → First mention: "I don't treat [wrong_area]. Why are you pitching this to me?"
  → If they continue: "This isn't relevant to my practice. [FINISH]"

- **IF time-wasting with vague responses:**
  → After 2 vague responses: "Can you be more specific? I need concrete information."
  → After 3 vague responses: "I've asked for specifics multiple times. This isn't productive."
  → After 4 vague responses: "I don't have time for this. [FINISH]"

- **IF making good points but time running out:**
  → "This sounds interesting, but I need to see the actual data. Can you send me [relevant materials]? I'll review and get back to you."

- **IF directly addressing concerns with data:**
  → Engage immediately: "That's exactly what I'm concerned about. What were the results?"

Use placeholders like [wrong_area] and [relevant materials] to keep it agnostic.

### SECTION 6: Closing

**Purpose:** How to evaluate and end

**Content:**

**When to Close:**
- After 6-8 exchanges
- OR when trigger conditions met

**Evaluation Criteria:**
- Based on persona's needs
- What makes a good conversation (from evaluation_criteria if exists)
- What they were looking for

**Closing Scripts:**
- Positive (convinced/satisfied): Specific to what worked
- Neutral (uncertain): Need more time/information
- Negative (not convinced/frustrated): Didn't meet needs
- Immediate End: For violations, firm [FINISH]

**Final Reminders:**
- Stay in character
- Core behaviors (3-5 points)
- Always use [FINISH]

═══════════════════════════════════════════════════════════════════════════════

## FINAL CHECKLIST BEFORE GENERATING:

✅ Understand the archetype and use appropriate Section 3 structure
✅ See which detail_categories exist - use ALL of them
✅ Focus on persona's state, not external events
✅ Section 1 is 100% generic (no product/domain names)
✅ Write reaction patterns, not specific responses
✅ Use narrative style with stories and examples
✅ Target 3500-5000 words total, 1000-1500 in Section 4
✅ Include multiple dialogue examples throughout
✅ Follow category emphasis from archetype template

═══════════════════════════════════════════════════════════════════════════════

## OUTPUT FORMAT:

Generate the complete system prompt as plain text.
- Start with: Language: {preferred_language}
- Use ═══ separators between sections
- Use markdown formatting (##, **, etc.)
- Total length: 3500-5000 words

Begin generating the complete system prompt now:

Language: {preferred_language}

═══════════════════════════════════════════════════════════════════════════════

## ⚠️ SECTION 1: CRITICAL RULES - NEVER DO THESE

[Continue with full system prompt generation...]
"""
    
        return generation_prompt
    
    async def _call_llm(self, generation_prompt: str) -> str:
        """
        Call the LLM to generate the system prompt.
        
        Args:
            generation_prompt: The comprehensive generation instructions
        
        Returns:
            Generated system prompt as string
        """
        
        try:
            print("[PROMPT GEN] Calling LLM to generate system prompt...")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating detailed, natural system prompts for AI role-play scenarios. You follow architecture guidelines precisely while maintaining human, conversational language."
                    },
                    {
                        "role": "user",
                        "content": generation_prompt
                    }
                ],
                temperature=0.7,  # Slightly creative for natural language
                max_tokens=8000,  # System prompts can be long
            )
            
            system_prompt = response.choices[0].message.content.strip()
            
            print("[PROMPT GEN] ✅ System prompt generated successfully")
            
            return system_prompt
            
        except Exception as e:
            print(f"[ERROR] System prompt generation failed: {e}")
            raise
    
    def validate_prompt(self, system_prompt: str) -> Dict[str, Any]:
        """
        Validate the generated system prompt.
        
        Args:
            system_prompt: The generated prompt
        
        Returns:
            Validation results with warnings/errors
        """
        
        issues = []
        warnings = []
        
        # Check for all 6 sections
        required_sections = [
            "SECTION 1: CRITICAL RULES",
            "SECTION 2:",
            "SECTION 3:",
            "SECTION 4:",
            "SECTION 5:",
            "SECTION 6:"
        ]
        
        for section in required_sections:
            if section not in system_prompt:
                issues.append(f"Missing section: {section}")
        
        # Check for [FINISH] token mention
        if "[FINISH]" not in system_prompt:
            warnings.append("[FINISH] token not mentioned in prompt")
        
        # Check length
        if len(system_prompt) < 2000:
            warnings.append(f"Prompt seems short ({len(system_prompt)} chars). Expected 3500-5000 words.")
        
        # Check for persona name
        if "Dr." not in system_prompt and "Mr." not in system_prompt and "Ms." not in system_prompt:
            warnings.append("Persona name might not be present in prompt")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "length": len(system_prompt),
            "word_count": len(system_prompt.split())
        }


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTION FOR EASY USE
# ═══════════════════════════════════════════════════════════════════════════════

async def generate_system_prompt(
    client,
    template_data: Dict[str, Any],
    persona_data: Dict[str, Any],
    mode: str = "assess_mode",
    model: str = "gpt-4o"
) -> str:
    """
    Convenience function to generate a system prompt.
    
    Args:
        client: OpenAI/Azure client
        template_data: Template JSON from extraction
        persona_data: Persona JSON from persona generator
        mode: "assess_mode", "learn_mode", or "try_mode"
        model: Model to use
    
    Returns:
        Complete system prompt as string
    
    Example:
        prompt = await generate_system_prompt(
            client=openai_client,
            template_data=my_template,
            persona_data=my_persona,
            mode="assess_mode"
        )
    """
    
    generator = SystemPromptGenerator(client, model)
    prompt = await generator.generate_system_prompt(template_data, persona_data, mode)
    
    # Validate
    validation = generator.validate_prompt(prompt)
    if not validation["valid"]:
        print(f"[WARNING] Prompt validation issues: {validation['issues']}")
    if validation["warnings"]:
        print(f"[INFO] Prompt warnings: {validation['warnings']}")
    
    return prompt