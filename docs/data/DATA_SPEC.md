# Data specification (P1-03)

All companies, policies and people in this dataset are fictional. Any
resemblance to real organizations is coincidental. No employer or client
material is used.

Files:
- `data/registry/tenants.json`: tenants, roles and access scopes
- `data/registry/policy_registry.csv`: one row per policy version
- `data/registry/source_manifest.csv`: source and license

## Tenants

| tenant_id | Name | Industry | Operating states |
|---|---|---|---|
| `grayer` | Grayer Logistics | Freight and warehousing | OH, IN, KY, PA |
| `applewhite` | Applewhite Health | Outpatient clinics | GA, SC, NC |
| `thomas` | Thomas Software | Software (remote-first) | CO, TX, WA, NY, IL, AZ |

## Roles and access scopes

Roles are hierarchical: `employee` < `manager` < `hr`. A document's
`access_scope` names the lowest role that may read it, always within the
reader's own tenant.

| access_scope | Readable by |
|---|---|
| `all_employees` | employee, manager, hr |
| `managers` | manager, hr |
| `hr_only` | hr |

## Registry conventions

- **Stable source ID:** `tenant_id:policy_id:v{version}` (e.g. `grayer:remote_work:v2`).
- **Dates** are ISO `YYYY-MM-DD` and half-open: a version applies when
  `effective_from <= date < effective_to`. An empty `effective_to` means the
  version is open-ended.
- **Supersession:** versions of one `policy_id` form a chain. Each version's
  `effective_to` equals the next version's `effective_from` (no gaps, no
  overlaps). "Superseded" is derived from dates, not stored.
- **approval_status:** `approved` or `withdrawn`. A withdrawn policy is
  revoked without replacement and must never be cited as current.
- **owner** is a team, never a person.
- **source_uri** is a repository path now; it becomes an S3 location after
  deployment.

## Deliberate differences per tenant

The same topic has different rules in each tenant, so an answer that uses
another tenant's rule is detectable.

| policy_id | Grayer Logistics | Applewhite Health | Thomas Software |
|---|---|---|---|
| `remote_work` | v2 (from 2025-07-01): an out-of-state move needs manager **and** HR approval, 60 days' notice, operating states only. v1 (superseded): manager approval only, 30 days' notice | Clinical roles are on-site only; non-clinical staff may work remotely within operating states with HR approval | Remote-first: any operating state; notify HR 30 days before moving; no approval needed |
| `pto_leave` | Accrual of 15 days/year; carry over up to 5 days | v2 (from 2026-01-01): 20 days/year; carry over up to 80 hours. v1 (superseded): 18 days/year, 40 hours | Flexible PTO with manager approval; at least 10 days/year encouraged |
| `benefits` | Medical eligibility after 30 days for staff working 30+ hours/week | Eligible on the first of the month after hire | Eligible from day one |
| `expenses` | Submit within 30 days; receipts required over $25 | Submit within 60 days; receipts over $50 | Submit within 90 days; receipts over $75; home-office stipend |
| `onboarding` | Safety training in week one | Credential verification before patient contact | Laptop shipped before day one; two-week buddy program |
| `manager_guide` (managers) | How to approve relocation and PTO requests | Scheduling and clinical coverage approvals | Approving moves and flexible PTO |
| `hr_relocation_guidelines` (hr_only) | Relocation assistance amounts and pay adjustment by state | Pay adjustment by state; clinical licensure transfer | Location-based pay bands |

## Deliberate test cases built into the data

| Case | Where | Expected behavior |
|---|---|---|
| Superseded policy | `grayer:remote_work:v1` | Cite v2 for current questions; v1 only for dates before 2025-07-01 |
| Contradictory PTO language | `applewhite:employee_handbook:v1` still says a 40-hour carryover; `applewhite:pto_leave:v2` says 80 hours | Cite the current PTO policy and surface the conflict |
| Withdrawn policy | `applewhite:pandemic_leave:v1` | Never cite as current |
| Role-restricted documents | `manager_guide` (managers), `hr_relocation_guidelines` (hr_only) | Never retrieved for a lower role |
| Missing context | Relocation questions without a role type or destination state | Ask for clarification or escalate |

## Synthetic authoring rules

1. Every document is original, fictional content and is labeled synthetic.
2. No employer or client material, including anonymized versions.
3. Each document states its tenant, policy ID, version and effective dates,
   and these must match the registry.
4. Rules in a document must match the difference table above; any change is
   made here first.
5. Conflicts exist only where they are listed above.
6. Any people named are fictional; no real personal data.
7. Documents are reviewed by the developer before they are used.
