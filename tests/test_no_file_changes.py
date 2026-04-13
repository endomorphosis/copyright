#!/usr/bin/env python3
"""
Tests for TODO.md "Acts With No File Changes" tasks.

These acts exist as commits in the repo but have empty `files_changed` in
acts.json. Each should produce actual file changes in the output repo when
the snapshot data is wired up.

Three categories:
1. Full snapshots ready — all expected section files exist in act-snapshots/
2. Partial snapshots — missing §101 reconstruction
3. Partial snapshots — other missing sections (TEACH missing §802,
   Fairness in Music Licensing has wrong sections_expected)

Additionally tests the remaining intermediate version differentiation tasks
for §119 and §111.

Usage:
    pytest tests/test_no_file_changes.py -v
"""

import json
import os
import re
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
SNAPSHOTS_DIR = os.path.join(DATA_DIR, 'snapshots')
ACT_SNAPSHOTS_DIR = os.path.join(DATA_DIR, 'act-snapshots')
ACTS_JSON = os.path.join(DATA_DIR, 'acts.json')


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_acts():
    with open(ACTS_JSON) as f:
        return json.load(f)


def load_versions(sec_num):
    path = os.path.join(SNAPSHOTS_DIR, f'{sec_num}-versions.json')
    with open(path) as f:
        return json.load(f)


def find_act_by_pl(acts, pl_prefix):
    """Find act(s) whose public_law field contains pl_prefix."""
    return [a for a in acts if pl_prefix in a.get('public_law', '')]


def find_act_snapshot_dir(name_fragment):
    """Find act-snapshot directory matching a name fragment."""
    for dirname in os.listdir(ACT_SNAPSHOTS_DIR):
        if name_fragment in dirname:
            return os.path.join(ACT_SNAPSHOTS_DIR, dirname)
    return None


def snapshot_dir_files(dirname):
    """List .md section files in an act-snapshot directory."""
    dirpath = os.path.join(ACT_SNAPSHOTS_DIR, dirname)
    if not os.path.isdir(dirpath):
        return []
    return [f.replace('.md', '') for f in os.listdir(dirpath)
            if f.endswith('.md')]


# ===========================================================================
# Acts.json: all 23 acts with empty files_changed should be fixed
# ===========================================================================

class TestActsWithNoFileChanges(unittest.TestCase):
    """Every act in acts.json that has sections_expected but empty
    files_changed represents a pipeline gap — the snapshot data exists
    but the build isn't wiring it up."""

    @classmethod
    def setUpClass(cls):
        cls.acts = load_acts()

    def test_no_file_changes_acts_count(self):
        """There should be acts with empty files_changed that have
        sections_expected. This test documents how many remain."""
        empty = [a for a in self.acts
                 if a.get('files_changed') == []
                 and a.get('sections_expected')]
        # As fixes land, this number should shrink toward 0
        # Currently 23 per TODO.md
        self.assertLessEqual(
            len(empty), 23,
            f"Found {len(empty)} acts with empty files_changed "
            f"(should shrink as fixes land)")

    def test_all_empty_acts_have_sections_expected(self):
        """Every act with empty files_changed in our TODO list should
        at least have sections_expected defined so we know what to fix."""
        todo_pls = [
            '108-446', '108-482', '111-144', '111-157', '113-144',
            '116-94', '116-260', '117-263', '118-159', '119-60',
            '101-319', '102-64', '103-369', '106-160', '107-321',
            '110-434', '110-435', '111-36', '111-151', '115-261',
            '117-201', '107-273', '105-298',
        ]
        for pl in todo_pls:
            matches = find_act_by_pl(self.acts, pl)
            for act in matches:
                if act.get('files_changed') == []:
                    with self.subTest(name=act['name'], pl=pl):
                        self.assertTrue(
                            act.get('sections_expected'),
                            f"{act['name']} has empty files_changed but "
                            f"no sections_expected")


# ===========================================================================
# Category 1: Full snapshots ready (10 acts)
# All expected section files exist in data/act-snapshots/
# ===========================================================================

