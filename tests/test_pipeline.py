#!/usr/bin/env python3
"""
Unit tests for the pipeline scripts: reconstruct.py, prepare_build_data.py,
and build.py.

Tests the core functions that power the version reconstruction pipeline,
including amendment reversal, text parsing, metadata extraction, and
filename sanitization. These tests run without needing the output repo.

Usage:
    python3 -m unittest tests/test_pipeline.py -v
"""

import json
import os
import re
import sys
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from reconstruct import (
    reverse_amendment,
    apply_simple_substitution,
    parse_amendment_notes,
    load_section_text,
)
from prepare_build_data import strip_source_credit, sanitize_filename, load_acts
from build import parse_acts, make_commit_message


# ===========================================================================
# reconstruct.py: reverse_amendment
# ===========================================================================

class TestReverseAmendmentSubstitution(unittest.TestCase):
    """Test the substitution reversal pattern."""

    def test_simple_substitution(self):
        """'substituted "X" for "Y"' should replace X with Y."""
        text = "the term is 70 years"
        desc = 'substituted "70" for "fifty"'
        result, success, _ = reverse_amendment(text, desc)
        self.assertTrue(success)
        self.assertIn('fifty', result)
        self.assertNotIn('70', result)

    def test_substitution_not_found(self):
        """If the new text isn't found, reversal should note the miss."""
        text = "the term is fifty years"
        desc = 'substituted "70" for "fifty"'
        result, success, method = reverse_amendment(text, desc)
        # "70" not in text, so it can't reverse
        self.assertFalse(success)

    def test_substitution_with_smart_quotes(self):
        """Should handle smart/curly quotes in descriptions."""
        text = "the term is 70 years"
        desc = 'substituted \u201c70\u201d for \u201cfifty\u201d'
        result, success, _ = reverse_amendment(text, desc)
        self.assertTrue(success)
        self.assertIn('fifty', result)

    def test_multiple_substitutions(self):
        """Multiple substitutions in one description via |||."""
        text = "95 years from publication or 120 years from creation"
        desc = ('substituted "95" for "seventy-five" ||| '
                'substituted "120" for "one hundred"')
        result, success, _ = reverse_amendment(text, desc)
        self.assertTrue(success)
        self.assertIn('seventy-five', result)
        self.assertIn('one hundred', result)

    def test_wherever_appearing(self):
        """'wherever appearing' should replace all occurrences."""
        text = "foo bar foo baz foo"
        desc = 'substituted "foo" for "qux" wherever appearing'
        result, success, _ = reverse_amendment(text, desc)
        self.assertTrue(success)
        self.assertEqual(result.count('qux'), 3)
        self.assertNotIn('foo', result)


class TestReverseAmendmentInsertion(unittest.TestCase):
    """Test the insertion reversal pattern."""

    def test_simple_insertion(self):
        """'inserted "X"' should remove X from text."""
        text = "in writing and signed by the owner"
        desc = 'inserted "and signed "'
        result, success, _ = reverse_amendment(text, desc)
        self.assertTrue(success)
        self.assertNotIn('and signed', result)

    def test_insertion_not_found(self):
        """If inserted text isn't in the current text, should fail."""
        text = "completely different text"
        desc = 'inserted "special phrase"'
        result, success, _ = reverse_amendment(text, desc)
        self.assertFalse(success)


class TestReverseAmendmentStruckInserted(unittest.TestCase):
    """Test the 'struck X and inserted Y' pattern."""

    def test_struck_and_inserted(self):
        """'struck "X" and inserted "Y"' should replace Y with X."""
        text = "shall may be placed"
        desc = 'struck "shall" and inserted "may"'
        result, success, _ = reverse_amendment(text, desc)
        self.assertTrue(success)
        self.assertIn('shall', result)
        self.assertNotIn('may', result)


class TestReverseAmendmentSkips(unittest.TestCase):
    """Test that non-substantive amendments are properly skipped."""

    def test_effective_date_skipped(self):
        """Effective date notes should be skipped, not treated as failures."""
        text = "unchanged text"
        desc = 'Effective Date of 1990 Amendment set out as a note under section 101'
        result, success, method = reverse_amendment(text, desc)
        self.assertTrue(success, f"Effective date should be skipped: {method}")
        self.assertEqual(result, text)

    def test_transition_provisions_skipped(self):
        """Transition provisions should be skipped."""
        text = "unchanged text"
        desc = 'Transition provisions set out as note under section 101'
        result, success, _ = reverse_amendment(text, desc)
        self.assertTrue(success)


