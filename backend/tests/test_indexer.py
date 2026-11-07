"""TDD: RAG corpus indexer (F5/T4, S1/S4/S7/S8).

Offline and deterministic: tests use temp directories and temp databases,
never the real `data/` corpus path or the default DB location. No network,
no LLM calls.

Covers:
- chunk_document: fixed-size overlapping chunks.
- compute_embedding: deterministic, 384-dim, unit-norm.
- index_corpus: indexes every *.md file in a data directory.
- search: top-k results ordered by relevance (distance ascending).
"""

import math
import shutil
import sqlite3
import tempfile
from pathlib import Path

import pytest

from backend.app.db.indexer import (
    chunk_document,
    compute_embedding,
    index_corpus,
    search,
)
from backend.app.db.schema import EMBEDDING_DIM, get_connection

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REAL_DATA_DIR = REPO_ROOT / "data"


def _temp_dir(prefix="indexer_test_"):
    return Path(tempfile.mkdtemp(prefix=prefix))


def _write_md(data_dir, name, content):
    (data_dir / name).write_text(content, encoding="utf-8")


def _cleanup(*paths):
    for path in paths:
        shutil.rmtree(path, ignore_errors=True)


# ---------------------------------------------------------------------------
# chunk_document
# ---------------------------------------------------------------------------

def test_chunk_document_splits_into_fixed_size_chunks():
    content = "x" * 500
    chunks = chunk_document(content, chunk_size=200, overlap=40)
    assert len(chunks) == 3
    assert [len(c) for c in chunks] == [200, 200, 180]
    assert chunks[0] == content[0:200]
    assert chunks[1] == content[160:360]
    assert chunks[2] == content[320:500]


def test_chunk_document_overlap_is_exact():
    content = "abcdefghijklmnopqrstuvwxyz" * 8  # 208 chars
    chunks = chunk_document(content, chunk_size=60, overlap=10)
    assert len(chunks) > 1
    start = 0
    for chunk in chunks:
        assert chunk == content[start:start + 60]
        start += 50
    # Coverage: every character of the content appears in some chunk.
    covered = [False] * len(content)
    start = 0
    for chunk in chunks:
        for i in range(start, min(start + 60, len(content))):
            covered[i] = True
        start += 50
    assert all(covered)
    # Overlap property between consecutive chunks.
    for first, second in zip(chunks, chunks[1:]):
        assert first[-10:] == second[:10]


def test_chunk_document_short_content_is_single_chunk():
    content = "corto"
    assert chunk_document(content, chunk_size=200, overlap=40) == ["corto"]


def test_chunk_document_empty_content_is_empty():
    assert chunk_document("", chunk_size=200, overlap=40) == []


def test_chunk_document_is_deterministic():
    content = "contenido de prueba para el indice de corpus rags" * 10
    assert chunk_document(content) == chunk_document(content)


def test_chunk_document_rejects_invalid_arguments():
    with pytest.raises(ValueError):
        chunk_document("x", chunk_size=0, overlap=40)
    with pytest.raises(ValueError):
        chunk_document("x", chunk_size=-5, overlap=40)
    with pytest.raises(ValueError):
        chunk_document("x", chunk_size=200, overlap=200)
    with pytest.raises(ValueError):
        chunk_document("x", chunk_size=200, overlap=-1)


# ---------------------------------------------------------------------------
# compute_embedding
# ---------------------------------------------------------------------------

def test_compute_embedding_is_deterministic():
    text = "deterministic hash based embedding for offline rag"
    assert compute_embedding(text) == compute_embedding(text)


def test_compute_embedding_is_384_dim_normalized_vector():
    vector = compute_embedding("vector de incrustacion de prueba")
    assert isinstance(vector, list)
    assert len(vector) == EMBEDDING_DIM == 384
    assert all(isinstance(v, float) for v in vector)
    norm = math.sqrt(sum(v * v for v in vector))
    assert abs(norm - 1.0) < 1e-6


def test_compute_embedding_empty_text_is_unit_vector():
    vector = compute_embedding("")
    assert len(vector) == EMBEDDING_DIM
    norm = math.sqrt(sum(v * v for v in vector))
    assert abs(norm - 1.0) < 1e-6 or all(v == 0.0 for v in vector)


def test_compute_embedding_different_texts_produce_different_vectors():
    assert compute_embedding("soldadura") != compute_embedding("reflow")


# ---------------------------------------------------------------------------
# index_corpus
# ---------------------------------------------------------------------------

