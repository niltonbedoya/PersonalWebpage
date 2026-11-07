"""SQLite + SQLite-vec schema for the RAG corpus (F5/T2).

Plain sqlite3 implementation (dependency-free beyond sqlite-vec). Creates and
maintains the documents, chunks and embeddings tables used by Cerebrito's real
grounding. All log output is ASCII-only (Windows cp1252 console rule).

Tables:
- documents: id, title, source_path, content, created_at
- chunks: id, document_id, chunk_index, content, metadata
- embeddings: sqlite-vec virtual table for vector search over chunk rowids
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

import sqlite_vec

# Deterministic hash-based embedding dimension (computed by T4 indexer).
EMBEDDING_DIM = 384

# Absolute, __file__-based path to the corpus database. Never cwd-relative so
# the backend works no matter where it is launched from.
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent.parent.parent / "data" / "rag_corpus.db"

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    source_path TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id INTEGER NOT NULL REFERENCES documents(id),
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT NOT NULL DEFAULT '{{}}',
    UNIQUE(document_id, chunk_index)
);

CREATE VIRTUAL TABLE IF NOT EXISTS embeddings USING vec0(embedding float[{dim}]);
"""


def serialize_embedding(vector):
    """Serialize a list of floats into the raw bytes sqlite-vec expects."""
    return sqlite_vec.serialize_float32(vector)


def get_connection(db_path=DEFAULT_DB_PATH):
    """Open a sqlite3 connection to db_path with the sqlite-vec extension loaded.

    db_path is resolved to an absolute path. The connection is returned to the
    caller, who owns committing and closing it.
    """
    db_path = Path(db_path)
    if not db_path.is_absolute():
        db_path = Path(__file__).resolve().parent.parent.parent.parent / db_path
    conn = sqlite3.connect(str(db_path))
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    return conn


def create_schema(conn, embedding_dim=EMBEDDING_DIM):
    """Create documents, chunks and embeddings tables if they do not exist.

    Idempotent: safe to run on an already initialized database.
    """
    conn.executescript(CREATE_SQL.format(dim=embedding_dim))


def init_db(db_path=DEFAULT_DB_PATH, embedding_dim=EMBEDDING_DIM):
    """Initialize the corpus database at db_path (idempotent).

    Returns the open sqlite3 connection with the schema created.
    """
    conn = get_connection(db_path)
    create_schema(conn, embedding_dim)
    conn.commit()
    return conn