class TestFullSnapshotsReady(unittest.TestCase):
    """These acts have ALL needed snapshot files in act-snapshots/ but
    still show empty files_changed in acts.json. Once wired up, each
    should produce the expected file changes."""

    FULL_SNAPSHOT_ACTS = [
        {
            'pl': '108-446',
            'name': 'Individuals with Disabilities Education Improvement Act of 2004',
            'dir_fragment': 'individuals-with-disabilities-education-improvement',
            'expected_sections': ['121'],
        },
        {
            'pl': '108-482',
            'name': 'Intellectual Property Protection and Courts Amendments Act of 2004',
            'dir_fragment': 'intellectual-property-protection-and-courts-amendments',
            'expected_sections': ['504'],
        },
        {
            'pl': '111-144',
            'name': 'Temporary Extension Act of 2010',
            'dir_fragment': 'temporary-extension-act-of-2010',
            'expected_sections': ['119'],
        },
        {
            'pl': '111-157',
            'name': 'Continuing Extension Act of 2010',
            'dir_fragment': 'continuing-extension-act-of-2010',
            'expected_sections': ['119'],
        },
        {
            'pl': '116-94',
            'name': 'Library of Congress Technical Corrections Act of 2019',
            'dir_fragment': 'library-of-congress-technical-corrections',
            'expected_sections': ['101', '701', '802', '803'],
        },
        {
            'pl': '117-263',
            'name': 'James M. Inhofe NDAA for FY2023',
            'dir_fragment': 'james-m-inhofe-national-defense-authorization',
            'expected_sections': ['105'],
        },
        {
            'pl': '118-159',
            'name': 'NDAA for FY2025',
            'dir_fragment': 'servicemember-quality-of-life-improvement',
            'expected_sections': ['105'],
        },
        {
            'pl': '119-60',
            'name': 'NDAA for FY2026',
            'dir_fragment': 'national-defense-authorization-act-for-fiscal-year-2026',
            'expected_sections': ['105'],
        },
    ]

    def test_snapshot_dirs_exist(self):
        """Each full-snapshot-ready act must have an act-snapshot directory."""
        for act in self.FULL_SNAPSHOT_ACTS:
            with self.subTest(name=act['name']):
                dirpath = find_act_snapshot_dir(act['dir_fragment'])
                self.assertIsNotNone(
                    dirpath,
                    f"No act-snapshot dir found for '{act['name']}' "
                    f"(searched for '{act['dir_fragment']}')")

    def test_all_expected_sections_present(self):
        """Each full-snapshot-ready act should have all expected section
        .md files in its act-snapshot directory."""
        for act in self.FULL_SNAPSHOT_ACTS:
            dirpath = find_act_snapshot_dir(act['dir_fragment'])
            if dirpath is None:
                continue
            actual_files = [f.replace('.md', '') for f in os.listdir(dirpath)
                            if f.endswith('.md')]
            for sec in act['expected_sections']:
                with self.subTest(name=act['name'], section=sec):
                    self.assertIn(
                        sec, actual_files,
                        f"{act['name']}: missing {sec}.md in "
                        f"act-snapshots dir")

    def test_snapshot_files_have_content(self):
        """Each section file in the snapshot should have real content."""
        for act in self.FULL_SNAPSHOT_ACTS:
            dirpath = find_act_snapshot_dir(act['dir_fragment'])
            if dirpath is None:
                continue
            for sec in act['expected_sections']:
                fpath = os.path.join(dirpath, f'{sec}.md')
                if not os.path.exists(fpath):
                    continue
                with self.subTest(name=act['name'], section=sec):
                    with open(fpath) as f:
                        content = f.read()
                    self.assertGreater(
                        len(content.strip()), 50,
                        f"{act['name']} §{sec}: snapshot file is too short "
                        f"({len(content.strip())} chars)")

    def test_files_changed_should_be_populated(self):
        """Once fixed, files_changed in acts.json should list the expected
        section files (as 'sections/NNN.md' paths)."""
        acts = load_acts()
        for act_spec in self.FULL_SNAPSHOT_ACTS:
            matches = find_act_by_pl(acts, act_spec['pl'])
            for act in matches:
                if act.get('files_changed') != []:
                    continue
                with self.subTest(name=act['name']):
                    expected_files = [f"sections/{s}.md"
                                      for s in act_spec['expected_sections']]
                    self.assertNotEqual(
                        act.get('files_changed'), [],
                        f"{act['name']} (PL {act_spec['pl']}): "
                        f"files_changed is still empty — expected "
                        f"{expected_files}")


# ===========================================================================
# Category 2: Partial snapshots — missing §101 reconstruction (11 acts)
# ===========================================================================

