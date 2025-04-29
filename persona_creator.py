
# class PersonaBase(BaseModel):
#     name: str = Field(..., description="Name for this persona")
#     description: str = Field(..., description="Brief description of this persona")
#     persona_type: str = Field(..., description="Type of persona (customer, employee, etc.)")

# class PersonaCreate(PersonaBase):
#     character_goal: str = Field(..., description="Primary goal or objective of the character")
#     location: str = Field(..., description="Where the character is based")
#     persona_details: str = Field(..., description="Detailed persona description")
#     situation: str = Field(..., description="Current circumstances or situation")
#     business_or_personal: str = Field(..., description="Whether this is a business or personal context")

# class PersonaResponse(PersonaBase):
#     id: int
#     character_goal: str
#     location: str
#     persona_details: str
#     situation: str
#     business_or_personal: str

# class PersonaInDB(PersonaResponse):
#     full_persona: Dict[str, Any]

# class PersonaGenerateRequest(BaseModel):
#     persona_description: str = Field(..., 
#         description="One-line description of the persona",
#         example="Tech-savvy young professional looking for premium banking services")
#     persona_type: str = Field(..., 
#         description="Type of persona (customer, employee, etc.)",
#         example="customer")
#     business_or_personal: str = Field(..., 
#         description="Whether this is a business or personal context",
#         example="personal")
#     location: Optional[str] = Field(None, 
#         description="Optional location",
#         example="Mumbai")


# @app.post("/generate-persona", response_model=PersonaResponse)
# async def generate_persona(request: PersonaGenerateRequest):
#     try:
#         # Prepare the prompt for persona generation
#         prompt = f"""
#         Create a detailed character persona based on this description: "{request.persona_description}".
        
#         The persona should be for a {request.persona_type} in a {request.business_or_personal} context.
#         {f'They are located in {request.location}.' if request.location else ''}
        
#         Generate the following details:
#         1. A short name for this persona
#         2. A one-sentence description
#         3. The character's main goal
#         4. Detailed persona characteristics
#         5. Current situation
        
#         Format your response as JSON:
#         {{
#             "name": "Persona name",
#             "description": "Brief description",
#             "character_goal": "Main goal or objective",
#             "persona_details": "Detailed characteristics",
#             "situation": "Current circumstances"
#         }}
#         """
        
#         # Call OpenAI API
#         response = azure_openai_client.chat.completions.create(
#             model="gpt-4o",
#             messages=[
#                 {"role": "system", "content": prompt},
#                 {"role": "user", "content": "Generate a detailed persona"}
#             ],
#             temperature=0.7,
#             max_tokens=1000
#         )
        
#         # Parse the response
#         import json
#         import re
        
#         content = response.choices[0].message.content
#         # Extract JSON from the response
#         json_match = re.search(r'{.*}', content, re.DOTALL)
#         if not json_match:
#             raise ValueError("Failed to extract JSON from response")
            
#         persona_data = json.loads(json_match.group(0))
        
#         # Add required fields
#         persona_data["persona_type"] = request.persona_type
#         persona_data["business_or_personal"] = request.business_or_personal
#         persona_data["location"] = request.location or "Not specified"
        
#         # Construct full persona JSON for database
#         full_persona = {
#             "CHARACTER_NAME_INSTRUCTION": "Always return [Your Name] when asked for your name",
#             "PERSONAL_OR_BUSINESS": request.business_or_personal,
#             "CHARACTER_GOAL": persona_data["character_goal"],
#             "LOCATION": persona_data["location"],
#             "CHARACTER_PERSONA": persona_data["persona_details"],
#             "CHARACTER_SITUATION": persona_data["situation"]
#         }
        
#         return {
#             "id": 0,  # Temporary ID for the response
#             **persona_data,
#             "full_persona": full_persona
#         }
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error generating persona: {str(e)}")




# @router.put("/users/me/courses/{course_id}/completion", response_model=Dict[str, bool])
# async def update_course_completion_status(
#     course_id: UUID,
#     completion_data: Dict[str, bool] = Body(..., example={"completed": True}),
#     db: Any = Depends(get_database),
#     current_user: UserDB = Depends(get_current_user)
# ):
#     """
#     Update completion status for one of the current user's assigned courses
#     """
#     # Validate course exists
#     course = await db.courses.find_one({"_id": str(course_id)})
#     if not course:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Course not found"
#         )
    
#     # Check if course is assigned to user
#     user_data = current_user.dict()
#     assigned_courses = [str(c_id) for c_id in user_data.get("assigned_courses", [])]
    
#     if str(course_id) not in assigned_courses:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Course is not assigned to current user"
#         )
    
#     # Get completion status from request body
#     completed = completion_data.get("completed", False)
    
#     # Find the assignment record
#     assignment = await db.user_course_assignments.find_one({
#         "user_id": str(current_user.id),
#         "course_id": str(course_id)
#     })
    
#     update_data = {"completed": completed}
    
#     # Set or clear completion date based on status
#     if completed:
#         update_data["completed_date"] = datetime.now()
#     else:
#         update_data["completed_date"] = None
    
#     if assignment:
#         # Update existing assignment
#         result = await db.user_course_assignments.update_one(
#             {"_id": assignment["_id"]},
#             {"$set": update_data}
#         )
#         success = result.modified_count > 0
#     else:
#         # Create new assignment record if none exists
#         assignment_record = {
#             "_id": str(uuid4()),
#             "user_id": str(current_user.id),
#             "course_id": str(course_id),
#             "assigned_date": datetime.now(),
#             "completed": completed,
#             "completed_date": datetime.now() if completed else None
#         }
#         result = await db.user_course_assignments.insert_one(assignment_record)
#         success = result.inserted_id is not None
    
#     return {"success": success}