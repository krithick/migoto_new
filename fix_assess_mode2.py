import re

# Read file
with open('scenario_generator.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with bot_persona assignment
for i, line in enumerate(lines):
    if "bot_persona = template_data.get('persona_definitions', {}).get('assess_mode_ai_bot', {})" in line:
        # Insert new lines after the bot_persona assignment and before the if statement
        # Find the line with "# Ensure bot_persona is a dictionary"
        for j in range(i, min(i+10, len(lines))):
            if "# Ensure bot_persona is a dictionary" in lines[j]:
                # Insert before this line
                lines.insert(j, "            archetype_classification = template_data.get('archetype_classification', {})\n")
                lines.insert(j+1, "            archetype = str(archetype_classification.get('primary_archetype', '')).split('.')[-1]\n")
                break
        break

# Find the line with "formatted_template = self.assess_mode_template.format("
for i, line in enumerate(lines):
    if "formatted_template = self.assess_mode_template.format(" in line:
        # Insert before this line
        lines.insert(i, "            # Format archetype-specific section\n")
        lines.insert(i+1, "            archetype_section = self._format_archetype_section(bot_persona, archetype)\n")
        lines.insert(i+2, "\n")
        break

# Write back
with open('scenario_generator.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("Fixed assess mode method - added archetype handling")
