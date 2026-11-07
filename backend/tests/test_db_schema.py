"""TDD: SQLite + SQLite-vec schema for the RAG corpus (F5/T2, S1/S4/S7).

Offline and deterministic: tests use a temp-directory database, never the
real data/ corpus path. No network, no LLM calls.

Covers:
- Database file is created at the expected (__file__-based absolute) path.
- documents table exists with correct columns.
- chunks table exists with correct columns.
- sqlite-vec virtual table exists and accepts vector insert/query.
- Insert a document + chunk + embedding, then query it back.
- Vector similarity search returns results ordered by distance.
- Re-running init is idempotent (no error on existing tables).
"""

import os
import sqlite3
import tempfile
from pathlib import Path

import pytest

from backend.app.db.schema import (
    DEFAULT_DB_PATH,
    EMBEDDING_DIM,
    create_schema,
    get_connection,
    init_db,
    serialize_embedding,
)

EXPECTED_DOCUMENT_COLUMNS = {"id", "title", "source_path", "content", "created_at"}
EXPECTED_CHUNK_COLUMNS = {"id", "document_id", "chunk_index", "content", "metadata"}


def _unit_vector(index: int):
    vec = [0.0] * EMBEDDING_DIM
    vec[index] = 1.0
    return vec


def _temp_db_path() -> Path:
    return Path(tempfile.mkdtemp(prefix="rag_schema_test_")) / "rag_corpus.db"


# S7 — path is __file__-based and absolute, never cwd-relative -------------

def test_default_db_path_is_absolute_and_file_based():
    assert DEFAULT_DB_PATH.is_absolute()
    assert DEFAULT_DB_PATH.name == "rag_corpus.db"
    assert str(DEFAULT_DB_PATH).endswith(os.path.join("data", "rag_corpus.db"))


# S1 — database file is created at the expected path -----------------------

def test_database_file_is_created_at_expected_path():
    db_path = _temp_db_path()
    assert not db_path.exists()
    init_db(db_path=db_path)
    assert db_path.exists()
    assert db_path.is_file()


# S1 — documents table exists with correct columns -------------------------

def test_documents_table_has_expected_columns():
    db_path = _temp_db_path()
    conn = init_db(db_path=db_path)
    try:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(documents)")}
    finally:
        conn.close()
    assert EXPECTED_DOCUMENT_COLUMNS.issubset(columns)


# S1 — chunks table exists with correct columns ----------------------------

def test_chunks_table_has_expected_columns():
    db_path = _temp_db_path()
    conn = init_db(db_path=db_path)
    try:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(chunks)")}
    finally:
        conn.close()
    assert EXPECTED_CHUNK_COLUMNS.issubset(columns)


# S4 — sqlite-vec virtual table exists and accepts vector insert/query -----

def test_sqlite_vec_virtual_table_exists_and_accepts_vectors():
    db_path = _temp_db_path()
    conn = init_db(db_path=db_path)
    try:
        row = conn.execute(
            "SELECT type, sql FROM sqlite_master WHERE name = 'embeddings'"
        ).fetchone()
        assert row is not None, "embeddings table missing"
        assert "vec0" in row[1], f"embeddings is not a sqlite-vec table: {row[1]}"

        vec = serialize_embedding(_unit_vector(0))
        conn.execute(
            "INSERT INTO embeddings(rowid, embedding) VALUES (1, ?)", [vec]
        )
        conn.commit()

        found = conn.execute(
            "SELECT rowid, distance FROM embeddings "
            "WHERE embedding MATCH ? ORDER BY distance LIMIT 5",
            [vec],
        ).fetchall()
        assert found == [(1, 0.0)]
    finally:
        conn.close()


# S4 — insert a document + chunk + embedding, then query it back -----------

