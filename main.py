#!/usr/bin/env python3
"""
File Explorer - A simple desktop file listing application using pywebview
"""

import webview
import os
import stat
from datetime import datetime
from semantic_search import SemanticSearchManager


class FileAPI:
    """Backend API for the file explorer application"""
    
    def __init__(self):
        self.current_directory = os.getcwd()
        self.markdown_extensions = {'.md', '.mdx'}
        # Initialize semantic search manager
        self.semantic_search = None
        self._initialize_semantic_search()
    
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
    
    def get_file_content(self, file_path):
        """Read the content of a markdown file"""
        try:
            if not self._is_markdown_file(os.path.basename(file_path)):
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
    
    def _initialize_semantic_search(self):
        """Initialize semantic search manager with error handling"""
        try:
            self.semantic_search = SemanticSearchManager()
            print("Semantic search initialized successfully")
        except Exception as e:
            print(f"Warning: Failed to initialize semantic search: {e}")
            print("Semantic search features will be disabled")
            self.semantic_search = None
    
    def is_semantic_search_available(self):
        """Check if semantic search is available"""
        return self.semantic_search is not None
    
    def get_all_markdown_files(self):
        """Get list of all markdown files in the current directory tree"""
        markdown_files = []
        
        try:
            for root, dirs, files in os.walk(self.current_directory):
                # Skip hidden directories
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    if self._is_markdown_file(file):
                        file_path = os.path.join(root, file)
                        markdown_files.append(file_path)
                        
        except (OSError, PermissionError) as e:
            print(f"Error scanning for markdown files: {e}")
            
        return markdown_files
    
    def build_semantic_index(self):
        """Build or rebuild the semantic search index"""
        if not self.semantic_search:
            return {
                "success": False,
                "error": "Semantic search not available"
            }
        
        try:
            # Get all markdown files
            markdown_files = self.get_all_markdown_files()
            
            if not markdown_files:
                return {
                    "success": False,
                    "error": "No markdown files found to index"
                }
            
            # Build the index
            results = self.semantic_search.build_index(markdown_files)
            
            return {
                "success": True,
                "results": results
            }
            
        except Exception as e:
            error_msg = f"Error building semantic index: {str(e)}"
            print(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def semantic_search_query(self, query, top_k=10):
        """Perform semantic search on indexed content"""
        if not self.semantic_search:
            return {
                "success": False,
                "error": "Semantic search not available"
            }
        
        if not query or not query.strip():
            return {
                "success": False,
                "error": "Empty search query"
            }
        
        try:
            results = self.semantic_search.semantic_search(query.strip(), top_k)
            
            # Format results for frontend
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "file_path": result["file_path"],
                    "file_name": result["file_name"],
                    "content_preview": result["content"][:200] + "..." if len(result["content"]) > 200 else result["content"],
                    "full_content": result["content"],
                    "similarity": result["similarity"],
                    "chunk_index": result["chunk_index"],
                    "modified_time": result["modified_time"]
                })
            
            return {
                "success": True,
                "results": formatted_results,
                "query": query,
                "total_results": len(formatted_results)
            }
            
        except Exception as e:
            error_msg = f"Error performing semantic search: {str(e)}"
            print(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def get_semantic_search_stats(self):
        """Get statistics about the semantic search index"""
        if not self.semantic_search:
            return {
                "success": False,
                "error": "Semantic search not available"
            }
        
        try:
            stats = self.semantic_search.get_stats()
            return {
                "success": True,
                "stats": stats
            }
        except Exception as e:
            error_msg = f"Error getting semantic search stats: {str(e)}"
            print(error_msg)
            return {
                "success": False,
                "error": error_msg
            }
    
    def refresh_semantic_index(self):
        """Refresh the semantic search index with any new or changed files"""
        if not self.semantic_search:
            return {
                "success": False,
                "error": "Semantic search not available"
            }
        
        try:
            # Get all current markdown files
            current_files = self.get_all_markdown_files()
            
            # Re-process all files (the semantic search manager handles change detection)
            results = self.semantic_search.build_index(current_files)
            
            return {
                "success": True,
                "message": "Semantic index refreshed successfully",
                "results": results
            }
            
        except Exception as e:
            error_msg = f"Error refreshing semantic index: {str(e)}"
            print(error_msg)
            return {
                "success": False,
                "error": error_msg
            }


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
