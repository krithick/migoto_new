from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import Dict, Any
import re
from scenario_generator import extract_text_from_docx, extract_text_from_pdf

router = APIRouter(prefix="/debug", tags=["Debug Extraction"])

@router.post("/raw-document-extraction")
async def debug_raw_extraction(file: UploadFile = File(...)):
    """
    Debug endpoint to show raw document extraction with section mapping
    """
    try:
        # Extract text from uploaded file
        content = await file.read()
        
        if file.filename.lower().endswith(('.doc', '.docx')):
            document_text = await extract_text_from_docx(content)
        elif file.filename.lower().endswith('.pdf'):
            document_text = await extract_text_from_pdf(content)
        else:
            document_text = content.decode('utf-8')
        
        if not document_text:
            raise HTTPException(400, "Could not extract text from document")
        
        # Parse sections from document
        sections = parse_document_sections(document_text)
        
        return {
            "filename": file.filename,
            "total_characters": len(document_text),
            "raw_text_preview": document_text[:1000] + "..." if len(document_text) > 1000 else document_text,
            "parsed_sections": sections,
            "section_mapping": {
                "section_1": "Project Basics (Company, Course, Module, Domain)",
                "section_2_1": "Target Skills (What learners should do)",
                "section_2_2": "Learner Info (Job roles, experience, challenges)",
                "section_3_1": "Learn Mode (AI Trainer Role, Topics, Style)",
                "section_3_2": "Try/Assess Mode (AI Colleague Role, Background, Concerns)",
                "section_3_3": "Conversation Examples",
                "section_4_2": "Common Situations & Responses (DOS)",
                "section_5_1": "Correction Preferences (Tone, Timing, Method)",
                "section_5_2": "Success Metrics",
                "section_7_3": "Common Mistakes (DONTS)"
            }
        }
        
    except Exception as e:
        raise HTTPException(500, f"Error processing document: {str(e)}")

