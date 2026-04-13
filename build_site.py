#!/usr/bin/env python3
"""
Build the static website from the copyright-history git repository.

Walks the git history and extracts all data into JSON files that the
frontend can load on demand. No external dependencies required.

Usage:
    python3 build_site.py [--history-repo ~/code/copyright-history] [--output docs/]
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

# Reuse parse_acts from build.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build import parse_acts

DEFAULT_HISTORY_REPO = os.path.expanduser('~/code/copyright-history')
DEFAULT_OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs')


def git(*args, repo):
    """Run a git command in the given repo, return stdout."""
    result = subprocess.run(
        ['git', '-C', repo] + list(args),
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def get_all_commits(repo):
    """Get all commits in order (oldest first)."""
    log = git('log', '--reverse', '--format=%H\t%s', repo=repo)
    if not log:
        return []
    commits = []
    for line in log.splitlines():
        parts = line.split('\t', 1)
        if len(parts) == 2:
            commits.append({'hash': parts[0], 'subject': parts[1]})
    return commits


def get_commit_details(hash_, repo):
    """Get full commit message details."""
    body = git('log', '-1', '--format=%b', hash_, repo=repo) or ''
    return body


def get_changed_files(hash_, repo):
    """Get list of files changed in a commit."""
    output = git('diff-tree', '--no-commit-id', '-r', '--name-only', hash_, repo=repo)
    if not output:
        return []
    return [f for f in output.splitlines() if f.strip()]


def get_file_at_commit(hash_, path, repo):
    """Get file contents at a specific commit."""
    return git('show', f'{hash_}:{path}', repo=repo)


def get_diff_for_commit(hash_, repo):
    """Get the unified diff for a commit."""
    return git('diff', f'{hash_}~1', hash_, repo=repo) or ''


def get_tags(repo):
    """Get all tags mapped to their commit hashes."""
    output = git('tag', '-l', repo=repo)
    if not output:
        return {}
    tags = {}
    for tag in output.splitlines():
        tag = tag.strip()
        if tag:
            hash_ = git('rev-list', '-1', tag, repo=repo)
            if hash_:
                tags[hash_] = tag
    return tags


def parse_commit_metadata(subject, body):
    """Extract structured metadata from commit message."""
    meta = {'name': subject}
    for line in body.splitlines():
        line = line.strip()
        if line.startswith('Public Law:'):
            meta['public_law'] = line.split(':', 1)[1].strip()
        elif line.startswith('Citation:'):
            meta['citation'] = line.split(':', 1)[1].strip()
        elif line.startswith('Chapter:'):
            meta['chapter'] = line.split(':', 1)[1].strip()
        elif line.startswith('Effective date:'):
            meta['effective_date'] = line.split(':', 1)[1].strip()
        elif line.startswith('Summary:'):
            meta['summary'] = line.split(':', 1)[1].strip()
    return meta


def extract_section_title(text):
    """Extract the section title from markdown content."""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith('\u00a7') or line.startswith('§'):
            # Line like: §107. Limitations on exclusive rights: Fair use
            m = re.match(r'§\d+[A-Za-z]?\.\s*(.*)', line)
            if m:
                return m.group(1).strip()
            return line
        if line.startswith('#') and '§' in line:
            continue  # Skip header lines like "# 17 U.S.C. § 107"
    return None


def parse_unified_diff(diff_text):
    """Parse unified diff into structured data for JSON."""
    if not diff_text:
        return []

    files = []
    current_file = None
    current_hunks = []
    current_hunk_lines = []

    for line in diff_text.splitlines():
        if line.startswith('diff --git'):
            # Save previous file
            if current_file and current_hunks:
                if current_hunk_lines:
                    current_hunks[-1]['lines'] = current_hunk_lines
                files.append({'path': current_file, 'hunks': current_hunks})
            # Parse new file path
            m = re.search(r'b/(.+)$', line)
            current_file = m.group(1) if m else None
            current_hunks = []
            current_hunk_lines = []
        elif line.startswith('@@'):
            # Save previous hunk
            if current_hunk_lines and current_hunks:
                current_hunks[-1]['lines'] = current_hunk_lines
            current_hunk_lines = []
            m = re.match(r'@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@', line)
            if m:
                current_hunks.append({
                    'old_start': int(m.group(1)),
                    'new_start': int(m.group(3)),
                    'lines': [],
                })
        elif line.startswith('---') or line.startswith('+++') or line.startswith('index '):
            continue
        elif current_hunks:
            if line.startswith('+'):
                current_hunk_lines.append({'type': 'add', 'text': line[1:]})
            elif line.startswith('-'):
                current_hunk_lines.append({'type': 'del', 'text': line[1:]})
            else:
                current_hunk_lines.append({'type': 'ctx', 'text': line[1:] if line.startswith(' ') else line})

    # Save last file/hunk
    if current_hunk_lines and current_hunks:
        current_hunks[-1]['lines'] = current_hunk_lines
    if current_file and current_hunks:
        files.append({'path': current_file, 'hunks': current_hunks})

    return files


def build_pl_sections_map(data_dir):
    """Build a map of PL number -> list of sections it amends."""
    map_file = os.path.join(data_dir, 'section-amendment-map.txt')
    if not os.path.exists(map_file):
        return {}
    pl_sections = {}
    with open(map_file) as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 3:
                sec, _date, pl = parts[0], parts[1], parts[2].strip()
                pl_sections.setdefault(pl, []).append(sec)
    return pl_sections


def build_acts_json(commits, tags, acts_metadata, repo, data_dir=None):
    """Build the main acts.json index."""
    # Map act names to metadata from acts.yaml
    meta_by_name = {}
    for act in acts_metadata:
        meta_by_name[act['name']] = act

    # Map PL -> sections from amendment map
    pl_sections = build_pl_sections_map(data_dir) if data_dir else {}

    acts = []
    for commit in commits:
        hash_ = commit['hash']
        subject = commit['subject']
        body = get_commit_details(hash_, repo)
        meta = parse_commit_metadata(subject, body)

        # Get changed files
        changed = get_changed_files(hash_, repo)
        sections_affected = []
        files_changed = []
        for f in changed:
            if f.startswith('sections/') and f.endswith('.md'):
                sec_num = f.replace('sections/', '').replace('.md', '')
                sections_affected.append(sec_num)
            files_changed.append(f)

        # Determine era
        is_pre_1976 = any(f.startswith('pre-1976/') for f in changed)
        era = 'pre-1976' if is_pre_1976 else 'post-1976'

        # Try to get date from acts.yaml metadata (more accurate for pre-1970)
        yaml_meta = meta_by_name.get(subject, {})
        date = yaml_meta.get('effective_date') or yaml_meta.get('date') or meta.get('effective_date', '')

        # Look up expected sections from the amendment map (by PL number)
        # Try full PL string first (e.g. "105-298, Title II") for multi-title
        # PLs, then fall back to base PL number (e.g. "105-298")
        pl_raw = meta.get('public_law', yaml_meta.get('public_law', '')) or ''
        pl_full = re.sub(r'Pub\. L\. ', '', pl_raw).strip()
        pl_base = pl_full.split(',')[0].strip()
        sections_expected = sorted(
            pl_sections.get(pl_full, pl_sections.get(pl_base, []))
        )

        has_diff = len(files_changed) > 0

        act_entry = {
            'hash': hash_[:7],
            'full_hash': hash_,
            'date': date,
            'name': subject,
            'public_law': pl_raw,
            'citation': meta.get('citation', yaml_meta.get('citation', '')),
            'summary': meta.get('summary', yaml_meta.get('summary', '')),
            'tag': tags.get(hash_, ''),
            'era': era,
            'sections_affected': sorted(sections_affected),
            'sections_expected': sections_expected,
            'has_diff': has_diff,
            'files_changed': files_changed,
        }
        acts.append(act_entry)

    return acts


def build_sections_data(commits, repo):
    """Build per-section version data and the sections index."""
    # First, find all section files in HEAD
    tree = git('ls-tree', '--name-only', '-r', 'HEAD', repo=repo)
    section_files = []
    if tree:
        for f in tree.splitlines():
            if f.startswith('sections/') and f.endswith('.md'):
                section_files.append(f)

    sections_index = {}
    sections_data = {}

    for sec_path in sorted(section_files):
        sec_num = sec_path.replace('sections/', '').replace('.md', '')

        # Get all commits that touched this file
        log = git('log', '--reverse', '--format=%H\t%s', '--', sec_path, repo=repo)
        if not log:
            continue

        versions = []
        for line in log.splitlines():
            parts = line.split('\t', 1)
            if len(parts) != 2:
                continue
            hash_, subject = parts

            text = get_file_at_commit(hash_, sec_path, repo)
            if text is None:
                continue

            versions.append({
                'act_hash': hash_[:7],
                'act_name': subject,
                'text': text,
            })

        if not versions:
            continue

        # Get current text
        current_text = get_file_at_commit('HEAD', sec_path, repo) or ''
        title = extract_section_title(current_text) or f'Section {sec_num}'

        sections_data[sec_num] = {
            'section': sec_num,
            'title': title,
            'current_text': current_text,
            'versions': versions,
        }

        sections_index[sec_num] = {
            'title': title,
            'amendment_count': len(versions),
            'first_version': versions[0]['act_name'] if versions else '',
            'last_amended': versions[-1]['act_name'] if versions else '',
        }

    return sections_index, sections_data


def build_pre1976_data(commits, repo):
    """Build data for pre-1976 act files."""
    # Find all pre-1976 files at the commit just before the 1976 Act
    # (they get deleted at the 1976 Act commit)
    pre1976_data = {}

    for commit in commits:
        changed = get_changed_files(commit['hash'], repo)
        for f in changed:
            if f.startswith('pre-1976/') and f.endswith('.md'):
                slug = f.replace('pre-1976/', '').replace('.md', '')
                text = get_file_at_commit(commit['hash'], f, repo)
                if text:
                    pre1976_data[slug] = {
                        'slug': slug,
                        'act_hash': commit['hash'][:7],
                        'act_name': commit['subject'],
                        'text': text,
                    }

    return pre1976_data


def build_diffs_data(commits, repo):
    """Build per-commit diff data."""
    diffs = {}
    for i, commit in enumerate(commits):
        hash_ = commit['hash']
        if i == 0:
            # First commit: diff against empty tree
            diff_text = git('diff', '--no-index', '/dev/null', '.', repo=repo)
            # Actually, use show for the first commit
            diff_text = git('diff-tree', '-p', '--root', hash_, repo=repo) or ''
        else:
            diff_text = get_diff_for_commit(hash_, repo)

        parsed = parse_unified_diff(diff_text)
        diffs[hash_[:7]] = {
            'hash': hash_[:7],
            'act_name': commit['subject'],
            'files': parsed,
        }

    return diffs


def main():
    parser = argparse.ArgumentParser(description='Build copyright history static site')
    parser.add_argument(
        '--history-repo', default=DEFAULT_HISTORY_REPO,
        help=f'Path to the copyright-history git repo (default: {DEFAULT_HISTORY_REPO})',
    )
    parser.add_argument(
        '--output', default=DEFAULT_OUTPUT,
        help=f'Output directory for the site (default: {DEFAULT_OUTPUT})',
    )
    args = parser.parse_args()

    repo = args.history_repo
    output = args.output

    if not os.path.isdir(os.path.join(repo, '.git')):
        print(f"ERROR: {repo} is not a git repository")
        sys.exit(1)

    # Load acts metadata from workspace
    workspace = os.path.dirname(os.path.abspath(__file__))
    yaml_path = os.path.join(workspace, 'metadata', 'acts.yaml')
    acts_metadata = []
    if os.path.exists(yaml_path):
        acts_metadata = parse_acts(yaml_path)
        print(f"Loaded {len(acts_metadata)} acts from acts.yaml")

    # Get git data
    print("Reading git history...")
    commits = get_all_commits(repo)
    print(f"  {len(commits)} commits")
    tags = get_tags(repo)
    print(f"  {len(tags)} tags")

    # Build data directory
    data_dir = os.path.join(output, 'data')
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(os.path.join(data_dir, 'sections'), exist_ok=True)
    os.makedirs(os.path.join(data_dir, 'diffs'), exist_ok=True)
    os.makedirs(os.path.join(data_dir, 'pre1976'), exist_ok=True)

    # Build acts.json
    print("Building acts.json...")
    src_data_dir = os.path.join(workspace, 'data')
    acts = build_acts_json(commits, tags, acts_metadata, repo, src_data_dir)
    with open(os.path.join(data_dir, 'acts.json'), 'w') as f:
        json.dump(acts, f, indent=1)
    print(f"  {len(acts)} acts")

    # Build sections data
    print("Building section data...")
    sections_index, sections_data = build_sections_data(commits, repo)
    with open(os.path.join(data_dir, 'sections_index.json'), 'w') as f:
        json.dump(sections_index, f, indent=1)
    for sec_num, data in sections_data.items():
        with open(os.path.join(data_dir, 'sections', f'{sec_num}.json'), 'w') as f:
            json.dump(data, f, indent=1)
    print(f"  {len(sections_data)} sections")

    # Build pre-1976 data
    print("Building pre-1976 data...")
    pre1976 = build_pre1976_data(commits, repo)
    for slug, data in pre1976.items():
        with open(os.path.join(data_dir, 'pre1976', f'{slug}.json'), 'w') as f:
            json.dump(data, f, indent=1)
    print(f"  {len(pre1976)} pre-1976 files")

    # Build diffs data
    print("Building diff data...")
    diffs = build_diffs_data(commits, repo)
    for hash_, data in diffs.items():
        with open(os.path.join(data_dir, 'diffs', f'{hash_}.json'), 'w') as f:
            json.dump(data, f, indent=1)
    print(f"  {len(diffs)} diffs")

    # Copy static site files
    site_src = os.path.join(workspace, 'site-src')
    if os.path.isdir(site_src):
        print("Copying frontend files...")
        for item in os.listdir(site_src):
            src = os.path.join(site_src, item)
            dst = os.path.join(output, item)
            if os.path.isdir(src):
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)

    # Write .nojekyll for GitHub Pages
    with open(os.path.join(output, '.nojekyll'), 'w') as f:
        pass

    print(f"\nDone! Site built at {output}")
    print(f"Serve with: python3 -m http.server -d {output}")


if __name__ == '__main__':
    main()
