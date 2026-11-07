"""RAG corpus indexer for Cerebrito's offline grounding (F5/T4, S1/S4/S7/S8).

Deterministic, offline, dependency-free beyond ``sqlite-vec``:
- ``chunk_document`` splits text into fixed-size overlapping chunks.
- ``compute_embedding`` builds a stable 384-dim unit vector from a hashlib
  seed (no LLM, no network).
- ``index_corpus`` reads every ``*.md`` file of a data directory, chunks it,
  embeds every chunk and stores documents / chunks / embeddings in SQLite
  using the schema from ``backend/app/db/schema.py``.
- ``search`` embeds the query and runs a sqlite-vec kNN search, returning the
  top-k chunks ordered by relevance (distance ascending) with content + source.

All log output is ASCII-only (Windows cp1252 console rule); this module logs
nothing.
"""

from __future__ import annotations

import hashlib
import math
import random
import re
from pathlib import Path

from backend.app.db.schema import (
    DEFAULT_DB_PATH,
    EMBEDDING_DIM,
    get_connection,
    init_db,
    serialize_embedding,
)

# Repository root, __file__-based so the indexer works no matter the cwd.
ROOT = Path(__file__).resolve().parent.parent.parent.parent

_TOKEN_SPLIT = re.compile(r"\w+")


def chunk_document(content: str, chunk_size: int = 200, overlap: int = 40) -> list[str]:
    """Split ``content`` into overlapping chunks of ``chunk_size`` characters.

    Consecutive chunks overlap by exactly ``overlap`` characters so no text
    is lost at the boundaries. Deterministic: same input, same output.
    """
    if (
        not isinstance(chunk_size, int)
        or isinstance(chunk_size, bool)
        or chunk_size <= 0
    ):
        raise ValueError("chunk_size must be a positive integer")
    if (
        not isinstance(overlap, int)
        or isinstance(overlap, bool)
        or overlap < 0
        or overlap >= chunk_size
    ):
        raise ValueError("overlap must satisfy 0 <= overlap < chunk_size")

    chunks: list[str] = []
    start = 0
    total = len(content)
    while start < total:
        chunks.append(content[start:start + chunk_size])
        if start + chunk_size >= total:
            break
        start += chunk_size - overlap
    return chunks


def _word_vector(word: str, dim: int) -> list[float]:
    """Deterministic pseudo-random unit-free vector derived from a word hash."""
    seed = int.from_bytes(hashlib.sha256(word.encode("utf-8")).digest()[:8], "big")
    rng = random.Random(seed)
    return [rng.gauss(0.0, 1.0) for _ in range(dim)]


def compute_embedding(text: str) -> list[float]:
    """Deterministic 384-dim normalized vector for ``text``.

    Hash-based (no LLM, no network): each token contributes a stable vector
    derived from a SHA-256 seed; the sum is L2-normalized. Same input always
    yields the same output.
    """
    words = _TOKEN_SPLIT.findall(str(text).lower())
    if not words:
        words = ["_empty_document_"]

    vector = [0.0] * EMBEDDING_DIM
    for word in words:
        word_vec = _word_vector(word, EMBEDDING_DIM)
        for i in range(EMBEDDING_DIM):
            vector[i] += word_vec[i]

    norm = math.sqrt(sum(v * v for v in vector))
    if norm <= 0.0:
        return [0.0] * EMBEDDING_DIM
    return [v / norm for v in vector]


def _document_title(content: str, fallback: str) -> str:
    """First non-empty markdown heading line, or ``fallback``."""
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            line = line.lstrip("#").strip()
        return line or fallback
    return fallback


def index_corpus(data_dir: str = "data", db_path=None) -> None:
    """Index every ``*.md`` file under ``data_dir`` into the SQLite-vec DB.

    Idempotent: re-running replaces the previous index (tables are cleared
    first), so the same corpus always produces the same stored rows.
    """
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    data_dir = Path(data_dir)
    if not data_dir.is_absolute():
        data_dir = ROOT / data_dir
    db_path = Path(db_path)

    md_files = sorted(data_dir.glob("*.md"))
    conn = init_db(db_path=db_path)
    try:
        conn.execute("DELETE FROM embeddings")
        conn.execute("DELETE FROM chunks")
        conn.execute("DELETE FROM documents")
        for path in md_files:
            content = path.read_text(encoding="utf-8")
            title = _document_title(content, path.stem)
            cursor = conn.execute(
                "INSERT INTO documents(title, source_path, content, created_at) "
                "VALUES (?, ?, ?, datetime('now'))",
                (title, str(path), content),
            )
            document_id = cursor.lastrowid
            for chunk_index, chunk in enumerate(chunk_document(content)):
                conn.execute(
                    "INSERT INTO chunks(document_id, chunk_index, content, metadata) "
                    "VALUES (?, ?, ?, '{}')",
                    (document_id, chunk_index, chunk),
                )
                chunk_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
                conn.execute(
                    "INSERT INTO embeddings(rowid, embedding) VALUES (?, ?)",
                    (chunk_id, serialize_embedding(compute_embedding(chunk))),
                )
        conn.commit()
    finally:
        conn.close()


def search(query_text, db_path=None, top_k=5) -> list[dict]:
    """Vector search for ``query_text``; returns up to ``top_k`` results.

    Each result is a dict with ``title``, ``source``, ``content`` and
    ``distance`` (cosine distance, ascending = most relevant first).
    """
    if db_path is None:
        db_path = DEFAULT_DB_PATH
    try:
        top_k = int(top_k)
    except (TypeError, ValueError) as exc:
        raise ValueError("top_k must be a positive integer") from exc
    if top_k <= 0:
        raise ValueError("top_k must be a positive integer")

    serialized = serialize_embedding(compute_embedding(str(query_text)))
    # The kNN scan must sit on the vec0 table directly (sqlite-vec does not
    # push MATCH/LIMIT down through joins), so the subquery runs first and the
    # join happens on its rowids.
    knn = (
        "SELECT rowid, distance FROM embeddings "
        "WHERE embedding MATCH ? ORDER BY distance LIMIT %d" % top_k
    )
    sql = (
        "SELECT d.title, d.source_path, c.content, e.distance FROM ("
        + knn
        + ") e JOIN chunks c ON c.id = e.rowid "
        "JOIN documents d ON d.id = c.document_id "
        "ORDER BY e.distance"
    )
    conn = get_connection(db_path)
    try:
        rows = conn.execute(sql, [serialized]).fetchall()
    finally:
        conn.close()
    return [
        {"title": row[0], "source": row[1], "content": row[2], "distance": row[3]}
        for row in rows
    ]
