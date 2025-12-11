#!/usr/bin/env python3
"""
Generate docs/trustmark-glossary.md from a CSV exported from your SharePoint
glossary.

- Auto-detects CSV delimiter (comma, pipe, semicolon, etc).
- Renders the glossary as a safe HTML <table>.
- Shows: Name, Definition, Type, Domain, Metric Calculation.
- Hides: Source Document (still expected in the CSV).
- Adds contact banner and keeps your filter/search controls.
"""

from pathlib import Path
import sys
import pandas as pd
import html

# ============================================
# CONFIG – update if your layout differs
# ============================================

# Path to your exported CSV (relative to the repo root)
SOURCE_FILE = Path("data/trustmark_glossary.csv")

# Output Markdown file that MkDocs uses
OUTPUT_FILE = Path("docs") / "trustmark-glossary.md"

# Columns expected in the CSV (headers must match exactly)
EXPECTED_COLUMNS = [
    "Name",
    "Definition",
    "Type",
    "Domain",
    "Metric Calculation",
    "Source Document",   # required in CSV but not shown on the page
]


# ======================
# LOAD & CLEAN THE DATA
# ======================

def load_glossary_df() -> pd.DataFrame:
    """Load the CSV and normalise it into the expected columns."""
    if not SOURCE_FILE.exists():
        print(f"[ERROR] CSV not found: {SOURCE_FILE}")
        sys.exit(1)

    # Auto-detect the delimiter (comma / pipe / semicolon etc.)
    try:
        df = pd.read_csv(SOURCE_FILE, sep=None, engine="python")
    except Exception as exc:
        print(f"[ERROR] Failed to read CSV: {exc}")
        sys.exit(1)

    # Check all required columns exist
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        print("\n[ERROR] Missing columns in CSV:")
        for m in missing:
            print("  -", m)
        print("\nDetected columns in file:")
        print(", ".join(df.columns))
        print("\nMake sure your exported CSV headers match EXPECTED_COLUMNS.")
        sys.exit(1)

    # Keep only the columns we care about, in the right order
    df = df[EXPECTED_COLUMNS]

    # Strip whitespace from all fields
    for col in EXPECTED_COLUMNS:
        df[col] = df[col].astype(str).str.strip()

    # Tidy Name – if it accidentally starts with '|' from an old Markdown row
    df["Name"] = df["Name"].str.lstrip("| ").str.strip()

    # Drop rows without a Name or Definition
    df = df[(df["Name"] != "") & (df["Definition"] != "")]

    # Keep sheet order (no sorting) so you control ordering in Excel
    return df


# ======================
# HTML HELPERS
# ======================

def safe_html(value: str) -> str:
    """Escape any value for safe HTML display inside a table cell."""
    if pd.isna(value):
        value = ""
    text = str(value).strip()

    # Preserve line breaks
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\n", "<br>")

    # Escape HTML special chars (so |, [ ], etc. are just text)
    return html.escape(text, quote=True)


def build_html_table(df: pd.DataFrame) -> str:
    """Build the glossary table as HTML."""
    parts = []

    parts.append(
        '<table class="tm-glossary">\n'
        "  <thead>\n"
        "    <tr>\n"
        "      <th>Name</th>\n"
        "      <th>Definition</th>\n"
        "      <th>Type</th>\n"
        "      <th>Domain</th>\n"
        "      <th>Metric Calculation</th>\n"
        "    </tr>\n"
        "  </thead>\n"
        "  <tbody>\n"
    )

    for _, row in df.iterrows():
        raw_type = (row["Type"] or "").strip()
        data_type = raw_type.lower()  # e.g. "Term" → "term"

        name = safe_html(row["Name"])
        definition = safe_html(row["Definition"])
        type_html = safe_html(raw_type)
        domain = safe_html(row["Domain"])
        metric = safe_html(row["Metric Calculation"])

        parts.append(
            f'    <tr data-type="{html.escape(data_type, quote=True)}">\n'
            f"      <td>{name}</td>\n"
            f"      <td>{definition}</td>\n"
            f"      <td>{type_html}</td>\n"
            f"      <td>{domain}</td>\n"
            f"      <td>{metric}</td>\n"
            "    </tr>\n"
        )

    parts.append("  </tbody>\n</table>\n")

    return "".join(parts)


# ======================
# PAGE WRAPPER
# ======================

def build_page(df: pd.DataFrame) -> str:
    """Build the full Markdown page (controls + banner + heading + table)."""
    header = """<!-- Glossary controls -->

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

<em>This page is generated from the source glossary CSV via <code>export_glossary.py</code>.</em>

"""

    table = build_html_table(df)
    return header + "\n" + table


# ======================
# MAIN
# ======================

def main():
    df = load_glossary_df()
    page = build_page(df)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(page, encoding="utf-8")
    print(f"[OK] Glossary written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
