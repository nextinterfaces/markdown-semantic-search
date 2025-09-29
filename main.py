#!/usr/bin/env python3
"""
MyNotes - A simple desktop notes application using pywebview
"""

import webview
import json
import os
from datetime import datetime


class NotesAPI:
    """Backend API for the notes application"""
    
    def __init__(self):
        self.notes_file = "notes.json"
        self.notes = self.load_notes()
    
    def load_notes(self):
        """Load notes from JSON file"""
        if os.path.exists(self.notes_file):
            try:
                with open(self.notes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return []
        return []
    
    def save_notes(self):
        """Save notes to JSON file"""
        try:
            with open(self.notes_file, 'w', encoding='utf-8') as f:
                json.dump(self.notes, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving notes: {e}")
            return False
    
    def get_notes(self):
        """Get all notes"""
        return self.notes
    
    def add_note(self, title, content):
        """Add a new note"""
        if not title.strip():
            return {"success": False, "error": "Title cannot be empty"}
        
        note = {
            "id": len(self.notes) + 1,
            "title": title.strip(),
            "content": content.strip(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self.notes.append(note)
        if self.save_notes():
            return {"success": True, "note": note}
        else:
            return {"success": False, "error": "Failed to save note"}
    
    def update_note(self, note_id, title, content):
        """Update an existing note"""
        for note in self.notes:
            if note["id"] == note_id:
                note["title"] = title.strip()
                note["content"] = content.strip()
                note["updated_at"] = datetime.now().isoformat()
                
                if self.save_notes():
                    return {"success": True, "note": note}
                else:
                    return {"success": False, "error": "Failed to save note"}
        
        return {"success": False, "error": "Note not found"}
    
    def delete_note(self, note_id):
        """Delete a note"""
        for i, note in enumerate(self.notes):
            if note["id"] == note_id:
                deleted_note = self.notes.pop(i)
                if self.save_notes():
                    return {"success": True, "note": deleted_note}
                else:
                    return {"success": False, "error": "Failed to save changes"}
        
        return {"success": False, "error": "Note not found"}
    
    def search_notes(self, query):
        """Search notes by title or content"""
        if not query.strip():
            return self.notes
        
        query = query.lower().strip()
        results = []
        
        for note in self.notes:
            if (query in note["title"].lower() or 
                query in note["content"].lower()):
                results.append(note)
        
        return results


def create_app():
    """Create and configure the webview application"""
    api = NotesAPI()
    
    # Create the webview window
    window = webview.create_window(
        title="MyNotes",
        url="web/index.html",
        js_api=api,
        width=1000,
        height=700,
        min_size=(800, 600),
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
