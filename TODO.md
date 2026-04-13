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

## ~~Acts Fixed by Pipeline Improvements~~
~~These acts were empty due to shared-PL disambiguation or failed auto-reversal false positives. Fixed by title-level PL matching in prepare_build_data.py:~~
- [x] ~~Fairness in Music Licensing Act of 1998 — §301, §302, §303, §304 now correctly attributed to CTEA (Title I); §101, §110, §504, §513 to Fairness (Title II)~~
- [x] ~~Digital Theft Deterrence and Copyright Damages Improvement Act of 1999 — §504 reversal now detected as substantive~~
- [x] ~~Individuals with Disabilities Education Improvement Act of 2004 — §121 reversal fixed~~
- [x] ~~Library of Congress Technical Corrections Act of 2019 — §501, §701 reversals fixed~~
- [x] ~~Semiconductor International Protection Extension Act of 1991 — §914 reversal fixed~~

## ~~Acts Fixed by Manual Reconstruction~~
~~These acts had failed auto-reversals that were manually reconstructed:~~
- [x] ~~Copyright Royalty Tribunal Reform and Miscellaneous Pay Act of 1989 — §701 reconstructed (added subsec. e, compensation changes). §802 skipped (old CRT section was completely replaced by PL 108-419 in 2004).~~
- [x] ~~Architectural Works Copyright Protection Act of 1990 — §102 already correct (auto-reversal worked)~~
- [x] ~~Intellectual Property Protection and Courts Amendments Act of 2004 — §504 fully reconstructed (all 6 versions with correct amounts, par. 3, subsec. d)~~
- [x] ~~Vessel Hull Design Protection Amendments of 2008 — §1301 reconstructed (pre-2008 text without deck/DoD provisions)~~
- [x] ~~Unlocking Consumer Choice and Wireless Competition Act of 2014 — §1201 (standalone statutory note, not a text amendment; act-snapshot already existed)~~
- [x] ~~Marrakesh Treaty Implementation Act of 2018 — §121 fully reconstructed (all 4 versions with specialized formats/accessible formats terminology)~~
- [x] ~~Protecting Lawful Streaming Act of 2020 — §1501, §1502 (new sections, version entries created for PL 116-260)~~
- [x] ~~Artistic Recognition for Talented Students Act of 2022 (ARTS Act) — §708 version added for PL 117-201; also fixed version convention shift for all 708 entries~~
- [x] ~~James M. Inhofe NDAA for FY2023 — §105 fully reconstructed (all 4 versions including 2019 NDAA, 2022 NDAA, 2024 NDAA, 2025 NDAA)~~
- [x] ~~Servicemember Quality of Life NDAA for FY2025 + NDAA for FY2026 — §105 (covered by same reconstruction)~~

## Acts Requiring Complex Manual Reconstruction
These acts involve very large sections (§110, §111, §112, §114, §118, §119) that underwent multiple complete chapter-level rewrites (PL 108-419 in 2004 rewrote the entire royalty chapter; PL 111-175 in 2010 rewrote §119). Reconstructing intermediate versions requires access to the full text of each version, which is beyond what can be derived from amendment notes alone.

### Partial fixes applied (CRJ anachronism removal, structural changes)
All six sections had "Copyright Royalty Judges" (a 2004 term) in pre-2004 versions. Fixed to use "Copyright Royalty Tribunal" (pre-1993) or "Librarian of Congress" (1993-2004) as appropriate. §112 subsec (f) addition/removal reconstructed. §110 par. (10)/(11) addition/removal reconstructed. §118 fully reconstructed with correct CRT/LoC/CRJ transitions across all versions.

### Remaining (full text reconstruction needed for precise intermediate versions)
- [ ] Satellite Home Viewer Act of 1994 — §111, §119 (§119 was completely rewritten by PL 111-175 in 2010)
- [ ] Technology, Education, and Copyright Harmonization Act of 2002 (TEACH Act) — §110 par. (2) rewrite still uses post-TEACH text in pre-TEACH versions
- [ ] Small Webcaster Amendments Act of 2002 — §114 (added pars, restructured; versions differentiated by CRJ fix but detailed text reconstruction pending)
- [ ] Webcaster Settlement Act of 2008 — §114
- [ ] Webcaster Settlement Act of 2009 — §114
- [ ] Temporary Extension Act of 2010 (Copyright Provision) — §119 (date changes, but requires full §119 reconstruction first)
- [ ] Satellite Television Extension Act of 2010 — §119 (comprehensive restructuring)
- [ ] Continuing Extension Act of 2010 (Copyright Provision) — §119 (date changes)

## ~~Data Quality Fixes~~
- [x] ~~§1501/§1502 (CASE Act) — populated empty v0 text from current text (no amendments since creation)~~
- [x] ~~§106A — fixed v0 attribution from PL 94-553 (1976) to PL 101-650 (VARA, 1990)~~
- [x] ~~§101 — removed "Copyright Royalty Judge" definition from all pre-2004 versions (added by PL 108-419)~~
- [x] ~~§118 — fully reconstructed: CRT (1976), LoC (1993-2002), CRJ (2004+) with correct text per era~~
- [x] ~~§112 — reconstructed subsec (f) addition by PL 107-273 and CRJ/LoC transitions~~
- [x] ~~§110 — reconstructed par. (10) addition (PL 97-366) and par. (11) addition (PL 109-9, Family Movie Act)~~
- [x] ~~§111, §114, §119 — fixed CRJ anachronism in all pre-2004 versions~~
- [x] ~~§115 — replaced placeholder current text with actual 119K-char current text~~
- [x] ~~PL/year mismatches — fixed 234 version entries with wrong year fields across all sections~~
- [x] ~~Version ordering — sorted all version files chronologically by year and PL number~~
- [x] ~~§304 — preserved pre-1976 term extension act entries (1962-1974), updated test bounds~~

## ~~Acts List Completeness~~
- [x] ~~Two PLs excluded as cross-references (91-375, 99-474) — confirmed: PL 91-375 (Postal Reorganization) amended old Title 17 only, superseded by 1976 Act; PL 99-474 (Computer Fraud) amends 18 USC only.~~
