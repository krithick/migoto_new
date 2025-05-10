# core/analysis_report.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from models.user_models import UserDB, UserRole
from core.user import get_current_user, get_admin_user

# Create router
router = APIRouter(prefix="/reports", tags=["Analysis Reports"])

# Dependency to get database
async def get_database():
    from database import get_db
    return await get_db()

@router.get("/user/{user_id}", response_model=List[Dict[str, Any]])
async def get_user_analysis_reports(
    user_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get all analysis reports for a specific user
    
    - Regular users can only view their own reports
    - Admins can view reports for users they manage
    - Superadmins can view all reports
    """
    # Check permissions
    if current_user.role == UserRole.USER and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: you can only view your own reports"
        )
    elif current_user.role == UserRole.ADMIN:
        # Check if this user is managed by the admin
        admin_data = await db.users.find_one({"_id": str(current_user.id)})
        if admin_data and "managed_users" in admin_data:
            managed_users = admin_data["managed_users"]
            if str(user_id) not in managed_users and current_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: you can only view reports for users you manage"
                )
    
    # Get all analysis reports for the user
    reports = []
    cursor = db.analysis.find({"user_id": str(user_id)}).skip(skip).limit(limit).sort("timestamp", -1)
    
    async for report in cursor:
        # Get the associated session data to include scenario information
        session_id = report.get("session_id")
        if session_id:
            session = await db.sessions.find_one({"_id": session_id})
            if session:
                # Add scenario information to the report
                report["scenario_name"] = session.get("scenario_name", "Unknown Scenario")
                
                # Get avatar interaction data for more context
                avatar_interaction_id = session.get("avatar_interaction")
                if avatar_interaction_id:
                    avatar_interaction = await db.avatar_interactions.find_one({"_id": avatar_interaction_id})
                    if avatar_interaction:
                        report["avatar_interaction_data"] = {
                            "id": avatar_interaction_id,
                            "bot_role": avatar_interaction.get("bot_role", "Unknown"),
                            "mode": avatar_interaction.get("mode", "Unknown")
                        }
        
        # Format the report for response
        # Convert MongoDB _id to id
        report["id"] = str(report.pop("_id"))
        
        # Add the report to our results
        reports.append(report)
    
    return reports

@router.get("/me", response_model=List[Dict[str, Any]])
async def get_my_analysis_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get all analysis reports for the current user
    """
    return await get_user_analysis_reports(current_user.id, skip, limit, db, current_user)

@router.get("/{report_id}", response_model=Dict[str, Any])
async def get_analysis_report(
    report_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get a specific analysis report by ID
    """
    # Find the report
    report = await db.analysis.find_one({"_id": str(report_id)})
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Check permissions
    if current_user.role == UserRole.USER and report.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: you can only view your own reports"
        )
    elif current_user.role == UserRole.ADMIN:
        # Check if this user is managed by the admin
        admin_data = await db.users.find_one({"_id": str(current_user.id)})
        if admin_data and "managed_users" in admin_data:
            managed_users = admin_data["managed_users"]
            if report.get("user_id") not in managed_users and report.get("user_id") != str(current_user.id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: you can only view reports for users you manage"
                )
    
    # Get the associated session data to include scenario information
    session_id = report.get("session_id")
    if session_id:
        session = await db.sessions.find_one({"_id": session_id})
        if session:
            # Add scenario information to the report
            report["scenario_name"] = session.get("scenario_name", "Unknown Scenario")
            
            # Get avatar interaction data for more context
            avatar_interaction_id = session.get("avatar_interaction")
            if avatar_interaction_id:
                avatar_interaction = await db.avatar_interactions.find_one({"_id": avatar_interaction_id})
                if avatar_interaction:
                    report["avatar_interaction_data"] = {
                        "id": avatar_interaction_id,
                        "bot_role": avatar_interaction.get("bot_role", "Unknown"),
                        "mode": avatar_interaction.get("mode", "Unknown")
                    }
    
    # Format the report for response
    # Convert MongoDB _id to id
    report["id"] = str(report.pop("_id"))
    
    return report

@router.get("/session/{session_id}", response_model=Dict[str, Any])
async def get_report_by_session(
    session_id: str,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get analysis report for a specific chat session
    """
    # Find the report
    report = await db.analysis.find_one({"session_id": session_id})
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found for this session"
        )
    
    # Check permissions
    if current_user.role == UserRole.USER and report.get("user_id") != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: you can only view your own reports"
        )
    elif current_user.role == UserRole.ADMIN:
        # Check if this user is managed by the admin
        admin_data = await db.users.find_one({"_id": str(current_user.id)})
        if admin_data and "managed_users" in admin_data:
            managed_users = admin_data["managed_users"]
            if report.get("user_id") not in managed_users and report.get("user_id") != str(current_user.id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: you can only view reports for users you manage"
                )
    
    # Get the associated session data to include scenario information
    session = await db.sessions.find_one({"_id": session_id})
    if session:
        # Add scenario information to the report
        report["scenario_name"] = session.get("scenario_name", "Unknown Scenario")
        
        # Get avatar interaction data for more context
        avatar_interaction_id = session.get("avatar_interaction")
        if avatar_interaction_id:
            avatar_interaction = await db.avatar_interactions.find_one({"_id": avatar_interaction_id})
            if avatar_interaction:
                report["avatar_interaction_data"] = {
                    "id": avatar_interaction_id,
                    "bot_role": avatar_interaction.get("bot_role", "Unknown"),
                    "mode": avatar_interaction.get("mode", "Unknown")
                }
    
    # Format the report for response
    # Convert MongoDB _id to id
    report["id"] = str(report.pop("_id"))
    
    return report

