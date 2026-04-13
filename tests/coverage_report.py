#!/usr/bin/env python3
"""
Test coverage report for the copyright legislative history project.

This is NOT code coverage -- it's STATUTE coverage. It answers:
  - Which sections of Title 17 have legal accuracy tests?
  - Which version snapshots are verified by tests?
  - Which act-snapshots have been tested?
  - What's the overall quality confidence level?

Usage:
    python3 tests/coverage_report.py
    python3 tests/coverage_report.py --json          # machine-readable output
    python3 tests/coverage_report.py --sections      # list untested sections
"""

import argparse
import ast
import json
import os
import re
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
TESTS_DIR = os.path.join(PROJECT_ROOT, 'tests')
SNAPSHOTS_DIR = os.path.join(DATA_DIR, 'snapshots')


def all_snapshot_sections():
    sections = []
    for fname in os.listdir(SNAPSHOTS_DIR):
        if fname.endswith('-versions.json'):
            sections.append(fname.replace('-versions.json', ''))
    return sorted(sections)


def count_versions():
    """Count total versions across all snapshot files."""
    total = 0
    per_section = {}
    for sec in all_snapshot_sections():
        path = os.path.join(SNAPSHOTS_DIR, f'{sec}-versions.json')
        with open(path) as f:
            data = json.load(f)
        n = len(data['versions'])
        total += n
        per_section[sec] = n
    return total, per_section


def extract_tested_sections(test_file):
    """Extract section numbers referenced in test file class/method names
    and assertion strings."""
    sections = set()
    with open(test_file) as f:
        content = f.read()

    # From class names like TestSection102, TestSection1201
    for m in re.finditer(r'TestSection(\d+[A-Z]?)', content):
        sections.add(m.group(1))

    # From get_v0_text('102') and load_versions('102') calls
    for m in re.finditer(r"(?:get_v0_text|load_versions|get_current_text)\s*\(\s*['\"](\d+[A-Z]?)['\"]", content):
        sections.add(m.group(1))

    # From ALL_AUDIT_SECTIONS lists
    for m in re.finditer(r"'(\d+[A-Z]?)'", content):
        sec = m.group(1)
        if sec.isdigit() and 100 <= int(sec) <= 2000:
            sections.add(sec)

    return sections


def count_test_methods(test_file):
    """Count test methods in a test file."""
    count = 0
    with open(test_file) as f:
        for line in f:
            stripped = line.strip()
            if stripped.startswith('def test_'):
                count += 1
    return count


def find_test_files():
    """Find all test files."""
    files = []
    for fname in sorted(os.listdir(TESTS_DIR)):
        if fname.startswith('test_') and fname.endswith('.py'):
            files.append(os.path.join(TESTS_DIR, fname))
    return files


def analyze_snapshot_quality():
    """Analyze quality of snapshot data."""
    issues = []
    stats = {
        'total_sections': 0,
        'sections_with_issues': 0,
        'total_versions': 0,
        'auto_reversed': 0,
        'manually_fixed': 0,
        'empty_text': 0,
    }
    for sec in all_snapshot_sections():
        path = os.path.join(SNAPSHOTS_DIR, f'{sec}-versions.json')
        with open(path) as f:
            data = json.load(f)

        stats['total_sections'] += 1
        versions = data['versions']
        stats['total_versions'] += len(versions)

        if data.get('issues'):
            stats['sections_with_issues'] += 1
            for issue in data['issues']:
                issues.append(f"  {sec}: {issue.get('issue', '?')[:60]}")

        for v in versions:
            if v.get('auto_reversed'):
                stats['auto_reversed'] += 1
            if v.get('manually_reconstructed'):
                stats['manually_fixed'] += 1
            if not v.get('text', '').strip():
                stats['empty_text'] += 1

    return stats, issues