class TestMissingSection101(unittest.TestCase):
    """These acts need §101 (Definitions) snapshot reconstruction.
    Each has some section snapshots but is missing §101.md."""

    ACTS_MISSING_101 = [
        {
            'pl': '101-319',
            'name': 'Copyright Royalty Tribunal Reform and Miscellaneous Pay Act of 1989',
            'dir_fragment': 'copyright-royalty-tribunal-reform-and-miscellaneous-pay',
            'has_sections': ['701'],
            'missing_sections': ['101', '802'],
        },
        {
            'pl': '102-64',
            'name': 'Semiconductor International Protection Extension Act of 1991',
            'dir_fragment': 'semiconductor-international-protection-extension',
            'has_sections': ['914'],
            'missing_sections': ['101'],
        },
        {
            'pl': '103-369',
            'name': 'Satellite Home Viewer Act of 1994',
            'dir_fragment': 'satellite-home-viewer-act-of-1994',
            'has_sections': ['111', '119'],
            'missing_sections': ['101'],
        },
        {
            'pl': '106-160',
            'name': 'Digital Theft Deterrence and Copyright Damages Improvement Act of 1999',
            'dir_fragment': 'digital-theft-deterrence',
            'has_sections': ['504'],
            'missing_sections': ['101'],
        },
        {
            'pl': '107-321',
            'name': 'Small Webcaster Amendments Act of 2002',
            'dir_fragment': 'small-webcaster-amendments',
            'has_sections': ['114'],
            'missing_sections': ['101'],
        },
        {
            'pl': '110-434',
            'name': 'Vessel Hull Design Protection Amendments of 2008',
            'dir_fragment': 'vessel-hull-design-protection',
            'has_sections': ['1301'],
            'missing_sections': ['101'],
        },
        {
            'pl': '110-435',
            'name': 'Webcaster Settlement Act of 2008',
            'dir_fragment': 'webcaster-settlement-act-of-2008',
            'has_sections': ['114'],
            'missing_sections': ['101'],
        },
        {
            'pl': '111-36',
            'name': 'Webcaster Settlement Act of 2009',
            'dir_fragment': 'webcaster-settlement-act-of-2009',
            'has_sections': ['114'],
            'missing_sections': ['101'],
        },
        {
            'pl': '111-151',
            'name': 'Satellite Television Extension Act of 2010',
            'dir_fragment': 'satellite-television-extension-act-of-2010',
            'has_sections': ['119'],
            'missing_sections': ['101'],
        },
        {
            'pl': '115-261',
            'name': 'Marrakesh Treaty Implementation Act of 2018',
            'dir_fragment': 'marrakesh-treaty-implementation',
            'has_sections': ['121'],
            'missing_sections': ['101'],
        },
        {
            'pl': '117-201',
            'name': 'Artistic Recognition for Talented Students Act of 2022',
            'dir_fragment': 'artistic-recognition-for-talented-students',
            'has_sections': ['708'],
            'missing_sections': ['101'],
        },
    ]

    def test_existing_sections_present(self):
        """Verify that the sections we already have are still in the
        act-snapshot directory."""
        for act in self.ACTS_MISSING_101:
            dirpath = find_act_snapshot_dir(act['dir_fragment'])
            if dirpath is None:
                continue
            actual = [f.replace('.md', '') for f in os.listdir(dirpath)
                      if f.endswith('.md')]
            for sec in act['has_sections']:
                with self.subTest(name=act['name'], section=sec):
                    self.assertIn(
                        sec, actual,
                        f"{act['name']}: expected {sec}.md in snapshot dir")

    def test_missing_sections_should_exist(self):
        """Each missing section .md file should be created in the
        act-snapshot directory."""
        for act in self.ACTS_MISSING_101:
            dirpath = find_act_snapshot_dir(act['dir_fragment'])
            if dirpath is None:
                continue
            actual = [f.replace('.md', '') for f in os.listdir(dirpath)
                      if f.endswith('.md')]
            for sec in act['missing_sections']:
                with self.subTest(name=act['name'], section=sec):
                    self.assertIn(
                        sec, actual,
                        f"{act['name']}: missing {sec}.md — needs "
                        f"reconstruction")

    def test_section_101_versions_exist(self):
        """§101 (Definitions) should have a versions.json snapshot file,
        since many acts modify the definitions section."""
        path = os.path.join(SNAPSHOTS_DIR, '101-versions.json')
        self.assertTrue(os.path.exists(path),
                        "§101 versions.json doesn't exist — needed as "
                        "source for §101 reconstruction")

    def test_section_101_has_enough_versions(self):
        """§101 is modified by ~20 acts. The version chain should reflect
        all of these amendments."""
        data = load_versions('101')
        versions = data['versions']
        # There are at least 11 acts in our TODO that modify §101
        # plus many more not in TODO. Should have substantial version count.
        non_current = [v for v in versions
                       if v.get('act') != 'Current'
                       and v.get('date') != 'current']
        self.assertGreaterEqual(
            len(non_current), 10,
            f"§101 has only {len(non_current)} non-current versions — "
            f"expected 10+ given the number of amending acts")


