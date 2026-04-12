#!/usr/bin/env python3
"""
Audit tests for reconstructed 1976-era statutory text of Title 17 sections.

These tests verify that version 0 (the oldest reconstructed snapshot) for each
section accurately represents the original 1976 Copyright Act text, free from
anachronistic language introduced by later amendments.

Usage:
    pytest tests/test_audit.py -v
    # or: python3 tests/test_audit.py
"""

import json
import os
import re
import subprocess
import unittest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

OUTPUT_REPO = os.environ.get(
    'COPYRIGHT_HISTORY_REPO',
    os.path.expanduser('~/code/copyright-history'),
)


# ---------------------------------------------------------------------------
# Helpers (reused from test_examples.py patterns)
# ---------------------------------------------------------------------------

def git(*args, repo=OUTPUT_REPO):
    """Run a git command in the output repo, return stdout."""
    result = subprocess.run(
        ['git', '-C', repo] + list(args),
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} failed:\n{result.stderr.strip()}"
        )
    return result.stdout.strip()


def commit_for(act_name):
    """Find the commit hash whose subject line contains act_name."""
    log = git('log', '--oneline', '--all')
    for line in log.splitlines():
        hash_, _, subject = line.partition(' ')
        if act_name.lower() in subject.lower():
            return hash_
    raise LookupError(f"No commit found matching '{act_name}'")


def show_file_at(commit, path):
    """Return file contents at a given commit."""
    return git('show', f'{commit}:{path}')


def skip_if_no_repo(fn):
    """Decorator to skip tests if the output repo doesn't exist."""
    def wrapper(*args, **kwargs):
        if not os.path.isdir(os.path.join(OUTPUT_REPO, '.git')):
            raise unittest.SkipTest(
                f"Output repo not found at {OUTPUT_REPO}. "
                "Build it with: python3 build.py"
            )
        return fn(*args, **kwargs)
    return wrapper


def load_versions(sec_num):
    """Load the full versions data for a section from its snapshot JSON."""
    path = os.path.join(DATA_DIR, 'snapshots', f'{sec_num}-versions.json')
    with open(path) as f:
        return json.load(f)


def get_v0_text(sec_num):
    """Return the oldest (version 0) reconstructed text for a section.

    This represents the 1976-era text before any amendments were applied.
    """
    data = load_versions(sec_num)
    return data['versions'][0]['text']


# ---------------------------------------------------------------------------
# Sections to audit across anachronism checks
# ---------------------------------------------------------------------------

ALL_AUDIT_SECTIONS = ['102', '104', '109', '113', '115', '116',
                      '201', '301', '504', '506', '708']


# ===========================================================================
# Section 102 -- Subject matter of copyright: In general
# ===========================================================================

class TestSection102(unittest.TestCase):
    """Audit the reconstructed 1976 text of Section 102."""

    def setUp(self):
        self.text = get_v0_text('102')

    def test_v0_has_seven_categories(self):
        """The original 1976 Act lists exactly 7 categories of copyrightable
        works. Category (8) -- architectural works -- was not added until
        the Architectural Works Copyright Protection Act of 1990."""
        self.assertIn('(7) sound recordings.', self.text)
        self.assertNotIn('(8)', self.text)

    def test_v0_no_architectural_works(self):
        """Architectural works were not copyrightable under the 1976 Act;
        they were added by PL 101-650 (1990)."""
        self.assertNotIn('architectural works', self.text.lower())

    def test_v0_category_7_ends_with_period(self):
        """Category (7) should end with a period, not '; and', because there
        is no category (8) in the original 1976 text."""
        self.assertIn('(7) sound recordings.', self.text)

    def test_v0_has_correct_heading(self):
        """Section 102 heading should read 'Subject matter of copyright:
        In general'."""
        self.assertIn('Subject matter of copyright: In general', self.text)

    def test_v0_subsection_b_complete(self):
        """Subsection (b) should contain the full idea/expression dichotomy
        enumeration."""
        self.assertIn(
            'idea, procedure, process, system, method of operation, '
            'concept, principle, or discovery',
            self.text,
        )


