#!/usr/bin/env python3
"""
Data integrity tests for all files in the copyright project.

Verifies that every data file (snapshots, current-sections, amendment-notes,
act-snapshots, pre-1976 text, acts.yaml) is structurally valid and internally
consistent. These tests catch corruption, missing fields, truncated files,
and format violations that would produce a broken output repo.

Usage:
    python3 -m unittest tests/test_data_integrity.py -v
"""

import json
import os
import re
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
SNAPSHOTS_DIR = os.path.join(DATA_DIR, 'snapshots')
CURRENT_DIR = os.path.join(DATA_DIR, 'current-sections')
NOTES_DIR = os.path.join(DATA_DIR, 'amendment-notes')
ACT_SNAPSHOTS_DIR = os.path.join(DATA_DIR, 'act-snapshots')
PRE1976_DIR = os.path.join(DATA_DIR, 'pre-1976-text')
METADATA_DIR = os.path.join(PROJECT_ROOT, 'metadata')


def all_snapshot_sections():
    sections = []
    for fname in os.listdir(SNAPSHOTS_DIR):
        if fname.endswith('-versions.json'):
            sections.append(fname.replace('-versions.json', ''))
    return sorted(sections)


def load_versions(sec_num):
    path = os.path.join(SNAPSHOTS_DIR, f'{sec_num}-versions.json')
    with open(path) as f:
        return json.load(f)


def parse_acts_yaml():
    with open(os.path.join(METADATA_DIR, 'acts.yaml')) as f:
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
        m_tag = re.search(r'tag:\s*(.+)', entry)
        m_summary = re.search(r'summary:\s*(.+)', entry)
        if m_name and m_date:
            acts.append({
                'name': m_name.group(1).strip(),
                'date': m_date.group(1).strip(),
                'public_law': m_pl.group(1).strip() if m_pl else None,
                'tag': m_tag.group(1).strip() if m_tag else None,
                'has_summary': m_summary is not None,
            })
    return acts


# ===========================================================================
# Snapshot JSON structural integrity
# ===========================================================================

class TestSnapshotFileValidity(unittest.TestCase):
    """Every snapshot JSON file must be valid JSON with required structure."""

    def test_all_snapshot_files_are_valid_json(self):
        """Every file in data/snapshots/ must parse as valid JSON."""
        for fname in os.listdir(SNAPSHOTS_DIR):
            if not fname.endswith('-versions.json'):
                continue
            path = os.path.join(SNAPSHOTS_DIR, fname)
            with self.subTest(file=fname):
                with open(path) as f:
                    try:
                        json.load(f)
                    except json.JSONDecodeError as e:
                        self.fail(f"{fname} is not valid JSON: {e}")

    def test_all_snapshots_have_section_field(self):
        """Every snapshot must have a 'section' field matching filename."""
        for sec in all_snapshot_sections():
            with self.subTest(section=sec):
                data = load_versions(sec)
                self.assertIn('section', data,
                              f"Section {sec} missing 'section' field")
                self.assertEqual(data['section'], sec,
                                 f"Section {sec}: 'section' field is "
                                 f"'{data['section']}', expected '{sec}'")

    def test_all_snapshots_have_versions_array(self):
        """Every snapshot must have a 'versions' array."""
        for sec in all_snapshot_sections():
            with self.subTest(section=sec):
                data = load_versions(sec)
                self.assertIn('versions', data)
                self.assertIsInstance(data['versions'], list)

    def test_all_snapshots_have_at_least_two_versions(self):
        """Every snapshot should have at least 2 versions (original + current)."""
        for sec in all_snapshot_sections():
            with self.subTest(section=sec):
                data = load_versions(sec)
                self.assertGreaterEqual(
                    len(data['versions']), 2,
                    f"Section {sec} has only {len(data['versions'])} version(s)")

    def test_all_snapshots_have_issues_array_if_reconstructed(self):
        """Snapshots produced by reconstruct.py should have an 'issues' array.
        Manually-created snapshots (e.g., §708) may omit it."""
        missing_issues = []
        for sec in all_snapshot_sections():
            data = load_versions(sec)
            if 'issues' not in data:
                missing_issues.append(sec)
        # Allow a small number of manually-created snapshots without issues
        self.assertLessEqual(
            len(missing_issues), 5,
            f"Too many snapshots missing 'issues': {missing_issues}")

    def test_snapshot_count_matches_expectations(self):
        """We should have snapshots for a substantial number of sections."""
        sections = all_snapshot_sections()
        self.assertGreaterEqual(len(sections), 85,
                                f"Expected 85+ snapshot files, got {len(sections)}")


