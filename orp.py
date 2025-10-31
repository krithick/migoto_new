# # import asyncio
# # import motor.motor_asyncio
# # import json
# # from datetime import datetime
# # from typing import Dict, List, Any, Optional

# # class CourseOwnershipAnalyzer:
# #     def __init__(self, mongodb_connection_string: str, database_name: str = "your_database_name"):
# #         """
# #         Initialize the analyzer with MongoDB connection
        
# #         Args:
# #             mongodb_connection_string: MongoDB connection string
# #             database_name: Name of your database
# #         """
# #         self.client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_connection_string)
# #         self.db = self.client[database_name]
    
# #     async def get_user_details(self, user_id: str) -> Dict[str, Any]:
# #         """Get user details by ID"""
# #         try:
# #             user = await self.db.users.find_one({"_id": user_id})
# #             if user:
# #                 return {
# #                     "id": user["_id"],
# #                     "username": user.get("username", "N/A"),
# #                     "email": user.get("email", "N/A"),
# #                     "role": user.get("role", "N/A"),
# #                     "company_id": user.get("company_id", "N/A")
# #                 }
# #             return {"id": user_id, "username": "USER_NOT_FOUND", "email": "N/A", "role": "N/A", "company_id": "N/A"}
# #         except Exception as e:
# #             return {"id": user_id, "username": f"ERROR: {str(e)}", "email": "N/A", "role": "N/A", "company_id": "N/A"}
    
# #     async def get_company_details(self, company_id: str) -> Dict[str, Any]:
# #         """Get company details by ID"""
# #         try:
# #             company = await self.db.companies.find_one({"_id": company_id})
# #             if company:
# #                 return {
# #                     "id": company["_id"],
# #                     "name": company.get("name", "N/A"),
# #                     "company_type": company.get("company_type", "N/A")
# #                 }
# #             return {"id": company_id, "name": "COMPANY_NOT_FOUND", "company_type": "N/A"}
# #         except Exception as e:
# #             return {"id": company_id, "name": f"ERROR: {str(e)}", "company_type": "N/A"}
    
# #     async def analyze_course_ownership(self, course_id: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
# #         """
# #         Analyze course ownership hierarchy
        
# #         Args:
# #             course_id: Specific course ID to analyze (if None, analyzes all courses)
# #             limit: Maximum number of courses to analyze (ignored if course_id is provided)
        
# #         Returns:
# #             Dictionary with complete ownership analysis
# #         """
# #         result = {
# #             "analysis_timestamp": datetime.now().isoformat(),
# #             "courses": [],
# #             "summary": {
# #                 "total_courses_analyzed": 0,
# #                 "courses_with_orphaned_content": 0,
# #                 "total_orphaned_avatar_interactions": 0,
# #                 "total_orphaned_templates": 0
# #             }
# #         }
        
# #         # Build query
# #         query = {}
# #         if course_id:
# #             query["_id"] = course_id
# #             limit = 1
        
# #         # Get courses
# #         courses_cursor = self.db.courses.find(query).limit(limit)
# #         courses = await courses_cursor.to_list(length=limit)
        
# #         result["summary"]["total_courses_analyzed"] = len(courses)
        
# #         for course in courses:
# #             course_analysis = await self._analyze_single_course(course)
# #             result["courses"].append(course_analysis)
            
# #             # Update summary
# #             if course_analysis["has_orphaned_content"]:
# #                 result["summary"]["courses_with_orphaned_content"] += 1
# #             result["summary"]["total_orphaned_avatar_interactions"] += len(course_analysis["orphaned_avatar_interactions"])
# #             result["summary"]["total_orphaned_templates"] += len(course_analysis["orphaned_templates"])
        
# #         return result
    
# #     async def _analyze_single_course(self, course: Dict[str, Any]) -> Dict[str, Any]:
# #         """Analyze a single course for ownership issues"""
# #         course_id = course["_id"]
# #         course_created_by = course.get("created_by")
# #         course_company_id = course.get("company_id")
        
# #         # Get course creator details
# #         course_creator = await self.get_user_details(course_created_by) if course_created_by else None
# #         course_company = await self.get_company_details(course_company_id) if course_company_id else None
        
# #         course_analysis = {
# #             "course": {
# #                 "id": course_id,
# #                 "title": course.get("title", "N/A"),
# #                 "description": course.get("description", "N/A"),
# #                 "created_by": course_created_by,
# #                 "company_id": course_company_id,
# #                 "created_at": course.get("created_at"),
# #                 "is_archived": course.get("is_archived", False),
# #                 "creator_details": course_creator,
# #                 "company_details": course_company
# #             },
# #             "modules": [],
# #             "orphaned_avatar_interactions": [],
# #             "orphaned_templates": [],
# #             "has_orphaned_content": False
# #         }
        
# #         # Get modules
# #         module_ids = course.get("modules", [])
# #         for module_id in module_ids:
# #             module = await self.db.modules.find_one({"_id": module_id})
# #             if not module:
# #                 continue
            
# #             module_created_by = module.get("created_by")
# #             module_creator = await self.get_user_details(module_created_by) if module_created_by else None
            
# #             module_analysis = {
# #                 "id": module_id,
# #                 "title": module.get("title", "N/A"),
# #                 "created_by": module_created_by,
# #                 "company_id": module.get("company_id"),
# #                 "is_archived": module.get("is_archived", False),
# #                 "creator_details": module_creator,
# #                 "scenarios": [],
# #                 "ownership_matches_course": module_created_by == course_created_by
# #             }
            
# #             # Get scenarios
# #             scenario_ids = module.get("scenarios", [])
# #             for scenario_id in scenario_ids:
# #                 scenario = await self.db.scenarios.find_one({"_id": scenario_id})
# #                 if not scenario:
# #                     continue
                
# #                 scenario_created_by = scenario.get("created_by")
# #                 scenario_creator = await self.get_user_details(scenario_created_by) if scenario_created_by else None
                
# #                 scenario_analysis = {
# #                     "id": scenario_id,
# #                     "title": scenario.get("title", "N/A"),
# #                     "created_by": scenario_created_by,
# #                     "company_id": scenario.get("company_id"),
# #                     "template_id": scenario.get("template_id"),
# #                     "is_archived": scenario.get("is_archived", False),
# #                     "creator_details": scenario_creator,
# #                     "ownership_matches_course": scenario_created_by == course_created_by,
# #                     "avatar_interactions": [],
# #                     "template_details": None
# #                 }
                
