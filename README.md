📘 TrustMark Business Glossary

This repository hosts the TrustMark Business Glossary — a single, authoritative source of business terms, metrics, and acronyms used across TrustMark.

The glossary is maintained in a structured Excel source file and published as a static website using MkDocs and GitHub Pages.

🌐 Live site

The published glossary is available at:

https://petehitchen.github.io/trustmark-glossary/trustmark-glossary/

🧩 Repository structure
Location	Purpose
/Data	Source Excel file containing glossary terms, metrics, and acronyms
/docs	MkDocs source content (Markdown, assets, CSS, JS)
/site	Generated static site output
mkdocs.yml	MkDocs configuration
export_glossary.py	Script used to generate glossary content from Excel
Update the glossary with the excel sheet.md	Step-by-step update instructions
✏️ How to update the glossary

Open the Excel file in /Data

Add or edit glossary entries

Do not rename column headers

Save the file

Run export_glossary.py (if required)

Commit and push changes to the repository

GitHub Pages will automatically republish the site within a few minutes

🧭 Editorial principles

Definitions should be clear and plain English

Metrics must include calculation logic

Acronyms must be expanded on first use

Avoid duplicate or overlapping terms

👤 Ownership

Technical & content owner: Philip Vaughan

Purpose: Shared business reference for TrustMark

ℹ️ Notes

The /site directory contains generated output

The source of truth is the Excel file and Markdown in /docs

No content is dependent on any individual’s local machine
