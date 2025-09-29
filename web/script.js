// MyNotes Frontend JavaScript

class NotesApp {
    constructor() {
        this.currentNote = null;
        this.notes = [];
        this.isEditing = false;
        
        this.initializeElements();
        this.bindEvents();
        this.loadNotes();
    }
    
    initializeElements() {
        // Get DOM elements
        this.notesList = document.getElementById('notesList');
        this.emptyState = document.getElementById('emptyState');
        this.welcomeScreen = document.getElementById('welcomeScreen');
        this.noteEditor = document.getElementById('noteEditor');
        this.noteTitle = document.getElementById('noteTitle');
        this.noteContent = document.getElementById('noteContent');
        this.searchInput = document.getElementById('searchInput');
        this.newNoteBtn = document.getElementById('newNoteBtn');
        this.saveNoteBtn = document.getElementById('saveNoteBtn');
        this.deleteNoteBtn = document.getElementById('deleteNoteBtn');
        this.toast = document.getElementById('toast');
    }
    
    bindEvents() {
        // Button events
        this.newNoteBtn.addEventListener('click', () => this.createNewNote());
        this.saveNoteBtn.addEventListener('click', () => this.saveCurrentNote());
        this.deleteNoteBtn.addEventListener('click', () => this.deleteCurrentNote());
        
        // Search functionality
        this.searchInput.addEventListener('input', (e) => this.searchNotes(e.target.value));
        
        // Auto-save on content change (with debounce)
        let saveTimeout;
        const autoSave = () => {
            if (this.currentNote && this.isEditing) {
                clearTimeout(saveTimeout);
                saveTimeout = setTimeout(() => this.saveCurrentNote(true), 2000);
            }
        };
        
        this.noteTitle.addEventListener('input', autoSave);
        this.noteContent.addEventListener('input', autoSave);
        
        // Mark as editing when user starts typing
        this.noteTitle.addEventListener('input', () => this.isEditing = true);
        this.noteContent.addEventListener('input', () => this.isEditing = true);
    }
    
    async loadNotes() {
        try {
            this.notes = await pywebview.api.get_notes();
            this.renderNotesList();
        } catch (error) {
            console.error('Error loading notes:', error);
            this.showToast('Error loading notes', 'error');
        }
    }
    
