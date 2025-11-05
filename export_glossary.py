from pathlib import Path
import pandas as pd

proj = Path(__file__).resolve().parent
xlsx = Path(r"C:\Users\PeterHitchen\OneDrive - TrustMark (2005) Limited\The TrustMark Data Guild - Data Governance\Business Glossary\TrustMark_Glossary raw file.xlsx")
page = proj / "docs" / "trustmark-glossary.md"

# Load Excel exactly as-is (keeps your columns and order)
df = pd.read_excel(xlsx)
df.columns = [str(c).strip() for c in df.columns]
df = df.dropna(how="all").fillna("")

def esc(v):
  s = "" if v is None else str(v)
  return s.replace("|","\\|").replace("\r\n","<br>").replace("\n","<br>")

cols = list(df.columns)
table = []
table.append("| " + " | ".join(cols) + " |")
table.append("| " + " | ".join(["---"]*len(cols)) + " |")
for _, row in df.iterrows():
  vals = [esc(row[c]) for c in cols]
  table.append("| " + " | ".join(vals) + " |")

# Insert/replace the table after the H1 heading
src = page.read_text(encoding="utf-8")
needle = "# TrustMark Glossary"
if needle in src:
    head, _, after = src.partition(needle)
    new_content = head + needle + "\n\n" + "\n".join(table) + "\n"
else:
    new_content = src.rstrip() + "\n\n" + "\n".join(table) + "\n"

page.write_text(new_content, encoding="utf-8")
print(f"Exported {len(df)} rows and {len(cols)} columns into {page}")