# ===========================================================================
# Section 104 -- Subject matter of copyright: National origin
# ===========================================================================

class TestSection104(unittest.TestCase):
    """Audit the reconstructed 1976 text of Section 104."""

    def setUp(self):
        self.text = get_v0_text('104')

    def test_v0_no_subsection_c(self):
        """The original 1976 text had only subsections (a) and (b). Subsection
        (c) was added by the Berne Convention Implementation Act of 1988."""
        self.assertNotRegex(self.text, r'\n\(c\) ')

    def test_v0_no_subsection_d(self):
        """No subsection (d) existed in the original 1976 text."""
        self.assertNotRegex(self.text, r'\n\(d\) ')

    def test_v0_no_treaty_party(self):
        """The term 'treaty party' was introduced by the Berne Convention
        Implementation Act of 1988 and should not appear in the 1976 text."""
        self.assertNotIn('treaty party', self.text.lower())

    def test_v0_has_foreign_nation_language(self):
        """The 1976 text uses 'foreign nation' language rather than the
        post-Berne 'treaty party' terminology."""
        self.assertIn(
            'foreign nation that is a party to a copyright treaty '
            'to which the United States is also a party',
            self.text,
        )

    def test_v0_has_universal_copyright_convention(self):
        """The 1976 text specifically references the Universal Copyright
        Convention (before Berne broadened the treaty references)."""
        self.assertIn('party to the Universal Copyright Convention', self.text)

    def test_v0_has_four_paragraphs(self):
        """Subsection (b) should have exactly 4 paragraphs -- (1) through (4).
        Paragraph (5) was added by a later amendment."""
        self.assertIn('(4)', self.text)
        self.assertNotIn('(5)', self.text)


# ===========================================================================
# Section 109 -- Limitations on exclusive rights: Effect of transfer
# ===========================================================================

class TestSection109(unittest.TestCase):
    """Audit the reconstructed 1976 text of Section 109."""

    def setUp(self):
        self.text = get_v0_text('109')

    def test_v0_only_three_subsections(self):
        """The original 1976 Act had only subsections (a), (b), and (c).
        Subsections (d) and (e) were added by the Record Rental Amendment
        Act of 1984 and Computer Software Rental Amendments Act of 1990."""
        self.assertIn('(a)', self.text)
        self.assertIn('(b)', self.text)
        self.assertIn('(c)', self.text)
        self.assertNotIn('\n(d)', self.text)
        self.assertNotIn('\n(e)', self.text)

    def test_v0_no_computer_program(self):
        """The term 'computer program' was not in the original Section 109;
        it was added by the Computer Software Rental Amendments Act of 1990."""
        self.assertNotIn('computer program', self.text.lower())

    def test_v0_subsection_b_is_display(self):
        """Subsection (b) in the original 1976 Act addresses the right to
        display a copy publicly."""
        self.assertIn('display that copy publicly', self.text)

    def test_v0_subsection_c_references_a_and_b(self):
        """Subsection (c) should cross-reference subsections (a) and (b)."""
        self.assertIn('subsections (a) and (b)', self.text)

    def test_v0_no_rental_prohibition(self):
        """The phrase 'rental, lease, or lending' was added by the Record
        Rental Amendment Act of 1984 and should not appear in 1976 text."""
        self.assertNotIn('rental, lease, or lending', self.text)

    def test_current_section_not_truncated(self):
        """Verify the current-sections/109.md file is complete by checking
        for subsection (e) and 'coin-operated' language."""
        path = os.path.join(DATA_DIR, 'current-sections', '109.md')
        with open(path) as f:
            current_text = f.read()
        self.assertIn('(e)', current_text)
        self.assertIn('coin-operated', current_text)


