
# Project 1 — RAG Knowledge Intelligence Platform

Application: HR Policy & Benefits Knowledge Assistant

## 1. Project Objective

Build a production-grade, permission-aware
Retrieval-Augmented Generation (RAG) application for
HR / employee operations.

Primary users:
- Employees searching for policy guidance
- HR staff validating answers

The corpus covers three fictional HR client companies
(tenants). Each has its own employee handbook, benefit
plans and policy versions, plus role-restricted
documents (for example manager-only and HR-only).

The assistant must:
- Answer only from supplied, approved documents,
  applicable effective dates, permissions and
  available employee context.
- Cite the current policy with verifiable citations.
- Surface outdated, superseded or conflicting versions.
- Abstain when trustworthy evidence is insufficient.
- Clarify or escalate when employee or location
  context is missing.
- Never retrieve another tenant's or a higher role's
  documents. Zero cross-tenant or cross-role exposure
  is a release requirement.

Example question:
"What does our remote-work policy require if I move to
another state, and who needs to approve it?"

The goal is to demonstrate production AI engineering,
not simply a working chatbot or notebook experiment.

Engineering standard:
WHY -> HOW -> MEASURE -> IMPROVE -> DEPLOY -> PROVE -> EXPLAIN

## 2. Authoritative Project Requirements

The sole authoritative specification is:
`docs/reference/2026 Final AI Bridge Portfolio.pdf`
(Reconciled execution edition, October 2026).

It supersedes
`AI_Bridge_Portfolio_Plan_ADVANCED_PRODUCTION_ENGINEERING.pdf`,
`AI_Bridge_Portfolio_Plan_CLEAN_FLOW_REVIEWED.pdf` and
all earlier portfolio versions. Where they conflict,
the 2026 Final PDF wins.

Project 1 is first in the portfolio build order.
Project numbers are fixed; build positions do not
renumber projects.

`docs/PROJECT_1_BUILD_CHECKLIST.md` organizes the PDF's
Project 1 requirements into stable steps P1-01 to
P1-19. It does not supersede the PDF.

Requirement levels used in this file and the checklist:
- Mandatory: required for Project 1 completion.
- Conditional: include only when the stated condition
  is met and the decision is recorded (usually in an
  ADR).
- Optional: stretch work; never a prerequisite for
  completion.

Do not:
- Redesign the portfolio.
- Expand the approved scope without permission.
- Introduce unnecessary services or dependencies.
- Replace approved technologies without justification.
- Implement unapproved architectural changes.
- Assume proposed decisions have already been approved.
- Treat optional or conditional items as prerequisites.

Distinguish between:
- Confirmed portfolio requirements
- Approved implementation decisions
- Proposed implementation choices
- Optional future improvements

The developer must approve significant changes.

If the portfolio PDF is not available in the repository,
request access to it rather than inventing requirements.

## 3. Employer and Data Boundaries (Mandatory)

- Use only personal hardware, accounts and time.
- Never use employer or client data, code, internal
  schemas, documents, screenshots or internal
  workflows, including anonymized versions.
- Build from public standards and fictional companies.
  Record provenance and licensing in data cards.
- Keep employer experience and portfolio repositories
  separate. Do not imply an employer endorses the work.
- The developer reviews employment agreements (IP
  assignment, outside activities, confidentiality)
  before publishing HR/payroll-adjacent work.
- Never send private employee records, credentials or
  proprietary data to unapproved model services.

## 4. Technology Stack

### Mandatory

Core AI:
- Python
- Amazon Bedrock / Claude for answer generation,
  including prompt caching
- Amazon Titan Text Embeddings via Bedrock (default
  embedding model)
- Hybrid retrieval: pgvector + PostgreSQL full-text /
  BM25, fused with reciprocal rank fusion (RRF)
- Structured LLM outputs with citation validation
- LangChain used thinly: document loaders and text
  splitters only. Retrieval, fusion, context packing
  and citation validation are hand-written (Section 15).

Data and storage:
- PostgreSQL + pgvector (HNSW) as the default vector
  store, plus PostgreSQL full-text search
- PostgreSQL row-level security (RLS) for tenant/role
  isolation
