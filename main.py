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
    
    def get_files(self):
        """Get all files and directories in the current folder"""
        try:
            files = []
            for item in os.listdir(self.current_directory):
                item_path = os.path.join(self.current_directory, item)
                
                try:
                    item_stat = os.stat(item_path)
                    is_dir = os.path.isdir(item_path)
                    
                    file_info = {
                        "name": item,
                        "path": item_path,
                        "is_directory": is_dir,
                        "size": item_stat.st_size if not is_dir else None,
                        "modified": datetime.fromtimestamp(item_stat.st_mtime).isoformat(),
                        "permissions": stat.filemode(item_stat.st_mode),
                        "type": "Directory" if is_dir else self.get_file_type(item)
                    }
                    files.append(file_info)
                except (OSError, PermissionError) as e:
                    # Skip files that can't be accessed
                    continue
            
            # Sort: directories first, then files, both alphabetically
            files.sort(key=lambda x: (not x["is_directory"], x["name"].lower()))
            return files
            
        except Exception as e:
            print(f"Error listing files: {e}")
            return []
    
    def get_file_type(self, filename):
        """Get file type based on extension"""
        if '.' not in filename:
            return "File"
        
        ext = filename.split('.')[-1].lower()
        file_types = {
            'txt': 'Text File',
            'md': 'Markdown',
            'py': 'Python',
            'js': 'JavaScript',
            'html': 'HTML',
            'css': 'CSS',
            'json': 'JSON',
            'xml': 'XML',
            'pdf': 'PDF',
            'doc': 'Word Document',
            'docx': 'Word Document',
            'xls': 'Excel',
            'xlsx': 'Excel',
            'ppt': 'PowerPoint',
            'pptx': 'PowerPoint',
            'jpg': 'Image',
            'jpeg': 'Image',
            'png': 'Image',
            'gif': 'Image',
            'svg': 'SVG Image',
            'mp4': 'Video',
            'avi': 'Video',
            'mov': 'Video',
            'mp3': 'Audio',
            'wav': 'Audio',
            'zip': 'Archive',
            'tar': 'Archive',
            'gz': 'Archive',
            'exe': 'Executable',
            'app': 'Application'
        }
        
        return file_types.get(ext, f'{ext.upper()} File')
    
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
        title="File Explorer",
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
    
    # Start the webview
    webview.start(debug=True)


if __name__ == "__main__":
    main()
