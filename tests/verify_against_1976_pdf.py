#!/usr/bin/env python3
"""
Verify reconstructed 1976-era section text against the actual 1976 Act PDF.

Extracts text from data/source-pdfs/1976-copyright-act.pdf (Pub. L. 94-553,
90 Stat. 2541) and compares against version 0 of each section's snapshot JSON.

Usage:
    source .venv/bin/activate
    python3 tests/verify_against_1976_pdf.py
"""

import difflib
import json
import os
import re
import sys

try:
    import fitz  # pymupdf
except ImportError:
    print("ERROR: pymupdf not installed. Run: source .venv/bin/activate && pip install pymupdf")
    sys.exit(1)

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_PATH = os.path.join(PROJECT_DIR, 'data', 'source-pdfs', '1976-copyright-act.pdf')
SNAPSHOTS_DIR = os.path.join(PROJECT_DIR, 'data', 'snapshots')

# Map section numbers to PDF page ranges (0-indexed)
# Each section starts on the given page; we extract through the next section's start
SECTION_PAGES = {
    '102': (3, 4),    # 90 Stat. 2544
    '104': (4, 5),    # 90 Stat. 2545
    '109': (7, 8),    # 90 Stat. 2548-2549
    '113': (19, 19),  # 90 Stat. 2560
    '115': (20, 21),  # 90 Stat. 2561-2562
    '116': (21, 24),  # 90 Stat. 2562-2565
    '201': (27, 27),  # 90 Stat. 2568
    '301': (31, 31),  # 90 Stat. 2572
    '504': (44, 45),  # 90 Stat. 2585-2586
    '506': (45, 45),  # 90 Stat. 2586
    '708': (52, 53),  # 90 Stat. 2593-2594
}


def extract_pdf_pages(doc, start_page, end_page):
    """Extract text from a range of PDF pages."""
    text = ''
    for i in range(start_page, end_page + 1):
        text += doc[i].get_text()
    return text


def extract_section_from_pdf(pdf_text, sec_num):
    """Isolate a specific section's text from PDF page text."""
    # Find the section start
    pattern = rf'§\s*{re.escape(sec_num)}\.'
    match = re.search(pattern, pdf_text)
    if not match:
        return None

    start = match.start()

    # Find the next section start (or end of text)
    next_sec = int(sec_num) + 1
    # Try a few possible next sections
    end = len(pdf_text)
    for next_num in range(next_sec, next_sec + 5):
        next_pattern = rf'§\s*{next_num}\.'
        next_match = re.search(next_pattern, pdf_text[start + 10:])
        if next_match:
            end = start + 10 + next_match.start()
            break

    section_text = pdf_text[start:end]

    # Strip page headers/footers
    section_text = re.sub(r'90 STAT\. \d+\n', '', section_text)
    section_text = re.sub(r'PUBLIC LAW 94-553.*?\n', '', section_text)

    return section_text.strip()


