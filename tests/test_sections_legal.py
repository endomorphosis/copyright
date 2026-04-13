#!/usr/bin/env python3
"""
Legal accuracy tests for sections not covered by test_audit.py or
test_substantive.py.

Each test verifies a specific historical fact about a section of Title 17
against the reconstructed version chain. These tests catch errors where
auto-reversal introduced wrong text or failed to remove post-enactment
language.

Usage:
    python3 -m unittest tests/test_sections_legal.py -v
"""

import json
import os
import re
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
SNAPSHOTS_DIR = os.path.join(DATA_DIR, 'snapshots')


def load_versions(sec_num):
    path = os.path.join(SNAPSHOTS_DIR, f'{sec_num}-versions.json')
    with open(path) as f:
        return json.load(f)


def get_v0_text(sec_num):
    return load_versions(sec_num)['versions'][0]['text']


def get_current_text(sec_num):
    return load_versions(sec_num)['versions'][-1].get('text', '')


def get_version_at_year(sec_num, target_year):
    """Return the version text that was current at a given year."""
    data = load_versions(sec_num)
    versions = data['versions']
    # Find the latest version whose year <= target_year
    best = None
    for v in versions:
        y = v.get('year')
        if y and y != 'current' and int(y) <= target_year:
            best = v
    return best


# ===========================================================================
# Section 101 -- Definitions
# ===========================================================================

class TestSection101(unittest.TestCase):
    """Section 101 defines terms used throughout Title 17. It has been
    amended extensively -- more than any other section."""

    def setUp(self):
        self.data = load_versions('101')
        self.v0_text = self.data['versions'][0]['text']

    def test_many_versions(self):
        """Section 101 has been amended by dozens of acts."""
        self.assertGreaterEqual(len(self.data['versions']), 10,
                                "Section 101 should have many versions")

    def test_v0_has_definitions_heading(self):
        """Should start with 'Definitions' heading."""
        self.assertIn('Definitions', self.v0_text[:50])

    def test_v0_defines_anonymous_work(self):
        """The term 'anonymous work' was defined in the original 1976 Act."""
        self.assertIn('anonymous work', self.v0_text.lower())

    def test_v0_defines_phonorecords(self):
        """'Phonorecords' is a key defined term from the 1976 Act."""
        self.assertIn('phonorecords', self.v0_text.lower())

    def test_v0_defines_work_made_for_hire(self):
        """'Work made for hire' is a critical defined term."""
        self.assertIn('work made for hire', self.v0_text.lower())

    def test_current_defines_architectural_work(self):
        """The current version should define 'architectural work'
        (added by PL 101-650 in 1990)."""
        current = get_current_text('101')
        self.assertIn('architectural work', current.lower())

    def test_v0_defines_literary_works(self):
        """'Literary works' was defined in the original 1976 Act."""
        self.assertIn('literary works', self.v0_text.lower())

    def test_v0_defines_publication(self):
        """'Publication' is a fundamental defined term from 1976."""
        self.assertIn('publication', self.v0_text.lower())


# ===========================================================================
# Section 103 -- Compilations and derivative works
# ===========================================================================

class TestSection103(unittest.TestCase):
    """Section 103 addresses copyright in compilations and derivative works.
    It has been remarkably stable since 1976."""

    def setUp(self):
        self.text = get_v0_text('103')

    def test_v0_references_section_102(self):
        """Section 103(a) cross-references section 102."""
        self.assertIn('section 102', self.text)

    def test_v0_has_compilations(self):
        """Must address compilations."""
        self.assertIn('compilations', self.text.lower())

    def test_v0_has_derivative_works(self):
        """Must address derivative works."""
        self.assertIn('derivative works', self.text.lower())

    def test_v0_preexisting_material(self):
        """Must discuss protection limits for preexisting material."""
        self.assertIn('preexisting material', self.text)

    def test_v0_two_subsections(self):
        """Section 103 has subsections (a) and (b)."""
        self.assertIn('(a)', self.text)
        self.assertIn('(b)', self.text)

    def test_v0_no_database_protection(self):
        """Database protection was never added to Section 103
        (various bills failed). No 'database' language."""
        self.assertNotIn('database', self.text.lower())


