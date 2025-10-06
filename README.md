# MyNotes - Semantic Search of Markdown Files

A desktop application for semantic search of markdown files using SQLite vector database and FAISS.

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![PyWebView](https://img.shields.io/badge/PyWebView-6.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎯 Features

- Semantic search capabilities for markdown files
- Uses SQLite vector database and FAISS for search
- Desktop interface built with PyWebView
- Fast and efficient search capabilities

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher

### Installation

1. **Install dependencies with uv**
   ```bash
   uv sync
   ```

2. **Run the application**
   ```bash
   uv run python src/main.py
   # Or use the included run script:
   ./run.sh
   ```

## 🛠️ Technical Details

### Architecture

The application uses a hybrid architecture:

- **Backend**: Python with PyWebView providing the desktop application framework
- **Frontend**: HTML, CSS, and JavaScript for the tree view interface
- **Search Engine**: SQLite vector database and FAISS for semantic search capabilities

### Stack

- Python 3.7+
- PyWebView
- SQLite vector database
- FAISS (Facebook AI Similarity Search)
- Markdown file processing

## 📄 License

This project is open source and available under the MIT License.

# Semantic Search Setup Guide


## How It Works

The semantic search system:

1. **Processes markdown files** by breaking them into overlapping text chunks
2. **Generates embeddings** using the `all-MiniLM-L6-v2` sentence transformer model
3. **Stores metadata** in SQLite database (`semantic_search.db`)
4. **Indexes embeddings** in FAISS index (`faiss_index.bin`) for fast similarity search
5. **Provides semantic search** that finds content based on meaning, not just keywords

## Features

### Smart Content Chunking
- Files are split into overlapping chunks to preserve context
- Each chunk is independently searchable
- Results show which chunk matched and its position in the file

### Similarity Scoring
- Results are ranked by semantic similarity (0-100%)
- Higher scores indicate better matches
- Helps you find the most relevant content quickly

### Change Detection
- The system automatically detects file modifications
- Only changed files are re-processed when rebuilding the index
- Efficient incremental updates

### Rich Search Results
- Content preview snippets
- File information and modification dates
- Chunk position within the document
- Click to open full file

## Advanced Configuration

You can modify the semantic search behavior by editing `src/semantic_search.py`:

- **Change the model**: Modify `model_name` parameter for different embedding models
- **Adjust chunk size**: Change `chunk_size` parameter for different content splitting
- **Modify overlap**: Change `overlap` parameter for chunk overlap amount

## Model Information

The default model `all-MiniLM-L6-v2`:
- Fast and efficient (384 dimensional embeddings)
- Good balance of speed and quality
- ~80MB download on first use
- Suitable for most use cases

For better quality (but slower performance), consider:
- `all-mpnet-base-v2` (768 dimensions)
- `multi-qa-mpnet-base-dot-v1` (768 dimensions, optimized for Q&A)
