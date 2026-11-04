# Review: P1-02 local database security design and verification

- Date: 2026-11-03
- Checklist step(s): P1-02
- Trigger: security-sensitive configuration (CLAUDE.md Section 14 walkthrough
  before implementation)
- Review type: design review before implementation, followed by verification
  against the running local container (P1-02 Steps 6-11)
- Reviewers: Claude Code security walkthrough, followed by an independent
  ChatGPT review of a sanitized design summary
- Hosting: external service; sanitized summary only (no secrets, credentials,
  .env values, private specification content or personal data)
- Scope reviewed: `docker-compose.yml` and `.env.example` for the local
  PostgreSQL/pgvector database
- Note: this is an additional design review. It does not replace or count
  toward the DeepSeek/Qwen code reviews required by the portfolio specification.
- Times: container timestamps are UTC (2026-11-04); local date 2026-11-03.

## Findings

| ID | Severity | File/function | Failure mechanism | Proposed correction | Reproducible test | Classification | Verification evidence | Decision | Rationale |
|---|---|---|---|---|---|---|---|---|---|
| SDR-001 | High (if it had reached implementation) | `.env.example` `POSTGRES_USER`; future application database connection | The PostgreSQL image creates `POSTGRES_USER` as a superuser. Superusers bypass row-level security, as do roles with `BYPASSRLS` and, by default, table owners. The original name `hr_rag_app`, described as "the user the application connects as", could lead the application to connect with the privileged bootstrap account, silently disabling tenant/role isolation. | Rename to `hr_rag_admin` and document it as the local admin/bootstrap account only; separate admin, migration and application roles in P1-09 (see "Proposed database role design") | Planned (P1-09/P1-15): see "Future acceptance tests" | Potential risk, prevented at design time | Rename implemented in `.env.example` (Step 4). Risk premise confirmed in Step 9a: `hr_rag_admin` has `rolsuper = t`, `rolbypassrls = t`. Role design documented as Proposed (Step 12). Separation and RLS not yet implemented | Accepted | RLS is the core tenant-isolation control; it must not depend on which account the application happens to use |
| SDR-002 | Medium | Database authentication | The design assumed the image's default `scram-sha-256` password authentication. An assumption is not evidence: image defaults or configuration can differ. | Verify with authenticated SQL: `password_encryption`, effective host-based authentication rules, and the stored password format for the admin role | Executed in Step 9a | Potential risk | Verified 2026-11-03 (Step 9a), from a separate client container on the Compose network (client IP `172.18.0.3`): wrong password → `FATAL: password authentication failed`; correct password → login. `password_encryption = scram-sha-256`; stored verifier prefix `SCRAM-SHA-256$`. Effective `pg_hba_file_rules`: `trust` for `local`, `127.0.0.1`, `::1` and their replication equivalents (container-internal only); final rule `host all all all scram-sha-256` | Accepted | Authentication strength should be measured, not assumed |
| SDR-003 | Low | `docker-compose.yml` health check | `pg_isready` only reports that the server accepts connections. It does not prove credentials work, the target database exists, or pgvector is available. A "healthy" status could give false confidence. | Keep `pg_isready` for container readiness; add separate authenticated SQL acceptance tests for access, the pgvector extension and persistence | Executed in Steps 8-10 | Potential risk | Verified 2026-11-03: `(healthy)` status (Step 8) backed by separate checks — login to `hr_policy_rag` (Step 9a); `CREATE EXTENSION vector` → `0.8.7`, L2 `5.196152422706632`, cosine `1`, `hnsw.ef_search = 40`, `hnsw.iterative_scan = off` (Step 9b); data survived container recreation (Step 10) | Accepted | Readiness and correctness are different signals |
| SDR-004 | Medium | Named volume `pgdata` | A persistent volume survives container restarts but is not a backup. `docker compose down -v`, accidental volume removal, corruption or a bad migration can destroy data. | Document and test once a simple `pg_dump`/restore procedure. Impact is reduced because the corpus and benchmark are version-controlled and can be re-ingested. | Executed in Steps 10-11 | Potential risk | Verified 2026-11-03. Persistence (Step 10): marker row written (`created_at 2026-11-04 02:16:01.736321+00`); `docker compose down` (no `-v`) removed container `31b000462a6e…` and the network; volume `hr-policy-rag_pgdata` still listed; new container `067c25f492fe…` healthy and returned the identical row and `vector 0.8.7`. Backup (Step 11a): `pg_dump -Fc` copied to the host outside the repository; table of contents listed the extension, table and table data; 2,520 bytes; SHA-256 `9D6333FF7014C4683B238C54AAA28A8F5B45FF06C3A200D0F5751413880666CD`. Restore (Step 11b): host copy restored into scratch database `hr_policy_rag_restore_test` with `--exit-on-error` and no errors; identical row and extension; scratch database dropped. Test table removed from `hr_policy_rag` (Step 11c) | Accepted | Persistence and recoverability are separate properties |
| SDR-005 | Low | Compose output and logs | `docker compose config` prints resolved environment values, including the database password, and pasted terminal output can leak credentials. | Warning comment in `docker-compose.yml`; never share `docker compose config` output; the health check uses no password; verification commands avoid printing secrets | Executed during Steps 6-11 | Potential risk | Verified 2026-11-03: validation used `docker compose config --quiet` and name-only listings; password checked by length and placeholder only; psql logins used the hidden prompt; stored password shown only as its 14-character format prefix. No output shared during Steps 6-11 contained the password | Accepted | Credentials must not appear in logs, screenshots or shared output |

