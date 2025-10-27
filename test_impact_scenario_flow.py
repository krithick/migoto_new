"""
Test script to simulate full IMPACT scenario flow and conversation
This will help identify where things might go wrong
"""

import asyncio
import json
from scenario_generator import EnhancedScenarioGenerator
from openai import AsyncAzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv(".env")

# Initialize OpenAI client
azure_openai_client = AsyncAzureOpenAI(
    api_key=os.getenv("api_key"),
    api_version=os.getenv("api_version"),
    azure_endpoint=os.getenv("endpoint")
)

# Your IMPACT scenario text
IMPACT_SCENARIO = """
ACRONYM	Steps	Complete IMPACT	Scoring	 
 	 	 	2	1	0	Additional remarks
I	Introduction	"I am XYZ from Integrace Orthopedics, the youngest top 100 pharma company in India / the makers of Dubinor, Lizolid and Esoz / Trusted by more than 34000 Indian doctors / Leaders in treatment of neuropathic pain and PAD	Complete I AND voice clarity	Incomplete I OR voice unclear	None	Check for the confidence and body language
M	Memorizing last visit	"I visited you last XX weeks ago and detailed ABC"
"in my last visit, we discussed…... And …......"
" Since __ visits, I am promoting XYZ for your patients of ____. However, I am unable to get Rxs. Let me try it once again"	Complete M AND voice clarity	Incomplete M OR voice unclear	None	Check for the confidence and body language
P	Probing	"Have you had an opportunity since then to prescribe ABC?"
"Doctor, would you like more information on ABC"
"Doctor, given a choice, what would you prefer the most in ABC (disease or therapy)?"
"Doctor, what are your key concerns while treating patients of ABC (disease or therapy)	Complete P and voice clarity	Incomplete P OR voice unclar	None	Keep a check on the type of question being asked. FSO should avoid interoogatory or questions that challenge doctor's decision. E.g. Dr, why do you use XXX in ABC (indication)?
Dr, Chemist told me that you use XXX for ABC patients. Why don't you use YYYY?
A	Articulation of relevant brand benefits	"Doctor did you know….&lt;brand benefits&gt; "
"Check for detailing of brands that is relevant to the competition that the Dr is prescribing"
FSO should be able to complete the features as well as benefits for the brand that he is detailing	Complete and Relevant A and Confidence	Incomplete or irrelevant A and fumbling	None	Word "relevant" plays a critical role in terms of detailing as per the competitio in the said dr chamber.
C	Clarify doubts	Check whether the FSO asks about brand conviction
In case of doubts, he should be able to handle it confidently
Even if he borrows time and promises to answer then  - will be considered as 2 or 1 - based on the type of the question raised	Confident ability to C	Incomplete C	None	Ask questions in terms of dosage / key benefits / price to confrim the FSO's confidence.
T	Take commitment	"Thank you for your time Doctor. I look forward for your prescriptions for &lt;brand&gt; in your next patient suffering from &lt;Indication&gt;
Check for the ability to ask and quantify prescription demand.	Clear T with sampling and availability	Incomplete T with or without sampling and availability	None	 
Field	Example	Comments	 
Coaching Title:	SmartDerma Objection Handling	Title of the coaching	 
Coaching Description
 	You are going to meet Dr. Archana Pandey – a gynaecologist. She is in a OPD and has a caesarean section planned after an hour. Today, you are going to launch the new product EO Dine to her.	Describe the scenario here - this will be visible to the learner	 
Background Information to the AI
 	The conversation is about the launch of new product intended for Endometriosis. The doctor being in a metro has many such cases.	Set the context for the AI. Provide detailed background. Giving more information can be helpful. However, the information should be relevant to the coaching scenario.	 
Customer Profile
 	Dr. Archana is a doctor in her early 40's having a practice for more than 15 years in the city. She has a OPD of 40 patients / day with at least two surgical procedures in a week. She owns the nursing home and has a attached pharmacy – Jawahar medical.
 	Give a profile of the customer.	 
Product Details
 	EO-Dine reduces chronic pelvic pain by 49% , Dysmenorrhoea by 44% , Dyspareunia by 20%. EO Dine inhibits ovulation &amp; has high contraceptive efficacy. EO dine is effective in menstrual cycle regulation. Long term use of Dienogest can cause irregular bleeding (Breakthrough bleeding) &amp; Bone loss. EO-Dine is safer and has great tolerability of upto 15 years of use.	Details about the product	 
Suggested Objections	•	How EO-Dine is better than Dienogest?
•	Share the data of efficacy in Endometriosis.	Some of the objections/questions that the physician might raise during the conversation.	 
"""