def test_insert_document_chunk_embedding_then_query_back():
    db_path = _temp_db_path()
    conn = init_db(db_path=db_path)
    try:
        conn.execute(
            "INSERT INTO documents(title, source_path, content, created_at) "
            "VALUES (?, ?, ?, datetime('now'))",
            ["SMT reflow profile", "data/smt_reflow.md",
             "Horno de reflow: zona de precalentamiento, reflow y enfriamiento."],
        )
        conn.execute(
            "INSERT INTO chunks(document_id, chunk_index, content, metadata) "
            "VALUES (?, 0, ?, '{}')",
            [1, "Zona de reflow: pasta de soldadura fundida sobre la placa."],
        )
        conn.execute(
            "INSERT INTO embeddings(rowid, embedding) VALUES (1, ?)",
            [serialize_embedding(_unit_vector(0))],
        )
        conn.commit()

        row = conn.execute(
            "SELECT d.title, c.content FROM documents d "
            "JOIN chunks c ON c.document_id = d.id WHERE d.id = 1"
        ).fetchone()
        assert row is not None
        assert row[0] == "SMT reflow profile"
        assert "pasta de soldadura" in row[1]

        vec_row = conn.execute(
            "SELECT rowid FROM embeddings WHERE rowid = 1"
        ).fetchone()
        assert vec_row == (1,)
    finally:
        conn.close()


# S4 — vector similarity search returns results ordered by distance --------

def test_vector_similarity_search_ordered_by_distance():
    db_path = _temp_db_path()
    conn = init_db(db_path=db_path)
    try:
        vectors = [
            (1, _unit_vector(0)),
            (2, _unit_vector(1)),
            (3, _unit_vector(2)),
        ]
        for rowid, vec in vectors:
            conn.execute(
                "INSERT INTO embeddings(rowid, embedding) VALUES (?, ?)",
                [rowid, serialize_embedding(vec)],
            )
        conn.commit()

        query = serialize_embedding(_unit_vector(0))
        results = conn.execute(
            "SELECT rowid, distance FROM embeddings "
            "WHERE embedding MATCH ? ORDER BY distance LIMIT 10",
            [query],
        ).fetchall()

        distances = [row[1] for row in results]
        assert distances == sorted(distances)
        assert results[0][0] == 1  # closest vector is rowid 1 (distance 0.0)
        assert abs(results[0][1] - 0.0) < 1e-6
    finally:
        conn.close()


# S1/S6 — re-running init is idempotent (no error on existing tables) -----

def test_init_db_is_idempotent():
    db_path = _temp_db_path()
    first = init_db(db_path=db_path)
    second = init_db(db_path=db_path)
    assert first is not None and second is not None

    conn = get_connection(db_path)
    try:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"
            )
        }
        assert {"documents", "chunks", "embeddings"}.issubset(tables)

        # Tables still accept writes after re-init.
        conn.execute(
            "INSERT INTO documents(title, source_path, content, created_at) "
            "VALUES (?, ?, ?, datetime('now'))",
            ["idempotency check", "data/x.md", "content"],
        )
        conn.commit()
        count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        assert count >= 1
    finally:
        conn.close()


# Default path helper returns a working connection -------------------------

def test_get_connection_loads_sqlite_vec():
    db_path = _temp_db_path()
    conn = get_connection(db_path)
    try:
        # Extension loaded: creating the vec0 virtual table works.
        conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS probe USING vec0(embedding float[3])")
        conn.execute(
            "INSERT INTO probe(rowid, embedding) VALUES (1, ?)",
            [serialize_embedding([1.0, 2.0, 3.0])],
        )
        conn.commit()
        row = conn.execute(
            "SELECT distance FROM probe WHERE embedding MATCH ? LIMIT 1",
            [serialize_embedding([1.0, 2.0, 3.0])],
        ).fetchone()
        assert abs(row[0] - 0.0) < 1e-6
    finally:
        conn.close()


def test_embedding_dimension_constant_is_positive():
    assert isinstance(EMBEDDING_DIM, int) and EMBEDDING_DIM > 0
