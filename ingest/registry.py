"""Load and validate the tenant specification and policy registry (P1-03).

The registry is the source of truth for tenant ownership, versions,
effective dates and access scopes. Later steps (ingestion, row-level
security, citations, ground truth) rely on it, so it is checked here
before anything else uses it.

Validation collects every problem instead of stopping at the first one,
so a single run shows everything that needs fixing.

Run from the repository root:
    uv run python -m ingest.registry
"""

from __future__ import annotations

import csv
import json
import sys
from collections import defaultdict
from datetime import date
from fnmatch import fnmatch
from itertools import pairwise
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
    field_validator,
    model_validator,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_DIR = REPO_ROOT / "data" / "registry"
TENANTS_PATH = REGISTRY_DIR / "tenants.json"
REGISTRY_PATH = REGISTRY_DIR / "policy_registry.csv"
MANIFEST_PATH = REGISTRY_DIR / "source_manifest.csv"

# The nine columns required by the portfolio spec, in order. Nothing extra.
REGISTRY_COLUMNS = [
    "tenant_id",
    "policy_id",
    "version",
    "effective_from",
    "effective_to",
    "approval_status",
    "access_scope",
    "owner",
    "source_uri",
]

# Roles are hierarchical; each access scope names the roles that may read it.
# tenants.json must declare exactly this mapping, so the data cannot quietly
# widen access without a code change and review.
ROLES = ["employee", "manager", "hr"]
SCOPE_ROLES = {
    "all_employees": {"employee", "manager", "hr"},
    "managers": {"manager", "hr"},
    "hr_only": {"hr"},
}

# Every tenant must have a current, approved version of each of these.
REQUIRED_POLICY_IDS = frozenset(
    {
        "employee_handbook",
        "benefits",
        "pto_leave",
        "remote_work",
        "onboarding",
        "expenses",
        "manager_guide",
        "hr_relocation_guidelines",
    }
)

# Restricted documents must keep their scope; a wrong scope here is a data leak.
RESTRICTED_POLICY_SCOPES = {
    "manager_guide": "managers",
    "hr_relocation_guidelines": "hr_only",
}

Identifier = Annotated[str, StringConstraints(pattern=r"^[a-z][a-z0-9_]*$")]
StateCode = Annotated[str, StringConstraints(pattern=r"^[A-Z]{2}$")]
ApprovalStatus = Literal["approved", "withdrawn"]
AccessScope = Literal["all_employees", "managers", "hr_only"]


class Tenant(BaseModel):
    """One fictional client company from tenants.json."""

    model_config = ConfigDict(extra="forbid")

    tenant_id: Identifier
    name: str = Field(min_length=1)
    industry: str = Field(min_length=1)
    hq_state: StateCode
    operating_states: list[StateCode] = Field(min_length=1)

    @model_validator(mode="after")
    def _hq_is_an_operating_state(self) -> Tenant:
        if self.hq_state not in self.operating_states:
            raise ValueError(f"hq_state {self.hq_state} is not in operating_states")
        return self


class TenantSpec(BaseModel):
    """The whole tenants.json file."""

    model_config = ConfigDict(extra="forbid")

    synthetic: Literal[True]  # the dataset must declare itself fictional
    notice: str = Field(min_length=1)
    roles: list[str]
    access_scopes: dict[str, list[str]]
    tenants: list[Tenant] = Field(min_length=1)