class TestReverseAmendmentManualCases(unittest.TestCase):
    """Test that complex amendments are flagged for manual review."""

    def test_added_paragraph_flagged(self):
        """'added par. (X)' should be flagged as needing manual work."""
        text = "text with (8) architectural works"
        desc = 'added par. (8)'
        result, success, method = reverse_amendment(text, desc)
        self.assertFalse(success)
        self.assertIn('MANUAL', method)

    def test_added_subsection_flagged(self):
        """'added subsec. (d)' should be flagged."""
        text = "text with subsection (d)"
        desc = 'added subsec. (d)'
        result, success, method = reverse_amendment(text, desc)
        self.assertFalse(success)
        self.assertIn('MANUAL', method)


# ===========================================================================
# reconstruct.py: apply_simple_substitution
# ===========================================================================

class TestApplySimpleSubstitution(unittest.TestCase):
    """Test the text substitution helper."""

    def test_basic_substitution(self):
        result = apply_simple_substitution("hello world", "world", "there")
        self.assertEqual(result, "hello there")

    def test_not_found_returns_none(self):
        result = apply_simple_substitution("hello world", "missing", "there")
        self.assertIsNone(result)

    def test_replace_first_only(self):
        result = apply_simple_substitution("aaa", "a", "b", replace_all=False)
        self.assertEqual(result, "baa")

    def test_replace_all(self):
        result = apply_simple_substitution("aaa", "a", "b", replace_all=True)
        self.assertEqual(result, "bbb")


# ===========================================================================
# reconstruct.py: parse_amendment_notes
# ===========================================================================

class TestParseAmendmentNotes(unittest.TestCase):
    """Test the amendment notes parser."""

    def test_parse_real_section(self):
        """Should parse amendment notes for a real section."""
        notes = parse_amendment_notes('302')
        self.assertIsInstance(notes, list)
        self.assertGreater(len(notes), 0,
                           "Section 302 should have amendment notes")

    def test_parsed_amendments_have_year(self):
        """Each parsed amendment should have a year."""
        notes = parse_amendment_notes('302')
        for note in notes:
            self.assertIn('year', note)
            self.assertTrue(note['year'].isdigit())

    def test_parsed_amendments_have_pl(self):
        """Each parsed amendment should have a public_law."""
        notes = parse_amendment_notes('302')
        for note in notes:
            self.assertIn('public_law', note)
            self.assertTrue(
                re.match(r'\d+-\d+', note['public_law']),
                f"Bad PL format: {note['public_law']}")

    def test_parsed_amendments_have_description(self):
        """Each parsed amendment should have a description."""
        notes = parse_amendment_notes('302')
        for note in notes:
            self.assertIn('description', note)
            self.assertGreater(len(note['description']), 5)

    def test_nonexistent_section_returns_empty(self):
        """A nonexistent section should return an empty list."""
        notes = parse_amendment_notes('99999')
        self.assertEqual(notes, [])

    def test_section_107_few_amendments(self):
        """Section 107 (fair use) should have very few amendments."""
        notes = parse_amendment_notes('107')
        self.assertLessEqual(len(notes), 4,
                             "Section 107 should have few amendments")


# ===========================================================================
# prepare_build_data.py: strip_source_credit
# ===========================================================================

class TestStripSourceCredit(unittest.TestCase):
    """Test the source credit stripping function."""

    def test_strips_pub_l_block(self):
        text = "Section text here.\n(\nPub. L. 94-553, Oct. 19, 1976, 90 Stat. 2541\n)"
        result = strip_source_credit(text)
        self.assertNotIn('Pub. L.', result)
        self.assertIn('Section text here.', result)

    def test_preserves_text_without_credits(self):
        text = "Just regular section text with no credits."
        result = strip_source_credit(text)
        self.assertEqual(result.strip(), text.strip())

    def test_preserves_subsection_parens(self):
        text = "(a) This is subsection a.\n(b) This is subsection b."
        result = strip_source_credit(text)
        self.assertIn('(a)', result)
        self.assertIn('(b)', result)


# ===========================================================================
# prepare_build_data.py and build.py: sanitize_filename
# ===========================================================================

class TestSanitizeFilename(unittest.TestCase):
    """Test filename sanitization for act directory names."""

    def test_simple_name(self):
        result = sanitize_filename("Copyright Act of 1976")
        self.assertEqual(result, "copyright-act-of-1976")

    def test_removes_parenthetical(self):
        result = sanitize_filename("Some Act (Public Law 100-100)")
        self.assertNotIn('(', result)
        self.assertNotIn(')', result)

    def test_truncation(self):
        """Long names should be truncated to 60 chars."""
        long_name = "A Very Long Act Name That Goes On And On And Never Seems To Stop At All Ever"
        result = sanitize_filename(long_name)
        self.assertLessEqual(len(result), 60)

    def test_no_special_chars(self):
        result = sanitize_filename("Act: With Special & Chars!")
        self.assertFalse(
            any(c in result for c in ':&!'),
            f"Result has special chars: {result}")

    def test_lowercase(self):
        result = sanitize_filename("DMCA Safe Harbors")
        self.assertEqual(result, result.lower())


