# Data Card — HR Policy Starter Corpus (draft, P1-04)

**Status:** draft for P1-04; expanded with checksums and the versioned dataset in P1-05.
**Date:** 2026-11-20

## Summary

27 synthetic HR policy documents for three **fictional** companies, built to test a
permission-aware RAG assistant: retrieval, citations, version handling, and tenant and
role isolation. **All companies, policies and people are fictional. No employer or client
material is used, including anonymized versions.** Nothing here is HR, legal or benefits
advice.

## Composition

| Tenant | Industry | Documents | Notes |
|---|---|---|---|
| Grayer Logistics (`grayer`) | Freight and warehousing (OH, IN, KY, PA) | 9 | Remote-work v1 superseded by v2 |
| Applewhite Health (`applewhite`) | Outpatient clinics (GA, SC, NC) | 10 | PTO v1 superseded by v2; withdrawn pandemic-leave policy |
| Thomas Software (`thomas`) | Remote-first software (CO, TX, WA, NY, IL, AZ) | 8 | — |

| Property | Count |
|---|---|
| Documents (registry rows) | 27 |
| Formats | 3 PDF (employee handbooks), 24 Markdown |
| Access scope | 21 all employees · 3 managers only · 3 HR only |
| Status | 26 approved · 1 withdrawn |
| Superseded versions | 2 |

Topics per tenant: employee handbook, benefits, PTO and leave, remote work and relocation,
onboarding, expenses, a manager-only guide and HR-only relocation guidelines.

Files: documents in `data/raw/{tenant}/{policy_id}/v{n}.{md|pdf}`; Markdown sources of the PDFs
in `data/source/`; metadata in `data/registry/` (`tenants.json`, `policy_registry.csv`,
`source_manifest.csv`).

## Provenance and generation

- **Origin:** original synthetic content. No public templates, scraped text or real policies
  were used as sources.
- **Authoring:** drafted with Claude Code (Anthropic) during development, following the
  authoring rules in `docs/data/DATA_SPEC.md`; every document reviewed and approved by the
  developer (Grayer: 2026-11-20; Applewhite and Thomas: 2026-11-20). No paid generation service
  was used.
- **PDFs:** rendered from the Markdown sources by `ingest/render_pdf.py` (markdown-pdf /
  PyMuPDF). Rendering is reproducible; re-rendering changes the embedded timestamp.
- **Metadata:** the registry is the source of truth for tenant, version, effective dates,
  approval status and access scope.

## Deliberate test content

Designed so specific failures are measurable (details in `docs/data/DATA_SPEC.md`):

- **Per-tenant differences:** the same topic has different rules per company, so an answer
  using another company's rule reveals cross-tenant leakage.
- **Superseded versions:** Grayer remote work v1 → v2; Applewhite PTO v1 → v2.
- **Planted contradiction:** Applewhite's handbook states a 40-hour PTO carryover; the newer PTO
  policy (v2) states 80 hours.
- **Withdrawn policy:** Applewhite pandemic leave — withdrawn only in the registry; the text
  itself reads as valid.
- **Restricted documents:** manager-only and HR-only documents (e.g. relocation pay factors)
  that must never reach lower roles.

## Validation

- `uv run python -m ingest.registry` — IDs, dates, version chains, scopes and manifest
  coverage.
- `uv run pytest tests/test_corpus_documents.py -v` — every registry document exists, parses,
  is labeled synthetic, and its header (tenant, policy ID, version, effective date, access,
  owner) matches the registry; no unregistered files.
- Manual review of every document by the developer.

**Validation finding (2026-11-20):** PDF text extraction returns typographic ligatures as single
characters (for example "Eﬀective" with U+FB00). Extracted PDF text must be Unicode-normalized
(NFKC) before matching or keyword search; required for the P1-07 PDF loader.

## Intended use

Development and evaluation of this project's RAG assistant: retrieval quality, citation
accuracy, version and conflict handling, abstention, and tenant/role isolation tests.

## Out of scope

- Real HR, legal, tax or benefits guidance.
- Statistical claims about real-world HR policies.
- Training data for general-purpose models.

## Known limitations

- Small (27 documents, about 1–2 pages each); performance-scale testing needs a separate,
  generated scale corpus (Amendment A, P1-17a).
- Simplified, US-only fictional policies; no state-specific legal accuracy is implied.
- English only.
- Contradictions exist only where planted; real corpora are messier.
- Authored by one developer with AI assistance; wording style is more uniform than real policy
  libraries.

## License

No repository license has been chosen yet; until one is added, default copyright applies. The
content is fictional and contains no personal data.

## Changes

| Date | Change |
|---|---|
| 2026-11-20 | Draft created with the P1-04 starter corpus |