class TestSnapshotVersionFields(unittest.TestCase):
    """Each version entry within a snapshot must have required fields."""

    def test_every_version_has_text_field(self):
        """Every version must have a 'text' field."""
        for sec in all_snapshot_sections():
            data = load_versions(sec)
            for i, v in enumerate(data['versions']):
                with self.subTest(section=sec, version=i):
                    self.assertIn('text', v,
                                  f"Section {sec} version {i} missing 'text'")

    def test_non_current_versions_have_year_or_date(self):
        """Every non-current version must have a 'year' or 'date' field.
        Sections with no amendments use 'date' instead of 'year'."""
        for sec in all_snapshot_sections():
            data = load_versions(sec)
            for i, v in enumerate(data['versions']):
                if v.get('act') == 'Current' or v.get('date') == 'current':
                    continue
                with self.subTest(section=sec, version=i):
                    has_year = 'year' in v
                    has_date = 'date' in v
                    self.assertTrue(
                        has_year or has_date,
                        f"Section {sec} version {i} missing both "
                        f"'year' and 'date'")
                    if has_year:
                        year = v['year']
                        # §304 has pre-1976 term extension acts (1962-1974)
                        min_year = 1960 if sec == '304' else 1976
                        self.assertTrue(
                            year.isdigit() and min_year <= int(year) <= 2026,
                            f"Section {sec} version {i}: year '{year}' "
                            f"out of range [{min_year}, 2026]")

    def test_non_current_versions_have_public_law(self):
        """Every non-current version should have a 'public_law' field."""
        for sec in all_snapshot_sections():
            data = load_versions(sec)
            for i, v in enumerate(data['versions']):
                if v.get('act') == 'Current' or v.get('date') == 'current':
                    continue
                with self.subTest(section=sec, version=i):
                    self.assertIn('public_law', v,
                                  f"Section {sec} version {i} missing "
                                  f"'public_law'")

    def test_public_law_format(self):
        """Public law numbers should match the pattern 'NNN-NNN'."""
        pl_pattern = re.compile(r'^\d+-\d+')
        for sec in all_snapshot_sections():
            data = load_versions(sec)
            for i, v in enumerate(data['versions']):
                pl = v.get('public_law')
                if not pl:
                    continue
                with self.subTest(section=sec, version=i):
                    self.assertTrue(
                        pl_pattern.match(pl),
                        f"Section {sec} version {i}: public_law '{pl}' "
                        f"doesn't match 'NNN-NNN' pattern")

    def test_last_version_is_current(self):
        """The last version in every snapshot must be 'Current'."""
        for sec in all_snapshot_sections():
            data = load_versions(sec)
            last = data['versions'][-1]
            with self.subTest(section=sec):
                is_current = (
                    last.get('act') == 'Current' or
                    last.get('date') == 'current'
                )
                self.assertTrue(is_current,
                                f"Section {sec}: last version is not Current")

    def test_first_version_is_oldest(self):
        """versions[0] should have the smallest year."""
        for sec in all_snapshot_sections():
            data = load_versions(sec)
            years = []
            for v in data['versions']:
                y = v.get('year')
                if y and y != 'current':
                    years.append(int(y))
            if len(years) < 2:
                continue
            with self.subTest(section=sec):
                self.assertEqual(years[0], min(years),
                                 f"Section {sec}: v0 year {years[0]} != "
                                 f"min {min(years)}")


