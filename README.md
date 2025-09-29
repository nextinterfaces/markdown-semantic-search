# MyNotes - Desktop Notes Application

A modern, elegant desktop notes application built with **pywebview** that combines the power of Python with a beautiful web-based user interface.

![MyNotes App](https://img.shields.io/badge/Python-3.7+-blue.svg)
![PyWebView](https://img.shields.io/badge/PyWebView-4.4.1-green.svg)
![UV](https://img.shields.io/badge/UV-Fast%20Python%20Manager-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- **Modern UI**: Clean, responsive interface with smooth animations
- **Full CRUD Operations**: Create, read, update, and delete notes
- **Real-time Search**: Instantly search through your notes by title or content
- **Auto-save**: Automatically saves your notes as you type
- **Keyboard Shortcuts**: Quick actions with familiar shortcuts
- **Cross-platform**: Works on Windows, macOS, and Linux
- **Local Storage**: All notes are stored locally in JSON format
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

### Creating Notes
- Click the **"New Note"** button in the header
- Or use the keyboard shortcut: `Ctrl+N` (or `Cmd+N` on macOS)
- Start typing your note title and content

### Editing Notes
- Click on any note in the sidebar to open it
- Edit the title by clicking in the title field
- Edit content in the main text area
- Notes auto-save as you type, or manually save with `Ctrl+S`

### Searching Notes
- Use the search box in the header
- Or press `Ctrl+F` (or `Cmd+F` on macOS) to focus the search
- Search works across both titles and content

### Deleting Notes
- Open the note you want to delete
- Click the **"Delete"** button
- Confirm the deletion (this action cannot be undone)

## 🛠️ Technical Details

### Architecture

The application uses a hybrid architecture:

- **Backend**: Python with pywebview providing the desktop application framework
- **Frontend**: HTML, CSS, and JavaScript for the user interface
- **Data Storage**: JSON file for simple, portable note storage
- **API**: Python methods exposed to JavaScript via pywebview's API bridge

### File Structure

```
mynotes/
├── main.py              # Main application entry point
├── pyproject.toml       # Project configuration and dependencies (uv)
├── requirements.txt     # Python dependencies (pip fallback)
├── uv.lock             # Locked dependency versions (generated)
├── notes.json          # Notes data (created automatically)
├── web/
│   ├── index.html      # Main HTML template
│   ├── style.css       # Styling and layout
│   └── script.js       # Frontend JavaScript logic
└── README.md           # This file
```

### Key Components

1. **NotesAPI Class** (`main.py`): Handles all note operations (CRUD)
2. **NotesApp Class** (`script.js`): Manages the frontend interface and user interactions
3. **Responsive UI**: Mobile-friendly design that works on different screen sizes

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
| `Ctrl+N` / `Cmd+N` | Create new note |
| `Ctrl+S` / `Cmd+S` | Save current note |
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

1. **Backend**: Add new methods to the `NotesAPI` class in `main.py`
2. **Frontend**: Extend the `NotesApp` class in `web/script.js`
3. **UI**: Modify `web/index.html` and `web/style.css` for interface changes

## 🐛 Troubleshooting

### Common Issues

1. **Application won't start**
   - Ensure Python 3.7+ is installed
   - Check that all dependencies are installed: `uv sync`
   - Try running with debug mode: The app already runs with `debug=True`

2. **Notes not saving**
   - Check file permissions in the application directory
   - Ensure the application has write access to create `notes.json`

3. **UI not loading**
   - Verify that the `web/` directory and all files exist
   - Check browser console for JavaScript errors (F12 in debug mode)

### Debug Mode

The application runs in debug mode by default, which:
- Opens browser developer tools
- Provides detailed error messages
- Allows hot-reloading of web assets

To disable debug mode, change `debug=True` to `debug=False` in `main.py`.

## 📝 Data Format

Notes are stored in `notes.json` with the following structure:

```json
[
  {
    "id": 1,
    "title": "My First Note",
    "content": "This is the content of my note...",
    "created_at": "2023-10-01T12:00:00.000000",
    "updated_at": "2023-10-01T12:30:00.000000"
  }
]
```

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
- [Font Awesome](https://fontawesome.com/) - For the beautiful icons
- The Python and web development communities

---

**Enjoy taking notes with MyNotes! 📝✨**