# ===========================================================================
# Section 113 -- Scope of exclusive rights in pictorial, graphic,
#                and sculptural works
# ===========================================================================

class TestSection113(unittest.TestCase):
    """Audit the reconstructed 1976 text of Section 113."""

    def setUp(self):
        self.text = get_v0_text('113')

    def test_v0_no_subsection_d(self):
        """Subsection (d) was added by VARA (1990) and should not be in the
        original 1976 text."""
        self.assertNotIn('\n(d)', self.text)

    def test_v0_no_vara_references(self):
        """VARA-specific terms should not appear in the 1976 text. The Visual
        Artists Rights Act was enacted in 1990."""
        self.assertNotIn('Visual Artists Rights', self.text)
        self.assertNotIn('106A', self.text)

    def test_v0_has_subsections_a_b_c(self):
        """The original 1976 text should have subsections (a), (b), and (c)."""
        self.assertIn('(a)', self.text)
        self.assertIn('(b)', self.text)
        self.assertIn('(c)', self.text)

    def test_v0_subsection_c_ends_with_news(self):
        """Subsection (c) should reference news reporting context, ending
        with 'news reports.' or similar language."""
        self.assertIn('news reports.', self.text)


# ===========================================================================
# Section 115 -- Scope of exclusive rights in nondramatic musical works:
#                Compulsory license for making and distributing phonorecords
# ===========================================================================

class TestSection115(unittest.TestCase):
    """Audit the reconstructed 1976 text of Section 115."""

    def setUp(self):
        self.text = get_v0_text('115')

    def test_v0_has_original_royalty_rate(self):
        """The original 1976 compulsory license royalty rate was two and
        three-fourths cents per work, or one-half cent per minute."""
        self.assertIn(
            'two and three-fourths cents, or one-half of one cent per minute',
            self.text,
        )

    def test_v0_no_digital_phonorecord(self):
        """The term 'digital phonorecord' was introduced by the DPRA (1995)
        and should not appear in 1976 text."""
        self.assertNotIn('digital phonorecord', self.text.lower())

    def test_v0_has_subsections_a_b_c(self):
        """The original 1976 text should have subsections (a), (b), and (c)."""
        self.assertIn('(a)', self.text)
        self.assertIn('(b)', self.text)
        self.assertIn('(c)', self.text)

    def test_v0_no_subsection_d(self):
        """No subsection (d) existed in the original 1976 text; it was added
        by the DPRA (1995)."""
        self.assertNotRegex(self.text, r'\n\(d\) ')

    def test_v0_has_section_509_reference(self):
        """The original remedies cross-reference should include section 509
        (which was later repealed)."""
        self.assertIn('sections 502 through 506 and 509', self.text)

    def test_v0_forecloses_language(self):
        """The original text should contain the 'forecloses' provision about
        compulsory licensing."""
        self.assertIn(
            'forecloses the possibility of a compulsory license',
            self.text,
        )


# ===========================================================================
# Section 116 -- Negotiated licenses for public performances by means of
#                coin-operated phonorecord players (jukeboxes)
# ===========================================================================

class TestSection116(unittest.TestCase):
    """Audit the reconstructed 1976 text of Section 116."""

    def setUp(self):
        self.text = get_v0_text('116')

    def test_v0_is_jukebox(self):
        """Section 116 originally dealt with jukebox compulsory licenses,
        using the term 'coin-operated phonorecord player'."""
        self.assertIn('coin-operated phonorecord player', self.text)

    def test_v0_has_8_dollar_royalty(self):
        """The annual royalty rate for jukebox performance was $8."""
        self.assertIn('$8', self.text)

    def test_v0_has_4_dollar_half_year(self):
        """A $4 fee applied for certain partial-year situations."""
        self.assertIn('$4', self.text)

    def test_v0_has_copyright_royalty_tribunal(self):
        """The 1976 Act established the Copyright Royalty Tribunal to handle
        jukebox royalty disputes."""
        self.assertIn('Copyright Royalty Tribunal', self.text)

    def test_v0_has_criminal_penalties(self):
        """The original Section 116 included criminal penalties provisions."""
        self.assertIn('Criminal Penalties', self.text)

    def test_v0_not_negotiated_licenses(self):
        """The phrase 'Negotiated licenses' was introduced by the Berne
        Convention Implementation Act (1988) and should not appear in 1976
        text."""
        self.assertNotIn('negotiated licenses', self.text.lower())