class TestSnapshotTextQuality(unittest.TestCase):
    """The text content in snapshots must be non-trivial and well-formed."""

    # Known sections with empty text due to data issues (§1501, §1502
    # are repealed/reserved sections that have no substantive text)
    KNOWN_EMPTY_SECTIONS = {'1501', '1502'}

    def test_v0_text_minimum_length(self):
        """Version 0 text should be at least 50 characters (real statute text)."""
        for sec in all_snapshot_sections():
            if sec in self.KNOWN_EMPTY_SECTIONS:
                continue
            data = load_versions(sec)
            text = data['versions'][0].get('text', '')
            with self.subTest(section=sec):
                self.assertGreaterEqual(
                    len(text.strip()), 50,
                    f"Section {sec} v0 text is only {len(text.strip())} chars")

    def test_current_text_minimum_length(self):
        """Current version text should be at least 50 characters."""
        for sec in all_snapshot_sections():
            if sec in self.KNOWN_EMPTY_SECTIONS:
                continue
            data = load_versions(sec)
            text = data['versions'][-1].get('text', '')
            with self.subTest(section=sec):
                self.assertGreaterEqual(
                    len(text.strip()), 50,
                    f"Section {sec} current text is only "
                    f"{len(text.strip())} chars")

    def test_no_html_tags_in_text(self):
        """Statute text should not contain HTML tags (indicates bad conversion)."""
        html_pattern = re.compile(r'<(?:p|div|span|br|table|td|tr|li|ul|ol)\b',
                                  re.IGNORECASE)
        for sec in all_snapshot_sections():
            data = load_versions(sec)
            for i, v in enumerate(data['versions']):
                text = v.get('text', '')
                with self.subTest(section=sec, version=i):
                    self.assertIsNone(
                        html_pattern.search(text),
                        f"Section {sec} version {i} contains HTML tags")

    def test_no_null_bytes_in_text(self):
        """Text should not contain null bytes (indicates binary corruption)."""
        for sec in all_snapshot_sections():
            data = load_versions(sec)
            for i, v in enumerate(data['versions']):
                text = v.get('text', '')
                with self.subTest(section=sec, version=i):
                    self.assertNotIn('\x00', text,
                                     f"Section {sec} version {i} has null bytes")

    def test_section_symbol_in_v0_text(self):
        """Most v0 text should begin with the section symbol or heading."""
        unexpected = []
        for sec in all_snapshot_sections():
            if sec in self.KNOWN_EMPTY_SECTIONS:
                continue
            data = load_versions(sec)
            text = data['versions'][0].get('text', '').strip()
            if not (text.startswith('\u00a7') or text.startswith('#') or
                    text.startswith('(a)') or text.startswith('Section')):
                unexpected.append((sec, text[:40]))
        # Allow a small number of exceptions
        self.assertLessEqual(
            len(unexpected), 5,
            f"Too many sections with unexpected v0 text start: "
            f"{unexpected}")


# ===========================================================================
# Current sections file integrity
# ===========================================================================

class TestCurrentSectionsIntegrity(unittest.TestCase):
    """Every file in data/current-sections/ must be well-formed."""

    def test_current_sections_exist(self):
        """The current-sections directory should have 100+ files."""
        files = [f for f in os.listdir(CURRENT_DIR) if f.endswith('.md')]
        self.assertGreaterEqual(len(files), 100,
                                f"Expected 100+ current sections, got {len(files)}")

    def test_all_current_sections_have_header(self):
        """Each current-sections file must start with '# 17 U.S.C. §'."""
        for fname in sorted(os.listdir(CURRENT_DIR)):
            if not fname.endswith('.md'):
                continue
            with self.subTest(file=fname):
                with open(os.path.join(CURRENT_DIR, fname)) as f:
                    first_line = f.readline().strip()
                self.assertTrue(
                    first_line.startswith('# 17 U.S.C.'),
                    f"{fname} header: '{first_line[:50]}' doesn't start "
                    f"with '# 17 U.S.C.'")

    def test_all_current_sections_non_trivial(self):
        """Each file should contain real statute text (> 100 chars)."""
        for fname in sorted(os.listdir(CURRENT_DIR)):
            if not fname.endswith('.md'):
                continue
            with self.subTest(file=fname):
                with open(os.path.join(CURRENT_DIR, fname)) as f:
                    content = f.read()
                self.assertGreater(
                    len(content), 100,
                    f"{fname} is only {len(content)} chars")

    def test_current_sections_have_source_credits(self):
        """Most current sections should have Pub. L. source credit blocks."""
        files_with_credits = 0
        total = 0
        for fname in sorted(os.listdir(CURRENT_DIR)):
            if not fname.endswith('.md'):
                continue
            total += 1
            with open(os.path.join(CURRENT_DIR, fname)) as f:
                content = f.read()
            if 'Pub. L.' in content:
                files_with_credits += 1
        self.assertGreaterEqual(
            files_with_credits / total, 0.9,
            f"Only {files_with_credits}/{total} sections have Pub. L. credits")

    def test_section_number_matches_filename(self):
        """The section number in the header should match the filename."""
        for fname in sorted(os.listdir(CURRENT_DIR)):
            if not fname.endswith('.md'):
                continue
            sec = fname.replace('.md', '')
            with self.subTest(file=fname):
                with open(os.path.join(CURRENT_DIR, fname)) as f:
                    first_line = f.readline().strip()
                self.assertIn(sec, first_line,
                              f"{fname}: header '{first_line}' doesn't "
                              f"contain section '{sec}'")

    def test_every_snapshot_has_current_section(self):
        """Every section with a snapshot should have a current-sections file."""
        for sec in all_snapshot_sections():
            with self.subTest(section=sec):
                path = os.path.join(CURRENT_DIR, f'{sec}.md')
                self.assertTrue(os.path.exists(path),
                                f"Section {sec} has snapshot but no "
                                f"current-sections file")


