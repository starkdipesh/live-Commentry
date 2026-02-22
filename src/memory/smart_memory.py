"""
Friday's Smart Memory System
Vector-based semantic memory with RAG (Retrieval-Augmented Generation)
Enables Friday to remember past conversations and retrieve relevant context.
"""

import json
import os
import sqlite3
import hashlib
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime


class SmartMemory:
    """
    Friday's long-term memory system using vector-based semantic storage.
    Stores conversation chunks with embeddings for efficient retrieval.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize SmartMemory with SQLite backend.
        
        Args:
            db_path: Path to SQLite database. If None, uses default location.
        """
        if db_path is None:
            base_dir = Path(__file__).resolve().parent.parent.parent
            db_path = base_dir / "config" / "friday_memory.db"
        
        self.db_path = str(db_path)
        self.embeddings_available = False
        self.embedding_model = None
        
        # Initialize embeddings if sentence-transformers is available
        try:
            from sentence_transformers import SentenceTransformer
            # Use lightweight model (80MB)
            model_name = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
            self.embedding_model = SentenceTransformer(model_name)
            self.embeddings_available = True
            print(f"✅ Embeddings loaded: {model_name}")
        except ImportError:
            print("⚠️ sentence-transformers not available. Using keyword-based retrieval.")
        except Exception as e:
            print(f"⚠️ Embeddings initialization failed: {e}")
        
        # Initialize database
        self._init_database()
        
        # Conversation buffer for recent context
        self.recent_buffer = []
        self.buffer_size = int(os.getenv('MEMORY_BUFFER_SIZE', '10'))
    
    def _init_database(self):
        """Initialize SQLite database with vector-friendly schema."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Main memory table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    session_id TEXT NOT NULL,
                    chunk_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    content_hash TEXT UNIQUE NOT NULL,
                    embedding BLOB,
                    metadata TEXT,
                    importance_score REAL DEFAULT 1.0
                )
            ''')
            
            # Index for fast retrieval
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_memory_time 
                ON memory_chunks(timestamp DESC)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_memory_type 
                ON memory_chunks(chunk_type)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_memory_session 
                ON memory_chunks(session_id)
            ''')
            
            # User profile table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_profile (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at REAL
                )
            ''')
            
            # Project context table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS project_context (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_name TEXT NOT NULL,
                    detected_at REAL,
                    last_active REAL,
                    context_data TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            print(f"✅ SmartMemory database ready: {self.db_path}")
            
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
    
    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding vector for text."""
        if not self.embeddings_available or self.embedding_model is None:
            return None
        
        try:
            embedding = self.embedding_model.encode(text, convert_to_tensor=False)
            return embedding.tolist()
        except Exception as e:
            print(f"⚠️ Embedding generation failed: {e}")
            return None
    
    def _content_hash(self, content: str) -> str:
        """Generate hash for content deduplication."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0
        
        try:
            import numpy as np
            v1 = np.array(vec1)
            v2 = np.array(vec2)
            
            dot_product = np.dot(v1, v2)
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
        except Exception:
            return 0.0
    
    def store_interaction(self, user_input: str, ai_response: str, 
                         visual_context: str = "", session_id: str = "default"):
        """
        Store a user-AI interaction in memory.
        
        Args:
            user_input: What the user said
            ai_response: What Friday replied
            visual_context: Screen/window context
            session_id: Session identifier
        """
        timestamp = time.time()
        
        # Store user input
        user_chunk = f"User: {user_input}"
        self._store_chunk(user_chunk, "user_input", timestamp, session_id, {
            "visual_context": visual_context[:200]
        })
        
        # Store AI response
        ai_chunk = f"Friday: {ai_response}"
        self._store_chunk(ai_chunk, "ai_response", timestamp, session_id, {
            "responding_to": user_input[:100]
        })
        
        # Add to recent buffer
        self.recent_buffer.append({
            "timestamp": timestamp,
            "user": user_input,
            "ai": ai_response,
            "context": visual_context
        })
        
        # Trim buffer
        if len(self.recent_buffer) > self.buffer_size:
            self.recent_buffer = self.recent_buffer[-self.buffer_size:]
        
        # Detect and store project context
        self._detect_project_context(visual_context, timestamp)
    
    def _store_chunk(self, content: str, chunk_type: str, timestamp: float,
                    session_id: str, metadata: Dict = None):
        """Store a single memory chunk."""
        try:
            content_hash = self._content_hash(content)
            embedding = self._generate_embedding(content)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check for duplicate
            cursor.execute(
                "SELECT id FROM memory_chunks WHERE content_hash = ?",
                (content_hash,)
            )
            if cursor.fetchone():
                conn.close()
                return
            
            # Calculate importance score
            importance = self._calculate_importance(content, chunk_type)
            
            # Store chunk
            cursor.execute('''
                INSERT INTO memory_chunks 
                (timestamp, session_id, chunk_type, content, content_hash, 
                 embedding, metadata, importance_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                session_id,
                chunk_type,
                content,
                content_hash,
                json.dumps(embedding) if embedding else None,
                json.dumps(metadata) if metadata else None,
                importance
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Failed to store chunk: {e}")
    
    def _calculate_importance(self, content: str, chunk_type: str) -> float:
        """Calculate importance score for a chunk."""
        score = 1.0
        
        # User commands are more important
        if chunk_type == "user_input":
            score += 0.5
            
            # Commands with action keywords are important
            action_keywords = [
                "open", "close", "search", "find", "create", "delete",
                "run", "execute", "save", "load", "settings", "config"
            ]
            content_lower = content.lower()
            if any(kw in content_lower for kw in action_keywords):
                score += 1.0
        
        # Error-related content is important
        error_keywords = ["error", "failed", "problem", "issue", "bug", "crash"]
        if any(kw in content.lower() for kw in error_keywords):
            score += 1.5
        
        # Questions indicate learning opportunities
        if "?" in content and chunk_type == "user_input":
            score += 0.3
        
        # Longer responses might have more information
        if len(content) > 200:
            score += 0.2
        
        return min(score, 3.0)  # Cap at 3.0
    
    def _detect_project_context(self, visual_context: str, timestamp: float):
        """Detect and store project context from window titles or paths."""
        if not visual_context:
            return
        
        # Extract project names from common patterns
        import re
        
        # VS Code: "filename - project - Visual Studio Code"
        vscode_match = re.search(r'-\s*(.+?)\s+-\s*Visual Studio Code', visual_context)
        if vscode_match:
            project_name = vscode_match.group(1).strip()
            self._update_project_context(project_name, timestamp)
            return
        
        # PyCharm/IntelliJ: "project [path] - filename"
        pycharm_match = re.search(r'\[(.+?)\].*-\s*PyCharm', visual_context)
        if pycharm_match:
            project_name = pycharm_match.group(1).split('/')[-1].strip()
            self._update_project_context(project_name, timestamp)
            return
        
        # Terminal: "user@host:~/path/to/project"
        terminal_match = re.search(r':~?/(.+?)(?:\s|$)', visual_context)
        if terminal_match:
            path = terminal_match.group(1)
            # Get last folder name
            project_name = path.split('/')[-1].strip()
            if project_name and len(project_name) > 2:
                self._update_project_context(project_name, timestamp)
                return
        
        # Git repo detection
        git_match = re.search(r'git.*\s+([\w\-]+)(?:\s|$)', visual_context)
        if git_match:
            project_name = git_match.group(1).strip()
            self._update_project_context(project_name, timestamp)
    
    def _update_project_context(self, project_name: str, timestamp: float):
        """Update or create project context."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if project exists
            cursor.execute(
                "SELECT id FROM project_context WHERE project_name = ?",
                (project_name,)
            )
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('''
                    UPDATE project_context 
                    SET last_active = ? 
                    WHERE project_name = ?
                ''', (timestamp, project_name))
            else:
                cursor.execute('''
                    INSERT INTO project_context 
                    (project_name, detected_at, last_active, context_data)
                    VALUES (?, ?, ?, ?)
                ''', (project_name, timestamp, timestamp, '{}'))
                print(f"📁 New project detected: {project_name}")
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Project context update failed: {e}")
    
    def retrieve_relevant_context(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Retrieve relevant context for a query using semantic search or keyword fallback.
        
        Args:
            query: The search query
            top_k: Number of results to return
            
        Returns:
            List of relevant memory chunks
        """
        if self.embeddings_available:
            return self._semantic_search(query, top_k)
        else:
            return self._keyword_search(query, top_k)
    
    def _semantic_search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Search using semantic embeddings."""
        try:
            query_embedding = self._generate_embedding(query)
            if not query_embedding:
                return self._keyword_search(query, top_k)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all chunks with embeddings from last 30 days
            cutoff_time = time.time() - (30 * 24 * 60 * 60)
            cursor.execute('''
                SELECT id, timestamp, chunk_type, content, embedding, 
                       metadata, importance_score
                FROM memory_chunks
                WHERE timestamp > ? AND embedding IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT 500
            ''', (cutoff_time,))
            
            chunks = cursor.fetchall()
            conn.close()
            
            # Calculate similarities
            scored_chunks = []
            for chunk in chunks:
                chunk_embedding = json.loads(chunk[4]) if chunk[4] else None
                if chunk_embedding:
                    similarity = self._cosine_similarity(query_embedding, chunk_embedding)
                    # Boost by importance and recency
                    recency_boost = 1.0 - (time.time() - chunk[1]) / (30 * 24 * 60 * 60)
                    importance_boost = chunk[6] / 3.0
                    final_score = similarity * (1 + recency_boost * 0.3 + importance_boost * 0.2)
                    
                    scored_chunks.append((final_score, chunk))
            
            # Sort by score and return top_k
            scored_chunks.sort(reverse=True, key=lambda x: x[0])
            top_chunks = scored_chunks[:top_k]
            
            results = []
            for score, chunk in top_chunks:
                if score > 0.5:  # Similarity threshold
                    results.append({
                        "id": chunk[0],
                        "timestamp": chunk[1],
                        "type": chunk[2],
                        "content": chunk[3],
                        "metadata": json.loads(chunk[5]) if chunk[5] else {},
                        "score": score
                    })
            
            return results
            
        except Exception as e:
            print(f"⚠️ Semantic search failed: {e}")
            return self._keyword_search(query, top_k)
    
    def _keyword_search(self, query: str, top_k: int = 3) -> List[Dict]:
        """Fallback keyword-based search."""
        try:
            keywords = query.lower().split()
            cutoff_time = time.time() - (30 * 24 * 60 * 60)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, timestamp, chunk_type, content, metadata, importance_score
                FROM memory_chunks
                WHERE timestamp > ?
                ORDER BY timestamp DESC
                LIMIT 200
            ''', (cutoff_time,))
            
            chunks = cursor.fetchall()
            conn.close()
            
            # Score by keyword matches
            scored_chunks = []
            for chunk in chunks:
                content_lower = chunk[3].lower()
                score = sum(1 for kw in keywords if kw in content_lower)
                
                if score > 0:
                    # Boost by importance and recency
                    recency_boost = 1.0 - (time.time() - chunk[1]) / (30 * 24 * 60 * 60)
                    importance_boost = chunk[5] / 3.0
                    final_score = score * (1 + recency_boost * 0.3 + importance_boost * 0.2)
                    
                    scored_chunks.append((final_score, chunk))
            
            scored_chunks.sort(reverse=True, key=lambda x: x[0])
            top_chunks = scored_chunks[:top_k]
            
            results = []
            for score, chunk in top_chunks:
                results.append({
                    "id": chunk[0],
                    "timestamp": chunk[1],
                    "type": chunk[2],
                    "content": chunk[3],
                    "metadata": json.loads(chunk[4]) if chunk[4] else {},
                    "score": score
                })
            
            return results
            
        except Exception as e:
            print(f"⚠️ Keyword search failed: {e}")
            return []
    
    def get_recent_context(self, n: int = 5) -> List[Dict]:
        """Get n most recent interactions."""
        return self.recent_buffer[-n:] if self.recent_buffer else []
    
    def get_current_project(self) -> Optional[str]:
        """Get the most recently active project."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT project_name FROM project_context
                ORDER BY last_active DESC
                LIMIT 1
            ''')
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            print(f"⚠️ Failed to get current project: {e}")
            return None
    
    def get_user_profile(self, key: str) -> Optional[str]:
        """Get a value from user profile."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT value FROM user_profile WHERE key = ?",
                (key,)
            )
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] if result else None
            
        except Exception as e:
            print(f"⚠️ Failed to get profile: {e}")
            return None
    
    def set_user_profile(self, key: str, value: str):
        """Set a value in user profile."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO user_profile (key, value, updated_at)
                VALUES (?, ?, ?)
            ''', (key, value, time.time()))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ Failed to set profile: {e}")
    
    def format_context_for_prompt(self, query: str, recent_n: int = 3, relevant_k: int = 3) -> str:
        """
        Format memory context for inclusion in AI prompt.
        
        Args:
            query: Current user query
            recent_n: Number of recent interactions to include
            relevant_k: Number of relevant past interactions to include
            
        Returns:
            Formatted context string
        """
        parts = []
        
        # Add current project
        current_project = self.get_current_project()
        if current_project:
            parts.append(f"Current Project: {current_project}")
        
        # Add recent context
        recent = self.get_recent_context(recent_n)
        if recent:
            parts.append("\nRecent Conversation:")
            for item in recent:
                parts.append(f"  User: {item['user']}")
                parts.append(f"  Friday: {item['ai']}")
        
        # Add relevant context from memory
        relevant = self.retrieve_relevant_context(query, relevant_k)
        if relevant:
            parts.append("\nRelevant Past Context:")
            for item in relevant:
                parts.append(f"  [{item['type']}] {item['content'][:150]}...")
        
        return "\n".join(parts) if parts else ""
    
    def get_stats(self) -> Dict:
        """Get memory statistics."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = {}
            
            # Total chunks
            cursor.execute("SELECT COUNT(*) FROM memory_chunks")
            stats['total_chunks'] = cursor.fetchone()[0]
            
            # Chunks by type
            cursor.execute('''
                SELECT chunk_type, COUNT(*) 
                FROM memory_chunks 
                GROUP BY chunk_type
            ''')
            stats['by_type'] = dict(cursor.fetchall())
            
            # Total projects
            cursor.execute("SELECT COUNT(*) FROM project_context")
            stats['total_projects'] = cursor.fetchone()[0]
            
            # Recent activity (24 hours)
            day_ago = time.time() - 86400
            cursor.execute('''
                SELECT COUNT(*) FROM memory_chunks
                WHERE timestamp > ?
            ''', (day_ago,))
            stats['recent_24h'] = cursor.fetchone()[0]
            
            conn.close()
            return stats
            
        except Exception as e:
            print(f"⚠️ Failed to get stats: {e}")
            return {}
    
    def cleanup_old_memories(self, days: int = 90):
        """Remove memories older than specified days."""
        try:
            cutoff = time.time() - (days * 24 * 60 * 60)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                DELETE FROM memory_chunks
                WHERE timestamp < ? AND importance_score < 2.0
            ''', (cutoff,))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            print(f"🧹 Cleaned up {deleted} old memory chunks")
            
        except Exception as e:
            print(f"⚠️ Cleanup failed: {e}")


# Utility function for quick access
def get_memory() -> SmartMemory:
    """Get or create singleton SmartMemory instance."""
    if not hasattr(get_memory, '_instance'):
        get_memory._instance = SmartMemory()
    return get_memory._instance
