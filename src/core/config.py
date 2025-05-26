# from pydantic import BaseSettings, Field
# from typing import Optional

# class Settings(BaseSettings):
#     """Application settings"""
    
#     # Application
#     app_name: str = "Learning Platform API"
#     debug: bool = False
    
#     # MongoDB
#     mongodb_uri: str = Field(..., env="MONGO_URL")
#     database_name: str = Field(..., env="DATABASE_NAME")
    
#     # JWT
#     secret_key: str = Field(..., env="SECRET_KEY")
#     algorithm: str = "HS256"
#     token_expire_minutes: int = 60 * 24 * 7  # 1 week
    
#     # CORS
#     cors_origins: list = ["*"]
    
#     # Pagination
#     default_skip: int = 0
#     default_limit: int = 100
#     max_limit: int = 1000
    
#     class Config:
#         env_file = ".env"
#         case_sensitive = False

# # Create settings instance
# settings = Settings()
from pydantic_settings import BaseSettings
from pydantic import Field,ConfigDict
from typing import Optional, List

class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "Learning Platform API"
    debug: bool = False
    
    # MongoDB
    mongodb_uri: str = Field(default="mongodb://localhost:27017", alias="MONGO_URL")
    database_name: str = Field(default="learning_platform", alias="DATABASE_NAME")
    
    # JWT
    secret_key: str = Field(default="your-secret-key-for-jwt", alias="SECRET_KEY")
    algorithm: str = "HS256"
    token_expire_minutes: int = 60 * 24 * 7  # 1 week
    
    # API Settings
    api_key: str = Field(default="", alias="api_key")
    endpoint: str = Field(default="", alias="endpoint")
    api_version: str = Field(default="", alias="api_version")
    
    # CORS
    cors_origins: List[str] = ["*"]
    
    # Pagination
    default_skip: int = 0
    default_limit: int = 100
    max_limit: int = 1000
    
    # class Config:
    #     env_file = ".env"
    #     case_sensitive = False
    #     populate_by_name = True  # This allows both field name and alias

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        populate_by_name=True,
        extra="allow"  # This allows extra fields from .env
    )
# Create settings instance
settings = Settings()