# ===========================================================================
# Section 105 -- Government works
# ===========================================================================

class TestSection105(unittest.TestCase):
    """Section 105 addresses copyright in US Government works.
    The original 1976 Act barred copyright in government works entirely.
    A 2019 amendment added an exception for certain works."""

    def setUp(self):
        self.text = get_v0_text('105')

    def test_v0_addresses_united_states_government(self):
        """Must reference United States Government works."""
        self.assertIn('United States Government', self.text)

    def test_v0_bars_copyright_protection(self):
        """The core rule: no copyright in government works."""
        lower = self.text.lower()
        self.assertTrue(
            'not subject to copyright protection' in lower or
            'copyright protection under this title is not available' in lower,
            "Section 105 should bar copyright in government works")

    def test_current_version_has_exception(self):
        """The current version should have an exception (added 2019)."""
        current = get_current_text('105')
        # The 2019 amendment (PL 116-92) added exceptions
        self.assertGreater(len(current), len(self.text),
                           "Current §105 should be longer than v0 "
                           "(2019 amendment added exceptions)")


# ===========================================================================
# Section 108 -- Library reproduction
# ===========================================================================

class TestSection108(unittest.TestCase):
    """Section 108 allows libraries and archives to reproduce works under
    certain conditions. Extensively amended."""

    def setUp(self):
        self.text = get_v0_text('108')

    def test_v0_mentions_library(self):
        """Core provision is about libraries."""
        self.assertIn('library', self.text.lower())

    def test_v0_mentions_archives(self):
        """Also covers archives."""
        self.assertIn('archives', self.text.lower())

    def test_v0_no_more_than_one_copy(self):
        """The original limit was 'no more than one copy'."""
        self.assertIn('no more than one copy', self.text)

    def test_v0_section_106_reference(self):
        """Should cross-reference section 106 (exclusive rights)."""
        self.assertIn('section 106', self.text)

    def test_v0_not_for_commercial_advantage(self):
        """Library copying must be without commercial advantage."""
        self.assertIn('commercial advantage', self.text.lower())

    def test_v0_has_multiple_subsections(self):
        """Section 108 has many subsections covering different scenarios."""
        for sub in ['(a)', '(b)', '(c)', '(d)', '(e)']:
            self.assertIn(sub, self.text,
                          f"Section 108 should have subsection {sub}")


# ===========================================================================
# Section 202 -- Ownership vs. material object
# ===========================================================================

class TestSection202(unittest.TestCase):
    """Section 202 codifies the fundamental principle that copyright
    ownership is distinct from ownership of a physical copy."""

    def setUp(self):
        self.text = get_v0_text('202')

    def test_v0_ownership_distinct(self):
        """Core principle: copyright ownership is distinct from material object."""
        self.assertIn('distinct from ownership of any material object', self.text)

    def test_v0_transfer_of_object(self):
        """Transfer of the object does not transfer copyright."""
        lower = self.text.lower()
        self.assertTrue(
            'transfer of ownership' in lower,
            "Should discuss transfer of ownership of material object")

    def test_v0_no_subsection_markers(self):
        """Section 202 is a single continuous paragraph with no subsections."""
        self.assertNotIn('(b)', self.text)

    def test_few_versions(self):
        """Section 202 has been rarely amended."""
        data = load_versions('202')
        self.assertLessEqual(len(data['versions']), 3)


# ===========================================================================
# Section 204 -- Written transfer requirement
# ===========================================================================

class TestSection204(unittest.TestCase):
    """Section 204 requires copyright transfers to be in writing."""

    def setUp(self):
        self.text = get_v0_text('204')

    def test_v0_writing_requirement(self):
        """Transfers must be 'in writing and signed'."""
        self.assertIn('in writing and signed', self.text)

    def test_v0_operation_of_law_exception(self):
        """Exception for transfers by operation of law."""
        self.assertIn('operation of law', self.text)

    def test_v0_has_subsection_a(self):
        """Has subsection (a) with the writing requirement."""
        self.assertIn('(a)', self.text)

    def test_v0_notarization_not_required(self):
        """The statute does not require notarization."""
        self.assertNotIn('notariz', self.text.lower())