@router.get("/stats/user/{user_id}", response_model=Dict[str, Any])
async def get_user_report_stats(
    user_id: UUID,
    db: Any = Depends(get_database),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get statistics for a user's analysis reports
    """
    # Check permissions
    if current_user.role == UserRole.USER and current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: you can only view your own report stats"
        )
    elif current_user.role == UserRole.ADMIN:
        # Check if this user is managed by the admin
        admin_data = await db.users.find_one({"_id": str(current_user.id)})
        if admin_data and "managed_users" in admin_data:
            managed_users = admin_data["managed_users"]
            if str(user_id) not in managed_users and current_user.id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied: you can only view report stats for users you manage"
                )
    
    # Get count of total reports
    total_reports = await db.analysis.count_documents({"user_id": str(user_id)})
    
    # Get average scores from reports
    pipeline = [
        {"$match": {"user_id": str(user_id)}},
        {"$group": {
            "_id": None,
            "avg_total_score": {"$avg": "$overall_evaluation.total_percentage_score"},
            "avg_role_score": {"$avg": "$role_fulfillment.score"},
            "avg_knowledge_score": {"$avg": "$knowledge_quality.overall_score"},
            "avg_communication_score": {"$avg": "$communication_quality.overall_score"},
            "avg_conversation_score": {"$avg": "$conversation_quality.overall_score"},
            "report_count": {"$sum": 1}
        }}
    ]
    
    stats_cursor = db.analysis.aggregate(pipeline)
    stats = await stats_cursor.to_list(length=1)
    
    if not stats:
        return {
            "user_id": str(user_id),
            "total_reports": 0,
            "average_scores": None
        }
    
    stats_result = stats[0]
    stats_result.pop("_id")
    
    # Get performance category distribution
    pipeline = [
        {"$match": {"user_id": str(user_id)}},
        {"$group": {
            "_id": "$overall_evaluation.performance_category",
            "count": {"$sum": 1}
        }},
        {"$sort": {"_id": 1}}
    ]
    
    categories_cursor = db.analysis.aggregate(pipeline)
    categories = await categories_cursor.to_list(length=None)
    
    performance_categories = {}
    for category in categories:
        performance_categories[category["_id"]] = category["count"]
    
    # Get recent improvement trend (last 5 reports)
    pipeline = [
        {"$match": {"user_id": str(user_id)}},
        {"$sort": {"timestamp": -1}},
        {"$limit": 5},
        {"$project": {
            "timestamp": 1,
            "total_score": "$overall_evaluation.total_percentage_score"
        }}
    ]
    
    trend_cursor = db.analysis.aggregate(pipeline)
    trend_data = await trend_cursor.to_list(length=5)
    
    # Format the response
    return {
        "user_id": str(user_id),
        "total_reports": total_reports,
        "average_scores": stats_result,
        "performance_categories": performance_categories,
        "recent_trend": trend_data
    }