# #                 # Check each mode for avatar interactions
# #                 for mode in ["learn_mode", "try_mode", "assess_mode"]:
# #                     mode_data = scenario.get(mode)
# #                     if mode_data and isinstance(mode_data, dict):
# #                         ai_id = mode_data.get("avatar_interaction")
# #                         if ai_id:
# #                             # Get avatar interaction details
# #                             avatar_interaction = await self.db.avatar_interactions.find_one({"_id": ai_id})
# #                             if avatar_interaction:
# #                                 ai_created_by = avatar_interaction.get("created_by")
# #                                 ai_creator = await self.get_user_details(ai_created_by) if ai_created_by else None
                                
# #                                 ai_analysis = {
# #                                     "id": ai_id,
# #                                     "mode": mode,
# #                                     "created_by": ai_created_by,
# #                                     "creator_details": ai_creator,
# #                                     "ownership_matches_course": ai_created_by == course_created_by,
# #                                     "bot_role": avatar_interaction.get("bot_role", "N/A"),
# #                                     "system_prompt_preview": (avatar_interaction.get("system_prompt", "")[:100] + "...") if avatar_interaction.get("system_prompt") else "N/A"
# #                                 }
                                
# #                                 scenario_analysis["avatar_interactions"].append(ai_analysis)
                                
# #                                 # Check if orphaned
# #                                 if ai_created_by != course_created_by:
# #                                     course_analysis["orphaned_avatar_interactions"].append({
# #                                         "avatar_interaction_id": ai_id,
# #                                         "scenario_title": scenario.get("title", "N/A"),
# #                                         "module_title": module.get("title", "N/A"),
# #                                         "mode": mode,
# #                                         "current_owner": ai_created_by,
# #                                         "current_owner_details": ai_creator,
# #                                         "should_be_owner": course_created_by,
# #                                         "should_be_owner_details": course_creator
# #                                     })
                
# #                 # Check template
# #                 template_id = scenario.get("template_id")
# #                 if template_id:
# #                     template = await self.db.templates.find_one({"id": template_id})
# #                     if template:
# #                         template_created_by = template.get("created_by")
# #                         template_creator = await self.get_user_details(template_created_by) if template_created_by else None
                        
# #                         scenario_analysis["template_details"] = {
# #                             "id": template_id,
# #                             "name": template.get("name", "N/A"),
# #                             "created_by": template_created_by,
# #                             "creator_details": template_creator,
# #                             "ownership_matches_course": template_created_by == course_created_by,
# #                             "knowledge_base_id": template.get("knowledge_base_id"),
# #                             "company_id": template.get("company_id")
# #                         }
                        
# #                         # Check if orphaned
# #                         if template_created_by != course_created_by:
# #                             course_analysis["orphaned_templates"].append({
# #                                 "template_id": template_id,
# #                                 "template_name": template.get("name", "N/A"),
# #                                 "scenario_title": scenario.get("title", "N/A"),
# #                                 "module_title": module.get("title", "N/A"),
# #                                 "current_owner": template_created_by,
# #                                 "current_owner_details": template_creator,
# #                                 "should_be_owner": course_created_by,
# #                                 "should_be_owner_details": course_creator,
# #                                 "knowledge_base_id": template.get("knowledge_base_id")
# #                             })
                
# #                 module_analysis["scenarios"].append(scenario_analysis)
            
# #             course_analysis["modules"].append(module_analysis)
        
# #         # Set orphaned flag
# #         course_analysis["has_orphaned_content"] = (
# #             len(course_analysis["orphaned_avatar_interactions"]) > 0 or
# #             len(course_analysis["orphaned_templates"]) > 0
# #         )
        
# #         return course_analysis
    
# #     async def get_orphaned_summary(self) -> Dict[str, Any]:
# #         """Get a quick summary of all courses with orphaned content"""
# #         all_courses = await self.db.courses.find({}).to_list(length=1000)
        
# #         orphaned_courses = []
# #         for course in all_courses:
# #             analysis = await self._analyze_single_course(course)
# #             if analysis["has_orphaned_content"]:
# #                 orphaned_courses.append({
# #                     "course_id": course["_id"],
# #                     "course_title": course.get("title", "N/A"),
# #                     "course_creator": analysis["course"]["creator_details"],
# #                     "orphaned_avatar_interactions_count": len(analysis["orphaned_avatar_interactions"]),
# #                     "orphaned_templates_count": len(analysis["orphaned_templates"]),
# #                     "orphaned_avatar_interactions": analysis["orphaned_avatar_interactions"],
# #                     "orphaned_templates": analysis["orphaned_templates"]
# #                 })
        
# #         return {
# #             "total_courses_checked": len(all_courses),
# #             "courses_with_orphaned_content": len(orphaned_courses),
# #             "orphaned_courses": orphaned_courses
# #         }
    
# #     async def close(self):
# #         """Close the database connection"""
# #         self.client.close()

# # # Example usage
# # async def main():
# #     MONGODB_CONNECTION_STRING = "mongodb+srv://novacxr:p6eNTq70xGXKAZ5A@unity-backend.frhzuaq.mongodb.net/"
# #     DATABASE_NAME = "Migoto_Fresh"
    
# #     analyzer = CourseOwnershipAnalyzer(MONGODB_CONNECTION_STRING, DATABASE_NAME)
    
# #     try:
# #         # Option 1: Analyze a specific course
# #         # result = await analyzer.analyze_course_ownership(course_id="your_course_id_here")
        
# #         # Option 2: Analyze first 5 courses
# #         # result = await analyzer.analyze_course_ownership(limit=5)
        
# #         # Option 3: Get quick orphaned summary
# #         result = await analyzer.get_orphaned_summary()
        
# #         # Pretty print the result
# #         print(json.dumps(result, indent=2, default=str))
        
# #         # Optional: Save to file
# #         with open("course_ownership_analysis.json", "w") as f:
# #             json.dump(result, f, indent=2, default=str)
        
# #     except Exception as e:
# #         print(f"Error: {e}")
# #     finally:
# #         await analyzer.close()

# # if __name__ == "__main__":
# #     asyncio.run(main())
# """
# Orphaned Content Fixer CLI
# A command-line tool to fix orphaned avatar interactions and templates in courses.
# """

# import asyncio
# import motor.motor_asyncio
# import json
# import argparse
# import sys
# from datetime import datetime
# from typing import Dict, List, Any, Optional
# from rich.console import Console
# from rich.table import Table
# from rich.progress import Progress, SpinnerColumn, TextColumn
# from rich.prompt import Confirm, Prompt
# from rich import print as rprint
# from rich.panel import Panel

# console = Console()

# class OrphanedContentFixer:
#     def __init__(self, mongodb_connection_string: str, database_name: str):
#         """Initialize the fixer with MongoDB connection"""
#         self.client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_connection_string)
#         self.db = self.client[database_name]
#         self.fixed_count = {
#             "avatar_interactions": 0,
#             "templates": 0,
#             "knowledge_bases": 0,
#             "supporting_documents": 0
#         }
    
