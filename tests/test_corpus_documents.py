"""Corpus validation report for P1-04: every document agrees with the registry.

Run `uv run pytest tests/test_corpus_documents.py -v` for a per-document report.

For each registry row this checks that the file exists and parses (Markdown read
as text; PDF text extracted with PyMuPDF), that it is labeled synthetic, and that
its header table (tenant, policy ID, version, effective date, access, owner)
matches the registry. Ingestion takes metadata from the registry, so a mismatch
would mean wrong citations (version/date) or a wrong access level (leak risk).
It also checks there are no files in data/raw that the registry does not know.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Any

import pymupdf
import pytest

from ingest import registry as reg

RAW_DIR = reg.REPO_ROOT / "data" / "raw"
SOURCE_DIR = reg.REPO_ROOT / "data" / "source"

ACCESS_LABELS = {
    "all employees": "all_employees",
    "managers only": "managers",
    "hr only": "hr_only",
}

_, REGISTRY_ROWS = reg.read_csv(reg.REGISTRY_PATH)


def row_id(row: dict[str, Any]) -> str:
    return f"{row['tenant_id']}:{row['policy_id']}:v{row['version']}"


def document_text(path: Path) -> str:
    """Text as ingestion will see it: Markdown as-is, PDF via text extraction.

    PDF extraction returns typographic ligatures as single characters
    ("Eﬀective" with U+FB00, "ﬁctional" with U+FB01), which breaks exact and
    keyword matching. NFKC normalization turns them back into plain letters.
    Found by this check on 2026-11-20; P1-07's PDF loader must do the same.
    """
    if path.suffix == ".pdf":
        with pymupdf.open(path) as doc:
            raw = "\n".join(str(page.get_text("text")) for page in doc)
        return unicodedata.normalize("NFKC", raw)
    return path.read_text(encoding="utf-8")


def _clean(value: str) -> str:
    return value.replace("`", "").replace("*", "").strip()


def header_fields(text: str, is_pdf: bool) -> dict[str, str]:
    """Return the header table as {label: value}.

    Markdown: rows like `| Version | 2 |`. PDF: extraction puts each table cell
    on its own line, so a value is the line after its label.
    """
    labels = ("Tenant", "Policy ID", "Version", "Effective date", "Access", "Owner")
    fields: dict[str, str] = {}
    if not is_pdf:
        for match in re.finditer(r"^\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$", text, re.MULTILINE):
            label, value = match.group(1), match.group(2)
            if label in labels and label not in fields:
                fields[label] = _clean(value)
        return fields
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for index, line in enumerate(lines[:-1]):
        if line in labels and line not in fields:
            fields[line] = _clean(lines[index + 1])
    return fields


@pytest.mark.parametrize("row", REGISTRY_ROWS, ids=row_id)
def test_document_matches_registry(row: dict[str, Any]) -> None:
    path = reg.REPO_ROOT / row["source_uri"]
    assert path.is_file(), f"missing file {row['source_uri']}"

    text = document_text(path)
    assert text.strip(), "no extractable text"
    assert "Synthetic document" in text, "not labeled synthetic"

    fields = header_fields(text, is_pdf=path.suffix == ".pdf")
    tenant = re.search(r"\(([a-z_]+)\)", fields.get("Tenant", ""))
    assert tenant is not None and tenant.group(1) == row["tenant_id"], fields.get("Tenant")
    assert fields.get("Policy ID") == row["policy_id"]
    assert fields.get("Version") == row["version"]
    assert fields.get("Effective date") == row["effective_from"]
    assert ACCESS_LABELS.get(fields.get("Access", "").lower()) == row["access_scope"], fields.get("Access")
    assert fields.get("Owner") == row["owner"]


def test_no_unregistered_files_in_raw() -> None:
    registered = {(reg.REPO_ROOT / row["source_uri"]).resolve() for row in REGISTRY_ROWS}
    on_disk = {path.resolve() for path in RAW_DIR.rglob("*") if path.is_file()}
    unknown = sorted(str(path.relative_to(reg.REPO_ROOT)) for path in on_disk - registered)
    assert unknown == []


def test_every_pdf_has_a_markdown_source() -> None:
    for row in REGISTRY_ROWS:
        if row["source_uri"].endswith(".pdf"):
            source = SOURCE_DIR / row["tenant_id"] / row["policy_id"] / f"v{row['version']}.md"
            assert source.is_file(), f"no source for {row_id(row)}"


# --- The checker itself must catch mismatches ---------------------------------


def test_header_parser_detects_wrong_version() -> None:
    text = "| Policy ID | `remote_work` |\n| Version | 3 |\n"
    assert header_fields(text, is_pdf=False)["Version"] != "2"


def test_header_parser_reads_pdf_style_lines() -> None:
    text = "Field\nValue\nTenant\nGrayer Logistics (grayer)\nAccess\nHR only\n"
    fields = header_fields(text, is_pdf=True)
    assert fields["Tenant"] == "Grayer Logistics (grayer)"
    assert ACCESS_LABELS[fields["Access"].lower()] == "hr_only"


def test_pdf_ligatures_are_normalized() -> None:
    # Guards the 2026-11-20 finding: without NFKC, "Effective" is not found.
    text = document_text(reg.REPO_ROOT / "data/raw/grayer/employee_handbook/v1.pdf")
    assert "Effective date" in text
    assert "ﬀ" not in text and "ﬁ" not in text


def test_header_parser_strips_markdown_emphasis() -> None:
    fields = header_fields("| Access | **Managers only** |\n", is_pdf=False)
    assert ACCESS_LABELS[fields["Access"].lower()] == "managers"