# ===========================================================================
# build.py: parse_acts
# ===========================================================================

class TestParseActs(unittest.TestCase):
    """Test the acts.yaml parser in build.py."""

    @classmethod
    def setUpClass(cls):
        yaml_path = os.path.join(PROJECT_ROOT, 'metadata', 'acts.yaml')
        cls.acts = parse_acts(yaml_path)

    def test_parses_many_acts(self):
        self.assertGreaterEqual(len(self.acts), 100)

    def test_acts_have_required_fields(self):
        for act in self.acts:
            self.assertIn('name', act)
            self.assertIn('date', act)

    def test_acts_sorted_by_date(self):
        dates = [a['date'] for a in self.acts]
        self.assertEqual(dates, sorted(dates))

    def test_1976_act_present(self):
        names = [a['name'] for a in self.acts]
        self.assertIn('Copyright Act of 1976', names)

    def test_acts_have_summaries(self):
        """Most acts should have summaries."""
        with_summary = sum(1 for a in self.acts if a.get('summary'))
        self.assertGreater(with_summary / len(self.acts), 0.8)


# ===========================================================================
# build.py: make_commit_message
# ===========================================================================

class TestMakeCommitMessage(unittest.TestCase):
    """Test commit message generation."""

    def test_basic_message(self):
        act = {
            'name': 'Test Act of 2020',
            'date': '2020-01-01',
            'public_law': 'Pub. L. 116-100',
            'citation': '134 Stat. 1234',
            'chapter': None,
            'effective_date': '2020-03-01',
            'summary': 'A test act.',
        }
        msg = make_commit_message(act)
        self.assertIn('Test Act of 2020', msg)
        self.assertIn('Pub. L. 116-100', msg)
        self.assertIn('134 Stat. 1234', msg)
        self.assertIn('2020-03-01', msg)
        self.assertIn('A test act.', msg)

    def test_message_first_line_is_name(self):
        act = {
            'name': 'Copyright Act of 1976',
            'date': '1976-10-19',
            'public_law': None,
            'citation': None,
            'chapter': None,
            'effective_date': None,
            'summary': 'Major revision.',
        }
        msg = make_commit_message(act)
        first_line = msg.split('\n')[0]
        self.assertEqual(first_line, 'Copyright Act of 1976')


# ===========================================================================
# reconstruct.py: load_section_text
# ===========================================================================

class TestLoadSectionText(unittest.TestCase):
    """Test loading and stripping section text."""

    def test_loads_existing_section(self):
        text = load_section_text('107')
        self.assertIsNotNone(text)
        self.assertIn('fair use', text.lower())

    def test_strips_header(self):
        """The '# 17 U.S.C.' header should be removed."""
        text = load_section_text('107')
        self.assertNotIn('# 17 U.S.C.', text)

    def test_returns_fair_use_content(self):
        """Section 107 text should contain fair use language."""
        text = load_section_text('107')
        self.assertIn('fair use', text.lower())

    def test_nonexistent_section(self):
        text = load_section_text('99999')
        self.assertIsNone(text)

    def test_loaded_text_non_empty(self):
        text = load_section_text('102')
        self.assertIsNotNone(text)
        self.assertGreater(len(text.strip()), 50)


# ===========================================================================
# Integration: full reconstruction round-trip
# ===========================================================================

class TestReconstructionIntegrity(unittest.TestCase):
    """Integration tests verifying the full reconstruction pipeline."""

    def test_reconstruct_produces_valid_output(self):
        """Running reconstruct on a real section should produce valid data."""
        from reconstruct import reconstruct_section
        result = reconstruct_section('305')
        self.assertIsNotNone(result)
        self.assertIn('section', result)
        self.assertIn('versions', result)
        self.assertIn('issues', result)

    def test_reconstruct_produces_multiple_versions(self):
        """A section with amendments should produce multiple versions."""
        from reconstruct import reconstruct_section
        result = reconstruct_section('302')
        self.assertIsNotNone(result)
        self.assertGreaterEqual(len(result['versions']), 2)

    def test_reconstruct_versions_have_text(self):
        """All reconstructed versions should have non-empty text."""
        from reconstruct import reconstruct_section
        result = reconstruct_section('302')
        for i, v in enumerate(result['versions']):
            self.assertTrue(len(v.get('text', '').strip()) > 0,
                            f"Version {i} has empty text")


if __name__ == '__main__':
    unittest.main()
