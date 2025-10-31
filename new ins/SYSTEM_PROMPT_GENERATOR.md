# System Prompt Generator - Single-Pass Implementation

## 🎯 Overview

This function takes template_data and persona_data JSONs and generates a complete system prompt using your 6-section architecture.

**Single-pass approach:** One LLM call generates all 6 sections naturally.

---

## 📋 Complete Implementation

### File to Create: `core/system_prompt_generator.py`

```python
"""
System Prompt Generator
Generates complete system prompts from template and persona data using LLM.
"""

import json
from typing import Dict, Any, Optional
from models.persona_models import PersonaInstance


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
        self.architecture_guide = self._load_architecture_guide()
    
    def _load_architecture_guide(self) -> str:
        """
        Load the 6-section architecture guide.
        
        PASTE YOUR ARCHITECTURE TEXT HERE (the one you shared with the 6 sections).
        This becomes the "instruction manual" for the LLM.
        """
        
        return """
{PASTE_YOUR_6_SECTION_ARCHITECTURE_HERE}

The architecture should include:
- Section 1: Critical Rules
- Section 2: Who You Are (Identity)
- Section 3: How You Should Act (Archetype Behavior)
- Section 4: Your Current Context (Detail Categories)
- Section 5: Conversation Flow
- Section 6: Closing & Reminders

Example structure from your document:
┌──────────────────────────────────────────────────────┐
│ SECTION 1: CRITICAL RULES (Universal - Top Priority)│
├──────────────────────────────────────────────────────┤
│ SECTION 2: CHARACTER IDENTITY (Persona-Specific)    │
└──────────────────────────────────────────────────────┘
... etc
"""
    
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
        Build the comprehensive prompt that instructs the LLM how to generate
        the system prompt following the 6-section architecture.
        
        This is the KEY method - creates the meta-prompt.
        """
        
        # Extract key information
        persona_name = persona_data.get("name", "Unknown")
        persona_role = persona_data.get("role", "Unknown")
        archetype = persona_data.get("archetype", "UNKNOWN")
        
        template_title = template_data.get("general_info", {}).get("title", "Unknown")
        domain = template_data.get("general_info", {}).get("domain", "general")
        
        # Get mode-specific info
        mode_info = template_data.get("mode_descriptions", {}).get(mode, {})
        learner_role = mode_info.get("learner_role", "learner")
        ai_bot_role = mode_info.get("ai_bot_role", persona_role)
        what_happens = mode_info.get("what_happens", "practice conversation")
        
        # Build the comprehensive generation prompt
        generation_prompt = f"""
You are an expert at creating system prompts for AI role-play scenarios.

Your task: Generate a COMPLETE, NATURAL, DETAILED system prompt for an AI that will role-play as this persona.

═══════════════════════════════════════════════════════════════════════════════

## ARCHITECTURE TO FOLLOW:

{self.architecture_guide}

═══════════════════════════════════════════════════════════════════════════════

## SCENARIO INFORMATION:

**Template Title:** {template_title}
**Domain:** {domain}
**Mode:** {mode}

**What's Happening:**
{what_happens}

**AI Bot Role:** {ai_bot_role}
**Learner Role:** {learner_role}

**Full Template Data:**
```json
{json.dumps(template_data, indent=2)}
```

═══════════════════════════════════════════════════════════════════════════════

## PERSONA INFORMATION:

**Name:** {persona_name}
**Role:** {persona_role}
**Archetype:** {archetype}

**Full Persona Data:**
```json
{json.dumps(persona_data, indent=2)}
```

═══════════════════════════════════════════════════════════════════════════════

## YOUR TASK:

Generate a COMPLETE system prompt following the 6-section architecture provided above.

**Critical Requirements:**

1. **Follow the Architecture Exactly**
   - Use all 6 sections in order
   - Use visual separators (═══) between sections
   - Match the tone and style of the architecture guide

2. **Use ALL Available Data**
   - Weave in persona details naturally throughout
   - Use all detail_categories that exist (time_constraints, decision_criteria, etc.)
   - Reference template data where relevant (methodology, domain knowledge, etc.)
   - Don't leave out details - be comprehensive!

3. **Archetype-Specific Behavior**
   - This persona is a {archetype} archetype
   - Section 3 must implement {archetype}-appropriate behavior patterns
   - Include clear IF-THEN rules for how to react
   - Give specific dialogue examples

4. **Natural, Human Language**
   - Write like you're briefing a human actor, not filling a template
   - Use conversational, clear language
   - Include specific examples and scenarios
   - Make it feel real and authentic

5. **Complete and Actionable**
   - Every section should be detailed and specific
   - Include exact phrases the AI should say
   - Cover edge cases and special situations
   - Make ending conditions crystal clear ([FINISH] token)

6. **Context Integration**
   - Section 2: Use professional_context and location details
   - Section 3: Use decision_criteria, current situation, pain points
   - Section 4: Use ALL detail_categories that exist in persona
   - Section 5: Use conversation_rules and behavioral_triggers
   - Section 6: Use evaluation_criteria from template if present

═══════════════════════════════════════════════════════════════════════════════

## SECTION-BY-SECTION GUIDANCE:

### Section 1: Critical Rules
- Start with language preference
- List 5-6 non-negotiable rules
- Make them specific to this scenario (use persona name, role, domain)
- Include ONE STRIKE rules for disrespect
- Mention off-topic handling
- Mention [FINISH] token requirement

### Section 2: Who You Are
- Full name, age, role, location
- Professional background (from professional_context)
- Current location and situation
- Reputation/standing
- Keep it concise but complete (50-100 words)

### Section 3: How You Should Act (Archetype)
- Current situation relevant to the scenario
- What you need to be convinced (for PERSUASION) or what problem you have (for HELP_SEEKING)
- Clear behavioral flow with IF-THEN rules
- Specific dialogue examples
- Decision-making timeline (when to close conversation)
- This should be the LONGEST section (150-200 words)

### Section 4: Your Current Context
- Sub-section for EACH detail_category that exists in persona data
- Time constraints (if exists)
- Decision criteria (if exists)
- Sales rep history (if exists)
- Medical/professional philosophy (if exists)
- Research behavior (if exists)
- Past experiences (if exists)
- Make each sub-section rich with specifics (50-100 words each)

### Section 5: Conversation Flow
- First response behavior (wait or initiate?)
- Response style and word limit
- Reaction triggers (what engages, frustrates, ends conversation)
- Special situations (off-topic, disrespect, wrong product, time wasting)
- Include specific dialogue examples for each trigger

### Section 6: Closing
- When to close (after how many exchanges)
- Evaluation criteria (what to assess)
- 3-4 closing scripts (positive, neutral, negative, immediate end)
- Each with exact dialogue and [FINISH] token
- Final reminders (3-5 bullet points)

═══════════════════════════════════════════════════════════════════════════════

## OUTPUT FORMAT:

Generate the complete system prompt as plain text.
- Use the exact section headers from the architecture
- Use ═══ separators between sections
- Use markdown formatting (##, **, -, etc.)
- Include all details from persona and template data
- Make it natural and human-readable
- Total length should be 3500-5000 words

Begin generating the system prompt now. Start with:

Language: [preferred_language]

═══════════════════════════════════════════════════════════════════════════════

## ⚠️ SECTION 1: CRITICAL RULES - NEVER DO THESE

[Continue from here...]
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
                max_tokens=6000,  # System prompts can be long
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
```

