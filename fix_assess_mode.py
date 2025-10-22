import re

# Read file
with open('scenario_generator.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the section
old_section = """            bot_persona = template_data.get('persona_definitions', {}).get('assess_mode_ai_bot', {})
            
            # Ensure bot_persona is a dictionary
            if not isinstance(bot_persona, dict):

                bot_persona = {}
            
            formatted_template = self.assess_mode_template.format("""

new_section = """            bot_persona = template_data.get('persona_definitions', {}).get('assess_mode_ai_bot', {})
            archetype_classification = template_data.get('archetype_classification', {})
            archetype = str(archetype_classification.get('primary_archetype', '')).split('.')[-1]
            
            # Ensure bot_persona is a dictionary
            if not isinstance(bot_persona, dict):

                bot_persona = {}
            
            # Format archetype-specific section
            archetype_section = self._format_archetype_section(bot_persona, archetype)
            
            formatted_template = self.assess_mode_template.format("""

content = content.replace(old_section, new_section)

# Write back
with open('scenario_generator.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed assess mode method")
