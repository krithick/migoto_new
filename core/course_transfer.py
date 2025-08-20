from typing import Dict, Any
from uuid import UUID
from datetime import datetime
from fastapi import HTTPException

async def transfer_course_complete(
db: Any,
course_id: UUID,
to_company_id: UUID,
new_admin_id: UUID,
boss_admin_id: UUID
) -> Dict[str, Any]:
    """Transfer complete course + modules + scenarios to new company/admin"""
    # Get course and validate
    course = await db.courses.find_one({"_id": str(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if course.get("is_archived", False):
        raise HTTPException(status_code=400, detail="Cannot transfer archived course")

    old_company_id = course["company_id"]

    # Get all modules in the course
    module_ids = course.get("modules", [])

    # Get all scenarios from all modules
    all_scenario_ids = []
    for module_id in module_ids:
        module = await db.modules.find_one({"_id": module_id})
        if module:
            scenario_ids = module.get("scenarios", [])
            all_scenario_ids.extend(scenario_ids)

    # Create transfer record
    transfer_record = {
    "from_company": str(old_company_id),
    "to_company": str(to_company_id),
    "transferred_by": str(boss_admin_id),
    "transferred_at": datetime.now().isoformat()
}

    # 1. Update Course
    await db.courses.update_one(
    {"_id": str(course_id)},
    {
        "$set": {
            "company_id": str(to_company_id),
            "created_by": str(new_admin_id),
            "updated_at": datetime.now()
        },
        "$push": {
            "transfer_history": transfer_record
        }
    }
)

    # 2. Update All Modules
    if module_ids:
        await db.modules.update_many(
        {"_id": {"$in": module_ids}},
        {
            "$set": {
                "company_id": str(to_company_id),
                "created_by": str(new_admin_id),
                "updated_at": datetime.now()
            },
            "$push": {
                "transfer_history": transfer_record
            }
        }
    )

    # 3. Update All Scenarios
    if all_scenario_ids:
        await db.scenarios.update_many(
        {"_id": {"$in": all_scenario_ids}},
        {
            "$set": {
                "company_id": str(to_company_id),
                "created_by": str(new_admin_id),
                "updated_at": datetime.now()
            },
            "$push": {
                "transfer_history": transfer_record
            }
        }
    )

    # 4. Archive existing course assignments
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

    # 5. Archive existing module assignments
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

    # 6. Archive existing scenario assignments
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
    "transferred_at": datetime.now().isoformat()
}