## Proposed database role design (SDR-001)

Status: **Proposed**, not implemented. Implementation and verification in
P1-09 (SQL layer) and P1-15 (API layer). Role names are provisional. The SQL
that creates these roles belongs to the engineer's hand-written P1-09 work
(`sql/`, `tests/test_isolation.py`); this section records properties and
responsibilities only.

| Role | Purpose | Required properties | Used by |
|---|---|---|---|
| `hr_rag_admin` | Bootstrap superuser created by the image | Superuser | Local setup and administration only: creating roles and databases, enabling extensions, backups. Never the application |
| Migration role (e.g. `hr_rag_migrator`) | Owns the schema; runs Alembic migrations | `LOGIN`, `NOSUPERUSER`, `NOBYPASSRLS`, `NOCREATEROLE`; owns tenant tables | Migrations only; never at request time |
| Application role (e.g. `hr_rag_app`) | Runtime connection for FastAPI | `LOGIN`, `NOSUPERUSER`, `NOBYPASSRLS`, `NOCREATEDB`, `NOCREATEROLE`; owns no tables; only explicitly granted privileges on specific tables | The API service at runtime |

Design rules:

- RLS is enabled **and forced** (`FORCE ROW LEVEL SECURITY`) on every
  tenant-scoped table, so the table-owning migration role is also subject to
  policies. A superuser still bypasses RLS, which is why `hr_rag_admin` is
  never used by the application.
- Each role has its own credential: local `.env` (new variables added to
  `.env.example` in P1-09) and AWS Secrets Manager in deployment.
- The application role receives the minimum privileges retrieval needs;
  schema changes, extension creation and role management are not granted.

Tenant-context requirements:

- Tenant and role identities come only from verified authentication and
  authorization performed by the API. They are never taken from request
  bodies, query parameters, headers the client controls, prompts or
  retrieved document content.
- Database context is transaction-scoped: set inside the transaction that
  uses it and discarded when that transaction ends, never left at session
  level.
- Pooled connections must not carry context from one request to the next.
  A connection returned to the pool holds no tenant or role context, and a
  request that starts without context sees no tenant data (fail closed).
- Custom PostgreSQL settings (for example a session variable read by RLS
  policies) are not, on their own, a complete security boundary: any
  connection able to run arbitrary SQL can change its own settings. The
  boundary depends on the combination of verified authentication, an
  application role that only runs parameterized application queries and
  never user-supplied SQL, transaction-scoped context, and RLS policies that
  fail closed when context is missing.

Open questions for P1-09:

- Exact privilege set for the application role (read-only for retrieval, or
  also writes for query and evaluation logs).
- Whether ingestion runs as the application role, the migration role or a
  separate ingestion role.
