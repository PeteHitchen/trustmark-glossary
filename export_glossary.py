#!/usr/bin/env python3
"""
Generate docs/trustmark-glossary.md from a source CSV (SharePoint export)
and render the table in pure HTML so NOTHING can break.

This version:
- Outputs a safe HTML <table>
- Works with any characters: | [ ] () <> markdown symbols
- Hides the Source Document column
"""

from pathlib import Path
import sys
import pandas as pd
import html

# =============================
# CONFIG
# =============================

SOURCE_FILE = Path("data/trustmark_glossary.csv")
OUTPUT_FILE = Path("docs") / "trustmark-glossary.md"

EXPECTED_COLUMNS = [
    "Name",
    "Definition",
    "Type",
    "Domain",
    "Metric Calculation",
    "Source Document",   # still required in CSV, not shown
]

# =============================
# LOAD DATA
# =============================

def load_glossary_df():
    if not SOURCE_FILE.exists():
        print(f"[ERROR] CSV not found: {SOURCE_FILE}")
        sys.exit(1)

    df = pd.read_csv(SOURCE_FILE)

    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        print("\n[ERROR] Missing columns in CSV:")
        for m in missing:
            print("  -", m)
        sys.exit(1)

    df = df[EXPECTED_COLUMNS]

    # Clean whitespace
    for col in EXPECTED_COLUMNS:
        df[col] = df[col].astype(str).str.strip()

    # Remove empty entries
    df = df[(df["Name"] != "") & (df["Definition"] != "")]

    return df


# =============================
# ESCAPING + HTML BUILDER
# =============================

def safe_html(value):
    """Convert any value to safe HTML text."""
    if pd.isna(value):
        return ""
    text = str(value).strip()

    # Escape ALL HTML-sensitive characters
    text = html.escape(text)

    # Convert newlines to <br>
    text = text.replace("\n", "<br>")

    return text


def build_html_table(df):
    """Return an HTML table string with escaped safe content."""

    html_rows = []

    # Header row
    html_rows.append("""
<table class="tm-glossary">
  <thead>
    <tr>
      <th>Name</th>
      <th>Definition</th>
      <th>Type</th>
      <th>Domain</th>
      <th>Metric Calculation</th>
    </tr>
  </thead>
  <tbody>
""")

    # Table rows
    for _, row in df.iterrows():
        name = safe_html(row["Name"])
        definition = safe_html(row["Definition"])
        type_ = safe_html(row["Type"])
        domain = safe_html(row["Domain"])
        metric = safe_html(row["Metric Calculation"])

        html_rows.append(f"""
    <tr>
      <td>{name}</td>
      <td>{definition}</td>
      <td>{type_}</td>
      <td>{domain}</td>
      <td>{metric}</td>
    </tr>
""")

    html_rows.append("""
  </tbody>
</table>
""")

    return "".join(html_rows)


# =============================
# PAGE HEADER BUILDER
# =============================

def build_header():
    return """<!-- Glossary controls -->

<div class="glossary-controls">
  <button class="tm-btn" data-type="all">All</button>
  <button class="tm-btn" data-type="term">Term</button>
  <button class="tm-btn" data-type="acronym">Acronym</button>
  <button class="tm-btn" data-type="metric">Metric</button>
  <input id="glossary-search" type="text" placeholder="Search all columns…" />
</div>

<div class="glossary-contact">
For any edits or additions to this TrustMark Glossary, please contact
<a href="mailto:phitchen@trustmark.org.uk">Pete Hitchen</a>.
</div>

# TrustMark Glossary

"""


# =============================
# MAIN
# =============================

def main():
    df = load_glossary_df()
    html_table = build_html_table(df)
    page = build_header() + html_table

    OUTPUT_FILE.write_text(page, encoding="utf-8")
    print(f"[OK] glossary written → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
