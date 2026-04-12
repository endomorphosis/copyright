#!/usr/bin/env python3
"""
Reconstruct historical versions of Title 17 sections by reverse-applying amendments.

For each section, reads the current text and amendment notes, then works backward
through each amendment to reconstruct the text at each point in time.

This handles simple substitution/insertion/deletion amendments automatically.
Complex amendments are flagged for manual review.
"""

import json
import os
import re
import sys


DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
SECTIONS_DIR = os.path.join(DATA_DIR, 'current-sections')
NOTES_DIR = os.path.join(DATA_DIR, 'amendment-notes')
SNAPSHOTS_DIR = os.path.join(DATA_DIR, 'snapshots')


def load_section_text(sec_num):
    """Load the current text of a section."""
    path = os.path.join(SECTIONS_DIR, f'{sec_num}.md')
    if not os.path.exists(path):
        return None
    with open(path) as f:
        content = f.read()
    # Strip the markdown header and source credit at the end
    lines = content.strip().split('\n')
    # Remove "# 17 U.S.C. §" header
    if lines and lines[0].startswith('#'):
        lines = lines[1:]
    # Remove trailing source credit (lines starting with "(" or "Pub. L.")
    while lines and (lines[-1].strip().startswith('(') or
                     lines[-1].strip().startswith('Pub.') or
                     lines[-1].strip().startswith(';') or
                     lines[-1].strip().startswith(')') or
                     lines[-1].strip() == ''):
        lines.pop()
    return '\n'.join(lines).strip()


def parse_amendment_notes(sec_num):
    """Parse amendment notes to extract structured change descriptions."""
    path = os.path.join(NOTES_DIR, f'{sec_num}-notes.md')
    if not os.path.exists(path):
        return []

    with open(path) as f:
        content = f.read()

    # Find the "Amendments" section
    amendments_start = content.find('Amendments')
    if amendments_start == -1:
        amendments_start = content.find('Amendment')
    if amendments_start == -1:
        return []

    amendments_text = content[amendments_start:]

    # Parse individual amendments
    # Pattern: year followed by PL reference and description
    amendments = []

    # Split by year headers or PL references
    entries = re.split(r'\n(\d{4})-?\n?', amendments_text)

    current_year = None
    for i, entry in enumerate(entries):
        if re.match(r'^\d{4}$', entry.strip()):
            current_year = entry.strip()
            continue

        if not current_year:
            continue

        # Find PL references and their descriptions
        pl_entries = re.split(r'(Pub\.\s*L\.\s*\d+.?\d+)', entry)
        current_pl = None
        for part in pl_entries:
            pl_match = re.match(r'Pub\.\s*L\.\s*(\d+).(\d+)', part)
            if pl_match:
                current_pl = f"{pl_match.group(1)}-{pl_match.group(2)}"
                continue
            if current_pl and part.strip():
                # This is the description of what the PL changed
                desc = part.strip()
                # Clean up
                desc = re.sub(r'^[,;\s]+', '', desc)
                desc = re.sub(r'\s+', ' ', desc)
                if desc and len(desc) > 5:
                    amendments.append({
                        'year': current_year,
                        'public_law': current_pl,
                        'description': desc,
                    })
                    current_pl = None  # Reset for next

    return amendments


def apply_simple_substitution(text, old_str, new_str):
    """Apply a simple substitution, return new text or None if not found."""
    if old_str in text:
        return text.replace(old_str, new_str, 1)
    return None


