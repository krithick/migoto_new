# PROMPT FOR AMAZON Q - System Prompt Generator

```
I need you to implement a System Prompt Generator that creates rich system prompts from template and persona data.

**READ THIS GUIDE:**
/mnt/user-data/outputs/SYSTEM_PROMPT_GENERATOR.md

**WHAT TO DO:**

Step 1: Create the File
- Create core/system_prompt_generator.py
- Copy the complete code from the guide

Step 2: Paste Architecture Guide
- In the _load_architecture_guide() method
- Replace {PASTE_YOUR_6_SECTION_ARCHITECTURE_HERE} with the user's 6-section architecture
- User will provide this separately

Step 3: Test It
- Create a simple test that:
  * Takes sample template_data and persona_data
  * Calls generate_system_prompt()
  * Prints the result
  * Validates it has all 6 sections

Step 4: Integration
- Find where conversations are created in our codebase
- Add system prompt generation before starting conversation
- Store the generated prompt for use

**KEY POINTS:**
- Single-pass generation (one LLM call)
- Uses existing OpenAI/Azure client
- Returns complete, ready-to-use system prompt
- ~200 lines of code total

**DELIVERABLES:**
1. core/system_prompt_generator.py created
2. Test showing it works
3. Integration into conversation creation flow

Start by creating the file with the code from the guide.
```

---

## 📋 What You Need to Give Amazon Q:

### 1. This Prompt (above)

### 2. Your 6-Section Architecture Text
When Amazon Q asks for the architecture guide, paste your text that starts with:
```
🏗️ Proposed Prompt Architecture:
Structure: 6 Core Sections
┌──────────────────────────────────────────────────────┐
│ SECTION 1: CRITICAL RULES (Universal - Top Priority)│
...
```

All the way to the end with examples and structure.

---

## ✅ That's It!

Amazon Q will:
1. ✅ Read the comprehensive guide
2. ✅ Create the file with all the code
3. ✅ Ask you for the architecture text to paste
4. ✅ Test it
5. ✅ Integrate it

**Estimated time:** 30-60 minutes for full integration
