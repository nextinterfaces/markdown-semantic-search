#!/usr/bin/env python3
"""
File Explorer - A simple desktop file listing application using pywebview
"""

import webview
import os
import stat
from datetime import datetime


class FileAPI:
    """Backend API for the file explorer application"""
    
    def __init__(self):
        self.current_directory = os.getcwd()
        self.markdown_extensions = {'.md', '.mdx'}
    
    def get_files(self):
        """Get all files and directories in tree structure, filtering for markdown files"""
        try:
            return self._build_tree(self.current_directory)
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    def _build_tree(self, directory_path, level=0):
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
                        if self._is_markdown_file(item):
                            tree_item = {
                                "name": item,
                                "path": item_path,
                                "is_directory": False,
                                "size": item_stat.st_size,
                                "modified": datetime.fromtimestamp(item_stat.st_mtime).isoformat(),
                                "permissions": stat.filemode(item_stat.st_mode),
                                "type": self.get_file_type(item),
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
    
    def _has_markdown_files(self, directory_path):
        """Check if directory or its subdirectories contain markdown files"""
        try:
            for root, dirs, files in os.walk(directory_path):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if self._is_markdown_file(file):
                        return True
                        
                # Limit depth for performance
                current_depth = root[len(directory_path):].count(os.sep)
                if current_depth >= 5:
                    dirs.clear()
                    
            return False
        except (OSError, PermissionError):
            return False
    
    def _is_markdown_file(self, filename):
        """Check if file is a markdown file (.md or .mdx)"""
        return any(filename.lower().endswith(ext) for ext in self.markdown_extensions)
    
    def get_file_type(self, filename):
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
    
    def expand_directory(self, directory_path):
        """Get children of a specific directory for dynamic expansion"""
        try:
            return self._build_tree(directory_path, 0)
        except Exception as e:
            print(f"Error expanding directory {directory_path}: {e}")
            return []
    
    def get_current_directory(self):
        """Get current directory path"""
        return self.current_directory
    
    def format_file_size(self, size_bytes):
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


def create_app():
    """Create and configure the webview application"""
    api = FileAPI()
    
    # Create the webview window
    window = webview.create_window(
        title="Markdown Explorer",
        url="web/index.html",
        js_api=api,
        width=1200,
        height=800,
        min_size=(900, 600),
        resizable=True,
        maximized=False,
        on_top=False,
        shadow=True
    )
    
    return window


def main():
    """Main entry point for the application"""
    # Create the application
    window = create_app()
    
    # Start the webview (debug=False hides dev tools by default, but keeps them accessible)
    webview.start(debug=False)


if __name__ == "__main__":
    main()