# ===========================================================================
# Amendment notes integrity
# ===========================================================================

class TestAmendmentNotesIntegrity(unittest.TestCase):
    """Every amendment notes file must be structurally valid."""

    def test_amendment_notes_exist(self):
        """Should have 80+ amendment notes files."""
        files = [f for f in os.listdir(NOTES_DIR) if f.endswith('-notes.md')]
        self.assertGreaterEqual(len(files), 80,
                                f"Expected 80+ notes files, got {len(files)}")

    def test_notes_have_section_header(self):
        """Each notes file should have a title header."""
        for fname in sorted(os.listdir(NOTES_DIR)):
            if not fname.endswith('-notes.md'):
                continue
            with self.subTest(file=fname):
                with open(os.path.join(NOTES_DIR, fname)) as f:
                    first_line = f.readline().strip()
                self.assertTrue(
                    first_line.startswith('#'),
                    f"{fname} doesn't start with a header: "
                    f"'{first_line[:50]}'")

    def test_most_notes_mention_pub_l(self):
        """Most amendment notes should reference at least one Pub. L. number.
        Some sections (e.g., 103, 202, 305) have never been amended and
        their notes contain only the original legislative history."""
        without_pl = []
        total = 0
        for fname in sorted(os.listdir(NOTES_DIR)):
            if not fname.endswith('-notes.md'):
                continue
            total += 1
            with open(os.path.join(NOTES_DIR, fname)) as f:
                content = f.read()
            if 'Pub. L.' not in content:
                without_pl.append(fname)
        # Allow up to 10% without PL references (unamended sections)
        self.assertLessEqual(
            len(without_pl), total * 0.15,
            f"{len(without_pl)}/{total} notes lack Pub. L. refs: "
            f"{without_pl}")

    def test_notes_filenames_match_sections(self):
        """Notes file names should correspond to valid section numbers."""
        sec_pattern = re.compile(r'^(\d+[A-Z]?)-notes\.md$')
        for fname in sorted(os.listdir(NOTES_DIR)):
            if not fname.endswith('-notes.md'):
                continue
            with self.subTest(file=fname):
                m = sec_pattern.match(fname)
                self.assertIsNotNone(m,
                                     f"{fname} doesn't match expected "
                                     f"naming pattern")

    def test_notes_non_empty(self):
        """Amendment notes should have content (> 100 chars).
        Some rarely-amended sections have short notes."""
        for fname in sorted(os.listdir(NOTES_DIR)):
            if not fname.endswith('-notes.md'):
                continue
            with self.subTest(file=fname):
                with open(os.path.join(NOTES_DIR, fname)) as f:
                    content = f.read()
                self.assertGreater(len(content), 100,
                                   f"{fname} is only {len(content)} chars")


# ===========================================================================
# Act-snapshots directory integrity
# ===========================================================================