#     async def get_user_details(self, user_id: str) -> Dict[str, Any]:
#         """Get user details by ID"""
#         try:
#             user = await self.db.users.find_one({"_id": user_id})
#             if user:
#                 return {
#                     "id": user["_id"],
#                     "username": user.get("username", "N/A"),
#                     "email": user.get("email", "N/A"),
#                     "role": user.get("role", "N/A"),
#                     "company_id": user.get("company_id", "N/A")
#                 }
#             return None
#         except Exception:
#             return None
    
#     async def find_orphaned_content(self, course_id: Optional[str] = None) -> Dict[str, Any]:
#         """Find all orphaned content grouped by should_be_owner"""
#         console.print("🔍 [bold blue]Scanning for orphaned content...[/bold blue]")
        
#         # Build query
#         query = {}
#         if course_id:
#             query["_id"] = course_id
        
#         courses = await self.db.courses.find(query).to_list(length=1000)
        
#         # Group orphaned content by should_be_owner (course creator)
#         orphaned_by_owner = {}
        
#         with Progress(
#             SpinnerColumn(),
#             TextColumn("[progress.description]{task.description}"),
#             console=console
#         ) as progress:
#             task = progress.add_task("Analyzing courses...", total=len(courses))
            
#             for course in courses:
#                 course_id = course["_id"]
#                 course_created_by = course.get("created_by")
                
#                 if not course_created_by:
#                     progress.advance(task)
#                     continue
                
#                 # Initialize owner group if not exists
#                 if course_created_by not in orphaned_by_owner:
#                     user_details = await self.get_user_details(course_created_by)
#                     orphaned_by_owner[course_created_by] = {
#                         "owner_details": user_details,
#                         "avatar_interactions": [],
#                         "templates": [],
#                         "courses_affected": set()
#                     }
                
#                 # Check modules and scenarios
#                 module_ids = course.get("modules", [])
#                 for module_id in module_ids:
#                     module = await self.db.modules.find_one({"_id": module_id})
#                     if not module:
#                         continue
                    
#                     scenario_ids = module.get("scenarios", [])
#                     for scenario_id in scenario_ids:
#                         scenario = await self.db.scenarios.find_one({"_id": scenario_id})
#                         if not scenario:
#                             continue
                        
#                         # Check avatar interactions
#                         for mode in ["learn_mode", "try_mode", "assess_mode"]:
#                             mode_data = scenario.get(mode)
#                             if mode_data and isinstance(mode_data, dict):
#                                 ai_id = mode_data.get("avatar_interaction")
#                                 if ai_id:
#                                     ai = await self.db.avatar_interactions.find_one({"_id": ai_id})
#                                     if ai and ai.get("created_by") != course_created_by:
#                                         current_owner = await self.get_user_details(ai.get("created_by"))
#                                         orphaned_by_owner[course_created_by]["avatar_interactions"].append({
#                                             "id": ai_id,
#                                             "scenario_title": scenario.get("title", "N/A"),
#                                             "module_title": module.get("title", "N/A"),
#                                             "course_title": course.get("title", "N/A"),
#                                             "mode": mode,
#                                             "current_owner": ai.get("created_by"),
#                                             "current_owner_details": current_owner,
#                                             "bot_role": ai.get("bot_role", "N/A")
#                                         })
#                                         orphaned_by_owner[course_created_by]["courses_affected"].add(course_id)
                        
#                         # Check templates
#                         template_id = scenario.get("template_id")
#                         if template_id:
#                             template = await self.db.templates.find_one({"id": template_id})
#                             if template and template.get("created_by") != course_created_by:
#                                 current_owner = await self.get_user_details(template.get("created_by"))
#                                 orphaned_by_owner[course_created_by]["templates"].append({
#                                     "id": template_id,
#                                     "name": template.get("name", "N/A"),
#                                     "scenario_title": scenario.get("title", "N/A"),
#                                     "module_title": module.get("title", "N/A"),
#                                     "course_title": course.get("title", "N/A"),
#                                     "current_owner": template.get("created_by"),
#                                     "current_owner_details": current_owner,
#                                     "knowledge_base_id": template.get("knowledge_base_id")
#                                 })
#                                 orphaned_by_owner[course_created_by]["courses_affected"].add(course_id)
                
#                 progress.advance(task)
        
#         # Convert sets to lists for JSON serialization
#         for owner_id in orphaned_by_owner:
#             orphaned_by_owner[owner_id]["courses_affected"] = list(orphaned_by_owner[owner_id]["courses_affected"])
        
#         # Filter out owners with no orphaned content
#         orphaned_by_owner = {k: v for k, v in orphaned_by_owner.items() 
#                            if v["avatar_interactions"] or v["templates"]}
        
#         return orphaned_by_owner
    
#     async def fix_avatar_interactions(self, avatar_interaction_ids: List[str], new_owner_id: str) -> int:
#         """Fix ownership of avatar interactions"""
#         if not avatar_interaction_ids:
#             return 0
        
#         result = await self.db.avatar_interactions.update_many(
#             {"_id": {"$in": avatar_interaction_ids}},
#             {
#                 "$set": {
#                     "created_by": new_owner_id,
#                     "updated_at": datetime.now()
#                 }
#             }
#         )
        
#         return result.modified_count
    
#     async def fix_templates_and_knowledge_bases(self, template_data: List[Dict], new_owner_id: str) -> Dict[str, int]:
#         """Fix ownership of templates and their knowledge bases"""
#         if not template_data:
#             return {"templates": 0, "knowledge_bases": 0, "supporting_documents": 0}
        
#         template_ids = [t["id"] for t in template_data]
#         knowledge_base_ids = [t["knowledge_base_id"] for t in template_data if t.get("knowledge_base_id")]
        
#         # Fix templates
#         template_result = await self.db.templates.update_many(
#             {"id": {"$in": template_ids}},
#             {
#                 "$set": {
#                     "created_by": new_owner_id,
#                     "updated_at": datetime.now()
#                 }
#             }
#         )
        
#         # Fix knowledge bases
#         kb_result = None
#         docs_count = 0
#         if knowledge_base_ids:
#             kb_result = await self.db.knowledge_bases.update_many(
#                 {"_id": {"$in": knowledge_base_ids}},
#                 {
#                     "$set": {
#                         "last_updated": datetime.now()
#                     }
#                 }
#             )
            
#             # Fix supporting documents
#             for kb_id in knowledge_base_ids:
#                 doc_result = await self.db.supporting_documents.update_many(
#                     {"knowledge_base_id": kb_id},
#                     {
#                         "$set": {
#                             "updated_at": datetime.now()
#                         }
#                     }
#                 )
#                 docs_count += doc_result.modified_count
        
