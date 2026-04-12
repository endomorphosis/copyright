# Use Cases: Who This Repository Is For

A git-based legislative history of US copyright law is not just an archival curiosity. It is a practical tool for lawyers, legislators, researchers, and anyone who needs to understand what the law said at a specific point in time, how it changed, and why.

This document describes concrete, actionable ways different audiences can use this repository.

## For Lawyers and Litigators

### Determine the law in effect at the time of infringement

Copyright cases often turn on what the statute said when the alleged infringement occurred, not what it says today. Checking out the repository at the relevant commit gives you the exact statutory text that governed.

**Example**: A publisher sues over unauthorized copies distributed in 1985. Was copyright notice required? Check out the law before the Berne Convention Implementation Act of 1988 to confirm that Section 401 still mandated notice on all published copies. See [Example 1](01-notice-requirement.md).

### Trace when a provision was added, modified, or removed

Courts care about legislative history. `git log` on a specific section file shows every act that touched it, and `git diff` shows exactly what changed each time.

**Example**: You need to argue that Congress deliberately expanded copyright duration. The diff of the Sonny Bono Copyright Term Extension Act shows the precise word changes — "fifty years" to "70 years", "seventy-five years" to "95 years." See [Example 2](02-copyright-duration.md).

### Build "the law didn't say X until Y" arguments

Some provisions that feel timeless are actually recent additions. A diff proves it.

**Example**: A defendant argues that architectural works have always been copyrightable. The repository shows that Section 102 listed only seven categories of works until the Architectural Works Copyright Protection Act of 1990 added "(8) architectural works." See [Example 3](03-architectural-works.md).

### Prepare statutory comparison exhibits for court

A clean diff between two versions of a section is more persuasive and easier for a judge to read than a narrative explanation. The `git diff` output can be formatted directly into a court exhibit showing additions in green and deletions in red.

### Identify what law applied to pre-1972 sound recordings

The preemption timeline for pre-1972 sound recordings under Section 301 is one of the most litigated questions in copyright. The commit history traces every change to this section, including the evolving preemption dates.

## For Legislators and Policy Staff

### Audit the cumulative effect of piecemeal amendments

Some sections have been patched so many times that the current text is nearly unreadable. The commit history shows how the complexity accreted.

**Example**: Section 108 (library and archives exceptions) was amended by at least 3 separate acts. Section 506 (criminal penalties) was amended 5 times between 1976 and 2005, each time ratcheting up penalties and expanding the definition of criminal infringement. See [Example 4](04-criminal-penalties.md).

### Find sections that haven't been updated in decades

Running `git log` on each section file reveals which parts of the law are stale vs. actively maintained — useful for prioritizing modernization. See [Example 8](08-stale-vs-active-sections.md).

**Example**: Fair use (Section 107) has been amended only once since 1976, by the Computer Software Rental Amendments Act of 1990. Meanwhile, Section 504 (statutory damages) has been amended 4 times. This asymmetry suggests fair use may be due for a legislative update.

### Find precedent for how past Congresses structured amendments

When drafting a new bill, look at how prior acts phrased additions, substitutions, and repeals. Each commit message includes the Public Law number and citation.

## For Potential Copyright Defendants / Compliance

### Determine whether notice was required for a specific work

The notice requirement changed dramatically over time. Before 1989, failure to include proper copyright notice could inject a work into the public domain. After the Berne Convention Implementation Act, notice became optional.

**Example**: A company discovers it has been using a photograph published in 1985 without a copyright notice. Was the work injected into the public domain? Check the law in effect at publication — Section 401 still required notice in 1985. Then check Section 405 to see whether the omission was curable. See [Example 1](01-notice-requirement.md).

### Check registration requirements at the time of publication

Whether registration was a prerequisite for filing suit has shifted. The repository lets you verify the exact requirements in effect when a work was published.

### Verify whether a specific use was exempt at the relevant time

Exemptions for satellite retransmission, distance education, software backup copies, and other uses appeared at specific dates. Checking out the law at the relevant time confirms whether an exemption existed. Similarly, DMCA safe harbor protections for platforms did not exist before 1998 — see [Example 7](07-dmca-safe-harbors.md).

## For Copyright Plaintiffs / Rights Holders

### Establish the penalties available at the time of infringement

Statutory damages amounts have changed multiple times. The 1976 Act set the range at $250–$10,000 (up to $50,000 for willful infringement). By 2004, those numbers had risen to $750–$30,000 (up to $150,000 for willful). The diff shows exactly when each increase took effect.

See [Example 4](04-criminal-penalties.md) for criminal penalties and [Example 6](06-statutory-damages.md) for civil statutory damages.

### Prove that a work was eligible for protection

Subject matter (Section 102), duration (Sections 302–305), and eligibility requirements have all expanded over time. Checking out the law at the creation or publication date confirms whether the work qualified.

## For Researchers and Educators

### Visualize how copyright scope has expanded over 230+ years

The git history itself is a dataset. The repository grew from a single file (the 1790 Act protecting books, maps, and charts for 14 years) to 122 section files covering everything from architectural works to vessel hull designs. The 120 commits tell a story about regulatory growth.

### Teach copyright law as a living, evolving system

Students can use `git log`, `git diff`, and `git checkout` to explore the law interactively rather than reading a static casebook. Seeing the exact words Congress added and removed is more vivid than a professor's summary.

### Fact-check claims about copyright law

"Copyright used to last only 14 years." True — but when did it change? The repository traces every extension: 28 years in 1831, life+50 in 1976, life+70 in 1998. Each step is a commit with a citation.

See [Example 5](05-exploring-the-timeline.md).

## For Journalists

### Quickly verify legislative claims in copyright debates

When a lobbyist claims "this provision has been in the law since 1976," the repository lets you verify in seconds whether that's true or whether it was actually added in 1998 or 2005.

### Understand the scope of proposed changes

When new copyright legislation is proposed, comparing the current statute text to the proposed changes is much easier when you have a clean, structured copy of the current law. The repository provides that baseline.
