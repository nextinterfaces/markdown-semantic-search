// File Explorer Frontend JavaScript

class FileExplorer {
    constructor() {
        this.files = [];
        this.filteredFiles = [];
        this.currentDirectory = '';
        
        this.initializeElements();
        this.bindEvents();
        this.loadFiles();
    }
    
    initializeElements() {
        // Get DOM elements
        this.filesList = document.getElementById('filesList');
        this.emptyState = document.getElementById('emptyState');
        this.welcomeScreen = document.getElementById('welcomeScreen');
        this.fileInfo = document.getElementById('fileInfo');
        this.searchInput = document.getElementById('searchInput');
        this.refreshBtn = document.getElementById('refreshBtn');
        this.toast = document.getElementById('toast');
    }
    
    bindEvents() {
        // Button events
        this.refreshBtn.addEventListener('click', () => this.refreshFiles());
        
        // Search functionality
        this.searchInput.addEventListener('input', (e) => this.filterFiles(e.target.value));
    }
    
    async loadFiles() {
        try {
            this.files = await pywebview.api.get_files();
            this.currentDirectory = await pywebview.api.get_current_directory();
            this.filteredFiles = [...this.files];
            this.renderFilesList();
            this.updateCurrentDirectory();
        } catch (error) {
            console.error('Error loading files:', error);
            this.showToast('Error loading files', 'error');
        }
    }
    
    updateCurrentDirectory() {
        const currentDirElement = document.getElementById('currentDir');
        if (currentDirElement) {
            currentDirElement.textContent = `Current directory: ${this.currentDirectory}`;
        }
    }
    
    async refreshFiles() {
        await this.loadFiles();
        this.showToast('Files refreshed');
    }
    
    filterFiles(query) {
        if (!query.trim()) {
            this.filteredFiles = [...this.files];
        } else {
            const searchQuery = query.toLowerCase();
            this.filteredFiles = this.files.filter(file => 
                file.name.toLowerCase().includes(searchQuery) ||
                file.type.toLowerCase().includes(searchQuery)
            );
        }
        this.renderFilesList();
    }
    
    renderFilesList() {
        const files = this.filteredFiles;
        
        if (files.length === 0) {
            this.filesList.innerHTML = '';
            this.filesList.appendChild(this.emptyState);
            this.showWelcomeScreen();
            return;
        }
        
        this.emptyState.style.display = 'none';
        
        const filesHTML = files.map(file => this.createFileItemHTML(file)).join('');
        this.filesList.innerHTML = filesHTML;
        
        // Add click events to file items
        this.filesList.querySelectorAll('.file-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const fileName = e.currentTarget.dataset.fileName;
                this.selectFile(fileName);
            });
        });
    }
    
    createFileItemHTML(file) {
        const date = new Date(file.modified).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        const size = file.is_directory ? '' : this.formatFileSize(file.size);
        const icon = this.getFileIcon(file);
        
        return `
            <div class="file-item" data-file-name="${this.escapeHtml(file.name)}">
                <div class="file-icon">${icon}</div>
                <div class="file-details">
                    <div class="file-name">${this.escapeHtml(file.name)}</div>
                    <div class="file-info">
                        <span class="file-type">${this.escapeHtml(file.type)}</span>
                        ${size ? `<span class="file-size">${size}</span>` : ''}
                        <span class="file-date">${date}</span>
                    </div>
                </div>
                <div class="file-permissions">${this.escapeHtml(file.permissions)}</div>
            </div>
        `;
    }
    
    getFileIcon(file) {
        if (file.is_directory) {
            return '<i class="fas fa-folder"></i>';
        }
        
        const ext = file.name.split('.').pop().toLowerCase();
        const iconMap = {
            'txt': 'fas fa-file-alt',
            'md': 'fab fa-markdown',
            'py': 'fab fa-python',
            'js': 'fab fa-js-square',
            'html': 'fab fa-html5',
            'css': 'fab fa-css3-alt',
            'json': 'fas fa-file-code',
            'xml': 'fas fa-file-code',
            'pdf': 'fas fa-file-pdf',
            'doc': 'fas fa-file-word',
            'docx': 'fas fa-file-word',
            'xls': 'fas fa-file-excel',
            'xlsx': 'fas fa-file-excel',
            'ppt': 'fas fa-file-powerpoint',
            'pptx': 'fas fa-file-powerpoint',
            'jpg': 'fas fa-file-image',
            'jpeg': 'fas fa-file-image',
            'png': 'fas fa-file-image',
            'gif': 'fas fa-file-image',
            'svg': 'fas fa-file-image',
            'mp4': 'fas fa-file-video',
            'avi': 'fas fa-file-video',
            'mov': 'fas fa-file-video',
            'mp3': 'fas fa-file-audio',
            'wav': 'fas fa-file-audio',
            'zip': 'fas fa-file-archive',
            'tar': 'fas fa-file-archive',
            'gz': 'fas fa-file-archive'
        };
        
        return `<i class="${iconMap[ext] || 'fas fa-file'}"></i>`;
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    selectFile(fileName) {
        const file = this.files.find(f => f.name === fileName);
        if (!file) return;
        
        this.showFileInfo(file);
    }
    
    showFileInfo(file) {
        const fileInfoHTML = `
            <div class="file-info-header">
                <div class="file-icon-large">${this.getFileIcon(file)}</div>
                <div class="file-name-large">${this.escapeHtml(file.name)}</div>
            </div>
            <div class="file-properties">
                <div class="property">
                    <span class="label">Type:</span>
                    <span class="value">${this.escapeHtml(file.type)}</span>
                </div>
                <div class="property">
                    <span class="label">Size:</span>
                    <span class="value">${file.is_directory ? 'Directory' : this.formatFileSize(file.size)}</span>
                </div>
                <div class="property">
                    <span class="label">Modified:</span>
                    <span class="value">${new Date(file.modified).toLocaleString()}</span>
                </div>
                <div class="property">
                    <span class="label">Permissions:</span>
                    <span class="value">${this.escapeHtml(file.permissions)}</span>
                </div>
                <div class="property">
                    <span class="label">Path:</span>
                    <span class="value">${this.escapeHtml(file.path)}</span>
                </div>
            </div>
        `;
        
        document.getElementById('fileInfoContent').innerHTML = fileInfoHTML;
        this.showFileInfoPanel();
    }
    
    showWelcomeScreen() {
        this.welcomeScreen.style.display = 'flex';
        this.fileInfo.style.display = 'none';
    }
    
    showFileInfoPanel() {
        this.welcomeScreen.style.display = 'none';
        this.fileInfo.style.display = 'flex';
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
            new FileExplorer();
        } else {
            setTimeout(initApp, 100);
        }
    };
    
    initApp();
});

// Handle keyboard shortcuts
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + R for refresh
    if ((e.ctrlKey || e.metaKey) && e.key === 'r') {
        e.preventDefault();
        document.getElementById('refreshBtn').click();
    }
    
    // Ctrl/Cmd + F for search
    if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
        e.preventDefault();
        document.getElementById('searchInput').focus();
    }
    
    // F5 for refresh
    if (e.key === 'F5') {
        e.preventDefault();
        document.getElementById('refreshBtn').click();
    }
});
