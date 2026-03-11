"""
Tool: export_pdf — Convert a markdown file to a styled PDF report.

Uses fpdf2 (pure Python, no system dependencies) to produce a professional
PDF with typography, tables, headers, and page layout.
"""

import re
from pathlib import Path

from fpdf import FPDF


PROJECT_ROOT = Path(__file__).parent.parent
TMP_DIR = PROJECT_ROOT / ".tmp"

# Color palette
NAVY = (13, 59, 102)
GREEN = (26, 107, 60)
DARK = (26, 26, 26)
GRAY = (100, 100, 100)
LIGHT_BG = (248, 249, 250)
WHITE = (255, 255, 255)
TABLE_HEADER_BG = (13, 59, 102)
TABLE_HEADER_FG = (255, 255, 255)
TABLE_ALT_BG = (240, 244, 248)
TABLE_BORDER = (200, 200, 200)
CODE_BG = (244, 244, 244)


class ReportPDF(FPDF):
    def __init__(self, title="Report"):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.report_title = title
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(*GRAY)
            self.cell(0, 6, self.report_title, align="L")
            self.ln(2)
            self.set_draw_color(*TABLE_BORDER)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(6)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*GRAY)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def _parse_table(lines, start):
    rows = []
    i = start
    while i < len(lines) and "|" in lines[i]:
        row_text = lines[i].strip()
        if row_text.startswith("|"):
            row_text = row_text[1:]
        if row_text.endswith("|"):
            row_text = row_text[:-1]
        cells = [c.strip() for c in row_text.split("|")]
        if cells and all(re.match(r"^[-:]+$", c) for c in cells if c):
            i += 1
            continue
        if cells:
            rows.append(cells)
        i += 1
    return rows, i


