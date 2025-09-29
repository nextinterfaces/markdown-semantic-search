# Markdown Explorer - Desktop Markdown File Browser

A modern, elegant desktop application for exploring and browsing markdown files built with **pywebview**. Features an expandable tree view that shows only `.md` and `.mdx` files in your directory structure.

![Markdown Explorer](https://img.shields.io/badge/Python-3.7+-blue.svg)
![PyWebView](https://img.shields.io/badge/PyWebView-6.0+-green.svg)
![UV](https://img.shields.io/badge/UV-Fast%20Python%20Manager-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- **Expandable Tree View**: Navigate directory structure with collapsible folders
- **Markdown-Only Filter**: Shows only `.md` and `.mdx` files
- **Clean Interface**: Minimalist design showing only file and directory names
- **Smart Directory Display**: Only shows folders containing markdown files
- **Markdown Rendering**: View rendered markdown content with full formatting support
- **Single-Click Navigation**: Single-click directories to expand/collapse
- **Real-time Search**: Filter files by name or type
- **Keyboard Shortcuts**: Quick actions with familiar shortcuts
- **Cross-platform**: Works on Windows, macOS, and Linux
- **No Internet Required**: Fully offline application
- **Modern Python Tooling**: Uses `uv` for lightning-fast dependency management
- **Easy Setup**: One command installation with automatic virtual environment

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- [uv](https://docs.astral.sh/uv/) (Fast Python package manager)

### Installing uv

If you don't have uv installed yet:

```bash
# On macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip:
pip install uv
```

### Installation

1. **Clone or download this repository**
   ```bash
   git clone <repository-url>
   cd mynotes
   ```

2. **Install dependencies with uv (automatically creates virtual environment)**
   ```bash
   uv sync
   ```

3. **Run the application**
   ```bash
   uv run python main.py
   # Or use the included run script:
   ./run.sh
   ```

### Alternative Installation (Traditional Method)

If you prefer using pip:

1. **Create a virtual environment**
   ```bash
   python -m venv .venv
   
   # On macOS/Linux:
   source .venv/bin/activate
   
   # On Windows:
   .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## 🎯 How to Use

### Exploring the Tree View
- **Expand/Collapse Folders**: 
  - Click the chevron (▶/▼) icons next to folder names
  - **Single-click** on any folder to expand/collapse it
- **Navigate Directories**: Only directories containing `.md` or `.mdx` files are shown
- **View Markdown Content**: Click on any `.md` or `.mdx` file to see its rendered content on the right

### Reading Markdown Files
- **Single-click** any markdown file in the tree to view its rendered content
- The right panel will display the markdown with proper formatting:
  - Headers, lists, code blocks
  - Links, images, tables
  - Blockquotes and styling
- Loading indicator shows while content is being fetched

### Searching Files
- Use the search box in the header to filter by filename
- Or press `Ctrl+F` (or `Cmd+F` on macOS) to focus the search
- Search works across file names and types

### Refreshing the View
- Click the **"Refresh"** button in the header
- Or use `Ctrl+R` or `F5` to refresh the file list
- This will scan for new or changed markdown files

## 🛠️ Technical Details

### Architecture

The application uses a hybrid architecture:

- **Backend**: Python with pywebview providing the desktop application framework
- **Frontend**: HTML, CSS, and JavaScript for the tree view interface
- **Markdown Rendering**: Uses Marked.js library for client-side markdown parsing
- **File System**: Directly reads `.md` and `.mdx` files from the file system
- **API**: Python methods exposed to JavaScript via pywebview's API bridge for file operations

### File Structure

```
markdown-explorer/
├── main.py              # Main application entry point
├── run.sh              # Quick run script
├── pyproject.toml       # Project configuration and dependencies (uv)
├── requirements.txt     # Python dependencies (pip fallback)
├── uv.lock             # Locked dependency versions (generated)
├── sample.md           # Sample markdown file for testing
├── web/
│   ├── index.html      # Main HTML template
│   ├── style.css       # Tree view styling and layout
│   └── script.js       # Frontend JavaScript tree logic
└── README.md           # This file
```

### Key Components

1. **FileAPI Class** (`main.py`): Handles file system operations and tree building
2. **MarkdownTreeExplorer Class** (`script.js`): Manages the tree view interface and interactions
3. **Responsive UI**: Clean tree design that works on different screen sizes

### Why uv?

This project uses [uv](https://docs.astral.sh/uv/) instead of traditional pip for dependency management because:

- **⚡ Lightning Fast**: 10-100x faster than pip for most operations
- **🔒 Deterministic**: Automatic lock file generation ensures reproducible builds  
- **🎯 Zero Config**: Works out of the box with minimal setup
- **🔄 Drop-in Replacement**: Compatible with existing pip workflows
- **🌍 Cross-platform**: Works seamlessly on Windows, macOS, and Linux

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+R` / `Cmd+R` | Refresh file tree |
| `F5` | Refresh file tree |
| `Ctrl+F` / `Cmd+F` | Focus search box |

## 🎨 Customization

### Changing the Theme

Edit `web/style.css` to customize colors, fonts, and layout:

```css
/* Header gradient */
.header {
    background: linear-gradient(135deg, #your-color1 0%, #your-color2 100%);
}

/* Primary button color */
.btn-primary {
    background: #your-primary-color;
}
```

### Adding Features

The application is designed to be easily extensible:

1. **Backend**: Add new methods to the `FileAPI` class in `main.py`
2. **Frontend**: Extend the `MarkdownTreeExplorer` class in `web/script.js`
3. **UI**: Modify `web/index.html` and `web/style.css` for interface changes

## 🐛 Troubleshooting

### Common Issues

1. **Application won't start**
   - Ensure Python 3.7+ is installed
   - Check that all dependencies are installed: `uv sync`
   - Try running with debug mode: The app already runs with `debug=True`

2. **Files not showing**
   - Ensure there are `.md` or `.mdx` files in the current directory or subdirectories
   - Check file permissions - the application needs read access to scan directories

3. **UI not loading**
   - Verify that the `web/` directory and all files exist
   - Check browser console for JavaScript errors (F12 in debug mode)

### Debug Mode

The application runs with debug mode disabled by default for a clean user experience. You can still access developer tools when needed:

- **macOS**: Right-click and select "Inspect Element" or use `Cmd+Option+I`
- **Windows/Linux**: Right-click and select "Inspect" or use `F12`

To enable debug mode (auto-opens developer tools), change `debug=False` to `debug=True` in `main.py`.

## 📁 Supported File Types

The application scans for and displays:

- **`.md`** files - Standard Markdown files
- **`.mdx`** files - MDX (Markdown with JSX) files

Directory structure is preserved and only directories containing these file types are shown in the tree view.

## 🤝 Contributing

Feel free to fork this project and submit pull requests for improvements:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- [pywebview](https://pywebview.flowrl.com/) - For the excellent Python-to-web bridge
- [Marked.js](https://marked.js.org/) - For fast, reliable markdown parsing
- [Font Awesome](https://fontawesome.com/) - For the beautiful icons
- The Python and web development communities

---

**Enjoy exploring your markdown files! 📁✨**
