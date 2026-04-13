# US Copyright Law: A Legislative History in Git

**[Browse the website](https://katelynsills.com/copyright/)** | **[View the build pipeline](https://github.com/katelynsills/copyright)**

Every amendment to United States copyright law — from the Copyright Act of 1790 to the present — encoded as a git commit. Browse 236 years of legislation with the tools you already know: `git log`, `git diff`, `git checkout`.

## Quick Start

```bash
# Browse the full timeline
git log --oneline

# See what the DMCA changed
git show v1998-dmca --stat

# Read the law as it existed after the 1976 Act
git checkout v1976

# Compare two eras
git diff v1909 v1976

# See exactly what an act added, removed, or modified
git diff <commit>~1 <commit>
```

## What's In This Repo

Each of the **122 commits** in this repository represents a single Act of Congress that created or amended federal copyright law. Commit messages include the act name, Public Law number, Statutes at Large citation, effective date, and a summary of what changed.

```
sections/          # Title 17 U.S.C. — one Markdown file per section (post-1976)
pre-1976/          # Statute text for acts before the 1976 rewrite
amendments/        # Placeholder notes for acts whose text changes are still in progress
CONTRIBUTING.md    # Guidelines for adding or correcting entries
LICENSE            # CC0 1.0 — public domain dedication
```

### Two Structural Eras

- **1790-1975** (38 acts): Copyright statutes existed as standalone acts, later codified in Title 17. Each major revision changed the structure significantly. These are stored in `pre-1976/`.
- **1976-present** (84 acts): The Copyright Act of 1976 (Pub. L. 94-553) completely rewrote Title 17 with the section numbering still used today. All subsequent amendments modify this stable structure. These are stored in `sections/`.

### Tags

Major acts are tagged for easy reference:

| Tag | Act | Year |
|-----|-----|------|
| `v1790` | Copyright Act of 1790 | 1790 |
| `v1831` | Copyright Act of 1831 | 1831 |
| `v1870` | Copyright Act of 1870 | 1870 |
| `v1909` | Copyright Act of 1909 | 1909 |
| `v1976` | Copyright Act of 1976 | 1976 |
| `v1984-chips` | Semiconductor Chip Protection Act | 1984 |
| `v1988-berne` | Berne Convention Implementation Act | 1988 |
| `v1998-ctea` | Sonny Bono Copyright Term Extension Act | 1998 |
| `v1998-dmca` | Digital Millennium Copyright Act | 1998 |
| `v2018-mma` | Music Modernization Act | 2018 |

## Examples

**How did copyright duration change over time?**
```bash
# 1790: 14 years. 1831: 28 years. 1909: 28+28. 1976: life+50. 1998: life+70.
git diff v1976 v1998-ctea -- sections/302.md
```

**When did buildings become copyrightable?**
```bash
# Architectural works were added to §102 on Dec 1, 1990
git log --oneline -- sections/102.md
```

**What did fair use look like before the internet?**
```bash
git show v1976 -- sections/107.md
```

## Status

This repository is generated from [katelynsills/copyright](https://github.com/katelynsills/copyright), which contains the build pipeline, source data, and 450+ automated tests that verify legal accuracy.

**In progress:** Some post-1976 acts have placeholder commits (in `amendments/`) where the exact text changes have not yet been reconstructed. The amendment anomalies documented in the pipeline repo describe cases where Congress's own amendment instructions are ambiguous, contradictory, or under-specified. See the pipeline repo for details.

## Commit Conventions

- Each commit = one Public Law
- `GIT_AUTHOR_DATE` is set to the enactment date for chronological ordering
- Commit messages follow this format:
  ```
  Act Name

  Public Law: Pub. L. XXX-XXX
  Citation: XXX Stat. XXXX
  Effective date: YYYY-MM-DD
  Summary: What changed.
  ```

## Sources

| Era | Primary Source |
|-----|---------------|
| 1790-1925 | Statutes at Large via Library of Congress / govinfo.gov |
| 1926-1975 | Historical U.S. Code via govinfo.gov |
| 1976-present | Office of Law Revision Counsel (uscode.house.gov) |
| Individual amendments | Congress.gov (bill text / Public Law text) |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding or correcting legislative entries.

Issues and improvements should be filed on the [pipeline repo](https://github.com/katelynsills/copyright/issues), which is the source of truth for all data in this repository.

## License

The text of US federal law is in the public domain. This repository's organizational structure and metadata are released under [CC0 1.0 Universal](LICENSE).