def reverse_amendment(text, amendment_desc):
    """
    Try to reverse-apply an amendment based on its description.
    Returns (reversed_text, success, method).
    """
    desc = amendment_desc.lower()

    # Pattern: substituted "X" for "Y"
    sub_match = re.search(
        r'substituted\s+["\u201c]([^"\u201d]+)["\u201d]\s+for\s+["\u201c]([^"\u201d]+)["\u201d]',
        amendment_desc, re.IGNORECASE
    )
    if sub_match:
        new_text = sub_match.group(1)
        old_text = sub_match.group(2)
        result = apply_simple_substitution(text, new_text, old_text)
        if result:
            return result, True, f"reversed substitution: '{new_text}' -> '{old_text}'"

    # Pattern: inserted "X" (at end, after Y, etc.)
    insert_match = re.search(
        r'inserted\s+(?:at end\s+)?["\u201c]([^"\u201d]+)["\u201d]',
        amendment_desc, re.IGNORECASE
    )
    if insert_match:
        inserted_text = insert_match.group(1)
        if inserted_text in text:
            result = text.replace(inserted_text, '', 1).strip()
            return result, True, f"removed inserted text: '{inserted_text[:50]}...'"

    # Pattern: struck out/struck "X"
    struck_match = re.search(
        r'(?:struck out|struck)\s+["\u201c]([^"\u201d]+)["\u201d]',
        amendment_desc, re.IGNORECASE
    )
    if struck_match:
        struck_text = struck_match.group(1)
        # To reverse: we need to re-insert it, but we don't always know where
        # Flag for manual review
        return text, False, f"MANUAL: need to re-insert struck text: '{struck_text[:50]}...'"

    # Pattern: added par. (X) / added subsec. (X)
    added_match = re.search(
        r'added\s+(?:par|subsec|subpar|cl)\.\s*\((\w+)\)',
        amendment_desc, re.IGNORECASE
    )
    if added_match:
        return text, False, f"MANUAL: need to remove added paragraph/subsection ({added_match.group(1)})"

    return text, False, f"UNHANDLED: {amendment_desc[:80]}..."


def reconstruct_section(sec_num, verbose=False):
    """Reconstruct all historical versions of a section."""
    current_text = load_section_text(sec_num)
    if not current_text:
        return None

    amendments = parse_amendment_notes(sec_num)
    if not amendments:
        # No amendments = section unchanged since 1976
        return {
            'section': sec_num,
            'versions': [{
                'act': 'Copyright Act of 1976',
                'date': '1976-10-19',
                'public_law': '94-553',
                'text': current_text,
                'note': 'No amendments since enactment'
            }],
            'issues': []
        }

    # Sort amendments chronologically (most recent first for reverse application)
    amendments.sort(key=lambda x: x['year'], reverse=True)

    versions = []
    issues = []
    text = current_text

    # Current version
    versions.append({
        'act': 'Current',
        'date': 'current',
        'text': text
    })

    # Reverse through amendments
    for amend in amendments:
        reversed_text, success, method = reverse_amendment(text, amend['description'])

        if success:
            text = reversed_text
            if verbose:
                print(f"  OK [{amend['year']}] PL {amend['public_law']}: {method}")
        else:
            issues.append({
                'year': amend['year'],
                'public_law': amend['public_law'],
                'issue': method
            })
            if verbose:
                print(f"  ?? [{amend['year']}] PL {amend['public_law']}: {method}")

        versions.append({
            'year': amend['year'],
            'public_law': amend['public_law'],
            'description': amend['description'],
            'text': text,
            'auto_reversed': success
        })

    # Reverse so oldest is first
    versions.reverse()

    return {
        'section': sec_num,
        'versions': versions,
        'issues': issues
    }


def main():
    os.makedirs(SNAPSHOTS_DIR, exist_ok=True)

    # Get all sections with amendment notes
    sections_with_notes = []
    for fname in sorted(os.listdir(NOTES_DIR)):
        if fname.endswith('-notes.md'):
            sec = fname.replace('-notes.md', '')
            sections_with_notes.append(sec)

    print(f"Processing {len(sections_with_notes)} sections with amendment notes...")

    total_auto = 0
    total_manual = 0
    total_versions = 0

    for sec in sections_with_notes:
        result = reconstruct_section(sec, verbose=True)
        if not result:
            continue

        n_versions = len(result['versions'])
        n_issues = len(result['issues'])
        n_auto = n_versions - n_issues - 1  # -1 for current version

        total_versions += n_versions
        total_auto += max(0, n_auto)
        total_manual += n_issues

        # Save result
        out_path = os.path.join(SNAPSHOTS_DIR, f'{sec}-versions.json')
        # Don't overwrite manually created versions
        if os.path.exists(out_path):
            print(f"  Section {sec}: skipping (manual version exists)")
            continue

        with open(out_path, 'w') as f:
            json.dump(result, f, indent=2)

        status = f"{n_auto} auto, {n_issues} manual" if n_issues else f"{n_auto} auto"
        print(f"  Section {sec}: {n_versions} versions ({status})")

    print(f"\nSummary:")
    print(f"  Total versions: {total_versions}")
    print(f"  Auto-reversed: {total_auto}")
    print(f"  Need manual review: {total_manual}")


if __name__ == '__main__':
    main()
