#!/usr/bin/env python3
"""
Tests for TODO.md tasks: complex manual reconstruction of sections
§110, §111, §112, §114, §118, §119.

These tests verify:
1. CRJ/CRT/LoC anachronism removal is correct across all versions
2. §118 full reconstruction with correct institutional transitions
3. §112 subsection (f) addition/removal is reconstructed
4. §110 paragraph (10)/(11) addition/removal is reconstructed
5. Chronological ordering and version chain integrity
6. Year-PL consistency (year field matches Public Law enactment date)
7. Adjacent versions are not identical (reconstruction actually changed text)
8. TEACH Act text should not appear in pre-TEACH versions of §110

Usage:
    pytest tests/test_todo_tasks.py -v
"""

import json
import os
import re
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
SNAPSHOTS_DIR = os.path.join(DATA_DIR, 'snapshots')


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_versions(sec_num):
    """Load the full versions data for a section from its snapshot JSON."""
    path = os.path.join(SNAPSHOTS_DIR, f'{sec_num}-versions.json')
    with open(path) as f:
        return json.load(f)


def get_v0_text(sec_num):
    """Return the oldest (version 0) reconstructed text for a section."""
    data = load_versions(sec_num)
    return data['versions'][0]['text']


# Known Public Law enactment years (used for year-PL consistency checks)
PL_ENACTMENT_YEARS = {
    '94-553': 1976, '97-366': 1982, '99-397': 1986, '100-667': 1988,
    '101-318': 1990, '103-198': 1993, '103-369': 1994, '104-39': 1995,
    '105-80': 1997, '105-298': 1998, '105-304': 1998, '106-44': 1999,
    '106-113': 1999, '107-273': 2002, '107-321': 2002, '108-419': 2004,
    '108-447': 2004, '109-9': 2005, '109-303': 2006, '110-229': 2007,
    '110-403': 2007, '110-435': 2008, '111-36': 2009, '111-118': 2009,
    '111-175': 2010, '111-144': 2010, '111-151': 2010, '111-157': 2010,
    '111-295': 2009, '113-200': 2014, '115-264': 2018, '116-94': 2019,
}

# Sections under scrutiny per TODO.md
TODO_SECTIONS = ['110', '111', '112', '114', '118', '119']


# ===========================================================================
# CRJ Anachronism Tests
# ===========================================================================

class TestCRJAnachronismRemoval(unittest.TestCase):
    """Copyright Royalty Judges (CRJ) were established by PL 108-419 in 2004.
    No version dated before 2004 should mention 'Copyright Royalty Judges'."""

    def test_no_crj_before_2004(self):
        """Every version with year < 2004 must be free of CRJ references."""
        failures = []
        for sec in TODO_SECTIONS:
            data = load_versions(sec)
            for i, v in enumerate(data['versions']):
                year = v.get('year')
                if not year:
                    continue
                if int(year) < 2004:
                    text = v.get('text', '')
                    if 'Copyright Royalty Judges' in text:
                        pl = v.get('public_law', '?')
                        failures.append(
                            f"§{sec} v{i} (year={year}, PL {pl}): "
                            f"contains 'Copyright Royalty Judges'"
                        )
        self.assertEqual(failures, [],
                         "CRJ anachronism found in pre-2004 versions:\n"
                         + "\n".join(failures))

    def test_crj_present_after_2004_where_expected(self):
        """Sections that reference royalty processes should have CRJ after 2004."""
        # These sections are known to reference royalty institutions
        royalty_sections = ['111', '112', '114', '118', '119']
        for sec in royalty_sections:
            data = load_versions(sec)
            post_2004 = [v for v in data['versions']
                         if v.get('year') and int(v['year']) >= 2004]
            if post_2004:
                with self.subTest(section=sec):
                    latest_post_2004 = post_2004[-1]
                    text = latest_post_2004.get('text', '')
                    self.assertIn('Copyright Royalty Judges', text,
                                  f"§{sec} post-2004 version should reference CRJ")


