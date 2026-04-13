# copyright — Build Pipeline for US Copyright Law in Git

This repository contains the tools, source data, and tests that generate [katelynsills/copyright-history](https://github.com/katelynsills/copyright-history) — a git repository where each commit represents an Act of Congress that created or amended US copyright law, from 1790 to present.

## What This Repo Does

The **copyright-history** repo is the public-facing product: 122 commits spanning 236 years, browsable with `git log`, `git diff`, and `git checkout`. This repo is the factory that builds it.

It contains:
- **Source data** — current statute text, historical snapshots, amendment notes, and pre-1976 act text from authoritative government sources
- **Build pipeline** — scripts that assemble the data into a clean git history with one commit per act
- **Reconstruction tools** — scripts that reverse-engineer historical versions of sections from OLRC amendment notes
- **450+ automated tests** — verify that reconstructed text matches known legal facts (e.g., that "fifty years" appears in the 1976 version of Section 302)
- **A static website** — browse the full legislative history in a browser with diffs, side-by-side comparison, Ramseyer redlines, and an "as of" date picker
- **Amendment anomalies** — 14 documented cases where Congress's own amendment instructions are ambiguous, contradictory, or contain drafting errors

## Repository Structure

```
build.py                  # Generates the copyright-history repo
build_site.py             # Generates the static website
prepare_build_data.py     # Prepares act-snapshots from version data
reconstruct.py            # Reconstructs historical section text from amendment notes
fetch_current_sections.py # Fetches current statute text from OLRC

data/
  acts.json               # Index of all 122 acts with metadata
  current-sections/       # Current Title 17 U.S.C. text (one .md per section)
  amendment-notes/        # OLRC amendment notes per section
  snapshots/              # Reconstructed version histories per section
  act-snapshots/          # Section text at each act boundary (build input)
  pre-1976-text/          # Full text of pre-1976 acts
  amendment-anomalies.md  # Documented anomalies (in progress — see below)

metadata/
  acts.yaml               # Act metadata used by build.py

site/                     # Generated static website
site-src/                 # Website source (templates, CSS, JS)
tests/                    # Automated legal accuracy tests
examples/                 # Example queries and usage
```

## Building

Generate the copyright-history repo:

```bash
python3 build.py [--output-dir /path/to/copyright-history]
```

Generate the static website:

```bash
python3 build_site.py
```

## In-Progress Work

### Amendment Anomalies (in progress — to be verified)

The file `data/amendment-anomalies.md` documents 14 cases where applying amendments mechanically reveals bugs in the legislative process. These include:

- Duplicate subsection letters that persisted for years (Section 105)
- Contradictory redesignation instructions (Section 701)
- Complete section replacements that erase amendment history (Section 802)
- Coordination failures between congressional committees (Section 105)
- Uncorrected typos and grammatical errors spanning decades (Sections 110, 119)

These anomalies are documented findings but have not all been independently verified against primary sources. They should be treated as preliminary until confirmed.

### Acts With No File Changes (in progress)

23 post-1976 acts have commits in the history repo but no reconstructed text changes yet. Of these, 10 have full snapshots ready to apply, 11 need Section 101 (definitions) reconstruction, and 2 need other missing sections. See `TODO.md` for the full list.

### Intermediate Version Differentiation (in progress)

Some sections (Section 111, Section 119) have multiple historical versions that currently use the same base text. The intermediate differences from individual acts have not yet been applied. See `TODO.md` for details.

## Sources

| Era | Primary Source |
|-----|---------------|
| 1790-1925 | Statutes at Large via Library of Congress / govinfo.gov |
| 1926-1975 | Historical U.S. Code via govinfo.gov |
| 1976-present | Office of Law Revision Counsel (uscode.house.gov) |
| Individual amendments | Congress.gov (bill text / Public Law text) |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on adding or correcting legislative entries.

## License

The text of US federal law is in the public domain. This repository's organizational structure and metadata are released under [CC0 1.0 Universal](LICENSE).