# ===========================================================================
# Section 201 -- Ownership of copyright
# ===========================================================================

class TestSection201(unittest.TestCase):
    """Audit the reconstructed 1976 text of Section 201."""

    def setUp(self):
        self.text = get_v0_text('201')

    def test_v0_no_title_11_exception(self):
        """The bankruptcy exception ('except as provided under title 11') was
        added by PL 95-598 (1978) and should not be in the 1976 text."""
        self.assertNotIn('except as provided under title 11', self.text)

    def test_v0_ends_under_this_title(self):
        """Without the bankruptcy exception, subsection (e) should end with
        'shall be given effect under this title.' (period, no qualifier)."""
        self.assertIn('shall be given effect under this title.', self.text)

    def test_v0_has_five_subsections(self):
        """The original 1976 text has five subsections: (a) through (e)."""
        for sub in ['(a)', '(b)', '(c)', '(d)', '(e)']:
            self.assertIn(sub, self.text,
                          f"Subsection {sub} should be present")

    def test_v0_works_for_hire(self):
        """The work-for-hire doctrine should reference 'employer or other
        person for whom the work was prepared'."""
        self.assertIn(
            'employer or other person for whom the work was prepared',
            self.text,
        )


# ===========================================================================
# Section 301 -- Preemption with respect to other laws
# ===========================================================================

class TestSection301(unittest.TestCase):
    """Audit the reconstructed 1976 text of Section 301."""

    def setUp(self):
        self.text = get_v0_text('301')

    def test_v0_has_2047(self):
        """The original preemption date for pre-1972 sound recordings was
        February 15, 2047 (before CTEA extended it to 2067)."""
        self.assertIn('2047', self.text)

    def test_v0_no_2067(self):
        """The year 2067 was introduced by the CTEA (1998) and should not
        appear in the original 1976 text."""
        self.assertNotIn('2067', self.text)

    def test_v0_no_subsection_e(self):
        """There was no Berne Convention preemption subsection in the original
        1976 text. Subsection (e) was added by the Berne Convention
        Implementation Act of 1988."""
        self.assertNotIn('Berne Convention', self.text)

    def test_v0_no_subsection_f(self):
        """VARA-related preemption language should not be in the 1976 text.
        It was added by the Visual Artists Rights Act of 1990."""
        self.assertNotIn('Visual Artists Rights', self.text)

    def test_v0_three_sentences_in_c(self):
        """Subsection (c) should contain exactly 3 references to the year
        2047 (the preemption sunset date for pre-1972 sound recordings)."""
        count = self.text.count('2047')
        self.assertEqual(count, 3,
                         f"Expected 3 occurrences of '2047', found {count}")

    def test_v0_no_paragraph_b4(self):
        """Subsection (b) should have exactly 3 paragraphs, (1)-(3).
        Paragraph (4) was added by a later amendment."""
        self.assertNotIn('(4)', self.text)

    def test_ctea_snapshot_has_2067(self):
        """The CTEA act-snapshot for Section 301 should contain the extended
        preemption date of 2067 but NOT the Classics Protection language
        (which came later in 2018)."""
        path = os.path.join(
            DATA_DIR,
            'act-snapshots',
            '1998-10-27-sonny-bono-copyright-term-extension-act-of-1998',
            '301.md',
        )
        with open(path) as f:
            ctea_text = f.read()
        self.assertIn('2067', ctea_text)
        self.assertNotIn('Classics Protection', ctea_text)