# ===========================================================================
# Category 3: Partial snapshots — other missing sections
# ===========================================================================

class TestTEACHActMissingSection802(unittest.TestCase):
    """The TEACH Act (PL 107-273 Div C Title III Subtitle C) has 12 section
    snapshots but is missing §802."""

    def setUp(self):
        self.dir = find_act_snapshot_dir(
            'technology-education-and-copyright-harmonization')

    def test_teach_snapshot_dir_exists(self):
        """TEACH Act should have an act-snapshot directory."""
        self.assertIsNotNone(self.dir,
                             "TEACH Act snapshot directory not found")

    def test_teach_has_12_existing_sections(self):
        """TEACH Act should have 12 section files already."""
        if self.dir is None:
            self.skipTest("No TEACH dir")
        files = [f for f in os.listdir(self.dir) if f.endswith('.md')]
        self.assertGreaterEqual(
            len(files), 12,
            f"TEACH Act has {len(files)} sections, expected 12+")

    def test_teach_existing_sections_correct(self):
        """Verify the 12 existing sections are the expected ones."""
        if self.dir is None:
            self.skipTest("No TEACH dir")
        expected = ['101', '106', '110', '112', '118', '119',
                    '121', '122', '203', '304', '501', '511']
        actual = [f.replace('.md', '') for f in os.listdir(self.dir)
                  if f.endswith('.md')]
        for sec in expected:
            with self.subTest(section=sec):
                self.assertIn(sec, actual)

    def test_teach_missing_section_802(self):
        """TEACH Act is missing §802.md — it should be created."""
        if self.dir is None:
            self.skipTest("No TEACH dir")
        fpath = os.path.join(self.dir, '802.md')
        self.assertTrue(
            os.path.exists(fpath),
            "TEACH Act snapshot is missing §802.md")

    def test_teach_sections_expected_includes_802(self):
        """acts.json sections_expected for TEACH should include §802."""
        acts = load_acts()
        teach = [a for a in acts if 'TEACH' in a.get('name', '')]
        self.assertTrue(teach, "TEACH Act not found in acts.json")
        for act in teach:
            with self.subTest(name=act['name']):
                self.assertIn(
                    '802', act.get('sections_expected', []),
                    f"TEACH Act sections_expected should include §802")


