#!/usr/bin/env python3
"""Build Track 3 PNAS submission using the official pnas-new.cls template.

Pipeline:
  1. Parse sections (Abstract, Significance, Introduction, Results, Discussion,
     Methods, References, etc.) from manuscript.md
  2. Convert Results + Discussion prose to LaTeX via pandoc
  3. Assemble into a tex file based on _template/main.tex
  4. Copy figures, bibliography
  5. Compile with pdflatex + bibtex + pdflatex + pdflatex

Outputs:
  docs/submissions/track3_pnas/build/manuscript.tex
  docs/submissions/track3_pnas/build/manuscript.pdf (compiled)
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "submissions" / "track3_pnas"
BUILD = SRC / "build"
TMPL = SRC / "_template"
FIGS = SRC / "figures"


# ---------- parsing helpers ----------
def read_md(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_section(txt: str, name: str) -> str:
    """Return body of `## name` section up to next `## `."""
    pat = rf"^## {re.escape(name)}\n(.*?)(?=^## |\Z)"
    m = re.search(pat, txt, re.MULTILINE | re.DOTALL)
    if not m:
        return ""
    body = m.group(1).strip()
    # Strip trailing markdown horizontal rules
    body = re.sub(r"\n+-{3,}\s*$", "", body).strip()
    return body


UNI_MAP = {
    "−": "$-$",  # U+2212 minus sign
    "≥": r"$\geq$", "≤": r"$\leq$", "≠": r"$\neq$",
    "≈": r"$\approx$", "∼": r"$\sim$",
    "×": r"$\times$", "·": r"$\cdot$",
    "±": r"$\pm$", "∓": r"$\mp$",
    "χ": r"$\chi$", "β": r"$\beta$", "α": r"$\alpha$", "γ": r"$\gamma$",
    "κ": r"$\kappa$",
    "Δ": r"$\Delta$", "δ": r"$\delta$", "μ": r"$\mu$", "σ": r"$\sigma$",
    "ρ": r"$\rho$", "λ": r"$\lambda$", "π": r"$\pi$", "Σ": r"$\Sigma$",
    "²": r"$^{2}$", "³": r"$^{3}$",
    "⁰": r"$^{0}$", "¹": r"$^{1}$", "⁴": r"$^{4}$", "⁵": r"$^{5}$",
    "⁶": r"$^{6}$", "⁷": r"$^{7}$", "⁸": r"$^{8}$", "⁹": r"$^{9}$",
    "⁻": r"$^{-}$",
    "₀": r"$_{0}$", "₁": r"$_{1}$", "₂": r"$_{2}$", "₃": r"$_{3}$",
    "₄": r"$_{4}$",
    "→": r"$\to$", "←": r"$\leftarrow$",
    "–": "--", "—": "---",
    "‘": "`", "’": "'",
    "“": "``", "”": "''",
    "…": r"\dots",
    "∈": r"$\in$",
    " ": "~",  # non-breaking space
}

def map_unicode(s: str) -> str:
    # Compound superscripts like 10⁻¹⁶ → 10\(^{-16}\)
    def super_sub(pat):
        supers = {"⁰":"0","¹":"1","²":"2","³":"3","⁴":"4","⁵":"5","⁶":"6","⁷":"7","⁸":"8","⁹":"9","⁻":"-"}
        content = "".join(supers.get(c, c) for c in pat.group(0))
        return f"$^{{{content}}}$"
    s = re.sub(r"[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]{2,}", super_sub, s)
    for k, v in UNI_MAP.items():
        s = s.replace(k, v)
    return s


def latex_escape_inline(s: str) -> str:
    """Escape LaTeX specials in prose NOT going through pandoc
    (significance/abstract macro arguments). Unicode math has already been
    mapped to \\(...\\) inline-math form, which must pass through unchanged.
    Do NOT escape backslashes here — we need the inline math intact."""
    s = s.replace("%", r"\%")
    s = s.replace("&", r"\&")
    s = s.replace("#", r"\#")
    s = s.replace("_", r"\_")
    # Markdown italic *p* -> \textit{p}
    s = re.sub(r"(?<![*\w])\*([^*\n]{1,12}?)\*(?![*\w])", r"\\textit{\1}", s)
    return s


def md_to_latex(md: str) -> str:
    """Convert markdown fragment to LaTeX; map Unicode symbols in the tex output."""
    r = subprocess.run(
        ["pandoc", "-f", "markdown+pipe_tables", "-t", "latex"],
        input=md, capture_output=True, text=True, check=True
    )
    out = r.stdout
    out = re.sub(r"\\section\{", r"\\section*{", out)
    out = re.sub(r"\\subsection\{", r"\\subsection*{", out)
    out = re.sub(r"\\subsubsection\{", r"\\subsubsection*{", out)
    # Post-pandoc Unicode mapping: pandoc emitted raw UTF-8 characters; replace
    # them with LaTeX math commands that pdflatex can render.
    out = map_unicode(out)
    # Convert `(1, 2)`-style citations to \cite{refN,...}
    out = convert_inline_citations(out)
    return out


def extract_refs(txt: str) -> list[tuple[int, str]]:
    """Parse the References section into (number, text) tuples."""
    refs_section = extract_section(txt, "References")
    refs = []
    for m in re.finditer(r"^(\d+)\.\s+(.+?)(?=^\d+\.\s|\Z)", refs_section, re.MULTILINE | re.DOTALL):
        num = int(m.group(1))
        body = m.group(2).strip()
        refs.append((num, body))
    return refs


def to_bibtex(refs: list[tuple[int, str]]) -> str:
    """Convert parsed references to a minimal .bib file (misc entries)."""
    lines = []
    for num, body in refs:
        key = f"ref{num}"
        # Strip markdown emphasis
        body_clean = re.sub(r"\*\*([^*]+)\*\*", r"\1", body)
        body_clean = re.sub(r"\*([^*]+)\*", r"\1", body_clean)
        # Escape BibTeX specials
        body_clean = body_clean.replace("{", "").replace("}", "")
        body_clean = body_clean.replace("&", r"\&").replace("%", r"\%")
        body_clean = body_clean.replace("\n", " ").strip()
        lines.append(f"@misc{{{key},\n  note = {{{body_clean}}}\n}}\n")
    return "\n".join(lines)


def convert_inline_citations(tex: str) -> str:
    """Convert `(1)`, `(1, 2)`, `(1, 2, 4)`, `(1–3)` to `\\cite{ref1,ref2,...}`.

    Applied to pandoc's tex output. Matches `(N)` and `(N, M)` and `(N–M)` ranges
    where numbers are plausible ref indices (1-99).
    """
    def expand(m):
        body = m.group(1)
        refs = []
        for part in re.split(r",\s*", body):
            rng = re.match(r"^(\d{1,3})[-–](\d{1,3})$", part.strip())
            if rng:
                lo, hi = int(rng.group(1)), int(rng.group(2))
                refs.extend(range(lo, hi + 1))
            else:
                n = re.match(r"^(\d{1,3})$", part.strip())
                if n:
                    refs.append(int(n.group(1)))
                else:
                    return m.group(0)  # non-numeric -> leave intact
        if not refs or max(refs) > 99:
            return m.group(0)
        keys = ",".join(f"ref{r}" for r in refs)
        return f"\\cite{{{keys}}}"

    # Match parenthesised lists of 1-3 comma/range-separated numbers
    return re.sub(r"\((\d{1,3}(?:(?:\s*[,–-]\s*\d{1,3}){0,5}))\)", expand, tex)


# ---------- pnas tex assembly ----------
PNAS_PREAMBLE = r"""\documentclass[9pt,twocolumn,twoside]{pnas-new}