# ===========================================================================
# Section 504 -- Remedies for infringement: Damages and profits
# ===========================================================================

class TestSection504(unittest.TestCase):
    """Audit the reconstructed 1976 text of Section 504."""

    def setUp(self):
        self.text = get_v0_text('504')

    def test_v0_has_250_minimum(self):
        """The original 1976 statutory damages minimum was $250."""
        self.assertIn('$250', self.text)

    def test_v0_has_10000_maximum(self):
        """The original 1976 statutory damages maximum was $10,000."""
        self.assertIn('$10,000', self.text)

    def test_v0_has_50000_willful(self):
        """The original 1976 willful infringement cap was $50,000."""
        self.assertIn('$50,000', self.text)

    def test_v0_has_100_innocent(self):
        """The original 1976 innocent infringement floor was $100."""
        self.assertIn('not less than $100.', self.text)

    def test_v0_no_domain_name(self):
        """The term 'domain name' relates to the Anticybersquatting Act (1999)
        and should not appear in 1976 text."""
        self.assertNotIn('domain name', self.text.lower())

    def test_v0_no_subsection_d(self):
        """No subsection '(d) Additional Damages' existed in the original
        1976 text."""
        self.assertNotIn('(d) Additional Damages', self.text)


# ===========================================================================
# Section 506 -- Criminal offenses
# ===========================================================================

class TestSection506(unittest.TestCase):
    """Audit the reconstructed 1976 text of Section 506."""

    def setUp(self):
        self.text = get_v0_text('506')

    def test_v0_has_10000_fine(self):
        """The original 1976 maximum fine was $10,000."""
        self.assertIn('$10,000', self.text)

    def test_v0_no_section_2319(self):
        """Reference to 18 USC 2319 was added by the Piracy and
        Counterfeiting Amendments Act of 1982 and should not be in 1976
        text."""
        self.assertNotIn('section 2319', self.text)

    def test_v0_no_subsection_f(self):
        """VARA-related attribution rights language should not be in the
        1976 text."""
        self.assertNotIn('Rights of Attribution', self.text)

    def test_v0_has_proviso(self):
        """The original 1976 text should contain the 'Provided, however'
        proviso clause."""
        self.assertIn('Provided, however', self.text)

    def test_v0_has_25000_and_50000(self):
        """The original 1976 text should reference both $25,000 and $50,000
        fine amounts."""
        self.assertIn('$25,000', self.text)
        self.assertIn('$50,000', self.text)


# ===========================================================================
# Section 708 -- Copyright Office fees
# ===========================================================================

class TestSection708(unittest.TestCase):
    """Audit the reconstructed 1976 text of Section 708."""

    def setUp(self):
        self.text = get_v0_text('708')

    def test_v0_has_11_items(self):
        """The original 1976 fee schedule had 11 items."""
        self.assertIn('(11)', self.text)

    def test_v0_original_fees(self):
        """The original 1976 fee amounts: $10 for registration, $6 for
        renewal, $2 for receipt of deposit."""
        self.assertIn('$10', self.text)
        self.assertIn('$6', self.text)
        self.assertIn('$2', self.text)

    def test_v0_secretary_of_treasury(self):
        """The original 1976 text directs fees to be credited 'in such manner
        as the Secretary of the Treasury directs', NOT 'to the appropriation
        for necessary expenses' (which was a 1977 amendment)."""
        self.assertIn(
            'in such manner as the Secretary of the Treasury directs',
            self.text,
        )
        self.assertNotIn('appropriation for necessary expenses', self.text)

    def test_v0_three_subsections(self):
        """The original 1976 text had three subsections: (a), (b), and (c).
        Subsection (d) was added when (b) was redesignated in 1990."""
        self.assertIn('(a)', self.text)
        self.assertIn('(b)', self.text)
        self.assertIn('(c)', self.text)
        self.assertNotIn('\n(d)', self.text)

    def test_v0_no_cpi(self):
        """Consumer Price Index adjustments were added in 1990 (PL 101-318)
        and should not appear in the original 1976 text."""
        self.assertNotIn('Consumer Price Index', self.text)


