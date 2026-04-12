# Open Issues / Things to Verify

## ~~Missing Sections~~
- [x] ~~Sections 1402, 1403, 1404 (Chapter 14 - Pre-1972 Sound Recordings) — these sections do not exist. Chapter 14 contains only §1401. Removed from fetch_current_sections.py.~~

## ~~CTEA Swap Bugs (auto-reversal failures)~~
~~These sections had their 1976-era text and CTEA-era text swapped in snapshots/act-snapshots.~~
- [x] ~~§302 — "fifty years"/"seventy-five years" swapped with "70 years"/"95 years"~~
- [x] ~~§303 — CTEA act-snapshot had "2027" (pre-CTEA) instead of "2047" (post-CTEA)~~
- [x] ~~§304 — version 0 had "67 years" (post-CTEA) instead of "47 years" (pre-CTEA)~~
- [x] ~~§401 — fixed by other session (notice "shall be placed" vs "may be placed")~~
- [x] ~~§301 — CTEA act-snapshot fixed: replaced MMA-era text with correct post-CTEA text containing "2067". Also fixed 301-versions.json with correct 1976 original (3-sentence subsec. (c) with "2047").~~

## ~~Failed Auto-Reversals (version 0 text == current text)~~
~~All 10 sections that were in the 1976 commit with incorrect 2026 text have been manually reconstructed:~~
- [x] ~~§102 — removed "(8) architectural works" from 1976 version~~
- [x] ~~§104 — reversed 1998 DMCA and 1988 Berne amendments (removed treaty party, subsecs c/d)~~
- [x] ~~§109 — reversed Record Rental (1984) and Computer Software (1990) amendments~~
- [x] ~~§113 — removed VARA subsec. (d)~~
- [x] ~~§115 — reconstructed 1976 text with original compulsory license (no digital phonorecord delivery)~~
- [x] ~~§116 — reconstructed 1976 jukebox compulsory license text (original §116 before 1993 repeal/renumber)~~
- [x] ~~§201 — removed bankruptcy exception from subsec. (e)~~
- [x] ~~§301 — reconstructed 1976 text with 3-sentence subsec. (c) and "2047"~~
- [x] ~~§506 — reconstructed 1976 text with original fine/imprisonment provisions~~
- [x] ~~§708 — reconstructed 1976 text with original fee schedule and all intermediate versions~~
- [x] ~~§512, §513, §1010, §1201, §122 — post-1976 sections, correctly excluded from 1976 commit~~

## ~~Marker Files (acts without section snapshots)~~
~~These acts produce marker files in amendments/ instead of actual section changes — all OK:~~
- [x] ~~Copyright Felony Act of 1992 — amends 18 USC, not Title 17 (marker OK)~~
- [x] ~~Legislative Branch Appropriations Act of 1994 — procedural, not Title 17 (marker OK)~~
- [x] ~~NDAA for FY2012 — amends 18 USC, not Title 17 (marker OK)~~
- [x] ~~CARES Act of 2020 — temporary authority, not codified (marker OK)~~

## ~~Text Quality~~
- [x] ~~Verify HTML-to-text conversion — all 122 sections checked: no HTML artifacts, proper Unicode, well-formed statute text.~~
- [x] ~~Section 115 (119K chars) — complete and correctly extracted (513 lines, ends properly at MMA citation).~~
- [x] ~~Amendment notes split check — found and fixed §109 truncation (subsecs (b)(2)(B)-(e) were in notes file instead of section file). §111, §114, §119 all complete.~~

## ~~Pre-1976 Text Quality~~
- [x] ~~Pre-1976 acts sourced from web searches — all verified as authentic statutory language (not summaries). Pre-1909 acts cannot be verified from free online sources (would need HeinOnline).
- [x] 1909 Act (49KB, 64 sections) — complete and correctly structured. PDF downloaded to data/source-pdfs/.
- [x] 1870 Act (14KB, §§85-111) — copyright provisions only, appropriate for project scope.
- [x] 1891 Chace Act (4.3KB, 8 sections) — reads as authentic statutory language, no free primary source available for cross-reference.
- [x] Short amendments (1874, 1879, 1882, 1893, 1895, 1897) — all use proper enacting clauses and period-appropriate legal language. Three are acknowledged extracts from larger bills (appropriately marked). Removed editorial note from 1897 Copyright Office establishment act.
- [x] Source PDFs: downloaded 1909 Act and 1976 Act from copyright.gov. Earlier acts not available as PDFs from government sources.

## Acts Without Reconstructed Section Snapshots
These 23 acts amend Title 17 sections (per the section-amendment-map) but have no snapshot data, so their commits are empty in the output repo. Each needs section text reconstructed for the versions it changed.

- [ ] Copyright Royalty Tribunal Reform and Miscellaneous Pay Act of 1989 — sections: §101, §701, §802
- [ ] Semiconductor International Protection Extension Act of 1991 — sections: §101, §914
- [ ] Satellite Home Viewer Act of 1994 — sections: §101, §111, §119
- [ ] Fairness in Music Licensing Act of 1998 — sections: §101, §108, §110, §203, §301, §302, §303, §304 (+2 more)
- [ ] Digital Theft Deterrence and Copyright Damages Improvement Act of 1999 — sections: §101, §504
- [ ] Technology, Education, and Copyright Harmonization Act of 2002 (TEACH Act) — sections: §101, §106, §110, §112, §118, §119, §121, §122 (+5 more)
- [ ] Small Webcaster Amendments Act of 2002 — sections: §101, §114
- [ ] Individuals with Disabilities Education Improvement Act of 2004 (Copyright Provision) — sections: §121
- [ ] Intellectual Property Protection and Courts Amendments Act of 2004 — sections: §504
- [ ] Webcaster Settlement Act of 2008 — sections: §101, §114
- [ ] Vessel Hull Design Protection Amendments of 2008 — sections: §101, §1301
- [ ] Webcaster Settlement Act of 2009 — sections: §101, §114
- [ ] Temporary Extension Act of 2010 (Copyright Provision) — sections: §119
- [ ] Satellite Television Extension Act of 2010 — sections: §101, §119
- [ ] Continuing Extension Act of 2010 (Copyright Provision) — sections: §119
- [ ] Unlocking Consumer Choice and Wireless Competition Act of 2014 — sections: §1201
- [ ] Marrakesh Treaty Implementation Act of 2018 — sections: §101, §121
- [ ] Library of Congress Technical Corrections Act of 2019 — sections: §101, §119, §501, §701, §802, §803
- [ ] Protecting Lawful Streaming Act of 2020 — sections: §101, §1501, §1502
- [ ] Artistic Recognition for Talented Students Act of 2022 (ARTS Act) — sections: §101, §708
- [ ] James M. Inhofe National Defense Authorization Act for Fiscal Year 2023 (Copyright Provision) — sections: §105
- [ ] Servicemember Quality of Life Improvement and National Defense Authorization Act for Fiscal Year 2025 (Copyright Provision) — sections: §105
- [ ] National Defense Authorization Act for Fiscal Year 2026 (Copyright Provision) — sections: §105

## ~~Acts List Completeness~~
- [x] ~~Two PLs excluded as cross-references (91-375, 99-474) — confirmed: PL 91-375 (Postal Reorganization) amended old Title 17 only, superseded by 1976 Act; PL 99-474 (Computer Fraud) amends 18 USC only.~~