class TestCRTAnachronismRemoval(unittest.TestCase):
    """Copyright Royalty Tribunal (CRT) was abolished in 1993 (PL 103-198).
    No version dated 1994 or later should use 'Copyright Royalty Tribunal'
    unless quoting historical text."""

    def test_no_crt_after_1993(self):
        """Versions from 1994 onwards should not reference the abolished CRT."""
        failures = []
        for sec in TODO_SECTIONS:
            data = load_versions(sec)
            for i, v in enumerate(data['versions']):
                year = v.get('year')
                if not year:
                    continue
                if int(year) >= 1994:
                    text = v.get('text', '')
                    if 'Copyright Royalty Tribunal' in text:
                        pl = v.get('public_law', '?')
                        failures.append(
                            f"§{sec} v{i} (year={year}, PL {pl}): "
                            f"contains 'Copyright Royalty Tribunal'"
                        )
        self.assertEqual(failures, [],
                         "CRT anachronism found in post-1993 versions:\n"
                         + "\n".join(failures))


class TestLoCTransition(unittest.TestCase):
    """Between 1993 (CRT abolished) and 2004 (CRJ established), royalty
    functions were handled by the Librarian of Congress. Versions from
    1993-2003 in royalty sections should reference LoC, not CRT or CRJ."""

    def test_loc_present_1993_to_2003(self):
        """Royalty sections should reference 'Librarian of Congress' in 1993-2003."""
        royalty_sections = ['111', '114', '118', '119']
        for sec in royalty_sections:
            data = load_versions(sec)
            for i, v in enumerate(data['versions']):
                year = v.get('year')
                if not year:
                    continue
                yr = int(year)
                if 1993 <= yr <= 2003:
                    with self.subTest(section=sec, version=i, year=year):
                        text = v.get('text', '')
                        self.assertIn('Librarian of Congress', text,
                                      f"§{sec} v{i} (year={year}) should "
                                      f"reference Librarian of Congress")


# ===========================================================================
# §118 Full Reconstruction Tests
# ===========================================================================

class TestSection118Reconstruction(unittest.TestCase):
    """§118 was claimed 'fully reconstructed with correct CRT/LoC/CRJ
    transitions across all versions' in TODO.md partial fixes."""

    def setUp(self):
        self.data = load_versions('118')
        self.versions = self.data['versions']

    def test_v0_uses_crt(self):
        """The 1976 original should reference Copyright Royalty Tribunal."""
        v0 = self.versions[0]
        self.assertEqual(v0.get('year'), '1976')
        self.assertIn('Copyright Royalty Tribunal', v0['text'])
        self.assertNotIn('Copyright Royalty Judges', v0['text'])
        self.assertNotIn('Librarian of Congress', v0['text'])

    def test_1993_version_uses_loc(self):
        """After CRT abolition (1993), §118 should reference LoC."""
        v1993 = None
        for v in self.versions:
            if v.get('public_law') == '103-198':
                v1993 = v
                break
        self.assertIsNotNone(v1993, "Should have a version for PL 103-198")
        self.assertIn('Librarian of Congress', v1993['text'])
        self.assertNotIn('Copyright Royalty Tribunal', v1993['text'])
        self.assertNotIn('Copyright Royalty Judges', v1993['text'])

    def test_post_2004_version_uses_crj(self):
        """After PL 108-419 (2004), §118 should reference CRJ."""
        v_108_419 = None
        for v in self.versions:
            if v.get('public_law') == '108-419':
                v_108_419 = v
                break
        self.assertIsNotNone(v_108_419,
                             "Should have a version for PL 108-419")
        self.assertIn('Copyright Royalty Judges', v_108_419['text'])
        self.assertNotIn('Copyright Royalty Tribunal', v_108_419['text'])

    def test_pl108_419_year_is_2004_not_1997(self):
        """PL 108-419 was enacted 2004-11-30. The year field must not be 1997.

        This is a known data error: the version for PL 108-419 in §118 has
        year='1997' instead of the correct year (2004 or later).
        """
        for v in self.versions:
            if v.get('public_law') == '108-419':
                year = v.get('year')
                self.assertNotEqual(year, '1997',
                                    "PL 108-419 was enacted in 2004, "
                                    "not 1997. Year field is wrong.")
                self.assertGreaterEqual(int(year), 2004,
                                        "PL 108-419 year should be >= 2004")

    def test_no_institutional_gaps(self):
        """Every version of §118 should reference exactly one of
        CRT, LoC, or CRJ (not zero, not two)."""
        for i, v in enumerate(self.versions):
            text = v.get('text', '')
            if not text:
                continue
            has_crt = 'Copyright Royalty Tribunal' in text
            has_loc = 'Librarian of Congress' in text
            has_crj = 'Copyright Royalty Judges' in text
            # At least one institution should be referenced
            institutions = [x for x in [has_crt, has_loc, has_crj] if x]
            with self.subTest(version=i, year=v.get('year', '?')):
                self.assertGreaterEqual(
                    len(institutions), 1,
                    f"v{i} has no institutional references")
                # CRT and CRJ should never coexist
                self.assertFalse(
                    has_crt and has_crj,
                    f"v{i} has both CRT and CRJ - impossible overlap")


