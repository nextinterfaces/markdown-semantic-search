#!/usr/bin/env python3
"""
Markdown Explorer - A desktop application for browsing markdown files with semantic search
"""

try:
    # When run as a module (python -m src.main or import src.main)
    from .semantic_search import SemanticSearchManager
    from .file_system import FileSystemManager
    from .utils import format_file_size
    from .app import create_app, start_app
except ImportError:
    # When run as a script (python src/main.py)
    from semantic_search import SemanticSearchManager
    from file_system import FileSystemManager
    from utils import format_file_size
    from app import create_app, start_app


class FileAPI:
    """Backend API for the markdown explorer application"""

    def __init__(self):
        # Initialize file system manager
        self.file_system = FileSystemManager()

        # Initialize semantic search manager lazily
        self.semantic_search = None
        self._semantic_search_initialized = False
        print("Markdown Explorer started - semantic search will be initialized on first use")
    
    def get_files(self):
        """Get all files and directories in tree structure, filtering for markdown files"""
        return self.file_system.get_files()

    def expand_directory(self, directory_path):
        """Get children of a specific directory for dynamic expansion"""
        return self.file_system.expand_directory(directory_path)

    def get_current_directory(self):
        """Get current directory path"""
        return self.file_system.get_current_directory()

    def get_file_content(self, file_path):
        """Read the content of a markdown file"""
        return self.file_system.get_file_content(file_path)

    def format_file_size(self, size_bytes):
        """Format file size in human readable format"""
        return format_file_size(size_bytes)
    
    def _initialize_semantic_search(self):
        """Initialize semantic search manager with error handling (lazy loading)"""
        if self._semantic_search_initialized:
            return
        
        try:
            print("Initializing semantic search (this may take a few seconds)...")
            self.semantic_search = SemanticSearchManager()
            self._semantic_search_initialized = True
            print("Semantic search initialized successfully")
        except Exception as e:
            print(f"Warning: Failed to initialize semantic search: {e}")
            print("Semantic search features will be disabled")
            self.semantic_search = None
            self._semantic_search_initialized = True  # Don't try again
    
    def is_semantic_search_available(self):
        """Check if semantic search is available (initializes on first check)"""
        if not self._semantic_search_initialized:
            self._initialize_semantic_search()
        return self.semantic_search is not None
    
    def get_all_markdown_files(self):
        """Get list of all markdown files in the current directory tree"""
        return self.file_system.get_all_markdown_files()
    
    def build_semantic_index(self):
        """Build or rebuild the semantic search index"""
        if not self._semantic_search_initialized:
            self._initialize_semantic_search()
            
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
        if not self._semantic_search_initialized:
            self._initialize_semantic_search()
            
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
        if not self._semantic_search_initialized:
            self._initialize_semantic_search()
            
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
        if not self._semantic_search_initialized:
            self._initialize_semantic_search()
            
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


def main():
    """Main entry point for the application"""
    # Create the API instance
    api = FileAPI()

    # Create and start the application
    window = create_app(api)
    start_app(window, debug=False)


if __name__ == "__main__":
    main()
