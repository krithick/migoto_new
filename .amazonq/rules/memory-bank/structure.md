# Project Structure

## Directory Organization

### Core Application Structure
```
migoto_new/
├── core/                    # Core business logic modules
├── models/                  # Pydantic data models and schemas
├── services/               # External service integrations
├── src/                    # Clean architecture implementation
├── tests/                  # Test suites
├── uploads/                # File storage directories
└── diagrams/               # System documentation diagrams
```

### Core Module Breakdown
- **core/**: Contains all business logic routers and handlers
  - `user.py` - User management and authentication
  - `scenario.py` - Training scenario management
  - `avatar.py` - Avatar configuration and management
  - `chat.py` - Real-time conversation handling
  - `azure_search_manager.py` - Vector search and knowledge base operations
  - `document_processor.py` - File processing and indexing
  - `tier_*.py` - Role-based access control systems

### Models Architecture
- **models/**: Pydantic models for data validation and serialization
  - `user_models.py` - User hierarchy and authentication models
  - `scenario_models.py` - Training scenario data structures
  - `tier_models.py` - Multi-tenant organization models
  - `evaluation_models.py` - Performance assessment schemas

### Clean Architecture (src/)
```
src/
├── api/                    # API layer (controllers)
├── application/            # Application services
├── core/                   # Business rules and entities
├── domain/                 # Domain models and interfaces
└── infrastructure/         # External concerns (DB, APIs)
```

## Component Relationships

### Data Flow Architecture
1. **API Layer**: FastAPI routers handle HTTP requests
2. **Business Logic**: Core modules process business rules
3. **Data Models**: Pydantic models ensure type safety
4. **Database Layer**: MongoDB with Motor async driver
5. **External Services**: Azure OpenAI and Azure Search integration

### Key Integrations
- **MongoDB**: Primary data storage with async operations
- **Azure OpenAI**: AI conversation and analysis engine
- **Azure Search**: Vector search for knowledge base queries
- **FastAPI**: Web framework with automatic API documentation

### File Organization Patterns
- **Separation of Concerns**: Clear boundaries between API, business logic, and data
- **Feature-Based Modules**: Each core feature has dedicated router and models
- **Hierarchical Access**: Tier-based routing for different user roles
- **Upload Management**: Organized file storage by type (audio, video, documents)

## Architectural Patterns

### Multi-Tenant Design
- Company-based data isolation
- Hierarchical user management
- Role-based access control
- Scalable organization structure

### Event-Driven Components
- Startup event handlers for system initialization
- Dynamic bot factory for AI conversation management
- Real-time chat processing with streaming responses

### Configuration Management
- Environment-based configuration (.env)
- Database connection pooling
- Service initialization on startup
- CORS and middleware configuration