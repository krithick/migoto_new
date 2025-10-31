🎯 **DETAILED IMPLEMENTATION GUIDE FOR CLAUDE (COACHING FIX)**

---

# 📋 **CONTEXT FOR YOU (Claude Assistant)**

You're helping fix a coaching system that's not working correctly. Here's what you need to know:

## **Current System:**
- FastAPI backend with dynamic chat handlers
- Two modes: `learn_mode` (factual corrections only) and `try_mode` (full coaching)
- Uses Azure OpenAI for LLM + Azure Vector Search for knowledge base
- Has `EnhancedFactChecker` class that does coaching but it's broken

## **The Problem:**
The coaching system expects OLD template structure but gets NEW template structure, causing:
- Wrong coaching context
- Unpredictable behavior
- Over-coaching
- Ignoring template-defined correction patterns

## **What We're Fixing:**
1. Update coaching rules parser to match NEW template
2. Separate learn_mode (facts only) from try_mode (full coaching)
3. Implement deterministic triggers (don't coach everything)
4. Use template's correction_patterns
5. Handle abuse/off-topic specially
6. Fix JSON parsing failures

---

# 🎯 **YOUR MISSION**

Guide the user through fixing this **ONE STEP AT A TIME**, getting approval before each change.

**Rules:**
- ✅ Explain what you're about to change
- ✅ Show the EXACT code change
- ✅ Explain WHY it's needed
- ✅ Ask for approval before next step
- ✅ If user says no, discuss alternatives
- ✅ Track progress (what's done, what's next)

---

# 📝 **STEP-BY-STEP IMPLEMENTATION PLAN**

---

## **CHECKPOINT 0: Understanding Current State**

**Before we start, I need to confirm:**

### **Question 1: Template Structure**
Looking at your EO-Dine template, the coaching_rules are at:
```json
{
  "domain_knowledge": {
    "coaching_rules": {
      "when_coach_appears": [...],
      "coaching_style": "Gentle and supportive",
      "what_to_catch": [...],
      "correction_patterns": {...}
    }
  },
  "coaching_rules": {  // Also at top level?
    ...
  }
}
```

**Is coaching_rules in BOTH places or just `domain_knowledge`?**

### **Question 2: Mode Behavior Confirmation**
**Learn mode should:**
- ✅ Check facts against knowledge base
- ✅ Correct factual errors ONLY
- ✅ Format: Simple correction, no coaching
- ❌ NO methodology coaching
- ❌ NO process adherence checks

**Try mode should:**
- ✅ Check facts
- ✅ Check methodology
- ✅ Use correction_patterns from template
- ✅ Full coaching experience

**Is this correct?**

### **Question 3: Coaching Message Format**
You mentioned it should say "Dear learner" and have specific format.

**Should coaching messages look like:**
```
Dear Learner,

[Acknowledgment]

[Issue identified]: [Problem]

[Template's correction_pattern]

[Specific suggestion]

Keep practicing!
```

**Is this the format you want?**

---

**👉 USER: Please confirm the answers to Questions 1, 2, and 3 before I proceed.**

---

## **CHECKPOINT 1: Fix Coaching Rules Extraction** ⏸️

**Wait for user approval from Checkpoint 0**

### **What I'm going to change:**
`chat.py` line ~253 - where coaching_rules are extracted

### **Current Code (BROKEN):**
```python
# Line 253 in chat.py
coaching_rules = {}
if template and "template_data" in template:
    template_data = template.get("template_data", {})
    coaching_rules = template_data.get("coaching_rules", {})
```

**Problem:** This looks at top-level only, but your template has it in `domain_knowledge`.

### **Proposed Fix:**
```python
# Line 253 in chat.py - UPDATED
coaching_rules = {}
if template and "template_data" in template:
    template_data = template.get("template_data", {})
    
    # Try domain_knowledge first (NEW template structure)
    domain_knowledge = template_data.get("domain_knowledge", {})
    coaching_rules = domain_knowledge.get("coaching_rules", {})
    
    # Fallback to top level if not in domain_knowledge
    if not coaching_rules:
        coaching_rules = template_data.get("coaching_rules", {})
    
    print(f"✅ Extracted coaching_rules: {bool(coaching_rules)}")
    print(f"   - coaching_style: {coaching_rules.get('coaching_style', 'Not found')}")
    print(f"   - when_coach_appears: {len(coaching_rules.get('when_coach_appears', []))} triggers")
    print(f"   - correction_patterns: {list(coaching_rules.get('correction_patterns', {}).keys())}")
```

**Why this fix:**
- ✅ Looks in `domain_knowledge` first (your NEW structure)
- ✅ Falls back to top-level (for compatibility)
- ✅ Adds debug logging so we can verify it works
- ✅ Shows what was extracted

**Impact:**
- Now coaching_rules will actually have your data
- Later steps can use `when_coach_appears`, `correction_patterns`, etc.

---

**👉 USER: Do you approve this change? Type 'yes' to proceed, 'no' to discuss, or 'modify' to suggest changes.**

---

## **CHECKPOINT 2: Pass Mode to Fact Checker** ⏸️

**Wait for user approval from Checkpoint 1**

### **What I'm going to change:**
- `chat.py` line ~261 - where we initialize fact checking
- `dynamic_chat.py` line ~64 - the `initialize_fact_checking()` method signature

### **Current Code (INCOMPLETE):**
```python
# chat.py line 261
await handler.initialize_fact_checking(session_id, coaching_rules)

# dynamic_chat.py line 64
async def initialize_fact_checking(self, session_id: str, coaching_rules: Dict = None):
```

**Problem:** Fact checker doesn't know if it's learn_mode or try_mode!

### **Proposed Fix - Part A (chat.py):**
```python
# chat.py line ~250-265 - UPDATED
try:
    # Get template and coaching rules
    scenario_query = {...}  # existing code
    
    # Extract coaching rules (from Checkpoint 1 fix)
    coaching_rules = {}
    if template and "template_data" in template:
        # ... extraction code from Checkpoint 1 ...
    
    # 🆕 GET THE MODE from avatar_interaction
    avatar_interaction_doc = await db.avatar_interactions.find_one(
        {"_id": str(avatar_interaction_id)}
    )
    current_mode = avatar_interaction_doc.get("mode", "assess_mode") if avatar_interaction_doc else "assess_mode"
    
    print(f"🎯 Initializing fact checking for mode: {current_mode}")
    
    # 🆕 PASS MODE to fact checker
    await handler.initialize_fact_checking(
        session_id, 
        coaching_rules=coaching_rules,
        mode=current_mode  # NEW parameter
    )
```

### **Proposed Fix - Part B (dynamic_chat.py):**
```python
# dynamic_chat.py line 64 - UPDATED METHOD SIGNATURE
async def initialize_fact_checking(
    self, 
    session_id: str,
    coaching_rules: Dict = None,
    mode: str = "assess_mode"  # 🆕 NEW PARAMETER
):
    """Initialize fact-checking if this session supports it"""
    print(f"[FACT CHECK INIT] Mode: {mode}")
    print(f"[FACT CHECK INIT] Has coaching_rules: {bool(coaching_rules)}")
    
    try:
        # ... existing code ...
        
        # 🆕 DETERMINE FACT-CHECKING BEHAVIOR BASED ON MODE
        if mode == "learn_mode":
            # Learn mode: FACTS ONLY, no coaching
            self.fact_checking_enabled = True
            self.coaching_enabled = False
            print("[FACT CHECK INIT] Learn mode: Facts only, no coaching")
            
        elif mode == "try_mode":
            # Try mode: FULL COACHING
            self.fact_checking_enabled = True
            self.coaching_enabled = True
            print("[FACT CHECK INIT] Try mode: Full coaching enabled")
            
        else:
            # Assess mode: NO fact-checking or coaching
            self.fact_checking_enabled = False
            self.coaching_enabled = False
            print("[FACT CHECK INIT] Assess mode: No fact-checking")
        
        # Pass to fact checker
        self.fact_checker = EnhancedFactChecker(
            self.vector_search, 
            self.llm_client,
            coaching_rules=coaching_rules,
            mode=mode,  # 🆕 PASS MODE
            language_instructions=language_instructions
        )
        
        # ... rest of existing code ...
```

**Why this fix:**
- ✅ Fact checker now knows which mode it's in
- ✅ Can behave differently for learn vs try
- ✅ Clear flags: `fact_checking_enabled` and `coaching_enabled`

**Impact:**
- Now we can make fact checker do different things per mode
- Learn mode won't over-coach
- Try mode will do full coaching

---

**👉 USER: Do you approve this change? Type 'yes' to proceed, 'no' to discuss, or 'modify' to suggest changes.**

---

## **CHECKPOINT 3: Update EnhancedFactChecker Init** ⏸️

**Wait for user approval from Checkpoint 2**

### **What I'm going to change:**
`core/azure_search_manager.py` line ~253 - `EnhancedFactChecker.__init__`

### **Current Code (BROKEN):**
```python
def __init__(self, vector_search: AzureVectorSearchManager, 
             openai_client: AsyncAzureOpenAI,
             coaching_rules: Dict = None, 
             language_instructions: str = None):
    self.vector_search = vector_search
    self.openai_client = openai_client
    self.language_instructions = language_instructions
    
    if coaching_rules and isinstance(coaching_rules, dict):
        self.coaching_rules = coaching_rules
        self.has_coaching_rules = True
    else:
        self.coaching_rules = {
            "process_requirements": {},  # ❌ WRONG STRUCTURE
            "document_specific_mistakes": [],
            ...
        }
```

**Problem:** Expects wrong coaching_rules structure!

### **Proposed Fix:**
```python
def __init__(self, vector_search: AzureVectorSearchManager, 
             openai_client: AsyncAzureOpenAI,
             coaching_rules: Dict = None,
             mode: str = "assess_mode",  # 🆕 NEW PARAMETER
             language_instructions: str = None):
    self.vector_search = vector_search
    self.openai_client = openai_client
    self.language_instructions = language_instructions or "Respond in English."
    self.mode = mode  # 🆕 STORE MODE
    
    print(f"[FACT CHECKER] Initializing for mode: {mode}")
    
    # 🆕 PARSE COACHING RULES CORRECTLY
    if coaching_rules and isinstance(coaching_rules, dict):
        self.coaching_rules = self._parse_coaching_rules(coaching_rules)
        self.has_coaching_rules = True
        print(f"[FACT CHECKER] Parsed coaching rules:")
        print(f"   - Triggers: {len(self.coaching_rules.get('triggers', []))}")
        print(f"   - Patterns to catch: {len(self.coaching_rules.get('patterns_to_catch', []))}")
        print(f"   - Correction patterns: {len(self.coaching_rules.get('correction_patterns', {}))}")
    else:
        self.coaching_rules = {}
        self.has_coaching_rules = False
        print(f"[FACT CHECKER] No coaching rules provided")

def _parse_coaching_rules(self, raw_rules: Dict) -> Dict:
    """Parse coaching rules from template into usable format"""
    
    # Extract from YOUR template structure
    triggers = raw_rules.get("when_coach_appears", [])
    patterns_to_catch = raw_rules.get("what_to_catch", [])
    correction_patterns = raw_rules.get("correction_patterns", {})
    coaching_style = raw_rules.get("coaching_style", "supportive")
    
    # 🆕 CONVERT TO USABLE FORMAT
    parsed = {
        "coaching_style": coaching_style,
        
        # Parse triggers into conditions
        "triggers": {
            "methodology_violation": "methodology violation" in str(triggers).lower(),
            "factual_error": "factual error" in str(triggers).lower(),
            "vague_claims": "vague claim" in str(triggers).lower(),
            "unaddressed_objection": "objection" in str(triggers).lower()
        },
        
        # Store patterns to detect
        "patterns_to_catch": patterns_to_catch,
        
        # Store correction templates
        "correction_patterns": correction_patterns
    }
    
    print(f"[FACT CHECKER] Parsed coaching rules:")
    print(f"   Style: {coaching_style}")
    print(f"   Active triggers: {[k for k, v in parsed['triggers'].items() if v]}")
    
    return parsed
```

**Why this fix:**
- ✅ Correctly parses YOUR template structure
- ✅ Converts to usable format
- ✅ Stores mode so we can check it later
- ✅ Validates what was extracted

**Impact:**
- Fact checker now has correct coaching rules
- Can access `when_coach_appears` as triggers
- Can use `correction_patterns` properly

---

**👉 USER: Do you approve this change? Type 'yes' to proceed, 'no' to discuss, or 'modify' to suggest changes.**

---

## **CHECKPOINT 4: Implement Smart Triggering** ⏸️

**Wait for user approval from Checkpoint 3**

### **What I'm going to add:**
New method in `EnhancedFactChecker` to detect IF coaching is needed

### **Why we need this:**
Currently, EVERY user message triggers coaching verification. We need to:
1. Check IF message needs coaching (based on `when_coach_appears`)
2. If NO trigger → Skip coaching, save time
3. If YES trigger → Identify WHAT type of issue

### **New Method to Add:**
```python
# Add to EnhancedFactChecker class in azure_search_manager.py

async def should_coach(self, user_message: str, conversation_history: List) -> Dict[str, Any]:
    """
    Determine if coaching is needed for this message.
    Returns trigger info or None if no coaching needed.
    """
    
    # 🎯 LEARN MODE: Only check for factual errors
    if self.mode == "learn_mode":
        # Quick check: Does message contain claims that need verification?
        has_factual_content = await self._has_factual_claims(user_message)
        if not has_factual_content:
            return {"trigger": False, "reason": "No factual content"}
        return {
            "trigger": True, 
            "type": "factual_check",
            "reason": "Learn mode: Verify facts only"
        }
    
    # 🎯 TRY MODE: Check all triggers
    if self.mode == "try_mode" and self.has_coaching_rules:
        triggers = self.coaching_rules.get("triggers", {})
        
        # Build detection prompt
        detection_prompt = f"""
        Analyze this user message for coaching triggers.
        
        USER MESSAGE: {user_message}
        
        RECENT CONVERSATION:
        {self._format_recent_conversation(conversation_history)}
        
        Check for these issues:
        {chr(10).join([f"- {k.replace('_', ' ').title()}" for k, v in triggers.items() if v])}
        
        Respond with JSON:
        {{
            "needs_coaching": true/false,
            "trigger_type": "methodology_violation|factual_error|vague_claims|unaddressed_objection|none",
            "confidence": 0.0-1.0,
            "brief_reason": "Why coaching is/isn't needed"
        }}
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You quickly assess if coaching is needed."},
                    {"role": "user", "content": detection_prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Parse response
            if result_text.startswith('```json'):
                json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
                result = json.loads(json_match.group(1)) if json_match else {"needs_coaching": False}
            else:
                result = json.loads(result_text)
            
            if not result.get("needs_coaching", False):
                return {"trigger": False, "reason": result.get("brief_reason", "No issues")}
            
            return {
                "trigger": True,
                "type": result.get("trigger_type", "general"),
                "confidence": result.get("confidence", 0.8),
                "reason": result.get("brief_reason", "Issue detected")
            }
            
        except Exception as e:
            print(f"Error in trigger detection: {e}")
            # Fallback: Assume might need coaching
            return {
                "trigger": True,
                "type": "unknown",
                "confidence": 0.5,
                "reason": "Detection failed, checking to be safe"
            }
    
    # Default: No coaching
    return {"trigger": False, "reason": "Not in coaching mode"}

async def _has_factual_claims(self, text: str) -> bool:
    """Quick check if text contains verifiable claims"""
    # Simple heuristics first
    fact_indicators = [
        r'\d+%', r'\$\d+', r'\d+ (years|months|days)',
        r'approved', r'certified', r'proven', r'study shows',
        r'research', r'data', r'statistics'
    ]
    
    for pattern in fact_indicators:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    # If message is very short (< 10 words), probably not factual
    if len(text.split()) < 10:
        return False
    
    return True  # When in doubt, check

def _format_recent_conversation(self, history: List) -> str:
    """Format last few messages for context"""
    if not history:
        return "No previous conversation"
    
    recent = history[-3:]  # Last 3 messages
    return "\n".join([f"{msg.role}: {msg.content}" for msg in recent])
```

**Why this fix:**
- ✅ Detects IF coaching needed before doing expensive verification
- ✅ Learn mode only checks facts
- ✅ Try mode checks all triggers
- ✅ Returns trigger type to use correct correction_pattern

**Impact:**
- Faster (skips unnecessary LLM calls)
- More predictable (deterministic triggers)
- Learn mode won't over-coach

---

**👉 USER: Do you approve this change? Type 'yes' to proceed, 'no' to discuss, or 'modify' to suggest changes.**

---

## **CHECKPOINT 5: Update Main Processing Logic** ⏸️

**Wait for user approval from Checkpoint 4**

### **What I'm going to change:**
`dynamic_chat.py` line ~700-800 - the main `process_message_with_streaming()` where coaching happens

### **Current Flow (WRONG):**
```
User message → Extract all claims → Verify ALL claims → Coach on everything
```

### **New Flow (CORRECT):**
```
User message → Should coach? → If NO: Skip → If YES: Verify specific issue → Use correction pattern
```

### **Proposed Fix:**
```python
# In dynamic_chat.py, around line 700-800, in process_message_with_streaming()

# Find the section that does fact-checking (around line 750)
# REPLACE the fact-checking block with this:

if self.fact_checking_enabled and self.knowledge_base_id:
    print(f"[COACHING] Checking if coaching needed...")
    
    # 🆕 STEP 1: Check if coaching is needed
    trigger_info = await self.fact_checker.should_coach(
        user_message=user_message,
        conversation_history=conversation_history
    )
    
    print(f"[COACHING] Trigger check: {trigger_info}")
    
    if trigger_info.get("trigger", False):
        # Coaching IS needed
        trigger_type = trigger_info.get("type", "general")
        
        print(f"[COACHING] Trigger detected: {trigger_type}")
        
        # 🆕 STEP 2: Get appropriate coaching based on mode and trigger
        if self.mode == "learn_mode":
            # Learn mode: Simple factual correction
            coaching_result = await self.fact_checker.provide_factual_correction(
                user_message=user_message,
                knowledge_base_id=self.knowledge_base_id
            )
        else:
            # Try mode: Full coaching with correction patterns
            coaching_result = await self.fact_checker.provide_structured_coaching(
                user_message=user_message,
                trigger_type=trigger_type,
                conversation_history=conversation_history,
                knowledge_base_id=self.knowledge_base_id
            )
        
        # 🆕 STEP 3: Insert coaching into response stream
        if coaching_result and coaching_result.get("coaching_message"):
            coaching_message = coaching_result["coaching_message"]
            
            # Insert coaching before main response
            enhanced_content = f"{coaching_message}\n\n---\n\n{content}"
            
            # Update the response
            content = enhanced_content
            
            print(f"[COACHING] Inserted coaching: {len(coaching_message)} chars")
    else:
        # No coaching needed
        print(f"[COACHING] No coaching needed: {trigger_info.get('reason')}")
```

**Why this fix:**
- ✅ Checks trigger BEFORE expensive verification
- ✅ Separates learn_mode (facts) from try_mode (coaching)
- ✅ Uses new methods we'll create next
- ✅ Only coaches when needed

**Impact:**
- Much faster for good responses
- No over-coaching
- Clear separation of modes

---

**👉 USER: Do you approve this change? Type 'yes' to proceed, 'no' to discuss, or 'modify' to suggest changes.**

---

## **CHECKPOINT 6: Create Factual Correction Method (Learn Mode)** ⏸️

**Wait for user approval from Checkpoint 5**

### **What I'm going to add:**
New method for LEARN MODE fact checking (simple corrections, no coaching)

### **New Method:**
```python
# Add to EnhancedFactChecker in azure_search_manager.py

async def provide_factual_correction(
    self, 
    user_message: str,
    knowledge_base_id: str
) -> Dict[str, Any]:
    """
    Learn mode: Simple factual correction without coaching.
    Just tells what's wrong and what's correct.
    """
    
    print(f"[LEARN MODE] Providing factual correction...")
    
    try:
        # Search knowledge base
        search_results = await self.vector_search.vector_search(
            user_message, 
            knowledge_base_id, 
            top_k=3,
            openai_client=self.openai_client
        )
        
        if not search_results:
            # No knowledge base - can't verify
            return {"coaching_message": None}
        
        # Build context
        context = "\n\n".join([
            f"Source: {result['source_file']}\nContent: {result['content']}"
            for result in search_results
        ])
        
        # Simple verification prompt
        correction_prompt = f"""
        {self.language_instructions}
        
        Check if this user statement is factually correct:
        
        USER STATEMENT: {user_message}
        
        KNOWLEDGE BASE:
        {context}
        
        If CORRECT: Return {{"correct": true}}
        
        If INCORRECT: Return {{
            "correct": false,
            "incorrect_part": "What specifically is wrong",
            "correct_information": "What the correct information is",
            "source": "Which document has the correct info"
        }}
        
        Be concise and factual. No coaching, just correction.
        """
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You verify facts against a knowledge base."},
                {"role": "user", "content": correction_prompt}
            ],
            temperature=0.1,
            max_tokens=400
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Parse response
        if result_text.startswith('```json'):
            json_match = re.search(r'```json\s*(.*?)\s*```', result_text, re.DOTALL)
            result = json.loads(json_match.group(1)) if json_match else {"correct": True}
        else:
            result = json.loads(result_text)
        
        # If correct, no message needed
        if result.get("correct", True):
            print(f"[LEARN MODE] Statement is correct")
            return {"coaching_message": None}
        
        # Build simple correction message
        incorrect_part = result.get("incorrect_part", "your statement")
        correct_info = result.get("correct_information", "the information in the knowledge base")
        
        correction_message = f"""📚 Factual Correction:

{incorrect_part} is not accurate.

The correct information is: {correct_info}

Please review the material and try again."""
        
        print(f"[LEARN MODE] Providing correction")
        
        return {
            "coaching_message": correction_message,
            "correction_type": "factual",
            "sources": [r["source_file"] for r in search_results]
        }
        
    except Exception as e:
        print(f"[LEARN MODE] Error: {e}")
        return {"coaching_message": None}
