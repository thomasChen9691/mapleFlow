"""Configuration settings for the backend application."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Qwen API
    qwen_api_key: str = ""
    
    # DeepSeek API
    deepseek_api_key: str = ""
    
    # MCP API
    mcp_api_key: str = ""
    mcp_base_url: Optional[str] = None
    mcp_access_token: Optional[str] = None
    mcp_secret_key: Optional[str] = None
    
    # Blog content path
    blog_content_path: str = "content/posts"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
