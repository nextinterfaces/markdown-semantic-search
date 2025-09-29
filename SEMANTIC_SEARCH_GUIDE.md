# Semantic Search Setup Guide

## Overview

Your Markdown Explorer now includes semantic search capabilities using SQLite for metadata storage and FAISS for vector similarity search. This allows you to search for content based on meaning rather than just keywords.

## Installation

1. **Install the new dependencies:**
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install sentence-transformers faiss-cpu numpy
   ```

2. **Run the application:**
   ```bash
   python main.py
   # or
   ./run.sh
   ```

## How It Works

The semantic search system:

1. **Processes markdown files** by breaking them into overlapping text chunks
2. **Generates embeddings** using the `all-MiniLM-L6-v2` sentence transformer model
3. **Stores metadata** in SQLite database (`semantic_search.db`)
4. **Indexes embeddings** in FAISS index (`faiss_index.bin`) for fast similarity search
5. **Provides semantic search** that finds content based on meaning, not just keywords

## Using Semantic Search

### 1. Build the Search Index

- Click the **"Build Index"** button in the interface
- This will process all markdown files and create the search index
- You'll see a progress notification when completed
- The index is automatically saved and persists between sessions

### 2. Search Your Content

1. **Switch to Semantic Search**: Select "Semantic Search" from the dropdown
2. **Enter your query**: Type what you're looking for (e.g., "neural networks", "machine learning concepts")
3. **View results**: See ranked results with similarity scores and content previews
4. **Click on results**: Open the full file to read more

### 3. Search Types

- **File Names**: Traditional filename-based search (filters the file tree)
- **Semantic Search**: Content-based search using AI embeddings

## Features

### Smart Content Chunking
- Files are split into overlapping chunks for better context preservation
- Each chunk is independently searchable
- Results show which chunk matched and its position in the file

### Similarity Scoring
- Results are ranked by semantic similarity (0-100%)
- Higher scores indicate better matches
- Helps you find the most relevant content quickly

### Change Detection
- The system automatically detects when files are modified
- Only changed files are re-processed when rebuilding the index
- Efficient incremental updates

### Rich Search Results
- Content preview snippets
- File information and modification dates
- Chunk position within the document
- Click to open full file

## Files Created

The semantic search system creates these files in your project directory:

- `semantic_search.db` - SQLite database with file metadata and chunks
- `faiss_index.bin` - FAISS vector index for fast similarity search
- `semantic_search.py` - The semantic search implementation

## Tips for Best Results

1. **Use descriptive queries**: "transformer attention mechanism" vs "attention"
2. **Try different phrasings**: The AI understands synonyms and related concepts
3. **Rebuild index after adding new files**: Use the "Build Index" button
4. **Be patient on first run**: Building the index takes time for large collections

## Troubleshooting

### "Semantic search not available"
- Make sure all dependencies are installed: `uv sync` or `pip install -r requirements.txt`
- Check the console for error messages about missing packages

### No search results
- Ensure the index has been built (click "Build Index")
- Try broader search terms
- Check that your markdown files contain text content

### Slow performance
- The first time building an index takes longer
- Subsequent updates are faster due to change detection
- Consider using GPU version of FAISS for very large document collections

## Advanced Configuration

You can modify the semantic search behavior by editing `semantic_search.py`:

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

## Performance Stats

After building an index, you can check statistics by calling the backend API:
```javascript
// In browser console (when app is running)
pywebview.api.get_semantic_search_stats()
```

This shows:
- Total files indexed
- Total chunks created
- Index size and dimensions
- Recently processed files