class PolicyVersion(BaseModel):
    """One registry row: one version of one policy for one tenant."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    tenant_id: Identifier
    policy_id: Identifier
    version: int = Field(ge=1)
    effective_from: date
    effective_to: date | None  # None = open-ended (still in force)
    approval_status: ApprovalStatus
    access_scope: AccessScope
    owner: str = Field(min_length=1)
    source_uri: str

    @field_validator("effective_to", mode="before")
    @classmethod
    def _blank_means_open_ended(cls, value: Any) -> Any:
        # CSV has no null; an empty cell means "no end date".
        return None if value == "" else value

    @model_validator(mode="after")
    def _check_row(self) -> PolicyVersion:
        if self.effective_to is not None and self.effective_to <= self.effective_from:
            raise ValueError("effective_to must be after effective_from")
        if self.approval_status == "withdrawn" and self.effective_to is None:
            raise ValueError("a withdrawn policy needs an effective_to date")
        # The path must match the row's own tenant/policy/version, so a row
        # cannot point at another tenant's file.
        prefix = f"data/raw/{self.tenant_id}/{self.policy_id}/v{self.version}."
        if not (
            self.source_uri.startswith(prefix)
            and self.source_uri.removeprefix(prefix) in {"md", "pdf"}
        ):
            raise ValueError(f"source_uri must be {prefix}md or {prefix}pdf")
        return self

    @property
    def source_id(self) -> str:
        """Stable identifier used by citations and ground truth."""
        return f"{self.tenant_id}:{self.policy_id}:v{self.version}"


def is_in_force(row: PolicyVersion, on_date: date) -> bool:
    """Half-open window: effective_from <= on_date < effective_to."""
    return row.effective_from <= on_date and (
        row.effective_to is None or on_date < row.effective_to
    )


def read_csv(path: Path) -> tuple[list[str], list[dict[str, Any]]]:
    """Return the header and rows. utf-8-sig tolerates a BOM added by Excel."""
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return list(reader.fieldnames or []), rows


def _format_errors(exc: ValidationError, label: str) -> list[str]:
    """Turn Pydantic's structured errors into one readable line each."""
    messages = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error["loc"])
        prefix = f"{label}: {location}" if location else label
        messages.append(f"{prefix}: {error['msg']}")
    return messages


def validate_tenant_spec(raw: dict[str, Any]) -> tuple[TenantSpec | None, list[str]]:
    """Validate tenants.json; return the parsed spec (None if unusable) and errors."""
    try:
        spec = TenantSpec.model_validate(raw)
    except ValidationError as exc:
        return None, _format_errors(exc, "tenants.json")

    errors = []
    if spec.roles != ROLES:
        errors.append(f"tenants.json: roles must be {ROLES}; got {spec.roles}")
    declared_scopes = {scope: set(roles) for scope, roles in spec.access_scopes.items()}
    if declared_scopes != SCOPE_ROLES:
        errors.append("tenants.json: access_scopes do not match the approved role hierarchy")
    tenant_ids = [tenant.tenant_id for tenant in spec.tenants]
    for tenant_id in sorted({t for t in tenant_ids if tenant_ids.count(t) > 1}):
        errors.append(f"tenants.json: duplicate tenant_id {tenant_id}")
    return spec, errors


def _check_chain(versions: list[PolicyVersion]) -> list[str]:
    """Versions of one policy must be numbered 1..n and meet end to start.

    Because each end date must equal the next start date, this one check
    catches gaps, overlaps and an open-ended version that is not the last.
    """
    errors = []
    label = f"{versions[0].tenant_id}:{versions[0].policy_id}"
    numbers = [row.version for row in versions]
    if numbers != list(range(1, len(versions) + 1)):
        errors.append(f"{label}: versions must be 1..n without gaps; got {numbers}")
    for previous, following in pairwise(versions):  # (v1, v2), (v2, v3), ...
        if previous.effective_to != following.effective_from:
            errors.append(
                f"{following.source_id}: effective_from {following.effective_from} must "
                f"equal {previous.source_id} effective_to {previous.effective_to}"
            )
        if previous.approval_status == "withdrawn":
            errors.append(
                f"{previous.source_id}: a withdrawn version cannot be followed by a later version"
            )
    return errors


