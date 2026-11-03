# HANDWRITTEN.md — Hand-Written Interview Core Ledger

Project 1: HR Policy & Benefits Knowledge Assistant

This ledger lists the files the developer writes without AI-generated
solutions, as required by `docs/reference/2026 Final AI Bridge Portfolio.pdf`
and `CLAUDE.md` Section 15.

## Rules

- The developer creates each file listed below and writes both its
  implementation and its tests. No placeholder files are created in
  advance.
- Each module uses exactly the path listed below, with no duplicate
  implementation under another folder name.
- No AI code generation in these files, including inline autocomplete.
  No pasted generated or tutorial code, and no typing along with
  code-along videos.
- Allowed: official documentation, books, papers, articles, Stack Overflow
  for syntax, videos for concepts (watch, then close and write).
- Claude may explain concepts without solution code, give hints (never the
  fix), suggest test cases, review and run the developer's tests, help
  interpret failures, and review completed work.
- Review findings are fixed by hand.

## Process for each file

1. Understand the concept well enough to explain it in plain English.
2. Write 3-5 small hand-worked test examples first, including edge cases.
3. Write the code from the plan's "What it must do" description and
   signature, using documentation for syntax. If stuck for about 20
   minutes, ask for a hint, not the solution.
4. Run the tests and debug.
5. Validate against a trusted library where one exists.
6. Get the second opinion: DeepSeek/Qwen independent review, then Claude
   review. Fix findings by hand and record decisions in `docs/reviews/`.
7. Write the five-line explanation below. About one week later, rewrite the
   core function from a blank file without looking.

Scaffolding ladder: (1) study a worked example; (2) close it and rewrite
from memory, logging each peek; (3) write from the spec, signature and docs
only (default for project files); (4) write from a blank file, timed, with
no references (interview drills).

## Register

| File | Step | Status |
|---|---|---|
| `ingest/chunker.py` | P1-08 | Not started |
| `retrieval/repository.py` + `sql/` | P1-09 | Not started |
| `eval/metrics.py` | P1-10 | Not started |
| `retrieval/bm25.py` | P1-11 | Not started |
| `retrieval/fusion.py` | P1-11 | Not started |
| `generation/context_packer.py` | P1-12 | Not started |
| `generation/citations.py` | P1-13 | Not started |
| `llm/provider.py` | P1-13 | Not started |
| `eval/judge_agreement.py` | P1-14 | Not started |
| `api/limits.py` | P1-15 | Not started |
| `tests/test_isolation.py` | P1-09, P1-15 | Not started |

Target: about 700-900 lines including tests.

## File entries

Copy the entry template for each file as work begins.

### Entry template

```
### <file path> (<step>)

- Status: Not started | In progress | Reviewed | Complete
- Requirement: <what it must do, from the plan>
- Tests written by developer: <test file(s)>
- Validated against: <library or method>
- Review records: docs/reviews/<record>
- Peeks logged: <date - what was looked up and why>

Explain-back:
1. What it does:
2. Key design decision:
3. One alternative:
4. One failure mode:
5. Complexity / cost:

What the reviewers caught:
Blank-file redo: <date> - <result>
```

### `ingest/chunker.py` (P1-08)

- Status: Not started
- Requirement: `chunk_document(doc, max_tokens, overlap) -> list[Chunk]`;
  heading-aware splitting, overlap, carries tenant/policy/version/
  effective-date/role metadata onto each chunk.
- Validated against: property tests (no text lost, sizes bounded)

### `retrieval/repository.py` + `sql/` (P1-09)

- Status: Not started
- Requirement: parameterized pgvector query with tenant/role/effective-date
  filters under RLS; HNSW index DDL; EXPLAIN ANALYZE notes.
- Validated against: EXPLAIN ANALYZE; recall vs exact search

### `eval/metrics.py` (P1-10)

- Status: Not started
- Requirement: precision@k, recall@k, MRR, nDCG@k; `bootstrap_ci`;
  `paired_bootstrap_diff`.
- Validated against: scikit-learn `ndcg_score`; scipy `bootstrap`

### `retrieval/bm25.py` (P1-11)

- Status: Not started
- Requirement: BM25 from scratch (tokenize, IDF, k1, b); compare rankings
  with Postgres full-text on 20 queries.
- Validated against: `rank_bm25` package; Postgres full-text rankings

### `retrieval/fusion.py` (P1-11)

- Status: Not started
- Requirement: `reciprocal_rank_fusion(rankings, k=60)`.
- Validated against: hand-computed examples

### `generation/context_packer.py` (P1-12)

- Status: Not started
- Requirement: `pack_context(chunks, token_budget) -> Context`; dedupe,
  order, assign citation IDs, stop at budget.
- Validated against: token counts from the model tokenizer

### `generation/citations.py` (P1-13)

- Status: Not started
- Requirement: Pydantic answer schema;
  `validate_citations(answer, context) -> list[Violation]`.
- Validated against: adversarial fake-citation cases

### `llm/provider.py` (P1-13)

- Status: Not started
- Requirement: provider protocol; async call with timeout, retries with
  exponential backoff + jitter (retryable errors only), streaming,
  token/cost accounting.
- Validated against: fault-injection tests with a fake client

### `eval/judge_agreement.py` (P1-14)

- Status: Not started
- Requirement: Cohen's kappa between LLM judge and human labels.
- Validated against: scikit-learn `cohen_kappa_score`

### `api/limits.py` (P1-15)

- Status: Not started
- Requirement: token-bucket rate limiter; per-tenant token budget.
- Validated against: time-controlled unit tests

### `tests/test_isolation.py` (P1-09, P1-15)

- Status: Not started
- Requirement: cross-tenant/cross-role tests at SQL and API layers.
- Validated against: zero leaked rows/chunks

## Timed re-implementation drills (Project 1)

Complete from a blank file, plain Python, before interviewing on Project 1,
then diff against the repository version.

| Drill | Target time | Date | Time taken | Notes |
|---|---|---|---|---|
| Mini RAG: chunk, embed (given function), cosine top-k with NumPy, BM25, RRF, cited answer | 45 min | | | |
| precision@k, recall@k, MRR, nDCG@k + bootstrap CI | 20 min | | | |
| Async LLM client: semaphore concurrency, timeout, retry with backoff + jitter | 20 min | | | |
| Token-bucket rate limiter | 15 min | | | |
| LRU cache with TTL | 15 min | | | |
