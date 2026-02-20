"""Configuration settings for the backend application.

从环境变量和 .env 文件加载配置，供 blog_parser 与 main 使用。
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ---------- 大模型 / 外部 API（可选，用于后续扩展） ----------
    # Qwen API
    qwen_api_key: str = ""
    # DeepSeek API
    deepseek_api_key: str = ""
    # MCP (Model Context Protocol) API
    mcp_api_key: str = ""
    mcp_base_url: Optional[str] = None
    mcp_access_token: Optional[str] = None
    mcp_secret_key: Optional[str] = None

    # ---------- 博客内容路径（Hugo content/posts 目录） ----------
    blog_content_path: str = "content/posts"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# 全局单例，在 main、blog_parser 中通过 backend.config.settings 使用
settings = Settings()