class TestActSnapshotsIntegrity(unittest.TestCase):
    """Every act-snapshot directory must contain valid section files."""

    def test_act_snapshots_exist(self):
        """Should have at least 50 act-snapshot directories."""
        dirs = [d for d in os.listdir(ACT_SNAPSHOTS_DIR)
                if os.path.isdir(os.path.join(ACT_SNAPSHOTS_DIR, d))]
        self.assertGreaterEqual(len(dirs), 50,
                                f"Expected 50+ act-snapshot dirs, got {len(dirs)}")

    def test_act_snapshot_dirs_have_date_prefix(self):
        """Each act-snapshot directory should start with a YYYY-MM-DD date."""
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}-')
        for dirname in sorted(os.listdir(ACT_SNAPSHOTS_DIR)):
            if not os.path.isdir(os.path.join(ACT_SNAPSHOTS_DIR, dirname)):
                continue
            with self.subTest(dir=dirname):
                self.assertTrue(
                    date_pattern.match(dirname),
                    f"'{dirname}' doesn't start with a date")

    def test_act_snapshot_files_are_markdown(self):
        """All files in act-snapshot dirs should be .md files."""
        for dirname in sorted(os.listdir(ACT_SNAPSHOTS_DIR)):
            dirpath = os.path.join(ACT_SNAPSHOTS_DIR, dirname)
            if not os.path.isdir(dirpath):
                continue
            for fname in os.listdir(dirpath):
                with self.subTest(dir=dirname, file=fname):
                    self.assertTrue(fname.endswith('.md'),
                                    f"{dirname}/{fname} is not a .md file")

    def test_act_snapshot_files_non_empty(self):
        """Section files in act-snapshots should have real content."""
        for dirname in sorted(os.listdir(ACT_SNAPSHOTS_DIR)):
            dirpath = os.path.join(ACT_SNAPSHOTS_DIR, dirname)
            if not os.path.isdir(dirpath):
                continue
            for fname in os.listdir(dirpath):
                if not fname.endswith('.md'):
                    continue
                filepath = os.path.join(dirpath, fname)
                with self.subTest(dir=dirname, file=fname):
                    with open(filepath) as f:
                        content = f.read()
                    self.assertGreater(
                        len(content.strip()), 50,
                        f"{dirname}/{fname}: only {len(content.strip())} chars")

    def test_act_snapshot_section_numbers_valid(self):
        """Section filenames should be valid section numbers."""
        sec_pattern = re.compile(r'^\d+[A-Z]?\.md$')
        for dirname in sorted(os.listdir(ACT_SNAPSHOTS_DIR)):
            dirpath = os.path.join(ACT_SNAPSHOTS_DIR, dirname)
            if not os.path.isdir(dirpath):
                continue
            for fname in os.listdir(dirpath):
                if not fname.endswith('.md'):
                    continue
                with self.subTest(dir=dirname, file=fname):
                    self.assertTrue(
                        sec_pattern.match(fname),
                        f"{dirname}/{fname} doesn't look like a section number")

    def test_1976_act_snapshot_has_sections(self):
        """The 1976 Act snapshot should contain section files.
        Note: the 1976 act-snapshot only contains sections that were
        modified by later amendments (since unmodified sections are
        taken directly from current-sections by build.py)."""
        act_dir = None
        for dirname in os.listdir(ACT_SNAPSHOTS_DIR):
            if '1976-10-19' in dirname and 'copyright-act' in dirname:
                act_dir = os.path.join(ACT_SNAPSHOTS_DIR, dirname)
                break
        if act_dir is None:
            self.skipTest("No 1976 Act snapshot directory found")
        files = [f for f in os.listdir(act_dir) if f.endswith('.md')]
        self.assertGreaterEqual(len(files), 10,
                                f"1976 Act snapshot has only {len(files)} sections")

    def test_act_snapshot_dirs_chronological(self):
        """Act-snapshot directory dates should span 1976-2025."""
        dates = []
        for dirname in sorted(os.listdir(ACT_SNAPSHOTS_DIR)):
            if not os.path.isdir(os.path.join(ACT_SNAPSHOTS_DIR, dirname)):
                continue
            m = re.match(r'^(\d{4})-(\d{2})-(\d{2})', dirname)
            if m:
                dates.append(f"{m.group(1)}-{m.group(2)}-{m.group(3)}")
        self.assertTrue(any(d.startswith('197') for d in dates),
                        "No 1970s act-snapshots found")
        self.assertTrue(any(d.startswith('199') for d in dates),
                        "No 1990s act-snapshots found")
        self.assertTrue(any(d.startswith('200') or d.startswith('201')
                            or d.startswith('202') for d in dates),
                        "No 2000s+ act-snapshots found")


