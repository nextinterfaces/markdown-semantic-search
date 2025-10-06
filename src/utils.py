#!/usr/bin/env python3
"""
Utility Functions - File type detection, formatting, and other utilities
"""

import os
from typing import Optional


def is_markdown_file(filename: str, markdown_extensions: set = None) -> bool:
    """Check if file is a markdown file (.md or .mdx)"""
    if markdown_extensions is None:
        markdown_extensions = {'.md', '.mdx'}
    return any(filename.lower().endswith(ext) for ext in markdown_extensions)


def get_file_type(filename: str) -> str:
    """Get file type based on extension"""
    if '.' not in filename:
        return "File"

    ext = filename.split('.')[-1].lower()
    file_types = {
        'md': 'Markdown',
        'mdx': 'MDX Markdown',
        'txt': 'Text File',
        'py': 'Python',
        'js': 'JavaScript',
        'html': 'HTML',
        'css': 'CSS',
        'json': 'JSON',
        'xml': 'XML'
    }

    return file_types.get(ext, f'{ext.upper()} File')


def format_file_size(size_bytes: Optional[int]) -> str:
    """Format file size in human readable format"""
    if size_bytes is None:
        return ""

    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f} {size_names[i]}"


def validate_directory(directory_path: str) -> bool:
    """Check if a directory exists and is accessible"""
    return os.path.exists(directory_path) and os.path.isdir(directory_path)


def get_safe_filename(filename: str) -> str:
    """Get a safe version of filename for display"""
    return os.path.basename(filename) if filename else "Unknown"