# ===========================================================================
# Section 205 -- Recordation of transfers
# ===========================================================================

class TestSection205(unittest.TestCase):
    """Section 205 governs recordation of copyright transfers."""

    def setUp(self):
        self.text = get_v0_text('205')

    def test_v0_recordation_conditions(self):
        """Should address conditions for recordation."""
        self.assertIn('Recordation', self.text)

    def test_v0_copyright_office(self):
        """Recordation is done with the Copyright Office."""
        self.assertIn('Copyright Office', self.text)

    def test_v0_constructive_notice(self):
        """Recordation provides constructive notice."""
        self.assertIn('constructive notice', self.text.lower())


# ===========================================================================
# Section 303 -- Duration of pre-1978 unpublished works
# ===========================================================================

class TestSection303(unittest.TestCase):
    """Section 303 addresses duration for works created but not published
    before January 1, 1978."""

    def setUp(self):
        self.text = get_v0_text('303')

    def test_v0_references_jan_1_1978(self):
        """Key date: January 1, 1978."""
        self.assertIn('January 1, 1978', self.text)

    def test_v0_december_31_2002(self):
        """Original minimum date was December 31, 2002."""
        self.assertIn('2002', self.text)

    def test_v0_references_section_302(self):
        """Cross-references section 302 for term calculation."""
        self.assertIn('section 302', self.text)

    def test_v0_not_in_public_domain(self):
        """Addresses works 'not theretofore in the public domain'."""
        self.assertIn('public domain', self.text.lower())


# ===========================================================================
# Section 305 -- Terminal date (year-end rule)
# ===========================================================================

class TestSection305(unittest.TestCase):
    """Section 305 provides that all copyright terms run to the end of
    the calendar year. This is the simplest section in Title 17."""

    def setUp(self):
        self.text = get_v0_text('305')

    def test_v0_calendar_year(self):
        """The year-end rule: terms run to end of calendar year."""
        self.assertIn('calendar year', self.text)

    def test_v0_references_sections_302_through_304(self):
        """Cross-references the duration sections."""
        self.assertIn('sections 302 through 304', self.text)

    def test_v0_is_concise(self):
        """Section 305 is one of the shortest sections -- single sentence."""
        # Should be well under 500 chars
        stripped = self.text.replace('\n', ' ').strip()
        # Remove source credits if present
        if '(Pub. L.' in stripped:
            stripped = stripped[:stripped.index('(Pub. L.')]
        self.assertLess(len(stripped), 500,
                        f"Section 305 should be concise, got {len(stripped)} chars")


# ===========================================================================
# Section 402 -- Notice on phonorecords
# ===========================================================================

class TestSection402(unittest.TestCase):
    """Section 402 addresses copyright notice on phonorecords of sound
    recordings. Mirrors 401 but for phonorecords."""

    def setUp(self):
        self.text = get_v0_text('402')

    def test_v0_phonorecords(self):
        """Must address phonorecords specifically."""
        self.assertIn('phonorecord', self.text.lower())

    def test_v0_sound_recordings(self):
        """Specifically about sound recordings."""
        self.assertIn('sound recording', self.text.lower())

    def test_v0_p_symbol(self):
        """The phonorecord notice uses the (P) symbol."""
        self.assertTrue(
            '\u2117' in self.text or '(P)' in self.text or 'P' in self.text,
            "Section 402 should reference the (P) symbol for phonorecords")

    def test_v0_post_berne_has_general_provisions(self):
        """After Berne (1988), heading should be 'General Provisions'
        (matching the change in Section 401)."""
        # v0 for 402 is the post-Berne version (PL 100-568)
        data = load_versions('402')
        v0 = data['versions'][0]
        if v0.get('public_law', '').startswith('100-568'):
            self.assertIn('General Provisions', self.text)