#         return {
#             "templates": template_result.modified_count,
#             "knowledge_bases": kb_result.modified_count if kb_result else 0,
#             "supporting_documents": docs_count
#         }
    
#     async def fix_orphaned_content_for_owner(self, owner_id: str, orphaned_data: Dict[str, Any], dry_run: bool = False) -> Dict[str, int]:
#         """Fix all orphaned content for a specific owner"""
        
#         if dry_run:
#             console.print(f"[yellow]🔍 DRY RUN: Would fix content for owner {owner_id}[/yellow]")
#             return {
#                 "avatar_interactions": len(orphaned_data.get("avatar_interactions", [])),
#                 "templates": len(orphaned_data.get("templates", [])),
#                 "knowledge_bases": len(set(t.get("knowledge_base_id") for t in orphaned_data.get("templates", []) if t.get("knowledge_base_id"))),
#                 "supporting_documents": 0  # Can't easily count without actually querying
#             }
        
#         results = {"avatar_interactions": 0, "templates": 0, "knowledge_bases": 0, "supporting_documents": 0}
        
#         # Fix avatar interactions
#         ai_ids = [ai["id"] for ai in orphaned_data.get("avatar_interactions", [])]
#         if ai_ids:
#             ai_count = await self.fix_avatar_interactions(ai_ids, owner_id)
#             results["avatar_interactions"] = ai_count
#             console.print(f"✅ Fixed {ai_count} avatar interactions")
        
#         # Fix templates and knowledge bases
#         templates = orphaned_data.get("templates", [])
#         if templates:
#             template_results = await self.fix_templates_and_knowledge_bases(templates, owner_id)
#             results.update(template_results)
#             console.print(f"✅ Fixed {template_results['templates']} templates, {template_results['knowledge_bases']} knowledge bases, {template_results['supporting_documents']} documents")
        
#         return results
    
#     def display_orphaned_summary(self, orphaned_by_owner: Dict[str, Any]):
#         """Display summary of orphaned content"""
#         if not orphaned_by_owner:
#             console.print("🎉 [bold green]No orphaned content found![/bold green]")
#             return
        
#         # Summary table
#         summary_table = Table(title="📊 Orphaned Content Summary")
#         summary_table.add_column("Owner", style="cyan")
#         summary_table.add_column("Username", style="green") 
#         summary_table.add_column("Email", style="blue")
#         summary_table.add_column("Avatar Interactions", justify="right", style="red")
#         summary_table.add_column("Templates", justify="right", style="yellow")
#         summary_table.add_column("Courses Affected", justify="right", style="magenta")
        
#         total_ai = 0
#         total_templates = 0
        
#         for owner_id, data in orphaned_by_owner.items():
#             owner_details = data.get("owner_details") or {}
#             ai_count = len(data.get("avatar_interactions", []))
#             template_count = len(data.get("templates", []))
#             courses_count = len(data.get("courses_affected", []))
            
#             total_ai += ai_count
#             total_templates += template_count
            
#             summary_table.add_row(
#                 owner_id[:12] + "..." if len(owner_id) > 15 else owner_id,
#                 owner_details.get("username", "N/A"),
#                 owner_details.get("email", "N/A"),
#                 str(ai_count),
#                 str(template_count),
#                 str(courses_count)
#             )
        
#         console.print(summary_table)
#         console.print(f"\n📈 [bold]Total: {total_ai} orphaned avatar interactions, {total_templates} orphaned templates across {len(orphaned_by_owner)} owners[/bold]")
    
#     def display_detailed_orphaned_content(self, owner_id: str, orphaned_data: Dict[str, Any]):
#         """Display detailed orphaned content for a specific owner"""
#         owner_details = orphaned_data.get("owner_details") or {}
        
#         console.print(Panel(
#             f"Owner: {owner_details.get('username', 'N/A')} ({owner_details.get('email', 'N/A')})\n"
#             f"Role: {owner_details.get('role', 'N/A')}\n"
#             f"Owner ID: {owner_id}",
#             title=f"🎯 Orphaned Content for {owner_details.get('username', owner_id[:12])}",
#             expand=False
#         ))
        
#         # Avatar Interactions Table
#         ai_data = orphaned_data.get("avatar_interactions", [])
#         if ai_data:
#             ai_table = Table(title=f"🤖 Avatar Interactions ({len(ai_data)})")
#             ai_table.add_column("ID", style="cyan", max_width=15)
#             ai_table.add_column("Course", style="green", max_width=20)
#             ai_table.add_column("Module", style="blue", max_width=20)
#             ai_table.add_column("Scenario", style="yellow", max_width=20)
#             ai_table.add_column("Mode", style="magenta")
#             ai_table.add_column("Bot Role", style="white")
#             ai_table.add_column("Current Owner", style="red", max_width=15)
            
#             for ai in ai_data:
#                 current_owner = ai.get("current_owner_details") or {}
#                 ai_table.add_row(
#                     ai["id"][:12] + "..." if len(ai["id"]) > 15 else ai["id"],
#                     ai["course_title"][:17] + "..." if len(ai["course_title"]) > 20 else ai["course_title"],
#                     ai["module_title"][:17] + "..." if len(ai["module_title"]) > 20 else ai["module_title"],
#                     ai["scenario_title"][:17] + "..." if len(ai["scenario_title"]) > 20 else ai["scenario_title"],
#                     ai["mode"].replace("_mode", ""),
#                     ai["bot_role"][:15] + "..." if len(ai["bot_role"]) > 18 else ai["bot_role"],
#                     current_owner.get("username", ai["current_owner"][:12])
#                 )
            
#             console.print(ai_table)
        
#         # Templates Table
#         template_data = orphaned_data.get("templates", [])
#         if template_data:
#             template_table = Table(title=f"📋 Templates ({len(template_data)})")
#             template_table.add_column("ID", style="cyan", max_width=15)
#             template_table.add_column("Name", style="green", max_width=25)
#             template_table.add_column("Course", style="blue", max_width=20)
#             template_table.add_column("Module", style="yellow", max_width=20)
#             template_table.add_column("Scenario", style="magenta", max_width=20)
#             template_table.add_column("Current Owner", style="red", max_width=15)
#             template_table.add_column("KB ID", style="white", max_width=15)
            
#             for template in template_data:
#                 current_owner = template.get("current_owner_details") or {}
#                 kb_id = template.get("knowledge_base_id", "N/A")
#                 template_table.add_row(
#                     template["id"][:12] + "..." if len(template["id"]) > 15 else template["id"],
#                     template["name"][:22] + "..." if len(template["name"]) > 25 else template["name"],
#                     template["course_title"][:17] + "..." if len(template["course_title"]) > 20 else template["course_title"],
#                     template["module_title"][:17] + "..." if len(template["module_title"]) > 20 else template["module_title"],
#                     template["scenario_title"][:17] + "..." if len(template["scenario_title"]) > 20 else template["scenario_title"],
#                     current_owner.get("username", template["current_owner"][:12]),
#                     kb_id[:12] + "..." if isinstance(kb_id, str) and len(kb_id) > 15 else str(kb_id)
#                 )
            