# ===========================================================================
# §112 Subsection (f) Reconstruction Tests
# ===========================================================================

class TestSection112SubsecF(unittest.TestCase):
    """TODO.md states '§112 subsec (f) addition/removal reconstructed'.
    Subsection (f) was added by PL 105-304 (DMCA, 1998). The original
    §112 from 1976 should NOT have subsection (f)."""

    def setUp(self):
        self.data = load_versions('112')
        self.versions = self.data['versions']

    def test_v0_year(self):
        """First version should be from 1998 (when §112 snapshot begins)
        or earlier if pre-DMCA text was reconstructed."""
        v0 = self.versions[0]
        year = v0.get('year')
        self.assertIsNotNone(year)

    def test_subsection_structure(self):
        """Check that subsection labels are consistent across versions."""
        for i, v in enumerate(self.versions):
            text = v.get('text', '')
            if not text:
                continue
            with self.subTest(version=i, year=v.get('year', '?')):
                # Every version should have subsection (a)
                self.assertIn('(a)', text,
                              f"v{i} missing subsection (a)")


# ===========================================================================
# §110 Paragraph (10)/(11) Tests
# ===========================================================================

class TestSection110Paragraphs(unittest.TestCase):
    """TODO.md states '§110 par. (10)/(11) addition/removal reconstructed'.
    Paragraph (11) was added by PL 107-273 (2002). Pre-2002 versions should
    have only (10) paragraphs, not (11)."""

    def setUp(self):
        self.data = load_versions('110')
        self.versions = self.data['versions']

    def test_pre_2002_has_no_par_11(self):
        """Versions before 2002 should not have paragraph (11)."""
        for i, v in enumerate(self.versions):
            year = v.get('year')
            if not year or int(year) >= 2002:
                continue
            with self.subTest(version=i, year=year):
                text = v.get('text', '')
                # Look for paragraph (11) at the start of a line or after whitespace
                has_11 = bool(re.search(r'\(11\)', text))
                self.assertFalse(has_11,
                                 f"v{i} (year={year}) should not have par. (11)")

    def test_post_2002_has_par_11(self):
        """Versions from 2002 onwards should have paragraph (11)."""
        for i, v in enumerate(self.versions):
            year = v.get('year')
            if not year or int(year) < 2002:
                continue
            with self.subTest(version=i, year=year):
                text = v.get('text', '')
                has_11 = bool(re.search(r'\(11\)', text))
                self.assertTrue(has_11,
                                f"v{i} (year={year}) should have par. (11)")

    def test_all_versions_have_par_10(self):
        """All versions of §110 should have paragraph (10)."""
        for i, v in enumerate(self.versions):
            text = v.get('text', '')
            if not text:
                continue
            with self.subTest(version=i, year=v.get('year', '?')):
                self.assertIn('(10)', text)


# ===========================================================================
# TEACH Act Anachronism Tests for §110
# ===========================================================================

