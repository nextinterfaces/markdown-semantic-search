#!/usr/bin/env python3
"""
File System Operations - Handles file scanning, tree building, and file reading
"""

import os
import stat
from datetime import datetime
from typing import List, Dict, Any, Optional
try:
    # When run as a module
    from .utils import is_markdown_file, get_file_type
except ImportError:
    # When run as a script
    from utils import is_markdown_file, get_file_type


class FileSystemManager:
    """Manages file system operations for the markdown explorer"""

    def __init__(self, current_directory: Optional[str] = None):
        self.current_directory = current_directory or os.getcwd()
        self.markdown_extensions = {'.md', '.mdx'}

    def get_files(self) -> List[Dict[str, Any]]:
        """Get all files and directories in tree structure, filtering for markdown files"""
        try:
            return self._build_tree(self.current_directory)
        except Exception as e:
            print(f"Error listing files: {e}")
            return []

    def _build_tree(self, directory_path: str, level: int = 0) -> List[Dict[str, Any]]:
        """Recursively build tree structure with markdown files"""
        tree_items = []

        try:
            # Limit depth to prevent infinite recursion and improve performance
            if level > 5:
                return tree_items

            items = os.listdir(directory_path)
            items.sort()

            for item in items:
                # Skip hidden files and directories
                if item.startswith('.'):
                    continue

                item_path = os.path.join(directory_path, item)

                try:
                    item_stat = os.stat(item_path)
                    is_dir = os.path.isdir(item_path)

                    if is_dir:
                        # Check if directory contains any markdown files (recursively)
                        if self._has_markdown_files(item_path):
                            children = self._build_tree(item_path, level + 1)
                            tree_item = {
                                "name": item,
                                "path": item_path,
                                "is_directory": True,
                                "modified": datetime.fromtimestamp(item_stat.st_mtime).isoformat(),
                                "permissions": stat.filemode(item_stat.st_mode),
                                "type": "Directory",
                                "children": children,
                                "expanded": False,
                                "level": level,
                                "has_children": len(children) > 0
                            }
                            tree_items.append(tree_item)
                    else:
                        # Only include markdown files
                        if is_markdown_file(item, self.markdown_extensions):
                            tree_item = {
                                "name": item,
                                "path": item_path,
                                "is_directory": False,
                                "size": item_stat.st_size,
                                "modified": datetime.fromtimestamp(item_stat.st_mtime).isoformat(),
                                "permissions": stat.filemode(item_stat.st_mode),
                                "type": get_file_type(item),
                                "level": level,
                                "has_children": False
                            }
                            tree_items.append(tree_item)

                except (OSError, PermissionError):
                    # Skip files that can't be accessed
                    continue

        except (OSError, PermissionError):
            # Skip directories that can't be accessed
            pass

        return tree_items

    def _has_markdown_files(self, directory_path: str) -> bool:
        """Check if directory or its subdirectories contain markdown files"""
        try:
            for root, dirs, files in os.walk(directory_path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]

                for file in files:
                    if is_markdown_file(file, self.markdown_extensions):
                        return True

                # Limit depth for performance
                current_depth = root[len(directory_path):].count(os.sep)
                if current_depth >= 5:
                    dirs.clear()

            return False
        except (OSError, PermissionError):
            return False

    def expand_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """Get children of a specific directory for dynamic expansion"""
        try:
            return self._build_tree(directory_path, 0)
        except Exception as e:
            print(f"Error expanding directory {directory_path}: {e}")
            return []

    def get_current_directory(self) -> str:
        """Get current directory path"""
        return self.current_directory

    def get_file_content(self, file_path: str) -> Dict[str, Any]:
        """Read the content of a markdown file"""
        try:
            if not is_markdown_file(os.path.basename(file_path), self.markdown_extensions):
                return {"success": False, "error": "Not a markdown file"}

            if not os.path.exists(file_path):
                return {"success": False, "error": "File not found"}

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            return {
                "success": True,
                "content": content,
                "filename": os.path.basename(file_path),
                "path": file_path
            }
        except Exception as e:
            return {"success": False, "error": f"Error reading file: {str(e)}"}

    def get_all_markdown_files(self) -> List[str]:
        """Get list of all markdown files in the current directory tree"""
        markdown_files = []

        try:
            for root, dirs, files in os.walk(self.current_directory):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]

                for file in files:
                    if is_markdown_file(file, self.markdown_extensions):
                        file_path = os.path.join(root, file)
                        markdown_files.append(file_path)

        except (OSError, PermissionError) as e:
            print(f"Error scanning for markdown files: {e}")

        return markdown_files

    def set_current_directory(self, new_directory: str):
        """Change the current working directory"""
        if os.path.exists(new_directory) and os.path.isdir(new_directory):
            self.current_directory = new_directory
        else:
            raise ValueError(f"Directory does not exist: {new_directory}")
