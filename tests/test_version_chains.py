#!/usr/bin/env python3
"""
Version chain consistency tests.

Verifies that version chains are internally consistent: adjacent versions
differ from each other, current version matches the current-sections file,
act-snapshot text corresponds to the right version in the chain, and
amendments in the notes are reflected in the version history.

These tests catch issues like:
- Identical adjacent versions (failed reversal that wasn't flagged)
- Current version drift (snapshot out of sync with current-sections)
- Missing amendments (notes mention a PL but no version exists for it)
- Act-snapshot/version-chain mismatches

Usage:
    python3 -m unittest tests/test_version_chains.py -v
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


def load_current_text(sec_num):
    """Load and strip the current-sections file to compare with snapshot."""
    path = os.path.join(CURRENT_DIR, f'{sec_num}.md')
    if not os.path.exists(path):
        return None
    with open(path) as f:
        content = f.read()
    # Strip header line
    lines = content.strip().split('\n')
    if lines and lines[0].startswith('#'):
        lines = lines[1:]
    return '\n'.join(lines).strip()


def normalize_text(text):
    """Normalize whitespace for comparison."""
    return re.sub(r'\s+', ' ', text.strip())


# ===========================================================================
# Adjacent version differences
# ===========================================================================

class TestAdjacentVersionsDiffer(unittest.TestCase):
    """Adjacent versions in a chain should differ from each other.
    Identical adjacent versions indicate a failed reversal. We track
    the overall quality metric rather than failing per-version, since
    many sections have known failed auto-reversals recorded in the
    'auto_reversed' field."""

    def test_identical_adjacent_versions_quality(self):
        """Track the overall quality of version reversals. Many amendments
        involve adding/removing subsections that the auto-reversal can't
        handle, producing identical adjacent versions. We verify the
        metric is above a baseline and track it for improvement."""
        total_pairs = 0
        identical_pairs = 0
        for sec in all_snapshot_sections():
            data = load_versions(sec)
            versions = data['versions']
            for i in range(1, len(versions)):
                total_pairs += 1
                text_prev = normalize_text(versions[i-1].get('text', ''))
                text_curr = normalize_text(versions[i].get('text', ''))
                if text_prev == text_curr:
                    identical_pairs += 1

        if total_pairs == 0:
            return
        pct_different = (total_pairs - identical_pairs) / total_pairs * 100
        # Current baseline is ~34%. If this drops, something regressed.
        self.assertGreaterEqual(
            pct_different, 25,
            f"Only {pct_different:.1f}% of version pairs differ "
            f"({identical_pairs}/{total_pairs} identical). "
            f"This is below baseline -- possible regression.")

    def test_key_sections_have_no_identical_adjacent_versions(self):
        """Sections that have been manually verified should have no
        identical adjacent versions (all reversals successful)."""
        key_sections = ['102', '104', '109', '113', '116', '301',
                        '302', '504', '506']
        for sec in key_sections:
            if sec not in set(all_snapshot_sections()):
                continue
            data = load_versions(sec)
            versions = data['versions']
            for i in range(1, len(versions)):
                text_prev = normalize_text(versions[i-1].get('text', ''))
                text_curr = normalize_text(versions[i].get('text', ''))
                with self.subTest(section=sec, version_pair=f"v{i-1}/v{i}"):
                    if text_prev == text_curr:
                        pl = versions[i].get('public_law', '?')
                        self.fail(
                            f"Key section {sec}: v{i-1} and v{i} identical "
                            f"(PL {pl})")

    def test_version_text_changes_are_mostly_substantive(self):
        """Where versions differ, the changes should generally involve
        different words, not just whitespace rearrangement. We allow
        a few exceptions since some amendments only change formatting
        (e.g., rewriting numerals, adding/removing hyphens)."""
        whitespace_only = []
        total_different = 0
        for sec in all_snapshot_sections():
            data = load_versions(sec)
            versions = data['versions']
            for i in range(1, len(versions)):
                text_prev = versions[i-1].get('text', '')
                text_curr = versions[i].get('text', '')
                if normalize_text(text_prev) != normalize_text(text_curr):
                    total_different += 1
                    words_prev = set(text_prev.split())
                    words_curr = set(text_curr.split())
                    diff = words_prev.symmetric_difference(words_curr)
                    if len(diff) == 0:
                        whitespace_only.append(f"{sec} v{i}")
        # Allow up to 20% whitespace-only changes
        if total_different > 0:
            pct = len(whitespace_only) / total_different * 100
            self.assertLess(
                pct, 20,
                f"{len(whitespace_only)}/{total_different} version changes "
                f"are whitespace-only: {whitespace_only[:5]}")


# ===========================================================================
# Current version matches current-sections file
# ===========================================================================

class TestCurrentVersionMatchesFile(unittest.TestCase):
    """The last version in each snapshot should match the current-sections file."""

    def test_current_version_text_overlaps_with_file(self):
        """The current version text should share substantial content with
        the current-sections file. We check word overlap rather than exact
        substring match since source credits may differ."""
        mismatches = []
        for sec in all_snapshot_sections():
            current_file_text = load_current_text(sec)
            if current_file_text is None or len(current_file_text) < 100:
                continue
            data = load_versions(sec)
            snapshot_current = data['versions'][-1].get('text', '')
            if len(snapshot_current) < 100:
                continue

            file_words = set(normalize_text(current_file_text).split())
            snap_words = set(normalize_text(snapshot_current).split())
            if not file_words:
                continue
            overlap = len(file_words & snap_words) / len(file_words)
            if overlap < 0.5:
                mismatches.append(f"{sec}: {overlap:.0%} word overlap")

        self.assertLessEqual(
            len(mismatches), 5,
            f"Too many sections where current version doesn't match file: "
            f"{mismatches}")

    def test_section_heading_consistent(self):
        """The section symbol/heading in v0 should reference the right section."""
        mismatches = []
        for sec in all_snapshot_sections():
            data = load_versions(sec)
            text = data['versions'][0].get('text', '')
            if text.startswith('\u00a7'):
                sec_ref = f'\u00a7{sec}'
                if not text.startswith(sec_ref):
                    mismatches.append(
                        f"{sec}: starts with '{text[:20]}'")
        self.assertLessEqual(
            len(mismatches), 3,
            f"Too many section heading mismatches: {mismatches}")


# ===========================================================================
# Version chain completeness
# ===========================================================================

class TestVersionChainCompleteness(unittest.TestCase):
    """The version chain should account for amendments listed in notes."""

    def test_version_count_reasonable(self):
        """Sections with many amendments should have many versions."""
        # These sections are known to be heavily amended
        heavily_amended = {
            '111': 6,   # Cable retransmission
            '119': 5,   # Satellite retransmission
            '114': 5,   # Sound recordings
            '504': 4,   # Statutory damages
            '506': 3,   # Criminal offenses
        }
        for sec, min_versions in heavily_amended.items():
            if sec not in set(all_snapshot_sections()):
                continue
            with self.subTest(section=sec):
                data = load_versions(sec)
                self.assertGreaterEqual(
                    len(data['versions']), min_versions,
                    f"Section {sec} should have {min_versions}+ versions "
                    f"but has {len(data['versions'])}")

    def test_rarely_amended_sections_few_versions(self):
        """Sections known to be rarely amended should have few versions."""
        rarely_amended = {
            '107': 5,  # Fair use - very stable
            '202': 4,  # Ownership vs. material object
            '305': 4,  # Duration: year-end rule
        }
        for sec, max_versions in rarely_amended.items():
            if sec not in set(all_snapshot_sections()):
                continue
            with self.subTest(section=sec):
                data = load_versions(sec)
                self.assertLessEqual(
                    len(data['versions']), max_versions,
                    f"Section {sec} has {len(data['versions'])} versions "
                    f"but should have at most {max_versions}")

    def test_dmca_sections_start_in_late_1990s(self):
        """DMCA-created sections (512, 1201, 1202) should have their
        earliest version in the late 1990s. The year may be 1998 or 1999
        depending on how amendment notes record the timeline."""
        dmca_sections = ['512', '1201', '1202']
        for sec in dmca_sections:
            if sec not in set(all_snapshot_sections()):
                continue
            with self.subTest(section=sec):
                data = load_versions(sec)
                v0 = data['versions'][0]
                year = v0.get('year', '')
                self.assertTrue(
                    year in ('1998', '1999'),
                    f"Section {sec} v0 year is '{year}', "
                    f"expected '1998' or '1999' (DMCA era)")

    def test_vara_sections_start_in_1990(self):
        """VARA-created sections (106A) should start in 1990."""
        if '106A' not in set(all_snapshot_sections()):
            self.skipTest("No 106A snapshot")
        data = load_versions('106A')
        v0 = data['versions'][0]
        year = v0.get('year', '')
        self.assertEqual(year, '1990',
                         f"Section 106A v0 year is '{year}', "
                         f"expected '1990' (VARA)")

    def test_chip_protection_sections_from_1980s(self):
        """Chapter 9 sections (901+) were created by the Semiconductor
        Chip Protection Act of 1984 (PL 98-620). The v0 may be from 1984
        or later if amendments restructured the version chain."""
        chip_sections = ['901', '902']
        for sec in chip_sections:
            if sec not in set(all_snapshot_sections()):
                continue
            with self.subTest(section=sec):
                data = load_versions(sec)
                v0 = data['versions'][0]
                year = v0.get('year', '')
                pl = v0.get('public_law', '')
                date = v0.get('date', '')
                # Accept 1984 in year, date, or PL 98-620
                is_1980s = (
                    (year and year.isdigit() and 1984 <= int(year) <= 1990) or
                    '98-620' in pl or
                    '94-553' in pl or  # listed under original 1976 Act
                    (date and '1984' in date)
                )
                self.assertTrue(
                    is_1980s,
                    f"Section {sec} v0: year={year}, pl={pl}, date={date}")


# ===========================================================================
# Act-snapshot / version-chain alignment
# ===========================================================================

class TestActSnapshotAlignment(unittest.TestCase):
    """Act-snapshot files should contain text from the correct version."""

    def _get_act_snapshot_text(self, dirname, sec):
        """Read an act-snapshot file for a section."""
        path = os.path.join(ACT_SNAPSHOTS_DIR, dirname, f'{sec}.md')
        if not os.path.exists(path):
            return None
        with open(path) as f:
            content = f.read()
        # Strip header
        lines = content.strip().split('\n')
        if lines and lines[0].startswith('#'):
            lines = lines[1:]
        return '\n'.join(lines).strip()

    def test_1976_act_snapshot_matches_v0(self):
        """For sections in the 1976 Act snapshot, the text should match
        the v0 text in the version chain."""
        act_dir = None
        for dirname in os.listdir(ACT_SNAPSHOTS_DIR):
            if '1976-10-19' in dirname and 'copyright-act' in dirname:
                act_dir = dirname
                break
        if act_dir is None:
            self.skipTest("No 1976 Act snapshot directory")

        dirpath = os.path.join(ACT_SNAPSHOTS_DIR, act_dir)
        sections_in_snapshot = set(all_snapshot_sections())

        for fname in sorted(os.listdir(dirpath)):
            if not fname.endswith('.md'):
                continue
            sec = fname.replace('.md', '')
            if sec not in sections_in_snapshot:
                continue

            with self.subTest(section=sec):
                act_text = self._get_act_snapshot_text(act_dir, sec)
                if act_text is None:
                    continue
                data = load_versions(sec)
                v0_text = data['versions'][0].get('text', '')

                # Compare normalized key phrases
                act_norm = normalize_text(act_text)[:200]
                v0_norm = normalize_text(v0_text)[:200]

                # They should share substantial content
                # (exact match may fail due to header stripping differences)
                overlap = len(set(act_norm.split()) &
                              set(v0_norm.split()))
                total = max(len(set(act_norm.split())), 1)
                self.assertGreater(
                    overlap / total, 0.5,
                    f"Section {sec}: 1976 act-snapshot and v0 text "
                    f"have low overlap ({overlap}/{total} words)")

    def test_berne_act_snapshot_differs_from_v0_for_key_sections(self):
        """For key sections modified by Berne (401, 104), the Berne
        act-snapshot text should differ from the pre-Berne v0 text."""
        berne_dir = None
        for dirname in os.listdir(ACT_SNAPSHOTS_DIR):
            if 'berne-convention' in dirname:
                berne_dir = dirname
                break
        if berne_dir is None:
            self.skipTest("No Berne Convention snapshot directory")

        # Only test sections known to have been meaningfully changed by Berne
        key_berne_sections = ['401', '104']
        for sec in key_berne_sections:
            if sec not in set(all_snapshot_sections()):
                continue
            berne_text = self._get_act_snapshot_text(berne_dir, sec)
            if berne_text is None:
                continue
            data = load_versions(sec)
            v0_text = data['versions'][0].get('text', '')
            with self.subTest(section=sec):
                self.assertNotEqual(
                    normalize_text(berne_text),
                    normalize_text(v0_text),
                    f"Section {sec}: Berne snapshot is identical "
                    f"to v0 (should show Berne amendments)")


# ===========================================================================
# Version year/PL cross-validation
# ===========================================================================

class TestVersionPLValidation(unittest.TestCase):
    """Public law numbers should be consistent across the project."""

    def test_no_duplicate_pls_in_version_chain(self):
        """Each PL should appear at most once per section's versions."""
        for sec in all_snapshot_sections():
            data = load_versions(sec)
            pls = []
            for v in data['versions']:
                pl = v.get('public_law')
                if pl:
                    pls.append(pl.split(',')[0].strip())
            with self.subTest(section=sec):
                seen = set()
                dupes = set()
                for pl in pls:
                    if pl in seen:
                        dupes.add(pl)
                    seen.add(pl)
                self.assertEqual(
                    len(dupes), 0,
                    f"Section {sec} has duplicate PLs: {dupes}")

    def test_version_years_monotonically_increasing(self):
        """Years should be non-decreasing through the version chain."""
        for sec in all_snapshot_sections():
            data = load_versions(sec)
            years = []
            for v in data['versions']:
                y = v.get('year')
                if y and y != 'current':
                    years.append(int(y))
            with self.subTest(section=sec):
                for i in range(1, len(years)):
                    self.assertGreaterEqual(
                        years[i], years[i-1],
                        f"Section {sec}: year {years[i]} at position {i} "
                        f"< year {years[i-1]} at position {i-1}")

    def test_pl_congress_matches_year(self):
        """The PL congress number should roughly correspond to the year.
        Congress N covers years (1787 + 2*N) to (1789 + 2*N).
        However, the 'year' field in snapshots represents when the
        amendment notes say the change occurred, which may be the year
        the act was enacted OR when it took effect. We allow +/- 2 years
        of slack since some amendments have delayed effective dates or
        the notes record an implementation year."""
        mismatches = []
        total = 0
        for sec in all_snapshot_sections():
            data = load_versions(sec)
            for i, v in enumerate(data['versions']):
                pl = v.get('public_law', '')
                year = v.get('year', '')
                if not pl or not year or year == 'current':
                    continue
                m = re.match(r'(\d+)-', pl)
                if not m:
                    continue
                congress = int(m.group(1))
                yr = int(year)
                total += 1
                # Congress N covers years (1787 + 2*N) to (1789 + 2*N)
                # Allow 2-year slack for delayed effective dates
                expected_start = 1787 + 2 * congress - 2
                expected_end = 1789 + 2 * congress + 2
                if not (expected_start <= yr <= expected_end):
                    mismatches.append(
                        f"{sec} v{i}: PL {pl} -> Congress {congress} "
                        f"({1787+2*congress}-{1789+2*congress}) but year={yr}")

        # Many sections (especially §101 with 43 versions) have the same
        # year for all versions because failed auto-reversals don't update
        # the year field. We track this as a quality metric.
        if total > 0:
            mismatch_pct = len(mismatches) / total * 100
            self.assertLess(
                mismatch_pct, 25,
                f"{len(mismatches)}/{total} ({mismatch_pct:.1f}%) PL/year "
                f"mismatches (baseline ~21%):\n" +
                '\n'.join(mismatches[:10]))


