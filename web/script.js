// Markdown Tree Explorer Frontend JavaScript

class MarkdownTreeExplorer {
    constructor() {
        this.treeData = [];
        this.filteredTreeData = [];
        this.currentDirectory = '';
        this.expandedNodes = new Set();
        this.selectedNode = null;
        
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
        this.searchInput.addEventListener('input', (e) => this.filterTree(e.target.value));
    }
    
    async loadFiles() {
        try {
            this.treeData = await pywebview.api.get_files();
            this.currentDirectory = await pywebview.api.get_current_directory();
            this.filteredTreeData = [...this.treeData];
            this.renderTree();
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
        // Clear expanded state to refresh completely
        this.expandedNodes.clear();
        await this.loadFiles();
        this.showToast('Markdown files refreshed');
    }
    
    filterTree(query) {
        if (!query.trim()) {
            this.filteredTreeData = [...this.treeData];
        } else {
            const searchQuery = query.toLowerCase();
            this.filteredTreeData = this._filterTreeRecursive(this.treeData, searchQuery);
        }
        this.renderTree();
    }
    
    _filterTreeRecursive(items, query) {
        return items.filter(item => {
            if (item.is_directory) {
                // For directories, include if name matches OR any children match
                const nameMatches = item.name.toLowerCase().includes(query);
                const childrenMatch = item.children && this._filterTreeRecursive(item.children, query).length > 0;
                
                if (nameMatches || childrenMatch) {
                    // Create a copy with filtered children
                    return {
                        ...item,
                        children: item.children ? this._filterTreeRecursive(item.children, query) : []
                    };
                }
                return false;
            } else {
                // For files, include if name matches
                return item.name.toLowerCase().includes(query);
            }
        }).map(item => {
            if (item.is_directory && item.children) {
                return {
                    ...item,
                    children: this._filterTreeRecursive(item.children, query)
                };
            }
            return item;
        });
    }
    
    renderTree() {
        const treeItems = this.filteredTreeData;
        
        if (treeItems.length === 0) {
            this.filesList.innerHTML = '';
            this.filesList.appendChild(this.emptyState);
            this.showWelcomeScreen();
            return;
        }
        
        this.emptyState.style.display = 'none';
        
        const treeHTML = this._renderTreeItems(treeItems);
        this.filesList.innerHTML = treeHTML;
        
        // Add click events to tree items
        this._attachTreeEvents();
    }
    
    _renderTreeItems(items, level = 0) {
        return items.map(item => this._createTreeItemHTML(item, level)).join('');
    }
    
    _attachTreeEvents() {
        // Toggle directory expansion
        this.filesList.querySelectorAll('.tree-toggle').forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                e.stopPropagation();
                const itemPath = e.currentTarget.dataset.path;
                this.toggleDirectory(itemPath);
            });
        });
        
        // Select file or directory
        this.filesList.querySelectorAll('.tree-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                const itemPath = e.currentTarget.dataset.path;
                const isDirectory = e.currentTarget.dataset.isDirectory === 'true';
                this.selectItem(itemPath, isDirectory);
            });
        });
    }
    
    _createTreeItemHTML(item, level = 0) {
        const indent = level * 20;
        const isExpanded = this.expandedNodes.has(item.path);
        const isSelected = this.selectedNode === item.path;
        const icon = this.getTreeIcon(item);
        
        let html = `
            <div class="tree-item ${isSelected ? 'selected' : ''}" 
                 data-path="${this.escapeHtml(item.path)}"
                 data-is-directory="${item.is_directory}"
                 style="padding-left: ${indent}px;">
                <div class="tree-item-content">
        `;
        
        // Toggle button for directories
        if (item.is_directory) {
            const toggleIcon = isExpanded ? 'fas fa-chevron-down' : 'fas fa-chevron-right';
            html += `
                <button class="tree-toggle" data-path="${this.escapeHtml(item.path)}">
                    <i class="${toggleIcon}"></i>
                </button>
            `;
        } else {
            html += `<span class="tree-spacer"></span>`;
        }
        
        html += `
                    <div class="tree-icon">${icon}</div>
                    <div class="tree-details">
                        <div class="tree-name">${this.escapeHtml(item.name)}</div>
                    </div>
                </div>
            </div>
        `;
        
        // Add children if expanded
        if (item.is_directory && isExpanded && item.children && item.children.length > 0) {
            html += `<div class="tree-children">`;
            html += this._renderTreeItems(item.children, level + 1);
            html += `</div>`;
        }
        
        return html;
    }
    
    getTreeIcon(item) {
        if (item.is_directory) {
            const isExpanded = this.expandedNodes.has(item.path);
            return isExpanded ? '<i class="fas fa-folder-open"></i>' : '<i class="fas fa-folder"></i>';
        }
        
        const ext = item.name.split('.').pop().toLowerCase();
        const iconMap = {
            'md': 'fab fa-markdown',
            'mdx': 'fab fa-markdown'
        };
        
        return `<i class="${iconMap[ext] || 'fab fa-markdown'}"></i>`;
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 B';
        
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
    }
    
    toggleDirectory(dirPath) {
        if (this.expandedNodes.has(dirPath)) {
            this.expandedNodes.delete(dirPath);
        } else {
            this.expandedNodes.add(dirPath);
        }
        this.renderTree();
    }
    
    selectItem(itemPath, isDirectory) {
        this.selectedNode = itemPath;
        
        // Find the item in tree data
        const item = this._findItemByPath(this.treeData, itemPath);
        if (item) {
            this.showFileInfo(item);
        }
        
        // Update visual selection
        this.renderTree();
    }
    
    _findItemByPath(items, targetPath) {
        for (const item of items) {
            if (item.path === targetPath) {
                return item;
            }
            if (item.children) {
                const found = this._findItemByPath(item.children, targetPath);
                if (found) return found;
            }
        }
        return null;
    }
    
    showFileInfo(item) {
        const itemTypeText = item.is_directory ? 'Directory' : 'Markdown File';
        const sizeText = item.is_directory ? 'Directory' : this.formatFileSize(item.size);
        
        const fileInfoHTML = `
            <div class="file-info-header">
                <div class="file-icon-large">${this.getTreeIcon(item)}</div>
                <div class="file-name-large">${this.escapeHtml(item.name)}</div>
            </div>
            <div class="file-properties">
                <div class="property">
                    <span class="label">Type:</span>
                    <span class="value">${this.escapeHtml(item.type)}</span>
                </div>
                <div class="property">
                    <span class="label">Size:</span>
                    <span class="value">${sizeText}</span>
                </div>
                <div class="property">
                    <span class="label">Modified:</span>
                    <span class="value">${new Date(item.modified).toLocaleString()}</span>
                </div>
                <div class="property">
                    <span class="label">Permissions:</span>
                    <span class="value">${this.escapeHtml(item.permissions)}</span>
                </div>
                <div class="property">
                    <span class="label">Path:</span>
                    <span class="value">${this.escapeHtml(item.path)}</span>
                </div>
                ${!item.is_directory ? `
                <div class="property">
                    <span class="label">Directory:</span>
                    <span class="value">${this.escapeHtml(item.path.split('/').slice(0, -1).join('/') || '/')}</span>
                </div>
                ` : ''}
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
            new MarkdownTreeExplorer();
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
