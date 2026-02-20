"""Data models for blog content.

与 Hugo 文章 front matter 对应：title、date、draft、categories、tags；
BlogPost 表示单篇文章，BlogPostList 用于 API 列表与搜索返回。
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class BlogPostFrontMatter(BaseModel):
    """Hugo 文章 front matter（TOML 块）解析后的元数据。"""
    title: str
    date: datetime
    draft: bool = False
    categories: List[str] = []
    tags: List[str] = []


class BlogPost(BaseModel):
    """单篇博客文章：元数据 + 正文 Markdown。slug 为文件名（无扩展名）。"""
    front_matter: BlogPostFrontMatter
    content: str
    filename: str
    slug: str


class BlogPostList(BaseModel):
    """文章列表响应：posts 数组 + 总数 total，用于 /api/posts 与 /api/posts/search。"""
    posts: List[BlogPost]
    total: int
