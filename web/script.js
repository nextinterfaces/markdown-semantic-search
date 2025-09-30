// Markdown Tree Explorer Frontend JavaScript

class MarkdownTreeExplorer {
    constructor() {
        this.treeData = [];
        this.filteredTreeData = [];
        this.currentDirectory = '';
        this.expandedNodes = new Set();
        this.selectedNode = null;
        this.searchResultsData = [];
        this.currentSearchType = 'filename';
        this.isSemanticSearchAvailable = false;
        
        this.initializeElements();
        this.bindEvents();
        this.initializeResize();
        this.loadFiles();
    }
    
    initializeElements() {
        // Get DOM elements
        this.filesList = document.getElementById('filesList');
        this.emptyState = document.getElementById('emptyState');
        this.welcomeScreen = document.getElementById('welcomeScreen');
        this.fileInfo = document.getElementById('fileInfo');
        this.searchInput = document.getElementById('searchInput');
        this.searchType = document.getElementById('searchType');
        this.buildIndexBtn = document.getElementById('buildIndexBtn');
        this.searchResults = document.getElementById('searchResults');
        this.searchResultsContent = document.getElementById('searchResultsContent');
        this.searchResultsCount = document.getElementById('searchResultsCount');
        this.refreshBtn = document.getElementById('refreshBtn');
        this.toast = document.getElementById('toast');
    }
    
    bindEvents() {
        // Button events
        this.refreshBtn.addEventListener('click', () => this.refreshFiles());
        this.buildIndexBtn.addEventListener('click', () => this.buildSemanticIndex());
        
        // Search functionality
        this.searchInput.addEventListener('input', (e) => this.handleSearch(e.target.value));
        this.searchType.addEventListener('change', (e) => this.handleSearchTypeChange(e.target.value));
    }
    