# ===========================================================================
# Section 407 -- Deposit for Library of Congress
# ===========================================================================

class TestSection407(unittest.TestCase):
    """Section 407 requires deposit of copies with the Library of Congress."""

    def setUp(self):
        self.text = get_v0_text('407')

    def test_v0_library_of_congress(self):
        """Deposit is with the Library of Congress."""
        self.assertIn('Library of Congress', self.text)

    def test_v0_deposit_requirement(self):
        """Should discuss depositing copies."""
        self.assertIn('deposit', self.text.lower())

    def test_v0_register_of_copyrights(self):
        """The Register of Copyrights administers deposits."""
        self.assertIn('Register of Copyrights', self.text)

    def test_v0_two_copies(self):
        """The standard requirement is two complete copies."""
        self.assertIn('two', self.text.lower())


# ===========================================================================
# Section 408 -- Registration in general
# ===========================================================================

class TestSection408(unittest.TestCase):
    """Section 408 governs copyright registration."""

    def setUp(self):
        self.text = get_v0_text('408')

    def test_v0_registration_permissive(self):
        """Registration is permissive (not required for copyright)."""
        self.assertIn('Registration Permissive', self.text)

    def test_v0_register_of_copyrights(self):
        """Registration is with the Register of Copyrights."""
        self.assertIn('Register of Copyrights', self.text)

    def test_v0_has_multiple_subsections(self):
        """Section 408 has multiple subsections."""
        for sub in ['(a)', '(b)', '(c)']:
            self.assertIn(sub, self.text)


# ===========================================================================
# Section 411 -- Registration and infringement actions
# ===========================================================================

class TestSection411(unittest.TestCase):
    """Section 411 generally requires registration before filing suit.
    Modified by Berne to add 106A exception."""

    def setUp(self):
        self.text = get_v0_text('411')

    def test_v0_registration_prerequisite(self):
        """No infringement suit without registration (general rule)."""
        self.assertIn('no civil action for infringement', self.text.lower())

    def test_v0_registration_reference(self):
        """Must reference registration."""
        self.assertIn('registration', self.text.lower())

    def test_v0_section_106A_reference(self):
        """Post-Berne v0 should reference 106A exception (VARA)."""
        # The earliest version is post-Berne (PL 100-568)
        data = load_versions('411')
        if data['versions'][0].get('public_law', '').startswith('100-568'):
            self.assertIn('106A', self.text)


# ===========================================================================
# Section 502 -- Injunctions
# ===========================================================================

class TestSection502(unittest.TestCase):
    """Section 502 authorizes injunctive relief for copyright infringement."""

    def setUp(self):
        self.text = get_v0_text('502')

    def test_v0_injunctions(self):
        """Core remedy: temporary and final injunctions."""
        self.assertIn('injunction', self.text.lower())

    def test_v0_temporary_and_final(self):
        """Should authorize both temporary and final injunctions."""
        self.assertIn('temporary and final', self.text.lower())

    def test_v0_prevent_or_restrain(self):
        """Injunctions to 'prevent or restrain' infringement."""
        self.assertIn('prevent or restrain', self.text)

    def test_v0_references_title_28(self):
        """Cross-references title 28 (Judiciary)."""
        self.assertIn('title 28', self.text.lower())

    def test_stable_section(self):
        """Section 502 has been rarely amended."""
        data = load_versions('502')
        self.assertLessEqual(len(data['versions']), 4)


# ===========================================================================
# Section 503 -- Impounding
# ===========================================================================

class TestSection503(unittest.TestCase):
    """Section 503 provides for impounding and disposition of infringing copies."""

    def setUp(self):
        self.text = get_v0_text('503')

    def test_v0_impounding(self):
        """Core remedy: impounding infringing articles."""
        self.assertIn('impound', self.text.lower())

    def test_v0_infringing_copies(self):
        """Should address infringing copies."""
        lower = self.text.lower()
        self.assertTrue(
            'infringing' in lower,
            "Section 503 should address infringing articles")

    def test_v0_disposition(self):
        """Should address final disposition (destruction/disposal)."""
        lower = self.text.lower()
        self.assertTrue(
            'destroy' in lower or 'dispos' in lower,
            "Section 503 should address destruction/disposition")


