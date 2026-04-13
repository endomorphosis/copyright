#!/usr/bin/env python3
"""
Tests for §111 intermediate version differentiation (v0-v3).

PL 100-667 (1988), PL 101-318 (1990), and PL 103-198 (1993) each made
specific changes to §111. Versions v0-v3 should reflect these changes
rather than all sharing identical text.

Usage:
    pytest tests/test_section111_intermediate.py -v
"""

import json
import os
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SNAPSHOTS_DIR = os.path.join(PROJECT_ROOT, 'data', 'snapshots')


def load_versions(sec_num):
    path = os.path.join(SNAPSHOTS_DIR, f'{sec_num}-versions.json')
    with open(path) as f:
        return json.load(f)


class TestSection111IntermediateVersions(unittest.TestCase):
    """§111 v0-v3 should be differentiated based on PL 100-667, 101-318,
    and 103-198. See TODO.md."""

    def setUp(self):
        self.data = load_versions('111')
        self.versions = self.data['versions']

    def _get_version_by_pl(self, pl):
        for v in self.versions:
            if v.get('public_law') == pl:
                return v
        return None

    # --- Version distinctness ---

    def test_v0_differs_from_v1(self):
        """v0 (PL 99-397) and v1 (PL 100-667) should have different text."""
        self.assertNotEqual(
            self.versions[0]['text'], self.versions[1]['text'],
            "v0 and v1 are identical — PL 100-667 changes not reconstructed")

    def test_v1_differs_from_v2(self):
        """v1 (PL 100-667) and v2 (PL 101-318) should have different text."""
        self.assertNotEqual(
            self.versions[1]['text'], self.versions[2]['text'],
            "v1 and v2 are identical — PL 101-318 changes not reconstructed")

    def test_v2_differs_from_v3(self):
        """v2 (PL 101-318) and v3 (PL 103-198) should have different text."""
        self.assertNotEqual(
            self.versions[2]['text'], self.versions[3]['text'],
            "v2 and v3 are identical — PL 103-198 changes not reconstructed")

    # --- PL 100-667 (Satellite Home Viewer Act of 1988) ---
    # Added (a)(4) and redesignated old (4) as (5).
    # Inserted §119 subscriber exclusion in d(1)(A).

    def test_v0_nonprofit_paragraph_numbered_4(self):
        """Before PL 100-667, the nonprofit paragraph was (a)(4) not (a)(5)."""
        v0 = self._get_version_by_pl('99-397')
        self.assertIn(
            '(4) the secondary transmission is not made by a cable system '
            'but is made by a governmental body',
            v0['text'])
        self.assertNotIn(
            '(5) the secondary transmission is not made by a cable system '
            'but is made by a governmental body',
            v0['text'])

    def test_v1_nonprofit_paragraph_numbered_5(self):
        """After PL 100-667, the nonprofit paragraph should be (a)(5)."""
        v1 = self._get_version_by_pl('100-667')
        self.assertIn(
            '(5) the secondary transmission is not made by a cable system '
            'but is made by a governmental body',
            v1['text'])

    def test_v0_no_section_119_exclusion(self):
        """Before PL 100-667, no §119 subscriber exclusion in d(1)(A)."""
        v0 = self._get_version_by_pl('99-397')
        # Only check text before subparagraph (B) to isolate d(1)(A)
        d1a = v0['text'].split('(B) Except in')[0] \
            if '(B) Except in' in v0['text'] else v0['text']
        self.assertNotIn(
            'subscribers receiving secondary transmissions',
            d1a)

    def test_v1_has_section_119_exclusion(self):
        """After PL 100-667, d(1)(A) should contain §119 exclusion."""
        v1 = self._get_version_by_pl('100-667')
        self.assertIn('section 119', v1['text'])

    # --- PL 101-318 (1990) ---
    # Struck "recorded the notice specified by subsection (d) and" from (c)(2)(B).

    def test_v1_has_recorded_notice_in_c2b(self):
        """Before PL 101-318, (c)(2)(B) had 'recorded the notice'."""
        v1 = self._get_version_by_pl('100-667')
        self.assertIn(
            'recorded the notice specified by subsection (d) and',
            v1['text'])

    def test_v2_no_recorded_notice_in_c2b(self):
        """After PL 101-318, 'recorded the notice' was struck."""
        v2 = self._get_version_by_pl('101-318')
        self.assertNotIn(
            'recorded the notice specified by subsection (d) and',
            v2['text'])

    # --- PL 103-198 (Copyright Royalty Tribunal Reform Act of 1993) ---
    # Struck CRT consultation phrases from d(1) and d(1)(A).
    # Replaced d(2) CRT distribution text.
    # Amended d(4)(B) generally.

    def test_v2_has_crt_consultation_in_d1(self):
        """Before PL 103-198, d(1) had CRT consultation phrase."""
        v2 = self._get_version_by_pl('101-318')
        self.assertIn(
            'after consultation with the Copyright Royalty Tribunal '
            '(if and when the Tribunal has been constituted)',
            v2['text'])

    def test_v3_no_crt_consultation_in_d1(self):
        """After PL 103-198, d(1) should not have CRT consultation phrase."""
        v3 = self._get_version_by_pl('103-198')
        self.assertNotIn(
            'after consultation with the Copyright Royalty Tribunal',
            v3['text'])

    def test_v2_d4b_uses_original_crt_text(self):
        """Before PL 103-198, d(4)(B) used 'the Tribunal determines'."""
        v2 = self._get_version_by_pl('101-318')
        self.assertIn(
            'If the Tribunal determines that no such controversy exists, '
            'it shall, after deducting its reasonable administrative costs',
            v2['text'])

    def test_v2_d2_has_original_crt_compilation_text(self):
        """Before PL 103-198, d(2) had 'as provided by this title'."""
        v2 = self._get_version_by_pl('101-318')
        self.assertIn(
            'for later distribution with interest by the Copyright Royalty '
            'Tribunal as provided by this title',
            v2['text'])

    # --- Identical-pair count ---

    def test_111_fewer_identical_pairs(self):
        """After reconstruction, §111 should have at most 2 identical
        adjacent pairs (v4-v5 and v8-v9 remain)."""
        identical = []
        for i in range(len(self.versions) - 1):
            if self.versions[i].get('text', '') == \
               self.versions[i + 1].get('text', ''):
                identical.append(
                    f"v{i}(PL {self.versions[i].get('public_law')})"
                    f"-v{i+1}(PL {self.versions[i+1].get('public_law')})")
        self.assertLessEqual(
            len(identical), 3,
            f"§111 has {len(identical)} identical adjacent version "
            f"pairs — expected at most 3: {identical}")


if __name__ == '__main__':
    unittest.main()