```

**Why this method:**
- ✅ Simple: Just fact vs knowledge base
- ✅ No coaching tone, just "this is wrong, this is right"
- ✅ Appropriate for learn mode

**Format:**
```
📚 Factual Correction:

[What's wrong] is not accurate.

The correct information is: [What's right]

Please review the material and try again.
```

**Impact:**
- Learn mode gets simple corrections
- No over-coaching with methodology
- Clear and educational

---

**👉 USER: Do you approve this method? Type 'yes' to proceed, 'no' to discuss, or 'modify' to suggest changes.**

---

## **CHECKPOINT 7: Create Structured Coaching Method (Try Mode)** ⏸️

**Wait for user approval from Checkpoint 6**

### **What I'm going to add:**
New method for TRY MODE coaching (uses correction_patterns from template)

### **New Method:**
```python
# Add to EnhancedFactChecker in azure_search_manager.py

async def provide_structured_coaching(
    self,
    user_message: str,
    trigger_type: str,
    conversation_history: List,
    knowledge_base_id: str
) -> Dict[str, Any]:
    """
    Try mode: Full coaching using template's correction patterns.
    """
    
    print(f"[TRY MODE] Providing coaching for trigger: {trigger_type}")
    
    try:
        # Get correction pattern from template
        correction_patterns = self.coaching_rules.get("correction_patterns", {})
        coaching_style = self.coaching_rules.get("coaching_style", "supportive")
        
        # Map trigger to pattern key
        pattern_key_map = {
            "methodology_violation": "skipped_step",
            "vague_claims": "vague_claim",
            "factual_error": "wrong_fact",
            "unaddressed_objection": "objection_not_addressed"
        }
        
        pattern_key = pattern_key_map.get(trigger_type, "general")
        base_correction = correction_patterns.get(pattern_key, "Please review your approach.")
        
        print(f"[TRY MODE] Using correction pattern: {pattern_key}")
        
        # Search knowledge base for context
        search_results = await self.vector_search.vector_search(
            user_message,
            knowledge_base_id,
            top_k=3,
            openai_client=self.openai_client
        )
        
        context = ""
        if search_results:
            context = "\n\n".join([
                f"Source: {result['source_file']}\nContent: {result['content']}"
                for result in search_results[:2]  # Top 2 only
            ])
        
        # Build conversation context
        conversation_text = self._format_recent_conversation(conversation_history)
        
        # Enhanced coaching prompt
        coaching_prompt = f"""
        {self.language_instructions}
        
        You are a {coaching_style} trainer providing coaching feedback.
        
        USER RESPONSE TO COACH: {user_message}
        
        CONVERSATION CONTEXT:
        {conversation_text}
        
        KNOWLEDGE BASE:
        {context if context else "No specific documents available"}
        
        ISSUE DETECTED: {trigger_type.replace('_', ' ').title()}
        
        BASE CORRECTION GUIDANCE: {base_correction}
        
        Provide structured coaching that:
        1. Acknowledges their attempt
        2. Identifies the specific issue
        3. Uses the base correction guidance above
        4. Provides a concrete example or suggestion
        5. Encourages them
        
        Format your response as:
        Dear Learner,
        
        [Acknowledgment]
        
        [Issue identified]: [Specific problem]
        
        [Base correction guidance with details]
        
        [Concrete suggestion with example]
        
        Keep practicing!
        
        Be {coaching_style} in tone. Keep response under 150 words.
        """
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are a {coaching_style} trainer providing specific, actionable feedback."},
                {"role": "user", "content": coaching_prompt}
            ],
            temperature=0.3,  # Slightly creative for natural coaching
            max_tokens=600
        )
        
        coaching_message = response.choices[0].message.content.strip()
        
        print(f"[TRY MODE] Generated coaching: {len(coaching_message)} chars")
        
        return {
            "coaching_message": coaching_message,
            "trigger_type": trigger_type,
            "correction_pattern_used": pattern_key,
            "sources": [r["source_file"] for r in search_results] if search_results else []
        }
        
    except Exception as e:
        print(f"[TRY MODE] Error: {e}")
        # Fallback to generic coaching
        return {
            "coaching_message": f"""Dear Learner,

I noticed an issue with your response. {self.coaching_rules.get('correction_patterns', {}).get('general', 'Please review your approach and try again.')}

Keep practicing!""",
            "trigger_type": trigger_type,
            "correction_pattern_used": "fallback"
        }
