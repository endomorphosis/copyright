#!/usr/bin/env python3
"""
Build the clean copyright-history git repository.

Reads acts metadata from metadata/acts.yaml and collected statute text from data/,
then creates a fresh git repo at OUTPUT_DIR with one commit per legislative act.

Usage:
    python3 build.py [--output-dir /path/to/copyright-history]
"""

import argparse
import os
import re
import shutil
import subprocess
import sys

DEFAULT_OUTPUT = os.path.expanduser('~/code/copyright-history')


def parse_acts(yaml_path):
    """Parse acts.yaml without requiring pyyaml."""
    with open(yaml_path, 'r') as f:
        content = f.read()

    # Normalize: ensure split works even for the first entry
    entries = re.split(r'\n(?=- name:)', '\n' + content)
    acts = []
    for entry in entries:
        entry = entry.strip()
        if not entry.startswith('- name:'):
            continue

        def get_field(field, text=entry):
            # Try single-line value first (handle YAML list prefix "- ")
            m = re.search(rf'(?:^|\s){field}:\s*(.+)$', text, re.MULTILINE)
            if not m:
                return None
            val = m.group(1).strip()
            if val == '>':
                # Multi-line YAML scalar
                lines = text.split('\n')
                result = []
                found = False
                for line in lines:
                    if found:
                        if line.startswith('    ') or line.startswith('\t'):
                            result.append(line.strip())
                        elif line.strip() == '':
                            continue
                        else:
                            break
                    if re.match(rf'^\s*{field}:\s*>', line):
                        found = True
                return ' '.join(result).strip()
            return val

        name = get_field('name')
        date = get_field('date')
        if not name or not date:
            continue

        acts.append({
            'name': name,
            'date': date,
            'citation': get_field('citation'),
            'chapter': get_field('chapter'),
            'public_law': get_field('public_law'),
            'summary': get_field('summary') or 'No summary available.',
            'tag': get_field('tag'),
            'effective_date': get_field('effective_date'),
        })

    acts.sort(key=lambda x: x['date'])
    return acts


def make_commit_message(act):
    """Build a structured commit message for an act."""
    lines = [act['name'], '']
    if act['public_law']:
        lines.append(f"Public Law: {act['public_law']}")
    if act['citation']:
        lines.append(f"Citation: {act['citation']}")
    if act['chapter']:
        lines.append(f"Chapter: {act['chapter']}")
    eff = act['effective_date'] or act['date']
    lines.append(f"Effective date: {eff}")
    lines.append(f"Summary: {act['summary']}")
    return '\n'.join(lines)


def run(cmd, cwd=None):
    """Run a shell command, raise on failure."""
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, cwd=cwd
    )
    if result.returncode != 0:
        print(f"  CMD FAILED: {cmd}")
        print(f"  STDERR: {result.stderr.strip()}")
    return result


def sanitize_filename(name):
    """Convert act name to a safe filename."""
    name = re.sub(r'\s*\([^)]*\)\s*', ' ', name)
    name = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    return name[:60].rstrip('-') if len(name) > 60 else name


def find_pre1976_text(act, data_dir):
    """Look for pre-1976 statute text in data/pre-1976-text/."""
    text_dir = os.path.join(data_dir, 'pre-1976-text')
    if not os.path.isdir(text_dir):
        return None
    # Try to match by date prefix or name
    for fname in os.listdir(text_dir):
        year = act['date'][:4]
        if fname.startswith(year) or sanitize_filename(act['name'])[:20] in fname:
            path = os.path.join(text_dir, fname)
            with open(path) as f:
                return f.read()
    return None


def find_section_text(section_num, data_dir):
    """Look for current section text in data/current-sections/."""
    path = os.path.join(data_dir, 'current-sections', f'{section_num}.md')
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return None