# ===========================================================================
# Pre-1976 text integrity
# ===========================================================================

class TestPre1976TextIntegrity(unittest.TestCase):
    """Pre-1976 statute text files must be authentic and substantive."""

    def test_pre1976_files_exist(self):
        """Should have at least 30 pre-1976 text files."""
        files = [f for f in os.listdir(PRE1976_DIR) if f.endswith('.md')]
        self.assertGreaterEqual(len(files), 30,
                                f"Expected 30+ pre-1976 files, got {len(files)}")

    def test_pre1976_files_have_year_prefix(self):
        """Pre-1976 files should start with a year."""
        for fname in sorted(os.listdir(PRE1976_DIR)):
            if not fname.endswith('.md'):
                continue
            with self.subTest(file=fname):
                self.assertTrue(
                    re.match(r'^\d{4}-', fname),
                    f"'{fname}' doesn't start with a year")

    def test_pre1976_key_acts_present(self):
        """Essential pre-1976 acts must have text files."""
        required = [
            '1790-copyright-act',
            '1831-copyright-act',
            '1870-copyright-act',
            '1909-copyright-act',
        ]
        files = os.listdir(PRE1976_DIR)
        for act_prefix in required:
            with self.subTest(act=act_prefix):
                matches = [f for f in files if f.startswith(act_prefix)]
                self.assertTrue(len(matches) > 0,
                                f"No pre-1976 file for '{act_prefix}'")

    def test_1909_act_is_substantial(self):
        """The 1909 Copyright Act should be a large document (full text)."""
        matches = [f for f in os.listdir(PRE1976_DIR)
                   if f.startswith('1909-copyright-act')]
        if not matches:
            self.skipTest("No 1909 Act file found")
        with open(os.path.join(PRE1976_DIR, matches[0])) as f:
            content = f.read()
        self.assertGreater(len(content), 10000,
                           f"1909 Act is only {len(content)} chars "
                           f"(expected full text)")

    def test_1790_act_mentions_books(self):
        """The 1790 Act protected books, maps, and charts."""
        matches = [f for f in os.listdir(PRE1976_DIR)
                   if f.startswith('1790-copyright-act')]
        if not matches:
            self.skipTest("No 1790 Act file found")
        with open(os.path.join(PRE1976_DIR, matches[0])) as f:
            content = f.read().lower()
        self.assertIn('book', content,
                      "1790 Act should mention books")
        self.assertIn('map', content,
                      "1790 Act should mention maps")

    def test_pre1976_files_non_trivial(self):
        """All pre-1976 files should be > 200 chars of real content."""
        for fname in sorted(os.listdir(PRE1976_DIR)):
            if not fname.endswith('.md'):
                continue
            with self.subTest(file=fname):
                with open(os.path.join(PRE1976_DIR, fname)) as f:
                    content = f.read()
                self.assertGreater(
                    len(content.strip()), 200,
                    f"{fname} is only {len(content.strip())} chars")

    def test_no_pre1976_file_references_post1976_law(self):
        """Pre-1976 files should not reference Title 17 sections
        (those didn't exist yet in their modern form)."""
        post_1976_terms = ['section 107', 'section 512', 'DMCA', 'VARA']
        for fname in sorted(os.listdir(PRE1976_DIR)):
            if not fname.endswith('.md'):
                continue
            with self.subTest(file=fname):
                with open(os.path.join(PRE1976_DIR, fname)) as f:
                    content = f.read().lower()
                for term in post_1976_terms:
                    self.assertNotIn(
                        term.lower(), content,
                        f"{fname} references post-1976 term '{term}'")


# ===========================================================================
# Acts.yaml metadata integrity
# ===========================================================================

