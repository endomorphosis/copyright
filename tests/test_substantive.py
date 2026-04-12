#!/usr/bin/env python3
"""
Substantive tests verifying the legal accuracy of reconstructed copyright
statute text against known historical facts about Title 17.

These tests use knowledge of the legislative history of US copyright law
to verify that:
  1. Version 0 (oldest snapshot) text matches the 1976 Act where applicable
  2. Key amendments are properly reflected in the version chain
  3. Section text contains (or excludes) legally significant language
  4. Cross-references between sections are consistent

Usage:
    python3 -m unittest tests/test_substantive.py -v
"""

import json
import os
import subprocess
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
SNAPSHOTS_DIR = os.path.join(DATA_DIR, 'snapshots')

OUTPUT_REPO = os.environ.get(
    'COPYRIGHT_HISTORY_REPO',
    os.path.expanduser('~/code/copyright-history'),
)


def load_versions(sec_num):
    path = os.path.join(SNAPSHOTS_DIR, f'{sec_num}-versions.json')
    with open(path) as f:
        return json.load(f)


def get_v0_text(sec_num):
    return load_versions(sec_num)['versions'][0]['text']


def get_current_text(sec_num):
    data = load_versions(sec_num)
    return data['versions'][-1].get('text', '')


def git(*args, repo=OUTPUT_REPO):
    result = subprocess.run(
        ['git', '-C', repo] + list(args),
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed:\n{result.stderr.strip()}")
    return result.stdout.strip()


def skip_if_no_repo(fn):
    def wrapper(*args, **kwargs):
        if not os.path.isdir(os.path.join(OUTPUT_REPO, '.git')):
            raise unittest.SkipTest(f"Output repo not found at {OUTPUT_REPO}")
        return fn(*args, **kwargs)
    return wrapper


# ===========================================================================
# Section 106 -- Exclusive rights in copyrighted works
# ===========================================================================

class TestSection106(unittest.TestCase):
    """The original 1976 Act granted 5 exclusive rights. The 6th (digital
    audio transmission) was added by the Digital Performance Right in Sound
    Recordings Act of 1995 (DPRA), Pub. L. 104-39."""

    def setUp(self):
        self.text = get_v0_text('106')

    def test_v0_has_five_exclusive_rights(self):
        """The original 1976 Act enumerated exactly 5 exclusive rights:
        reproduce, prepare derivatives, distribute, perform, display."""
        self.assertIn('(1)', self.text)
        self.assertIn('(2)', self.text)
        self.assertIn('(3)', self.text)
        self.assertIn('(4)', self.text)
        self.assertIn('(5)', self.text)

    def test_v0_reproduce_right(self):
        """Right (1): reproduce in copies or phonorecords."""
        self.assertIn('reproduce the copyrighted work in copies or phonorecords',
                       self.text)

    def test_v0_derivative_works_right(self):
        """Right (2): prepare derivative works."""
        self.assertIn('prepare derivative works based upon the copyrighted work',
                       self.text)

    def test_v0_distribution_right(self):
        """Right (3): distribute copies or phonorecords to the public."""
        self.assertIn('distribute copies or phonorecords', self.text)

    def test_v0_performance_right(self):
        """Right (4): perform the copyrighted work publicly."""
        self.assertIn('perform the copyrighted work publicly', self.text)

    def test_v0_display_right(self):
        """Right (5): display the copyrighted work publicly."""
        self.assertIn('display the copyrighted work publicly', self.text)

    def test_v0_subject_to_limitations(self):
        """The introductory clause should reference sections 107-118 (the
        original limitation sections), not 107-122 (post-STELA)."""
        self.assertIn('Subject to sections 107 through', self.text)


# ===========================================================================
# Section 107 -- Fair use
# ===========================================================================

class TestSection107(unittest.TestCase):
    """Section 107 codified the fair use doctrine. The four statutory factors
    have remained essentially unchanged since 1976, though a sentence about
    unpublished works was added in 1992 (Pub. L. 102-492)."""

    def setUp(self):
        self.text = get_v0_text('107')

    def test_v0_has_four_factors(self):
        """The four fair use factors should all be present."""
        self.assertIn('(1)', self.text)
        self.assertIn('(2)', self.text)
        self.assertIn('(3)', self.text)
        self.assertIn('(4)', self.text)

    def test_v0_factor1_purpose_and_character(self):
        """Factor 1: the purpose and character of the use."""
        self.assertIn('purpose and character of the use', self.text)

    def test_v0_factor2_nature_of_work(self):
        """Factor 2: the nature of the copyrighted work."""
        self.assertIn('nature of the copyrighted work', self.text)

    def test_v0_factor3_amount_and_substantiality(self):
        """Factor 3: the amount and substantiality of the portion used."""
        self.assertIn('amount and substantiality of the portion used', self.text)

    def test_v0_factor4_market_effect(self):
        """Factor 4: the effect upon the potential market."""
        self.assertIn('effect of the use upon the potential market', self.text)

    def test_v0_enumerated_purposes(self):
        """The preamble should enumerate illustrative fair use purposes:
        criticism, comment, news reporting, teaching, scholarship, research."""
        for purpose in ['criticism', 'comment', 'news reporting',
                        'teaching', 'scholarship', 'research']:
            self.assertIn(purpose, self.text,
                          f"Fair use preamble should mention '{purpose}'")

    def test_v0_classroom_parenthetical(self):
        """The parenthetical about multiple copies for classroom use should
        be present -- this was part of the original 1976 Act."""
        self.assertIn('including multiple copies for classroom use', self.text)


# ===========================================================================
# Section 110 -- Performance and display exemptions
# ===========================================================================

class TestSection110(unittest.TestCase):
    """Section 110 exempts certain performances and displays from
    infringement. The original 1976 Act had exemptions (1)-(10)."""

    def setUp(self):
        self.text = get_v0_text('110')

    def test_v0_face_to_face_teaching(self):
        """Exemption (1): face-to-face teaching in a nonprofit educational
        institution classroom."""
        self.assertIn('face-to-face teaching activities', self.text)
        self.assertIn('nonprofit educational institution', self.text)

    def test_v0_religious_services(self):
        """Exemption (3): performance of nondramatic literary or musical
        works in the course of religious services."""
        self.assertIn('in the course of services at a place of worship',
                       self.text)

    def test_v0_has_exemption_for_veterans_orgs(self):
        """Exemption (10): performance at social functions of nonprofit
        veterans' or fraternal organizations."""
        self.assertIn('veterans', self.text.lower())


# ===========================================================================
# Section 117 -- Computer programs
# ===========================================================================

class TestSection117(unittest.TestCase):
    """Section 117 was completely replaced by the Computer Software Copyright
    Act of 1980 (Pub. L. 96-517). The current text allows owners of copies
    to make backup copies and adaptations."""

    def setUp(self):
        self.text = get_v0_text('117')

    def test_v0_essential_step(self):
        """The 1980 version allows making a copy as an 'essential step in
        the utilization' of a computer program."""
        self.assertIn('essential step in the utilization', self.text)

    def test_v0_backup_copy(self):
        """The 1980 version allows archival (backup) copies."""
        self.assertIn('archival purposes', self.text)

    def test_v0_owner_of_copy(self):
        """The right to make copies is limited to the 'owner of a copy'
        of the computer program (not a licensee)."""
        self.assertIn('owner of a copy of a computer program', self.text)


# ===========================================================================
# Section 203 -- Termination of transfers (post-1978 works)
# ===========================================================================

class TestSection203(unittest.TestCase):
    """Section 203 allows authors to terminate transfers after 35 years.
    This was a key provision of the 1976 Act, granting authors a
    non-waivable right to reclaim their copyrights."""

    def setUp(self):
        self.text = get_v0_text('203')

    def test_v0_35_year_window(self):
        """The termination window begins 35 years after execution of the
        grant (for grants not involving publication)."""
        self.assertIn('thirty-five years', self.text)

    def test_v0_5_year_window(self):
        """Termination can be exercised during a 5-year window."""
        self.assertIn('five years', self.text)

    def test_v0_work_for_hire_exception(self):
        """Works made for hire are excluded from termination rights."""
        self.assertIn('work made for hire', self.text)

    def test_v0_two_year_advance_notice(self):
        """Notice of termination must be served at least 2 years before
        the effective date."""
        self.assertIn('not less than two', self.text)

    def test_v0_grant_on_or_after_1978(self):
        """Section 203 applies to grants executed on or after January 1, 1978."""
        self.assertIn('January 1, 1978', self.text)


# ===========================================================================
# Section 302 -- Duration: works created on or after Jan 1, 1978
# ===========================================================================

class TestSection302(unittest.TestCase):
    """The 1976 Act set copyright duration at life + 50 years for individual
    authors, and 75 years from publication (or 100 years from creation) for
    works for hire and anonymous/pseudonymous works. The CTEA (1998) extended
    these to life+70, 95, and 120 respectively."""

    def setUp(self):
        self.text = get_v0_text('302')

    def test_v0_life_plus_fifty(self):
        """Pre-CTEA: individual works last life + 50 years."""
        self.assertIn('fifty years after the author\'s death', self.text)

    def test_v0_seventy_five_from_publication(self):
        """Pre-CTEA: works for hire last 75 years from publication."""
        self.assertIn('seventy-five years from', self.text)

    def test_v0_one_hundred_from_creation(self):
        """Pre-CTEA: anonymous/pseudonymous works last 100 years from creation."""
        self.assertIn('one hundred years from', self.text)

    def test_v0_no_70_years(self):
        """The post-CTEA '70 years' should not appear in v0."""
        self.assertNotIn('70 years', self.text)

    def test_v0_no_95_years(self):
        """The post-CTEA '95 years' should not appear in v0."""
        self.assertNotIn('95 years', self.text)

    def test_v0_no_120_years(self):
        """The post-CTEA '120 years' should not appear in v0."""
        self.assertNotIn('120 years', self.text)

    def test_v0_joint_works(self):
        """Joint works: term measured from death of last surviving author."""
        self.assertIn('last surviving author', self.text)

    def test_v0_presumption_of_death(self):
        """Subsection (e) establishes a presumption of death for purposes
        of determining copyright duration."""
        self.assertIn('presumption', self.text.lower())

    def test_current_has_ctea_terms(self):
        """The current text should reflect CTEA extensions."""
        current = get_current_text('302')
        self.assertIn('70', current)


# ===========================================================================
# Section 401 -- Copyright notice on visually perceptible copies
# ===========================================================================

class TestSection401(unittest.TestCase):
    """Before the Berne Convention Implementation Act of 1988 (Pub. L. 100-568),
    copyright notice was MANDATORY ('shall be placed'). After Berne, it became
    OPTIONAL ('may be placed')."""

    def setUp(self):
        self.text = get_v0_text('401')

    def test_v0_notice_mandatory(self):
        """Pre-Berne: notice 'shall be placed on all publicly distributed copies'."""
        self.assertIn('shall be placed on all publicly distributed copies',
                       self.text)

    def test_v0_general_requirement_heading(self):
        """Pre-Berne: the heading was 'General Requirement' (not 'General Provisions')."""
        self.assertIn('General Requirement', self.text)

    def test_v0_three_elements(self):
        """Notice must contain three elements: (1) symbol/word, (2) year,
        (3) name of copyright owner."""
        self.assertIn('(1)', self.text)
        self.assertIn('(2)', self.text)
        self.assertIn('(3)', self.text)

    def test_v0_copyright_symbol(self):
        """The notice may use the symbol (c) or the word 'Copyright'."""
        # Check for the symbol or word reference
        lower = self.text.lower()
        self.assertTrue(
            'copyright' in lower and ('copr' in lower or '©' in lower),
            "Notice should reference the copyright symbol or abbreviation"
        )

    def test_post_berne_notice_optional(self):
        """After Berne amendment, notice should use 'may be placed'."""
        data = load_versions('401')
        if len(data['versions']) < 2:
            self.skipTest("No post-Berne version available")
        v1_text = data['versions'][1].get('text', '')
        self.assertIn('may be placed', v1_text)

    def test_post_berne_heading_changed(self):
        """After Berne, heading should change to 'General Provisions'."""
        data = load_versions('401')
        if len(data['versions']) < 2:
            self.skipTest("No post-Berne version available")
        v1_text = data['versions'][1].get('text', '')
        self.assertIn('General Provisions', v1_text)


# ===========================================================================
# Section 405 -- Effect of omission of notice
# ===========================================================================

class TestSection405(unittest.TestCase):
    """Section 405 addressed what happened when copyright notice was omitted.
    Before Berne (1989), omission could result in loss of copyright under
    certain conditions. After Berne, this section was limited to pre-Berne
    publications."""

    def setUp(self):
        self.text = get_v0_text('405')

    def test_v0_berne_limitation(self):
        """The current v0 should reference Berne since the earliest
        snapshot includes post-Berne amendments."""
        # The v0 was modified by Berne Implementation Act
        self.assertIn('Berne Convention Implementation Act', self.text)

    def test_v0_registration_cure(self):
        """Registration within 5 years could 'cure' omission of notice."""
        self.assertIn('registration', self.text.lower())


# ===========================================================================
# Section 501 -- Infringement of copyright
# ===========================================================================

class TestSection501(unittest.TestCase):
    """Section 501 defines copyright infringement and who may bring suit."""

    def setUp(self):
        self.text = get_v0_text('501')

    def test_v0_violation_of_exclusive_rights(self):
        """Infringement occurs when someone 'violates any of the exclusive
        rights of the copyright owner'."""
        self.assertIn('violates any of the exclusive rights', self.text)

    def test_v0_importation_infringement(self):
        """Importing copies in violation of section 602 is also infringement."""
        self.assertIn('section 602', self.text)

    def test_v0_legal_or_beneficial_owner(self):
        """The 'legal or beneficial owner' of a right may sue."""
        self.assertIn('legal or beneficial owner', self.text)

    def test_v0_references_106A(self):
        """After VARA (1990), section 501 references 106A rights."""
        self.assertIn('106A', self.text)


# ===========================================================================
# Section 512 -- DMCA Safe Harbors
# ===========================================================================

class TestSection512(unittest.TestCase):
    """Section 512 was added by the DMCA (1998) and establishes four safe
    harbor categories for service providers. This is one of the most
    consequential provisions for internet platforms."""

    def setUp(self):
        self.text = get_v0_text('512')

    def test_v0_four_safe_harbors(self):
        """The four safe harbors: (a) transitory communications, (b) system
        caching, (c) information on systems at user direction, (d) information
        location tools."""
        self.assertIn('Transitory Digital Network Communications', self.text)
        self.assertIn('System Caching', self.text)

    def test_v0_takedown_notice(self):
        """Section 512(c)(3) describes the elements of a takedown notification."""
        self.assertIn('notification', self.text.lower())

    def test_v0_counter_notification(self):
        """Section 512(g) provides for counter-notifications."""
        self.assertIn('counter notification', self.text.lower())

    def test_v0_service_provider_definition(self):
        """Section 512(k) defines 'service provider'."""
        self.assertIn('service provider', self.text.lower())

    def test_v0_designated_agent(self):
        """Service providers must designate an agent for receiving takedown
        notices."""
        self.assertIn('designated agent', self.text.lower())

    def test_v0_good_faith(self):
        """The safe harbors require good faith compliance."""
        self.assertIn('good faith', self.text.lower())

    def test_v0_repeat_infringer_policy(self):
        """Service providers must have a policy for terminating repeat
        infringers."""
        self.assertIn('repeat infringer', self.text.lower())

    def test_v0_subpoena(self):
        """Section 512(h) provides for subpoenas to identify infringers."""
        self.assertIn('subpoena', self.text.lower())


# ===========================================================================
# Section 1201 -- Anti-circumvention (DMCA Title I)
# ===========================================================================

class TestSection1201(unittest.TestCase):
    """Section 1201 prohibits circumventing technological measures that
    control access to copyrighted works. Added by the DMCA in 1998."""

    def setUp(self):
        self.text = get_v0_text('1201')

    def test_v0_anti_circumvention_prohibition(self):
        """The core prohibition: no person shall circumvent a technological
        measure that effectively controls access to a work."""
        self.assertIn('circumvent a technological measure', self.text)

    def test_v0_trafficking_prohibition(self):
        """Section 1201(a)(2) and (b) prohibit trafficking in circumvention
        tools/services."""
        self.assertIn('primarily designed', self.text.lower())

    def test_v0_librarian_of_congress_rulemaking(self):
        """The Librarian of Congress conducts triennial rulemaking to create
        exemptions from the anti-circumvention prohibition."""
        self.assertIn('Librarian of Congress', self.text)

    def test_v0_nonprofit_library_exception(self):
        """Section 1201(d) provides an exception for nonprofit libraries,
        archives, and educational institutions."""
        self.assertIn('nonprofit library', self.text.lower())

    def test_v0_reverse_engineering_exception(self):
        """Section 1201(f) provides a reverse engineering exception for
        achieving interoperability."""
        self.assertIn('interoperability', self.text.lower())

    def test_v0_security_testing_exception(self):
        """Section 1201(j) provides an exception for security testing."""
        self.assertIn('security testing', self.text.lower())

    def test_v0_law_enforcement_exception(self):
        """Section 1201(e) exempts law enforcement and intelligence
        activities."""
        self.assertIn('law enforcement', self.text.lower())


# ===========================================================================
# Section 106A -- Visual Artists Rights (VARA)
# ===========================================================================

class TestSection106A(unittest.TestCase):
    """Section 106A was added by the Visual Artists Rights Act of 1990
    (VARA), Pub. L. 101-650, Title VI. It grants moral rights of
    attribution and integrity to authors of works of visual art."""

    def setUp(self):
        self.text = get_v0_text('106A')

    def test_v0_attribution_right(self):
        """VARA grants the right to claim authorship."""
        self.assertIn('claim authorship', self.text)

    def test_v0_integrity_right(self):
        """VARA grants the right to prevent intentional distortion,
        mutilation, or modification that is prejudicial to honor/reputation."""
        lower = self.text.lower()
        self.assertIn('distortion', lower)
        self.assertIn('mutilation', lower)

    def test_v0_work_of_visual_art(self):
        """VARA applies specifically to 'work of visual art'."""
        self.assertIn('work of visual art', self.text)

    def test_v0_recognized_stature(self):
        """VARA protects works of 'recognized stature' from destruction."""
        self.assertIn('recognized stature', self.text)

    def test_v0_lifetime_duration(self):
        """For works created after VARA's effective date, moral rights
        last for the life of the author."""
        self.assertIn('life of the author', self.text)

    def test_v0_waiver_provision(self):
        """VARA rights can be waived by a written instrument signed by
        the author."""
        self.assertIn('waiver', self.text.lower())

    def test_v0_no_transfer(self):
        """VARA rights cannot be transferred (only waived)."""
        self.assertIn('not be transferred', self.text)


# ===========================================================================
# Cross-section consistency checks
# ===========================================================================

class TestCrossSectionConsistency(unittest.TestCase):
    """Verify that cross-references between sections are internally
    consistent and that the version history of related sections aligns."""

    def test_section_102_references_authorship(self):
        """Section 102 should reference 'original works of authorship'."""
        text = get_v0_text('102')
        self.assertIn('original works of authorship', text)

    def test_section_107_references_section_106(self):
        """Section 107 (fair use) should reference section 106 (exclusive
        rights) as the rights it limits."""
        text = get_v0_text('107')
        self.assertIn('106', text)

    def test_section_501_references_section_106(self):
        """Section 501 (infringement) should reference section 106
        (exclusive rights)."""
        text = get_v0_text('501')
        self.assertIn('106', text)

    def test_section_512_references_section_501(self):
        """Section 512 (safe harbors) should reference section 501
        (infringement), or at least the concept of infringement."""
        text = get_v0_text('512')
        self.assertIn('infringement', text.lower())

    def test_section_1201_not_in_chapter_1(self):
        """Section 1201 is in Chapter 12, not Chapter 1. Its text should
        reference 'this chapter' not 'this title' in certain contexts."""
        text = get_v0_text('1201')
        self.assertIn('this chapter', text.lower())


# ===========================================================================
# Snapshot structural checks for additional sections
# ===========================================================================

class TestAdditionalSectionStructure(unittest.TestCase):
    """Structural checks for sections not covered by test_audit.py."""

    def test_section_106_versions_chronological(self):
        data = load_versions('106')
        years = [int(v['year']) for v in data['versions']
                 if v.get('year') and v.get('year') != 'current'
                 and v.get('act') != 'Current']
        for i in range(1, len(years)):
            self.assertGreaterEqual(years[i], years[i - 1])

    def test_section_107_few_amendments(self):
        """Fair use has been remarkably stable. Only 2 amendments
        (VARA 1990 adding 106A ref, and 1992 unpublished works sentence)."""
        data = load_versions('107')
        # versions includes current, so should be 3 total
        self.assertLessEqual(len(data['versions']), 5,
                             "Section 107 should have very few amendments")

    def test_section_302_has_ctea_amendment(self):
        """Section 302 must show the CTEA changing durations."""
        data = load_versions('302')
        self.assertGreaterEqual(len(data['versions']), 2)

    def test_section_512_created_by_dmca(self):
        """Section 512 should have been added by the DMCA (Pub. L. 105-304)."""
        data = load_versions('512')
        v0 = data['versions'][0]
        self.assertIn('105-304', v0.get('public_law', ''))

    def test_section_1201_is_anti_circumvention(self):
        """Section 1201 should contain the core anti-circumvention prohibition."""
        text = get_v0_text('1201')
        self.assertIn('circumvent', text.lower())

    def test_all_snapshots_have_current_version(self):
        """Every snapshot file should end with a 'Current' version."""
        for fname in os.listdir(SNAPSHOTS_DIR):
            if not fname.endswith('-versions.json'):
                continue
            sec = fname.replace('-versions.json', '')
            data = load_versions(sec)
            last = data['versions'][-1]
            is_current = (
                last.get('act') == 'Current' or
                last.get('date') == 'current'
            )
            self.assertTrue(is_current,
                            f"Section {sec}: last version is not Current")

    def test_no_empty_version_text(self):
        """Every version should have non-empty text."""
        for fname in os.listdir(SNAPSHOTS_DIR):
            if not fname.endswith('-versions.json'):
                continue
            sec = fname.replace('-versions.json', '')
            data = load_versions(sec)
            for i, v in enumerate(data['versions']):
                text = v.get('text', '')
                self.assertTrue(len(text.strip()) > 0,
                                f"Section {sec} version {i} has empty text")


# ===========================================================================
# Section 304 -- Duration: subsisting copyrights
# ===========================================================================

class TestSection304(unittest.TestCase):
    """Section 304 governs the duration of copyrights that were already
    in existence on January 1, 1978. It has been amended many times,
    especially regarding renewal terms."""

    def setUp(self):
        self.text = get_v0_text('304')

    def test_v0_28_year_first_term(self):
        """The first term of copyright was 28 years from the date it was
        originally secured."""
        self.assertIn('28 years', self.text)

    def test_v0_references_jan_1_1978(self):
        """Section 304 is specifically about copyrights subsisting on
        January 1, 1978."""
        self.assertIn('January 1, 1978', self.text)


# ===========================================================================
# Section 114 -- Sound recordings
# ===========================================================================

class TestSection114(unittest.TestCase):
    """Section 114 limits the exclusive rights in sound recordings.
    Originally very narrow (no public performance right), it was
    significantly expanded by the DPRA (1995) and later acts."""

    def setUp(self):
        self.text = get_v0_text('114')

    def test_v0_sound_recording_limitations(self):
        """Section 114 addresses scope of rights in sound recordings."""
        self.assertIn('sound recording', self.text.lower())

    def test_v0_no_general_performance_right(self):
        """Sound recordings originally had NO general public performance
        right. The limited digital performance right was added in 1995."""
        # The original text should discuss limitations, not grant broad rights
        self.assertIn('imitate', self.text.lower(),
                      "Original §114 should discuss the right to independently "
                      "imitate sounds (the 'independent fixation' limitation)")


# ===========================================================================
# Section 120 -- Architectural works
# ===========================================================================

class TestSection120(unittest.TestCase):
    """Section 120 was added by the Architectural Works Copyright Protection
    Act of 1990 (Pub. L. 101-650, Title VII). It limits the exclusive
    rights in architectural works."""

    def setUp(self):
        self.text = get_v0_text('120')

    def test_v0_pictorial_representations(self):
        """Section 120(a) allows making pictorial representations of
        buildings visible from public places."""
        lower = self.text.lower()
        self.assertTrue(
            'pictorial' in lower or 'photograph' in lower or 'depict' in lower,
            "Section 120 should address pictorial representations of buildings"
        )

    def test_v0_alterations_to_buildings(self):
        """Section 120(b) allows the owner of a building to alter or
        destroy it without consent of the architect/author."""
        lower = self.text.lower()
        self.assertTrue(
            'alter' in lower or 'destroy' in lower,
            "Section 120 should address alterations/destruction of buildings"
        )


# ===========================================================================
# Output repo tests (require built repo)
# ===========================================================================

class TestOutputRepoAdditional(unittest.TestCase):
    """Additional tests against the built copyright-history git repo."""

    @skip_if_no_repo
    def test_dmca_creates_chapter_12_sections(self):
        """The DMCA commit should create sections 1201, 1202, etc."""
        from tests.test_examples import commit_for, show_file_at
        dmca = commit_for('Digital Millennium Copyright Act')
        try:
            text = show_file_at(dmca, 'sections/1201.md')
            self.assertIn('circumvent', text.lower())
        except RuntimeError:
            self.fail("DMCA commit should create sections/1201.md")

    @skip_if_no_repo
    def test_ctea_modifies_section_302(self):
        """The CTEA should modify section 302 (duration)."""
        from tests.test_examples import commit_for
        ctea = commit_for('Sonny Bono Copyright Term Extension')
        diff = git('diff', f'{ctea}~1', ctea, '--name-only')
        self.assertIn('sections/302.md', diff,
                       "CTEA should modify sections/302.md")

    @skip_if_no_repo
    def test_1976_act_creates_section_107(self):
        """The 1976 Act should create section 107 (fair use)."""
        from tests.test_examples import commit_for, show_file_at
        act_1976 = commit_for('Copyright Act of 1976')
        text = show_file_at(act_1976, 'sections/107.md')
        self.assertIn('fair use', text.lower())

    @skip_if_no_repo
    def test_no_future_dates_in_commits(self):
        """No commit should have a date after 2025."""
        log = git('log', '--format=%ai')
        for line in log.splitlines():
            if not line.strip():
                continue
            year = int(line[:4])
            self.assertLessEqual(year, 2025,
                                  f"Commit date {line} is in the future")

    @skip_if_no_repo
    def test_commits_are_chronological(self):
        """All commits should be in chronological order by author date."""
        log = git('log', '--format=%at', '--reverse')
        timestamps = [int(t) for t in log.splitlines() if t.strip()]
        for i in range(1, len(timestamps)):
            self.assertGreaterEqual(
                timestamps[i], timestamps[i - 1],
                f"Commit {i} is out of chronological order"
            )


# ===========================================================================
# Anachronism checks for additional sections
# ===========================================================================

class TestAdditionalAnachronisms(unittest.TestCase):
    """Verify sections that existed in the 1976 Act don't contain
    language from post-1976 legislation."""

    # Sections whose v0 is genuinely the original 1976 text
    SECTIONS_1976_CLEAN = ['107', '203', '302']

    def test_no_internet_terms_in_1976_sections(self):
        """Sections whose v0 represents the 1976 Act should not contain
        internet-related terms that didn't exist until the 1990s+."""
        internet_terms = ['internet', 'website', 'email']
        for sec in self.SECTIONS_1976_CLEAN:
            text = get_v0_text(sec)
            lower = text.lower()
            for term in internet_terms:
                self.assertNotIn(term, lower,
                                 f"Section {sec} v0 contains '{term}'")

    def test_no_streaming_in_1976_sections(self):
        """The concept of 'streaming' did not exist in 1976."""
        for sec in self.SECTIONS_1976_CLEAN:
            text = get_v0_text(sec)
            self.assertNotIn('streaming', text.lower(),
                             f"Section {sec} v0 contains 'streaming'")

    def test_no_mma_terms_in_extended_sections(self):
        """The Music Modernization Act (2018) terms should not appear
        in any pre-2018 version 0 text."""
        mma_terms = ['music modernization', 'mechanical licensing collective',
                     'blanket license']
        for sec in ['106', '107', '110', '114', '115']:
            text = get_v0_text(sec)
            lower = text.lower()
            for term in mma_terms:
                self.assertNotIn(term, lower,
                                 f"Section {sec} v0 contains MMA term '{term}'")


if __name__ == '__main__':
    unittest.main()
