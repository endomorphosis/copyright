#!/usr/bin/env python3
"""
Transform per-section version histories into per-act section snapshots
that the build script can consume.

Reads: data/snapshots/SECTION-versions.json (from reconstruct.py)
Writes: data/act-snapshots/DATE-ACTNAME/SECTION.md (for build.py)
"""

import json
import os
import re
import sys

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
SNAPSHOTS_DIR = os.path.join(DATA_DIR, 'snapshots')
ACT_SNAPSHOTS_DIR = os.path.join(DATA_DIR, 'act-snapshots')


def strip_source_credit(text):
    """Remove the trailing source credit block (Pub. L. references) from section text."""
    lines = text.strip().split('\n')
    # Find where source credit starts — look for a line that's just "("
    # followed by "Pub. L." references
    cut_idx = len(lines)
    for i in range(len(lines) - 1, max(0, len(lines) - 30), -1):
        line = lines[i].strip()
        if line == '(' or (line.startswith('(') and 'Pub. L.' in '\n'.join(lines[i:])):
            # Check if this looks like a source credit block
            remaining = '\n'.join(lines[i:])
            if 'Pub. L.' in remaining and remaining.rstrip().endswith(')'):
                cut_idx = i
                break
    result = '\n'.join(lines[:cut_idx]).rstrip()
    return result


def sanitize_filename(name):
    name = re.sub(r'\s*\([^)]*\)\s*', ' ', name)
    name = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    return name[:60].rstrip('-') if len(name) > 60 else name


def load_acts():
    """Load acts from acts.yaml."""
    with open(os.path.join(os.path.dirname(DATA_DIR), 'metadata', 'acts.yaml')) as f:
        content = f.read()

    entries = re.split(r'\n(?=- name:)', '\n' + content)
    acts = []
    for entry in entries:
        entry = entry.strip()
        if not entry.startswith('- name:'):
            continue
        m_name = re.search(r'name:\s*(.+)', entry)
        m_date = re.search(r'date:\s*(.+)', entry)
        m_pl = re.search(r'public_law:\s*(.+)', entry)
        if m_name and m_date:
            pl = m_pl.group(1).strip() if m_pl else ''
            # Normalize PL
            pl_num = re.sub(r'Pub\. L\. ', '', pl).strip()
            acts.append({
                'name': m_name.group(1).strip(),
                'date': m_date.group(1).strip(),
                'pl_num': pl_num,
            })
    acts.sort(key=lambda x: x['date'])
    return acts


def main():
    acts = load_acts()
    print(f"Loaded {len(acts)} acts")

    # Build PL -> act mapping
    pl_to_act = {}
    for act in acts:
        if act['pl_num']:
            pl_to_act[act['pl_num']] = act

    # Load all section version histories
    section_versions = {}
    for fname in os.listdir(SNAPSHOTS_DIR):
        if not fname.endswith('-versions.json'):
            continue
        sec = fname.replace('-versions.json', '')
        with open(os.path.join(SNAPSHOTS_DIR, fname)) as f:
            data = json.load(f)
        section_versions[sec] = data

    print(f"Loaded version histories for {len(section_versions)} sections")

    # For each act, find which sections have a version at that point
    # and write the section text to the act's snapshot directory
    acts_with_snapshots = 0
    sections_written = 0

    for act in acts:
        pl = act['pl_num']
        if not pl:
            continue

        act_dir_name = f"{act['date']}-{sanitize_filename(act['name'])}"
        act_dir = os.path.join(ACT_SNAPSHOTS_DIR, act_dir_name)

        # Find all sections that have a version for this PL.
        # Each version's text is the text BEFORE that amendment was applied
        # (since versions are built by reverse-applying amendments).
        # For act-snapshots we need the text AFTER the amendment, which is
        # the next version's text in the list.
        found_sections = []
        for sec, data in section_versions.items():
            versions = data.get('versions', [])
            for i, version in enumerate(versions):
                if version.get('public_law') == pl:
                    # Use the NEXT version's text (= post-amendment text)
                    if i + 1 < len(versions):
                        found_sections.append((sec, versions[i + 1]))
                    break

        if not found_sections:
            continue

        # Clean out old files before writing new ones
        if os.path.isdir(act_dir):
            for old_file in os.listdir(act_dir):
                if old_file.endswith('.md'):
                    os.remove(os.path.join(act_dir, old_file))
        os.makedirs(act_dir, exist_ok=True)
        acts_with_snapshots += 1

        for sec, version in found_sections:
            text = version.get('text', '')
            if text:
                # Strip source credit block from text
                text = strip_source_credit(text)
                path = os.path.join(act_dir, f'{sec}.md')
                with open(path, 'w') as f:
                    f.write(f'# 17 U.S.C. § {sec}\n\n')
                    f.write(text.strip())
                    f.write('\n')
                sections_written += 1

    print(f"\nCreated snapshots for {acts_with_snapshots} acts")
    print(f"Total section files written: {sections_written}")
    print(f"Output directory: {ACT_SNAPSHOTS_DIR}")


if __name__ == '__main__':
    main()
