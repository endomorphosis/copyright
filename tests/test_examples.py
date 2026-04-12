#!/usr/bin/env python3
"""
Tests that verify the examples in examples/ against the built output repo.

These tests run git commands against the copyright-history output repo and
check that the claims made in the example documents are actually true.
Commit hashes are looked up dynamically by commit message, so these tests
survive repo rebuilds.

Usage:
    pytest tests/test_examples.py -v
    # or: python3 tests/test_examples.py

Requires the output repo to exist at OUTPUT_REPO (default ~/code/copyright-history).
"""

import os
import re
import subprocess
import unittest

OUTPUT_REPO = os.environ.get(
    'COPYRIGHT_HISTORY_REPO',
    os.path.expanduser('~/code/copyright-history'),
)


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


def commits_for_file(path):
    """Return list of (hash, subject) tuples from git log for a file."""
    log = git('log', '--oneline', '--', path)
    results = []
    for line in log.splitlines():
        if not line.strip():
            continue
        hash_, _, subject = line.partition(' ')
        results.append((hash_, subject))
    return results


def show_file_at(commit, path):
    """Return file contents at a given commit."""
    return git('show', f'{commit}:{path}')


def diff_file(commit_a, commit_b, path):
    """Return diff of a file between two commits."""
    return git('diff', commit_a, commit_b, '--', path)


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


class TestExample01NoticeRequirement(unittest.TestCase):
    """Example 1: Was Copyright Notice Required?"""

    @skip_if_no_repo
    def test_section_401_has_two_commits(self):
        """Section 401 should have at least the 1976 Act and Berne Act."""
        commits = commits_for_file('sections/401.md')
        subjects = [s for _, s in commits]
        self.assertTrue(
            any('Copyright Act of 1976' in s for s in subjects),
            "Section 401 should have a Copyright Act of 1976 commit",
        )
        self.assertTrue(
            any('Berne Convention' in s for s in subjects),
            "Section 401 should have a Berne Convention commit",
        )

    @skip_if_no_repo
    def test_pre_berne_notice_mandatory(self):
        """Before Berne, Section 401(a) should say 'shall be placed on all'."""
        berne = commit_for('Berne Convention Implementation Act')
        text = show_file_at(f'{berne}~1', 'sections/401.md')
        self.assertIn('shall be placed on all publicly distributed copies', text)
        self.assertIn('General Requirement', text)

    @skip_if_no_repo
    def test_post_berne_notice_optional(self):
        """After Berne, Section 401(a) should say 'may be placed on'."""
        berne = commit_for('Berne Convention Implementation Act')
        text = show_file_at(berne, 'sections/401.md')
        self.assertIn('may be placed on publicly distributed copies', text)
        self.assertIn('General Provisions', text)

    @skip_if_no_repo
    def test_berne_diff_shows_shall_to_may(self):
        """The Berne diff should show the shall->may change."""
        berne = commit_for('Berne Convention Implementation Act')
        d = diff_file(f'{berne}~1', berne, 'sections/401.md')
        # Old text removed
        self.assertIn('-', d)
        self.assertIn('+', d)
        # Verify the semantic change is visible in the diff
        lines = d.splitlines()
        removed = [l for l in lines if l.startswith('-') and not l.startswith('---')]
        added = [l for l in lines if l.startswith('+') and not l.startswith('+++')]
        removed_text = ' '.join(removed)
        added_text = ' '.join(added)
        self.assertIn('shall', removed_text.lower())
        self.assertIn('may', added_text.lower())


