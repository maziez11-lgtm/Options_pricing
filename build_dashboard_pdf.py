"""Build dashboard_manual.pdf from dashboard_manual.md.

Run from project root:

    python build_dashboard_pdf.py
"""

from __future__ import annotations

from pathlib import Path

import markdown
from weasyprint import HTML, CSS

ROOT = Path(__file__).parent
SRC = ROOT / "dashboard_manual.md"
OUT = ROOT / "dashboard_manual.pdf"

CSS_STYLE = """
@page {
    size: A4;
    margin: 22mm 18mm 22mm 18mm;
    @top-center {
        content: "TTF Options Dashboard — User Manual";
        font-family: "Helvetica", "Arial", sans-serif;
        font-size: 9pt;
        color: #555;
        border-bottom: 0.4pt solid #aaa;
        padding-bottom: 4pt;
        width: 100%;
    }
    @bottom-center {
        content: "Page " counter(page) " of " counter(pages);
        font-family: "Helvetica", "Arial", sans-serif;
        font-size: 9pt;
        color: #555;
        border-top: 0.4pt solid #aaa;
        padding-top: 4pt;
        width: 100%;
    }
}

@page :first {
    @top-center { content: ""; border-bottom: 0; }
    @bottom-center { content: ""; border-top: 0; }
}

html, body {
    font-family: "Helvetica", "Arial", sans-serif;
    font-size: 10.5pt;
    line-height: 1.45;
    color: #1f2937;
}

h1, h2, h3, h4 {
    color: #0f172a;
    font-family: "Helvetica", "Arial", sans-serif;
    line-height: 1.25;
    page-break-after: avoid;
}

h1 { font-size: 22pt; margin-top: 0; border-bottom: 1.5pt solid #1e3a8a;
     padding-bottom: 6pt; }
h2 { font-size: 16pt; margin-top: 22pt;
     border-bottom: 0.6pt solid #94a3b8; padding-bottom: 4pt; }
h3 { font-size: 13pt; margin-top: 14pt; color: #1e3a8a; }
h4 { font-size: 11pt; margin-top: 10pt; color: #334155; }

p { margin: 6pt 0; text-align: justify; }

ul, ol { margin: 4pt 0 4pt 18pt; }
li { margin: 2pt 0; }

code {
    font-family: "Menlo", "Consolas", "Courier New", monospace;
    font-size: 9.5pt;
    background: #f1f5f9;
    border: 0.4pt solid #cbd5e1;
    border-radius: 2pt;
    padding: 0 3pt;
}

pre {
    font-family: "Menlo", "Consolas", "Courier New", monospace;
    font-size: 9pt;
    background: #0f172a;
    color: #e2e8f0;
    padding: 8pt 10pt;
    border-radius: 4pt;
    overflow-x: auto;
    page-break-inside: avoid;
}

pre code {
    background: transparent;
    border: 0;
    color: inherit;
    padding: 0;
}

blockquote {
    margin: 8pt 0;
    padding: 4pt 10pt;
    border-left: 3pt solid #1e3a8a;
    background: #f8fafc;
    color: #334155;
}

table {
    border-collapse: collapse;
    margin: 8pt 0 12pt 0;
    width: 100%;
    font-size: 9.5pt;
    page-break-inside: avoid;
}
th, td {
    border: 0.4pt solid #cbd5e1;
    padding: 4pt 6pt;
    text-align: left;
    vertical-align: top;
}
th {
    background: #1e3a8a;
    color: #ffffff;
    font-weight: 600;
}
tr:nth-child(even) td { background: #f8fafc; }

img {
    display: block;
    max-width: 100%;
    margin: 12pt auto;
    border: 0.5pt solid #cbd5e1;
    border-radius: 3pt;
    page-break-inside: avoid;
}

hr {
    border: 0;
    border-top: 0.6pt solid #94a3b8;
    margin: 16pt 0;
}

a { color: #1e3a8a; text-decoration: none; }

/* Cover */
.cover {
    page-break-after: always;
    text-align: center;
    padding-top: 60mm;
}
.cover h1 {
    font-size: 30pt;
    border: 0;
    color: #1e3a8a;
}
.cover .subtitle {
    font-size: 14pt;
    color: #475569;
    margin-top: 10pt;
}
.cover .meta {
    margin-top: 40mm;
    font-size: 11pt;
    color: #64748b;
}

/* Table of contents */
.toc {
    page-break-after: always;
}
.toc h2 {
    border-bottom: 1pt solid #1e3a8a;
    margin-top: 0;
}
.toc ul {
    list-style: none;
    padding-left: 0;
}
.toc ul ul { padding-left: 16pt; }
.toc li { margin: 4pt 0; }
.toc a {
    color: #0f172a;
    text-decoration: none;
}
.toc .toc-h2 { font-weight: 600; font-size: 11pt; }
.toc .toc-h3 { color: #475569; font-size: 10pt; }

/* Force page breaks before each top-level section */
h2 { page-break-before: always; }
h2.first-section { page-break-before: auto; }
"""


def build_toc(md_text: str) -> str:
    """Build a manual table of contents from the markdown headings.

    We only include H2 (## ) and H3 (### ) entries.
    """
    items: list[tuple[int, str, str]] = []
    for raw in md_text.splitlines():
        line = raw.rstrip()
        if line.startswith("## ") and not line.startswith("### "):
            title = line[3:].strip()
            items.append((2, title, _slug(title)))
        elif line.startswith("### "):
            title = line[4:].strip()
            items.append((3, title, _slug(title)))

    out = ['<div class="toc"><h2>Table of contents</h2><ul>']
    for level, title, slug in items:
        cls = "toc-h2" if level == 2 else "toc-h3"
        out.append(f'<li class="{cls}"><a href="#{slug}">{title}</a></li>')
    out.append("</ul></div>")
    return "\n".join(out)


def _slug(title: str) -> str:
    """Markdown 'toc' extension slugify rules (lowercase, dash-separated)."""
    import re
    s = title.lower()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s).strip("-")
    return s


def main() -> None:
    md_text = SRC.read_text(encoding="utf-8")

    # Convert markdown to HTML
    md = markdown.Markdown(
        extensions=["extra", "tables", "fenced_code", "toc", "sane_lists"],
        extension_configs={"toc": {"toc_depth": "2-3"}},
    )
    html_body = md.convert(md_text)

    cover = (
        '<div class="cover">'
        "<h1>TTF Options Dashboard</h1>"
        '<div class="subtitle">User Manual</div>'
        '<div class="meta">'
        "Sections 1 – 7 · Pricer · Structures · Vol Surface · TTF/HH Spread · Expiries · Troubleshooting"
        "</div>"
        "</div>"
    )

    toc_html = build_toc(md_text)

    full_html = (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>TTF Options Dashboard — User Manual</title>"
        "</head><body>"
        + cover
        + toc_html
        + html_body
        + "</body></html>"
    )

    HTML(string=full_html, base_url=str(ROOT)).write_pdf(
        target=str(OUT),
        stylesheets=[CSS(string=CSS_STYLE)],
    )
    print(f"Wrote {OUT}  ({OUT.stat().st_size / 1024:.0f} kB)")


if __name__ == "__main__":
    main()