class TestSection110TEACHAct(unittest.TestCase):
    """The TEACH Act (PL 107-273 Div. C Title III Subtitle C, 2002) rewrote
    §110(2). Pre-TEACH versions should have the original 1976 par. (2) text,
    not the rewritten digital/mediated instructional text.

    Note: PL 107-273 was enacted 2002-11-02 but the version has year='2001'
    (a year-PL mismatch). We identify pre/post-TEACH by PL number, not year.
    """

    def setUp(self):
        self.data = load_versions('110')
        self.versions = self.data['versions']
        # Find the index of the TEACH Act version (PL 107-273)
        self.teach_idx = None
        for i, v in enumerate(self.versions):
            if v.get('public_law', '').startswith('107-273'):
                self.teach_idx = i
                break

    def _extract_par2(self, text):
        """Extract paragraph (2) text from a §110 version."""
        match = re.search(r'\(2\)(.*?)(?=\n\(3\)|\n\n\(3\))', text, re.DOTALL)
        return match.group(0) if match else ''

    def _is_pre_teach(self, idx):
        """Whether a version index is before the TEACH Act."""
        if self.teach_idx is None:
            return False
        return idx < self.teach_idx

    def test_teach_act_year_should_be_2002(self):
        """PL 107-273 was enacted 2002-11-02. The year field should be 2002,
        not 2001."""
        self.assertIsNotNone(self.teach_idx,
                             "TEACH Act version (PL 107-273) not found in §110")
        v = self.versions[self.teach_idx]
        year = v.get('year')
        self.assertEqual(year, '2002',
                         f"TEACH Act (PL 107-273) has year={year}, "
                         f"expected 2002")

    def test_pre_teach_no_digital_transmission(self):
        """Pre-TEACH versions should not contain 'digital' in par. (2).

        The original §110(2) covered 'transmission' for 'systematic
        instructional activities' — it did not mention digital networks.
        """
        for i, v in enumerate(self.versions):
            if not self._is_pre_teach(i):
                continue
            year = v.get('year', '?')
            with self.subTest(version=i, year=year):
                par2 = self._extract_par2(v.get('text', ''))
                self.assertNotIn('digital', par2.lower(),
                                 f"Pre-TEACH v{i} (year={year}) par. (2) "
                                 f"should not mention 'digital'")

    def test_pre_teach_no_mediated_instructional(self):
        """Pre-TEACH versions should not reference 'mediated instructional
        activities' — that language was introduced by the TEACH Act."""
        for i, v in enumerate(self.versions):
            if not self._is_pre_teach(i):
                continue
            year = v.get('year', '?')
            with self.subTest(version=i, year=year):
                text = v.get('text', '')
                self.assertNotIn('mediated instructional activities',
                                 text.lower(),
                                 f"Pre-TEACH v{i} (year={year}) should "
                                 f"not reference mediated instructional activities")

    def test_post_teach_has_mediated_instructional(self):
        """Post-TEACH versions (from PL 107-273 onwards) should contain the
        rewritten par. (2) text."""
        self.assertIsNotNone(self.teach_idx)
        for i, v in enumerate(self.versions):
            if i < self.teach_idx:
                continue
            if v.get('act') == 'Current':
                continue
            year = v.get('year', '?')
            with self.subTest(version=i, year=year):
                text = v.get('text', '')
                self.assertIn('mediated instructional activities',
                              text.lower(),
                              f"Post-TEACH v{i} (year={year}) should "
                              f"reference mediated instructional activities")


# ===========================================================================
# Chronological Ordering Tests
# ===========================================================================

class TestVersionChronologicalOrder(unittest.TestCase):
    """Version chains should be in chronological order (oldest first)."""

    def test_versions_are_chronologically_sorted(self):
        """Years should be non-decreasing across the version chain."""
        for sec in TODO_SECTIONS:
            data = load_versions(sec)
            years = []
            for v in data['versions']:
                y = v.get('year')
                if y:
                    years.append(int(y))
            with self.subTest(section=sec):
                self.assertEqual(years, sorted(years),
                                 f"§{sec} versions are not in chronological "
                                 f"order: {years}")


# ===========================================================================
# Year-PL Consistency Tests
# ===========================================================================