#             console.print(template_table)
    
#     async def close(self):
#         """Close the database connection"""
#         self.client.close()

# async def main():
#     parser = argparse.ArgumentParser(description="Fix orphaned avatar interactions and templates in courses")
#     parser.add_argument("--connection", "-c", required=True, help="MongoDB connection string")
#     parser.add_argument("--database", "-d", required=True, help="Database name")
#     parser.add_argument("--course-id", help="Specific course ID to analyze")
#     parser.add_argument("--owner-id", help="Fix content for specific owner ID only")
#     parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed without making changes")
#     parser.add_argument("--export-json", help="Export findings to JSON file")
#     parser.add_argument("--batch-fix", action="store_true", help="Fix all orphaned content without individual confirmation")
    
#     args = parser.parse_args()
    
#     console.print("🔧 [bold blue]Orphaned Content Fixer CLI[/bold blue]")
#     console.print(f"Database: {args.database}")
    
#     if args.dry_run:
#         console.print("[yellow]⚠️  DRY RUN MODE: No changes will be made[/yellow]")
    
#     fixer = OrphanedContentFixer(args.connection, args.database)
    
#     try:
#         # Find orphaned content
#         orphaned_by_owner = await fixer.find_orphaned_content(args.course_id)
        
#         if not orphaned_by_owner:
#             console.print("🎉 [bold green]No orphaned content found![/bold green]")
#             return
        
#         # Display summary
#         fixer.display_orphaned_summary(orphaned_by_owner)
        
#         # Export to JSON if requested
#         if args.export_json:
#             with open(args.export_json, 'w') as f:
#                 json.dump(orphaned_by_owner, f, indent=2, default=str)
#             console.print(f"📄 [green]Exported findings to {args.export_json}[/green]")
        
#         # Fix content for specific owner
#         if args.owner_id:
#             if args.owner_id not in orphaned_by_owner:
#                 console.print(f"❌ [red]Owner ID {args.owner_id} not found in orphaned content[/red]")
#                 return
            
#             owner_data = orphaned_by_owner[args.owner_id]
#             fixer.display_detailed_orphaned_content(args.owner_id, owner_data)
            
#             if not args.dry_run:
#                 if args.batch_fix or Confirm.ask(f"\n🔧 Fix orphaned content for this owner?"):
#                     console.print(f"\n🔄 [bold yellow]Fixing content for owner {args.owner_id}...[/bold yellow]")
#                     results = await fixer.fix_orphaned_content_for_owner(args.owner_id, owner_data)
#                     console.print(f"✅ [bold green]Fixed: {results['avatar_interactions']} AI, {results['templates']} templates, {results['knowledge_bases']} KBs, {results['supporting_documents']} docs[/bold green]")
#             else:
#                 results = await fixer.fix_orphaned_content_for_owner(args.owner_id, owner_data, dry_run=True)
#                 console.print(f"🔍 [yellow]Would fix: {results['avatar_interactions']} AI, {results['templates']} templates[/yellow]")
            
#             return
        
#         # Interactive mode - fix for each owner
#         if not args.batch_fix:
#             console.print("\n🎯 [bold cyan]Interactive Fixing Mode[/bold cyan]")
#             console.print("You can review and fix content for each owner individually.\n")
        
#         for owner_id, owner_data in orphaned_by_owner.items():
#             fixer.display_detailed_orphaned_content(owner_id, owner_data)
            
#             if args.batch_fix:
#                 should_fix = True
#                 console.print("🔧 [yellow]Batch fixing...[/yellow]")
#             elif args.dry_run:
#                 should_fix = True
#             else:
#                 should_fix = Confirm.ask(f"\n🔧 Fix orphaned content for this owner?")
            
#             if should_fix:
#                 console.print(f"\n🔄 [bold yellow]Processing content for owner {owner_id}...[/bold yellow]")
#                 results = await fixer.fix_orphaned_content_for_owner(owner_id, owner_data, args.dry_run)
                
#                 if args.dry_run:
#                     console.print(f"🔍 [yellow]Would fix: {results['avatar_interactions']} AI, {results['templates']} templates[/yellow]")
#                 else:
#                     console.print(f"✅ [bold green]Fixed: {results['avatar_interactions']} AI, {results['templates']} templates, {results['knowledge_bases']} KBs, {results['supporting_documents']} docs[/bold green]")
                    
#                     # Update totals
#                     fixer.fixed_count["avatar_interactions"] += results["avatar_interactions"]
#                     fixer.fixed_count["templates"] += results["templates"]
#                     fixer.fixed_count["knowledge_bases"] += results["knowledge_bases"]
#                     fixer.fixed_count["supporting_documents"] += results["supporting_documents"]
            
#             console.print("\n" + "="*60 + "\n")
        
#         # Final summary
#         if not args.dry_run and any(fixer.fixed_count.values()):
#             console.print(Panel(
#                 f"🎉 [bold green]Fixing Complete![/bold green]\n\n"
#                 f"Fixed:\n"
#                 f"• {fixer.fixed_count['avatar_interactions']} Avatar Interactions\n"
#                 f"• {fixer.fixed_count['templates']} Templates\n"
#                 f"• {fixer.fixed_count['knowledge_bases']} Knowledge Bases\n"
#                 f"• {fixer.fixed_count['supporting_documents']} Supporting Documents",
#                 title="✅ Success Summary"
#             ))
    
#     except KeyboardInterrupt:
#         console.print("\n🛑 [yellow]Operation cancelled by user[/yellow]")
#     except Exception as e:
#         console.print(f"❌ [bold red]Error: {str(e)}[/bold red]")
#         sys.exit(1)
#     finally:
#         await fixer.close()

# if __name__ == "__main__":
#     # Install required packages:
#     # pip install motor rich
#     asyncio.run(main())
#!/usr/bin/env python3
"""
Orphaned Content Fixer CLI
A command-line tool to fix orphaned avatar interactions and templates in courses.
"""

import asyncio
import motor.motor_asyncio
import json
import argparse
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich import print as rprint
from rich.panel import Panel

console = Console()