- SQLAlchemy + Alembic for queries, transactions and
  migrations
- SQL for policy versions, effective dates, permissions,
  retrieval/evaluation outcomes and benchmark analysis
- Docker Compose with persistent local database storage
- Amazon S3 for original source documents
- Amazon RDS for PostgreSQL in AWS

Privacy:
- Presidio or an equivalent PII detection/redaction
  solution

Backend:
- FastAPI, Pydantic, typed request/response models
- Asynchronous endpoints where appropriate
- API validation and error handling
- Streaming responses

Frontend:
- Streamlit over FastAPI

Quality and performance:
- pytest, Ruff, Pyright, Bandit
- locust or k6 for load testing

Observability:
- OpenTelemetry (X-Ray-compatible tracing)
- Amazon CloudWatch
- One LLM tracing tool: LangSmith or Langfuse (choose
  one and record the decision in an ADR)

Infrastructure:
- Docker
- Terraform for all AWS resources (required)
- GitHub Actions CI/CD
- AWS ECS/Fargate and Amazon ECR
- Amazon API Gateway or Application Load Balancer
- AWS Secrets Manager and least-privilege IAM
- AWS Budgets / cost alerts

Development:
- Visual Studio Code and Jupyter notebooks inside VS
  Code (experiments only)
- Reusable Python application modules
- Git and GitHub
- Claude Code for implementation, except the
  hand-written core (Section 15)
- DeepSeek or Qwen for independent code review, run
  locally or through Bedrock (Section 5)

### Conditional

- LangGraph: only if a genuinely stateful, multi-step
  policy workflow appears. Requires an ADR comparing
  LangGraph with simpler Python control flow. Not
  needed for basic RAG.
- Bedrock Rerank or a cross-encoder: only after the
  baseline; keep only if measured precision/recall
  benefit justifies its cost.
- Caching and model routing: only where measurement
  shows they are useful.
- Amazon OpenSearch: documented ADR alternative and
  scale benchmark; not built unless a measured need
  appears.

### Optional

- Chroma: local experiment only; not a production
  dependency.
- Query rewriting/HyDE and contextual retrieval
  ablations (stretch goal).

Hugging Face and Pinecone are not project dependencies.

Build and validate locally before deploying to AWS.

AWS setup order: enable MFA; add a budget/cost alert;
use IAM development access instead of root; request
Bedrock model access; configure local environment
variables and Secrets Manager; create GitHub CI roles
and secrets; provision project resources only after the
local vertical slice works; tear down unused resources.

Do not provision paid services without explicit approval.

## 5. Model Strategy

### Development Assistance

Claude Code is the primary implementation assistant.

Use Claude for:
- Application code outside the hand-written core
- Scaffolding around hand-written modules
- Refactoring
- Debugging
- Automated tests for non-hand-written code
- Documentation
- Explaining implementation decisions
- Reviewing architecture and integration points
- Explaining concepts, giving hints, reviewing and
  helping test hand-written modules (Section 15)

Claude does not generate the initial implementation of
hand-written core modules.

Claude is not the sole authority on code correctness.

### Independent Code Review

DeepSeek or Qwen serves as the independent second-model
reviewer. Run it locally or through Bedrock where
available, not through a third-party public API, so
code and data stay within approved services.

Review cadence (Mandatory):
- At least at each staged milestone: Core
  implementation, Production hardening, Evaluation &
  optimization, Final benchmark.
- On any change touching authorization, data deletion,
  evaluation code or CI gates.
- On every hand-written core file.

The reviewer must examine:
- Correctness, logical errors and edge cases
- Security: authorization bypass, SQL injection,
  XSS/CSRF where applicable, exposed secrets, unsafe
  input, data isolation
- Tenant/role isolation
- Database integrity: transactions, indexing,
  migrations, RLS, concurrency
- Reliability: race conditions, resource leaks,
  background jobs, retries/recovery
- Efficiency: algorithmic complexity, N+1 and
  unindexed queries, inefficient vector retrieval,
  unnecessary or repeated LLM/API calls, token waste in
  prompts and context, blocking calls in async code,
  memory use
