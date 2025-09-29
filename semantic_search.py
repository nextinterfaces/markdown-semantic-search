#!/usr/bin/env python3
"""
Semantic Search Manager - Handles embedding generation, SQLite storage, and FAISS indexing
"""

import os
import sqlite3
import hashlib
import time
from typing import List, Dict, Optional, Tuple, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss


class SemanticSearchManager:
    """Manager for semantic search functionality using SQLite + FAISS"""
    
    def __init__(self, 
                 db_path: str = "semantic_search.db",
                 faiss_index_path: str = "faiss_index.bin",
                 model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the semantic search manager
        
        Args:
            db_path: Path to SQLite database
            faiss_index_path: Path to FAISS index file
            model_name: Name of the sentence transformer model to use
        """
        self.db_path = db_path
        self.faiss_index_path = faiss_index_path
        self.model_name = model_name
        
        # Initialize sentence transformer model
        print(f"Loading sentence transformer model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        
        # Initialize database and FAISS index
        self.init_database()
        self.faiss_index = self.load_or_create_faiss_index()
        
    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create files table to store file metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                file_name TEXT NOT NULL,
                file_size INTEGER,
                modified_time REAL,
                content_hash TEXT,
                chunk_count INTEGER DEFAULT 0,
                created_at REAL,
                updated_at REAL
            )
        ''')
        
        # Create chunks table to store text chunks and their metadata
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER,
                chunk_index INTEGER,
                content TEXT NOT NULL,
                content_hash TEXT,
                faiss_id INTEGER UNIQUE,
                created_at REAL,
                FOREIGN KEY (file_id) REFERENCES files (id) ON DELETE CASCADE
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_path ON files(file_path)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_files_modified ON files(modified_time)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chunks_file_id ON chunks(file_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_chunks_faiss_id ON chunks(faiss_id)')
        
        conn.commit()
        conn.close()
        
    def load_or_create_faiss_index(self) -> faiss.Index:
        """Load existing FAISS index or create a new one"""
        if os.path.exists(self.faiss_index_path):
            try:
                print(f"Loading existing FAISS index from {self.faiss_index_path}")
                index = faiss.read_index(self.faiss_index_path)
                return index
            except Exception as e:
                print(f"Error loading FAISS index: {e}. Creating new index.")
        
        print("Creating new FAISS index")
        # Using IndexFlatIP for inner product (cosine similarity with normalized vectors)
        index = faiss.IndexFlatIP(self.embedding_dim)
        return index
    
    def save_faiss_index(self):
        """Save the FAISS index to disk"""
        try:
            faiss.write_index(self.faiss_index, self.faiss_index_path)
            print(f"FAISS index saved to {self.faiss_index_path}")
        except Exception as e:
            print(f"Error saving FAISS index: {e}")
    
    def get_file_hash(self, file_path: str) -> str:
        """Generate hash for file content"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            print(f"Error generating hash for {file_path}: {e}")
            return ""
    
    def chunk_text(self, text: str, chunk_size: int = 512, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunk = text[start:end]
            chunks.append(chunk)
            
            if end == len(text):
                break
                
            start = end - overlap
            
        return chunks
    
    def process_markdown_file(self, file_path: str) -> bool:
        """
        Process a markdown file and add it to the search index
        
        Args:
            file_path: Path to the markdown file
            
        Returns:
            bool: True if processing was successful
        """
        try:
            # Get file metadata
            stat_result = os.stat(file_path)
            file_size = stat_result.st_size
            modified_time = stat_result.st_mtime
            content_hash = self.get_file_hash(file_path)
            
            # Check if file already exists and hasn't changed
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'SELECT id, content_hash, modified_time FROM files WHERE file_path = ?',
                (file_path,)
            )
            existing_file = cursor.fetchone()
            
            current_time = time.time()
            
            if existing_file:
                existing_id, existing_hash, existing_modified = existing_file
                if existing_hash == content_hash and existing_modified == modified_time:
                    print(f"File {file_path} unchanged, skipping...")
                    conn.close()
                    return True
                
                # File changed, remove old chunks from FAISS index
                cursor.execute('SELECT faiss_id FROM chunks WHERE file_id = ?', (existing_id,))
                old_faiss_ids = [row[0] for row in cursor.fetchall() if row[0] is not None]
                
                # Remove old chunks from database
                cursor.execute('DELETE FROM chunks WHERE file_id = ?', (existing_id,))
            
            # Read and process file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                print(f"File {file_path} is empty, skipping...")
                conn.close()
                return False
            
            # Split content into chunks
            chunks = self.chunk_text(content)
            if not chunks:
                print(f"No chunks created for {file_path}")
                conn.close()
                return False
            
            # Generate embeddings for all chunks
            print(f"Generating embeddings for {len(chunks)} chunks from {file_path}")
            embeddings = self.model.encode(chunks, convert_to_numpy=True)
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            
            # Add embeddings to FAISS index and get their IDs
            start_idx = self.faiss_index.ntotal
            self.faiss_index.add(embeddings)
            faiss_ids = list(range(start_idx, start_idx + len(chunks)))
            
            # Update or insert file record
            if existing_file:
                cursor.execute('''
                    UPDATE files 
                    SET file_name = ?, file_size = ?, modified_time = ?, 
                        content_hash = ?, chunk_count = ?, updated_at = ?
                    WHERE id = ?
                ''', (
                    os.path.basename(file_path), file_size, modified_time,
                    content_hash, len(chunks), current_time, existing_id
                ))
                file_id = existing_id
            else:
                cursor.execute('''
                    INSERT INTO files 
                    (file_path, file_name, file_size, modified_time, content_hash, 
                     chunk_count, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    file_path, os.path.basename(file_path), file_size, modified_time,
                    content_hash, len(chunks), current_time, current_time
                ))
                file_id = cursor.lastrowid
            
            # Insert chunk records
            chunk_data = [
                (file_id, i, chunk, hashlib.md5(chunk.encode()).hexdigest(), 
                 faiss_id, current_time)
                for i, (chunk, faiss_id) in enumerate(zip(chunks, faiss_ids))
            ]
            
            cursor.executemany('''
                INSERT INTO chunks 
                (file_id, chunk_index, content, content_hash, faiss_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', chunk_data)
            
            conn.commit()
            conn.close()
            
            print(f"Successfully processed {file_path}: {len(chunks)} chunks")
            return True
            
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            return False
    
    def build_index(self, markdown_files: List[str], progress_callback=None) -> Dict[str, Any]:
        """
        Build or rebuild the search index for given markdown files
        
        Args:
            markdown_files: List of markdown file paths to index
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dict with indexing results
        """
        start_time = time.time()
        results = {
            'total_files': len(markdown_files),
            'processed_files': 0,
            'failed_files': 0,
            'total_chunks': 0,
            'errors': []
        }
        
        print(f"Building index for {len(markdown_files)} markdown files...")
        
        for i, file_path in enumerate(markdown_files):
            try:
                if progress_callback:
                    progress_callback(i + 1, len(markdown_files), file_path)
                
                success = self.process_markdown_file(file_path)
                if success:
                    results['processed_files'] += 1
                else:
                    results['failed_files'] += 1
                    
            except Exception as e:
                error_msg = f"Error processing {file_path}: {e}"
                print(error_msg)
                results['errors'].append(error_msg)
                results['failed_files'] += 1
        
        # Get total chunk count
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM chunks')
        results['total_chunks'] = cursor.fetchone()[0]
        conn.close()
        
        # Save FAISS index
        self.save_faiss_index()
        
        elapsed_time = time.time() - start_time
        results['elapsed_time'] = elapsed_time
        
        print(f"Index building completed in {elapsed_time:.2f}s")
        print(f"Processed: {results['processed_files']}/{results['total_files']} files")
        print(f"Total chunks: {results['total_chunks']}")
        
        return results
    
    def semantic_search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Perform semantic search on indexed content
        
        Args:
            query: Search query string
            top_k: Number of results to return
            
        Returns:
            List of search results with metadata
        """
        if not query.strip():
            return []
        
        try:
            # Generate embedding for query
            query_embedding = self.model.encode([query], convert_to_numpy=True)
            faiss.normalize_L2(query_embedding)
            
            # Search in FAISS index
            similarities, faiss_indices = self.faiss_index.search(query_embedding, top_k)
            
            if len(faiss_indices[0]) == 0:
                return []
            
            # Get chunk details from database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            results = []
            for similarity, faiss_id in zip(similarities[0], faiss_indices[0]):
                if faiss_id == -1:  # FAISS returns -1 for invalid indices
                    continue
                
                cursor.execute('''
                    SELECT c.content, c.chunk_index, f.file_path, f.file_name, f.modified_time
                    FROM chunks c
                    JOIN files f ON c.file_id = f.id
                    WHERE c.faiss_id = ?
                ''', (int(faiss_id),))
                
                row = cursor.fetchone()
                if row:
                    content, chunk_index, file_path, file_name, modified_time = row
                    results.append({
                        'content': content,
                        'chunk_index': chunk_index,
                        'file_path': file_path,
                        'file_name': file_name,
                        'modified_time': modified_time,
                        'similarity': float(similarity),
                        'faiss_id': int(faiss_id)
                    })
            
            conn.close()
            
            # Sort by similarity (higher is better)
            results.sort(key=lambda x: x['similarity'], reverse=True)
            
            return results
            
        except Exception as e:
            print(f"Error performing semantic search: {e}")
            return []
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the search index"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM files')
            total_files = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM chunks')
            total_chunks = cursor.fetchone()[0]
            
            cursor.execute('SELECT SUM(file_size) FROM files')
            total_size = cursor.fetchone()[0] or 0
            
            cursor.execute('''
                SELECT f.file_name, f.chunk_count, f.modified_time
                FROM files f
                ORDER BY f.updated_at DESC
                LIMIT 5
            ''')
            recent_files = [
                {
                    'name': row[0],
                    'chunks': row[1],
                    'modified': row[2]
                }
                for row in cursor.fetchall()
            ]
            
            conn.close()
            
            return {
                'total_files': total_files,
                'total_chunks': total_chunks,
                'total_size_bytes': total_size,
                'faiss_index_size': self.faiss_index.ntotal,
                'embedding_dimension': self.embedding_dim,
                'model_name': self.model_name,
                'recent_files': recent_files
            }
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
    
    def remove_file(self, file_path: str) -> bool:
        """Remove a file from the search index"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get file ID and associated FAISS IDs
            cursor.execute('SELECT id FROM files WHERE file_path = ?', (file_path,))
            result = cursor.fetchone()
            
            if not result:
                print(f"File {file_path} not found in index")
                conn.close()
                return False
            
            file_id = result[0]
            
            # Get FAISS IDs for chunks (we can't efficiently remove from FAISS index)
            cursor.execute('SELECT faiss_id FROM chunks WHERE file_id = ?', (file_id,))
            faiss_ids = [row[0] for row in cursor.fetchall() if row[0] is not None]
            
            # Delete chunks and file record
            cursor.execute('DELETE FROM chunks WHERE file_id = ?', (file_id,))
            cursor.execute('DELETE FROM files WHERE id = ?', (file_id,))
            
            conn.commit()
            conn.close()
            
            print(f"Removed {file_path} from index ({len(faiss_ids)} chunks)")
            return True
            
        except Exception as e:
            print(f"Error removing file {file_path}: {e}")
            return False