class TestExample02CopyrightDuration(unittest.TestCase):
    """Example 2: How Copyright Duration Changed."""

    @skip_if_no_repo
    def test_section_302_has_expected_commits(self):
        """Section 302 should show 1976 Act, CTEA, and possibly others."""
        commits = commits_for_file('sections/302.md')
        subjects = [s for _, s in commits]
        self.assertTrue(
            any('Copyright Act of 1976' in s for s in subjects),
        )
        self.assertTrue(
            any('Sonny Bono' in s or 'Copyright Term Extension' in s for s in subjects),
        )

    @skip_if_no_repo
    def test_1976_duration_life_plus_fifty(self):
        """The 1976 Act should set duration to life + 50 years."""
        act_1976 = commit_for('Copyright Act of 1976')
        text = show_file_at(act_1976, 'sections/302.md')
        self.assertIn('fifty years', text.lower(),
                       "1976 Act should say 'fifty years' for individual authors")
        self.assertIn('seventy-five years', text.lower(),
                       "1976 Act should say 'seventy-five years' for works for hire")
        self.assertIn('one hundred years', text.lower(),
                       "1976 Act should say 'one hundred years' from creation")

    @skip_if_no_repo
    def test_ctea_extends_to_70_years(self):
        """CTEA should extend to life + 70 / 95 / 120."""
        ctea = commit_for('Sonny Bono Copyright Term Extension')
        text = show_file_at(ctea, 'sections/302.md')
        self.assertIn('70 years', text,
                       "CTEA should say '70 years' for individual authors")
        self.assertIn('95 years', text,
                       "CTEA should say '95 years' for works for hire")
        self.assertIn('120 years', text,
                       "CTEA should say '120 years' from creation")

    @skip_if_no_repo
    def test_ctea_diff_shows_extension(self):
        """CTEA diff should show fifty->70, seventy-five->95, etc."""
        ctea = commit_for('Sonny Bono Copyright Term Extension')
        d = diff_file(f'{ctea}~1', ctea, 'sections/302.md')
        lines = d.splitlines()
        removed_text = ' '.join(l for l in lines if l.startswith('-'))
        added_text = ' '.join(l for l in lines if l.startswith('+'))
        self.assertIn('fifty', removed_text.lower())
        self.assertIn('70', added_text)


class TestExample03ArchitecturalWorks(unittest.TestCase):
    """Example 3: When Did Architectural Works Become Copyrightable?"""

    @skip_if_no_repo
    def test_section_102_has_expected_commits(self):
        """Section 102 should show 1976, Software Rental, and Architectural Works acts."""
        commits = commits_for_file('sections/102.md')
        subjects = [s for _, s in commits]
        self.assertTrue(
            any('Copyright Act of 1976' in s for s in subjects),
        )
        self.assertTrue(
            any('Architectural Works' in s for s in subjects),
        )

    @skip_if_no_repo
    def test_1976_has_seven_categories(self):
        """The original 1976 Act should list exactly 7 categories, not 8."""
        act_1976 = commit_for('Copyright Act of 1976')
        text = show_file_at(act_1976, 'sections/102.md')
        # Should NOT have architectural works yet
        has_arch = 'architectural works' in text.lower()
        has_eight = '(8)' in text
        if has_arch or has_eight:
            self.fail(
                "BUG: The 1976 commit already contains '(8) architectural works'. "
                "It should only have 7 categories. Architectural works were not "
                "added until the Architectural Works Copyright Protection Act of 1990."
            )

    @skip_if_no_repo
    def test_architectural_works_act_adds_category_8(self):
        """The Architectural Works Act should ADD '(8) architectural works'."""
        arch = commit_for('Architectural Works Copyright Protection')
        d = diff_file(f'{arch}~1', arch, 'sections/102.md')
        added_lines = [l for l in d.splitlines()
                       if l.startswith('+') and not l.startswith('+++')]
        added_text = '\n'.join(added_lines)
        if 'architectural works' not in added_text.lower():
            self.fail(
                "BUG: The Architectural Works Act diff does not ADD "
                "'architectural works'. The diff should show this category "
                "being added, not removed."
            )

    @skip_if_no_repo
    def test_pre_architectural_works_no_category_8(self):
        """Just before the Architectural Works Act, section 102 should have 7 categories."""
        arch = commit_for('Architectural Works Copyright Protection')
        text = show_file_at(f'{arch}~1', 'sections/102.md')
        if '(8)' in text:
            self.fail(
                "BUG: The commit before the Architectural Works Act already "
                "has category (8). Section 102 should only have 7 categories "
                "until this act adds the 8th."
            )