class OrphanedContentFixer:
    def __init__(self, mongodb_connection_string: str, database_name: str):
        """Initialize the fixer with MongoDB connection"""
        self.client = motor.motor_asyncio.AsyncIOMotorClient(mongodb_connection_string)
        self.db = self.client[database_name]
        self.fixed_count = {
            "avatar_interactions": 0,
            "templates": 0,
            "knowledge_bases": 0,
            "supporting_documents": 0
        }
    
    async def get_user_details(self, user_id: str) -> Dict[str, Any]:
        """Get user details by ID"""
        try:
            if not user_id:
                return {}
                
            user = await self.db.users.find_one({"_id": user_id})
            if user:
                return {
                    "id": user["_id"],
                    "username": user.get("username", "N/A"),
                    "email": user.get("email", "N/A"),
                    "role": user.get("role", "N/A"),
                    "company_id": user.get("company_id", "N/A")
                }
            return {}  # Return empty dict instead of None
        except Exception as e:
            console.print(f"[red]Warning: Error fetching user {user_id}: {str(e)}[/red]")
            return {}  # Return empty dict instead of None
    
    async def find_orphaned_content(self, course_id: Optional[str] = None) -> Dict[str, Any]:
        """Find all orphaned content grouped by should_be_owner"""
        console.print("🔍 [bold blue]Scanning for orphaned content...[/bold blue]")
        
        # Build query
        query = {}
        if course_id:
            query["_id"] = course_id
        
        courses = await self.db.courses.find(query).to_list(length=1000)
        
        # Group orphaned content by should_be_owner (course creator)
        orphaned_by_owner = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Analyzing courses...", total=len(courses))
            
            for course in courses:
                course_id = course["_id"]
                course_created_by = course.get("created_by")
                
                if not course_created_by:
                    progress.advance(task)
                    continue
                
                # Initialize owner group if not exists
                if course_created_by not in orphaned_by_owner:
                    user_details = await self.get_user_details(course_created_by)
                    # Ensure user_details is not None
                    if user_details is None:
                        user_details = {}
                    
                    orphaned_by_owner[course_created_by] = {
                        "owner_details": user_details,
                        "avatar_interactions": [],
                        "templates": [],
                        "courses_affected": set()
                    }
                
                # Check modules and scenarios
                module_ids = course.get("modules", [])
                for module_id in module_ids:
                    module = await self.db.modules.find_one({"_id": module_id})
                    if not module:
                        continue
                    
                    scenario_ids = module.get("scenarios", [])
                    for scenario_id in scenario_ids:
                        scenario = await self.db.scenarios.find_one({"_id": scenario_id})
                        if not scenario:
                            continue
                        
                        # Check avatar interactions
                        for mode in ["learn_mode", "try_mode", "assess_mode"]:
                            mode_data = scenario.get(mode)
                            if mode_data and isinstance(mode_data, dict):
                                ai_id = mode_data.get("avatar_interaction")
                                if ai_id:
                                    ai = await self.db.avatar_interactions.find_one({"_id": ai_id})
                                    if ai and ai.get("created_by") != course_created_by:
                                        current_owner = await self.get_user_details(ai.get("created_by"))
                                        # Ensure current_owner is not None
                                        if current_owner is None:
                                            current_owner = {}
                                            
                                        orphaned_by_owner[course_created_by]["avatar_interactions"].append({
                                            "id": ai_id,
                                            "scenario_title": scenario.get("title", "N/A"),
                                            "module_title": module.get("title", "N/A"),
                                            "course_title": course.get("title", "N/A"),
                                            "mode": mode,
                                            "current_owner": ai.get("created_by", "N/A"),
                                            "current_owner_details": current_owner,
                                            "bot_role": ai.get("bot_role", "N/A")
                                        })
                                        orphaned_by_owner[course_created_by]["courses_affected"].add(course_id)
                        
                        # Check templates
                        template_id = scenario.get("template_id")
                        if template_id:
                            template = await self.db.templates.find_one({"id": template_id})
                            if template and template.get("created_by") != course_created_by:
                                current_owner = await self.get_user_details(template.get("created_by"))
                                # Ensure current_owner is not None  
                                if current_owner is None:
                                    current_owner = {}
                                    
                                orphaned_by_owner[course_created_by]["templates"].append({
                                    "id": template_id,
                                    "name": template.get("name", "N/A"),
                                    "scenario_title": scenario.get("title", "N/A"),
                                    "module_title": module.get("title", "N/A"),
                                    "course_title": course.get("title", "N/A"),
                                    "current_owner": template.get("created_by", "N/A"),
                                    "current_owner_details": current_owner,
                                    "knowledge_base_id": template.get("knowledge_base_id")
                                })
                                orphaned_by_owner[course_created_by]["courses_affected"].add(course_id)
                
                progress.advance(task)
        
        # Convert sets to lists for JSON serialization
        for owner_id in orphaned_by_owner:
            orphaned_by_owner[owner_id]["courses_affected"] = list(orphaned_by_owner[owner_id]["courses_affected"])
        
        # Filter out owners with no orphaned content
        orphaned_by_owner = {k: v for k, v in orphaned_by_owner.items() 
                           if v["avatar_interactions"] or v["templates"]}
        
        return orphaned_by_owner
    
    async def fix_avatar_interactions(self, avatar_interaction_ids: List[str], new_owner_id: str) -> int:
        """Fix ownership of avatar interactions"""
        if not avatar_interaction_ids:
            return 0
        
        result = await self.db.avatar_interactions.update_many(
            {"_id": {"$in": avatar_interaction_ids}},
            {
                "$set": {
                    "created_by": new_owner_id,
                    "updated_at": datetime.now()
                }
            }
        )
        
        return result.modified_count
    
    async def fix_templates_and_knowledge_bases(self, template_data: List[Dict], new_owner_id: str) -> Dict[str, int]:
        """Fix ownership of templates and their knowledge bases"""
        if not template_data:
            return {"templates": 0, "knowledge_bases": 0, "supporting_documents": 0}
        
        template_ids = [t["id"] for t in template_data]
        knowledge_base_ids = [t["knowledge_base_id"] for t in template_data if t.get("knowledge_base_id")]
        
        # Fix templates
        template_result = await self.db.templates.update_many(
            {"id": {"$in": template_ids}},
            {
                "$set": {
                    "created_by": new_owner_id,
                    "updated_at": datetime.now()
                }
            }
        )
        
        # Fix knowledge bases
        kb_result = None
        docs_count = 0
        if knowledge_base_ids:
            kb_result = await self.db.knowledge_bases.update_many(
                {"_id": {"$in": knowledge_base_ids}},
                {
                    "$set": {
                        "last_updated": datetime.now()
                    }
                }
            )
            
            # Fix supporting documents
            for kb_id in knowledge_base_ids:
                doc_result = await self.db.supporting_documents.update_many(
                    {"knowledge_base_id": kb_id},
                    {
                        "$set": {
                            "updated_at": datetime.now()
                        }
                    }
                )
                docs_count += doc_result.modified_count
        
        return {
            "templates": template_result.modified_count,
            "knowledge_bases": kb_result.modified_count if kb_result else 0,
            "supporting_documents": docs_count
        }
    
    async def fix_orphaned_content_for_owner(self, owner_id: str, orphaned_data: Dict[str, Any], dry_run: bool = False) -> Dict[str, int]:
        """Fix all orphaned content for a specific owner"""
        
        if dry_run:
            console.print(f"[yellow]🔍 DRY RUN: Would fix content for owner {owner_id}[/yellow]")
            return {
                "avatar_interactions": len(orphaned_data.get("avatar_interactions", [])),
                "templates": len(orphaned_data.get("templates", [])),
                "knowledge_bases": len(set(t.get("knowledge_base_id") for t in orphaned_data.get("templates", []) if t.get("knowledge_base_id"))),
                "supporting_documents": 0  # Can't easily count without actually querying
            }
        
        results = {"avatar_interactions": 0, "templates": 0, "knowledge_bases": 0, "supporting_documents": 0}
        
        # Fix avatar interactions
        ai_ids = [ai["id"] for ai in orphaned_data.get("avatar_interactions", [])]
        if ai_ids:
            ai_count = await self.fix_avatar_interactions(ai_ids, owner_id)
            results["avatar_interactions"] = ai_count
            console.print(f"✅ Fixed {ai_count} avatar interactions")
        
        # Fix templates and knowledge bases
        templates = orphaned_data.get("templates", [])
        if templates:
            template_results = await self.fix_templates_and_knowledge_bases(templates, owner_id)
            results.update(template_results)
            console.print(f"✅ Fixed {template_results['templates']} templates, {template_results['knowledge_bases']} knowledge bases, {template_results['supporting_documents']} documents")
        
        return results
    
    def display_orphaned_summary(self, orphaned_by_owner: Dict[str, Any]):
        """Display summary of orphaned content"""
        if not orphaned_by_owner:
            console.print("🎉 [bold green]No orphaned content found![/bold green]")
            return
        
        # Summary table
        summary_table = Table(title="📊 Orphaned Content Summary")
        summary_table.add_column("Owner", style="cyan")
        summary_table.add_column("Username", style="green") 
        summary_table.add_column("Email", style="blue")
        summary_table.add_column("Avatar Interactions", justify="right", style="red")
        summary_table.add_column("Templates", justify="right", style="yellow")
        summary_table.add_column("Courses Affected", justify="right", style="magenta")
        
        total_ai = 0
        total_templates = 0
        
        for owner_id, data in orphaned_by_owner.items():
            owner_details = data.get("owner_details") or {}
            ai_count = len(data.get("avatar_interactions", []))
            template_count = len(data.get("templates", []))
            courses_count = len(data.get("courses_affected", []))
            
            total_ai += ai_count
            total_templates += template_count
            
            summary_table.add_row(
                owner_id[:12] + "..." if len(owner_id) > 15 else owner_id,
                owner_details.get("username", "N/A"),
                owner_details.get("email", "N/A"),
                str(ai_count),
                str(template_count),
                str(courses_count)
            )
        
        console.print(summary_table)
        console.print(f"\n📈 [bold]Total: {total_ai} orphaned avatar interactions, {total_templates} orphaned templates across {len(orphaned_by_owner)} owners[/bold]")
    
    def display_detailed_orphaned_content(self, owner_id: str, orphaned_data: Dict[str, Any]):
        """Display detailed orphaned content for a specific owner"""
        # Add safety checks for None values
        if not orphaned_data:
            console.print(f"❌ [red]No orphaned data found for owner {owner_id}[/red]")
            return
            
        owner_details = orphaned_data.get("owner_details") or {}
        
        # Safety check for owner_details being None
        if owner_details is None:
            owner_details = {}
        
        console.print(Panel(
            f"Owner: {owner_details.get('username', 'N/A')} ({owner_details.get('email', 'N/A')})\n"
            f"Role: {owner_details.get('role', 'N/A')}\n"
            f"Owner ID: {owner_id}",
            title=f"🎯 Orphaned Content for {owner_details.get('username', owner_id[:12])}",
            expand=False
        ))
        
        # Avatar Interactions Table
        ai_data = orphaned_data.get("avatar_interactions", [])
        if ai_data and isinstance(ai_data, list):
            ai_table = Table(title=f"🤖 Avatar Interactions ({len(ai_data)})")
            ai_table.add_column("ID", style="cyan", max_width=15)
            ai_table.add_column("Course", style="green", max_width=20)
            ai_table.add_column("Module", style="blue", max_width=20)
            ai_table.add_column("Scenario", style="yellow", max_width=20)
            ai_table.add_column("Mode", style="magenta")
            ai_table.add_column("Bot Role", style="white")
            ai_table.add_column("Current Owner", style="red", max_width=15)
            
            for ai in ai_data:
                # Add safety checks for None values
                if not ai or not isinstance(ai, dict):
                    continue
                    
                current_owner = ai.get("current_owner_details")
                # Safety check for current_owner being None
                if current_owner is None:
                    current_owner = {}
                
                # Safety checks for all required fields
                ai_id = ai.get("id", "N/A")
                course_title = ai.get("course_title", "N/A") 
                module_title = ai.get("module_title", "N/A")
                scenario_title = ai.get("scenario_title", "N/A")
                mode = ai.get("mode", "N/A")
                bot_role = ai.get("bot_role", "N/A")
                current_owner_name = current_owner.get("username", ai.get("current_owner", "N/A")[:12])
                
                ai_table.add_row(
                    ai_id[:12] + "..." if len(str(ai_id)) > 15 else str(ai_id),
                    course_title[:17] + "..." if len(str(course_title)) > 20 else str(course_title),
                    module_title[:17] + "..." if len(str(module_title)) > 20 else str(module_title),
                    scenario_title[:17] + "..." if len(str(scenario_title)) > 20 else str(scenario_title),
                    str(mode).replace("_mode", ""),
                    bot_role[:15] + "..." if len(str(bot_role)) > 18 else str(bot_role),
                    str(current_owner_name)
                )
            
            console.print(ai_table)
        
        # Templates Table
        template_data = orphaned_data.get("templates", [])
        if template_data and isinstance(template_data, list):
            template_table = Table(title=f"📋 Templates ({len(template_data)})")
            template_table.add_column("ID", style="cyan", max_width=15)
            template_table.add_column("Name", style="green", max_width=25)
            template_table.add_column("Course", style="blue", max_width=20)
            template_table.add_column("Module", style="yellow", max_width=20)
            template_table.add_column("Scenario", style="magenta", max_width=20)
            template_table.add_column("Current Owner", style="red", max_width=15)
            template_table.add_column("KB ID", style="white", max_width=15)
            
            for template in template_data:
                # Add safety checks for None values
                if not template or not isinstance(template, dict):
                    continue
                    
                current_owner = template.get("current_owner_details")
                if current_owner is None:
                    current_owner = {}
                    
                # Safety checks for all fields
                template_id = template.get("id", "N/A")
                name = template.get("name", "N/A")
                course_title = template.get("course_title", "N/A")
                module_title = template.get("module_title", "N/A") 
                scenario_title = template.get("scenario_title", "N/A")
                current_owner_name = current_owner.get("username", template.get("current_owner", "N/A")[:12])
                kb_id = template.get("knowledge_base_id", "N/A")
                
                template_table.add_row(
                    str(template_id)[:12] + "..." if len(str(template_id)) > 15 else str(template_id),
                    str(name)[:22] + "..." if len(str(name)) > 25 else str(name),
                    str(course_title)[:17] + "..." if len(str(course_title)) > 20 else str(course_title),
                    str(module_title)[:17] + "..." if len(str(module_title)) > 20 else str(module_title),
                    str(scenario_title)[:17] + "..." if len(str(scenario_title)) > 20 else str(scenario_title),
                    str(current_owner_name),
                    str(kb_id)[:12] + "..." if isinstance(kb_id, str) and len(kb_id) > 15 else str(kb_id)
                )
            
            console.print(template_table)
    
    async def close(self):
        """Close the database connection"""
        self.client.close()