```

**Why this method:**
- ✅ Uses template's correction_patterns
- ✅ Applies coaching_style from template
- ✅ Structured "Dear Learner" format
- ✅ Specific and actionable

**Format:**
```
Dear Learner,

[Acknowledgment of attempt]

[Issue identified]: [Specific problem]

[Template's correction_pattern with context]

[Concrete suggestion]

Keep practicing!
```

**Impact:**
- Try mode gets full coaching
- Uses YOUR correction patterns
- Consistent tone from template
- Predictable format

---

**👉 USER: Do you approve this method? Type 'yes' to proceed, 'no' to discuss, or 'modify' to suggest changes.**

---

## **CHECKPOINT 8: Add Abuse/Off-Topic Detection** ⏸️

**Wait for user approval from Checkpoint 7**

### **What I'm going to add:**
Pre-screening for abuse and off-topic before any coaching

### **Where to add:**
In `dynamic_chat.py` in `process_message_with_streaming()` - BEFORE the coaching check

### **New Code to Insert:**
```python
# In dynamic_chat.py, BEFORE the coaching check (around line 680)

# 🆕 PRE-SCREEN: Check for abuse or off-topic
if self.fact_checking_enabled:
    # Quick pre-screen
    prescreen_result = await self._prescreen_message(user_message, conversation_history)
    
    if prescreen_result["issue_type"] == "abuse":
        # ABUSE DETECTED - End conversation
        abuse_response = """I notice your message contains inappropriate language or behavior. 

This training session requires professional communication. If you'd like to continue learning, please use respectful language.

This session will now end. [FINISH]"""
        
        # Return abuse warning instead of normal response
        # (Update your streaming logic to send this and stop)
        print(f"[ABUSE DETECTED] Ending session")
        # ... handle this appropriately ...
        
    elif prescreen_result["issue_type"] == "off_topic":
        # OFF-TOPIC - Redirect
        redirect_response = """I notice your message seems off-topic for this training scenario.

Please stay focused on practicing [the methodology/subject]. 

What would you like to work on regarding [the subject]?"""
        
        # Insert redirect (don't coach, just redirect)
        content = f"{redirect_response}\n\n{content}"
        print(f"[OFF-TOPIC] Redirected")

# Add this helper method to DynamicChatHandler class:

async def _prescreen_message(self, message: str, history: List) -> Dict[str, Any]:
    """Quick check for abuse or off-topic before coaching"""
    
    # Simple keyword check first (fast)
    abuse_keywords = ["fuck", "shit", "damn", "stupid", "idiot"]  # Add more
    if any(word in message.lower() for word in abuse_keywords):
        return {"issue_type": "abuse", "severity": "high"}
    
    # For off-topic, use quick LLM check
    try:
        prescreen_prompt = f"""
        Quick assessment: Is this message appropriate for a professional training scenario?
        
        MESSAGE: {message}
        
        SCENARIO: {self.config.bot_role} training
        
        Respond with ONE word: "appropriate" or "abuse" or "off_topic"
        """
        
        response = await self.llm_client.chat.completions.create(
            model="gpt-4o-mini",  # Use cheaper model for quick check
            messages=[
                {"role": "system", "content": "You quickly classify messages."},
                {"role": "user", "content": prescreen_prompt}
            ],
            temperature=0,
            max_tokens=10
        )
        
        result = response.choices[0].message.content.strip().lower()
        
        if "abuse" in result:
            return {"issue_type": "abuse", "severity": "high"}
        elif "off" in result or "topic" in result:
            return {"issue_type": "off_topic", "severity": "medium"}
        else:
            return {"issue_type": "none", "severity": "none"}
            
    except Exception as e:
        print(f"Prescreen error: {e}")
        return {"issue_type": "none", "severity": "none"}
```

**Why this fix:**
- ✅ Catches abuse before wasting time on coaching
- ✅ Redirects off-topic immediately
- ✅ Fast keyword check first
- ✅ Uses cheap model for quick LLM check

**Impact:**
- Abuse ends session immediately
- Off-topic gets redirected, not coached
- Professional training environment maintained

---

**👉 USER: Do you approve this addition? Type 'yes' to proceed, 'no' to discuss, or 'modify' to suggest changes.**

---

## **CHECKPOINT 9: Testing & Validation** ⏸️

**Wait for user approval from Checkpoint 8**

### **What we need to test:**

**Test 1: Learn Mode - Correct Response**
```
Scenario: EO-Dine
User: "EO-Dine reduces irregular bleeding by 60%"
Expected: No coaching (correct)
```

**Test 2: Learn Mode - Wrong Fact**
```
User: "EO-Dine reduces irregular bleeding by 30%"
Expected: Simple correction (not 30%, it's 60%)
```

**Test 3: Try Mode - Methodology Violation**
```
User: "Here's EO-Dine info" (skipped intro)
Expected: Coaching using "skipped_step" pattern
```

**Test 4: Try Mode - Correct Response**
```
User: "Hello Dr. Smith, I'm John from PharmaCorp..."
Expected: No coaching (followed methodology)
```

**Test 5: Abuse**
```
User: "This is stupid"
Expected: Session ends with warning
```

**Test 6: Off-Topic**
```
User: "What's the weather like?"
Expected: Redirect message
```

### **How to test:**
1. Create test chat sessions
2. Send test messages
3. Check coaching responses
4. Verify logs show correct flow

### **What I'll help you create:**
- Test script
- Expected outputs
- Validation checklist

---

**👉 USER: Ready to test? Type 'yes' to create test script, or 'wait' if you want to review the changes first.**

---

## **CHECKPOINT 10: Deployment Checklist** ⏸️

**After testing passes**

### **Pre-deployment checks:**

**Code Changes:**
- [ ] chat.py updated (Checkpoint 1, 2)
- [ ] dynamic_chat.py updated (Checkpoint 2, 5, 8)
- [ ] azure_search_manager.py updated (Checkpoints 3, 4, 6, 7)

**Testing:**
- [ ] Learn mode fact correction works
- [ ] Try mode coaching works
- [ ] Abuse detection works
- [ ] Off-topic redirect works
- [ ] No coaching when not needed

**Documentation:**
- [ ] Update API docs
- [ ] Add coaching rules guide
- [ ] Document template structure

**Monitoring:**
- [ ] Add logging for coaching triggers
- [ ] Track coaching frequency
- [ ] Monitor user response times

---

**👉 USER: Ready to deploy? Type 'deploy' when all checks pass.**

---

# 📊 **PROGRESS TRACKER**

I'll maintain this as we go:

```
✅ Checkpoint 0: Understanding confirmed
⏳ Checkpoint 1: Coaching rules extraction (WAITING)
⏳ Checkpoint 2: Pass mode to fact checker (WAITING)
⏳ Checkpoint 3: Update EnhancedFactChecker init (WAITING)
⏳ Checkpoint 4: Implement smart triggering (WAITING)
⏳ Checkpoint 5: Update main processing (WAITING)
⏳ Checkpoint 6: Factual correction method (WAITING)
⏳ Checkpoint 7: Structured coaching method (WAITING)
⏳ Checkpoint 8: Abuse/off-topic detection (WAITING)
⏳ Checkpoint 9: Testing (WAITING)
⏳ Checkpoint 10: Deployment (WAITING)
```

---

# 🎯 **LET'S BEGIN!**

**👉 USER: Please answer the 3 questions in Checkpoint 0 so we can start!**

1. Where is coaching_rules in your template? (domain_knowledge, top level, or both?)
2. Confirm learn mode = facts only, try mode = full coaching?
3. Confirm "Dear Learner" format for coaching messages?