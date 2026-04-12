#!/usr/bin/env python3
"""
Fetch current text of all Title 17 sections from uscode.house.gov.
Saves each section as a markdown file in data/current-sections/.
"""

import os
import re
import subprocess
import sys
import html
from concurrent.futures import ThreadPoolExecutor, as_completed

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'current-sections')
NOTES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'amendment-notes')

# All sections of Title 17
SECTIONS = [
    # Chapter 1
    '101', '102', '103', '104', '104A', '105', '106', '106A',
    '107', '108', '109', '110', '111', '112', '113', '114', '115',
    '116', '117', '118', '119', '120', '121', '121A', '122',
    # Chapter 2
    '201', '202', '203', '204', '205',
    # Chapter 3
    '301', '302', '303', '304', '305',
    # Chapter 4
    '401', '402', '403', '404', '405', '406', '407', '408', '409',
    '410', '411', '412',
    # Chapter 5
    '501', '502', '503', '504', '505', '506', '507', '508', '509',
    '510', '511', '512', '513',
    # Chapter 6
    '601', '602', '603',
    # Chapter 7
    '701', '702', '703', '704', '705', '706', '707', '708',
    # Chapter 8
    '801', '802', '803', '804', '805',
    # Chapter 9
    '901', '902', '903', '904', '905', '906', '907', '908', '909',
    '910', '911', '912', '913', '914',
    # Chapter 10
    '1001', '1002', '1003', '1004', '1005', '1006', '1007', '1008',
    '1009', '1010',
    # Chapter 11
    '1101',
    # Chapter 12
    '1201', '1202', '1203', '1204', '1205',
    # Chapter 13
    '1301', '1302', '1303', '1304', '1305', '1306', '1307', '1308',
    '1309', '1310',
    # Chapter 14
    '1401', '1402', '1403', '1404',
    # Chapter 15
    '1501', '1502', '1503', '1504', '1505',
]


def clean_html_to_text(raw_html):
    """Convert HTML to readable text, preserving structure."""
    text = raw_html

    # Remove script and style tags
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)

    # Convert common block elements to newlines
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</?p[^>]*>', '\n', text)
    text = re.sub(r'</?div[^>]*>', '\n', text)
    text = re.sub(r'</?tr[^>]*>', '\n', text)

    # Strip remaining tags
    text = re.sub(r'<[^>]+>', '', text)

    # Unescape HTML entities
    text = html.unescape(text)

    # Clean up whitespace
    lines = text.split('\n')
    cleaned = []
    for line in lines:
        line = line.strip()
        if line:
            cleaned.append(line)

    return '\n'.join(cleaned)


def extract_section_text(raw_html, section_num):
    """Extract the statute text from OLRC HTML page."""
    # The main content is usually in a div with class containing "content"
    # Try to find the statutory text portion

    # Look for the section heading
    # Pattern: "§101." or "§ 101." etc.
    text = clean_html_to_text(raw_html)

    # Find where the actual section text starts
    # Usually after navigation/header stuff
    lines = text.split('\n')

    # Find the section heading line
    start_idx = 0
    for i, line in enumerate(lines):
        if re.search(rf'§\s*{re.escape(section_num)}[\.\s]', line):
            start_idx = i
            break
        if f'Section {section_num}' in line and ('—' in line or '-' in line):
            start_idx = i
            break

    # Find where amendment notes start (end of statute text)
    end_idx = len(lines)
    for i in range(start_idx, len(lines)):
        if any(marker in lines[i] for marker in [
            'Editorial Notes', 'Historical and Revision Notes',
            'Amendments', 'References in Text', 'Statutory Notes',
            'Source Credit', 'HISTORICAL AND STATUTORY NOTES',
        ]):
            end_idx = i
            break

    section_text = '\n'.join(lines[start_idx:end_idx]).strip()

    # Also extract amendment notes (everything after)
    notes_text = '\n'.join(lines[end_idx:]).strip()

    return section_text, notes_text


def fetch_section(section_num):
    """Fetch a single section from OLRC."""
    url = f"https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title17-section{section_num}&num=0&edition=prelim"

    try:
        result = subprocess.run(
            ['curl', '-s', '--max-time', '30', url],
            capture_output=True, text=True, timeout=35
        )
        if result.returncode != 0:
            return section_num, None, None, f"curl failed: {result.stderr}"

        raw_html = result.stdout
        if not raw_html or len(raw_html) < 500:
            return section_num, None, None, "empty or too short response"

        section_text, notes_text = extract_section_text(raw_html, section_num)

        return section_num, section_text, notes_text, None

    except Exception as e:
        return section_num, None, None, str(e)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(NOTES_DIR, exist_ok=True)

    print(f"Fetching {len(SECTIONS)} sections of Title 17...")

    success = 0
    failed = 0

    # Use thread pool for parallel fetching
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(fetch_section, sec): sec
            for sec in SECTIONS
        }

        for future in as_completed(futures):
            sec_num, text, notes, error = future.result()

            if error:
                print(f"  FAILED Section {sec_num}: {error}")
                failed += 1
                continue

            if text:
                # Save section text
                filepath = os.path.join(OUTPUT_DIR, f'{sec_num}.md')
                with open(filepath, 'w') as f:
                    f.write(f'# 17 U.S.C. § {sec_num}\n\n')
                    f.write(text)
                    f.write('\n')

                # Save amendment notes separately
                if notes:
                    notes_path = os.path.join(NOTES_DIR, f'{sec_num}-notes.md')
                    with open(notes_path, 'w') as f:
                        f.write(f'# Amendment Notes for 17 U.S.C. § {sec_num}\n\n')
                        f.write(notes)
                        f.write('\n')

                success += 1
                print(f"  OK Section {sec_num} ({len(text)} chars)")
            else:
                print(f"  EMPTY Section {sec_num}")
                failed += 1

    print(f"\nDone: {success} succeeded, {failed} failed")
    print(f"Section text saved to: {OUTPUT_DIR}")
    print(f"Amendment notes saved to: {NOTES_DIR}")


if __name__ == '__main__':
    main()
