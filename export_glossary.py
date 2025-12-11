#!/usr/bin/env python3
"""
Generate docs/trustmark-glossary.md from a source CSV exported from SharePoint.

This version:
- Escapes ALL problematic characters (|, newlines, etc.)
- Prevents table row collapse
- Displays ONLY: Name, Definition, Type, Domain, Metric Calculation
- Keeps your controls + contact text
"""

from pathlib import Path
import sys
import pandas as pd

# =============================
# CONFIG – UPDATE IF NEEDED
# =============================

# Path to your exported CSV (relative to repo root)
SOURCE_FILE = Path("data/trustmark_glossary.csv")

# Output location
OUTPUT_FILE = Path("docs") / "trustmark-glossary.md"

# Expected columns (Source Document is required but not displayed)
EXPECTED_COLUMNS = [
    "Name",
    "Definition",
    "Type",
    "Domain",
    "Metric Calculation",
    "Source Document",
]

# =============================
# LOADING + SANITISING
# =============================


def load_glossary_df() -> pd.DataFrame:
    if not SOURCE_FILE.exists():
        print(f"[ERROR] CSV not found: {SOURCE_FILE}")
        sys.exit(1)

    df = pd.read_csv(SOURCE_FILE)

    # Check required headers exist
    missing = [col for col in EXPECTED_COLUMNS if col not in df.columns]
    if missing:
        print("[ERROR] Missing columns:")
        for m in missing:
            print("  -", m)
        sys.exit(1)

    # Keep the relevant columns
    df = df[EXPECTED_COLUMNS]

    # Strip whitespace
    for col in EXPECTED_COLUMNS:
        df[col] = df[col].astype(str).str.strip()

    # Drop rows with missing Name/Definition
    df = df[(df["Name"] != "") & (df["Definition"] != "")]

    return df


def escape_cell(value: str) -> str:
    """Escape content so it is 100% safe for Markdown tables."""
    if pd.isna(value):
        value = ""
    value = str(value)

    # escape pipes so they don't split the table
    value = value.replace("|", "\\|")

    # Convert any newlines into <br>
    value = value.replace("\r\n", "\n")
    value = value.replace("\r", "\n")
    value = value.replace("\n", "<br>")

    # Strip again after transformations
    return value.strip()


# =============================
# CONTENT BUILDERS
# =============================


def build_header() -> str:
    """Static top of the glossary page + table header."""
    return """<!-- Load our styles and scripts from this folder (no leading slash) -->

<div class="glossary-controls">
  <button class="tm-btn" data-type="all">All</button>
  <button class="tm-btn" data-type="term">Term</button>
  <button class="tm-btn" data-type="acronym">Acronym</button>
  <button class="tm-btn" data-type="metric">Metric</button>
  <input id="glossary-search" type="text" placeholder="Search all columns…" />
</div>

<div class="glossary-contact">
For any edits or additions to this TrustMark Glossary, please contact <a href="mailto:phitchen@trustmark.org.uk">Pete Hitchen</a>.
</div>

# TrustMark Glossary

| Name | Definition | Type | Domain | Metric Calculation |
| --- | --- | --- | --- | --- |
"""


def build_table_rows(df: pd.DataFrame) -> str:
    """Generate clean Markdown rows for the table."""
    lines = []

    for _, row in df.iterrows():

        name = escape_cell(row["Name"])
        definition = escape_cell(row["Definition"])
        type_ = escape_cell(row["Type"])
        domain = escape_cell(row["Domain"])
        metric = escape_cell(row["Metric Calculation"])

        # Build the row safely
        line = f"| {name} | {definition} | {type_} | {domain} | {metric} |"
        lines.append(line)

    return "\n".join(lines) + "\n"


def build_markdown(df: pd.DataFrame) -> str:
    return build_header() + build_table_rows(df)


# =============================
# MAIN
# =============================


def main():
    df = load_glossary_df()
    md = build_markdown(df)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(md, encoding="utf-8")

    print(f"[OK] Built glossary → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