class TestExample04CriminalPenalties(unittest.TestCase):
    """Example 4: How Criminal Penalties Escalated Over Time."""

    @skip_if_no_repo
    def test_section_506_has_five_commits(self):
        """Section 506 should have commits from 5 acts."""
        commits = commits_for_file('sections/506.md')
        expected_acts = [
            'Copyright Act of 1976',
            'Piracy and Counterfeiting',
            'Visual Artists Rights',
            'No Electronic Theft',
            'Family Entertainment',
        ]
        subjects = [s for _, s in commits]
        for act in expected_acts:
            self.assertTrue(
                any(act.lower() in s.lower() for s in subjects),
                f"Section 506 should have a commit for '{act}', "
                f"got: {subjects}",
            )

    @skip_if_no_repo
    def test_1976_simple_criminal_provision(self):
        """The original 1976 Section 506 should be a simple provision.

        The original text should require willfulness + commercial motive,
        with a $10,000 max fine and 1 year max imprisonment.
        """
        act_1976 = commit_for('Copyright Act of 1976')
        text = show_file_at(act_1976, 'sections/506.md')
        # The original 1976 version should NOT have NET Act language
        if '180' in text and 'day period' in text.lower():
            self.fail(
                "BUG: The 1976 commit for Section 506 contains '180-day period' "
                "language from the No Electronic Theft Act of 1997. "
                "The original 1976 text should be the simple one-sentence "
                "provision about willful infringement for commercial advantage."
            )

    @skip_if_no_repo
    def test_1976_506_mentions_commercial_advantage(self):
        """Original 506 should require commercial advantage or private financial gain."""
        act_1976 = commit_for('Copyright Act of 1976')
        text = show_file_at(act_1976, 'sections/506.md')
        self.assertIn('commercial advantage', text.lower(),
                       "Original 506 should mention 'commercial advantage'")
        self.assertIn('private financial gain', text.lower(),
                       "Original 506 should mention 'private financial gain'")


class TestExample05Timeline(unittest.TestCase):
    """Example 5: Exploring the Full Timeline."""

    @skip_if_no_repo
    def test_tags_exist(self):
        """Key era tags should exist."""
        tags = git('tag', '-l').splitlines()
        expected_tags = [
            'v1790', 'v1831', 'v1870', 'v1909', 'v1976',
            'v1988-berne', 'v1998-ctea', 'v1998-dmca',
        ]
        for tag in expected_tags:
            self.assertIn(tag, tags, f"Tag {tag} should exist")

    @skip_if_no_repo
    def test_commit_count(self):
        """Should have ~122 commits (121 acts + initial commit)."""
        log = git('log', '--oneline')
        count = len(log.splitlines())
        # Allow some flexibility as acts are added/removed
        self.assertGreaterEqual(count, 100,
                                 f"Expected ~122 commits, got {count}")
        self.assertLessEqual(count, 150,
                              f"Expected ~122 commits, got {count}")

    @skip_if_no_repo
    def test_section_107_rarely_amended(self):
        """Fair use (Section 107) should have very few amendments."""
        commits = commits_for_file('sections/107.md')
        # Should be 2-3 at most (1976 Act + maybe one amendment)
        self.assertLessEqual(len(commits), 4,
                              f"Section 107 should be rarely amended, "
                              f"but has {len(commits)} commits")

    @skip_if_no_repo
    def test_1790_act_exists_at_tag(self):
        """The v1790 tag should have the 1790 Act text."""
        try:
            text = git('show', 'v1790:pre-1976/copyright-act-of-1790.md')
            self.assertTrue(len(text) > 50,
                           "1790 Act text should be non-trivial")
        except RuntimeError:
            # Might be under a different filename
            files = git('ls-tree', '--name-only', '-r', 'v1790')
            self.assertTrue(
                any('1790' in f for f in files.splitlines()),
                f"v1790 tag should have a 1790 act file. Files: {files}",
            )

    @skip_if_no_repo
    def test_1976_act_creates_sections_dir(self):
        """The 1976 Act commit should create the sections/ directory."""
        act_1976 = commit_for('Copyright Act of 1976')
        files = git('ls-tree', '--name-only', act_1976)
        self.assertIn('sections', files.splitlines(),
                       "1976 Act should create the sections/ directory")

    @skip_if_no_repo
    def test_pre_1976_dir_removed_at_1976(self):
        """After the 1976 Act, pre-1976/ should no longer exist."""
        act_1976 = commit_for('Copyright Act of 1976')
        files = git('ls-tree', '--name-only', act_1976)
        self.assertNotIn('pre-1976', files.splitlines(),
                          "1976 Act should remove the pre-1976/ directory")


