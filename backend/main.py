"""FastAPI application for blog content API."""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
import json
from backend.blog_parser import get_all_blog_posts, get_blog_post_by_slug
from backend.models import BlogPost, BlogPostList
from backend.config import settings

app = FastAPI(
    title="MapleFlow Blog API",
    description="API for accessing Hugo blog content",
    version="0.1.0",
)

# Custom JSON response class to ensure UTF-8 encoding
class UTF8JSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")

# Set default response class
app.default_response_class = UTF8JSONResponse

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "MapleFlow Blog API",
        "version": "0.1.0",
        "endpoints": {
            "posts": "/api/posts",
            "post_by_slug": "/api/posts/{slug}",
            "health": "/health",
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/posts", response_model=BlogPostList)
async def get_posts(
    include_drafts: bool = Query(False, description="Include draft posts"),
    limit: Optional[int] = Query(None, description="Limit number of posts"),
    offset: int = Query(0, description="Offset for pagination"),
):
    """
    Get all blog posts.
    
    Args:
        include_drafts: Whether to include draft posts
        limit: Maximum number of posts to return
        offset: Number of posts to skip
        
    Returns:
        BlogPostList with posts and total count
    """
    posts = get_all_blog_posts(include_drafts=include_drafts)
    total = len(posts)
    
    # Apply pagination
    if offset > 0:
        posts = posts[offset:]
    if limit:
        posts = posts[:limit]
    
    return BlogPostList(posts=posts, total=total)


@app.get("/api/posts/search")
async def search_posts(
    q: str = Query(..., description="Search query"),
    include_drafts: bool = Query(False, description="Include draft posts"),
):
    """
    Search blog posts by title, content, tags, or categories.
    
    Args:
        q: Search query string
        include_drafts: Whether to include draft posts
        
    Returns:
        List of matching BlogPost objects
    """
    posts = get_all_blog_posts(include_drafts=include_drafts)
    query_lower = q.lower()
    
    matching_posts = []
    for post in posts:
        # Search in title
        if query_lower in post.front_matter.title.lower():
            matching_posts.append(post)
            continue
        
        # Search in content
        if query_lower in post.content.lower():
            matching_posts.append(post)
            continue
        
        # Search in tags
        if any(query_lower in tag.lower() for tag in post.front_matter.tags):
            matching_posts.append(post)
            continue
        
        # Search in categories
        if any(query_lower in cat.lower() for cat in post.front_matter.categories):
            matching_posts.append(post)
            continue
    
    return BlogPostList(posts=matching_posts, total=len(matching_posts))


@app.get("/api/posts/{slug}", response_model=BlogPost)
async def get_post(slug: str):
    """
    Get a single blog post by slug.
    
    Args:
        slug: The slug (filename without extension) of the post
        
    Returns:
        BlogPost object
    """
    post = get_blog_post_by_slug(slug)
    if not post:
        raise HTTPException(status_code=404, detail=f"Post '{slug}' not found")
    return post


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