async def test_full_flow():
    """Test the complete flow from scenario text to conversation"""
    
    print("=" * 80)
    print("STEP 1: ANALYZING SCENARIO AND GENERATING TEMPLATE")
    print("=" * 80)
    
    generator = EnhancedScenarioGenerator(azure_openai_client)
    
    # Extract template data
    template_data = await generator.extract_scenario_info(IMPACT_SCENARIO)
    
    print("\n[OK] Template Data Extracted:")
    print(f"Domain: {template_data.get('general_info', {}).get('domain')}")
    print(f"Scenario Title: {template_data.get('context_overview', {}).get('scenario_title')}")
    print(f"Learn Mode Role: {template_data.get('persona_definitions', {}).get('learn_mode_ai_bot', {}).get('role')}")
    print(f"Assess Mode Role: {template_data.get('persona_definitions', {}).get('assess_mode_ai_bot', {}).get('role')}")
    
    # Check archetype
    archetype_info = template_data.get('archetype_classification', {})
    print(f"\n[ARCHETYPE] {archetype_info.get('primary_archetype')}")
    print(f"Confidence: {archetype_info.get('confidence_score')}")
    print(f"Reasoning: {archetype_info.get('reasoning', 'N/A')[:100]}...")
    
    # Check if archetype-specific fields were injected
    assess_persona = template_data.get('persona_definitions', {}).get('assess_mode_ai_bot', {})
    print(f"\n[FIELDS] Archetype-Specific Fields in Persona:")
    print(f"- Has objection_library: {'objection_library' in assess_persona}")
    print(f"- Has decision_criteria: {'decision_criteria' in assess_persona}")
    print(f"- Has personality_type: {'personality_type' in assess_persona}")
    
    if 'objection_library' in assess_persona:
        print(f"- Objection count: {len(assess_persona.get('objection_library', []))}")
        if assess_persona.get('objection_library'):
            print(f"- First objection: {assess_persona['objection_library'][0]}")
    
    print("\n" + "=" * 80)
    print("STEP 2: GENERATING ASSESS MODE PROMPT")
    print("=" * 80)
    
    # Generate assess mode prompt
    assess_prompt = await generator.generate_assess_mode_from_template(template_data)
    
    print("\n[OK] Assess Mode Prompt Generated")
    print(f"Prompt length: {len(assess_prompt)} characters")
    
    # Check if archetype section is in prompt
    if "objection" in assess_prompt.lower():
        print("[OK] Objection content found in prompt")
    else:
        print("[ERROR] WARNING: No objection content in prompt!")
    
    if "decision criteria" in assess_prompt.lower():
        print("[OK] Decision criteria found in prompt")
    else:
        print("[ERROR] WARNING: No decision criteria in prompt!")
    
    # Save prompt for inspection
    with open("d:/migoto_dev/migoto_new/test_assess_prompt.txt", "w", encoding="utf-8") as f:
        f.write(assess_prompt)
    print("\n[SAVED] Full prompt saved to: test_assess_prompt.txt")
    
    print("\n" + "=" * 80)
    print("STEP 3: SIMULATING CONVERSATION - GOOD USER")
    print("=" * 80)
    
    # Simulate conversation with good user
    conversation_history = []
    
    test_conversations = [
        {
            "name": "GOOD USER (Follows IMPACT)",
            "messages": [
                "Hello Dr. Archana, I am Rajesh from Integrace Orthopedics, the makers of Dubinor, Lizolid and Esoz, trusted by more than 34,000 Indian doctors.",
                "I visited you 3 weeks ago and detailed our endometriosis portfolio. Since then, have you had a chance to prescribe any of our products?",
                "That's great that you're treating endometriosis actively. Doctor, what are your key concerns when treating endometriosis patients?",
                "Exactly, Doctor. That's where EO-Dine excels. It reduces chronic pelvic pain by 49%, dysmenorrhea by 44%, and has superior tolerability for up to 15 years compared to Dienogest, which can cause bone loss with long-term use.",
                "I have the clinical data here showing head-to-head comparisons. EO-Dine has high contraceptive efficacy and better safety profile. Can I share these studies with you?",
                "Thank you Doctor. I look forward to your prescriptions for EO-Dine in your next endometriosis patient. I'll leave the data and samples with your staff."
            ]
        },
        {
            "name": "BAD USER (Skips IMPACT)",
            "messages": [
                "Hi, I'm here to talk about EO-Dine.",
                "It's a new product for endometriosis.",
                "Because it's better.",
                "It reduces pain.",
                "I don't have the data with me right now.",
                "Okay, bye."
            ]
        }
    ]
    
    for test_case in test_conversations:
        print(f"\n{'=' * 80}")
        print(f"TEST CASE: {test_case['name']}")
        print(f"{'=' * 80}\n")
        
        conversation_history = []
        
        for i, user_message in enumerate(test_case['messages'], 1):
            print(f"\n--- Turn {i} ---")
            print(f"USER: {user_message}")
            
            # Build messages for API
            messages = [
                {"role": "system", "content": assess_prompt}
            ]
            
            for msg in conversation_history:
                messages.append(msg)
            
            messages.append({"role": "user", "content": user_message})
            
            # Get bot response
            try:
                response = await azure_openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=300
                )
                
                bot_response = response.choices[0].message.content
                print(f"BOT (Dr. Archana): {bot_response}")
                
                # Add to history
                conversation_history.append({"role": "user", "content": user_message})
                conversation_history.append({"role": "assistant", "content": bot_response})
                
                # Check if conversation ended
                if "[FINISH]" in bot_response:
                    print("\n[END] Conversation ended by bot")
                    break
                    
            except Exception as e:
                print(f"[ERROR] Error getting bot response: {e}")
                break
        
        print(f"\n{'=' * 80}")
        print(f"END OF TEST CASE: {test_case['name']}")
        print(f"Total turns: {len(conversation_history) // 2}")
        print(f"{'=' * 80}\n")
    
    print("\n" + "=" * 80)
    print("STEP 4: ANALYSIS OF POTENTIAL ISSUES")
    print("=" * 80)
    
    issues_found = []
    
    # Check 1: Archetype fields injection
    if 'objection_library' not in assess_persona or not assess_persona.get('objection_library'):
        issues_found.append("[ERROR] ISSUE: Objection library not injected into persona")
    else:
        print("[OK] Objection library properly injected")
    
    # Check 2: Archetype section in prompt
    if "objection" not in assess_prompt.lower():
        issues_found.append("[ERROR] ISSUE: Archetype-specific behavior not in prompt")
    else:
        print("[OK] Archetype-specific behavior in prompt")
    
    # Check 3: IMPACT framework in knowledge base
    conversation_topics = template_data.get('knowledge_base', {}).get('conversation_topics', [])
    has_impact = any('IMPACT' in str(topic).upper() or 'introduction' in str(topic).lower() 
                     for topic in conversation_topics)
    if not has_impact:
        issues_found.append("[WARN] WARNING: IMPACT framework may not be in conversation topics")
    else:
        print("[OK] IMPACT framework detected in conversation topics")
    
    # Check 4: Product details in knowledge base
    key_facts = template_data.get('knowledge_base', {}).get('key_facts', [])
    has_product = any('EO-Dine' in str(fact) or 'Dienogest' in str(fact) for fact in key_facts)
    if not has_product:
        issues_found.append("[WARN] WARNING: Product details may not be in key facts")
    else:
        print("[OK] Product details in key facts")
    
    if issues_found:
        print("\n[ISSUES] ISSUES FOUND:")
        for issue in issues_found:
            print(issue)
    else:
        print("\n[OK] No critical issues found!")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    
    # Save full template data for inspection
    with open("d:/migoto_dev/migoto_new/test_template_data.json", "w", encoding="utf-8") as f:
        json.dump(template_data, f, indent=2, default=str)
    print("\n[SAVED] Full template data saved to: test_template_data.json")

if __name__ == "__main__":
    asyncio.run(test_full_flow())