- How transaction-scoped context is set and how pool reset is verified.
- Migration data operations under forced RLS. `FORCE ROW LEVEL SECURITY` also
  applies to the table-owning migration role during data operations
  (`SELECT`, `INSERT`, `UPDATE`, `DELETE`), although not to schema changes. A
  data migration or backfill run without tenant context would see or change
  no rows, or only one tenant's rows. Authorized data migrations, such as
  backfills, re-indexing, tenant deletion and supersession updates, therefore
  need an explicitly designed, reviewed and tested execution path rather than
  an ad-hoc bypass. The options and the decision are recorded in P1-09.

## Future acceptance tests (SDR-001)

To be implemented by the engineer in the hand-written `tests/test_isolation.py`
(P1-09 SQL layer, P1-15 API layer). Listed here as test scenarios only:

- The application role reports `rolsuper = false` and `rolbypassrls = false`.
- The application role does not own any tenant-scoped table.
- Connected as the application role with tenant A's context, queries return
  zero rows and zero chunks belonging to tenant B or C.
- A role without manager or HR scope cannot retrieve manager-only or HR-only
  documents.
- A request with no tenant context returns no tenant data.
- Tenant context does not survive the end of a transaction or carry over to
  the next request on a reused pooled connection.
- Attempts to set or override tenant or role context through untrusted input
  are rejected and return no other tenant's or higher role's data.
- Retrieval logs and answers contain zero cross-tenant or cross-role chunks
  (CI gate; leakage count must be 0).

## Fixes applied

- SDR-001: `.env.example` renames the bootstrap superuser to `hr_rag_admin`
  and documents it as an admin-only account (Step 4); the role design and
  tenant-context requirements are documented (Step 12). Implementation is
  pending (P1-09/P1-15).
- SDR-002 to SDR-005: verification commands executed during Steps 6-11; no
  configuration change was needed.

## Test and eval evidence

Manual acceptance checks against the running local container, 2026-11-03
(image `pgvector/pgvector:0.8.7-pg17`, digest
`sha256:7d0a41464797aeb9862dfdc0bbf1526b82cfd324cdd8036df19e3545f4a9ccb8`,
PostgreSQL 17.11). Results are in the findings table. These are manual
verifications, not automated tests; automated database tests begin in P1-09.

## Residual risks

- SDR-001 remains open until the restricted application role and its isolation
  tests exist and pass (P1-09/P1-15).
- SDR-002: container-internal `trust` rules remain; acceptable only for local
  development, because anyone able to run `docker exec` already controls the
  container. Deployed authentication (RDS, TLS) is assessed in P1-18.
- SDR-004: the backup is on the same machine as the volume, is manual and
  unscheduled, and does not include roles. RDS automated backups are assessed
  in P1-18.
- SDR-005: relies on continued care when sharing output.
- Zero observed failures in a finite test suite will not establish zero risk.

## Engineering lessons

- In PostgreSQL, row-level security protects data only from roles that do not
  bypass it. Which account the application connects as is part of the security
  design, not a deployment detail.
- Names shape behavior: a privileged account named and described as the "app"
  user invites misuse. Clear naming is a cheap, early control.
- "Healthy", "persistent" and "uses secure defaults" are claims that need their
  own evidence.

## Communication notes (articles, LinkedIn, interviews)

Accurate framing: "During design review, before writing any database code, we
identified that PostgreSQL superusers bypass row-level security and that our
bootstrap account's naming could have led the application to use it. We changed
the design to separate admin, migration and application roles, and defined
isolation tests the application role must pass." Do not describe this as a
vulnerability found in running software or as a verified mitigation until the
P1-09/P1-15 tests pass. Suitable as the interview kit's "design decision" or
"what I caught before it became a bug" example; it is not a defect caught by the
DeepSeek/Qwen code review.

## Summary

- Accepted: 5
- Rejected: 0
- Not confirmed: 0
- Verified: 4 (SDR-002 to SDR-005, by manual checks during P1-02)
- Open: 1 (SDR-001; verification in P1-09/P1-15)
- Most important finding: SDR-001 (prevented at design time; verification
  pending)
