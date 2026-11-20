"""Render a policy document's Markdown source to its registry PDF path (P1-04).

Some corpus documents (the employee handbooks) are registered as PDFs. They are
authored in Markdown under `data/source/{tenant}/{policy_id}/v{n}.md` and
rendered here to the registry `source_uri`, e.g.
`data/raw/grayer/employee_handbook/v1.pdf`.

Raw corpus files are preserved untouched, so an existing PDF is never
overwritten unless `--overwrite` is passed explicitly. Note that each render
embeds a new creation timestamp, so the file's checksum changes on re-render.

Run from the repository root:
    uv run python -m ingest.render_pdf grayer employee_handbook 1
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from markdown_pdf import MarkdownPdf, Section

from ingest.registry import REGISTRY_PATH, REPO_ROOT, read_csv

SOURCE_DIR = REPO_ROOT / "data" / "source"

# Minimal styling: visible table borders so header tables stay readable.
CSS = (
    "table { border-collapse: collapse; }"
    "th, td { border: 1px solid #999999; padding: 3px 6px; }"
    "blockquote { color: #444444; }"
)


def source_path(tenant_id: str, policy_id: str, version: int) -> Path:
    """Markdown authoring source for a PDF document (DATA_SPEC rule 9)."""
    return SOURCE_DIR / tenant_id / policy_id / f"v{version}.md"


def registry_pdf_path(
    tenant_id: str, policy_id: str, version: int, registry_path: Path = REGISTRY_PATH
) -> Path:
    """Return the registry target path; it must exist and be a .pdf."""
    _, rows = read_csv(registry_path)
    for row in rows:
        if (row["tenant_id"], row["policy_id"], row["version"]) == (
            tenant_id,
            policy_id,
            str(version),
        ):
            uri = row["source_uri"]
            if not uri.endswith(".pdf"):
                raise ValueError(f"{tenant_id}:{policy_id}:v{version} is registered as {uri}, not a PDF")
            return REPO_ROOT / uri
    raise KeyError(f"{tenant_id}:{policy_id}:v{version} is not in the registry")


def document_title(markdown: str) -> str:
    """The first level-1 heading becomes the PDF's title metadata."""
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    raise ValueError("source has no level-1 heading")


def render(source: Path, target: Path, *, overwrite: bool = False) -> Path:
    """Render `source` Markdown to `target` PDF; refuse to replace an existing file."""
    if target.exists() and not overwrite:
        raise FileExistsError(f"{target} exists; raw files are not overwritten (use --overwrite)")
    markdown = source.read_text(encoding="utf-8")
    pdf = MarkdownPdf(toc_level=2)  # headings up to level 2 become PDF bookmarks
    pdf.meta["title"] = document_title(markdown)
    pdf.meta["subject"] = "Synthetic document - fictional company for a portfolio project"
    pdf.add_section(Section(markdown, paper_size="Letter"), user_css=CSS)
    target.parent.mkdir(parents=True, exist_ok=True)
    pdf.save(str(target))
    return target


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render a registered PDF document from its Markdown source.")
    parser.add_argument("tenant_id")
    parser.add_argument("policy_id")
    parser.add_argument("version", type=int)
    parser.add_argument("--overwrite", action="store_true", help="replace an existing PDF")
    args = parser.parse_args(argv)

    try:
        target = registry_pdf_path(args.tenant_id, args.policy_id, args.version)
        render(source_path(args.tenant_id, args.policy_id, args.version), target, overwrite=args.overwrite)
    except (KeyError, ValueError, FileExistsError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"OK: wrote {target.relative_to(REPO_ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