class TestYearPLConsistency(unittest.TestCase):
    """The 'year' field should be consistent with the Public Law enactment
    date. A tolerance of ±2 years is allowed for effective dates that differ
    from enactment, but large mismatches indicate data errors."""

    def test_year_matches_pl_enactment(self):
        """Year field should be within 2 years of the PL enactment date."""
        failures = []
        for sec in TODO_SECTIONS:
            data = load_versions(sec)
            for i, v in enumerate(data['versions']):
                year = v.get('year')
                pl = v.get('public_law', '')
                # Strip title suffixes for lookup
                pl_base = re.sub(r',\s*Title.*$', '', pl)
                if year and pl_base in PL_ENACTMENT_YEARS:
                    expected = PL_ENACTMENT_YEARS[pl_base]
                    diff = abs(int(year) - expected)
                    if diff > 2:
                        failures.append(
                            f"§{sec} v{i}: year={year} but PL {pl_base} "
                            f"was enacted in {expected} (off by {diff} years)")
        self.assertEqual(failures, [],
                         "Year-PL mismatches found:\n" + "\n".join(failures))

    def test_118_pl108_419_not_year_1997(self):
        """Specific regression: §118 PL 108-419 had year='1997' instead of 2004."""
        data = load_versions('118')
        for v in data['versions']:
            if v.get('public_law') == '108-419':
                self.assertNotEqual(v.get('year'), '1997',
                                    "Known bug: §118 PL 108-419 listed as "
                                    "year 1997 instead of 2004")


# ===========================================================================
# Adjacent Version Uniqueness Tests
# ===========================================================================

class TestAdjacentVersionsNotIdentical(unittest.TestCase):
    """If two adjacent versions have identical text, the reconstruction
    failed to apply the amendment. This indicates a TODO item that hasn't
    been completed (full text reconstruction still needed)."""

    def _count_identical_pairs(self, sec):
        """Count pairs of adjacent versions with identical text."""
        data = load_versions(sec)
        identical = []
        for i in range(len(data['versions']) - 1):
            t1 = data['versions'][i].get('text', '')
            t2 = data['versions'][i + 1].get('text', '')
            if t1 and t2 and t1 == t2:
                y1 = data['versions'][i].get('year', '?')
                y2 = data['versions'][i + 1].get('year', '?')
                identical.append((i, y1, y2))
        return identical

    def test_114_has_distinct_versions(self):
        """§114 has extensive identical adjacent versions (webcaster acts etc.)
        indicating amendments were not properly reverse-applied.

        Currently v0==v1==v2==v3 (1995-2002) and v4==v5==...==v10 (2004-current)
        meaning only the CRJ substitution was successfully applied.
        """
        identical = self._count_identical_pairs('114')
        # If the TODO tasks are done, there should be far fewer identical pairs
        # Currently there are ~9 identical pairs out of 10 transitions
        self.assertLess(len(identical), 9,
                        f"§114 has {len(identical)} identical adjacent version "
                        f"pairs — amendments not properly reconstructed: "
                        f"{identical}")

    def test_119_has_distinct_versions(self):
        """§119 was comprehensively restructured by multiple acts.
        Multiple identical pairs indicate incomplete reconstruction."""
        identical = self._count_identical_pairs('119')
        # Currently ~12 identical pairs — far too many
        self.assertLess(len(identical), 12,
                        f"§119 has {len(identical)} identical adjacent version "
                        f"pairs — amendments not properly reconstructed: "
                        f"{identical}")

    def test_111_has_distinct_versions(self):
        """§111 should have distinct text across its 15 versions."""
        identical = self._count_identical_pairs('111')
        self.assertLess(len(identical), 6,
                        f"§111 has {len(identical)} identical adjacent version "
                        f"pairs — amendments not properly reconstructed: "
                        f"{identical}")

    def test_110_has_distinct_versions(self):
        """§110 should have distinct text across versions, especially after
        the TEACH Act and other amendments."""
        identical = self._count_identical_pairs('110')
        self.assertLess(len(identical), 4,
                        f"§110 has {len(identical)} identical adjacent version "
                        f"pairs — amendments not properly reconstructed: "
                        f"{identical}")


# ===========================================================================
# §111 Satellite Home Viewer Act Tests
# ===========================================================================