    async loadFiles() {
        try {
            this.treeData = await pywebview.api.get_files();
            this.currentDirectory = await pywebview.api.get_current_directory();
            this.filteredTreeData = [...this.treeData];
            this.renderTree();
            this.updateCurrentDirectory();
            
            // Check if semantic search is available
            this.checkSemanticSearchAvailability();
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
    
    filterTreeByFilename(query) {
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
        
        // Handle clicks on tree items
        this.filesList.querySelectorAll('.tree-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                const itemPath = e.currentTarget.dataset.path;
                const isDirectory = e.currentTarget.dataset.isDirectory === 'true';
                
                if (isDirectory) {
                    // Single click on directory toggles expansion
                    this.toggleDirectory(itemPath);
                } else {
                    // Single click on file shows content
                    this.selectItem(itemPath, isDirectory);
                }
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
            const toggleIcon = isExpanded ? '-' : '+';
            html += `
                <button class="tree-toggle" data-path="${this.escapeHtml(item.path)}">
                    ${toggleIcon}
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
        // Return empty string to remove all icons
        return '';
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
    
    async selectItem(itemPath, isDirectory) {
        this.selectedNode = itemPath;
        
        // Find the item in tree data
        const item = this._findItemByPath(this.treeData, itemPath);
        if (item) {
            if (isDirectory) {
                this.showDirectoryInfo(item);
            } else {
                // Load and render markdown content for files
                await this.showMarkdownFile(item);
            }
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
    
    showDirectoryInfo(item) {
        const fileInfoHTML = `
            <div class="file-info-header">
                <div class="file-icon-large">${this.getTreeIcon(item)}</div>
                <div class="file-name-large">${this.escapeHtml(item.name)}</div>
            </div>
            <div class="directory-info">
                <p>Directory containing markdown files.</p>
                <p>Click to expand/collapse, or use the +/- icon.</p>
                <div class="file-properties">
                    <div class="property">
                        <span class="label">Path:</span>
                        <span class="value">${this.escapeHtml(item.path)}</span>
                    </div>
                    <div class="property">
                        <span class="label">Modified:</span>
                        <span class="value">${new Date(item.modified).toLocaleString()}</span>
                    </div>
                    <div class="property">
                        <span class="label">Contains:</span>
                        <span class="value">${item.children ? item.children.length : 0} items</span>
                    </div>
                </div>
            </div>
        `;
        
        document.getElementById('fileInfoContent').innerHTML = fileInfoHTML;
        this.showFileInfoPanel();
    }
    
    async showMarkdownFile(item) {
        try {
            // Show loading state
            const loadingHTML = `
                <div class="file-info-header">
                    <div class="file-icon-large">${this.getTreeIcon(item)}</div>
                    <div class="file-name-large">${this.escapeHtml(item.name)}</div>
                </div>
                <div class="markdown-loading">
                    Loading markdown content...
                </div>
            `;
            document.getElementById('fileInfoContent').innerHTML = loadingHTML;
            this.showFileInfoPanel();
            
            // Load file content
            const response = await pywebview.api.get_file_content(item.path);
            
            if (response.success) {
                // Configure marked options for better rendering
                marked.setOptions({
                    breaks: true,
                    gfm: true,
                    sanitize: false
                });
                
                const renderedContent = marked.parse(response.content);
                
                const fileInfoHTML = `
                    <div class="file-info-header">
                        <div class="file-icon-large">${this.getTreeIcon(item)}</div>
                        <div class="file-name-large">${this.escapeHtml(item.name)}</div>
                        <div class="file-meta">
                            <span class="file-size">${this.formatFileSize(item.size)}</span>
                            <span class="file-modified">${new Date(item.modified).toLocaleDateString()}</span>
                        </div>
                    </div>
                    <div class="markdown-content">
                        ${renderedContent}
                    </div>
                `;
                
                document.getElementById('fileInfoContent').innerHTML = fileInfoHTML;
            } else {
                const errorHTML = `
                    <div class="file-info-header">
                        <div class="file-icon-large">${this.getTreeIcon(item)}</div>
                        <div class="file-name-large">${this.escapeHtml(item.name)}</div>
                    </div>
                    <div class="markdown-error">
                        Error loading file: ${this.escapeHtml(response.error)}
                    </div>
                `;
                document.getElementById('fileInfoContent').innerHTML = errorHTML;
            }
        } catch (error) {
            console.error('Error loading markdown file:', error);
            this.showToast('Error loading markdown file', 'error');
        }
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
    
    // Semantic Search Methods
    
    async checkSemanticSearchAvailability() {
        try {
            this.isSemanticSearchAvailable = await pywebview.api.is_semantic_search_available();
            this.updateSemanticSearchUI();
        } catch (error) {
            console.error('Error checking semantic search availability:', error);
            this.isSemanticSearchAvailable = false;
            this.updateSemanticSearchUI();
        }
    }
    
    updateSemanticSearchUI() {
        if (!this.isSemanticSearchAvailable) {
            this.searchType.disabled = true;
            this.buildIndexBtn.disabled = true;
            this.buildIndexBtn.title = "Semantic search not available (missing dependencies)";
            
            // Remove semantic search option
            const semanticOption = this.searchType.querySelector('option[value="semantic"]');
            if (semanticOption) {
                semanticOption.disabled = true;
                semanticOption.textContent = "Semantic Search (Not Available)";
            }
        } else {
            this.searchType.disabled = false;
            this.buildIndexBtn.disabled = false;
            this.buildIndexBtn.title = "Build semantic search index";
        }
    }
    
    handleSearchTypeChange(searchType) {
        this.currentSearchType = searchType;
        const currentQuery = this.searchInput.value;
        
        if (currentQuery.trim()) {
            this.handleSearch(currentQuery);
        } else {
            this.hideSearchResults();
        }
    }
    
    async handleSearch(query) {
        if (!query.trim()) {
            this.hideSearchResults();
            this.filteredTreeData = [...this.treeData];
            this.renderTree();
            return;
        }
        
        if (this.currentSearchType === 'semantic') {
            await this.performSemanticSearch(query);
        } else {
            this.hideSearchResults();
            this.filterTreeByFilename(query);
        }
    }
    
    async performSemanticSearch(query) {
        if (!this.isSemanticSearchAvailable) {
            this.showToast('Semantic search not available', 'error');
            return;
        }
        
        try {
            // Show loading state
            this.showSearchLoading();
            
            const response = await pywebview.api.semantic_search_query(query, 15);
            
            if (response.success) {
                this.searchResultsData = response.results;
                this.displaySearchResults(response.results, query);
            } else {
                this.showToast(`Search error: ${response.error}`, 'error');
                this.hideSearchResults();
            }
        } catch (error) {
            console.error('Error performing semantic search:', error);
            this.showToast('Error performing semantic search', 'error');
            this.hideSearchResults();
        }
    }
    
    showSearchLoading() {
        this.searchResults.style.display = 'block';
        this.welcomeScreen.style.display = 'none';
        this.fileInfo.style.display = 'none';
        
        this.searchResultsContent.innerHTML = '<div class="search-loading">Searching...</div>';
        this.searchResultsCount.textContent = '';
    }
    
    displaySearchResults(results, query) {
        if (results.length === 0) {
            this.searchResultsContent.innerHTML = `
                <div class="search-empty">
                    <p>No results found for "${this.escapeHtml(query)}"</p>
                    <small>Try different keywords or build the search index first.</small>
                </div>
            `;
            this.searchResultsCount.textContent = '0 results';
        } else {
            const resultsHTML = results.map(result => this.createSearchResultHTML(result)).join('');
            this.searchResultsContent.innerHTML = resultsHTML;
            this.searchResultsCount.textContent = `${results.length} result${results.length !== 1 ? 's' : ''}`;
            
            // Add click handlers to search results
            this.attachSearchResultEvents();
        }
        
        this.searchResults.style.display = 'block';
        this.welcomeScreen.style.display = 'none';
        this.fileInfo.style.display = 'none';
    }
    
    createSearchResultHTML(result) {
        const similarity = (result.similarity * 100).toFixed(1);
        const modifiedDate = new Date(result.modified_time * 1000).toLocaleDateString();
        
        return `
            <div class="search-result-item" data-file-path="${this.escapeHtml(result.file_path)}">
                <div class="search-result-header">
                    <div class="search-result-file">${this.escapeHtml(result.file_name)}</div>
                    <div class="search-result-similarity">${similarity}%</div>
                </div>
                <div class="search-result-content">${this.escapeHtml(result.content_preview)}</div>
                <div class="search-result-meta">
                    <span>📄 Chunk ${result.chunk_index + 1}</span>
                    <span>📅 ${modifiedDate}</span>
                    <span>📁 ${this.getShortPath(result.file_path)}</span>
                </div>
            </div>
        `;
    }
    
    getShortPath(fullPath) {
        const parts = fullPath.split('/');
        if (parts.length > 3) {
            return '.../' + parts.slice(-2).join('/');
        }
        return fullPath;
    }
    
    attachSearchResultEvents() {
        this.searchResultsContent.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const filePath = e.currentTarget.dataset.filePath;
                this.openFileFromSearch(filePath);
            });
        });
    }
    
    async openFileFromSearch(filePath) {
        try {
            const response = await pywebview.api.get_file_content(filePath);
            if (response.success) {
                // Create a temporary item object for display
                const item = {
                    name: response.filename,
                    path: filePath,
                    is_directory: false,
                    size: response.content.length,
                    modified: new Date().toISOString()
                };
                
                await this.showMarkdownFile(item);
            } else {
                this.showToast(`Error opening file: ${response.error}`, 'error');
            }
        } catch (error) {
            console.error('Error opening file from search:', error);
            this.showToast('Error opening file', 'error');
        }
    }
    
    hideSearchResults() {
        this.searchResults.style.display = 'none';
        this.searchResultsData = [];
        
        // Show welcome screen if no file is selected
        if (this.fileInfo.style.display === 'none') {
            this.showWelcomeScreen();
        }
    }
    
    async buildSemanticIndex() {
        if (!this.isSemanticSearchAvailable) {
            this.showToast('Semantic search not available', 'error');
            return;
        }
        
        try {
            // Disable button and show loading state
            this.buildIndexBtn.disabled = true;
            this.buildIndexBtn.textContent = 'Building...';
            
            this.showToast('Building semantic search index...', 'info');
            
            const response = await pywebview.api.build_semantic_index();
            
            if (response.success) {
                const results = response.results;
                this.showToast(
                    `Index built successfully! Processed ${results.processed_files} files, ${results.total_chunks} chunks.`,
                    'success'
                );
            } else {
                this.showToast(`Error building index: ${response.error}`, 'error');
            }
        } catch (error) {
            console.error('Error building semantic index:', error);
            this.showToast('Error building semantic index', 'error');
        } finally {
            // Re-enable button
            this.buildIndexBtn.disabled = false;
            this.buildIndexBtn.textContent = 'Build Index';
        }
    }
    
    // Sidebar Resize Functionality
    
    initializeResize() {
        const sidebar = document.querySelector('.sidebar');
        const resizer = document.createElement('div');
        resizer.className = 'sidebar-resizer';
        sidebar.appendChild(resizer);
        
        let isResizing = false;
        let startX = 0;
        let startWidth = 0;
        
        resizer.addEventListener('mousedown', (e) => {
            isResizing = true;
            startX = e.clientX;
            startWidth = parseInt(document.defaultView.getComputedStyle(sidebar).width, 10);
            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
            document.body.style.cursor = 'col-resize';
            document.body.style.userSelect = 'none';
        });
        
        const handleMouseMove = (e) => {
            if (!isResizing) return;
            
            const newWidth = startWidth + e.clientX - startX;
            const minWidth = 200;
            const maxWidth = window.innerWidth * 0.6;
            
            if (newWidth >= minWidth && newWidth <= maxWidth) {
                sidebar.style.width = newWidth + 'px';
            }
        };
        
        const handleMouseUp = () => {
            if (isResizing) {
                isResizing = false;
                document.removeEventListener('mousemove', handleMouseMove);
                document.removeEventListener('mouseup', handleMouseUp);
                document.body.style.cursor = '';
                document.body.style.userSelect = '';
            }
        };
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