# ===========================================================================
# Cross-section anachronism checks
# ===========================================================================

class TestAnachronisms(unittest.TestCase):
    """Check ALL audited sections for terms that could not have appeared
    in the original 1976 Copyright Act."""

    def setUp(self):
        self.v0_texts = {}
        for sec in ALL_AUDIT_SECTIONS:
            self.v0_texts[sec] = get_v0_text(sec)

    def test_no_dmca_terms(self):
        """No version 0 text should contain DMCA-era language. The Digital
        Millennium Copyright Act was enacted in 1998."""
        for sec, text in self.v0_texts.items():
            lower = text.lower()
            self.assertNotIn('dmca', lower,
                             f"Section {sec} v0 contains 'DMCA'")
            self.assertNotIn('digital millennium', lower,
                             f"Section {sec} v0 contains 'digital millennium'")

    def test_no_vara_terms(self):
        """No version 0 text should contain VARA language. The Visual Artists
        Rights Act was enacted in 1990."""
        for sec, text in self.v0_texts.items():
            self.assertNotIn('Visual Artists Rights', text,
                             f"Section {sec} v0 contains 'Visual Artists Rights'")
            self.assertNotIn('106A', text,
                             f"Section {sec} v0 contains '106A'")

    def test_no_mma_terms(self):
        """No version 0 text should contain Music Modernization Act language.
        The MMA was enacted in 2018."""
        for sec, text in self.v0_texts.items():
            lower = text.lower()
            self.assertNotIn('music modernization', lower,
                             f"Section {sec} v0 contains 'Music Modernization'")
            self.assertNotIn('mechanical licensing collective', lower,
                             f"Section {sec} v0 contains "
                             f"'mechanical licensing collective'")

    def test_no_post_1976_pl_refs(self):
        """No version 0 text should reference public law numbers from
        post-1976 congresses (105th, 108th, 110th, 115th)."""
        for sec, text in self.v0_texts.items():
            for pl in ['Pub. L. 105', 'Pub. L. 108',
                       'Pub. L. 110', 'Pub. L. 115']:
                self.assertNotIn(pl, text,
                                 f"Section {sec} v0 contains '{pl}'")

    def test_no_classics_protection(self):
        """No version 0 text should reference the Classics Protection and
        Access Act (part of the MMA, 2018)."""
        for sec, text in self.v0_texts.items():
            self.assertNotIn('Classics Protection', text,
                             f"Section {sec} v0 contains 'Classics Protection'")


# ===========================================================================
# Version structure integrity checks
# ===========================================================================