class TestFairnessInMusicLicensingAct(unittest.TestCase):
    """Fairness in Music Licensing Act of 1998 (PL 105-298 Title II) has
    snapshot files for §101, §110, §504, §513. The sections_expected in
    acts.json was wrong (included CTEA Title I sections) but has been
    corrected to ['101', '110', '504', '513']."""

    def setUp(self):
        self.dir = find_act_snapshot_dir('fairness-in-music-licensing')
        self.acts = load_acts()
        self.act = None
        for a in self.acts:
            if 'Fairness in Music' in a.get('name', ''):
                self.act = a
                break

    def test_fairness_snapshot_dir_exists(self):
        """Fairness in Music Licensing Act should have a snapshot dir."""
        self.assertIsNotNone(self.dir,
                             "Fairness in Music snapshot dir not found")

    def test_fairness_has_correct_sections(self):
        """Should have §101, §110, §504, §513."""
        if self.dir is None:
            self.skipTest("No dir")
        expected = ['101', '110', '504', '513']
        actual = [f.replace('.md', '') for f in os.listdir(self.dir)
                  if f.endswith('.md')]
        for sec in expected:
            with self.subTest(section=sec):
                self.assertIn(sec, actual)

    def test_fairness_sections_expected_correct(self):
        """sections_expected should be ['101', '110', '504', '513'],
        NOT the CTEA Title I sections (108, 203, 301, 302, 303, 304)."""
        self.assertIsNotNone(self.act, "Act not found in acts.json")
        expected = sorted(['101', '110', '504', '513'])
        actual = sorted(self.act.get('sections_expected', []))
        self.assertEqual(
            actual, expected,
            f"Fairness in Music Licensing sections_expected is "
            f"{actual}, should be {expected} (not CTEA sections)")

    def test_fairness_no_ctea_sections(self):
        """sections_expected must NOT include CTEA Title I sections
        (108, 203, 301, 302, 303, 304) — those belong to the Sonny Bono
        CTEA, not the Fairness in Music Licensing Act."""
        self.assertIsNotNone(self.act, "Act not found in acts.json")
        ctea_sections = ['108', '203', '301', '302', '303', '304']
        for sec in ctea_sections:
            with self.subTest(section=sec):
                self.assertNotIn(
                    sec, self.act.get('sections_expected', []),
                    f"§{sec} is a CTEA section, not a Fairness Act section")

    def test_fairness_files_changed_should_be_populated(self):
        """Once fixed, files_changed should list the 4 sections."""
        self.assertIsNotNone(self.act, "Act not found in acts.json")
        expected_files = ['sections/101.md', 'sections/110.md',
                          'sections/504.md', 'sections/513.md']
        self.assertNotEqual(
            self.act.get('files_changed'), [],
            f"Fairness in Music Licensing files_changed is still empty — "
            f"expected {expected_files}")


# ===========================================================================
# §119 Intermediate Version Differentiation (Remaining TODO)
# ===========================================================================

class TestSection119IntermediateVersions(unittest.TestCase):
    """Pre-STELA §119 versions v0-v11 currently all use the same 2009-era
    base text. Intermediate differences from the Satellite Home Viewer Act
    of 1994 and other acts should produce distinct versions."""

    def setUp(self):
        self.data = load_versions('119')
        self.versions = self.data['versions']

    def _pre_stela_versions(self):
        """Return all pre-STELA (pre-PL 111-175) versions."""
        pre = []
        for v in self.versions:
            if v.get('public_law') == '111-175':
                break
            if v.get('act') == 'Current':
                break
            pre.append(v)
        return pre

    def test_pre_stela_versions_exist(self):
        """There should be multiple pre-STELA versions of §119."""
        pre = self._pre_stela_versions()
        self.assertGreaterEqual(
            len(pre), 5,
            f"Expected 5+ pre-STELA §119 versions, got {len(pre)}")

    def test_pre_stela_not_all_identical(self):
        """Pre-STELA versions should NOT all have identical text.
        Currently they do (all use 2009-era base text) — this test
        verifies that intermediate amendments have been applied."""
        pre = self._pre_stela_versions()
        if len(pre) < 2:
            self.skipTest("Too few pre-STELA versions")
        texts = [v.get('text', '') for v in pre]
        unique = len(set(t for t in texts if t))
        self.assertGreater(
            unique, 1,
            f"All {len(pre)} pre-STELA §119 versions have identical text — "
            f"intermediate amendments not yet applied")

    def test_satellite_home_viewer_1994_distinct(self):
        """PL 103-369 (Satellite Home Viewer Act of 1994) should produce
        a §119 version distinct from adjacent versions."""
        for i, v in enumerate(self.versions):
            if v.get('public_law') == '103-369':
                if i > 0:
                    self.assertNotEqual(
                        v.get('text', ''),
                        self.versions[i - 1].get('text', ''),
                        "§119 PL 103-369 version is identical to prior")
                break

    def test_earlier_amendments_produce_changes(self):
        """Each of these PLs should produce a distinct §119 version:
        103-198, 105-80, 106-44, 106-113, 107-273, 108-419,
        108-447, 109-303, 110-403"""
        target_pls = ['103-198', '105-80', '106-44', '106-113', '107-273',
                      '108-419', '108-447', '109-303', '110-403']
        identical_to_prior = []
        for i, v in enumerate(self.versions):
            pl = v.get('public_law', '')
            pl_base = re.sub(r',\s*.*$', '', pl)
            if pl_base in target_pls and i > 0:
                if v.get('text', '') == self.versions[i - 1].get('text', ''):
                    identical_to_prior.append(pl_base)
        # Some may legitimately be identical if the §119 change was minimal,
        # but ALL being identical means no reconstruction was done
        self.assertLess(
            len(identical_to_prior), len(target_pls),
            f"All listed PLs produce versions identical to their prior: "
            f"{identical_to_prior}")


