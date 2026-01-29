"""Data models for blog content."""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class BlogPostFrontMatter(BaseModel):
    """Front matter metadata for a blog post."""
    title: str
    date: datetime
    draft: bool = False
    categories: List[str] = []
    tags: List[str] = []


class BlogPost(BaseModel):
    """Complete blog post with front matter and content."""
    front_matter: BlogPostFrontMatter
    content: str
    filename: str
    slug: str


class BlogPostList(BaseModel):
    """List of blog posts."""
    posts: List[BlogPost]
    total: int