def main():
    parser = argparse.ArgumentParser(
        description='Statute test coverage report')
    parser.add_argument('--json', action='store_true',
                        help='Output in JSON format')
    parser.add_argument('--sections', action='store_true',
                        help='List untested sections')
    args = parser.parse_args()

    # Gather data
    all_sections = set(all_snapshot_sections())
    total_versions, versions_per_section = count_versions()
    test_files = find_test_files()

    tested_sections = set()
    test_method_counts = {}
    total_tests = 0

    for tf in test_files:
        name = os.path.basename(tf)
        sections = extract_tested_sections(tf)
        tested_sections |= sections
        count = count_test_methods(tf)
        test_method_counts[name] = count
        total_tests += count

    untested = sorted(all_sections - tested_sections,
                      key=lambda s: (len(s), s))
    tested_in_snapshots = tested_sections & all_sections

    snapshot_stats, snapshot_issues = analyze_snapshot_quality()

    # Coverage metrics
    section_coverage = len(tested_in_snapshots) / len(all_sections) * 100
    version_coverage_sections = len(tested_in_snapshots)

    # Build result
    result = {
        'summary': {
            'total_test_methods': total_tests,
            'total_snapshot_sections': len(all_sections),
            'tested_sections': len(tested_in_snapshots),
            'untested_sections': len(untested),
            'section_coverage_pct': round(section_coverage, 1),
            'total_versions': total_versions,
        },
        'test_files': test_method_counts,
        'snapshot_quality': snapshot_stats,
        'untested_sections': untested,
    }

    if args.json:
        print(json.dumps(result, indent=2))
        return

    # Human-readable output
    print("=" * 70)
    print("  COPYRIGHT PROJECT: STATUTE TEST COVERAGE REPORT")
    print("=" * 70)
    print()

    print("TEST SUITE SUMMARY")
    print("-" * 40)
    for fname, count in sorted(test_method_counts.items()):
        print(f"  {fname:40s} {count:4d} tests")
    print(f"  {'TOTAL':40s} {total_tests:4d} tests")
    print()

    print("SECTION COVERAGE")
    print("-" * 40)
    print(f"  Total sections with snapshots:  {len(all_sections):4d}")
    print(f"  Sections with test coverage:    {len(tested_in_snapshots):4d}")
    print(f"  Sections without tests:         {len(untested):4d}")
    print(f"  Section coverage:               {section_coverage:5.1f}%")
    print()

    print("VERSION CHAIN QUALITY")
    print("-" * 40)
    print(f"  Total versions across all sections:  {snapshot_stats['total_versions']:4d}")
    print(f"  Successfully auto-reversed:          {snapshot_stats['auto_reversed']:4d}")
    print(f"  Manually reconstructed:              {snapshot_stats['manually_fixed']:4d}")
    print(f"  Empty text (data issues):            {snapshot_stats['empty_text']:4d}")
    print(f"  Sections with open issues:           {snapshot_stats['sections_with_issues']:4d}")
    print()

    if args.sections or untested:
        print("UNTESTED SECTIONS")
        print("-" * 40)
        if untested:
            # Group by chapter
            chapters = {}
            for sec in untested:
                sec_num = int(re.match(r'\d+', sec).group())
                if sec_num < 200:
                    ch = 'Ch.1 (101-122)'
                elif sec_num < 300:
                    ch = 'Ch.2 (201-205)'
                elif sec_num < 400:
                    ch = 'Ch.3 (301-305)'
                elif sec_num < 500:
                    ch = 'Ch.4 (401-412)'
                elif sec_num < 600:
                    ch = 'Ch.5 (501-513)'
                elif sec_num < 700:
                    ch = 'Ch.6 (601-603)'
                elif sec_num < 800:
                    ch = 'Ch.7 (701-710)'
                elif sec_num < 900:
                    ch = 'Ch.8 (801-805)'
                elif sec_num < 1000:
                    ch = 'Ch.9 (901-914)'
                elif sec_num < 1100:
                    ch = 'Ch.10 (1001-1010)'
                elif sec_num < 1200:
                    ch = 'Ch.11 (1101)'
                elif sec_num < 1300:
                    ch = 'Ch.12 (1201-1205)'
                elif sec_num < 1400:
                    ch = 'Ch.13 (1301-1332)'
                else:
                    ch = f'Ch.14+ ({sec_num}+)'
                chapters.setdefault(ch, []).append(sec)

            for ch, secs in sorted(chapters.items()):
                print(f"  {ch}: {', '.join(secs)}")
        else:
            print("  All sections have test coverage!")
        print()

    if snapshot_stats['sections_with_issues'] > 0:
        print("OPEN SNAPSHOT ISSUES")
        print("-" * 40)
        for issue in snapshot_issues[:10]:
            print(issue)
        if len(snapshot_issues) > 10:
            print(f"  ... and {len(snapshot_issues) - 10} more")
        print()

    # Confidence assessment
    print("CONFIDENCE ASSESSMENT")
    print("-" * 40)
    if section_coverage >= 80:
        level = "HIGH"
        msg = "Most sections have dedicated legal accuracy tests."
    elif section_coverage >= 50:
        level = "MODERATE"
        msg = "Many sections tested, but gaps remain in less-common chapters."
    else:
        level = "LOW"
        msg = "Significant gaps in test coverage. Priority: add tests for core sections."
    print(f"  Coverage level: {level}")
    print(f"  {msg}")

    if snapshot_stats['empty_text'] > 0:
        print(f"  WARNING: {snapshot_stats['empty_text']} version(s) have empty text")
    print()
    print("=" * 70)


if __name__ == '__main__':
    main()
