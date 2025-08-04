"""
Validation utilities
"""
import re
from typing import Dict, List
import requests


def validate_github_url(url: str) -> Dict[str, any]:
    """Validate GitHub repository URL"""
    if not url:
        return {"valid": False, "error": "URL cannot be empty"}
    
    # Check basic format
    github_pattern = r'^https://github\.com/[\w\-\.]+/[\w\-\.]+/?$'
    if not re.match(github_pattern, url):
        return {
            "valid": False, 
            "error": "Invalid GitHub URL format. Use: https://github.com/username/repository"
        }
    
    return {"valid": True}


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe filesystem usage"""
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove multiple underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Remove leading/trailing underscores and dots
    sanitized = sanitized.strip('_.')
    
    return sanitized or "untitled"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def extract_repo_name(github_url: str) -> str:
    """Extract repository name from GitHub URL"""
    try:
        # Remove trailing slash and .git
        url = github_url.rstrip('/').replace('.git', '')
        # Split and get last part
        return url.split('/')[-1]
    except:
        return "unknown-repo"


def validate_env_var_name(name: str) -> Dict[str, any]:
    """Validate environment variable name"""
    if not name:
        return {"valid": False, "error": "Variable name cannot be empty"}
    
    if not re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', name):
        return {
            "valid": False,
            "error": "Variable name must start with letter or underscore and contain only letters, numbers, and underscores"
        }
    
    return {"valid": True}


def get_file_icon(filename: str) -> str:
    """Get appropriate icon for file type"""
    ext = filename.lower().split('.')[-1] if '.' in filename else ''
    
    icons = {
        'py': '🐍',
        'js': '📜', 
        'json': '📋',
        'txt': '📄',
        'md': '📝',
        'yml': '⚙️',
        'yaml': '⚙️',
        'env': '🔐',
        'requirements': '📦'
    }
    
    if 'requirements' in filename.lower():
        return '📦'
    
    return icons.get(ext, '📄')


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + "..."


def format_duration(seconds: int) -> str:
    """Format duration in human readable format"""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