class TestActsYamlIntegrity(unittest.TestCase):
    """The acts.yaml file must be well-formed with required fields."""

    @classmethod
    def setUpClass(cls):
        cls.acts = parse_acts_yaml()

    def test_acts_yaml_has_many_entries(self):
        """Should have 100+ acts defined."""
        self.assertGreaterEqual(len(self.acts), 100,
                                f"Expected 100+ acts, got {len(self.acts)}")

    def test_all_acts_have_name(self):
        """Every act must have a name."""
        for act in self.acts:
            self.assertTrue(len(act['name']) > 5,
                            f"Act has short name: '{act['name']}'")

    def test_all_acts_have_valid_date(self):
        """Every act must have a YYYY-MM-DD date."""
        date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}$')
        for act in self.acts:
            with self.subTest(act=act['name']):
                self.assertTrue(
                    date_pattern.match(act['date']),
                    f"Act '{act['name']}' has invalid date: '{act['date']}'")

    def test_acts_are_chronological(self):
        """Acts should be sorted by date."""
        dates = [a['date'] for a in self.acts]
        self.assertEqual(dates, sorted(dates),
                         "Acts are not in chronological order")

    def test_no_duplicate_act_names(self):
        """Act names should be unique."""
        names = [a['name'] for a in self.acts]
        dupes = [n for n in names if names.count(n) > 1]
        self.assertEqual(len(dupes), 0,
                         f"Duplicate act names: {set(dupes)}")

    def test_key_acts_present(self):
        """Essential acts must be defined."""
        required_acts = [
            'Copyright Act of 1790',
            'Copyright Act of 1831',
            'Copyright Act of 1870',
            'Copyright Act of 1909',
            'Copyright Act of 1976',
        ]
        act_names = [a['name'] for a in self.acts]
        for req in required_acts:
            with self.subTest(act=req):
                self.assertIn(req, act_names,
                              f"Required act '{req}' not found")

    def test_post_1976_acts_have_public_law(self):
        """Acts after 1976 should have a public_law field."""
        post_1976 = [a for a in self.acts if a['date'] > '1976-10-19']
        with_pl = [a for a in post_1976 if a['public_law']]
        ratio = len(with_pl) / len(post_1976) if post_1976 else 0
        self.assertGreaterEqual(
            ratio, 0.9,
            f"Only {len(with_pl)}/{len(post_1976)} post-1976 acts "
            f"have public_law numbers")

    def test_date_range_spans_history(self):
        """Acts should span from 1790 to recent times."""
        dates = [a['date'] for a in self.acts]
        self.assertTrue(dates[0].startswith('179'),
                        f"First act date is {dates[0]}, expected 179x")
        last_year = int(dates[-1][:4])
        self.assertGreaterEqual(last_year, 2010,
                                f"Last act year is {last_year}, expected 2010+")


# ===========================================================================
# Cross-file consistency
# ===========================================================================

class TestCrossFileConsistency(unittest.TestCase):
    """Verify consistency between different data directories."""

    def test_snapshot_sections_subset_of_current_sections(self):
        """Every snapshot section should have a current-sections file."""
        current_files = {f.replace('.md', '') for f in os.listdir(CURRENT_DIR)
                         if f.endswith('.md')}
        for sec in all_snapshot_sections():
            with self.subTest(section=sec):
                self.assertIn(sec, current_files,
                              f"Section {sec} has snapshot but no current file")

    def test_notes_sections_subset_of_current_sections(self):
        """Every amendment-notes section should have a current-sections file."""
        current_files = {f.replace('.md', '') for f in os.listdir(CURRENT_DIR)
                         if f.endswith('.md')}
        for fname in os.listdir(NOTES_DIR):
            if not fname.endswith('-notes.md'):
                continue
            sec = fname.replace('-notes.md', '')
            with self.subTest(section=sec):
                self.assertIn(sec, current_files,
                              f"Section {sec} has notes but no current file")

    def test_original_1976_sections_have_snapshots(self):
        """Sections created by the 1976 Act should have snapshot files."""
        original_1976 = [
            '102', '106', '107', '109', '110', '111', '112',
            '201', '203', '301', '302', '401', '501', '504', '506',
        ]
        snapshot_secs = set(all_snapshot_sections())
        for sec in original_1976:
            with self.subTest(section=sec):
                self.assertIn(sec, snapshot_secs,
                              f"Original 1976 section {sec} has no snapshot")


if __name__ == '__main__':
    unittest.main()