def parse_document_sections(document_text: str) -> Dict[str, Any]:
    """Parse document into clear sections"""
    sections = {}
    
    # Section 1: Project Basics
    section_1 = extract_section_content(document_text, r"SECTION 1.*?PROJECT BASICS", r"SECTION 2")
    if section_1:
        sections["section_1_project_basics"] = {
            "raw_content": section_1,
            "company": extract_field(section_1, r"Company Name\s*([^\n\r]+)"),
            "course": extract_field(section_1, r"Course\s*([^\n\r]+)"),
            "module": extract_field(section_1, r"Module\s*([^\n\r]+)"),
            "scenario": extract_field(section_1, r"Scenario\s*([^\n\r]+)"),
            "domain": extract_field(section_1, r"Training Domain.*?☑\s*([^\s☐]+)")
        }
    
    # Section 2.1: Target Skills
    section_2_1 = extract_section_content(document_text, r"2\.1.*?What Should Learners", r"2\.2")
    if section_2_1:
        skills = extract_numbered_list(section_2_1, 5)
        sections["section_2_1_target_skills"] = {
            "raw_content": section_2_1,
            "skills": skills
        }
    
    # Section 2.2: Learner Info
    section_2_2 = extract_section_content(document_text, r"2\.2.*?Who Are Your Learners", r"SECTION 3")
    if section_2_2:
        sections["section_2_2_learner_info"] = {
            "raw_content": section_2_2,
            "job_roles": extract_field(section_2_2, r"Job Roles\s*([^\n\r]+)"),
            "experience": extract_field(section_2_2, r"Experience Level.*?☑\s*([^\s☐]+)"),
            "challenges": extract_field(section_2_2, r"Current Challenges\s*([^\n\r]+)")
        }
    
    # Section 3.1: Learn Mode
    section_3_1 = extract_section_content(document_text, r"3\.1.*?Learn Mode", r"3\.2")
    if section_3_1:
        sections["section_3_1_learn_mode"] = {
            "raw_content": section_3_1,
            "ai_trainer_role": extract_field(section_3_1, r"AI Trainer Role\s*([^\n\r]+)"),
            "training_topics": extract_field(section_3_1, r"Training Topics\s*([^\n\r]+)"),
            "teaching_style": extract_field(section_3_1, r"Teaching Style.*?☑\s*([^\s☐]+)")
        }
    
    # Section 3.2: Try/Assess Mode
    section_3_2 = extract_section_content(document_text, r"3\.2.*?Try/Assess Mode", r"3\.3")
    if section_3_2:
        sections["section_3_2_assess_mode"] = {
            "raw_content": section_3_2,
            "ai_colleague_role": extract_field(section_3_2, r"AI (?:Colleague|Stakeholder) Role\s*([^\n\r]+)"),
            "colleague_background": extract_field(section_3_2, r"(?:Colleague|Stakeholder) Background\s*([^\n\r]+)"),
            "typical_concerns": extract_field(section_3_2, r"Typical Concerns.*?\s*([^\n\r]+)"),
            "difficulty_level": extract_field(section_3_2, r"Difficulty Level.*?☑\s*([^\s☐]+)")
        }
    
    # Section 3.3: Conversation Examples
    section_3_3 = extract_section_content(document_text, r"3\.3.*?Real Conversation", r"SECTION 4")
    if section_3_3:
        sections["section_3_3_examples"] = {
            "raw_content": section_3_3,
            "conversation_topic": extract_field(section_3_3, r"Conversation Topic:\s*([^\n\r]+)"),
            "ai_colleague_line": extract_field(section_3_3, r"AI Colleague:\s*\"([^\"]+)\""),
            "correct_response": extract_field(section_3_3, r"Correct Learner Response:\s*\"([^\"]+)\""),
            "incorrect_response": extract_field(section_3_3, r"Incorrect Learner Response:\s*\"([^\"]+)\"")
        }
    
    # Section 4.2: Common Situations (DOS)
    section_4_2 = extract_section_content(document_text, r"4\.2.*?Common Situations", r"SECTION 5")
    if section_4_2:
        situations_table = extract_table_data(section_4_2)
        sections["section_4_2_common_situations"] = {
            "raw_content": section_4_2,
            "situations_table": situations_table
        }
    
    # Section 5.1: Correction Preferences
    section_5_1 = extract_section_content(document_text, r"5\.1.*?How Should AI Correct", r"5\.2")
    if section_5_1:
        sections["section_5_1_corrections"] = {
            "raw_content": section_5_1,
            "tone": extract_field(section_5_1, r"Tone.*?☑\s*([^\s☐]+)"),
            "timing": extract_field(section_5_1, r"Timing.*?☑\s*([^\s☐]+)"),
            "method": extract_field(section_5_1, r"Method.*?☑\s*([^\s☐]+)")
        }
    
    # Section 5.2: Success Metrics
    section_5_2 = extract_section_content(document_text, r"5\.2.*?Success Metrics", r"SECTION 6")
    if section_5_2:
        metrics_table = extract_table_data(section_5_2)
        sections["section_5_2_success_metrics"] = {
            "raw_content": section_5_2,
            "metrics_table": metrics_table
        }
    
    # Section 7.3: Common Mistakes (DONTS)
    section_7_3 = extract_section_content(document_text, r"7\.3.*?Common Mistakes", r"$")
    if section_7_3:
        mistakes_table = extract_table_data(section_7_3)
        sections["section_7_3_common_mistakes"] = {
            "raw_content": section_7_3,
            "mistakes_table": mistakes_table
        }
    
    return sections

def extract_section_content(text: str, start_pattern: str, end_pattern: str) -> str:
    """Extract content between two patterns"""
    try:
        start_match = re.search(start_pattern, text, re.IGNORECASE | re.DOTALL)
        if not start_match:
            return ""
        
        start_pos = start_match.end()
        
        if end_pattern == "$":
            return text[start_pos:].strip()
        
        end_match = re.search(end_pattern, text[start_pos:], re.IGNORECASE | re.DOTALL)
        if not end_match:
            return text[start_pos:].strip()
        
        end_pos = start_pos + end_match.start()
        return text[start_pos:end_pos].strip()
    except:
        return ""

def extract_field(text: str, pattern: str) -> str:
    """Extract a specific field using regex"""
    try:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        return match.group(1).strip() if match else ""
    except:
        return ""

def extract_numbered_list(text: str, max_items: int = 5) -> list:
    """Extract numbered list items"""
    items = []
    for i in range(1, max_items + 1):
        pattern = rf"{i}\s*([^\n\r]+)"
        match = re.search(pattern, text)
        if match:
            items.append(match.group(1).strip())
    return items

def extract_table_data(text: str) -> list:
    """Extract table-like data from text"""
    lines = text.split('\n')
    table_data = []
    
    for line in lines:
        line = line.strip()
        if line and not line.startswith(('Common Situation', 'Metric', 'Common Mistake')):
            # Split by tabs or multiple spaces
            parts = re.split(r'\t+|\s{3,}', line)
            if len(parts) >= 2:
                table_data.append({
                    "situation": parts[0].strip(),
                    "response": parts[1].strip() if len(parts) > 1 else "",
                    "source": parts[2].strip() if len(parts) > 2 else ""
                })
    
    return table_data