- Error handling and maintainability
- Test quality: tests that cannot fail, weak or missing
  assertions, over-mocking, missing negative/adversarial
  cases, and correctness of evaluation code (metric
  formulas, leakage between splits)
- AI-generated-code risks: plausible but wrong logic,
  invented or misused library APIs, silently swallowed
  exceptions, hard-coded values, duplicated code,
  unnecessary or unpinned dependencies
- AI-specific security: prompt injection, untrusted
  model output, malicious document uploads
- LLM token consumption and cost

Required reviewer output for every finding:
- Severity
- Affected file/function or code
- Failure mechanism
- Proposed correction
- Reproducible test
- Classification: confirmed defect, potential risk or
  optional improvement

Measure, don't trust:
- Confirm every efficiency finding with a profiler,
  EXPLAIN ANALYZE, a benchmark or a load test, before
  and after the fix.
- For every missing-test finding, add the test and
  record whether it failed on the old code.
- Record a finding that cannot be reproduced as
  "not confirmed"; do not silently drop it.

Decision and verification:
- The developer reviews findings.
- Claude explains and validates each recommendation and
  accepts or rejects it with rationale.
- Apply only approved fixes; rerun tests and evals.
- Do not automatically merge second-model suggestions.
- Do not treat an LLM review as proof that code is
  secure.

Store review records in `docs/reviews/`: findings,
accepted/rejected decisions, fixes, test evidence,
residual risks and reviewer model/version. Summarize
accepted/rejected counts and the most important caught
defect in the project write-up.

Additional reviewer (optional, developer-initiated): ChatGPT may be consulted as
an extra independent reviewer for significant decisions, security-sensitive
configuration, tradeoff comparisons, difficult issues, metric evaluation and
milestone approval. It does not replace the DeepSeek/Qwen reviews above. Never
paste secrets, credentials, .env values, private specification content or
personal data into it.

Do not claim code is optimized without evidence.

### Runtime Model Strategy

Claude through AWS Bedrock is the primary runtime model.

DeepSeek/Qwen are offline challengers, run through
Bedrock where available.

Compare Claude and challengers using identical:
- Frozen document collections
- Held-out evaluation questions
- Expected answer facts
- Citation requirements and citation validator
- Prompts and context/evidence budgets
- Retrieval evidence
- Evaluation rubric

Measure:
- Answer correctness and groundedness
- Citation accuracy and attribution
- No-answer accuracy and appropriate abstention
- Structured output (schema) validity
- Latency
- Reliability and retries
- Input/output/reasoning token usage
- Total cost, USD per query and cost per acceptable
  answer

Long-context baseline (Mandatory): for a single
tenant's handbook, compare RAG against sending the whole
handbook with Bedrock prompt caching. Report quality,
latency, cost per query and where each approach wins.
Record the decision in an ADR.

Do not assume any model or approach wins.

Do not add dual-model routing, review, or fallback
unless justified by testing.

Keep development assistance, document generation,
and runtime model evaluation separate.

Exact model versions and endpoints must be selected
using current official documentation.

## 6. Data Generation, Provenance and Ground Truth

### HR Policy Corpus (Mandatory)

For each of the three fictional client companies:
- Employee handbook
- Benefits overview and enrollment
- PTO and leave
- Remote work and relocation
- Onboarding
- Expenses and reimbursement
- Superseded policy versions
- Role-restricted documents (for example manager-only,
  HR-only)

Create the same policy topic with deliberately
different rules per tenant so leakage is detectable.

Author original synthetic PDF/Markdown policies.
Preserve raw copies untouched in local raw storage and
later S3. License-verified public templates may be used
only as supplementary reference material, never as a
fictional company's approved policy.

### Policy Inventory and Version Registry

Maintain a CSV/JSON registry with:
- tenant_id
- policy_id
- version
- effective_from
- effective_to
- approval_status
- access_scope (role scope)
- owner
- source_uri

Each document must have a stable source identifier.

### Synthetic HR Cases

Generate fictional employee questions, departments,
employment/location contexts, ambiguous relocation
cases, outdated-policy conflicts, permission-limited
scenarios, and cross-tenant and cross-role probing
questions. Label every synthetic record and record the
authoring rules.

