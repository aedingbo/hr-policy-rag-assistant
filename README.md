# HR Policy & Benefits Knowledge Assistant

A production-oriented, permission-aware retrieval-augmented generation (RAG)
application for HR policy and benefits questions. Project 1 of a five-project
AI engineering portfolio.

## What it will do

- Answer employee and HR-staff questions from versioned policy documents for
  three fictional client companies.
- Cite the current policy, flag outdated or conflicting versions, and abstain,
  clarify or escalate when evidence or employee context is missing.
- Enforce tenant and role isolation in the database and retrieval layer, not in
  prompts.
- Measure retrieval and answer quality on a fixed, version-controlled benchmark.

All companies, employees and policies are fictional. No employer, client or
real employee data is used.

## Status

Early setup. Current step: **P1-01 — Initialize repository** (in progress).
No application functionality is implemented and no results have been measured
yet. Progress is tracked in
[docs/PROJECT_1_BUILD_CHECKLIST.md](docs/PROJECT_1_BUILD_CHECKLIST.md).

## Planned stack

Python 3.12, FastAPI, Streamlit, PostgreSQL with pgvector, Amazon Bedrock,
Docker, Terraform and GitHub Actions. Each component is added when its
milestone begins.

## Repository layout

| Path | Purpose |
|---|---|
| `api/` | FastAPI service |
| `ingest/` | Document loading, PII redaction and chunking |
| `retrieval/` | Vector, keyword and hybrid search over PostgreSQL/pgvector |
| `eval/` | Evaluation metrics and benchmark runners |
| `ui/` | Streamlit interface |
| `tests/` | Unit, integration and security tests |
| `data/` | Versioned synthetic policies, registry, manifests and benchmark |
| `infrastructure/terraform/` | AWS infrastructure as code |
| `docs/` | Checklist, review records and decision records |

## Local setup

Prerequisites: Python 3.12, [uv](https://docs.astral.sh/uv/) and Docker.

1. Copy the configuration template and fill in local values:

   ```powershell
   Copy-Item .env.example .env
   ```

   `.env` is excluded from Git and must never be committed.
2. Dependencies are declared in `pyproject.toml` and pinned in `uv.lock`, which
   is created when the first dependency is added.

## Engineering practices

- Important changes receive an independent second-model review, recorded in
  [docs/reviews/](docs/reviews/).
- Core modules are written by hand and tracked in [HANDWRITTEN.md](HANDWRITTEN.md).
- Reported metrics include sample sizes and confidence intervals; no result is
  claimed without a measured run.

## License

Not yet chosen.
