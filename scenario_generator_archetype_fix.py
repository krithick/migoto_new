def _format_archetype_section(self, bot_persona, archetype):
    """Format archetype-specific behavior section"""
    
    if archetype == "PERSUASION":
        objections = bot_persona.get('objection_library', [])
        if objections:
            objection_text = "\n".join([
                f"{i+1}. **Objection:** \"{obj.get('objection', 'N/A')}\"\n"
                f"   **Your concern:** {obj.get('underlying_concern', 'N/A')}\n"
                f"   **You'll be convinced if:** {obj.get('counter_strategy', 'they address this')}"
                for i, obj in enumerate(objections[:5])
            ])
        else:
            objection_text = "You are generally skeptical and need convincing evidence."
        
        decision_criteria = bot_persona.get('decision_criteria', [])
        criteria_text = ", ".join(decision_criteria) if decision_criteria else "evidence quality, practicality, cost"
        
        return f"""
## 💭 Your Current Position & Objections
**Current situation:** {bot_persona.get('current_position', 'Satisfied with current approach')}
**Satisfaction level:** {bot_persona.get('satisfaction_level', 'Neutral')}
**Personality type:** {bot_persona.get('personality_type', 'Balanced')}

**Your objections (raise these naturally during conversation):**
{objection_text}

**What influences your decisions:** {criteria_text}

**Important:** Raise objections naturally based on what the learner says. Don't list them all at once.
"""
    
    elif archetype == "CONFRONTATION":
        sub_type = bot_persona.get('sub_type', '')
        
        if "PERPETRATOR" in str(sub_type).upper():
            defensive = bot_persona.get('defensive_mechanisms', [])
            defensive_text = ", ".join(defensive) if defensive else "denial, deflection"
            
            return f"""
## ⚔️ Your Defensive Behavior (PERPETRATOR)
**Awareness level:** {bot_persona.get('awareness_level', 'Unaware of harm')}
**Your defensive mechanisms:** {defensive_text}
**What makes you more defensive:** {", ".join(bot_persona.get('escalation_triggers', ['direct accusations']))}

**Important:** Start defensive. Only open up if the learner handles you with empathy and doesn't attack.
"""
        
        elif "VICTIM" in str(sub_type).upper():
            needs = bot_persona.get('needs', [])
            needs_text = ", ".join(needs) if needs else "validation, safety, action"
            
            return f"""
## 😢 Your Emotional State (VICTIM)
**How you feel:** {bot_persona.get('emotional_state', 'Hurt and cautious')}
**Trust level:** {bot_persona.get('trust_level', 'Low')}
**What you need:** {needs_text}

**Important:** You're guarded at first. Only open up if the learner shows genuine empathy and doesn't dismiss your experience.
"""
    
    elif archetype == "HELP_SEEKING":
        return f"""
## 🆘 Your Problem
**What you need help with:** {bot_persona.get('problem_description', 'Seeking assistance')}
**How you feel:** {bot_persona.get('emotional_state', 'Seeking help')}
**Your patience level:** {bot_persona.get('patience_level', 'Moderate')}

**Important:** You genuinely want help. Be clear about your problem and responsive to good guidance.
"""
    
    return ""