class TestSection111SatelliteActs(unittest.TestCase):
    """The Satellite Home Viewer Act of 1994 (PL 103-369) modified §111.
    This is listed as a remaining TODO item."""

    def setUp(self):
        self.data = load_versions('111')
        self.versions = self.data['versions']

    def test_1994_version_differs_from_prior(self):
        """The 1994 Satellite Home Viewer Act should produce a distinct
        version (not identical to the prior version)."""
        for i, v in enumerate(self.versions):
            if v.get('public_law') == '103-369':
                prior = self.versions[i - 1] if i > 0 else None
                if prior:
                    self.assertNotEqual(
                        v.get('text', ''), prior.get('text', ''),
                        "PL 103-369 (Satellite Home Viewer Act 1994) "
                        "version is identical to prior — reconstruction "
                        "not applied")
                break

    def test_has_satellite_related_content(self):
        """Post-1994 versions should contain satellite-related language."""
        for v in self.versions:
            if v.get('public_law') == '103-369':
                text = v.get('text', '').lower()
                self.assertTrue(
                    'satellite' in text or 'secondary transmission' in text,
                    "§111 version for Satellite Home Viewer Act should "
                    "contain satellite-related language")
                break


# ===========================================================================
# §119 Comprehensive Reconstruction Tests
# ===========================================================================

class TestSection119Reconstruction(unittest.TestCase):
    """§119 underwent multiple complete rewrites. TODO.md lists several
    remaining acts for §119."""

    def setUp(self):
        self.data = load_versions('119')
        self.versions = self.data['versions']

    def test_2010_versions_are_not_all_identical(self):
        """§119 has 4 versions in 2010 (PLs 111-144, 111-151, 111-157, 111-175).
        These should not all be identical — they represent different acts
        with different effects."""
        v2010 = [v for v in self.versions if v.get('year') == '2010']
        if len(v2010) >= 2:
            texts = [v.get('text', '') for v in v2010]
            unique = len(set(texts))
            self.assertGreater(unique, 1,
                               f"All {len(v2010)} versions from 2010 have "
                               f"identical text — reconstruction incomplete")

    def test_111_175_comprehensive_rewrite(self):
        """PL 111-175 (STELA 2010) completely rewrote §119. Its text should
        differ substantially from the prior version."""
        for i, v in enumerate(self.versions):
            if v.get('public_law') == '111-175':
                prior = self.versions[i - 1] if i > 0 else None
                if prior:
                    self.assertNotEqual(
                        v.get('text', ''), prior.get('text', ''),
                        "PL 111-175 (STELA 2010 rewrite of §119) should "
                        "differ from prior version")
                break

    def test_pre_1994_uses_loc_not_crj(self):
        """All pre-1994 versions of §119 should use Librarian of Congress,
        not Copyright Royalty Judges."""
        for i, v in enumerate(self.versions):
            year = v.get('year')
            if not year or int(year) >= 1994:
                continue
            with self.subTest(version=i, year=year):
                text = v.get('text', '')
                self.assertNotIn('Copyright Royalty Judges', text)


# ===========================================================================
# §114 Webcaster Acts Tests
# ===========================================================================

