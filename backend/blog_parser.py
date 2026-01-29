"""Parser for Hugo blog posts (Markdown with TOML front matter)."""
import re
import os
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from datetime import datetime
import tomli

from backend.models import BlogPost, BlogPostFrontMatter
from backend.config import settings


def parse_front_matter(content: str) -> Tuple[Dict, str]:
    """
    Parse TOML front matter from Hugo markdown file.
    
    Returns:
        tuple: (front_matter_dict, markdown_content)
    """
    # Match TOML front matter (+++ ... +++ or --- ... ---)
    pattern = r'^(\+\+\+|\-\-\-)\s*\n(.*?)\n\1\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)
    
    if match:
        front_matter_str = match.group(2)
        markdown_content = match.group(3)
        
        try:
            front_matter = tomli.loads(front_matter_str)
            return front_matter, markdown_content
        except Exception as e:
            print(f"Error parsing front matter: {e}")
            return {}, content
    else:
        # No front matter found
        return {}, content


def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime object."""
    # Try ISO format first
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except:
        pass
    
    # Try other common formats
    formats = [
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    
    # Default to now if parsing fails
    return datetime.now()


def load_blog_post(file_path: Path) -> Optional[BlogPost]:
    """Load and parse a single blog post file."""
    try:
        content = file_path.read_text(encoding='utf-8')
        front_matter_dict, markdown_content = parse_front_matter(content)
        
        # Extract front matter fields
        front_matter = BlogPostFrontMatter(
            title=front_matter_dict.get('title', 'Untitled'),
            date=parse_date(front_matter_dict.get('date', datetime.now().isoformat())),
            draft=front_matter_dict.get('draft', True),
            categories=front_matter_dict.get('categories', []),
            tags=front_matter_dict.get('tags', []),
        )
        
        # Generate slug from filename
        slug = file_path.stem
        
        return BlogPost(
            front_matter=front_matter,
            content=markdown_content,
            filename=file_path.name,
            slug=slug,
        )
    except Exception as e:
        print(f"Error loading blog post {file_path}: {e}")
        return None


def get_all_blog_posts(include_drafts: bool = False) -> List[BlogPost]:
    """
    Load all blog posts from the content directory.
    
    Args:
        include_drafts: Whether to include draft posts
        
    Returns:
        List of BlogPost objects
    """
    content_path = Path(settings.blog_content_path)
    
    if not content_path.exists():
        return []
    
    posts = []
    for md_file in content_path.glob("*.md"):
        post = load_blog_post(md_file)
        if post:
            if not include_drafts and post.front_matter.draft:
                continue
            posts.append(post)
    
    # Sort by date (newest first)
    posts.sort(key=lambda x: x.front_matter.date, reverse=True)
    
    return posts


def get_blog_post_by_slug(slug: str) -> Optional[BlogPost]:
    """Get a single blog post by its slug (filename without extension)."""
    content_path = Path(settings.blog_content_path)
    file_path = content_path / f"{slug}.md"
    
    if file_path.exists():
        return load_blog_post(file_path)
    return None