class TestVersionStructure(unittest.TestCase):
    """Verify structural integrity of the snapshot version arrays."""

    def _all_snapshot_sections(self):
        """Return list of section numbers that have snapshot files."""
        snapshots_dir = os.path.join(DATA_DIR, 'snapshots')
        sections = []
        for fname in os.listdir(snapshots_dir):
            if fname.endswith('-versions.json'):
                sec = fname.replace('-versions.json', '')
                sections.append(sec)
        return sorted(sections)

    def test_no_duplicate_pls(self):
        """Each public_law value should appear at most once per section's
        version history (no duplicate amendments)."""
        for sec in self._all_snapshot_sections():
            data = load_versions(sec)
            pls = []
            for v in data['versions']:
                pl = v.get('public_law')
                if pl:
                    pls.append(pl)
            duplicates = [pl for pl in pls if pls.count(pl) > 1]
            self.assertEqual(
                len(duplicates), 0,
                f"Section {sec} has duplicate public_law entries: "
                f"{set(duplicates)}",
            )

    def test_versions_chronological(self):
        """Version years should be monotonically non-decreasing."""
        for sec in self._all_snapshot_sections():
            data = load_versions(sec)
            years = []
            for v in data['versions']:
                y = v.get('year')
                if y and y != 'current':
                    years.append(int(y))
            for i in range(1, len(years)):
                self.assertGreaterEqual(
                    years[i], years[i - 1],
                    f"Section {sec}: version years not chronological: "
                    f"{years}",
                )

    def test_all_versions_have_text(self):
        """Every version entry must have a non-empty 'text' field."""
        for sec in self._all_snapshot_sections():
            data = load_versions(sec)
            for i, v in enumerate(data['versions']):
                text = v.get('text', '')
                self.assertTrue(
                    len(text.strip()) > 0,
                    f"Section {sec} version {i} has empty text",
                )

    def test_version0_is_oldest(self):
        """versions[0] should have the earliest year in the array."""
        for sec in self._all_snapshot_sections():
            data = load_versions(sec)
            versions = data['versions']
            years = []
            for v in versions:
                y = v.get('year')
                if y and y != 'current':
                    years.append(int(y))
            if len(years) >= 2:
                self.assertEqual(
                    years[0], min(years),
                    f"Section {sec}: version 0 (year {years[0]}) is not "
                    f"the oldest (min is {min(years)})",
                )

    def test_last_version_is_current(self):
        """The last version entry should represent the current law, indicated
        by 'act': 'Current' or 'date': 'current'."""
        for sec in self._all_snapshot_sections():
            data = load_versions(sec)
            last = data['versions'][-1]
            is_current = (
                last.get('act') == 'Current' or
                last.get('date') == 'current'
            )
            self.assertTrue(
                is_current,
                f"Section {sec}: last version does not have "
                f"act='Current' or date='current'. Keys: {list(last.keys())}",
            )

    @skip_if_no_repo
    def test_1976_commit_has_sections(self):
        """At the 1976 Act commit, the sections/ directory should contain
        at least 60 section files."""
        act_1976 = commit_for('Copyright Act of 1976')
        files = git('ls-tree', '--name-only', f'{act_1976}:sections')
        file_list = [f for f in files.splitlines() if f.endswith('.md')]
        self.assertGreaterEqual(
            len(file_list), 60,
            f"Expected at least 60 section files at 1976 commit, "
            f"got {len(file_list)}",
        )

    @skip_if_no_repo
    def test_1976_commit_102_no_arch_works(self):
        """At the 1976 commit, sections/102.md should NOT contain '(8)'
        (architectural works were added later)."""
        act_1976 = commit_for('Copyright Act of 1976')
        text = show_file_at(act_1976, 'sections/102.md')
        self.assertNotIn('(8)', text)

    @skip_if_no_repo
    def test_berne_commit_touches_104(self):
        """The Berne Convention Implementation Act commit should modify
        sections/104.md."""
        berne = commit_for('Berne Convention Implementation Act')
        diff = git('diff', f'{berne}~1', berne, '--name-only')
        self.assertIn('sections/104.md', diff)

    @skip_if_no_repo
    def test_vara_commit_touches_113(self):
        """The Visual Artists Rights Act commit should modify
        sections/113.md."""
        vara = commit_for('Visual Artists Rights')
        diff = git('diff', f'{vara}~1', vara, '--name-only')
        self.assertIn('sections/113.md', diff)

    @skip_if_no_repo
    def test_commits_chronological(self):
        """All commits in the output repo should be in chronological order
        by author date."""
        log = git('log', '--format=%at', '--reverse')
        timestamps = [int(t) for t in log.splitlines() if t.strip()]
        for i in range(1, len(timestamps)):
            self.assertGreaterEqual(
                timestamps[i], timestamps[i - 1],
                f"Commit {i} has timestamp {timestamps[i]} which is before "
                f"commit {i-1} timestamp {timestamps[i-1]}",
            )


if __name__ == '__main__':
    unittest.main()