### Ground Truth (Mandatory)

Create a version-controlled benchmark of 150-300
questions. Each record includes:
- Tenant
- Employee-context fields
- Expected answer facts
- Approved current source IDs
- Citation passages
- Effective-date rules
- Conflict and no-answer labels
- Escalation expectation
- Permission boundaries

Include easy, ambiguous, conflicting, outdated and
no-answer cases. Explicitly test a superseded
remote-work policy, contradictory PTO language,
missing eligibility and restricted documents.

Prepare the ground truth during P1-06. After answer
generation is working (P1-13), and before judge
calibration or any reliance on judge scores (P1-14),
the developer completes at least 60 human-labeled
answer assessments.

Expected facts and citations must be verified against
source documents, not blindly accepted from an LLM.

### Adversarial Set (Mandatory)

Version-controlled cases for prompt injection,
retrieval poisoning, conflicting evidence, no-answer
behavior, cross-tenant access and cross-role access.

### Generation Process

Generate a small sample first.

Review the sample before scaling.

Do not generate a large dataset without approval.

Optional proposal: DeepSeek may be evaluated for
inexpensive synthetic document generation. It requires
separate developer approval and budget authorization,
and must follow Section 3.

No paid generation is authorized automatically.

### Data Quality

Validate:
- Required fields and document structure
- Factual consistency within each tenant
- Deliberate, documented differences across tenants
- Cross-document references
- IDs and relationships
- Effective dates, chronology and supersession
- Tenant and role scope
- Duplicate content
- File integrity
- Metadata and source attribution

Valid JSON alone does not prove factual consistency.

Do not count multiple file formats of identical content
as multiple unique documents.

### Reproducibility

Maintain:
- Small starter dataset
- Versioned full dataset
- Data manifest
- Checksums
- Generation rules and prompts
- Data card: source URLs/names, license/usage notes,
  generation rules, validation, known limitations
- Data validation reports
- Repeatable ingestion instructions

Another developer must be able to reproduce the project
without paying to regenerate its original dataset.

## 7. Document Processing

Supported formats:
- Policy documents: PDF and Markdown
- Policy registry: CSV/JSON

Use LangChain loaders and splitters thinly.

Inspect extracted text before implementing cleanup rules.

Preserve meaningful:
- Headings
- Lists
- Tables
- Effective-date and eligibility statements
- Approval requirements
- Policy and version identifiers
- Document references

Explain each document loader and why it was selected.

### PII Detection and Redaction (Mandatory)

- Use Presidio or an equivalent solution, plus custom
  recognizers for employee IDs.
- Apply to uploaded documents and logged queries.
- Log redaction counts, never raw PII.
- Test detection and redaction.

### Chunking

The chunker is hand-written (Section 15).

- Heading-aware splitting with overlap
- Carry tenant, policy, version, effective-date and
  role metadata onto each chunk
- Property tests: no text lost, sizes bounded

Evaluate chunk size and overlap with a controlled grid.

Document:
- Splitting strategy
- Chunk size
- Chunk overlap
- Header handling
- Metadata preservation
- Source traceability

Do not automatically remove whitespace or formatting
that carries meaning.

### Embeddings

Default: Amazon Titan Text Embeddings via Bedrock.
Compare embedding models in the evaluation grid.

Document:
- Model provider and version
- Embedding dimensions
- Similarity measure
- Cost
- Latency
- Storage requirements
- Retrieval performance

### Incremental Ingestion and Freshness

Track document changes with stable identifiers
and content hashes.

Do not unnecessarily reprocess unchanged documents.

Support:
- Initial ingestion
- Re-ingestion
- Document updates
- Revocation and supersession
- Document deletion
- Permission changes
- Index synchronization
- Failure recovery

Freshness test: update, revoke or supersede a policy;
reindex; query both current and historical contexts.
There must be no stale/current-policy mix-ups. Record
indexing lag and a freshness SLA from a measured run.

## 8. Retrieval Engineering and Authorization

### Authorization Inside Retrieval (Mandatory)

- PostgreSQL row-level security keyed on the session's
  tenant and role.
