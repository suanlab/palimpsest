#!/usr/bin/env python3
"""Compile markdown manuscripts to PDF via pandoc + XeLaTeX.

Produces three PDFs:
  docs/submissions/track3_pnas/manuscript.pdf   (PNAS-style 2-column)
  docs/submissions/track1_nhb/manuscript.pdf    (Nature-style single column)
  docs/submissions/track2_note/manuscript.pdf   (Brief communication)

Also compiles SI appendix + cover letters.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from textwrap import dedent

ROOT = Path(__file__).resolve().parents[1]
SUB = ROOT / "docs" / "submissions"

# Pandoc's default template provides \documentclass, geometry, fontspec, hyperref, etc.
# Header-includes here add only per-style customizations.
PNAS_HEADER = dedent(r"""
    \usepackage{booktabs,array,microtype}
    \usepackage[hang,small,bf]{caption}
    \usepackage{titlesec}
    \titleformat{\section}{\normalfont\large\bfseries}{}{0em}{}
    \titleformat{\subsection}{\normalfont\normalsize\bfseries}{}{0em}{}
    \setlength{\parskip}{0.2em}
    \linespread{1.05}
""").strip()

NATURE_HEADER = dedent(r"""
    \usepackage{booktabs,array,microtype}
    \usepackage[hang,small,bf]{caption}
    \usepackage{titlesec}
    \titleformat{\section}{\normalfont\large\bfseries}{}{0em}{}
    \titleformat{\subsection}{\normalfont\normalsize\bfseries}{}{0em}{}
    \setlength{\parskip}{0.3em}
    \linespread{1.25}
""").strip()

NOTE_HEADER = dedent(r"""
    \usepackage{booktabs,array,microtype}
    \usepackage[hang,small,bf]{caption}
    \usepackage{titlesec}
    \titleformat{\section}{\normalfont\large\bfseries}{}{0em}{}
    \setlength{\parskip}{0.25em}
    \linespread{1.2}
""").strip()


def compile_md(src: Path, out_pdf: Path, header: str, two_column: bool = False) -> None:
    """Run pandoc → LaTeX → PDF."""
    header_file = src.parent / f".pandoc_header_{src.stem}.tex"
    header_file.write_text(header)

    cmd = [
        "pandoc", src.name,
        "-f", "markdown+pipe_tables+implicit_figures+tex_math_dollars",
        "--pdf-engine=xelatex",
        "-V", "mainfont=DejaVu Serif",
        "-V", "sansfont=DejaVu Sans",
        "-V", "monofont=DejaVu Sans Mono",
        "-V", "geometry:margin=2cm",
        "-V", "fontsize=10pt" if two_column else "fontsize=11pt",
        "-H", header_file.name,
        "--resource-path=.:figures:si_figures",
        "--toc-depth=2",
        "--wrap=preserve",
        "-o", out_pdf.name,
    ]
    print(f"  {src.relative_to(ROOT)} → {out_pdf.name}")
    # Run from manuscript's own directory so relative image paths resolve
    r = subprocess.run(cmd, capture_output=True, text=True, cwd=src.parent)
    if r.returncode != 0:
        print("  STDERR (last 20 lines):")
        for line in r.stderr.splitlines()[-20:]:
            print(f"    {line}")
        raise RuntimeError(f"pandoc failed on {src}")
    else:
        size_kb = out_pdf.stat().st_size / 1024
        print(f"    ok, {size_kb:.1f} KB")
    header_file.unlink(missing_ok=True)


def main() -> None:
    targets = [
        # Track 3 PNAS
        (SUB/"track3_pnas/manuscript.md",   SUB/"track3_pnas/manuscript.pdf",   NATURE_HEADER, False),
        (SUB/"track3_pnas/si_appendix.md",  SUB/"track3_pnas/si_appendix.pdf",  NATURE_HEADER, False),
        (SUB/"track3_pnas/cover_letter.md", SUB/"track3_pnas/cover_letter.pdf", NOTE_HEADER,   False),
        # Track 3 preprint (combined ms+SI for bioRxiv/SocArXiv)
        (SUB/"track3_preprint/preprint.md", SUB/"track3_preprint/preprint.pdf", NATURE_HEADER, False),
        # Track 1 NHB
        (SUB/"track1_nhb/manuscript.md",    SUB/"track1_nhb/manuscript.pdf",    NATURE_HEADER, False),
        (SUB/"track1_nhb/cover_letter.md",  SUB/"track1_nhb/cover_letter.pdf",  NOTE_HEADER,   False),
        # Track 2 note
        (SUB/"track2_note/manuscript.md",   SUB/"track2_note/manuscript.pdf",   NOTE_HEADER,   False),
    ]
    for src, pdf, header, twocol in targets:
        if not src.exists():
            print(f"  skip (missing): {src}")
            continue
        try:
            compile_md(src, pdf, header, twocol)
        except Exception as e:
            print(f"  FAILED: {e}")


if __name__ == "__main__":
    main()