---

## 📋 Usage Examples

### Example 1: Basic Usage

```python
from core.system_prompt_generator import generate_system_prompt

# Assume you have these from extraction + persona generation
template_data = {...}  # Your EO-Dine template
persona_data = {...}   # Your Dr. Priya persona

# Generate the prompt
system_prompt = await generate_system_prompt(
    client=openai_client,
    template_data=template_data,
    persona_data=persona_data,
    mode="assess_mode"
)

# Use it
print(system_prompt)
# Save it
with open("generated_prompt.txt", "w") as f:
    f.write(system_prompt)
```

### Example 2: Using the Class

```python
from core.system_prompt_generator import SystemPromptGenerator

generator = SystemPromptGenerator(client=openai_client, model="gpt-4o")

# Generate for assess mode
assess_prompt = await generator.generate_system_prompt(
    template_data=template_data,
    persona_data=persona_data,
    mode="assess_mode"
)

# Generate for try mode (same persona, different mode)
try_prompt = await generator.generate_system_prompt(
    template_data=template_data,
    persona_data=persona_data,
    mode="try_mode"
)

# Validate
validation = generator.validate_prompt(assess_prompt)
print(f"Valid: {validation['valid']}")
print(f"Length: {validation['length']} chars")
print(f"Issues: {validation['issues']}")
```

### Example 3: End-to-End Pipeline

```python
# Full pipeline: Extraction → Persona → Prompt
from core.scenario_extractor_v2 import ScenarioExtractorV2
from core.persona_generator_v2 import PersonaGenerator
from core.system_prompt_generator import SystemPromptGenerator

# Step 1: Extract scenario
extractor = ScenarioExtractorV2(client)
template_data = await extractor.extract_scenario_info(document_text)

# Step 2: Generate persona
persona_gen = PersonaGenerator(client)
persona_data = await persona_gen.generate_persona(
    template_data=template_data,
    mode="assess_mode",
    gender="Female"
)

# Step 3: Generate system prompt
prompt_gen = SystemPromptGenerator(client)
system_prompt = await prompt_gen.generate_system_prompt(
    template_data=template_data,
    persona_data=persona_data.dict(),  # Convert to dict if it's a Pydantic model
    mode="assess_mode"
)

print("✅ Complete system prompt generated!")
print(f"Length: {len(system_prompt)} characters")
```