def _strip_md(text):
    """Strip markdown formatting to plain text."""
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)  # links
    text = text.replace("**", "").replace("*", "").replace("`", "")
    # Replace common unicode that fpdf can't handle
    text = text.replace("\u2014", "--").replace("\u2013", "-")
    text = text.replace("\u2018", "'").replace("\u2019", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2026", "...").replace("\u00a0", " ")
    text = text.replace("\u2248", "~").replace("\u2265", ">=").replace("\u2264", "<=")
    text = text.replace("\u2022", "-")
    # Replace checkmarks/crosses
    text = text.replace("\u2705", "[Y]").replace("\u274c", "[N]")
    text = text.replace("\u2b50", "[*]").replace("\u2753", "[?]")
    text = text.replace("\u26a0\ufe0f", "[!]").replace("\u26a0", "[!]")
    text = text.replace("\u2139\ufe0f", "[i]")
    text = text.replace("\U0001f404", "[cow]")
    text = text.replace("\U0001f415", "[dog]")
    # Encode to latin-1, replacing unknown chars
    text = text.encode("latin-1", errors="replace").decode("latin-1")
    return text


def _render_table(pdf, rows):
    if not rows or len(rows) < 2:
        return

    num_cols = max(len(r) for r in rows)
    if num_cols == 0:
        return

    usable_width = 190
    col_widths = []
    for col_idx in range(num_cols):
        max_len = 0
        for row in rows:
            if col_idx < len(row):
                max_len = max(max_len, len(_strip_md(row[col_idx])))
        col_widths.append(max(max_len, 3))

    total = sum(col_widths)
    col_widths = [(w / total) * usable_width for w in col_widths]

    # Cap columns
    for i in range(len(col_widths)):
        col_widths[i] = min(col_widths[i], usable_width * 0.55)
    total = sum(col_widths)
    col_widths = [(w / total) * usable_width for w in col_widths]

    if pdf.get_y() + 20 > 270:
        pdf.add_page()

    def render_header():
        header = rows[0]
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_fill_color(*TABLE_HEADER_BG)
        pdf.set_text_color(*TABLE_HEADER_FG)
        pdf.set_draw_color(*TABLE_HEADER_BG)
        for idx in range(num_cols):
            w = col_widths[idx]
            cell_text = _strip_md(header[idx]) if idx < len(header) else ""
            pdf.cell(w, 6.5, cell_text[:55], border=1, fill=True, align="L")
        pdf.ln()

    render_header()

    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_draw_color(*TABLE_BORDER)

    for row_idx, row in enumerate(rows[1:], 1):
        if pdf.get_y() + 6.5 > 275:
            pdf.add_page()
            render_header()
            pdf.set_font("Helvetica", "", 7.5)
            pdf.set_draw_color(*TABLE_BORDER)

        if row_idx % 2 == 0:
            pdf.set_fill_color(*TABLE_ALT_BG)
        else:
            pdf.set_fill_color(*WHITE)

        pdf.set_text_color(*DARK)
        for idx in range(num_cols):
            w = col_widths[idx]
            cell_text = _strip_md(row[idx]) if idx < len(row) else ""
            display = cell_text[:65] + ("..." if len(cell_text) > 65 else "")
            pdf.cell(w, 6.5, display, border=1, fill=True, align="L")
        pdf.ln()

    pdf.ln(3)


def export_pdf(input_file, output_file=None):
    """Convert a markdown file to a styled PDF."""
    input_path = Path(input_file)
    if not input_path.is_absolute():
        input_path = PROJECT_ROOT / input_path

    if not input_path.exists():
        return f"ERROR: File not found: {input_path}"

    if output_file:
        output_path = Path(output_file)
        if not output_path.is_absolute():
            output_path = PROJECT_ROOT / output_file
    else:
        output_path = input_path.with_suffix(".pdf")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        md_content = input_path.read_text(encoding="utf-8")
        lines = md_content.split("\n")

        # Extract title
        title = "Report"
        for line in lines:
            if line.startswith("# ") and not line.startswith("## "):
                title = _strip_md(line[2:].strip())
                break

        pdf = ReportPDF(title=title)
        pdf.alias_nb_pages()
        pdf.add_page()

        # ── Cover Page ──
        pdf.set_font("Helvetica", "B", 26)
        pdf.set_text_color(*NAVY)
        pdf.ln(35)
        pdf.multi_cell(0, 11, title, align="C")
        pdf.ln(4)

        # Subtitle
        for line in lines[:10]:
            if line.startswith("## ") and not line.startswith("### "):
                pdf.set_font("Helvetica", "", 13)
                pdf.set_text_color(*GRAY)
                pdf.multi_cell(0, 7, _strip_md(line[3:].strip()), align="C")
                break

        pdf.ln(6)
        pdf.set_draw_color(*NAVY)
        pdf.set_line_width(0.8)
        pdf.line(60, pdf.get_y(), 150, pdf.get_y())
        pdf.ln(8)

        # Meta info from early lines
        for line in lines[:20]:
            if line.startswith("**") and ":**" in line:
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(*GRAY)
                pdf.cell(0, 6, _strip_md(line), align="C")
                pdf.ln(5)

        pdf.add_page()

        # ── Render Body ──
        i = 0
        in_code_block = False
        code_buffer = []
        skip_cover = True

        while i < len(lines):
            line = lines[i]

            # Skip first title/subtitle (already on cover)
            if skip_cover and i < 6:
                if line.startswith("# ") or (line.startswith("## ") and i < 5):
                    i += 1
                    continue
                if line.strip() == "---":
                    skip_cover = False
                    i += 1
                    continue

            # Horizontal rules
            if line.strip() in ("---", "***", "___"):
                pdf.set_draw_color(*TABLE_BORDER)
                pdf.line(10, pdf.get_y() + 1, 200, pdf.get_y() + 1)
                pdf.ln(5)
                i += 1
                continue

            # Code blocks
            if line.strip().startswith("```"):
                if in_code_block:
                    in_code_block = False
                    if code_buffer:
                        if pdf.get_y() + len(code_buffer) * 3.5 > 270:
                            pdf.add_page()
                        pdf.set_fill_color(*CODE_BG)
                        pdf.set_draw_color(*TABLE_BORDER)
                        pdf.set_font("Courier", "", 7)
                        pdf.set_text_color(51, 51, 51)
                        code_text = "\n".join(code_buffer)
                        code_text = _strip_md(code_text)
                        pdf.multi_cell(190, 3.5, code_text, fill=True, border=1)
                        pdf.ln(3)
                    code_buffer = []
                else:
                    in_code_block = True
                    code_buffer = []
                i += 1
                continue

            if in_code_block:
                code_buffer.append(line)
                i += 1
                continue

            # Tables
            if "|" in line and i + 1 < len(lines) and "|" in lines[i + 1]:
                rows, new_i = _parse_table(lines, i)
                if rows and len(rows) >= 2:
                    _render_table(pdf, rows)
                i = new_i
                continue

            # H1
            if line.startswith("# ") and not line.startswith("## "):
                if pdf.get_y() > 235:
                    pdf.add_page()
                pdf.ln(5)
                pdf.set_font("Helvetica", "B", 18)
                pdf.set_text_color(*NAVY)
                pdf.multi_cell(0, 9, _strip_md(line[2:].strip()))
                pdf.set_draw_color(*NAVY)
                pdf.set_line_width(0.5)
                pdf.line(10, pdf.get_y() + 1, 200, pdf.get_y() + 1)
                pdf.ln(4)
                i += 1
                continue

            # H2
            if line.startswith("## "):
                if pdf.get_y() > 245:
                    pdf.add_page()
                pdf.ln(4)
                pdf.set_font("Helvetica", "B", 14)
                pdf.set_text_color(*GREEN)
                pdf.multi_cell(0, 7, _strip_md(line[3:].strip()))
                pdf.set_draw_color(*GREEN)
                pdf.set_line_width(0.3)
                pdf.line(10, pdf.get_y() + 1, 100, pdf.get_y() + 1)
                pdf.ln(3)
                i += 1
                continue

            # H3
            if line.startswith("### "):
                if pdf.get_y() > 255:
                    pdf.add_page()
                pdf.ln(3)
                pdf.set_font("Helvetica", "B", 11.5)
                pdf.set_text_color(44, 62, 80)
                pdf.multi_cell(0, 6, _strip_md(line[4:].strip()))
                pdf.ln(2)
                i += 1
                continue

            # H4
            if line.startswith("#### "):
                pdf.ln(2)
                pdf.set_font("Helvetica", "B", 10)
                pdf.set_text_color(52, 73, 94)
                pdf.multi_cell(0, 5.5, _strip_md(line[5:].strip()))
                pdf.ln(1.5)
                i += 1
                continue

            # Bullet points
            if re.match(r"^\s*[-*]\s+", line):
                content = re.sub(r"^\s*[-*]\s+", "", line).strip()
                indent = len(line) - len(line.lstrip())
                pdf.set_font("Helvetica", "", 9.5)
                pdf.set_text_color(*DARK)
                left_margin = 12 + (indent * 2)
                pdf.set_x(left_margin)
                pdf.cell(4, 5, "-", align="R")
                pdf.cell(2)
                pdf.multi_cell(190 - left_margin - 6, 5, _strip_md(content))
                pdf.ln(0.5)
                i += 1
                continue

            # Numbered lists
            num_match = re.match(r"^\s*(\d+)\.\s+", line)
            if num_match:
                content = re.sub(r"^\s*\d+\.\s+", "", line).strip()
                pdf.set_font("Helvetica", "B", 9.5)
                pdf.set_text_color(*NAVY)
                pdf.cell(8, 5, f"{num_match.group(1)}.", align="R")
                pdf.cell(2)
                pdf.set_font("Helvetica", "", 9.5)
                pdf.set_text_color(*DARK)
                pdf.multi_cell(180, 5, _strip_md(content))
                pdf.ln(0.5)
                i += 1
                continue

            # Empty lines
            if not line.strip():
                pdf.ln(2)
                i += 1
                continue

            # Regular paragraph
            pdf.set_font("Helvetica", "", 9.5)
            pdf.set_text_color(*DARK)
            pdf.multi_cell(0, 5, _strip_md(line.strip()))
            pdf.ln(1.5)
            i += 1

        pdf.output(str(output_path))
        return f"PDF saved to: {output_path}"

    except Exception as e:
        return f"ERROR: PDF generation failed: {type(e).__name__}: {e}"