\templatetype{pnasresearcharticle}

\title{The Half-Life of Bad Science: Citation Persistence and Knowledge Contamination After Retraction}

\author[a,1]{Suan Lee}

\affil[a]{Semyung University, Chungcheongbuk-do, Republic of Korea}

\leadauthor{Lee}

\significancestatement{SIGNIFICANCE_PLACEHOLDER}

\authorcontributions{S.L. is the sole author of this work. S.L. designed the study, built the Neo4j citation graph, constructed the matched-control sample, performed the statistical analyses (matched-control, survival, propensity-score matching, paper-mill stratification, citation-context sampling), generated all figures, and wrote the manuscript.}
\authordeclaration{The authors declare no competing interests.}
\correspondingauthor{\textsuperscript{1}To whom correspondence should be addressed. E-mail: suanlee@semyung.ac.kr.}

\keywords{retraction $|$ citation networks $|$ metascience $|$ paper mills $|$ scientific integrity}

% pandoc compatibility: provide missing commands
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\providecommand{\passthrough}[1]{#1}

\begin{abstract}
ABSTRACT_PLACEHOLDER
\end{abstract}

\dates{This manuscript was compiled on \today}
\doi{\url{www.pnas.org/cgi/doi/10.1073/pnas.XXXXXXXXXX}}

\begin{document}

\maketitle
\thispagestyle{firststyle}
\ifthenelse{\boolean{shortarticle}}{\ifthenelse{\boolean{singlecolumn}}{\abscontentformatted}{\abscontent}}{}

"""

PNAS_POSTAMBLE_TEMPLATE = r"""
\matmethods{METHODS_PLACEHOLDER}
\showmatmethods{}

\acknow{ACKNOW_PLACEHOLDER}
\showacknow{}

\begin{thebibliography}{99}
BIBITEMS_PLACEHOLDER
\end{thebibliography}

\end{document}
"""


FIG_TEMPLATE = r"""\begin{figure*}[tbp]
\centering
\includegraphics[width=\textwidth]{PATH}
\caption{CAPTION}
\label{fig:LABEL}
\end{figure*}
"""

# Smaller, single-column figure environment (PNAS one-column = ~3.4 in wide).
# Used for figures whose content is simple enough not to need the full
# two-column page width.
FIG_TEMPLATE_SMALL = r"""\begin{figure}[tbp]
\centering
\includegraphics[width=\columnwidth]{PATH}
\caption{CAPTION}
\label{fig:LABEL}
\end{figure}
"""

# Path stems that should use the small (single-column) figure environment.
SMALL_FIGURE_STEMS = {"fig_policy_sim"}


def extract_figures(md: str) -> list[str]:
    """Parse `![caption](path)` blocks and build PNAS figure* environments."""
    figs = []
    for m in re.finditer(r"!\[([^\]]+)\]\(([^)]+)\)", md):
        caption_md = m.group(1).strip()
        path = m.group(2).strip()
        # Strip the manual "**Fig. N.**" / "**Figure N.**" prefix — pnas-new.cls
        # automatically prepends "Fig. N." via \caption{}, so we keep only the
        # descriptive body and avoid the doubled "Fig. 1. Fig. 1." rendering.
        caption_md = re.sub(
            r"^\*\*(?:Fig(?:ure)?\.?\s*\d+[A-Za-z]?\.?)\*\*\s*",
            "",
            caption_md,
        )
        # Convert markdown emphasis in caption
        cap = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", caption_md)
        cap = re.sub(r"\*([^*]+)\*", r"\\emph{\1}", cap)
        cap = map_unicode(cap).replace("&", r"\&").replace("%", r"\%")
        label = Path(path).stem
        template = (FIG_TEMPLATE_SMALL if label in SMALL_FIGURE_STEMS
                    else FIG_TEMPLATE)
        figs.append(template.replace("PATH", path).replace("CAPTION", cap).replace("LABEL", label))
    return figs


def build_tex(ms_md: str) -> str:
    # Title & abstract
    abstract = extract_section(ms_md, "Abstract")
    significance = extract_section(ms_md, "Significance Statement")
    intro = extract_section(ms_md, "Introduction")
    results = extract_section(ms_md, "Results")
    discussion = extract_section(ms_md, "Discussion")
    methods = extract_section(ms_md, "Materials and Methods")
    ack = extract_section(ms_md, "Acknowledgments") or "We thank the Retraction Watch team and the OpenAlex team. Funding: [to be completed]."
    figures_section = extract_section(ms_md, "Figures")

    # Convert body sections
    intro_tex = md_to_latex(intro)
    results_tex = md_to_latex(results)
    discussion_tex = md_to_latex(discussion)
    methods_tex = md_to_latex(methods)
    ack_tex = md_to_latex(ack).strip()

    # Assemble body — PNAS convention: no "Introduction" heading
    body = []
    # Dropcap on first word of intro
    first_para = intro.split("\n\n", 1)
    if first_para:
        fp = first_para[0]
        fp_rest = first_para[1] if len(first_para) > 1 else ""
        # Remove leading inline markdown (bold/italic) from dropcap
        first_word_match = re.match(r"^(?:\*+)?(\w+)(?:\*+)?", fp.strip())
        if first_word_match:
            letter = first_word_match.group(1)[0]
            rest = fp.strip()[len(first_word_match.group(0)):]
            # First paragraph with dropcap
            first_para_tex = md_to_latex(rest).strip()
            # Remove any wrapping $...$ or outer \par etc.
            body.append(f"\\dropcap{{{letter}}}{first_para_tex}\n")
            if fp_rest:
                body.append(md_to_latex(fp_rest))
        else:
            body.append(intro_tex)
    # Insert figures after Introduction, before Results
    fig_blocks = extract_figures(figures_section)
    if fig_blocks:
        body.extend(fig_blocks)
    # Results as section
    body.append("\\section*{Results}\n" + results_tex)
    body.append("\\section*{Discussion}\n" + discussion_tex)

    # Clean placeholders + escape LaTeX specials (Unicode first, then LaTeX escapes)
    abstract_clean = latex_escape_inline(map_unicode(abstract.replace("\n", " ").strip()))
    significance_clean = latex_escape_inline(map_unicode(significance.replace("\n", " ").strip()))

    tex = PNAS_PREAMBLE.replace("SIGNIFICANCE_PLACEHOLDER", significance_clean)
    tex = tex.replace("ABSTRACT_PLACEHOLDER", abstract_clean)
    tex += "\n\n".join(body)

    # Build \bibitem list directly from the parsed references (avoid BibTeX's
    # strict field requirements; the PNAS style is approximated inline).
    refs = extract_refs(ms_md)
    bibitems = []
    for num, body_ref in refs:
        body_clean = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", body_ref)
        body_clean = re.sub(r"\*([^*]+)\*", r"\\emph{\1}", body_clean)
        body_clean = body_clean.replace("&", r"\&").replace("%", r"\%")
        body_clean = map_unicode(body_clean).replace("\n", " ").strip()
        bibitems.append(f"\\bibitem{{ref{num}}} {body_clean}")
    bibitem_block = "\n\n".join(bibitems)

    tex += (PNAS_POSTAMBLE_TEMPLATE
            .replace("METHODS_PLACEHOLDER", methods_tex)
            .replace("BIBITEMS_PLACEHOLDER", bibitem_block))
    tex = tex.replace("ACKNOW_PLACEHOLDER", ack_tex)
    return tex


def main() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    # Copy template class/style files
    for f in ["pnas-new.cls", "pnas-new.bst", "pnasresearcharticle.sty", "widetext.sty"]:
        shutil.copy(TMPL / f, BUILD / f)
    # Copy figures directory
    if (BUILD / "figures").exists():
        shutil.rmtree(BUILD / "figures")
    shutil.copytree(FIGS, BUILD / "figures")

    ms = read_md(SRC / "manuscript.md")
    tex = build_tex(ms)
    (BUILD / "manuscript.tex").write_text(tex)

    # BibTeX from references
    refs = extract_refs(ms)
    (BUILD / "citations.bib").write_text(to_bibtex(refs))
    print(f"Wrote manuscript.tex ({len(tex)} chars) and citations.bib ({len(refs)} refs)")


if __name__ == "__main__":
    main()