# ===========================================================================
# Section 601 -- Manufacturing clause
# ===========================================================================

class TestSection601(unittest.TestCase):
    """Section 601 imposed the manufacturing clause -- requiring certain
    works to be manufactured in the US. This was a protectionist measure
    that expired on July 1, 1986."""

    def setUp(self):
        self.text = get_v0_text('601')

    def test_v0_manufacture_requirement(self):
        """Should discuss manufacturing requirements."""
        self.assertIn('manufacture', self.text.lower())

    def test_v0_united_states(self):
        """Manufacturing must be in the United States."""
        self.assertIn('United States', self.text)

    def test_v0_nondramatic_literary_material(self):
        """Applied to nondramatic literary material in English."""
        self.assertIn('nondramatic literary material', self.text)

    def test_v0_english_language(self):
        """Applied specifically to English-language works."""
        self.assertIn('English language', self.text)


# ===========================================================================
# Section 602 -- Infringing importation
# ===========================================================================

class TestSection602(unittest.TestCase):
    """Section 602 addresses importation of infringing copies."""

    def setUp(self):
        self.text = get_v0_text('602')

    def test_v0_importation(self):
        """Core subject: importation of copies."""
        self.assertIn('importation', self.text.lower())

    def test_v0_infringing(self):
        """Addresses infringing copies."""
        self.assertIn('infring', self.text.lower())

    def test_v0_customs(self):
        """References customs enforcement."""
        lower = self.text.lower()
        self.assertTrue(
            'customs' in lower or 'secretary of' in lower,
            "Section 602 should reference customs enforcement")


# ===========================================================================
# Section 701 -- Copyright Office organization
# ===========================================================================

class TestSection701(unittest.TestCase):
    """Section 701 establishes the Copyright Office's responsibilities."""

    def setUp(self):
        self.text = get_v0_text('701')

    def test_v0_register_of_copyrights(self):
        """The head of the Copyright Office is the Register of Copyrights."""
        self.assertIn('Register of Copyrights', self.text)

    def test_v0_library_of_congress(self):
        """The Copyright Office is part of the Library of Congress."""
        self.assertIn('Library of Congress', self.text)

    def test_v0_administrative_functions(self):
        """Should address administrative functions."""
        self.assertIn('administrative functions', self.text.lower())


# ===========================================================================
# Section 801 -- Copyright Royalty Judges
# ===========================================================================

class TestSection801(unittest.TestCase):
    """Section 801 originally established the Copyright Royalty Tribunal.
    It was later replaced by Copyright Royalty Judges (2004)."""

    def setUp(self):
        self.data = load_versions('801')
        self.v0_text = self.data['versions'][0]['text']

    def test_v0_addresses_royalty_adjudication(self):
        """Should address royalty determination/adjudication."""
        lower = self.v0_text.lower()
        self.assertTrue(
            'royalt' in lower,
            "Section 801 should address royalty matters")

    def test_v0_librarian_of_congress(self):
        """The Librarian of Congress is involved in appointments."""
        self.assertIn('Librarian of Congress', self.v0_text)

    def test_current_references_judges(self):
        """Current version should reference Copyright Royalty Judges
        (replacing the old Copyright Royalty Tribunal)."""
        current = get_current_text('801')
        self.assertIn('Copyright Royalty Judge', current)


# ===========================================================================
# Section 901 -- Semiconductor chip definitions
# ===========================================================================

