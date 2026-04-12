# Open Issues / Things to Verify

## Missing Sections
- [x] Sections 1402, 1403, 1404 (Chapter 14 - Pre-1972 Sound Recordings) — these sections do not exist. Chapter 14 contains only §1401. Removed from fetch_current_sections.py.

## CTEA Swap Bugs (auto-reversal failures)
These sections had their 1976-era text and CTEA-era text swapped in snapshots/act-snapshots.
Fixed so far:
- [x] §302 — "fifty years"/"seventy-five years" swapped with "70 years"/"95 years"
- [x] §303 — CTEA act-snapshot had "2027" (pre-CTEA) instead of "2047" (post-CTEA)
- [x] §304 — version 0 had "67 years" (post-CTEA) instead of "47 years" (pre-CTEA)
- [x] §401 — fixed by other session (notice "shall be placed" vs "may be placed")
Still need investigation:
- [x] §301 — CTEA act-snapshot fixed: replaced MMA-era text with correct post-CTEA text containing "2067". Also fixed 301-versions.json with correct 1976 original (3-sentence subsec. (c) with "2047").

## Failed Auto-Reversals (version 0 text == current text)
These 15 sections have version 0 text identical to current text, meaning the auto-reversal
in reconstruct.py did not actually change the text. The 1976-era version in the output repo
will incorrectly show 2026 text for these sections:
- [x] §102 — removed "(8) architectural works" from 1976 version
- [x] §104 — reversed 1998 DMCA and 1988 Berne amendments (removed treaty party, subsecs c/d)
- [x] §109 — reversed Record Rental (1984) and Computer Software (1990) amendments
- [x] §113 — removed VARA subsec. (d)
- [x] §115 — reconstructed 1976 text with original compulsory license (no digital phonorecord delivery)
- [x] §116 — reconstructed 1976 jukebox compulsory license text (original §116 before 1993 repeal/renumber)
- [x] §201 — removed bankruptcy exception from subsec. (e)
- [x] §301 — reconstructed 1976 text with 3-sentence subsec. (c) and "2047"
- [x] §506 — reconstructed 1976 text with original fine/imprisonment provisions
- [ ] §512 — DMCA safe harbor (created post-1976, shouldn't be in 1976 commit — OK if excluded)
- [ ] §513 — determination of reasonable license fees (post-1976, OK if excluded)
- [x] §708 — reconstructed 1976 text with original fee schedule and all intermediate versions
- [ ] §1010 — digital audio recording devices (post-1976, OK if excluded)
- [ ] §1201 — DMCA anti-circumvention (post-1976, OK if excluded)
- [ ] §122 — secondary transmissions (post-1976, OK if excluded)

Note: §512, §513, §1010, §1201, §122 are post-1976 sections and are correctly excluded
from the 1976 commit already. The remaining 10 sections (§102, §104, §109, §113, §115,
§116, §201, §301, §506, §708) ARE in the 1976 commit but show 2026 text instead of
1976-era text. These need manual reconstruction.

## Marker Files (acts without section snapshots)
These acts produce marker files in amendments/ instead of actual section changes:
- [ ] Copyright Felony Act of 1992 — amends 18 USC, not Title 17 (marker OK)
- [ ] Legislative Branch Appropriations Act of 1994 — procedural, not Title 17 (marker OK)
- [ ] NDAA for FY2012 — amends 18 USC, not Title 17 (marker OK)
- [ ] CARES Act of 2020 — temporary authority, not codified (marker OK)

## Text Quality
- [ ] Verify HTML-to-text conversion didn't lose formatting or content in any section
- [ ] Section 115 is 119K chars — verify it extracted correctly (very long section)
- [ ] Check that amendment notes extraction didn't cut off section text prematurely

## Pre-1976 Text Quality
- [ ] Pre-1976 acts sourced from web searches — verify against Statutes at Large PDFs where possible
- [ ] 1909 Act (49KB) — sourced from ellenwhite.info, verify against copyright.gov PDF
- [ ] 1870 Act — sourced from Wikisource/ellenwhite.info, verify against Statutes at Large
- [ ] 1891 Chace Act — reconstructed from Patry and secondary sources, verify against original
- [ ] Short amendments (1874, 1879, 1882, 1893, 1895, 1897) — some reconstructed from descriptions, verify exact statutory language
- [ ] Pre-1976 PDF sources should be downloaded and saved to data/source-pdfs/

## Acts List Completeness
- [x] Two PLs excluded as cross-references (91-375, 99-474) — confirmed: PL 91-375 (Postal Reorganization) amended old Title 17 only, superseded by 1976 Act; PL 99-474 (Computer Fraud) amends 18 USC only.