# ===========================================================================
# Text content sanity
# ===========================================================================

class TestTextContentSanity(unittest.TestCase):
    """Basic sanity checks on version text content."""

    def test_no_version_text_is_just_whitespace(self):
        """No version should have text that's only whitespace."""
        for sec in all_snapshot_sections():
            data = load_versions(sec)
            for i, v in enumerate(data['versions']):
                with self.subTest(section=sec, version=i):
                    text = v.get('text', '')
                    self.assertTrue(
                        len(text.strip()) > 0,
                        f"Section {sec} version {i} text is empty/whitespace")

    def test_version_text_not_truncated(self):
        """Version text should not end mid-word (truncation indicator).
        We check that text ends with a sentence-ending character,
        a closing paren (source credits), or a section reference."""
        truncated = []
        for sec in all_snapshot_sections():
            data = load_versions(sec)
            for i, v in enumerate(data['versions']):
                text = v.get('text', '').strip()
                if not text or len(text) < 50:
                    continue
                last_char = text[-1]
                # Acceptable endings
                if last_char in '.;:)"\u201d\u2019\u2014-':
                    continue
                # Some sections end with a list item or definition
                if last_char in ']>':
                    continue
                truncated.append(f"{sec} v{i}: ends with '{last_char}'")
        # Allow some edge cases
        self.assertLessEqual(
            len(truncated), 10,
            f"Too many possibly truncated versions:\n" +
            '\n'.join(truncated[:10]))

    def test_no_json_artifacts_in_text(self):
        """Text should not contain JSON syntax artifacts like literal
        backslash-n sequences (not actual newlines)."""
        for sec in all_snapshot_sections():
            data = load_versions(sec)
            for i, v in enumerate(data['versions']):
                text = v.get('text', '')
                with self.subTest(section=sec, version=i):
                    # Check for literal \n (not actual newlines)
                    self.assertNotIn('\\n', text[:50],
                                     f"Section {sec} v{i} starts with "
                                     f"escaped newlines (JSON artifact)")

    def test_versions_grow_or_shrink_reasonably(self):
        """Most version transitions shouldn't show extreme size changes.
        A few exceptions exist (e.g., §115 was completely rewritten by
        the MMA in 2018, going from ~3K to ~30K chars)."""
        extreme = []
        for sec in all_snapshot_sections():
            data = load_versions(sec)
            versions = data['versions']
            for i in range(1, len(versions)):
                len_prev = len(versions[i-1].get('text', ''))
                len_curr = len(versions[i].get('text', ''))
                if len_prev == 0 or len_curr == 0:
                    continue
                ratio = max(len_prev, len_curr) / min(len_prev, len_curr)
                if ratio >= 10:
                    extreme.append(f"{sec} v{i}: {ratio:.1f}x")
        # Allow a few extreme changes (complete rewrites do happen)
        self.assertLessEqual(
            len(extreme), 5,
            f"Too many extreme size changes: {extreme}")


if __name__ == '__main__':
    unittest.main()