class TestSection901(unittest.TestCase):
    """Section 901 defines terms for the Semiconductor Chip Protection Act
    of 1984 (Chapter 9)."""

    def setUp(self):
        self.text = get_v0_text('901')

    def test_v0_semiconductor(self):
        """Must define semiconductor chip product."""
        self.assertIn('semiconductor chip product', self.text.lower())

    def test_v0_mask_work(self):
        """Must define 'mask work'."""
        self.assertIn('mask work', self.text.lower())

    def test_v0_chapter_reference(self):
        """Should reference 'this chapter' (Chapter 9, not Title 17 generally)."""
        self.assertIn('this chapter', self.text.lower())

    def test_v0_layers(self):
        """Semiconductor chips have layers of material."""
        self.assertIn('layers', self.text.lower())


# ===========================================================================
# Section 1202 -- Copyright management information
# ===========================================================================

class TestSection1202(unittest.TestCase):
    """Section 1202 was added by the DMCA (1998) and prohibits removal or
    alteration of copyright management information."""

    def setUp(self):
        self.text = get_v0_text('1202')

    def test_v0_copyright_management_information(self):
        """Should address copyright management information."""
        self.assertIn('copyright management information', self.text.lower())

    def test_v0_integrity_of_information(self):
        """Prohibits tampering with copyright information."""
        lower = self.text.lower()
        self.assertTrue(
            'remove' in lower or 'alter' in lower,
            "Section 1202 should prohibit removing/altering CMI")

    def test_v0_is_from_dmca_era(self):
        """Section 1202 was created by the DMCA (1998) or amended shortly after."""
        data = load_versions('1202')
        v0 = data['versions'][0]
        # The DMCA created 1202 but later amendments may have restructured
        # the version chain; verify it's from the late 1990s era
        year = v0.get('year', '')
        pl = v0.get('public_law', '')
        self.assertTrue(
            '105-' in pl or '106-' in pl,
            f"Section 1202 v0 should be from a late-1990s PL, "
            f"got PL '{pl}'")


# ===========================================================================
# Cross-section legal consistency
# ===========================================================================

class TestCrossSectionLegalConsistency(unittest.TestCase):
    """Verify that legal cross-references are internally consistent."""

    def test_section_103_references_102(self):
        """Section 103 should reference section 102."""
        text = get_v0_text('103')
        self.assertIn('section 102', text)

    def test_section_108_references_106(self):
        """Section 108 references section 106 (exclusive rights it limits)."""
        text = get_v0_text('108')
        self.assertIn('section 106', text)

    def test_section_411_references_registration(self):
        """Section 411 discusses registration as prerequisite to suit."""
        text = get_v0_text('411')
        self.assertIn('registration', text.lower())

    def test_section_502_references_infringement(self):
        """Section 502 (injunctions) addresses infringement."""
        text = get_v0_text('502')
        self.assertIn('infringement', text.lower())

    def test_section_305_references_302_303_304(self):
        """Section 305 cross-references the duration sections."""
        text = get_v0_text('305')
        self.assertIn('302', text)

    def test_section_601_importation_language(self):
        """Section 601 discusses importation requirements."""
        text = get_v0_text('601')
        self.assertIn('importation', text.lower())

    def test_chapters_have_correct_section_ranges(self):
        """Verify that chapters contain the expected section number ranges."""
        snapshot_secs = set(all_snapshot_sections())
        # Chapter 1: 101-122
        ch1 = [s for s in snapshot_secs if s.isdigit()
               and 101 <= int(s) <= 122]
        self.assertGreaterEqual(len(ch1), 15,
                                "Chapter 1 should have 15+ sections")
        # Chapter 2: 201-205
        ch2 = [s for s in snapshot_secs if s.isdigit()
               and 201 <= int(s) <= 205]
        self.assertGreaterEqual(len(ch2), 4,
                                "Chapter 2 should have 4+ sections")
        # Chapter 3: 301-305
        ch3 = [s for s in snapshot_secs if s.isdigit()
               and 301 <= int(s) <= 305]
        self.assertGreaterEqual(len(ch3), 4,
                                "Chapter 3 should have 4+ sections")
        # Chapter 5: 501-513
        ch5 = [s for s in snapshot_secs if s.isdigit()
               and 501 <= int(s) <= 513]
        self.assertGreaterEqual(len(ch5), 8,
                                "Chapter 5 should have 8+ sections")


