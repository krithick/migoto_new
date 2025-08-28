from typing import Dict, Any
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException

async def fix_already_transferred_course(
    db: Any,
    course_id: UUID,
    boss_admin_id: UUID
) -> Dict[str, Any]:
    """Fix courses that were already transferred but missing avatar interactions/templates"""
    
    course = await db.courses.find_one({"_id": str(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    current_company_id = course["company_id"]
    current_admin_id = course["created_by"]
    
    # Get all modules and scenarios
    module_ids = course.get("modules", [])
    all_scenario_ids = []
    
    for module_id in module_ids:
        module = await db.modules.find_one({"_id": module_id})
        if module:
            all_scenario_ids.extend(module.get("scenarios", []))
    
    # Find orphaned avatar interactions
    avatar_interaction_ids = set()
    template_ids = set()
    
    for scenario_id in all_scenario_ids:
        scenario = await db.scenarios.find_one({"_id": scenario_id})
        if scenario:
            # Check each mode for avatar interactions
            for mode in ["learn_mode", "try_mode", "assess_mode"]:
                if mode in scenario and scenario[mode]:
                    ai_id = scenario[mode].get("avatar_interaction")
                    if ai_id:
                        avatar_interaction_ids.add(ai_id)
            
            # Check for template
            if scenario.get("template_id"):
                template_ids.add(scenario["template_id"])
    
    # Transfer orphaned avatar interactions
    ai_fixed = 0
    for ai_id in avatar_interaction_ids:
        ai = await db.avatar_interactions.find_one({"_id": str(ai_id)})
        if ai and ai.get("created_by") != current_admin_id:
            await db.avatar_interactions.update_one(
                {"_id": str(ai_id)},
                {"$set": {
                    "created_by": current_admin_id,
                    "updated_at": datetime.now()
                }}
            )
            ai_fixed += 1
    
    # Transfer orphaned templates and their knowledge bases
    templates_fixed = 0
    kb_fixed = 0
    docs_fixed = 0
    
    for template_id in template_ids:
        template = await db.templates.find_one({"id": template_id})
        if template and template.get("created_by") != current_admin_id:
            # Transfer template
            await db.templates.update_one(
                {"id": template_id},
                {"$set": {
                    "created_by": current_admin_id,
                    "company_id": current_company_id,
                    "updated_at": datetime.now()
                }}
            )
            templates_fixed += 1
            
            # Transfer associated knowledge base
            kb_id = template.get("knowledge_base_id")
            if kb_id:
                kb = await db.knowledge_bases.find_one({"_id": kb_id})
                if kb:
                    await db.knowledge_bases.update_one(
                        {"_id": kb_id},
                        {"$set": {
                            "company_id": current_company_id,
                            "last_updated": datetime.now()
                        }}
                    )
                    kb_fixed += 1
                    
                    # Transfer supporting documents
                    doc_result = await db.supporting_documents.update_many(
                        {"knowledge_base_id": kb_id},
                        {"$set": {
                            "company_id": current_company_id,
                            "updated_at": datetime.now()
                        }}
                    )
                    docs_fixed += doc_result.modified_count
    
    return {
        "success": True,
        "course_id": str(course_id),
        "avatar_interactions_fixed": ai_fixed,
        "templates_fixed": templates_fixed,
        "knowledge_bases_fixed": kb_fixed,
        "supporting_documents_fixed": docs_fixed,
        "fixed_at": datetime.now().isoformat()
    }

# Updated complete transfer function
async def transfer_course_complete(
    db: Any,
    course_id: UUID,
    to_company_id: UUID,
    new_admin_id: UUID,
    boss_admin_id: UUID
) -> Dict[str, Any]:
    """Transfer complete course + modules + scenarios + avatar interactions + templates"""
    
    course = await db.courses.find_one({"_id": str(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.get("is_archived", False):
        raise HTTPException(status_code=400, detail="Cannot transfer archived course")

    old_company_id = course["company_id"]

    # Get all modules and scenarios
    module_ids = course.get("modules", [])
    all_scenario_ids = []
    
    for module_id in module_ids:
        module = await db.modules.find_one({"_id": module_id})
        if module:
            all_scenario_ids.extend(module.get("scenarios", []))

    # NEW: Collect avatar interactions and templates
    avatar_interaction_ids = set()
    template_ids = set()
    knowledge_base_ids = set()
    
    for scenario_id in all_scenario_ids:
        scenario = await db.scenarios.find_one({"_id": scenario_id})
        if scenario:
            # Check each mode for avatar interactions
            for mode in ["learn_mode", "try_mode", "assess_mode"]:
                if mode in scenario and scenario[mode]:
                    ai_id = scenario[mode].get("avatar_interaction")
                    if ai_id:
                        avatar_interaction_ids.add(ai_id)
            
            # Check for template
            if scenario.get("template_id"):
                template_ids.add(scenario["template_id"])

    # NEW: Get knowledge bases from templates
    for template_id in template_ids:
        template = await db.templates.find_one({"id": template_id})
        if template and template.get("knowledge_base_id"):
            knowledge_base_ids.add(template["knowledge_base_id"])

    # Create transfer record
    transfer_record = {
        "from_company": str(old_company_id),
        "to_company": str(to_company_id),
        "transferred_by": str(boss_admin_id),
        "transferred_at": datetime.now().isoformat()
    }

    # 1. Update Course (existing)
    await db.courses.update_one(
        {"_id": str(course_id)},
        {
            "$set": {
                "company_id": str(to_company_id),
                "created_by": str(new_admin_id),
                "updated_at": datetime.now()
            },
            "$push": {"transfer_history": transfer_record}
        }
    )

    # 2. Update Modules (existing)
    if module_ids:
        await db.modules.update_many(
            {"_id": {"$in": module_ids}},
            {
                "$set": {
                    "company_id": str(to_company_id),
                    "created_by": str(new_admin_id),
                    "updated_at": datetime.now()
                },
                "$push": {"transfer_history": transfer_record}
            }
        )

    # 3. Update Scenarios (existing)
    if all_scenario_ids:
        await db.scenarios.update_many(
            {"_id": {"$in": all_scenario_ids}},
            {
                "$set": {
                    "company_id": str(to_company_id),
                    "created_by": str(new_admin_id),
                    "updated_at": datetime.now()
                },
                "$push": {"transfer_history": transfer_record}
            }
        )

    # 4. NEW: Update Avatar Interactions
    avatar_interactions_transferred = 0
    if avatar_interaction_ids:
        ai_result = await db.avatar_interactions.update_many(
            {"_id": {"$in": list(avatar_interaction_ids)}},
            {"$set": {
                "created_by": str(new_admin_id),
                "updated_at": datetime.now()
            }}
        )
        avatar_interactions_transferred = ai_result.modified_count

    # 5. NEW: Update Templates
    templates_transferred = 0
    if template_ids:
        template_result = await db.templates.update_many(
            {"id": {"$in": list(template_ids)}},
            {"$set": {
                "created_by": str(new_admin_id),
                "company_id": str(to_company_id),
                "updated_at": datetime.now()
            }}
        )
        templates_transferred = template_result.modified_count

    # 6. NEW: Update Knowledge Bases
    knowledge_bases_transferred = 0
    supporting_docs_transferred = 0
    if knowledge_base_ids:
        kb_result = await db.knowledge_bases.update_many(
            {"_id": {"$in": list(knowledge_base_ids)}},
            {"$set": {
                "company_id": str(to_company_id),
                "last_updated": datetime.now()
            }}
        )
        knowledge_bases_transferred = kb_result.modified_count
        
        # 7. NEW: Update Supporting Documents
        for kb_id in knowledge_base_ids:
            doc_result = await db.supporting_documents.update_many(
                {"knowledge_base_id": kb_id},
                {"$set": {
                    "company_id": str(to_company_id),
                    "updated_at": datetime.now()
                }}
            )
            supporting_docs_transferred += doc_result.modified_count

    # Archive existing assignments (existing logic)
    await db.user_course_assignments.update_many(
        {"course_id": str(course_id), "is_archived": False},
        {
            "$set": {
                "is_archived": True,
                "archived_at": datetime.now(),
                "archived_by": str(boss_admin_id),
                "archived_reason": "Course transferred to another company"
            }
        }
    )

    if module_ids:
        await db.user_module_assignments.update_many(
            {"module_id": {"$in": module_ids}, "is_archived": False},
            {
                "$set": {
                    "is_archived": True,
                    "archived_at": datetime.now(),
                    "archived_by": str(boss_admin_id),
                    "archived_reason": "Course transferred to another company"
                }
            }
        )

    if all_scenario_ids:
        await db.user_scenario_assignments.update_many(
            {"scenario_id": {"$in": all_scenario_ids}, "is_archived": False},
            {
                "$set": {
                    "is_archived": True,
                    "archived_at": datetime.now(),
                    "archived_by": str(boss_admin_id),
                    "archived_reason": "Course transferred to another company"
                }
            }
        )

    return {
        "success": True,
        "course_id": str(course_id),
        "from_company": str(old_company_id),
        "to_company": str(to_company_id),
        "new_owner": str(new_admin_id),
        "modules_transferred": len(module_ids),
        "scenarios_transferred": len(all_scenario_ids),
        "avatar_interactions_transferred": avatar_interactions_transferred,  # NEW
        "templates_transferred": templates_transferred,                      # NEW
        "knowledge_bases_transferred": knowledge_bases_transferred,          # NEW
        "supporting_documents_transferred": supporting_docs_transferred,     # NEW
        "transferred_at": datetime.now().isoformat()
    }