# Development Guidelines

## Code Quality Standards

### Import Organization
- **Standard Pattern**: Group imports by type (standard library, third-party, local)
- **FastAPI Convention**: Import FastAPI components first, followed by typing, then domain-specific imports
- **Example Structure**:
  ```python
  from fastapi import APIRouter, Depends, HTTPException, status, Body, Path, Query
  from typing import List, Optional, Dict, Any, Union
  from uuid import UUID, uuid4
  from datetime import datetime
  # Local imports last
  from models.user_models import UserDB, UserRole
  from core.database import get_db
  ```

### Error Handling Patterns
- **Consistent HTTPException Usage**: Always use appropriate status codes with descriptive messages
- **Database Error Handling**: Wrap database operations in try-catch blocks with meaningful error responses
- **Validation Pattern**: Check existence before operations, provide specific error messages
- **Example**:
  ```python
  user = await get_user_by_id(db, user_id)
  if not user:
      raise HTTPException(status_code=404, detail="User not found")
  ```

### Function Documentation
- **Docstring Standard**: Use triple quotes with clear descriptions of purpose, parameters, and return values
- **Type Hints**: Always include comprehensive type hints for parameters and return values
- **Async Pattern**: Clearly document async functions and their database dependencies

### Variable Naming Conventions
- **Database IDs**: Use `_id` suffix for MongoDB document IDs, `id` for UUID fields
- **Boolean Flags**: Use `is_`, `has_`, `can_` prefixes for clarity
- **Collections**: Use plural nouns for lists and dictionaries
- **Constants**: Use UPPER_CASE for configuration values and enums

## Architectural Patterns

### FastAPI Router Structure
- **Prefix Pattern**: Use descriptive prefixes for router grouping (`/auth`, `/scenario`, `/admin`)
- **Dependency Injection**: Leverage FastAPI's dependency system for database connections and user authentication
- **Response Models**: Always define Pydantic response models for consistent API contracts
- **Status Codes**: Use appropriate HTTP status codes (201 for creation, 204 for deletion, etc.)

### Database Operations
- **Async Pattern**: All database operations use async/await with Motor driver
- **Connection Management**: Use dependency injection for database connections
- **Error Handling**: Consistent error handling with try-catch blocks
- **Document Conversion**: Convert MongoDB ObjectIds to strings for JSON serialization
- **Example Pattern**:
  ```python
  async def get_user_by_id(db: Any, user_id: UUID) -> Optional[UserDB]:
      user = await db.users.find_one({"_id": str(user_id)})
      if user:
          return UserDB(**user)
      return None
  ```

### Authentication & Authorization
- **JWT Pattern**: Use JWT tokens with role-based access control
- **Dependency Chain**: Create role-specific dependencies (`get_admin_user`, `get_superadmin_user`)
- **Permission Validation**: Check permissions at multiple levels (company, role, ownership)
- **Security Headers**: Always include appropriate security headers in responses

### Multi-Tenant Architecture
- **Company Isolation**: Filter all queries by company_id for data isolation
- **Hierarchical Permissions**: Implement role-based hierarchy (Boss Admin > Super Admin > Admin > User)
- **Demo Account Handling**: Special logic for demo account expiration and inheritance
- **Usage Tracking**: Implement tier-based usage limits and tracking

## Internal API Usage Patterns

### Azure OpenAI Integration
- **Client Initialization**: Use AsyncAzureOpenAI with environment-based configuration
- **Token Logging**: Implement token usage tracking for cost monitoring
- **Error Handling**: Graceful fallbacks when AI services are unavailable
- **Temperature Control**: Use appropriate temperature settings (0.1-0.3 for factual, 0.7 for creative)
- **Example**:
  ```python
  response = await self.openai_client.chat.completions.create(
      model="gpt-4o",
      messages=messages,
      temperature=0.2,
      max_tokens=800
  )
  log_token_usage(response, "function_name")
  ```

### Azure Search Vector Operations
- **Security Pattern**: Always filter by knowledge_base_id to prevent cross-contamination
- **Client Management**: Properly close search clients in finally blocks
- **Embedding Generation**: Use text-embedding-ada-002 for consistent embeddings
- **Batch Processing**: Process documents in batches of 100 for optimal performance

### Database Query Patterns
- **Aggregation Pipeline**: Use MongoDB aggregation for complex queries
- **Pagination**: Implement skip/limit patterns for large result sets
- **Indexing Strategy**: Create compound indexes for frequently queried fields
- **Cursor Management**: Use async iteration for large collections

## Common Code Idioms

### Pydantic Model Patterns
- **Field Validation**: Use Field() with descriptions and constraints
- **UUID Handling**: Convert UUIDs to strings for MongoDB compatibility
- **Datetime Fields**: Use datetime.now() as default factory for timestamps
- **Optional Fields**: Use Optional[] for nullable fields with None defaults

### FastAPI Endpoint Patterns
- **Parameter Validation**: Use Query(), Path(), Body() for explicit parameter handling
- **Response Models**: Always specify response_model for type safety
- **Status Codes**: Use status_code parameter for non-200 responses
- **Dependency Injection**: Chain dependencies for authentication and database access

### Error Response Patterns
- **Consistent Structure**: Use HTTPException with status_code and detail
- **User-Friendly Messages**: Provide clear, actionable error messages
- **Security Considerations**: Don't expose internal system details in error messages
- **Logging**: Log detailed errors internally while returning sanitized messages to users

### Async/Await Best Practices
- **Database Operations**: Always await database calls
- **External API Calls**: Use async for OpenAI and Azure Search operations
- **Error Propagation**: Let async exceptions bubble up to FastAPI error handlers
- **Resource Cleanup**: Use try/finally blocks for resource cleanup

## Popular Annotations

### Type Hints
- `List[Dict[str, Any]]` for flexible data structures
- `Optional[UUID]` for nullable ID fields
- `Union[UserDB, AdminUserDB]` for polymorphic user types
- `Depends(get_current_user)` for authentication dependencies

### Pydantic Decorators
- `@validator` for custom field validation
- `@root_validator` for cross-field validation
- `Field(...)` for field constraints and descriptions
- `BaseModel.dict(by_alias=True)` for MongoDB serialization

### FastAPI Decorators
- `@router.post("/endpoint", response_model=Model)` for endpoint definition
- `@app.on_event("startup")` for application initialization
- `@app.middleware("http")` for request/response middleware

### Database Patterns
- `await db.collection.find_one({"_id": str(id)})` for single document retrieval
- `async for doc in cursor:` for iterating over query results
- `await db.collection.update_one(filter, {"$set": update_data})` for updates
- `result.inserted_id` for getting created document IDs

## Frequently Used Code Patterns

### User Authentication Flow
```python
async def get_current_user(token: str = Depends(oauth2_scheme), db: Any = Depends(get_database)):
    # JWT validation
    # User lookup
    # Demo expiry check
    return user
```

### Database CRUD Operations
```python
async def create_entity(db: Any, entity_data: EntityCreate) -> EntityDB:
    entity_dict = entity_data.dict()
    entity_dict["created_at"] = datetime.now()
    result = await db.entities.insert_one(entity_dict)
    return await get_entity_by_id(db, result.inserted_id)
```

### Permission Checking
```python
if user.role == UserRole.ADMIN:
    if user.company_id != target_company_id:
        raise HTTPException(status_code=403, detail="Not authorized")
```

### Response Formatting
```python
return {
    "success": True,
    "data": result,
    "message": "Operation completed successfully"
}
```

These patterns ensure consistency, maintainability, and security across the codebase while following FastAPI and MongoDB best practices.