async def main():
    parser = argparse.ArgumentParser(description="Fix orphaned avatar interactions and templates in courses")
    parser.add_argument("--connection", "-c", required=True, help="MongoDB connection string")
    parser.add_argument("--database", "-d", required=True, help="Database name")
    parser.add_argument("--course-id", help="Specific course ID to analyze")
    parser.add_argument("--owner-id", help="Fix content for specific owner ID only")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed without making changes")
    parser.add_argument("--export-json", help="Export findings to JSON file")
    parser.add_argument("--batch-fix", action="store_true", help="Fix all orphaned content without individual confirmation")
    
    args = parser.parse_args()
    
    console.print("🔧 [bold blue]Orphaned Content Fixer CLI[/bold blue]")
    console.print(f"Database: {args.database}")
    
    if args.dry_run:
        console.print("[yellow]⚠️  DRY RUN MODE: No changes will be made[/yellow]")
    
    fixer = OrphanedContentFixer(args.connection, args.database)
    
    try:
        # Find orphaned content
        orphaned_by_owner = await fixer.find_orphaned_content(args.course_id)
        
        if not orphaned_by_owner:
            console.print("🎉 [bold green]No orphaned content found![/bold green]")
            return
        
        # Display summary
        fixer.display_orphaned_summary(orphaned_by_owner)
        
        # Export to JSON if requested
        if args.export_json:
            with open(args.export_json, 'w') as f:
                json.dump(orphaned_by_owner, f, indent=2, default=str)
            console.print(f"📄 [green]Exported findings to {args.export_json}[/green]")
        
        # Fix content for specific owner
        if args.owner_id:
            if args.owner_id not in orphaned_by_owner:
                console.print(f"❌ [red]Owner ID {args.owner_id} not found in orphaned content[/red]")
                return
            
            owner_data = orphaned_by_owner[args.owner_id]
            fixer.display_detailed_orphaned_content(args.owner_id, owner_data)
            
            if not args.dry_run:
                if args.batch_fix or Confirm.ask(f"\n🔧 Fix orphaned content for this owner?"):
                    console.print(f"\n🔄 [bold yellow]Fixing content for owner {args.owner_id}...[/bold yellow]")
                    results = await fixer.fix_orphaned_content_for_owner(args.owner_id, owner_data)
                    console.print(f"✅ [bold green]Fixed: {results['avatar_interactions']} AI, {results['templates']} templates, {results['knowledge_bases']} KBs, {results['supporting_documents']} docs[/bold green]")
            else:
                results = await fixer.fix_orphaned_content_for_owner(args.owner_id, owner_data, dry_run=True)
                console.print(f"🔍 [yellow]Would fix: {results['avatar_interactions']} AI, {results['templates']} templates[/yellow]")
            
            return
        
        # Interactive mode - fix for each owner
        if not args.batch_fix:
            console.print("\n🎯 [bold cyan]Interactive Fixing Mode[/bold cyan]")
            console.print("You can review and fix content for each owner individually.\n")
        
        for owner_id, owner_data in orphaned_by_owner.items():
            fixer.display_detailed_orphaned_content(owner_id, owner_data)
            
            if args.batch_fix:
                should_fix = True
                console.print("🔧 [yellow]Batch fixing...[/yellow]")
            elif args.dry_run:
                should_fix = True
            else:
                should_fix = Confirm.ask(f"\n🔧 Fix orphaned content for this owner?")
            
            if should_fix:
                console.print(f"\n🔄 [bold yellow]Processing content for owner {owner_id}...[/bold yellow]")
                results = await fixer.fix_orphaned_content_for_owner(owner_id, owner_data, args.dry_run)
                
                if args.dry_run:
                    console.print(f"🔍 [yellow]Would fix: {results['avatar_interactions']} AI, {results['templates']} templates[/yellow]")
                else:
                    console.print(f"✅ [bold green]Fixed: {results['avatar_interactions']} AI, {results['templates']} templates, {results['knowledge_bases']} KBs, {results['supporting_documents']} docs[/bold green]")
                    
                    # Update totals
                    fixer.fixed_count["avatar_interactions"] += results["avatar_interactions"]
                    fixer.fixed_count["templates"] += results["templates"]
                    fixer.fixed_count["knowledge_bases"] += results["knowledge_bases"]
                    fixer.fixed_count["supporting_documents"] += results["supporting_documents"]
            
            console.print("\n" + "="*60 + "\n")
        
        # Final summary
        if not args.dry_run and any(fixer.fixed_count.values()):
            console.print(Panel(
                f"🎉 [bold green]Fixing Complete![/bold green]\n\n"
                f"Fixed:\n"
                f"• {fixer.fixed_count['avatar_interactions']} Avatar Interactions\n"
                f"• {fixer.fixed_count['templates']} Templates\n"
                f"• {fixer.fixed_count['knowledge_bases']} Knowledge Bases\n"
                f"• {fixer.fixed_count['supporting_documents']} Supporting Documents",
                title="✅ Success Summary"
            ))
    
    except KeyboardInterrupt:
        console.print("\n🛑 [yellow]Operation cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"❌ [bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)
    finally:
        await fixer.close()

if __name__ == "__main__":
    # Install required packages:
    # pip install motor rich
    asyncio.run(main())