---

## 🧪 Testing

### Test File: `tests/test_system_prompt_generator.py`

```python
import pytest
import asyncio
from core.system_prompt_generator import SystemPromptGenerator

@pytest.mark.asyncio
async def test_prompt_generation_basic():
    """Test basic prompt generation"""
    
    # Mock data
    template_data = {
        "general_info": {"title": "Test Scenario", "domain": "test"},
        "mode_descriptions": {
            "assess_mode": {
                "what_happens": "Testing",
                "learner_role": "Tester",
                "ai_bot_role": "Test Subject"
            }
        }
    }
    
    persona_data = {
        "name": "Test Person",
        "role": "Test Role",
        "archetype": "PERSUASION",
        "age": 30,
        "location": {"city": "Test City"},
        "detail_categories": {}
    }
    
    generator = SystemPromptGenerator(client)
    prompt = await generator.generate_system_prompt(
        template_data, persona_data, "assess_mode"
    )
    
    assert len(prompt) > 1000
    assert "SECTION 1" in prompt
    assert "Test Person" in prompt
    assert "[FINISH]" in prompt


@pytest.mark.asyncio
async def test_prompt_validation():
    """Test prompt validation"""
    
    generator = SystemPromptGenerator(client)
    
    # Good prompt
    good_prompt = """
    SECTION 1: CRITICAL RULES
    SECTION 2: WHO YOU ARE
    SECTION 3: BEHAVIOR
    SECTION 4: CONTEXT
    SECTION 5: FLOW
    SECTION 6: CLOSING
    [FINISH]
    """ * 100  # Make it long enough
    
    validation = generator.validate_prompt(good_prompt)
    assert validation["valid"] == True
    
    # Bad prompt (missing sections)
    bad_prompt = "SECTION 1: CRITICAL RULES"
    
    validation = generator.validate_prompt(bad_prompt)
    assert validation["valid"] == False
    assert len(validation["issues"]) > 0
```

---

## 📝 Integration Steps for Amazon Q

### Step 1: Create the File
```
Create core/system_prompt_generator.py with the code above
```

### Step 2: Paste Your Architecture
```
In _load_architecture_guide() method, replace {PASTE_YOUR_6_SECTION_ARCHITECTURE_HERE}
with your actual 6-section architecture description.
```

### Step 3: Test It
```python
# Quick test
template = {...}  # Your template
persona = {...}   # Your persona

prompt = await generate_system_prompt(client, template, persona, "assess_mode")
print(prompt[:500])  # Print first 500 chars
```

### Step 4: Integrate Into Service
```python
# In your main service file
from core.system_prompt_generator import generate_system_prompt

class ScenarioService:
    async def create_conversation_session(self, template_id, persona_id):
        # Get template and persona
        template = await self.get_template(template_id)
        persona = await self.get_persona(persona_id)
        
        # Generate system prompt
        system_prompt = await generate_system_prompt(
            self.client,
            template,
            persona,
            mode="assess_mode"
        )
        
        # Use in conversation
        return {"system_prompt": system_prompt}
```

---

## ⚡ Performance Notes

- **Single LLM call:** ~10-30 seconds depending on model
- **Token usage:** ~5000 input + ~4000 output = ~9000 tokens total
- **Cost:** ~$0.05 per prompt with GPT-4o
- **Cache:** Can cache prompts for same template+persona combination

---

## 🎯 Expected Output Quality

The generated prompt will be:
- ✅ 3500-5000 words (comprehensive)
- ✅ Natural, human-readable language
- ✅ All 6 sections present and detailed
- ✅ Persona details woven throughout
- ✅ Archetype-appropriate behavior
- ✅ Clear IF-THEN rules
- ✅ Specific dialogue examples
- ✅ Ready to use immediately

---

## 🔧 Troubleshooting

### Issue: Prompt too short
**Solution:** Increase temperature or adjust generation prompt emphasis on "comprehensive" and "detailed"

### Issue: Missing details from persona
**Solution:** Check that persona_data has all detail_categories populated

### Issue: Wrong archetype behavior
**Solution:** Verify archetype is correctly set in persona_data

### Issue: Sections not following architecture
**Solution:** Make sure architecture guide in _load_architecture_guide() is complete

---

## ✅ Done!

You now have:
- ✅ Complete SystemPromptGenerator class
- ✅ Single-pass generation implementation
- ✅ Validation logic
- ✅ Usage examples
- ✅ Testing strategy

**Give this to Amazon Q to integrate!**
