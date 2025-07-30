# core/dashboard.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta

from models.user_models import UserDB, UserRole
from core.user import get_current_user, get_admin_user

# Create router
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

# Database dependency
async def get_database():
    from database import get_db
    return await get_db()

# User Stats Endpoint
@router.get("/user-stats", response_model=Dict[str, int])
async def get_user_stats(
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Get user statistics:
    - Total users
    - Active users
    - Assigned users (to current admin)
    - Unassigned users (not assigned to any admin)
    
    Admin users see stats for users they manage.
    Superadmin users see stats for all users.
    """
    stats = {
        "total_users": 0,
        "active_users": 0,
        "assigned_users": 0,
        "unassigned_users": 0
    }
    
    # Set up base query for user filters
    base_query = {"role": UserRole.USER.value}
    
    # For admin, only show managed users
    if admin_user.role == UserRole.ADMIN:
        admin_data = await db.users.find_one({"_id": str(admin_user.id)})
        managed_users = admin_data.get("managed_users", []) if admin_data else []
        
        # Get total users managed by this admin
        stats["total_users"] = await db.users.count_documents({
            "role": UserRole.USER.value,
            "_id": {"$in": managed_users}
        })
        
        # Get active users managed by this admin
        stats["active_users"] = await db.users.count_documents({
            "role": UserRole.USER.value,
            "is_active": True,
            "_id": {"$in": managed_users}
        })
        
        # All managed users are "assigned" (to this admin)
        stats["assigned_users"] = stats["total_users"]
        stats["unassigned_users"] = 0
    else:
        # Superadmin sees all users
        stats["total_users"] = await db.users.count_documents({"role": UserRole.USER.value})
        stats["active_users"] = await db.users.count_documents({
            "role": UserRole.USER.value,
            "is_active": True
        })
        
        # Count users assigned to any admin
        all_admins = await db.users.find({"role": UserRole.ADMIN.value}).to_list(length=None)
        assigned_user_ids = set()
        
        for admin in all_admins:
            managed_users = admin.get("managed_users", [])
            assigned_user_ids.update(managed_users)
        
        stats["assigned_users"] = len(assigned_user_ids)
        stats["unassigned_users"] = stats["total_users"] - stats["assigned_users"]
    
    return stats

# Course Stats Endpoint
# @router.get("/course-stats", response_model=Dict[str, int])
# async def get_course_stats(
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)
# ):
#     """
#     Get course statistics:
#     - Total courses
#     - Created by current user
#     - Created by other admins
#     - Created by superadmin
#     - Pre-feeded courses
#     """
#     stats = {
#         "total_courses": 0,
#         "created_by_me": 0,
#         "created_by_other_admins": 0,
#         "created_by_superadmin": 0,
#         "pre_feeded": 0  # Assuming pre-feeded courses have a special flag or creator
#     }
    
#     # Get total courses
#     stats["total_courses"] = await db.courses.count_documents({})
    
#     # Get courses created by current user
#     stats["created_by_me"] = await db.courses.count_documents({
#         "created_by": str(admin_user.id)
#     })
    
#     # Get superadmin users
#     superadmins = await db.users.find({"role": UserRole.SUPERADMIN.value}).to_list(length=None)
#     superadmin_ids = [str(admin["_id"]) for admin in superadmins]
    
#     # Get courses created by superadmins
#     stats["created_by_superadmin"] = await db.courses.count_documents({
#         "created_by": {"$in": superadmin_ids}
#     })
    
#     # Get other admin users (excluding current user if they're an admin)
#     admin_query = {"role": UserRole.ADMIN.value}
#     if admin_user.role == UserRole.ADMIN:
#         admin_query["_id"] = {"$ne": str(admin_user.id)}
    
#     other_admins = await db.users.find(admin_query).to_list(length=None)
#     other_admin_ids = [str(admin["_id"]) for admin in other_admins]
    
#     # Get courses created by other admins
#     stats["created_by_other_admins"] = await db.courses.count_documents({
#         "created_by": {"$in": other_admin_ids}
#     })
    
#     # Determine pre-feeded courses (assuming system user or null creator)
#     # This may need adjustment based on how pre-feeded courses are marked
#     stats["pre_feeded"] = stats["total_courses"] - (
#         stats["created_by_me"] + 
#         stats["created_by_other_admins"] + 
#         stats["created_by_superadmin"]
#     )
    
#     return stats

# Updated Course Stats Endpoint
@router.get("/course-stats", response_model=Dict[str, Any])
async def get_course_stats(
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Get comprehensive course statistics with company hierarchy awareness:
    - Total courses accessible to admin
    - Courses by creation source (self, company, mother company)
    - Assignment statistics
    - Content visibility breakdown
    - Company context information
    """
    from models.company_models import CompanyType, CompanyDB
    from core.course import get_accessible_courses_for_user, get_assignable_courses_for_user
    
    stats = {
        # Basic counts
        "total_courses": 0,
        "assignable_courses": 0,
        "archived_courses": 0,
        
        # Creation source breakdown
        "created_by_me": 0,
        "created_by_my_company": 0,
        "created_by_mother_company": 0,
        "created_by_other_companies": 0,
        
        # Visibility breakdown
        "creator_only_courses": 0,
        "company_wide_courses": 0,
        
        # Assignment statistics
        "total_assignments": 0,
        "my_assignments": 0,  # Assignments made by current admin
        "internal_assignments": 0,  # Same company assignments
        "cross_company_assignments": 0,  # Mother -> Client assignments
        
        # Company context
        "company_info": {},
        "accessible_companies": [],
        
        # Content hierarchy stats
        "total_modules": 0,
        "total_scenarios": 0,
        "assigned_modules": 0,
        "assigned_scenarios": 0
    }
    
    # Get admin's company information
    admin_company = await db.companies.find_one({"_id": str(admin_user.company_id)})
    if admin_company:
        company_obj = CompanyDB(**admin_company)
        stats["company_info"] = {
            "id": str(company_obj.id),
            "name": company_obj.name,
            "type": company_obj.company_type,
            "status": company_obj.status
        }
    
    # Get accessible courses for this admin
    try:
        accessible_courses = await get_accessible_courses_for_user(db, admin_user)
        assignable_courses = await get_assignable_courses_for_user(db, admin_user)
        
        stats["total_courses"] = len(accessible_courses)
        stats["assignable_courses"] = len(assignable_courses)
        
        # Company type for hierarchy logic
        admin_company_type = admin_company.get("company_type") if admin_company else CompanyType.CLIENT
        
        # Get MOTHER company IDs for comparison
        mother_companies = []
        mother_cursor = db.companies.find({"company_type": CompanyType.MOTHER})
        async for company_doc in mother_cursor:
            mother_companies.append(company_doc["_id"])
            stats["accessible_companies"].append({
                "id": company_doc["_id"],
                "name": company_doc.get("name", "Unknown"),
                "type": "MOTHER"
            })
        
        # Add admin's own company to accessible companies if not already there
        if str(admin_user.company_id) not in [c["id"] for c in stats["accessible_companies"]]:
            stats["accessible_companies"].append({
                "id": str(admin_user.company_id),
                "name": admin_company.get("name", "Unknown") if admin_company else "Unknown",
                "type": admin_company_type
            })
        
        # Analyze each accessible course
        for course in accessible_courses:
            course_company_id = str(course.company_id)
            course_created_by = str(course.created_by)
            
            # Creation source analysis
            if course_created_by == str(admin_user.id):
                stats["created_by_me"] += 1
            elif course_company_id == str(admin_user.company_id):
                stats["created_by_my_company"] += 1
            elif course_company_id in mother_companies:
                stats["created_by_mother_company"] += 1
            else:
                stats["created_by_other_companies"] += 1
            
            # Visibility analysis
            if hasattr(course, 'visibility'):
                if course.visibility == "creator_only":
                    stats["creator_only_courses"] += 1
                elif course.visibility == "company_wide":
                    stats["company_wide_courses"] += 1
        
        # Get archived courses count
        archived_query = {"is_archived": True}
        if admin_user.role == UserRole.ADMIN:
            # Admin only sees their own archived courses
            archived_query["created_by"] = str(admin_user.id)
        elif admin_user.role == UserRole.SUPERADMIN:
            # Superadmin sees company's archived courses
            if admin_company_type == CompanyType.MOTHER:
                pass  # Can see all archived courses
            else:
                # Can see own company + MOTHER company archived courses
                accessible_companies = [str(admin_user.company_id)] + mother_companies
                archived_query["company_id"] = {"$in": accessible_companies}
        
        stats["archived_courses"] = await db.courses.count_documents(archived_query)
        
    except Exception as e:
        print(f"Error getting accessible courses: {e}")
        # Fallback to direct database queries
        stats["total_courses"] = await db.courses.count_documents({"is_archived": False})
        stats["created_by_me"] = await db.courses.count_documents({
            "created_by": str(admin_user.id),
            "is_archived": False
        })
    
    # Assignment statistics
    assignment_query = {}
    
    if admin_user.role == UserRole.ADMIN:
        # Admin sees assignments they made
        assignment_query["assigned_by"] = str(admin_user.id)
    elif admin_user.role == UserRole.SUPERADMIN:
        # Superadmin sees assignments in their company
        assignment_query["assigned_by_company"] = str(admin_user.company_id)
    elif admin_user.role == UserRole.BOSS_ADMIN:
        # Boss admin sees all assignments
        pass
    
    # Get assignment counts
    stats["total_assignments"] = await db.user_course_assignments.count_documents({
        **assignment_query,
        "is_archived": False
    })
    
    stats["my_assignments"] = await db.user_course_assignments.count_documents({
        "assigned_by": str(admin_user.id),
        "is_archived": False
    })
    
    stats["internal_assignments"] = await db.user_course_assignments.count_documents({
        **assignment_query,
        "assignment_context": "internal",
        "is_archived": False
    })
    
    stats["cross_company_assignments"] = await db.user_course_assignments.count_documents({
        **assignment_query,
        "assignment_context": "cross_company",
        "is_archived": False
    })
    
    # Content hierarchy statistics
    module_query = {}
    scenario_query = {}
    
    if admin_user.role == UserRole.ADMIN:
        # Admin sees content they created
        module_query["created_by"] = str(admin_user.id)
        scenario_query["created_by"] = str(admin_user.id)
    elif admin_user.role == UserRole.SUPERADMIN:
        # Superadmin sees company content + MOTHER content
        if admin_company_type == CompanyType.MOTHER:
            # MOTHER company admin sees all content
            pass
        else:
            accessible_companies = [str(admin_user.company_id)] + mother_companies
            module_query["company_id"] = {"$in": accessible_companies}
            scenario_query["company_id"] = {"$in": accessible_companies}
    
    # Add archived filter
    module_query["is_archived"] = False
    scenario_query["is_archived"] = False
    
    stats["total_modules"] = await db.modules.count_documents(module_query)
    stats["total_scenarios"] = await db.scenarios.count_documents(scenario_query)
    
    # Assignment counts for modules and scenarios
    module_assignment_query = {}
    scenario_assignment_query = {}
    
    if admin_user.role == UserRole.ADMIN:
        module_assignment_query["assigned_by"] = str(admin_user.id)
        scenario_assignment_query["assigned_by"] = str(admin_user.id)
    elif admin_user.role == UserRole.SUPERADMIN:
        module_assignment_query["assigned_by_company"] = str(admin_user.company_id)
        scenario_assignment_query["assigned_by_company"] = str(admin_user.company_id)
    
    # Add archived filter
    module_assignment_query["is_archived"] = False
    scenario_assignment_query["is_archived"] = False
    
    stats["assigned_modules"] = await db.user_module_assignments.count_documents(module_assignment_query)
    stats["assigned_scenarios"] = await db.user_scenario_assignments.count_documents(scenario_assignment_query)
    
    # Add completion rates
    if stats["total_assignments"] > 0:
        completed_assignments = await db.user_course_assignments.count_documents({
            **assignment_query,
            "is_archived": False,
            "completed": True
        })
        stats["completion_rate"] = round((completed_assignments / stats["total_assignments"]) * 100, 2)
    else:
        stats["completion_rate"] = 0
    
    # Add recent activity (assignments in last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.now() - timedelta(days=30)
    
    stats["recent_assignments"] = await db.user_course_assignments.count_documents({
        **assignment_query,
        "is_archived": False,
        "assigned_date": {"$gte": thirty_days_ago}
    })
    
    return stats
# User Analysis Reports Endpoint
# @router.get("/user-analysis", response_model=List[Dict[str, Any]])
# async def get_user_analysis_reports(
#     limit: int = Query(10, ge=1, le=100),
#     offset: int = Query(0, ge=0),
#     min_score: Optional[float] = Query(None, ge=0, le=100),
#     max_score: Optional[float] = Query(None, ge=0, le=100),
#     time_period: Optional[int] = Query(None, description="Time period in days"),
#     db: Any = Depends(get_database),
#     admin_user: UserDB = Depends(get_admin_user)
# ):
#     """
#     Get analysis reports for users assigned to the current admin.
#     Filter by score range and time period if specified.
#     """
#     # For admin users, get managed user IDs
#     user_ids = []
#     if admin_user.role == UserRole.ADMIN:
#         admin_data = await db.users.find_one({"_id": str(admin_user.id)})
#         if admin_data and "managed_users" in admin_data:
#             user_ids = admin_data["managed_users"]
    
#     # Build query
#     query = {}
    
#     # Filter by user IDs for admin
#     if admin_user.role == UserRole.ADMIN and user_ids:
#         query["user_id"] = {"$in": user_ids}
    
#     # Add score filters if specified
#     if min_score is not None or max_score is not None:
#         query["overall_evaluation.total_score"] = {}
#         if min_score is not None:
#             query["overall_evaluation.total_score"]["$gte"] = min_score
#         if max_score is not None:
#             query["overall_evaluation.total_score"]["$lte"] = max_score
    
#     # Add time period filter if specified
#     if time_period is not None:
#         start_date = datetime.now() - timedelta(days=time_period)
#         query["timestamp"] = {"$gte": start_date}
    
#     # Execute query with pagination
#     cursor = db.analysis.find(query).sort("overall_evaluation.total_score", -1).skip(offset).limit(limit)
#     reports = await cursor.to_list(length=limit)
    
#     # Process results to include user and scenario information
#     result = []
#     for report in reports:
#         # Convert MongoDB _id to id
#         report["id"] = str(report.pop("_id"))
        
#         # Get user information
#         user = await db.users.find_one({"_id": report["user_id"]})
#         user_info = {
#             "id": report["user_id"],
#             "name": f"{user['username']}" if user else "Unknown User",
#             "email": user.get("email", "No email") if user else "No email"
#         }
        
#         # Get session information
#         session = await db.sessions.find_one({"_id": report["session_id"]})
#         scenario_name = session.get("scenario_name", "Unknown Scenario") if session else "Unknown Scenario"
        
#         # Format data for response
#         result.append({
#             "id": report["id"],
#             "user": user_info,
#             "scenario_name": scenario_name,
#             "overall_score": report.get("overall_evaluation", {}).get("total_score", 0),
#             "performance_category": report.get("overall_evaluation", {}).get("user_performance_category", "Unknown"),
#             "timestamp": report.get("timestamp", datetime.now()),
#             # Include other relevant fields as needed
#         })
    
#     return result


# Fixed User Analysis Reports Endpoint
@router.get("/user-analysis", response_model=List[Dict[str, Any]])
async def get_user_analysis_reports(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    min_score: Optional[float] = Query(None, ge=0, le=100),
    max_score: Optional[float] = Query(None, ge=0, le=100),
    time_period: Optional[int] = Query(None, description="Time period in days"),
    user_id: Optional[UUID] = Query(None, description="Filter by specific user ID"),
    scenario_name: Optional[str] = Query(None, description="Filter by scenario name"),
    company_id: Optional[UUID] = Query(None, description="Filter by company (boss admin only)"),
    assignment_context: Optional[str] = Query(None, description="Filter by assignment context (internal/cross_company)"),
    performance_category: Optional[str] = Query(None, description="Filter by performance category"),
    db: Any = Depends(get_database),
    admin_user: UserDB = Depends(get_admin_user)
):
    """
    Get analysis reports with enhanced company data (backward compatible)
    """
    try:
        # Start with basic query - get all analysis reports first
        query = {}
        
        # Only add user filtering for non-boss admins
        if admin_user.role == UserRole.ADMIN:
            # Admin sees reports for users they manage
            admin_data = await db.users.find_one({"_id": str(admin_user.id)})
            if admin_data and "managed_users" in admin_data:
                managed_users = admin_data["managed_users"]
                if managed_users:
                    query["user_id"] = {"$in": managed_users}
                else:
                    return []  # No managed users
            else:
                return []  # No managed users data
                
        elif admin_user.role == UserRole.SUPERADMIN:
            # Superadmin sees all users in their company
            company_users = []
            users_cursor = db.users.find({
                "company_id": str(admin_user.company_id),
                "role": UserRole.USER
            })
            async for user in users_cursor:
                company_users.append(user["_id"])
            
            if company_users:
                query["user_id"] = {"$in": company_users}
            else:
                return []  # No users in company
        
        # BOSS_ADMIN sees all reports (no user filter)
        
        # Apply simple filters
        if user_id:
            query["user_id"] = str(user_id)
        
        if time_period is not None:
            start_date = datetime.now() - timedelta(days=time_period)
            query["timestamp"] = {"$gte": start_date}
        
        # Simple score filter
        if min_score is not None or max_score is not None:
            score_query = {}
            if min_score is not None:
                score_query["$gte"] = min_score
            if max_score is not None:
                score_query["$lte"] = max_score
            
            # Try both possible score fields
            query["$or"] = [
                {"overall_evaluation.total_score": score_query},
                {"overall_evaluation.total_percentage_score": score_query}
            ]
        
        print(f"Query: {query}")  # Debug log
        
        # Execute query with pagination
        cursor = db.analysis.find(query).sort("timestamp", -1).skip(offset).limit(limit)
        reports = await cursor.to_list(length=limit)
        
        print(f"Found {len(reports)} reports")  # Debug log
        
        if not reports:
            # Fallback: try to get ANY reports for debugging
            all_reports = await db.analysis.find({}).limit(5).to_list(length=5)
            print(f"Total reports in DB: {len(all_reports)}")
            if all_reports:
                print(f"Sample report structure: {all_reports[0].keys()}")
        
        # Process results with fallback handling
        result = []
        
        for report in reports:
            try:
                # Convert MongoDB _id to id
                report_id = str(report.pop("_id")) if "_id" in report else str(report.get("id", "unknown"))
                user_id = report.get("user_id", "unknown")
                session_id = report.get("session_id", "")
                
                # Get user information (with fallback)
                user = await db.users.find_one({"_id": user_id})
                user_info = {
                    "id": user_id,
                    "name": user.get("username", "Unknown User") if user else "Unknown User",
                    "email": user.get("email", "No email") if user else "No email"
                }
                
                # Get session info (with fallback)
                session = await db.sessions.find_one({"_id": session_id}) if session_id else None
                scenario_name = session.get("scenario_name", "Unknown Scenario") if session else "Unknown Scenario"
                
                # Extract score (try multiple fields)
                overall_eval = report.get("overall_evaluation", {})
                score = (overall_eval.get("total_score") or 
                        overall_eval.get("total_percentage_score") or 
                        (overall_eval.get("total_raw_score", 0) * 2.5) or 0)
                
                # Extract performance category
                performance_category = (overall_eval.get("user_performance_category") or 
                                      overall_eval.get("performance_category") or 
                                      "Unknown")
                
                # Apply scenario name filter if specified
                if scenario_name and scenario_name.lower() not in scenario_name.lower():
                    continue
                
                # Apply performance category filter if specified  
                if performance_category and performance_category.lower() not in performance_category.lower():
                    continue
                
                # ===== BACKWARD COMPATIBLE STRUCTURE =====
                analysis_result = {
                    "id": report_id,
                    "user": user_info,
                    "scenario_name": scenario_name,
                    "overall_score": score,
                    "performance_category": performance_category,
                    "timestamp": report.get("timestamp", datetime.now())
                }
                
                # ===== ENHANCED DATA (OPTIONAL) =====
                try:
                    # Add enhanced user info if user exists
                    if user:
                        user_company = await db.companies.find_one({"_id": user.get("company_id")})
                        analysis_result["user_enhanced"] = {
                            "role": user.get("role", "USER"),
                            "account_type": user.get("account_type", "REGULAR"),
                            "company": {
                                "id": user.get("company_id", ""),
                                "name": user_company.get("name", "Unknown") if user_company else "Unknown",
                                "type": user_company.get("company_type", "CLIENT") if user_company else "CLIENT"
                            }
                        }
                    
                    # Add performance details
                    strengths = (overall_eval.get("user_strengths") or 
                               overall_eval.get("strengths") or [])
                    improvement_areas = (overall_eval.get("user_improvement_areas") or 
                                       overall_eval.get("areas_for_improvement") or [])
                    
                    analysis_result.update({
                        "strengths": strengths[:3] if strengths else [],
                        "improvement_areas": improvement_areas[:3] if improvement_areas else [],
                        "session_id": session_id,
                        "detailed_scores": {
                            "domain_knowledge": report.get("user_domain_knowledge", {}).get("overall_score", 0),
                            "communication_clarity": report.get("user_communication_clarity", {}).get("overall_score", 0),
                            "engagement_quality": report.get("user_engagement_quality", {}).get("overall_score", 0),
                            "problem_solving": report.get("user_problem_solving", {}).get("overall_score", 0),
                            "learning_adaptation": report.get("user_learning_adaptation", {}).get("overall_score", 0)
                        }
                    })
                    
                except Exception as enhance_error:
                    print(f"Error adding enhanced data: {enhance_error}")
                    # Continue with basic data only
                
                result.append(analysis_result)
                
            except Exception as process_error:
                print(f"Error processing report: {process_error}")
                continue
        
        # Sort by score descending if we have scores
        if result and any(r.get("overall_score", 0) > 0 for r in result):
            result.sort(key=lambda x: x.get("overall_score", 0), reverse=True)
        
        return result
        
    except Exception as e:
        print(f"Error in get_user_analysis_reports: {e}")
        # Return empty array instead of error to prevent frontend crash
        return []