"""
Learn Mode Prompt Generator
Generates trainer prompts for teaching scenarios (learn mode).
Uses template_data only - no persona needed.
"""

import json
from typing import Dict, Any, Optional
from core.learn_mode_prompt_templates import LEARN_MODE_ARCHITECTURE


class LearnModePromptGenerator:
    """
    Generates trainer prompts for learn mode.
    
    Learn mode = AI is a TRAINER teaching methodology/skills.
    Different from assess mode where AI is a PERSONA being evaluated.
    
    Uses:
    - mode_descriptions.learn_mode
    - methodology_steps
    - key_facts, dos, donts
    - coaching_rules (for teaching style)
    """
    
    def __init__(self, client, model="gpt-4o"):
        """
        Initialize the learn mode generator.
        
        Args:
            client: OpenAI/Azure client
            model: Model to use for generation
        """
        self.client = client
        self.model = model
        self.learn_mode_architecture = LEARN_MODE_ARCHITECTURE
    
    async def generate_trainer_prompt(
        self,
        template_data: Dict[str, Any]
    ) -> str:
        """
        Main entry point: Generate complete trainer prompt for learn mode.
        
        Args:
            template_data: Extracted scenario template (contains methodology, facts, etc.)
        
        Returns:
            Complete trainer prompt as string (ready to use)
        
        Example:
            generator = LearnModePromptGenerator(client)
            prompt = await generator.generate_trainer_prompt(
                template_data=eo_dine_template
            )
        """
        
        print("[LEARN GEN] Generating trainer prompt for learn mode")
        
        # Extract key info
        general_info = template_data.get("general_info", {})
        title = general_info.get("title", "Unknown")
        domain = general_info.get("domain", "general")
        
        learn_info = template_data.get("mode_descriptions", {}).get("learn_mode", {})
        bot_role = learn_info.get("ai_bot_role", "expert trainer")
        
        print(f"[LEARN GEN] Title: {title}")
        print(f"[LEARN GEN] Domain: {domain}")
        print(f"[LEARN GEN] Trainer Role: {bot_role}")
        
        # Build the generation prompt
        generation_prompt = self._build_learn_generation_prompt(template_data)
        
        # Call LLM once to generate complete prompt
        trainer_prompt = await self._call_llm(generation_prompt)
        
        print(f"[LEARN GEN] Generated trainer prompt length: {len(trainer_prompt)} characters")
        
        return trainer_prompt
    
    def _build_learn_generation_prompt(
        self,
        template_data: Dict[str, Any]
    ) -> str:
        """
        Build the comprehensive meta-prompt that instructs the LLM how to generate
        the trainer prompt following the 8-section architecture.
        
        This is the KEY method - creates the meta-prompt for learn mode.
        """
        
        # Extract general info
        general_info = template_data.get("general_info", {})
        if not isinstance(general_info, dict):
            general_info = {}
        title = general_info.get("title", "Unknown")
        domain = general_info.get("domain", "general")
        preferred_language = general_info.get("preferred_language", "English")
        
        # Extract learn mode info
        mode_descriptions = template_data.get("mode_descriptions", {})
        if not isinstance(mode_descriptions, dict):
            mode_descriptions = {}
        learn_info = mode_descriptions.get("learn_mode", {})
        if not isinstance(learn_info, dict):
            learn_info = {}
        bot_role = learn_info.get("ai_bot_role", "expert trainer")
        learner_role = learn_info.get("learner_role", "learner")
        what_happens = learn_info.get("what_happens", "training session")
        teaching_focus = learn_info.get("teaching_focus", "skills and knowledge")
        
        # Extract domain knowledge
        domain_knowledge = template_data.get("domain_knowledge", {})
        if not isinstance(domain_knowledge, dict):
            domain_knowledge = {}
        methodology = domain_knowledge.get("methodology", "")
        methodology_steps = domain_knowledge.get("methodology_steps", [])
        key_facts = domain_knowledge.get("key_facts", [])
        dos = domain_knowledge.get("dos", [])
        donts = domain_knowledge.get("donts", [])
        subject_matter = domain_knowledge.get("subject_matter", {})
        
        # Extract coaching style
        coaching_rules = template_data.get("coaching_rules", {})
        if not isinstance(coaching_rules, dict):
            coaching_rules = {}
        coaching_style = coaching_rules.get("coaching_style", "supportive and encouraging")
        
        # Build the comprehensive generation prompt
        generation_prompt = f"""
You are creating comprehensive training documentation for an educational scenario.

Task: Write detailed trainer guidelines following the 8-section structure provided.

═══════════════════════════════════════════════════════════════════════════════

## DOCUMENTATION STRUCTURE:

{self.learn_mode_architecture}

═══════════════════════════════════════════════════════════════════════════════

## SCENARIO INFORMATION:

**Training Subject:** {title}
**Domain:** {domain}
**Language:** {preferred_language}
**Trainer Role:** {bot_role}
**Learner Role:** {learner_role}
**Teaching Focus:** {teaching_focus}
**Teaching Style:** {coaching_style}

**Methodology to Teach:** {methodology}
**Methodology Steps:**
{chr(10).join([f"  {i+1}. {step}" for i, step in enumerate(methodology_steps)]) if methodology_steps else "  (No steps provided)"}

**Key Facts to Cover:**
{chr(10).join([f"- {fact}" for fact in key_facts]) if key_facts else "- (No facts provided)"}

**Best Practices (Do's):**
{chr(10).join([f"- {do}" for do in dos]) if dos else "- (No dos provided)"}

**Common Mistakes (Don'ts):**
{chr(10).join([f"- {dont}" for dont in donts]) if donts else "- (No donts provided)"}

Full scenario details:
```json
{json.dumps(template_data, indent=2)}
```

═══════════════════════════════════════════════════════════════════════════════

## WRITING GUIDELINES:

**Approach:**
- Create educational trainer documentation
- Focus: Teaching {methodology if methodology else teaching_focus}
- Tone: {coaching_style}, patient, helpful
- Style: Clear explanations with concrete examples

**Content Requirements:**
1. Cover all {len(methodology_steps)} methodology steps in detail
2. Include all {len(key_facts)} key facts with explanations
3. Address all {len(dos)} do's and {len(donts)} don'ts
4. Provide specific dialogue examples throughout
5. Keep individual responses concise (30-50 words)

**Structure:**
- Follow 8-section format exactly
- Length: 2000-3000 words total
- Section 4 (Methodology) should be longest (400-600 words)
- Use markdown formatting
- Include ═══ separators between sections

═══════════════════════════════════════════════════════════════════════════════

## SECTION INSTRUCTIONS:

### Section 1: Trainer Role Definition (200-300 words)

Define the trainer's identity:
- Role: {bot_role} teaching {teaching_focus}
- Audience: {learner_role}
- Style: {coaching_style}
- Response guidelines: 30-50 words, clear language
- Core principles:
  * Focus on explaining concepts
  * Provide demonstrations and examples
  * Guide learners through practice
  * Offer constructive feedback
  * Use encouraging language
  * End sessions with [FINISH] token

Include language preference: {preferred_language}

### Section 2: Subject Overview (200-300 words)

Describe what's being taught:
- Subject: {title} in {domain} domain
- Overview of {methodology if methodology else teaching_focus}
- Why this matters for {learner_role}
- Learning objectives
- Application context

### Section 3: Teaching Methodology (250-350 words)

Explain the teaching approach:
- Process: Explain → Demonstrate → Practice → Feedback
- Feedback style: {coaching_style}
- Question handling approach
- Mistake correction approach (gentle, constructive)
- Example feedback phrases

### Section 4: Core Content (400-600 words)

**Most important section!**

For each of the {len(methodology_steps)} steps in {methodology}:
- Step name and purpose
- Why this step matters
- How to execute this step (specific actions)
- Concrete example showing the step
- Common mistakes for this step
- Correct alternatives

If methodology_steps is empty, break down {teaching_focus} into teachable components.

### Section 5: Knowledge Reference (300-400 words)

Present all {len(key_facts)} key facts:
- Each fact with explanation
- Why the fact is important
- Example of applying the fact
- Supporting terminology
- Background context

### Section 6: Best Practices Guide (300-400 words)

**Do's ({len(dos)} items):**
- Each do with: importance, how-to, example

**Don'ts ({len(donts)} items):**
- Each don't with: why avoid, alternative approach, comparison

### Section 7: Conversation Guidelines (300-400 words)

Session flow:
- Starting the session
- Teaching each topic (explain → demonstrate → practice → feedback)
- Handling situations:
  * Questions: Answer + example
  * Mistakes: Gentle correction + guidance
  * Success: Praise + reinforcement
  * Confusion: Simplify + more examples
  * Off-topic: Acknowledge + redirect
- Feedback format: [Positive] + [Improvement] + [Encouragement]

### Section 8: Session Conclusion (200-300 words)

Closing approaches:
- When: After covering material (8-12 exchanges)
- How: Summarize + praise + encourage
- Types:
  * Full understanding: Positive encouragement
  * Questions remain: Offer clarification
  * Partial progress: Acknowledge + next steps
  * Resource request: Provide guidance
- Always include [FINISH] token

Provide specific closing dialogue for each type.

═══════════════════════════════════════════════════════════════════════════════

## QUALITY CHECKLIST:

- [ ] All 8 sections present
- [ ] Total 2000-3000 words
- [ ] Each methodology step detailed
- [ ] All key facts included
- [ ] All do's and don'ts covered
- [ ] Multiple dialogue examples
- [ ] {coaching_style} tone throughout
- [ ] Concrete, specific examples
- [ ] [FINISH] token mentioned
- [ ] Clear, practical guidance

═══════════════════════════════════════════════════════════════════════════════

Begin creating the training documentation:

Language: {preferred_language}

═══════════════════════════════════════════════════════════════════════════════

## SECTION 1: TRAINER ROLE DEFINITION

[Continue with complete documentation...]
"""
        print(generation_prompt,"//////////////////////////////////check/////")
        with open("issue.txt", "w", encoding="utf-8") as f:
            f.write(generation_prompt)
        return generation_prompt
    
    async def _call_llm(self, generation_prompt: str) -> str:
        """
        Call the LLM to generate the trainer prompt.
        
        Args:
            generation_prompt: The comprehensive generation instructions
        
        Returns:
            Generated trainer prompt as string
        """
        
        try:
            print("[LEARN GEN] Calling LLM to generate trainer prompt...")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating detailed, natural trainer prompts for educational AI scenarios. You create clear, comprehensive teaching prompts that are encouraging and educational."
                    },
                    {
                        "role": "user",
                        "content": generation_prompt
                    }
                ],
                temperature=0.7,
                max_tokens=8000,
            )
            
            trainer_prompt = response.choices[0].message.content.strip()
            
            print("[LEARN GEN] ✅ Trainer prompt generated successfully")
            
            return trainer_prompt
            
        except Exception as e:
            print(f"[ERROR] Trainer prompt generation failed: {e}")
            raise
    
    def validate_prompt(self, trainer_prompt: str) -> Dict[str, Any]:
        """
        Validate the generated trainer prompt.
        
        Args:
            trainer_prompt: The generated prompt
        
        Returns:
            Validation results with warnings/errors
        """
        
        issues = []
        warnings = []
        
        # Check for all 8 sections
        required_sections = [
            "SECTION 1: YOUR ROLE AS TRAINER",
            "SECTION 2:",
            "SECTION 3:",
            "SECTION 4:",
            "SECTION 5:",
            "SECTION 6:",
            "SECTION 7:",
            "SECTION 8:"
        ]
        
        for section in required_sections:
            if section not in trainer_prompt:
                issues.append(f"Missing section: {section}")
        
        # Check for [FINISH] token mention
        if "[FINISH]" not in trainer_prompt:
            warnings.append("[FINISH] token not mentioned in prompt")
        
        # Check length
        word_count = len(trainer_prompt.split())
        if word_count < 1500:
            warnings.append(f"Prompt seems short ({word_count} words). Expected 2000-3000 words.")
        elif word_count > 3500:
            warnings.append(f"Prompt seems long ({word_count} words). Expected 2000-3000 words.")
        
        # Check for teaching language
        teaching_keywords = ["teach", "explain", "demonstrate", "practice", "feedback", "learn"]
        found_keywords = [kw for kw in teaching_keywords if kw in trainer_prompt.lower()]
        if len(found_keywords) < 4:
            warnings.append("Prompt may not have enough teaching-focused language")
        
        # Check it's not persona-focused
        persona_keywords = ["I am", "I currently", "I prescribe", "my practice"]
        found_persona = [kw for kw in persona_keywords if kw in trainer_prompt.lower()]
        if len(found_persona) > 2:
            issues.append("Prompt seems persona-focused rather than trainer-focused")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "length": len(trainer_prompt),
            "word_count": word_count,
            "teaching_keywords_found": found_keywords
        }


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTION FOR EASY USE
# ═══════════════════════════════════════════════════════════════════════════════

async def generate_trainer_prompt(
    client,
    template_data: Dict[str, Any],
    model: str = "gpt-4o"
) -> str:
    """
    Convenience function to generate a trainer prompt for learn mode.
    
    Args:
        client: OpenAI/Azure client
        template_data: Template JSON from extraction
        model: Model to use
    
    Returns:
        Complete trainer prompt as string
    
    Example:
        prompt = await generate_trainer_prompt(
            client=openai_client,
            template_data=my_template
        )
    """
    
    generator = LearnModePromptGenerator(client, model)
    prompt = await generator.generate_trainer_prompt(template_data)
    
    # Validate
    validation = generator.validate_prompt(prompt)
    if not validation["valid"]:
        print(f"[WARNING] Prompt validation issues: {validation['issues']}")
    if validation["warnings"]:
        print(f"[INFO] Prompt warnings: {validation['warnings']}")
    
    print(f"[INFO] Generated trainer prompt: {validation['word_count']} words")
    print(f"[INFO] Teaching keywords found: {', '.join(validation['teaching_keywords_found'])}")
    
    return prompt