    renderNotesList(notesToRender = null) {
        const notes = notesToRender || this.notes;
        
        if (notes.length === 0) {
            this.notesList.innerHTML = '';
            this.notesList.appendChild(this.emptyState);
            this.showWelcomeScreen();
            return;
        }
        
        this.emptyState.style.display = 'none';
        
        const notesHTML = notes.map(note => this.createNoteItemHTML(note)).join('');
        this.notesList.innerHTML = notesHTML;
        
        // Add click events to note items
        this.notesList.querySelectorAll('.note-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const noteId = parseInt(e.currentTarget.dataset.noteId);
                this.selectNote(noteId);
            });
        });
    }
    
    createNoteItemHTML(note) {
        const preview = note.content.substring(0, 100) + (note.content.length > 100 ? '...' : '');
        const date = new Date(note.created_at).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
        
        return `
            <div class="note-item ${this.currentNote && this.currentNote.id === note.id ? 'active' : ''}" 
                 data-note-id="${note.id}">
                <div class="note-title">${this.escapeHtml(note.title)}</div>
                <div class="note-preview">${this.escapeHtml(preview)}</div>
                <div class="note-date">${date}</div>
            </div>
        `;
    }
    
    selectNote(noteId) {
        const note = this.notes.find(n => n.id === noteId);
        if (!note) return;
        
        this.currentNote = note;
        this.isEditing = false;
        
        // Update UI
        this.noteTitle.value = note.title;
        this.noteContent.value = note.content;
        
        this.showNoteEditor();
        this.updateActiveNote();
    }
    
    updateActiveNote() {
        this.notesList.querySelectorAll('.note-item').forEach(item => {
            item.classList.remove('active');
            if (this.currentNote && parseInt(item.dataset.noteId) === this.currentNote.id) {
                item.classList.add('active');
            }
        });
    }
    
    async createNewNote() {
        const title = 'Untitled Note';
        const content = '';
        
        try {
            const response = await pywebview.api.add_note(title, content);
            
            if (response.success) {
                this.notes.unshift(response.note);
                this.currentNote = response.note;
                this.isEditing = true;
                
                this.noteTitle.value = title;
                this.noteContent.value = content;
                
                this.renderNotesList();
                this.showNoteEditor();
                this.noteTitle.focus();
                this.noteTitle.select();
                
                this.showToast('New note created');
            } else {
                this.showToast(response.error || 'Failed to create note', 'error');
            }
        } catch (error) {
            console.error('Error creating note:', error);
            this.showToast('Error creating note', 'error');
        }
    }
    
    async saveCurrentNote(isAutoSave = false) {
        if (!this.currentNote) return;
        
        const title = this.noteTitle.value.trim() || 'Untitled Note';
        const content = this.noteContent.value;
        
        try {
            const response = await pywebview.api.update_note(this.currentNote.id, title, content);
            
            if (response.success) {
                // Update the note in our local array
                const noteIndex = this.notes.findIndex(n => n.id === this.currentNote.id);
                if (noteIndex !== -1) {
                    this.notes[noteIndex] = response.note;
                    this.currentNote = response.note;
                }
                
                this.isEditing = false;
                this.renderNotesList();
                
                if (!isAutoSave) {
                    this.showToast('Note saved');
                }
            } else {
                this.showToast(response.error || 'Failed to save note', 'error');
            }
        } catch (error) {
            console.error('Error saving note:', error);
            this.showToast('Error saving note', 'error');
        }
    }
    
    async deleteCurrentNote() {
        if (!this.currentNote) return;
        
        if (!confirm('Are you sure you want to delete this note? This action cannot be undone.')) {
            return;
        }
        
        try {
            const response = await pywebview.api.delete_note(this.currentNote.id);
            
            if (response.success) {
                // Remove note from local array
                this.notes = this.notes.filter(n => n.id !== this.currentNote.id);
                this.currentNote = null;
                
                this.renderNotesList();
                this.showWelcomeScreen();
                this.showToast('Note deleted');
            } else {
                this.showToast(response.error || 'Failed to delete note', 'error');
            }
        } catch (error) {
            console.error('Error deleting note:', error);
            this.showToast('Error deleting note', 'error');
        }
    }
    
    async searchNotes(query) {
        try {
            const results = await pywebview.api.search_notes(query);
            this.renderNotesList(results);
        } catch (error) {
            console.error('Error searching notes:', error);
            this.showToast('Error searching notes', 'error');
        }
    }
    
    showWelcomeScreen() {
        this.welcomeScreen.style.display = 'flex';
        this.noteEditor.style.display = 'none';
        this.currentNote = null;
    }
    
    showNoteEditor() {
        this.welcomeScreen.style.display = 'none';
        this.noteEditor.style.display = 'flex';
    }
    
    showToast(message, type = 'success') {
        this.toast.textContent = message;
        this.toast.className = `toast ${type}`;
        this.toast.classList.add('show');
        
        setTimeout(() => {
            this.toast.classList.remove('show');
        }, 3000);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the app when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Wait for pywebview API to be available
    const initApp = () => {
        if (window.pywebview && window.pywebview.api) {
            new NotesApp();
        } else {
            setTimeout(initApp, 100);
        }
    };
    
    initApp();
});

// Handle keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + N for new note
    if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
        e.preventDefault();
        document.getElementById('newNoteBtn').click();
    }
    
    // Ctrl/Cmd + S for save
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        document.getElementById('saveNoteBtn').click();
    }
    
    // Ctrl/Cmd + F for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        document.getElementById('searchInput').focus();
    }
});
