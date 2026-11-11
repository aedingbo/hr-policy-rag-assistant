"""Tests for ingest.registry (P1-03).

The committed registry must pass. Each broken variant must fail with a
specific message, so a validator that accepts everything cannot pass.
"""

from __future__ import annotations

import copy
import json
from collections.abc import Callable
from datetime import date
from typing import Any

import pytest

from ingest import registry as reg

# Fixed date so results never depend on the day the tests run.
ON_DATE = date(2026, 11, 10)
TENANT_IDS = {"grayer", "applewhite", "thomas"}

Row = dict[str, Any]


@pytest.fixture
def raw_tenants() -> dict[str, Any]:
    return json.loads(reg.TENANTS_PATH.read_text(encoding="utf-8"))


@pytest.fixture
def registry() -> tuple[list[str], list[Row]]:
    return reg.read_csv(reg.REGISTRY_PATH)


def find(rows: list[Row], source_id: str) -> Row:
    """Locate a raw CSV row by its stable ID, e.g. 'grayer:remote_work:v2'."""
    tenant_id, policy_id, version = source_id.split(":")
    for row in rows:
        if (row["tenant_id"], row["policy_id"], f"v{row['version']}") == (
            tenant_id,
            policy_id,
            version,
        ):
            return row
    raise KeyError(source_id)


def registry_errors(header: list[str], rows: list[Row]) -> list[str]:
    _, errors = reg.validate_registry(rows, header, TENANT_IDS, ON_DATE)
    return errors


# --- The committed data ---------------------------------------------------


def test_committed_registry_files_are_valid() -> None:
    assert reg.load_and_validate(ON_DATE) == []


def test_committed_registry_has_three_tenants_and_planted_cases(
    registry: tuple[list[str], list[Row]],
) -> None:
    header, raw_rows = registry
    rows, errors = reg.validate_registry(raw_rows, header, TENANT_IDS, ON_DATE)
    assert errors == []
    assert {row.tenant_id for row in rows} == TENANT_IDS
    by_id = {row.source_id: row for row in rows}
    # Superseded version is no longer in force; its successor is.
    assert not reg.is_in_force(by_id["grayer:remote_work:v1"], ON_DATE)
    assert reg.is_in_force(by_id["grayer:remote_work:v2"], ON_DATE)
    assert by_id["applewhite:pandemic_leave:v1"].approval_status == "withdrawn"
    assert by_id["thomas:hr_relocation_guidelines:v1"].access_scope == "hr_only"


# --- Half-open effective dates ------------------------------------------------


def test_is_in_force_uses_half_open_window(registry: tuple[list[str], list[Row]]) -> None:
    header, raw_rows = registry
    rows, _ = reg.validate_registry(raw_rows, header, TENANT_IDS, ON_DATE)
    by_id = {row.source_id: row for row in rows}
    v1, v2 = by_id["grayer:remote_work:v1"], by_id["grayer:remote_work:v2"]
    boundary = date(2025, 7, 1)
    assert reg.is_in_force(v1, date(2025, 6, 30))
    assert not reg.is_in_force(v1, boundary)  # end date is exclusive
    assert reg.is_in_force(v2, boundary)  # start date is inclusive
    assert not reg.is_in_force(v2, date(2025, 6, 30))


# --- Broken registries must fail ----------------------------------------------
# Each helper returns a function that breaks a copy of the real registry in
# one specific way.


def _set(source_id: str, **changes: str) -> Callable[[list[Row]], None]:
    def mutate(rows: list[Row]) -> None:
        find(rows, source_id).update(changes)

    return mutate


def _append_copy(source_id: str, **changes: str) -> Callable[[list[Row]], None]:
    def mutate(rows: list[Row]) -> None:
        row = copy.deepcopy(find(rows, source_id))
        row.update(changes)
        rows.append(row)

    return mutate


def _remove(source_id: str) -> Callable[[list[Row]], None]:
    def mutate(rows: list[Row]) -> None:
        rows.remove(find(rows, source_id))

    return mutate


def _add_extra_cell(source_id: str) -> Callable[[list[Row]], None]:
    # csv.DictReader puts cells beyond the header under the key None.
    def mutate(rows: list[Row]) -> None:
        find(rows, source_id)[None] = ["extra cell"]  # type: ignore[index]

    return mutate