# ===========================================================================
# §111 Intermediate Version Differentiation (Remaining TODO)
# ===========================================================================

class TestSection111IntermediateVersions(unittest.TestCase):
    """§111 v0-v3 are currently identical. Changes from PL 100-667,
    101-318, 103-198 should produce distinct versions."""

    def setUp(self):
        self.data = load_versions('111')
        self.versions = self.data['versions']

    def test_v0_through_v3_not_all_identical(self):
        """The first 4 versions of §111 should not all be identical.
        Currently v0==v1==v2==v3 per TODO.md."""
        if len(self.versions) < 4:
            self.skipTest("§111 has fewer than 4 versions")
        texts = [self.versions[i].get('text', '') for i in range(4)]
        unique = len(set(t for t in texts if t))
        self.assertGreater(
            unique, 1,
            "§111 v0-v3 are all identical — PL 100-667, 101-318, "
            "103-198 changes not yet applied")

    def test_pl_100_667_distinct(self):
        """PL 100-667 (1988 Satellite Home Viewer Act) should produce
        a §111 version distinct from v0."""
        for i, v in enumerate(self.versions):
            pl = v.get('public_law', '')
            if '100-667' in pl and i > 0:
                self.assertNotEqual(
                    v.get('text', ''),
                    self.versions[i - 1].get('text', ''),
                    "§111 PL 100-667 version is identical to prior — "
                    "reconstruction not applied")
                break

    def test_pl_101_318_distinct(self):
        """PL 101-318 (1990) should produce a distinct §111 version."""
        for i, v in enumerate(self.versions):
            pl = v.get('public_law', '')
            if '101-318' in pl and i > 0:
                self.assertNotEqual(
                    v.get('text', ''),
                    self.versions[i - 1].get('text', ''),
                    "§111 PL 101-318 version is identical to prior — "
                    "reconstruction not applied")
                break

    def test_pl_103_198_distinct(self):
        """PL 103-198 (Copyright Royalty Tribunal Reform Act 1993) should
        produce a distinct §111 version (CRT -> LoC transition)."""
        for i, v in enumerate(self.versions):
            pl = v.get('public_law', '')
            if '103-198' in pl and i > 0:
                self.assertNotEqual(
                    v.get('text', ''),
                    self.versions[i - 1].get('text', ''),
                    "§111 PL 103-198 version is identical to prior — "
                    "CRT/LoC transition not applied")
                break


# ===========================================================================
# Snapshot content quality for acts with full snapshots ready
# ===========================================================================

class TestSnapshotContentQuality(unittest.TestCase):
    """Verify that act-snapshot files contain authentic statute text,
    not stubs or placeholders."""

    SPOT_CHECKS = [
        # (dir_fragment, section, must_contain_text)
        ('individuals-with-disabilities-education-improvement',
         '121', 'reproduction'),
        ('intellectual-property-protection-and-courts-amendments',
         '504', 'statutory damages'),
        ('unlocking-consumer-choice',
         '1201', 'circumvent'),
        ('james-m-inhofe-national-defense-authorization',
         '105', 'united states government'),
        ('library-of-congress-technical-corrections',
         '701', 'copyright office'),
        ('protecting-lawful-streaming',
         '1501', None),  # just check existence and length
        ('temporary-extension-act-of-2010',
         '119', 'satellite'),
        ('continuing-extension-act-of-2010',
         '119', 'satellite'),
    ]

    def test_snapshot_content_spot_checks(self):
        """Each snapshot file should contain expected legal terminology."""
        for dir_frag, sec, must_contain in self.SPOT_CHECKS:
            dirpath = find_act_snapshot_dir(dir_frag)
            if dirpath is None:
                continue
            fpath = os.path.join(dirpath, f'{sec}.md')
            if not os.path.exists(fpath):
                continue
            with open(fpath) as f:
                content = f.read()
            with self.subTest(dir=dir_frag, section=sec):
                self.assertGreater(
                    len(content.strip()), 100,
                    f"Snapshot {dir_frag}/{sec}.md is too short")
                if must_contain:
                    self.assertIn(
                        must_contain, content.lower(),
                        f"Snapshot {dir_frag}/{sec}.md should contain "
                        f"'{must_contain}'")


if __name__ == '__main__':
    unittest.main()
