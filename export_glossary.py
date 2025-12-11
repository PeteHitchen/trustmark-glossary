#!/usr/bin/env python3
"""
Generate docs/trustmark-glossary.md from a source spreadsheet/CSV.

HOW TO USE
----------
1. Export your SharePoint glossary sheet to a CSV file.
2. Save it in this repo and update SOURCE_FILE below to point to it.
3. Make sure the column names in COLUMN_MAP match your CSV headers.
4. Run:  python export_glossary.py
"""

from pathlib import Path
import sys
import pandas as pd

# =============================
# CONFIG – UPDATE FOR YOUR SETUP
# =============================

# Path to your exported CSV (relative to repo root)
# e.g. export your SharePoint sheet to "data/trustmark_glossary.csv"
SOURCE_FILE = Path("data/trustmark_glossary.csv")

# Expected column names in the CSV.
# LEFT side: what the script uses
# RIGHT side: the actual header text in your CSV
COLUMN_MAP = {
    "term": "Term",             # REQUIRED
    "definition": "Definition", # REQUIRED
    # Optional extras – comment out or change header names as needed
    "category": "Category",     # e.g. "Data Protection", "Governance", etc.
    "owner": "Owner",           # e.g. "Data Team"
    "aka": "Also known as",     # e.g. abbreviations or synonyms
    "notes": "Notes",           # any commentary
}

# Output location for the generated glossary markdown
OUTPUT_FILE = Path("docs") / "trustmark-glossary.md"

# =============================
# SCRIPT LOGIC – USUALLY NO NEED TO CHANGE BELOW HERE
# =============================


def load_glossary_df() -> pd.DataFrame:
    """Load the glossary from the configured CSV file."""
    if not SOURCE_FILE.exists():
        print(f"[ERROR] Source file not found: {SOURCE_FILE}")
        print("        Please export your SharePoint sheet to CSV and "
              "update SOURCE_FILE in export_glossary.py.")
        sys.exit(1)

    df = pd.read_csv(SOURCE_FILE)

    # Ensure required columns exist
    for logical_name in ("term", "definition"):
        csv_col = COLUMN_MAP.get(logical_name)
        if csv_col not in df.columns:
            print(f"[ERROR] Required column '{csv_col}' "
                  f"(for '{logical_name}') not found in CSV.")
            print("        Check COLUMN_MAP in export_glossary.py "
                  "matches your CSV headers.")
            sys.exit(1)

    # Normalise column names to the logical keys used below
    mapped_cols = {}
    for logical_name, csv_col in COLUMN_MAP.items():
        if csv_col in df.columns:
            mapped_cols[logical_name] = csv_col

    df = df.rename(columns={v: k for k, v in mapped_cols.items()})

    # Trim whitespace
    df["term"] = df["term"].astype(str).str.strip()
    df["definition"] = df["definition"].astype(str).str.strip()

    # Drop rows without a term or definition
    df = df[(df["term"] != "") & (df["definition"] != "")]

    # Sort alphabetically by term (case-insensitive)
    df = df.sort_values("term", key=lambda s: s.str.lower())

    return df


def build_header() -> str:
    """Return the static header for the glossary page, including the contact text."""
    return """# TrustMark Glossary

<div class="glossary-contact">
For any edits or additions to this TrustMark Glossary, please contact <a href="mailto:phitchen@trustmark.org.uk">Pete Hitchen</a>.
</div>

---

"""


def build_entry(row: pd.Series) -> str:
    """Build the markdown for a single glossary entry."""
    term = row.get("term", "").strip()
    definition = row.get("definition", "").strip()

    # Optional metadata
    category = str(row.get("category", "") or "").strip()
    owner = str(row.get("owner", "") or "").strip()
    aka = str(row.get("aka", "") or "").strip()
    notes = str(row.get("notes", "") or "").strip()

    md_parts = []

    # Term as H2
    md_parts.append(f"## {term}\n")
    md_parts.append(f"{definition}\n")

    # Add a small metadata list if anything is present
    meta_lines = []
    if category:
        meta_lines.append(f"- **Category:** {category}")
    if aka:
        meta_lines.append(f"- **Also known as:** {aka}")
    if owner:
        meta_lines.append(f"- **Owner:** {owner}")
    if notes:
        meta_lines.append(f"- **Notes:** {notes}")

    if meta_lines:
        md_parts.append("\n" + "\n".join(meta_lines) + "\n")

    # Blank line between entries
    md_parts.append("\n")

    return "".join(md_parts)


def build_glossary_markdown(df: pd.DataFrame) -> str:
    """Build the full markdown for the glossary page."""
    header = build_header()
    entries = []

    for _, row in df.iterrows():
        entries.append(build_entry(row))

    return header + "".join(entries)


def main():
    df = load_glossary_df()
    markdown = build_glossary_markdown(df)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(markdown, encoding="utf-8")

    print(f"[OK] Generated glossary markdown: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