def validate_registry(
    raw_rows: list[dict[str, Any]],
    header: list[str],
    tenant_ids: set[str],
    on_date: date,
) -> tuple[list[PolicyVersion], list[str]]:
    """Validate registry rows; return the parsed rows and a list of errors.

    on_date is passed in (not read from the clock) so tests are deterministic.
    """
    if header != REGISTRY_COLUMNS:
        return [], [f"policy_registry.csv: header must be {REGISTRY_COLUMNS}; got {header}"]

    rows: list[PolicyVersion] = []
    errors: list[str] = []
    for line_number, raw in enumerate(raw_rows, start=2):  # line 1 is the header
        if None in raw:  # csv.DictReader stores surplus cells under the key None
            errors.append(f"row {line_number}: too many fields")
            continue
        try:
            rows.append(PolicyVersion.model_validate(raw))
        except ValidationError as exc:
            errors.extend(_format_errors(exc, f"row {line_number}"))
    if errors:
        # Chain checks on partially parsed data would add misleading errors.
        return rows, errors

    seen: set[str] = set()
    chains: dict[tuple[str, str], list[PolicyVersion]] = defaultdict(list)
    for row in rows:
        if row.tenant_id not in tenant_ids:
            errors.append(f"{row.source_id}: unknown tenant_id {row.tenant_id}")
        expected_scope = RESTRICTED_POLICY_SCOPES.get(row.policy_id)
        if expected_scope is not None and row.access_scope != expected_scope:
            errors.append(f"{row.source_id}: access_scope must be {expected_scope}")
        if row.source_id in seen:
            errors.append(f"{row.source_id}: duplicate tenant_id/policy_id/version")
            continue
        seen.add(row.source_id)
        chains[(row.tenant_id, row.policy_id)].append(row)

    for key in sorted(chains):
        errors.extend(_check_chain(sorted(chains[key], key=lambda row: row.version)))

    for tenant_id in sorted(tenant_ids):
        current = {
            row.policy_id
            for row in rows
            if row.tenant_id == tenant_id
            and row.approval_status == "approved"
            and is_in_force(row, on_date)
        }
        missing = sorted(REQUIRED_POLICY_IDS - current)
        if missing:
            errors.append(
                f"{tenant_id}: missing current approved version of {missing} on {on_date}"
            )
    return rows, errors


def validate_manifest(
    raw_rows: list[dict[str, Any]], registry_rows: list[PolicyVersion]
) -> list[str]:
    """Every registry source_uri must be covered by a manifest row with origin and license."""
    errors = []
    for line_number, raw in enumerate(raw_rows, start=2):
        for column in ("source_scope", "origin", "license"):
            if not (raw.get(column) or "").strip():
                errors.append(f"source_manifest.csv row {line_number}: {column} is empty")
    scopes = [raw.get("source_scope") or "" for raw in raw_rows]
    for row in registry_rows:
        # fnmatch's "*" also matches "/", so "data/raw/**" covers every subfolder.
        if not any(fnmatch(row.source_uri, scope) for scope in scopes if scope):
            errors.append(f"{row.source_id}: source_uri is not covered by source_manifest.csv")
    return errors


def load_and_validate(
    on_date: date,
    tenants_path: Path = TENANTS_PATH,
    registry_path: Path = REGISTRY_PATH,
    manifest_path: Path = MANIFEST_PATH,
) -> list[str]:
    """Validate all registry files; return a list of problems (empty = valid)."""
    raw_tenants = json.loads(tenants_path.read_text(encoding="utf-8"))
    spec, errors = validate_tenant_spec(raw_tenants)
    if spec is None:
        return errors

    header, raw_rows = read_csv(registry_path)
    tenant_ids = {tenant.tenant_id for tenant in spec.tenants}
    rows, registry_errors = validate_registry(raw_rows, header, tenant_ids, on_date)
    errors.extend(registry_errors)

    _, manifest_rows = read_csv(manifest_path)
    errors.extend(validate_manifest(manifest_rows, rows))
    return errors


def main() -> int:
    """Command-line entry point; exit code 1 on any problem (usable in CI later)."""
    on_date = date.today()
    errors = load_and_validate(on_date)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(f"FAILED: {len(errors)} problem(s) as of {on_date}", file=sys.stderr)
        return 1
    print(f"OK: tenants, policy registry and source manifest are valid as of {on_date}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