def all_snapshot_sections():
    sections = []
    for fname in os.listdir(SNAPSHOTS_DIR):
        if fname.endswith('-versions.json'):
            sections.append(fname.replace('-versions.json', ''))
    return sorted(sections)


# ===========================================================================
# Broad anachronism sweep for all 1976-era sections
# ===========================================================================

class TestBroadAnachronismSweep(unittest.TestCase):
    """Check all sections whose v0 represents the original 1976 Act for
    terms that could not have existed in 1976."""

    # Sections whose v0 should be 1976-era text
    # (determined by having PL 94-553 as the public_law or being in the
    # original 1976 Act section range with no amendments)
    SECTIONS_1976_ERA = []

    @classmethod
    def setUpClass(cls):
        # Only include sections whose v0 is genuinely from the 1976 Act
        # (PL 94-553). Sections added later (106A, 120, 512, 1201, 1401, etc.)
        # should NOT be checked for 1976 anachronisms.
        original_1976_range = set(str(n) for n in list(range(101, 119)) +
                                  list(range(201, 206)) +
                                  list(range(301, 306)) +
                                  list(range(401, 413)) +
                                  list(range(501, 511)) +
                                  list(range(601, 604)) +
                                  list(range(701, 709)))
        for sec in all_snapshot_sections():
            if sec not in original_1976_range:
                continue
            data = load_versions(sec)
            v0 = data['versions'][0]
            pl = v0.get('public_law', '')
            year = v0.get('year', '')
            # Only include if the v0 PL is 94-553 AND the reversal
            # actually reached 1976-era text (year is empty or <= 1980).
            # Sections where reversal failed have v0 year much later.
            if '94-553' in pl:
                if not year or (year.isdigit() and int(year) <= 1980):
                    cls.SECTIONS_1976_ERA.append(sec)

    def test_no_digital_millennium_in_1976(self):
        """No 1976-era section should mention the DMCA (1998)."""
        for sec in self.SECTIONS_1976_ERA:
            text = get_v0_text(sec).lower()
            with self.subTest(section=sec):
                self.assertNotIn('digital millennium', text)

    def test_no_internet_in_1976(self):
        """'Internet' didn't exist as a concept in 1976."""
        for sec in self.SECTIONS_1976_ERA:
            text = get_v0_text(sec).lower()
            with self.subTest(section=sec):
                self.assertNotIn('internet', text)

    def test_no_online_service_provider_in_1976(self):
        """'Online service provider' is a 1990s concept."""
        for sec in self.SECTIONS_1976_ERA:
            text = get_v0_text(sec).lower()
            with self.subTest(section=sec):
                self.assertNotIn('online service provider', text)

    def test_no_section_512_references_in_1976(self):
        """Section 512 didn't exist until 1998 (DMCA)."""
        for sec in self.SECTIONS_1976_ERA:
            text = get_v0_text(sec)
            with self.subTest(section=sec):
                self.assertNotIn('section 512', text)

    def test_no_webcasting_in_1976(self):
        """'Webcasting' is a post-internet concept."""
        for sec in self.SECTIONS_1976_ERA:
            text = get_v0_text(sec).lower()
            with self.subTest(section=sec):
                self.assertNotIn('webcasting', text)

    def test_no_digital_audio_transmission_in_1976(self):
        """'Digital audio transmission' was added by the DPRA (1995)."""
        for sec in self.SECTIONS_1976_ERA:
            text = get_v0_text(sec).lower()
            with self.subTest(section=sec):
                self.assertNotIn('digital audio transmission', text)

    def test_no_copyright_royalty_judges_in_1976(self):
        """'Copyright Royalty Judges' replaced the Tribunal in 2004."""
        for sec in self.SECTIONS_1976_ERA:
            text = get_v0_text(sec)
            with self.subTest(section=sec):
                self.assertNotIn('Copyright Royalty Judge', text)


if __name__ == '__main__':
    unittest.main()
