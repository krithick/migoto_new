# Technology Stack

## Programming Languages
- **Python 3.8+**: Primary backend language
- **JavaScript/TypeScript**: Frontend integration (implied from API structure)

## Core Framework
- **FastAPI**: Modern, fast web framework for building APIs
  - Automatic API documentation with Swagger/OpenAPI
  - Built-in data validation with Pydantic
  - Async/await support for high performance
  - CORS middleware for cross-origin requests

## Database & Storage
- **MongoDB**: Primary NoSQL database
  - Motor: Async MongoDB driver for Python
  - PyMongo: MongoDB driver for synchronous operations
- **Azure Search**: Vector search and knowledge base storage
- **File System**: Local file storage with organized upload directories

## AI & Machine Learning
- **Azure OpenAI**: GPT models for conversation and analysis
  - Chat completions for interactive scenarios
  - Text analysis for performance evaluation
  - Embedding generation for semantic search
- **Vector Search**: Semantic document retrieval and fact-checking

## Authentication & Security
- **JWT (JSON Web Tokens)**: Stateless authentication
- **Passlib**: Password hashing with bcrypt
- **Python-JOSE**: JWT token handling
- **Role-Based Access Control**: Multi-tier user permissions

## Data Validation & Serialization
- **Pydantic v2**: Data validation and settings management
- **Email Validator**: Email format validation
- **UUID**: Unique identifier generation

## Development Tools
- **Uvicorn**: ASGI server for FastAPI applications
- **Python-dotenv**: Environment variable management
- **Python-multipart**: File upload handling

## Build & Deployment
```bash
# Install dependencies
pip install -r req.txt

# Run development server
uvicorn main:app --host 0.0.0.0 --port 9000 --reload

# Environment setup
cp .env.example .env
# Configure MongoDB, Azure OpenAI, and Azure Search credentials
```

## Key Dependencies
```
fastapi>=0.103.1          # Web framework
uvicorn>=0.23.2           # ASGI server
motor>=3.3.1              # Async MongoDB driver
pymongo>=4.5.0            # MongoDB driver
pydantic>=2.0.0           # Data validation
python-jose>=3.3.0        # JWT handling
passlib>=1.7.4            # Password hashing
bcrypt==4.0.1             # Encryption
python-dotenv>=1.0.0      # Environment management
```

## Configuration Requirements
- **MongoDB Connection**: Database URL and name
- **Azure OpenAI**: API key, endpoint, and version
- **Azure Search**: Service name and API key
- **Authentication**: JWT secret key
- **File Storage**: Upload directory permissions

## Development Commands
- `python main.py` - Start the application
- `uvicorn main:app --reload` - Development server with auto-reload
- Database migrations handled through startup events
- Bot factory initialization on application start

## API Documentation
- Swagger UI available at `/docs`
- ReDoc documentation at `/redoc`
- OpenAPI schema at `/openapi.json`