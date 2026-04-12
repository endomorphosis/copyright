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


def build_act_sections_map(acts):
    """Build a map from act name -> set of section numbers, using source credits
    in current-sections to correctly attribute sections to specific acts
    (including title-level disambiguation for shared PLs).
    """
    current_dir = os.path.join(DATA_DIR, 'current-sections')
    if not os.path.isdir(current_dir):
        return {}

    # Build PL base -> list of acts (to find shared PLs)
    pl_acts = {}
    for act in acts:
        pl_base = act['pl_num'].split(',')[0].strip()
        if pl_base:
            pl_acts.setdefault(pl_base, []).append(act)

    result = {}  # act name -> set of section numbers

    for fname in sorted(os.listdir(current_dir)):
        if not fname.endswith('.md'):
            continue
        sec = fname.replace('.md', '')

        with open(os.path.join(current_dir, fname)) as f:
            content = f.read()

        # Normalize dashes
        normalized = content.replace('\u2013', '-').replace('\u2014', '-')

        # Find PL references with optional title info
        pl_refs = re.findall(
            r'Pub\.\s*L\.\s*(\d+)[–-](\d+)\s*,?\s*\n?\s*'
            r'(?:(title\s+[IVX]+)\s*,?\s*)?',
            normalized, re.IGNORECASE
        )

        for pl_major, pl_minor, title_ref in pl_refs:
            pl_base = f'{pl_major}-{pl_minor}'
            matching_acts = pl_acts.get(pl_base, [])

            matched_act = None
            if len(matching_acts) == 1:
                matched_act = matching_acts[0]
            elif len(matching_acts) > 1 and title_ref:
                # Normalize: "title II" -> "Title II" (preserve Roman numerals)
                title_norm = 'Title ' + title_ref.strip().split()[-1].upper()
                for a in matching_acts:
                    if title_norm.lower() in a['pl_num'].lower():
                        matched_act = a
                        break
            if not matched_act and matching_acts:
                matched_act = matching_acts[0]  # fallback

            if matched_act:
                result.setdefault(matched_act['name'], set()).add(sec)

    return result


def main():
    acts = load_acts()
    print(f"Loaded {len(acts)} acts")

    # Build act -> sections map with title-level disambiguation
    act_sections_map = build_act_sections_map(acts)

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

        pl_base = pl.split(',')[0].strip()

        # Get sections assigned to this act from the source-credit map
        assigned_sections = act_sections_map.get(act['name'], set())

        # Find all sections that have a version for this PL.
        # Each version's text is the text BEFORE that amendment was applied
        # (since versions are built by reverse-applying amendments).
        # For act-snapshots we need the text AFTER the amendment, which is
        # the next version's text in the list.
        found_sections = []
        for sec, data in section_versions.items():
            # Only process sections assigned to this act
            if assigned_sections and sec not in assigned_sections:
                continue

            versions = data.get('versions', [])
            for i, version in enumerate(versions):
                v_pl = version.get('public_law', '').split(',')[0].strip()
                if v_pl == pl_base:
                    # Use the NEXT version's text (= post-amendment text)
                    if i + 1 < len(versions):
                        # Only include if the text actually changed
                        # (skip failed auto-reversals that produced identical text)
                        if version['text'] != versions[i + 1]['text']:
                            found_sections.append((sec, versions[i + 1]))
                        else:
                            # Check if a manually-fixed act-snapshot file exists
                            # and preserve it (it may have been corrected independently)
                            manual_path = os.path.join(act_dir, f'{sec}.md')
                            if os.path.exists(manual_path):
                                # Keep the existing file by not cleaning it
                                found_sections.append((sec, {'text': None, '_keep_existing': True}))
                    break

        if not found_sections:
            continue

        # Clean out old files before writing new ones, but preserve manually-fixed files
        keep_files = set()
        for sec, version in found_sections:
            if version.get('_keep_existing'):
                keep_files.add(f'{sec}.md')

        if os.path.isdir(act_dir):
            for old_file in os.listdir(act_dir):
                if old_file.endswith('.md') and old_file not in keep_files:
                    os.remove(os.path.join(act_dir, old_file))
        os.makedirs(act_dir, exist_ok=True)
        acts_with_snapshots += 1

        for sec, version in found_sections:
            if version.get('_keep_existing'):
                sections_written += 1
                continue
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