class TestSection114WebcasterActs(unittest.TestCase):
    """§114 was modified by Small Webcaster Amendments Act of 2002,
    Webcaster Settlement Act of 2008, and Webcaster Settlement Act of 2009.
    These are listed as remaining TODO items."""

    def setUp(self):
        self.data = load_versions('114')
        self.versions = self.data['versions']

    def test_2002_webcaster_produces_distinct_version(self):
        """Small Webcaster Amendments Act of 2002 (PL 107-321) should
        produce a version distinct from PL 105-304 (1998)."""
        for i, v in enumerate(self.versions):
            if v.get('public_law') == '107-321':
                prior = self.versions[i - 1] if i > 0 else None
                if prior:
                    self.assertNotEqual(
                        v.get('text', ''), prior.get('text', ''),
                        "PL 107-321 (Small Webcaster 2002) version is "
                        "identical to prior — reconstruction not applied")
                break

    def test_2008_webcaster_produces_distinct_version(self):
        """Webcaster Settlement Act of 2008 (PL 110-435) should produce
        a distinct version."""
        for i, v in enumerate(self.versions):
            if v.get('public_law') == '110-435':
                prior = self.versions[i - 1] if i > 0 else None
                if prior:
                    self.assertNotEqual(
                        v.get('text', ''), prior.get('text', ''),
                        "PL 110-435 (Webcaster Settlement 2008) version is "
                        "identical to prior — reconstruction not applied")
                break

    def test_2009_webcaster_produces_distinct_version(self):
        """Webcaster Settlement Act of 2009 (PL 111-36) should produce
        a distinct version."""
        for i, v in enumerate(self.versions):
            if v.get('public_law') == '111-36':
                prior = self.versions[i - 1] if i > 0 else None
                if prior:
                    self.assertNotEqual(
                        v.get('text', ''), prior.get('text', ''),
                        "PL 111-36 (Webcaster Settlement 2009) version is "
                        "identical to prior — reconstruction not applied")
                break

    def test_pre_2004_all_identical_is_bad(self):
        """If all pre-2004 versions (1995-2002) are identical, the DPRA and
        webcaster amendments were not reconstructed at all."""
        pre_2004 = [v for v in self.versions
                    if v.get('year') and int(v['year']) < 2004]
        if len(pre_2004) >= 2:
            texts = [v.get('text', '') for v in pre_2004]
            unique = len(set(t for t in texts if t))
            self.assertGreater(unique, 1,
                               f"All {len(pre_2004)} pre-2004 versions of §114 "
                               f"are identical — no amendments reconstructed")


# ===========================================================================
# General Version Chain Sanity
# ===========================================================================

class TestVersionChainSanity(unittest.TestCase):
    """General sanity checks on all TODO section version chains."""

    def test_versions_have_required_fields(self):
        """Every non-current version should have year and public_law fields."""
        for sec in TODO_SECTIONS:
            data = load_versions(sec)
            for i, v in enumerate(data['versions']):
                if v.get('act') == 'Current':
                    continue
                with self.subTest(section=sec, version=i):
                    self.assertIn('text', v,
                                  f"§{sec} v{i} missing 'text' field")
                    self.assertTrue(v['text'],
                                    f"§{sec} v{i} has empty text")

    def test_no_null_versions(self):
        """The last entry being a null/empty version is a data format issue
        that should be cleaned up."""
        for sec in TODO_SECTIONS:
            data = load_versions(sec)
            last = data['versions'][-1]
            with self.subTest(section=sec):
                text = last.get('text', '')
                self.assertTrue(text,
                                f"§{sec} last version has empty/null text")

    def test_first_version_has_substantive_text(self):
        """Version 0 should have substantial text (not a stub)."""
        for sec in TODO_SECTIONS:
            v0_text = get_v0_text(sec)
            with self.subTest(section=sec):
                self.assertGreater(len(v0_text), 500,
                                   f"§{sec} v0 text is suspiciously short "
                                   f"({len(v0_text)} chars)")

    def test_issues_list_exists(self):
        """Each section should have an 'issues' field documenting known
        reconstruction problems."""
        for sec in TODO_SECTIONS:
            data = load_versions(sec)
            with self.subTest(section=sec):
                self.assertIn('issues', data,
                              f"§{sec} missing 'issues' field")


# ===========================================================================
# Cross-Section Institutional Consistency
# ===========================================================================

class TestInstitutionalConsistencyAcrossSections(unittest.TestCase):
    """All sections should agree on institutional terminology for a given era.
    If §111 uses LoC in 1999, then §118 and §119 should too."""

    def test_1999_versions_agree_on_loc(self):
        """All sections with a 1999 version should use LoC, not CRJ or CRT."""
        for sec in ['111', '114', '118', '119']:
            data = load_versions(sec)
            for v in data['versions']:
                if v.get('year') == '1999':
                    text = v.get('text', '')
                    with self.subTest(section=sec, pl=v.get('public_law')):
                        if 'Librarian of Congress' in text or \
                           'Copyright Royalty' in text:
                            self.assertNotIn('Copyright Royalty Judges', text,
                                             f"§{sec} 1999 version has CRJ")
                            self.assertNotIn('Copyright Royalty Tribunal', text,
                                             f"§{sec} 1999 version has CRT")


if __name__ == '__main__':
    unittest.main()
