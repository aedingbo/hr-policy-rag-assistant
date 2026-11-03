# Project 1 — RAG Knowledge Intelligence Platform

Application: HR Policy & Benefits Knowledge Assistant

## Implementation Checklist (v2.0)

**Authoritative requirements:** `docs/reference/2026 Final AI Bridge Portfolio.pdf` (Reconciled execution edition, October 2026). It supersedes `AI_Bridge_Portfolio_Plan_ADVANCED_PRODUCTION_ENGINEERING.pdf`, `AI_Bridge_Portfolio_Plan_CLEAN_FLOW_REVIEWED.pdf` and all earlier versions. This checklist organizes its Project 1 implementation requirements; it does not supersede the plan.

**Workflow rule:** The engineer owns prioritization and approves work. Claude Code may recommend actions but must not independently expand scope, change task IDs, or declare tasks complete without evidence and engineer approval.

**Status values:** `Not started` · `In progress` · `Blocked` · `Verified`.

**Requirement levels:** Every deliverable in the task table is **Mandatory** unless marked **(Conditional)** or **(Optional)**. Conditional items are included only when their stated condition is met and recorded in an ADR. Optional items are never prerequisites for completion. See [Conditional and optional items](#conditional-and-optional-items).

**Current task:** `P1-01` — In progress. Claude Code extension, repository folder and `CLAUDE.md` are set up; `CLAUDE.md` is aligned to the 2026 Final PDF; the `HANDWRITTEN.md` ledger template and `docs/reviews/` exist. Git (`main` branch), `.gitignore`, `.env.example`, the Python 3.12.4 virtual environment, the approved repository layout, `pyproject.toml`, the initial Docker configuration and the README are in place. uv 0.13.7 is installed, `uv.lock` is generated and the initial commit `dc0cbc8` exists on `main`. Remaining: engineer verification of P1-01.

**Every task requires:** implementation or artifact; objective completion check; relevant tests/verification evidence; metrics reported with sample size and 95% confidence interval where applicable; a `HANDWRITTEN.md` entry for any hand-written file; a review record in `docs/reviews/` when the review cadence applies; decision log (ADR) entry if a significant choice was made. Only then mark **Verified**.

| ID | Task | Status | Purpose | Deliverable | Completion check | Hand-written files |
|---|---|---|---|---|---|---|
| P1-01 | Initialize repository | In progress | Establish Git, isolated Python development and project governance files | One consistent repository layout, proposed for engineer approval during P1-01, covering application, ingestion, retrieval, evaluation, tests, UI, infrastructure (including Terraform folder) and data areas, using the PDF's exact hand-written paths with no duplicate directories (for example `ingestion/` vs `ingest/`, `evaluation/` vs `eval/`); README; .gitignore; environment template; Docker configuration; CLAUDE.md; `HANDWRITTEN.md` ledger; `docs/reviews/`. No placeholder files for hand-written modules | VS Code opens repository; Git commit succeeds; Python environment works; approved layout and required files exist | — |
| P1-02 | Local development infrastructure | Not started | Run PostgreSQL/pgvector locally with persistence | Docker Compose for PostgreSQL/pgvector and health check | Database remains intact after container restart | — |
| P1-03 | Data model and provenance | Not started | Define three fictional HR client companies, role scopes and policy metadata with source tracking | Tenant specification for three fictional client companies with deliberate per-tenant policy differences; role scopes (including manager-only and HR-only); policy inventory/version registry in CSV/JSON with `tenant_id`, `policy_id`, `version`, `effective_from`, `effective_to`, `approval_status`, `access_scope`, `owner`, `source_uri`; source/license manifest; synthetic authoring rules | IDs, effective dates, supersession chains, tenant/role scopes and references satisfy validation checks; the same policy topic has different rules per tenant | — |
| P1-04 | Source collection and starter corpus | Not started | Author a reviewed starter HR policy corpus for each tenant | Per tenant: employee handbook, benefits overview/enrollment, PTO and leave, remote work/relocation, onboarding, expenses/reimbursement, superseded versions and role-restricted documents, as original synthetic PDF/Markdown; raw copies preserved untouched; license-verified public templates used only as reference; generated content tagged; data card draft; validation report | Sources parse; manual review confirms source accuracy, conflicts, supersession and permissions | — |
| P1-05 | Versioned larger dataset | Not started | Build reproducible data only after starter review | Versioned full corpus for all three tenants; data manifest; checksums; generation rules and prompts; data card (source URLs/names, license/usage notes, generation rules, validation, known limitations); repeatable ingestion instructions | Another developer can verify/download/ingest without paying to regenerate | — |
| P1-06 | Ground-truth benchmark | Not started | Fix a fair, tenant-aware evaluation set | Labeled synthetic HR cases (employee questions, departments, employment/location contexts, ambiguous relocation, outdated-policy conflicts, permission-limited scenarios, cross-tenant and cross-role probes); 150–300 versioned questions, each with tenant, employee-context fields, expected facts, approved current source IDs, citation passages, effective-date rules, conflict/no-answer labels, escalation expectation and permission boundaries; versioned adversarial set (prompt injection, retrieval poisoning, conflict, no-answer, cross-tenant, cross-role) | Expected facts and citations manually verified against sources; set includes easy, ambiguous, conflicting, outdated and no-answer cases, plus a superseded remote-work policy, contradictory PTO language, missing eligibility and restricted documents | — |
| P1-07 | Document loading and extraction | Not started | Preserve policy structure and remove PII during ingestion | PDF/Markdown loaders (LangChain used thinly); extraction notebook; PII detection/redaction with Presidio or an equivalent solution plus custom employee-ID recognizers; tests | Headings, lists, tables, effective dates and identifiers preserved; PII detection tests pass; logs record redaction counts, never raw PII | — |
| P1-08 | Splitting and embeddings | Not started | Define traceable chunks and vector representations | Hand-written heading-aware chunker with overlap that carries tenant, policy, version, effective-date and role metadata onto each chunk; embedding selection record (Amazon Titan Text Embeddings default); reusable modules | Property tests pass (no text lost, sizes bounded); metadata and embedding-dimension tests pass | `ingest/chunker.py` |
| P1-09 | Vector indexing and changes | Not started | Maintain an accurate, tenant-isolated pgvector index over time | SQLAlchemy/Alembic schema and migrations; HNSW index DDL; PostgreSQL RLS policies keyed on session tenant and role; parameterized pgvector queries with tenant/role/effective-date filters and iterative index scans; ingest/upsert/search/delete/reindex with content hashes; freshness handling for updates, revocation, supersession and permission changes; EXPLAIN ANALYZE notes | Updated, deleted and superseded documents handled; unchanged documents skipped; zero leaked rows at the SQL layer; freshness test shows no stale/current-policy mix-ups and records indexing lag | `retrieval/repository.py` + `sql/`; `tests/test_isolation.py` (SQL layer) |
| P1-10 | Semantic retrieval baseline | Not started | Measure baseline quality before improvements | Frozen evaluation run: Precision@K, Recall@K, MRR, nDCG@K where graded labels exist, bootstrap 95% confidence intervals and failure report; recall with vs without authorization filters across HNSW `ef_search` and iterative-scan settings | Repeatable results on fixed benchmark with sample sizes and confidence intervals; recall loss from filtering quantified and addressed | `eval/metrics.py` |
| P1-11 | Retrieval improvements | Not started | Compare justified retrieval enhancements one factor at a time | Hybrid PostgreSQL full-text/BM25 + vector retrieval fused with RRF; hand-written BM25 compared with Postgres full-text on 20 queries; chunk-size/overlap grid; embedding-model comparison; filter experiments; reranker **(Conditional)**; experiment table (chunking, embeddings, top-k, filters, reranker, Precision@K, Recall@K, p50/p95 latency, cost, confidence intervals; citation accuracy and groundedness columns completed once P1-13 exists) | Same evaluation set; corpus and splits held constant; paired comparisons on the same cases; filter-leak count = 0 | `retrieval/bm25.py`; `retrieval/fusion.py` |
| P1-12 | System prompt and answer orchestration | Not started | Manage evidence-driven question answering safely | Versioned system prompt; hand-written context packer (dedupe, order, citation IDs, token budget); answer control flow for cite, abstain, clarify and escalate, including outdated/conflicting versions; ADR: LangGraph vs simpler Python control flow (LangGraph **Conditional**) | No-evidence, conflict, outdated, missing-context and adversarial paths behave as specified; retries bounded | `generation/context_packer.py` |
| P1-13 | Claude runtime generation | Not started | Produce structured grounded answers | Bedrock provider interface (async calls, timeouts, retries with exponential backoff and jitter on retryable errors only, streaming, token/cost accounting); Bedrock prompt caching; Pydantic answer schema; citation validator; tests | Every citation references a retrieved chunk and quoted text exists in the source, or the system abstains, on held-out questions; fault-injection tests pass with a fake client | `llm/provider.py`; `generation/citations.py` |
| P1-14 | Challenger and long-context benchmark | Not started | Compare answer providers and RAG vs long context fairly | At least 60 human-labeled answer assessments completed by the engineer after generation (P1-13) is working and before judge calibration; judge calibration (Cohen's kappa against those labels); DeepSeek/Qwen challengers (via Bedrock where available) with identical prompts, context budgets, held-out questions, rubric and citation validator; single-tenant RAG vs whole-handbook long-context with Bedrock prompt caching; ADRs: Claude vs DeepSeek/Qwen, RAG vs long context | Judge agreement recorded before judge scores are used; groundedness, citation attribution, no-answer accuracy, schema validity, tokens, latency, USD/query and cost per acceptable answer (including retries/reasoning costs) reported with confidence intervals | `eval/judge_agreement.py` |
| P1-15 | FastAPI and access controls | Not started | Expose a validated API and isolate tenants, users and sessions | Typed endpoints: upload/validate/list/activate/reindex policies; query with knowledge-base scope and optional non-sensitive employee context; evidence, citation, model, eval, usage and health; tenant scope from the authenticated session only; per-user/session separation; usage metering; token-bucket rate limiting and per-tenant token budgets; streaming; PII redaction of logged queries | API contract and permission tests pass; zero cross-tenant/cross-role leakage at the API layer; tenant scope cannot be set from user input | `api/limits.py`; `tests/test_isolation.py` (API layer) |
| P1-16 | Streamlit interface | Not started | Provide an end-to-end interactive demo | Ask HR workspace (knowledge-base scope, optional employee context, question, Ask policy assistant; streaming answer, numbered citations, excerpts, version/effective date, abstain/clarify/escalate); Source library (upload, select active documents, permissions/version metadata, reindex, ingestion status, PII redaction count); Evaluation/operations (metrics with confidence intervals, leakage count, model comparison, RAG vs long context, CI gate status); retrieval-trace, security and usage tabs | End-to-end workflow runs through UI and API; switching to another tenant's user returns that tenant's policy and never the first tenant's | — |
| P1-17 | Security, observability, CI gates and load testing | Not started | Catch regressions, trace failures/cost and measure performance | Versioned red-team suite (injection, poisoning, conflict, no-answer, cross-tenant, cross-role) and security report with OWASP LLM coverage; structured logs; OpenTelemetry + one LLM tracing tool (LangSmith or Langfuse, with ADR); usage controls; CI quality gate with thresholds set after baseline (groundedness, retrieval, citation correctness, structured-output validity, security, access-control tests, p95 latency budget); locust or k6 load test at 1, 10 and 50 concurrent users | Deliberately regressed version fails the deployment gate; leakage tests report zero; load-test report gives p50/p95, error rate, throughput, cost per 1,000 queries and cache hit rate | — |
| P1-18 | AWS deployment | Not started | Prove operation in cloud | Terraform-managed S3, RDS PostgreSQL/pgvector, ECR, ECS/Fargate, API Gateway or ALB, Secrets Manager, least-privilege IAM, Bedrock, CloudWatch/OpenTelemetry tracing and budget/cost alerts; ADR: pgvector vs OpenSearch/Chroma; runbook | Cloud health, tenant isolation, rollback and reproducible Terraform setup verified; load test repeated against the deployed service | — |
| P1-19 | Final benchmarking and portfolio proof | Not started | Prove engineering/business impact | Deployed held-out benchmark; README (WHY, HOW, measured outcome, limitations); architecture diagram; data card; reports (RAG optimization, tenant isolation, security, load, RAG vs long context); failure traces and fixes; time-to-answer vs manual baseline; demo; ADR log; review-record summary (accepted/rejected counts, most important caught defect); completed `HANDWRITTEN.md` and timed drills; public technical write-up; one-page interview kit | All public numerical claims tie to measured runs with sample sizes and confidence intervals; one measured improvement and remaining failure categories recorded; evaluation set, retrieval grid, citation/abstention tests, update/reindex checks, provider comparison, report and CI gate are runnable by a reviewer | — |

## Conditional and optional items

| Item | Level | Condition / note | Related step |
|---|---|---|---|
| LangGraph | Conditional | Only for a genuinely stateful, multi-step policy workflow; decided by ADR vs simpler Python control flow | P1-12 |
| Bedrock Rerank or cross-encoder | Conditional | Only after the baseline; keep only with measured benefit | P1-11 |
| Caching and model routing | Conditional | Only where measurement shows benefit; no runtime routing without evidence | P1-13, P1-14 |
| Amazon OpenSearch | Conditional | ADR alternative/scale benchmark; not built unless a measured need appears | P1-18 |
| nDCG@K | Conditional | Reported where graded relevance labels exist | P1-10, P1-11 |
| Chroma | Optional | Local experiment only; not a production dependency | — |
| Query rewriting/HyDE, contextual retrieval ablations | Optional | Stretch goal | P1-11 |
| DeepSeek synthetic document generation | Optional | Proposal only; requires separate engineer approval and budget authorization | P1-04, P1-05 |

Not optional: Terraform, exactly one of LangSmith/Langfuse, Presidio or equivalent PII redaction, locust or k6 load testing, and tenant/role-aware retrieval.

## Staged milestones and review cadence

Independent DeepSeek/Qwen review (run locally or through Bedrock) is required at least at each stage milestone below, and on any change touching authorization, data deletion, evaluation code or CI gates. Every hand-written file is reviewed. Store records in `docs/reviews/`.

| Stage | Completion evidence | Steps |
|---|---|---|
| Core implementation | Working semantic top-k retrieval and cited answer path; evaluation manifest and policy-index version; first review record | P1-01 to P1-10, P1-12, P1-13 |
| Production hardening | Authorization before retrieval, RLS, PII redaction, freshness, cross-tenant isolation; negative-case security fixtures; zero-leak report | P1-07, P1-09, P1-15, P1-17 |
| Evaluation & optimization | Experiment table with confidence intervals; RAG vs long context; load test | P1-11, P1-14, P1-17 |
| Final benchmark & documentation | Provider comparison, CI rejection log, deployed evidence, review summary, write-up, interview kit | P1-18, P1-19 |

A stage review is due when the last listed step of that stage is ready for verification.

## Hand-written core register

Details and explain-back entries live in `HANDWRITTEN.md`.

| File | Step | Developer tests written | Library validation | Review record | `HANDWRITTEN.md` entry | Blank-file redo |
|---|---|---|---|---|---|---|
| `ingest/chunker.py` | P1-08 | Not started | Not started | Not started | Not started | Not started |
| `retrieval/repository.py` + `sql/` | P1-09 | Not started | Not started | Not started | Not started | Not started |
| `eval/metrics.py` | P1-10 | Not started | Not started | Not started | Not started | Not started |
| `retrieval/bm25.py` | P1-11 | Not started | Not started | Not started | Not started | Not started |
| `retrieval/fusion.py` | P1-11 | Not started | Not started | Not started | Not started | Not started |
| `generation/context_packer.py` | P1-12 | Not started | Not started | Not started | Not started | Not started |
| `generation/citations.py` | P1-13 | Not started | Not started | Not started | Not started | Not started |
| `llm/provider.py` | P1-13 | Not started | Not started | Not started | Not started | Not started |
| `eval/judge_agreement.py` | P1-14 | Not started | Not started | Not started | Not started | Not started |
| `api/limits.py` | P1-15 | Not started | Not started | Not started | Not started | Not started |
| `tests/test_isolation.py` | P1-09, P1-15 | Not started | Not started | Not started | Not started | Not started |

## Task execution protocol

1. Read `CLAUDE.md`, the authoritative Project 1 plan, and this checklist.
2. Locate the current task ID and summarize its purpose, dependencies, expected deliverable and completion check.
3. Identify applicable production engineering and security concerns (CLAUDE.md Section 14), or mark them N/A with a reason.
4. Propose the smallest useful implementation increment. Identify any uncertainty or proposed engineering decision, and which files are hand-written.
5. Wait for the engineer's approval before changing files, installing dependencies, triggering paid services, or proceeding beyond the approved increment.
6. Implement only the approved increment; explain code, inputs, outputs, important syntax and tradeoffs. For hand-written files, the engineer creates the files and writes the implementation and tests; Claude explains concepts, gives hints, suggests test cases, reviews and runs tests, helps interpret failures and reviews completed work, and never creates placeholder files.
7. Run appropriate local tests, linters, type checks, security checks and performance tests.
8. Independently review with DeepSeek/Qwen when the review cadence applies, without disclosing secrets; verify findings empirically and store the record in `docs/reviews/`.
9. Record evidence and significant decisions. Ask the engineer to approve completion.
10. After approval, update task status to **Verified**, set the next approved step to **In progress**, and keep `CLAUDE.md` current status aligned.
11. Commit the checklist together with the verified code/doc changes; never silently add or renumber scope.

## Progress and verification log

| Date | Task ID | Evidence (command, test, link or report) | Engineer approval | Notes |
|---|---|---|---|---|
| 2026-10-23 | P1-01 | Project folder and Claude Code setup; `CLAUDE.md` read-only verification passed | Partial only | Git and Python setup are still pending |
| 2026-11-03 | P1-01 | `CLAUDE.md` and this checklist aligned to `2026 Final AI Bridge Portfolio.pdf`; `HANDWRITTEN.md` template and `docs/reviews/` created; authoritative PDF verified readable (76 pages) | Approved (documentation alignment only; P1-01 remains In progress) | Git, Python environment, README, .gitignore, environment template, Docker configuration and folder layout still pending |
| 2026-11-03 | P1-01 | `git status`: repository on `main`, no commits yet, only intended files untracked. `git check-ignore`: `.env`, `.venv/`, `docs/reference/` PDF and Terraform state ignored; `.env.example`, `pyproject.toml`, `.python-version`, `Dockerfile`, `.dockerignore`, `README.md`, `data/` trackable. `.venv` reports Python 3.12.4 with only `pip==24.0` installed. `pyproject.toml` parses with `tomllib`; listed packages `api`, `ingest`, `retrieval`, `eval` exist; `requires-python` satisfied. Approved directories created with empty markers; no hand-written module files exist. Dockerfile and `.dockerignore` prepared (not built); Docker 27.5.1 present. | Pending | uv not installed and `uv.lock` not yet created; no commit yet, so the "Git commit succeeds" check is not met |
| 2026-11-03 | P1-01 | `winget install --id=astral-sh.uv`: uv 0.13.7 installed (installer hash verified). Dockerfile `UV_VERSION` set to 0.13.7 (Unix line endings kept). `uv lock` (managed Python downloads disabled): resolved 1 package, `uv.lock` created; `uv lock --check` passes. `.venv` snapshot identical before and after (1,031 files, same size, same `pyvenv.cfg` hash, only `pip==24.0`). `git add --dry-run --all`: 20 intended files; secret-pattern scan found no matches; no `.env`, `.venv`, private PDF, Terraform state, keys or credentials among candidates. | Pending | Commit not made: Git `user.name` is unset and the public author identity needs an engineer decision before the first commit |
| 2026-11-03 | P1-01 | Repository-local `user.name` and `user.email` both set to `aedingbo@outlook.com` (engineer decision). Staged exactly the 20 reviewed files (no unexpected files). `git commit` succeeded: root commit `dc0cbc81e592c6800ea35f4daeaa540897440284` on `main` (author and committer metadata rewritten locally before any push), 20 files, 1,845 insertions. Not pushed. | Pending | "Git commit succeeds" check met |
| 2026-11-03 | P1-01 | Added `.gitattributes` pinning `Dockerfile` and `.dockerignore` to LF because Git for Windows sets `core.autocrlf=true`; `git ls-files --eol` shows `eol=lf` applied. Committed together with these evidence updates as the second commit on `main`. | Pending | Awaiting engineer verification of P1-01 |

## Sprint planning template

- **Sprint objective:**
- **Selected task IDs (from this checklist):**
- **Dependencies and risks:**
- **Definition of done / tests:**
- **Engineer approval:**
- **Sprint review outcome and evidence:**

> Note: Sprint planning selects from approved project tasks; it does not automatically authorize unrelated work or paid actions.