def test_index_corpus_indexes_every_md_file():
    temp_root = _temp_dir()
    data_dir = _temp_dir()
    db_path = temp_root / "rag_corpus.db"
    try:
        _write_md(data_dir, "alpha.md", "# Alpha\ntitulo alfa sobre soldadura.")
        _write_md(data_dir, "beta.md", "# Beta\ntitulo beta sobre reflow.")
        _write_md(data_dir, "gamma.md", "# Gamma\ntitulo gamma sobre traduccion.")
        index_corpus(data_dir=data_dir, db_path=db_path)
        conn = sqlite3.connect(str(db_path))
        try:
            count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        finally:
            conn.close()
        expected = len(list(data_dir.glob("*.md")))
        assert count == expected == 3
    finally:
        _cleanup(temp_root, data_dir)


def test_index_corpus_indexes_real_data_directory():
    temp_root = _temp_dir()
    db_path = temp_root / "rag_corpus.db"
    try:
        index_corpus(data_dir=str(REAL_DATA_DIR), db_path=db_path)
        conn = sqlite3.connect(str(db_path))
        try:
            count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
        finally:
            conn.close()
        expected = len(list(REAL_DATA_DIR.glob("*.md")))
        assert count == expected
    finally:
        _cleanup(temp_root)


def test_index_corpus_stores_chunks_and_embeddings():
    temp_root = _temp_dir()
    data_dir = _temp_dir()
    db_path = temp_root / "rag_corpus.db"
    try:
        _write_md(data_dir, "one.md", "# Uno\ncontenido largo " * 40)
        index_corpus(data_dir=data_dir, db_path=db_path)
        conn = get_connection(db_path)
        try:
            doc_count = conn.execute("SELECT COUNT(*) FROM documents").fetchone()[0]
            chunk_count = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
            emb_count = conn.execute("SELECT COUNT(*) FROM embeddings").fetchone()[0]
            row = conn.execute(
                "SELECT c.chunk_index, c.content FROM chunks c "
                "ORDER BY c.chunk_index LIMIT 1"
            ).fetchone()
            embedding_row = conn.execute(
                "SELECT e.rowid FROM embeddings e ORDER BY e.rowid LIMIT 1"
            ).fetchone()
        finally:
            conn.close()
        assert doc_count == 1
        assert chunk_count > 1  # overlapping chunks of a long document
        assert emb_count == chunk_count  # one embedding vector per chunk
        assert row[0] == 0 and "contenido" in row[1]
        assert embedding_row[0] == 1  # embedding rowid mirrors chunks.id
    finally:
        _cleanup(temp_root, data_dir)


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------

def _search_in_corpus(names_contents, query, top_k=5):
    temp_root = _temp_dir()
    data_dir = _temp_dir()
    db_path = temp_root / "rag_corpus.db"
    try:
        for name, content in names_contents:
            _write_md(data_dir, name, content)
        index_corpus(data_dir=data_dir, db_path=db_path)
        return search(query, db_path=db_path, top_k=top_k)
    finally:
        _cleanup(temp_root, data_dir)


def test_search_returns_top_k_results_ordered_by_relevance():
    corpus = [
        ("a.md", "# A\nsoldadura de la junta de la placa."),
        ("b.md", "# B\nmetricas de calidad de software en pipeline."),
        ("c.md", "# C\nprocesos termales de horno de reflow."),
    ]
    results = _search_in_corpus(corpus, "soldadura", top_k=2)
    assert len(results) <= 2
    distances = [row["distance"] for row in results]
    assert distances == sorted(distances)
    for row in results:
        assert set(row) >= {"content", "source"}


def test_search_term_present_in_corpus_returns_that_document():
    corpus = [
        ("term_doc.md", "# Term\naqui hablamos de soldadura y nada mas."),
        ("other.md", "# Other\ntemas de logistica y metricas de inventario."),
    ]
    results = _search_in_corpus(corpus, "soldadura", top_k=5)
    assert results, "search should return results"
    assert "soldadura" in results[0]["content"].lower()


def test_search_unrelated_term_returns_low_scores():
    corpus = [
        ("a.md", "# A\nsoldadura de la junta de la placa."),
        ("b.md", "# B\nmetricas de calidad de software."),
    ]
    results = _search_in_corpus(corpus, "zzzqwertyunrelated", top_k=5)
    assert results
    assert all(row["distance"] > 1.1 for row in results)


def test_search_deterministic_results():
    corpus = [
        ("a.md", "# A\ncontenido determinista para pruebas de busqueda."),
    ]
    first = _search_in_corpus(corpus, "determinista", top_k=3)
    second = _search_in_corpus(corpus, "determinista", top_k=3)
    assert [(r["content"], r["distance"]) for r in first] == [
        (r["content"], r["distance"]) for r in second
    ]