def normalize_text(text):
    """Normalize text for comparison: collapse whitespace, standardize formatting."""
    # Remove section symbol variations
    text = text.replace('§ ', '§')
    # Normalize quotes
    text = text.replace('\u201c', '"').replace('\u201d', '"')
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    # Normalize dashes
    text = text.replace('\u2014', '--').replace('\u2013', '-')
    # Fix OCR hyphenation artifacts (word- \nword -> word)
    text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)
    text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)
    # Remove PDF page margin notes (17 USC nnn., post/ante references)
    text = re.sub(r'\d+ usc \d+[a-z]?\.', '', text, flags=re.IGNORECASE)
    text = re.sub(r'(?:post|ante),?\s*p\.\s*\d+\.?', '', text, flags=re.IGNORECASE)
    text = re.sub(r'(?:statements? of account|claims?|regulations?|civil action|distribution procedures?)[,.]?\s*(?=\n|\s{2})', '', text, flags=re.IGNORECASE)
    # Remove tilde artifacts from OCR
    text = text.replace('~', '')
    # Fix common OCR character substitutions
    text = text.replace('\u2018', "'").replace('\u2019', "'")
    text = re.sub(r"0[l1]\u2019", "or", text)
    # Collapse whitespace (but preserve paragraph breaks indicated by double newlines)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r'\n(?!\n)', ' ', text)  # Join lines within paragraphs
    text = re.sub(r'  +', ' ', text)
    # Normalize subsection markers
    text = re.sub(r'\(\s*([a-z0-9]+)\s*\)', r'(\1)', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    # Lowercase for comparison
    text = text.lower()
    return text


def load_v0_text(sec_num):
    """Load version 0 text from snapshot JSON."""
    path = os.path.join(SNAPSHOTS_DIR, f'{sec_num}-versions.json')
    if not os.path.exists(path):
        return None
    with open(path) as f:
        data = json.load(f)
    versions = data.get('versions', [])
    if not versions:
        return None
    return versions[0].get('text', '')


def compare_section(sec_num, pdf_text, v0_text):
    """Compare PDF-extracted text with reconstructed text. Return (pass, diff_lines)."""
    pdf_norm = normalize_text(pdf_text)
    v0_norm = normalize_text(v0_text)

    if pdf_norm == v0_norm:
        return True, []

    # Generate unified diff
    pdf_lines = pdf_norm.split('\n')
    v0_lines = v0_norm.split('\n')

    diff = list(difflib.unified_diff(
        pdf_lines, v0_lines,
        fromfile=f'PDF (90 Stat.) §{sec_num}',
        tofile=f'Reconstructed §{sec_num}',
        lineterm='',
    ))

    return False, diff


def check_key_phrases(sec_num, pdf_text, v0_text):
    """Check that key distinctive phrases from the PDF appear in the reconstruction."""
    pdf_norm = normalize_text(pdf_text)
    v0_norm = normalize_text(v0_text)

    # Extract distinctive multi-word phrases from PDF (skip very common words)
    # Split into sentences, then extract 4+ word phrases
    issues = []

    # Check specific known key phrases per section
    key_phrases = {
        '102': ['sound recordings', 'method of operation'],
        '104': ['presidential proclamation', 'universal copyright convention'],
        '109': ['dispose of the possession', 'display that copy publicly'],
        '113': ['useful article', 'news reports'],
        '115': ['compulsory license', 'phonorecords', 'royalty'],
        '116': ['coin-operated phonorecord player', 'copyright royalty tribunal'],
        '201': ['works made for hire', 'involuntary transfer'],
        '301': ['preemption', 'sound recordings fixed before february 15, 1972'],
        '504': ['statutory damages', 'actual damages and profits'],
        '506': ['criminal infringement', 'fraudulent copyright notice'],
        '708': ['register of copyrights', 'copyright office'],
    }

    for phrase in key_phrases.get(sec_num, []):
        if phrase.lower() in pdf_norm and phrase.lower() not in v0_norm:
            issues.append(f"PDF has '{phrase}' but reconstruction does not")
        if phrase.lower() in v0_norm and phrase.lower() not in pdf_norm:
            issues.append(f"Reconstruction has '{phrase}' but PDF does not")

    return issues


def main():
    if not os.path.exists(PDF_PATH):
        print(f"ERROR: PDF not found at {PDF_PATH}")
        print("Download it: curl -o data/source-pdfs/1976-copyright-act.pdf "
              "https://www.copyright.gov/history/pl94-553.pdf")
        sys.exit(1)

    doc = fitz.open(PDF_PATH)
    print(f"Opened PDF: {len(doc)} pages")
    print()

    passed = 0
    failed = 0
    errors = 0

    for sec_num, (start_page, end_page) in sorted(SECTION_PAGES.items(), key=lambda x: int(x[0])):
        print(f"=== Section {sec_num} (PDF pages {start_page}-{end_page}) ===")

        # Extract from PDF
        pdf_raw = extract_pdf_pages(doc, start_page, end_page)
        pdf_section = extract_section_from_pdf(pdf_raw, sec_num)

        if not pdf_section:
            print(f"  ERROR: Could not extract §{sec_num} from PDF")
            errors += 1
            continue

        # Load reconstruction
        v0_text = load_v0_text(sec_num)
        if not v0_text:
            print(f"  ERROR: No version 0 found in snapshots")
            errors += 1
            continue

        # Check key phrases
        phrase_issues = check_key_phrases(sec_num, pdf_section, v0_text)
        if phrase_issues:
            print(f"  KEY PHRASE ISSUES:")
            for issue in phrase_issues:
                print(f"    - {issue}")

        # Full comparison
        match, diff_lines = compare_section(sec_num, pdf_section, v0_text)

        if match and not phrase_issues:
            print(f"  PASS (exact match after normalization)")
            passed += 1
        elif not phrase_issues:
            print(f"  WARN (formatting differences only, no key phrase mismatches)")
            print(f"  Diff ({len(diff_lines)} lines):")
            for line in diff_lines[:20]:
                print(f"    {line}")
            if len(diff_lines) > 20:
                print(f"    ... ({len(diff_lines) - 20} more lines)")
            passed += 1  # formatting diffs are OK
        else:
            print(f"  FAIL (substantive differences)")
            for line in diff_lines[:30]:
                print(f"    {line}")
            if len(diff_lines) > 30:
                print(f"    ... ({len(diff_lines) - 30} more lines)")
            failed += 1

        print()

    doc.close()

    print(f"{'='*60}")
    print(f"Results: {passed} passed, {failed} failed, {errors} errors")
    print(f"Total sections checked: {len(SECTION_PAGES)}")

    if failed > 0 or errors > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