- Authorization filters enforced before retrieval, not
  only in generated text.
- Tenant scope comes from the authenticated session,
  never from user input.
- Parameterized pgvector queries with tenant, role and
  effective-date filters under RLS.
- HNSW index with filtered search using pgvector
  iterative index scans, so filters do not silently
  reduce recall.
- Measure recall with and without filters; vary HNSW
  ef_search and iterative-scan settings.
- Record EXPLAIN ANALYZE notes for retrieval queries.
- Zero leaked chunks in retrieval logs and answers.

### Retrieval Quality

Begin with baseline semantic top-k retrieval.

Establish measurable retrieval quality before
adding more sophisticated methods.

Then evaluate:
- Hybrid retrieval: PostgreSQL full-text/BM25 + vector,
  fused with RRF
- Metadata and authorization filters
- Chunk-size/overlap grid
- Embedding-model comparison
- Reranking (Conditional)

Change one factor at a time. Hold the corpus and splits
constant. Use the same frozen evaluation set and paired
comparisons on the same cases.

Preserve source IDs and chunk metadata for citations.

Track:
- Precision@K and Recall@K
- MRR
- nDCG@K where graded relevance labels exist
- Recall with vs without authorization filters
- Filter-leak count (must be 0)
- Retrieval latency (p50/p95)
- Retrieval failures
- Citation correctness

Do not describe a method as superior without
benchmark evidence.

## 9. Answer Generation and Orchestration

- Put Claude/Bedrock behind a provider interface:
  async calls with timeouts, retries with exponential
  backoff and jitter on retryable errors only,
  streaming, and token/cost accounting.
- Use Bedrock prompt caching.
- Pack context within a token budget: deduplicate,
  order, assign citation IDs, stop at the budget.
- Require cited structured output (Pydantic schema).
- Citation validator: every citation must reference a
  retrieved chunk, and quoted text must exist in the
  source.
- Apply confidence/fallback rules: cite the current
  policy, surface outdated/conflicting versions,
  abstain on insufficient evidence, clarify or escalate
  missing employee/location context.
- Bound all retries.

Default orchestration is plain Python control flow.

LangGraph is Conditional: adopt it only if a genuinely
stateful, multi-step policy workflow appears, and only
after an ADR comparing it with simpler Python control
flow. If adopted, explain graph nodes, edges, state
schema, state changes, conditional branches, retry
limits and error handling.

Do not add complex agent behavior without a clear need.

Do not rely on LLM prompts alone for security,
permissions, or deterministic validation.

## 10. Prompt Engineering

Maintain version-controlled system prompts.

Separate:
- System/application instructions
- Developer-controlled context
- User questions
- Retrieved document content

Treat retrieved documents as untrusted evidence.

Explicitly test:
- Missing evidence
- Conflicting evidence
- Outdated or superseded evidence
- Ambiguous questions
- Missing employee or location context
- Prompt injection
- Retrieval poisoning
- Cross-tenant and cross-role requests
- Unsupported assertions

Require citations when evidence supports an answer.

Abstain when sufficient trustworthy evidence
is unavailable.

Test and version prompt changes rather than
editing prompts without measurement.

## 11. Application Security

Security must be implemented in code and infrastructure,
not solely through system prompts.

Apply:
- Input validation, including uploaded documents
- Authentication and authorization
- Tenant/role isolation with RLS and pre-retrieval
  filters
- Tenant scope from the authenticated session only
- User/session separation
- Least-privilege permissions
- Secure secret management
- PII redaction in documents and logs
- Safe error handling
- Prompt-injection protections
- Treat model output as untrusted
- Data-access boundaries
- Per-tenant token and cost budgets; rate limiting
- API timeout and retry policies

Never hardcode credentials.

Never expose secrets in:
- Source code
- Logs
- Documentation
- Screenshots
- Prompts
- Public repositories

Do not share sensitive code or credentials with
independent reviewers.

Use synthetic or sanitized code samples when necessary.

Include adversarial tests aligned with relevant OWASP
LLM risks, including sensitive information disclosure
(LLM02) and vector/embedding weaknesses (LLM08).

Zero observed failures in a finite test suite does not
establish zero risk.

