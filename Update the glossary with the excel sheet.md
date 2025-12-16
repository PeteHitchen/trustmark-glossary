1\. open PowerShell,

Whenever you change the Excel file:



1️⃣ Run the script

cd "C:\\Glossary WIP\\trustmark-glossary"

**python export\_glossary.py**



2️⃣ Commit \& deploy

**git add .**

**git commit -m "Update glossary"**

**git push**

**python -m mkdocs gh-deploy**





then:

**python -m mkdocs gh-deploy**





Within ~30 seconds, the live site refreshes.

