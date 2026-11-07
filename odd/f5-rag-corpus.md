# Feature Document: F5 — RAG Corpus (SQLite-vec)

**Objective:** Build the sanitized technical corpus in `data/`, index it in
SQLite-vec, and wire Cerebrito to real grounding (score + citations from the
corpus, not hardcoded 0.9). Add a corpus-sanitization battery (PII / credentials
/ real brands) as a build gate so contaminated data never reaches the index.
Per `docs/plan_de_fases_verificacion.md` (F5) and prompt maestro §5 (TDD).
**Branch:** main. **Test runner:** `python -m pytest backend/tests/ -v`
**Environment dependency:** `sqlite-vec` Python package must be installable.

## Specs

S1. "Corpus técnico sanitizado en `data/` indexado localmente; Cerebrito responde
con score y citas reales." (plan_de_fases_verificacion.md F5)
S2. "grounding_score calculado sobre corpus real (no entrada), respuesta 'no
contesto' cuando score <0.85." (F5)
S3. "Batería de sanitización del corpus (regex PII/credenciales/marcas sobre
`data/`) como gate de build — corpus con fuga NO se indexa." (F5)
S4. "Indexado del corpus (chunking, top-k correcto), recuperación mínima."
S5. "Respuesta 'no contesto fuera del corpus' — máxima apertura sobre el corpus,
síntesis neutral, no invento."
S6. TDD: tests antes de implementación, Red → Green → Refactor.
S7. All offline/deterministic, no network; logs ASCII-only (cp1252).

## Tasks

T1. Create feature doc + install sqlite-vec + verify import (this document).
T2. Create `backend/app/db/` schema + migrations: SQLite tables for documents,
chunks, embeddings; SQLite-vec virtual table for vector search. — DONE 2026-11-07 (subagent gentle-ai-worker). backend/app/db/schema.py (new), backend/tests/test_db_schema.py (new, 10 tests). sqlite-vec v0.1.9 installed. vec0 virtual table, idempotent init, KNN search with LIMIT/k. S1-S4, S7.
T3. Create sanitized corpus in `data/` — DONE 2026-11-07 (subagent gentle-ai-worker). 16 .md files covering SMT/THT machinery, thermal processes, metallurgy, handling, 5 software case studies, engineering metrics. Sanitization self-check passed (no PII/credentials/phones). S1, S3, S6, S7.
T4. Build indexing script: chunk documents, compute embeddings (deterministic hash-based for offline; no LLM), store in SQLite-vec. Delegated worker.
T5. Corpus sanitization battery (build gate): scan `data/` for PII/credentials/
real brands; fail build if found. — DONE 2026-11-07 (subagent gentle-ai-worker). backend/tests/test_corpus_sanitization.py (new, 87 tests). Emails, credential assignments, phones = hard failure; unapproved brands = warn-only; title line check. S3, S7.
T6. Wire Cerebrito to real SQLite-vec grounding — DONE 2026-11-07 (subagent gentle-ai-worker). backend/app/agents/cerebrito.py (modified), backend/tests/test_cerebrito_rag.py (new, 9 tests). Real indexer.search() when context_chunks=None; grounding score from term_coverage + distance_quality; score >= 0.85 grounded with citations; score < 0.85 → "No se encontraron fuentes relevantes". Replaces hardcoded 0.9. S1, S2, S5, S7, S8.
T7. Tests: db schema, sanitization battery, indexing, Cerebrito grounding.
Delegated worker.
T8. Full suite green; update roadmap/log.

## Allowed edit surfaces (per task — passed to workers)
T1: odd/f5-rag-corpus.md (this document)
T2: backend/app/db/schema.py (new), backend/app/db/migrations/ (new)
T3: data/*.txt or *.md corpus files (new)
T4: backend/app/db/indexer.py (new) or scripts/index_corpus.py
T5: backend/tests/test_corpus_sanitization.py (new) + build gate logic
T6: backend/app/agents/cerebrito.py (modify)
T7: backend/tests/test_db_*.py, backend/tests/test_indexer.py,
    backend/tests/test_cerebrito_rag.py (new)
T8: odd/f5-rag-corpus.md (log), docs/plan_de_fases_verificacion.md (F5 status)

## Log

L1. 2026-11-07: Feature doc created. F4 complete (182 tests green). `data/`
empty (placeholder README only), `backend/app/db/` empty scaffold, `sqlite_vec`
not installed. Cerebrito currently uses hardcoded grounding_score=0.9 (defect
fixed in F2 wave 1 for token-overlap, but needs real SQLite-vec grounding).