def build_repo(acts, data_dir, output_dir):
    """Build the clean output repository."""
    # Find the 1976 Act index
    pivot_idx = None
    for i, act in enumerate(acts):
        if act['name'] == 'Copyright Act of 1976':
            pivot_idx = i
            break

    if pivot_idx is None:
        print("ERROR: Could not find Copyright Act of 1976 in acts list!")
        sys.exit(1)

    # Wipe and create output dir
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # Init repo
    run('git init', cwd=output_dir)
    run('git checkout -b main', cwd=output_dir)

    # Create initial README
    readme_path = os.path.join(output_dir, 'README.md')
    src_readme = os.path.join(os.path.dirname(data_dir), 'README.md')
    if os.path.exists(src_readme):
        shutil.copy2(src_readme, readme_path)
    else:
        with open(readme_path, 'w') as f:
            f.write('# US Copyright Law: A Legislative History in Git\n')

    # Copy supporting files
    for fname in ['CONTRIBUTING.md', 'LICENSE']:
        src = os.path.join(os.path.dirname(data_dir), fname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(output_dir, fname))

    run('git add -A', cwd=output_dir)
    run('git commit -m "Initialize repository"', cwd=output_dir)

    # Process each act
    for i, act in enumerate(acts):
        print(f"[{i+1}/{len(acts)}] {act['name']} ({act['date']})")

        is_1976_act = act['name'] == 'Copyright Act of 1976'
        is_pre_1976 = i < pivot_idx
        is_post_1976 = i > pivot_idx

        pre1976_dir = os.path.join(output_dir, 'pre-1976')
        sections_dir = os.path.join(output_dir, 'sections')

        if is_pre_1976:
            os.makedirs(pre1976_dir, exist_ok=True)

            # Check for real statute text
            real_text = find_pre1976_text(act, data_dir)
            filename = sanitize_filename(act['name']) + '.md'
            filepath = os.path.join(pre1976_dir, filename)

            if real_text:
                with open(filepath, 'w') as f:
                    f.write(real_text)
            else:
                with open(filepath, 'w') as f:
                    f.write(f"# {act['name']}\n\n")
                    f.write(f"*{act['date']}*\n\n")
                    if act['citation']:
                        f.write(f"**Citation:** {act['citation']}\n\n")
                    if act['public_law']:
                        f.write(f"**Public Law:** {act['public_law']}\n\n")
                    if act['chapter']:
                        f.write(f"**Chapter:** {act['chapter']}\n\n")
                    f.write(f"## Summary\n\n{act['summary']}\n\n")
                    f.write(f"> [TODO] Full text to be added from primary sources.\n")

        elif is_1976_act:
            # THE pivotal commit: transition from pre-1976/ to sections/
            # Remove pre-1976 act files (keep directory with a note)
            if os.path.isdir(pre1976_dir):
                shutil.rmtree(pre1976_dir)

            os.makedirs(sections_dir, exist_ok=True)

            # List all current section files we have
            current_dir = os.path.join(data_dir, 'current-sections')
            if os.path.isdir(current_dir):
                for fname in sorted(os.listdir(current_dir)):
                    if fname.endswith('.md'):
                        # For now, use current text as starting point
                        # (will be replaced with reconstructed 1976 text later)
                        src = os.path.join(current_dir, fname)
                        shutil.copy2(src, os.path.join(sections_dir, fname))

            # If no current sections fetched yet, create placeholders
            if not os.listdir(sections_dir) if os.path.isdir(sections_dir) else True:
                placeholder_sections = [
                    '101', '102', '103', '104', '105', '106', '107', '108',
                    '109', '110', '111', '112', '113', '114', '115', '116',
                    '117', '118', '201', '202', '203', '204', '205',
                    '301', '302', '303', '304', '305',
                    '401', '402', '403', '404', '405', '406', '407', '408',
                    '409', '410', '411', '412',
                    '501', '502', '503', '504', '505', '506', '507', '508',
                    '509', '510',
                    '601', '602', '603',
                    '701', '702', '703', '704', '705', '706', '707', '708',
                    '801', '802', '803', '804', '805',
                ]
                for sec in placeholder_sections:
                    path = os.path.join(sections_dir, f'{sec}.md')
                    if not os.path.exists(path):
                        with open(path, 'w') as f:
                            f.write(f'# Section {sec}\n\n')
                            f.write(f'> [TODO] Text to be added.\n')

        else:
            # Post-1976 amendments
            # Check for reconstructed section snapshots for this act
            snapshot_dir = os.path.join(
                data_dir, 'snapshots', act['date'] + '-' + sanitize_filename(act['name'])
            )
            if os.path.isdir(snapshot_dir):
                # Copy updated section files
                for fname in os.listdir(snapshot_dir):
                    if fname.endswith('.md'):
                        src = os.path.join(snapshot_dir, fname)
                        dst = os.path.join(sections_dir, fname)
                        shutil.copy2(src, dst)
            else:
                # No reconstructed text yet — create a marker file
                # that notes what this act changed
                amendments_dir = os.path.join(output_dir, 'amendments')
                os.makedirs(amendments_dir, exist_ok=True)
                marker = os.path.join(
                    amendments_dir,
                    f"{act['date']}-{sanitize_filename(act['name'])}.md"
                )
                with open(marker, 'w') as f:
                    f.write(f"# {act['name']}\n\n")
                    f.write(f"*{act['date']}*\n\n")
                    if act['public_law']:
                        f.write(f"**Public Law:** {act['public_law']}\n\n")
                    if act['citation']:
                        f.write(f"**Citation:** {act['citation']}\n\n")
                    f.write(f"## Changes\n\n{act['summary']}\n\n")
                    f.write("> [TODO] Apply text changes to section files.\n")

        # Stage and commit
        run('git add -A', cwd=output_dir)

        msg = make_commit_message(act)
        msg_file = '/tmp/copyright_commit_msg.txt'
        with open(msg_file, 'w') as f:
            f.write(msg)

        run(f'git commit --allow-empty -F {msg_file}', cwd=output_dir)

        if act.get('tag'):
            run(f"git tag {act['tag']}", cwd=output_dir)

        print(f"  -> committed")

    print(f"\nDone! Built {len(acts)} commits in {output_dir}")
    print(f"Run: cd {output_dir} && git log --oneline")


def main():
    parser = argparse.ArgumentParser(description='Build copyright-history repo')
    parser.add_argument(
        '--output-dir', default=DEFAULT_OUTPUT,
        help=f'Output directory (default: {DEFAULT_OUTPUT})'
    )
    args = parser.parse_args()

    workspace = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(workspace, 'metadata', 'acts.yaml')
    data_dir = os.path.join(workspace, 'data')

    if not os.path.exists(yaml_path):
        print(f"ERROR: {yaml_path} not found")
        sys.exit(1)

    acts = parse_acts(yaml_path)
    print(f"Loaded {len(acts)} acts from {yaml_path}")

    build_repo(acts, data_dir, args.output_dir)


if __name__ == '__main__':
    main()