BROKEN_REGISTRIES = [
    pytest.param(
        _set("grayer:remote_work:v2", effective_from="2025-08-01"),
        "must equal",
        id="gap-between-versions",
    ),
    pytest.param(
        _set("grayer:remote_work:v1", effective_to="2025-09-01"),
        "must equal",
        id="overlapping-versions",
    ),
    pytest.param(
        _set("grayer:remote_work:v1", effective_to=""),
        "must equal",
        id="open-ended-version-that-is-not-last",
    ),
    pytest.param(
        _set(
            "grayer:remote_work:v2",
            version="3",
            source_uri="data/raw/grayer/remote_work/v3.md",
        ),
        "without gaps",
        id="version-number-gap",
    ),
    pytest.param(
        _append_copy("thomas:benefits:v1"),
        "duplicate",
        id="duplicate-version",
    ),
    pytest.param(
        _append_copy(
            "thomas:benefits:v1",
            tenant_id="acme",
            source_uri="data/raw/acme/benefits/v1.md",
        ),
        "unknown tenant_id",
        id="unknown-tenant",
    ),
    pytest.param(
        _set("thomas:benefits:v1", access_scope="public"),
        "access_scope",
        id="invalid-access-scope",
    ),
    pytest.param(
        _set("grayer:hr_relocation_guidelines:v1", access_scope="all_employees"),
        "access_scope must be hr_only",
        id="hr-only-document-opened-to-employees",
    ),
    pytest.param(
        _set("applewhite:manager_guide:v1", access_scope="all_employees"),
        "access_scope must be managers",
        id="manager-document-opened-to-employees",
    ),
    pytest.param(
        _append_copy(
            "applewhite:pandemic_leave:v1",
            version="2",
            effective_from="2023-06-01",
            effective_to="2024-01-01",
            source_uri="data/raw/applewhite/pandemic_leave/v2.md",
        ),
        "withdrawn version cannot be followed",
        id="withdrawn-version-followed-by-another",
    ),
    pytest.param(
        _set("applewhite:pandemic_leave:v1", effective_to=""),
        "withdrawn policy needs an effective_to",
        id="withdrawn-without-end-date",
    ),
    pytest.param(
        _set("thomas:expenses:v1", effective_to="2024-12-31"),
        "after effective_from",
        id="end-before-start",
    ),
    pytest.param(
        _set("thomas:expenses:v1", source_uri="data/raw/grayer/expenses/v1.md"),
        "source_uri must be",
        id="source-uri-points-at-another-tenant",
    ),
    pytest.param(
        _set("thomas:expenses:v1", effective_from="2025-13-01"),
        "effective_from",
        id="invalid-date",
    ),
    pytest.param(
        _set("thomas:expenses:v1", approval_status="draft"),
        "approval_status",
        id="unapproved-status-value",
    ),
    pytest.param(
        _remove("thomas:expenses:v1"),
        "missing current approved version of ['expenses']",
        id="tenant-missing-required-policy",
    ),
    pytest.param(
        _add_extra_cell("thomas:expenses:v1"),
        "too many fields",
        id="row-with-extra-cell",
    ),
]


@pytest.mark.parametrize(("mutate", "expected"), BROKEN_REGISTRIES)
def test_broken_registry_is_rejected(
    registry: tuple[list[str], list[Row]],
    mutate: Callable[[list[Row]], None],
    expected: str,
) -> None:
    header, raw_rows = registry
    rows = copy.deepcopy(raw_rows)
    mutate(rows)
    errors = registry_errors(header, rows)
    assert any(expected in error for error in errors), errors


def test_wrong_header_is_rejected(registry: tuple[list[str], list[Row]]) -> None:
    header, raw_rows = registry
    errors = registry_errors([*header, "notes"], raw_rows)
    assert len(errors) == 1
    assert "header must be" in errors[0]


# --- Tenant specification -------------------------------------------------------


def test_hq_state_must_be_an_operating_state(raw_tenants: dict[str, Any]) -> None:
    raw_tenants["tenants"][0]["hq_state"] = "CA"
    _, errors = reg.validate_tenant_spec(raw_tenants)
    assert any("hq_state CA is not in operating_states" in error for error in errors)


def test_duplicate_tenant_id_is_rejected(raw_tenants: dict[str, Any]) -> None:
    raw_tenants["tenants"][1]["tenant_id"] = "grayer"
    _, errors = reg.validate_tenant_spec(raw_tenants)
    assert "tenants.json: duplicate tenant_id grayer" in errors


def test_widened_access_scope_is_rejected(raw_tenants: dict[str, Any]) -> None:
    raw_tenants["access_scopes"]["hr_only"].append("manager")
    _, errors = reg.validate_tenant_spec(raw_tenants)
    assert any("role hierarchy" in error for error in errors)


def test_data_must_be_marked_synthetic(raw_tenants: dict[str, Any]) -> None:
    raw_tenants["synthetic"] = False
    spec, errors = reg.validate_tenant_spec(raw_tenants)
    assert spec is None
    assert any("synthetic" in error for error in errors)


# --- Source manifest ---------------------------------------------------------------


def test_source_uri_must_be_covered_by_manifest(
    registry: tuple[list[str], list[Row]],
) -> None:
    header, raw_rows = registry
    rows, _ = reg.validate_registry(raw_rows, header, TENANT_IDS, ON_DATE)
    manifest = [{"source_scope": "data/raw/grayer/**", "origin": "x", "license": "y"}]
    errors = reg.validate_manifest(manifest, rows)
    assert any(error.startswith("thomas:") for error in errors)
    assert not any(error.startswith("grayer:") for error in errors)


def test_manifest_requires_license(registry: tuple[list[str], list[Row]]) -> None:
    header, raw_rows = registry
    rows, _ = reg.validate_registry(raw_rows, header, TENANT_IDS, ON_DATE)
    manifest = [{"source_scope": "data/raw/**", "origin": "original_synthetic", "license": ""}]
    assert "source_manifest.csv row 2: license is empty" in reg.validate_manifest(manifest, rows)
