"""Tests for ingest.render_pdf (P1-04).

The key property: text in the rendered PDF can be extracted again, because
ingestion (P1-07) will read these PDFs. Renders go to pytest's tmp_path, so the
real raw corpus is never touched.
"""

from __future__ import annotations

from pathlib import Path

import pymupdf
import pytest

from ingest import render_pdf as rp

GRAYER_HANDBOOK = rp.source_path("grayer", "employee_handbook", 1)


def extract_text(pdf_path: Path) -> str:
    with pymupdf.open(pdf_path) as doc:
        # get_text() is typed as str | list | dict (it depends on the mode); the
        # default "text" mode returns str, so make that explicit for the type checker.
        return "\n".join(str(page.get_text("text")) for page in doc)


def test_grayer_handbook_renders_with_extractable_text(tmp_path: Path) -> None:
    target = rp.render(GRAYER_HANDBOOK, tmp_path / "v1.pdf")
    text = extract_text(target)
    # Title, header-table values and body text all survive the round trip.
    for expected in (
        "Grayer Logistics",
        "Employee Handbook",
        "employee_handbook",
        "2025-01-01",
        "People Operations",
        "Synthetic document",
        "Remote Work and Relocation Policy",
    ):
        assert expected in text, expected


def test_pdf_title_metadata_comes_from_heading(tmp_path: Path) -> None:
    target = rp.render(GRAYER_HANDBOOK, tmp_path / "v1.pdf")
    with pymupdf.open(target) as doc:
        assert doc.metadata is not None
        assert doc.metadata["title"] == "Grayer Logistics — Employee Handbook"


def test_existing_pdf_is_not_overwritten(tmp_path: Path) -> None:
    target = tmp_path / "v1.pdf"
    target.write_bytes(b"original")
    with pytest.raises(FileExistsError):
        rp.render(GRAYER_HANDBOOK, target)
    assert target.read_bytes() == b"original"


def test_overwrite_flag_replaces_existing_pdf(tmp_path: Path) -> None:
    target = tmp_path / "v1.pdf"
    target.write_bytes(b"original")
    rp.render(GRAYER_HANDBOOK, target, overwrite=True)
    assert target.read_bytes().startswith(b"%PDF")


def test_registry_lookup_returns_pdf_path() -> None:
    path = rp.registry_pdf_path("grayer", "employee_handbook", 1)
    assert path.as_posix().endswith("data/raw/grayer/employee_handbook/v1.pdf")


def test_registry_lookup_rejects_markdown_documents() -> None:
    with pytest.raises(ValueError, match="not a PDF"):
        rp.registry_pdf_path("grayer", "remote_work", 2)


def test_registry_lookup_rejects_unknown_document() -> None:
    with pytest.raises(KeyError):
        rp.registry_pdf_path("grayer", "employee_handbook", 9)


def test_source_without_heading_is_rejected(tmp_path: Path) -> None:
    source = tmp_path / "v1.md"
    source.write_text("no heading here\n", encoding="utf-8")
    with pytest.raises(ValueError, match="level-1 heading"):
        rp.render(source, tmp_path / "v1.pdf")