## 12. Automated Testing and Code Quality

### Required Test Layers

- Unit + schema: parsers, chunker, metrics, Pydantic
  contracts, permission predicates.
- Integration + API contract: real database
  boundaries, migrations, mocked upstream failures,
  file validation, service health.
- Model evaluation: fixed holdout with confidence
  intervals.
- Security and reliability: prompt injection, least
  privilege, secrets, sensitive data, tenant isolation,
  retries/timeouts, graceful failure.
- Performance and cost: latency, throughput, tokens,
  LLM cost, memory.
- Release quality gate (Section 13).

Use deterministic test fixtures.

### Static Analysis
- Ruff for Python linting
- Pyright for static type checking
- Bandit for Python security checks

### Load Testing (Mandatory)

Use locust or k6 at 1, 10 and 50 concurrent users.
Report p50/p95 latency, error rate, throughput, cost
per 1,000 queries and cache hit rate. Run locally
before deployment and against the deployed service.

Choose other profiling tools when performance work
begins. Do not claim performance results without
measurement.

Automated tools complement independent AI review;
they do not guarantee correctness or security.

## 13. Evaluation and Regression Gates

Use the fixed, version-controlled evaluation set and
adversarial set from Section 6.

Combine deterministic evaluation with LLM-as-a-judge.
Before trusting judge scores, measure judge-human
agreement (Cohen's kappa) on at least 60 hand-labeled
answers.

Statistical honesty (Mandatory):
- Every reported metric carries its sample size and a
  95% bootstrap confidence interval.
- Every claimed improvement uses a paired comparison on
  the same cases.

Measure:
- Precision@K, Recall@K, MRR, nDCG@K (where graded)
- Grounded-answer accuracy
- Citation correctness and attribution
- Hallucination / unsupported-answer rate
- Abstention precision and coverage
- Cross-tenant/cross-role leakage count (must be 0)
- Recall with vs without authorization filters
- Average, p50 and p95 latency, including under load
- Token usage, cost per query, cost per 1,000 queries
- Cache hit rate
- RAG vs long-context quality, latency and cost
- Time-to-answer versus a defined manual baseline

Release gate:
- Set thresholds after the baseline is measured.
- Gate on groundedness, retrieval quality, citation
  correctness, structured-output validity, security,
  required access-control tests and a p95 latency
  budget.
- CI/CD must block deployment when approved thresholds
  regress.
- Demonstrate that an intentionally regressed version
  fails the gate.

Improvement loop: baseline -> fixed evaluation set with
provenance -> run and log -> classify failures ->
change one targeted factor -> rerun the same benchmark
-> check regressions, security and statistical
significance -> document measured improvement or honest
non-improvement -> record the decision, limitations and
review record.

Never invent metrics, thresholds or uplift, or use
unmeasured outcomes in documentation or resume bullets.

## 14. Required Code Review Workflow

Before each implementation milestone, Claude identifies
applicable concerns from: authentication vs
authorization, indexing, row-level security, SQL
transactions, schema migrations, concurrency/race
conditions, memory/resource leaks, input validation,
CSRF, XSS, SQL injection, secrets, error handling,
logging/monitoring, unit and integration testing,
webhook signature verification, background jobs and
backup/recovery. Explain why each applies or mark it
N/A with a reason, and propose safeguards and tests
before substantial code changes.

For meaningful AI-assisted implementation changes:

1. Confirm the requested task and scope.
2. Claude proposes an implementation approach.
3. The developer reviews the approach.
4. Claude implements the approved change.
5. Review the code diff.
6. Run automated tests and static checks.
7. Submit the relevant diff to DeepSeek or Qwen for
   independent review when the review cadence applies
   (Section 5).
8. Evaluate the reviewer's findings.
9. Apply approved corrections.
10. Re-run tests and security checks.
11. Benchmark performance-sensitive changes.
12. Document important engineering decisions and store
    the review record in `docs/reviews/`.
13. Commit the validated implementation.

For hand-written core files:

1. The developer writes the code and tests.
2. DeepSeek/Qwen independent review.
3. Claude review.
4. The developer fixes findings by hand.
5. Run automated tests and evals.
6. Record review decisions in `docs/reviews/` and what
   was learned in `HANDWRITTEN.md`.

Do not claim success because code merely runs.

A change is complete when its agreed completion
checks pass.

Do not automatically execute destructive operations,
deploy resources, or incur paid API charges.

## 15. Hand-Written Interview Core (Mandatory)

The developer writes both the implementation code and
the tests for these files, without AI-generated
solutions. Use exactly the paths below, which are the
paths required by the PDF. Each module exists in one
location only; there are no duplicate implementations
under alternative folder names (for example
`ingestion/` vs `ingest/` or `evaluation/` vs `eval/`).

| File | Checklist step |
|---|---|
| `ingest/chunker.py` | P1-08 |
| `retrieval/repository.py` + `sql/` | P1-09 |
| `eval/metrics.py` | P1-10 |
| `retrieval/bm25.py` | P1-11 |
| `retrieval/fusion.py` | P1-11 |
| `generation/context_packer.py` | P1-12 |
| `generation/citations.py` | P1-13 |
| `llm/provider.py` | P1-13 |
| `eval/judge_agreement.py` | P1-14 |
| `api/limits.py` | P1-15 |
| `tests/test_isolation.py` | P1-09 (SQL layer), P1-15 (API layer) |

Target: about 700-900 lines including tests.

Claude may:
- Explain concepts, without solution code
- Give hints when the developer is stuck, never the fix
- Suggest test cases and edge cases
- Review and run the developer's tests and help
  interpret failures
- Review the developer's completed work
- Scaffold code outside these files, such as callers
  and wiring

Claude must not:
- Generate the implementation, function bodies, tests
  or solution code for these files
- Create placeholder, stub or skeleton files for these
  modules; the developer creates each file
- Edit these files or paste code into them
- Apply review fixes to these files; the developer
  fixes them by hand

Also not allowed in these files: inline AI
autocomplete, pasted generated or tutorial code, and
typing along with code-along videos. Official
documentation, books, papers and concept videos are
allowed.

For each file:
- Validate against a trusted library where one exists.
- Record a five-line explanation in `HANDWRITTEN.md`:
  what it does, the key design decision, one
  alternative, one failure mode, complexity/cost.
- Rewrite the core function from a blank file about one
  week later.

Before interviews, complete the timed Project 1 drills
listed in `HANDWRITTEN.md`.

## 16. Engineering and Coding Standards

Write production-oriented Python code.

Prefer:
- Readable functions
- Descriptive variable names
- Type hints where appropriate
- Small, testable modules
- Clear interfaces
- Pydantic validation
- Parameterized SQL
- Explicit error handling
- Structured logging
- Dependency management with pinned versions
- Reproducible configuration

Avoid:
- Unnecessary abstractions
- Premature optimization
- Hardcoded credentials
- Excessive dependencies
- Duplicate business logic
- Silent exception handling
- Unbounded retries
- Unnecessary LLM calls

Use notebooks for experimentation.

Move reusable application logic into Python modules.

Keep CI/CD definitions in the GitHub repository.

## 17. Teaching and Collaboration

The developer has enterprise integration engineering
experience with:
- REST and SOAP APIs
- Authentication
- SQL
- Troubleshooting
- Production integrations
- Deployment pipelines

The developer is learning production AI engineering.

Explain new concepts as they are encountered.

For each significant code component:
1. Explain its purpose.
2. Explain where it belongs in the architecture.
3. Explain relevant Python syntax.
4. Explain LangChain or LangGraph methods used.
5. Identify the inputs.
6. Identify the outputs.
7. Explain possible failures.
8. Explain important engineering tradeoffs.
9. Explain how to test it.
10. Provide an interview-ready explanation.

For hand-written core files, teach without supplying
solution code (Section 15).

Do not assume familiarity with Python-specific syntax
because of experience with other programming languages.

Do not send the developer back to a long course
as a prerequisite to implementing a feature.

Work through manageable steps.

Do not generate an entire application in one response.

When asked to implement a single step, focus on that step.

## 18. Documentation and Decision Records

Maintain project documentation covering:
- README: WHY, HOW, measured outcome and known
  limitations
- Architecture diagram and data flow
- Document ingestion activity diagram
- Question-answering activity diagram
- Stable build checklist
- Architecture decision records (ADRs)
- Concepts and code cheat sheet
- Data card and provenance
- Evaluation methodology
- Benchmark results
- Security report (OWASP LLM coverage, mitigations)
- Tenant-isolation test report
- Load-test report
- Independent review records (`docs/reviews/`)
- Hand-written core ledger (`HANDWRITTEN.md`)
- Operational runbook
- Deployment instructions

For each material decision, record an ADR with:
- ADR ID, date and status (Proposed or Approved)
- Engineering problem
- Candidate approaches
- Chosen approach and rationale
- Security/privacy implications
- Reliability and failure modes
- Measured quality/latency/cost
- Evidence and run links
- Alternatives rejected
- Limitations
- Revisit trigger

Required Project 1 ADRs:
- Claude/Bedrock vs DeepSeek/Qwen
- RAG vs long context with prompt caching
- pgvector vs OpenSearch/Chroma
- Thin LangChain use and retrieval fusion
- LangGraph vs simpler Python control flow
- LangSmith vs Langfuse

Do not repeatedly display the decision log unless requested.

Keep implementation and documentation consistent.

## 19. Progress, Write-Up and Interview Kit

The developer intends to share verified progress
on LinkedIn and X.

At meaningful milestones, prepare concise notes covering:
- What was built
- Why it matters
- What engineering concept was learned
- What was tested
- Any verified results

Mandatory at project completion:
- One public technical write-up
- One one-page interview kit: 90-second pitch (WHY ->
  HOW -> MEASURE), an architecture diagram redrawable
  in 3 minutes, three ADRs with rejected alternatives,
  one failure story, one defect caught by second-model
  review and how it was verified, real numbers with
  sample sizes and confidence intervals, "at 100x scale
  I would change...", and "what is already outdated in
  this design"

Do not automatically publish content.

Do not invent accomplishments or performance metrics.

Avoid sharing credentials, sensitive data,
or unreviewed technical claims.

## 20. Completion Standards

Every significant feature should have:
- Working implementation
- Clear purpose
- Automated tests
- Relevant documentation
- Error-handling coverage
- Independent review where the cadence applies
- Benchmark evidence when performance matters
- Verified completion criteria

Project 1 is complete when it demonstrates:
- Deployed tenant-safe retrieval with zero
  cross-tenant/cross-role leakage tests
- Evidence-grounded, cited answers and controlled
  abstention, clarification and escalation
- Citation validation and PII redaction
- Baseline vs hybrid/reranked retrieval and RAG vs
  long-context comparisons with paired statistics
- A locked evaluation set, judge calibration and
  confidence intervals
- Working FastAPI service and Streamlit interface with
  streaming
- Security and quality regression gates that block a
  deliberately regressed version
- Load-test report
- Terraform-managed AWS deployment with monitoring
- Hand-written core with tests and `HANDWRITTEN.md`
- Independent review records for each milestone
- Public write-up and interview kit
- Reproducible evaluation, runnable by a reviewer, with
  one measured improvement and remaining failure
  categories recorded

## 21. Current Project Status

Project: RAG Knowledge Intelligence Platform
(HR Policy & Benefits Knowledge Assistant)

Current step: P1-02 — Local development infrastructure
(In progress)

Previous step: P1-01 — Initialize repository (Verified
2026-11-03)

Done: Claude Code extension, project folder, CLAUDE.md
aligned to the 2026 Final PDF, `HANDWRITTEN.md` ledger
template, `docs/reviews/`, Git on `main`, `.gitignore`,
`.env.example`, Python 3.12.4 virtual environment, the
approved root-level repository layout, `pyproject.toml`,
initial Docker configuration and README.

uv 0.13.7 is installed, `uv.lock` is generated and the
initial commit `dc0cbc8` exists on `main`.

P1-01 was verified by the developer on 2026-11-03.

Do not begin implementing the RAG pipeline until
the developer explicitly authorizes the next step.

Follow the numbered implementation checklist
and preserve stable step identifiers.
