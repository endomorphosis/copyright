# US Copyright Law: A Legislative History in Git

This repository tracks every legislative change to United States copyright law, from the first Copyright Act of 1790 to the present day. Each commit represents a single Act of Congress that created or amended copyright law, with the full statute text and metadata about the change.

## How to Use This Repository

**Browse the timeline**: `git log --oneline` shows every act that changed copyright law in chronological order.

**See what an act changed**: `git show <commit>` or `git diff <commit>~1 <commit>` shows exactly what a given act added, removed, or modified.

**Read the law at any point in time**: `git checkout <commit>` checks out the full text of copyright law as it existed after a given act.

**Compare two eras**: `git diff v1909 v1976` shows the complete transformation from the 1909 Act to the 1976 Act.

## Repository Structure

```
sections/          # Current Title 17 U.S.C. (one file per section, post-1976)
pre-1976/          # Statute text as it existed before the 1976 rewrite
metadata/
  acts.yaml        # Index of all acts with dates, citations, and summaries
```

### Pre-1976 vs. Post-1976

US copyright law has two distinct structural eras:

- **1790-1975**: Copyright statutes existed as standalone acts, later codified in Title 17 of the U.S. Code. The structure changed significantly with each major revision. These are stored in `pre-1976/`.
- **1976-present**: The Copyright Act of 1976 (Pub. L. 94-553) completely rewrote Title 17 with the section numbering used today. Amendments since then modify this stable structure. These are stored in `sections/`.

## Commit Conventions

- Each commit represents one Public Law that created or amended copyright law
- Commit messages include the act name, Public Law number, effective date, and a brief summary
- `GIT_AUTHOR_DATE` is set to the enactment date for chronological accuracy
- Major acts are tagged (e.g., `v1790`, `v1909`, `v1976`)

## Sources

| Era | Primary Source |
|-----|---------------|
| 1790-1925 | Statutes at Large via LOC / govinfo.gov |
| 1926-1975 | Historical U.S. Code via govinfo.gov |
| 1976-present | Office of Law Revision Counsel (uscode.house.gov) |
| Individual amendments | Congress.gov (bill text / Public Law text) |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding or correcting legislative entries.

## License

The text of US federal law is in the public domain. This repository's organizational structure and metadata are released under [CC0 1.0 Universal](LICENSE).
