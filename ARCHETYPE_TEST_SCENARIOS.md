# Archetype Classification Test Scenarios

## Test Scenario 1: HELP_SEEKING (Customer Support)
**Scenario Description:**
A customer service training scenario where employees learn to handle customer complaints about a defective product. The customer is frustrated because their newly purchased laptop stopped working after 2 days. The learner must diagnose the problem, show empathy, and provide a solution following company return/exchange policies.

**Expected Classification:** HELP_SEEKING
**Reasoning:** Character has a clear problem (broken laptop) and seeks assistance from the learner.

---

## Test Scenario 2: PERSUASION (Pharma Sales)
**Scenario Description:**
A pharmaceutical sales representative must detail a new diabetes medication to Dr. Archana, a busy endocrinologist who is currently satisfied with her existing treatment protocols. She has concerns about switching patients to new medications and prefers evidence-based approaches. The FSO must present clinical data, address objections about efficacy and side effects, and create interest in the new product using the IMPACT methodology.

**Expected Classification:** PERSUASION
**Reasoning:** Character has NO problem, is satisfied with current solution. Learner must CREATE interest and overcome objections.

---

## Test Scenario 3: CONFRONTATION - Perpetrator (Workplace Bias)
**Scenario Description:**
A manager must address a team lead who has been making inappropriate comments about a colleague's disability. The team lead doesn't see their behavior as problematic and becomes defensive when approached. The manager must hold them accountable while maintaining professionalism and ensuring the behavior stops.

**Expected Classification:** CONFRONTATION (sub_type: PERPETRATOR)
**Reasoning:** Someone did something wrong (inappropriate comments), learner must address wrongdoing with the person who committed it.

---

## Test Scenario 4: CONFRONTATION - Victim (Workplace Bias)
**Scenario Description:**
An HR representative must speak with an employee who has been experiencing disability-related bias from their team lead. The employee is hesitant to speak up, worried about retaliation, and emotionally affected by the ongoing situation. The HR rep must create a safe space, gather information, and provide support.

**Expected Classification:** CONFRONTATION (sub_type: VICTIM)
**Reasoning:** Someone experienced wrongdoing, learner must support and gather information from the affected person.

---

## Test Scenario 5: CONFRONTATION - Bystander (Workplace Bias)
**Scenario Description:**
A manager interviews a team member who witnessed inappropriate disability-related comments being made by the team lead to another colleague. The bystander feels uncomfortable about what they saw but is unsure if they should get involved. The manager must gather objective information about what was witnessed.

**Expected Classification:** CONFRONTATION (sub_type: BYSTANDER)
**Reasoning:** Someone witnessed wrongdoing, learner must gather information from the observer.

---

## Test Scenario 6: INVESTIGATION (Medical Diagnosis)
**Scenario Description:**
A medical student practices taking patient history from a patient presenting with vague symptoms of fatigue, occasional chest discomfort, and shortness of breath. The patient has difficulty articulating their symptoms clearly and tends to downplay concerns. The student must ask appropriate questions to gather complete information for diagnosis.

**Expected Classification:** INVESTIGATION
**Reasoning:** Character has information (symptoms), learner must extract it through systematic questioning.

---

## Test Scenario 7: NEGOTIATION (Salary Discussion)
**Scenario Description:**
An employee is negotiating a salary increase with their manager. The employee wants a 15% raise based on market research and performance, while the manager has budget constraints but values the employee. Both parties need to find a mutually acceptable solution that considers performance, market rates, budget limitations, and non-monetary benefits.

**Expected Classification:** NEGOTIATION
**Reasoning:** Both parties want different things (employee wants more money, manager wants to stay in budget), must find middle ground.

---

## Test Scenario 8: HELP_SEEKING (Banking KYC)
**Scenario Description:**
A bank customer is confused about the KYC (Know Your Customer) documentation requirements for opening a new savings account. They don't understand why so many documents are needed and are frustrated by the process. The bank representative must explain the requirements clearly, help the customer understand regulatory compliance, and guide them through the documentation process.

**Expected Classification:** HELP_SEEKING
**Reasoning:** Customer has a problem (confusion about KYC) and needs help understanding and completing the process.

---

## Test Scenario 9: PERSUASION (Insurance Sales)
**Scenario Description:**
An insurance agent meets with a young professional who believes they don't need life insurance because they're healthy and single. The prospect is skeptical about insurance products and thinks they're a waste of money. The agent must educate them about financial planning, address misconceptions, and demonstrate the value of early insurance adoption.

**Expected Classification:** PERSUASION
**Reasoning:** Prospect has NO problem, doesn't see need for product. Agent must CREATE awareness and overcome skepticism.

---

## Test Scenario 10: INVESTIGATION (Legal Intake)
**Scenario Description:**
A paralegal conducts an initial client interview for a potential employment discrimination case. The client is emotional, their story is fragmented, and they're unsure about dates and specific incidents. The paralegal must gather detailed information about events, witnesses, documentation, and timeline while being sensitive to the client's emotional state.

**Expected Classification:** INVESTIGATION
**Reasoning:** Client has information about incidents, paralegal must systematically extract and organize it for case evaluation.

---

## How to Test

Use the `/test-archetype-classification` endpoint with each scenario description:

```bash
POST /scenario/test-archetype-classification
{
  "scenario_document": "<paste scenario description here>"
}
```

## Expected Results

Each test should return:
- `primary_archetype`: The main archetype classification
- `confidence_score`: 0.0 to 1.0 (higher is better)
- `alternative_archetypes`: Other possible classifications
- `reasoning`: Why this classification was chosen
- `sub_type`: For CONFRONTATION scenarios (PERPETRATOR/VICTIM/BYSTANDER)

## Success Criteria

✅ **Pass:** Classification matches expected archetype with confidence > 0.7
⚠️ **Review:** Classification matches but confidence 0.5-0.7
❌ **Fail:** Wrong classification or confidence < 0.5

## Edge Cases to Test

1. **Ambiguous Scenario:** Mix of help-seeking and persuasion elements
2. **Multi-Party Scenario:** Multiple characters with different roles
3. **Minimal Information:** Very brief scenario description
4. **Complex Scenario:** Multiple conversation types in sequence