class TestExample06StatutoryDamages(unittest.TestCase):
    """Example 6: What Statutory Damages Were Available?"""

    @skip_if_no_repo
    def test_section_504_has_expected_commits(self):
        """Section 504 should show multiple amendments."""
        commits = commits_for_file('sections/504.md')
        subjects = [s for _, s in commits]
        self.assertTrue(
            any('Copyright Act of 1976' in s for s in subjects),
        )
        self.assertTrue(
            any('Berne Convention' in s for s in subjects),
        )

    @skip_if_no_repo
    def test_1976_504_has_original_amounts(self):
        """The 1976 Act should have original damage amounts ($250/$10K/$50K)."""
        act_1976 = commit_for('Copyright Act of 1976')
        text = show_file_at(act_1976, 'sections/504.md')
        self.assertIn('$250', text,
                       "1976 Act 504 should show $250 minimum")
        self.assertIn('$10,000', text,
                       "1976 Act 504 should show $10,000 maximum")
        self.assertIn('$50,000', text,
                       "1976 Act 504 should show $50,000 willful cap")

    @skip_if_no_repo
    def test_damages_increase_after_berne(self):
        """A later amendment should raise the damage amounts above $10,000."""
        commits = commits_for_file('sections/504.md')
        # Get the commit after Berne (second-most-recent before current)
        subjects = [s for _, s in commits]
        berne_idx = next(
            i for i, s in enumerate(subjects) if 'Berne' in s
        )
        if berne_idx == 0:
            self.skipTest("No amendment after Berne in history")
        later_hash = commits[berne_idx - 1][0]
        text = show_file_at(later_hash, 'sections/504.md')
        self.assertIn('$30,000', text,
                       "A later amendment should raise the max to $30,000")


class TestExample07DMCASafeHarbors(unittest.TestCase):
    """Example 7: When Did DMCA Safe Harbors Appear?"""

    @skip_if_no_repo
    def test_section_512_created_by_dmca(self):
        """Section 512 should be created by the DMCA and nothing else."""
        commits = commits_for_file('sections/512.md')
        self.assertEqual(len(commits), 1,
                          "Section 512 should have exactly one commit (DMCA)")
        self.assertIn('DMCA', commits[0][1],
                       "The sole commit should be the DMCA")

    @skip_if_no_repo
    def test_section_512_not_exist_before_dmca(self):
        """Section 512 should not exist before the DMCA commit."""
        dmca = commit_for('Digital Millennium Copyright Act')
        try:
            show_file_at(f'{dmca}~1', 'sections/512.md')
            self.fail("Section 512 should not exist before the DMCA")
        except RuntimeError:
            pass  # Expected: file does not exist

    @skip_if_no_repo
    def test_section_512_has_safe_harbor_categories(self):
        """Section 512 should contain the four safe harbor categories."""
        dmca = commit_for('Digital Millennium Copyright Act')
        text = show_file_at(dmca, 'sections/512.md')
        # Check for the subsection headers or key phrases
        self.assertIn('(a)', text)
        self.assertIn('(b)', text)
        self.assertIn('(c)', text)
        self.assertIn('(d)', text)


class TestExample08StaleVsActiveSections(unittest.TestCase):
    """Example 8: Finding Stale vs. Active Sections."""

    @skip_if_no_repo
    def test_section_111_is_heavily_amended(self):
        """Section 111 (cable retransmission) should be one of the most amended."""
        commits = commits_for_file('sections/111.md')
        self.assertGreaterEqual(len(commits), 6,
                                 f"Section 111 should be heavily amended, "
                                 f"got {len(commits)} commits")

    @skip_if_no_repo
    def test_section_119_is_heavily_amended(self):
        """Section 119 (satellite) should be one of the most amended."""
        commits = commits_for_file('sections/119.md')
        self.assertGreaterEqual(len(commits), 6,
                                 f"Section 119 should be heavily amended, "
                                 f"got {len(commits)} commits")

    @skip_if_no_repo
    def test_fair_use_less_amended_than_cable(self):
        """Fair use (107) should have far fewer amendments than cable (111)."""
        fair_use = len(commits_for_file('sections/107.md'))
        cable = len(commits_for_file('sections/111.md'))
        self.assertGreater(cable, fair_use * 2,
                           f"Cable ({cable}) should be amended much more "
                           f"than fair use ({fair_use})")


if __name__ == '__main__':
    unittest.main()
